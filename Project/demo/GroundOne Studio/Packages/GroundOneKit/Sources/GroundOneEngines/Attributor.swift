import Foundation
import GroundOneCore
import NaturalLanguage

/// Source links (§4c, M3b; demonstrative, not evaluated): GroundOne per passage picks the passage, word overlap picks
/// the span. One pass per passage for the whole answer, computed lazily and cached per answer.
public actor PassageAttributor {
    let verifier: GroundOneVerifier
    var cache: [String: [[SentenceVerdict]]] = [:]

    public init(verifier: GroundOneVerifier) { self.verifier = verifier }

    /// Per-passage verdicts for every sentence of the answer: result[passage][sentence].
    func perPassage(answer: [Segment], passages: [Passage], key: String) async throws -> [[SentenceVerdict]] {
        if let c = cache[key] { return c }
        var out: [[SentenceVerdict]] = []
        for p in passages {
            out.append(try await verifier.verify(document: p.text, sentences: answer).sentences)
        }
        cache[key] = out
        return out
    }

    /// Links for every scored sentence: the passage with the highest P(supported) (green) if the sentence is supported
    /// there, and the one with the highest P(contradicted) (red) if contradicted there.
    public func links(answer: [Segment], passages: [Passage], key: String) async throws -> [Int: [SourceLink]] {
        guard !passages.isEmpty else { return [:] }
        let per = try await perPassage(answer: answer, passages: passages, key: key)
        var out: [Int: [SourceLink]] = [:]
        for (i, seg) in answer.enumerated() where seg.checkable {
            var links: [SourceLink] = []
            for kind in [Label.supported, Label.contradicted] {
                let k = kind.index
                let best = per.indices.max { (per[$0][i].probs?[k] ?? 0) < (per[$1][i].probs?[k] ?? 0) }!
                guard let p = per[best][i].probs, Decision.decide(p, threshold: verifier.model.info.calibration.threshold) == kind
                else { continue }
                let span = Self.bestSpan(for: seg.text, in: passages[best].text)
                links.append(SourceLink(sentence: i, kind: kind, passage: passages[best], probability: p[k],
                                        spanStart: span.start, spanEnd: span.end, spanText: span.text))
            }
            if !links.isEmpty { out[i] = links }
        }
        return out
    }

    /// The passage sentence that best matches the answer sentence: shared word stems weighted by their rarity among the
    /// passage's sentences (IDF), so that a distinctive term ("temperature") outweighs words repeated everywhere.
    static func bestSpan(for sentence: String, in passage: String) -> (start: Int, end: Int, text: String) {
        let tok = NLTokenizer(unit: .sentence)
        tok.string = passage
        var spans: [(NSRange, String)] = []
        tok.enumerateTokens(in: passage.startIndex..<passage.endIndex) { range, _ in
            spans.append((NSRange(range, in: passage), String(passage[range])))
            return true
        }
        guard !spans.isEmpty else { return (0, (passage as NSString).length, passage) }
        let stems = spans.map { stemSet($0.1) }
        var df: [String: Int] = [:]
        for s in stems { for w in s { df[w, default: 0] += 1 } }
        let n = Double(spans.count)
        let target = stemSet(sentence)
        let scores = stems.map { s in s.intersection(target).map { log(1 + n / Double(df[$0]!)) }.reduce(0, +) }
        let best = scores.indices.max { scores[$0] < scores[$1] }!
        let r = spans[best].0
        return (r.location, r.upperBound, spans[best].1.trimmingCharacters(in: .whitespacesAndNewlines))
    }

    /// Lower-cased words longer than two letters, cut to six characters (a crude stem: calibrates ~ calibrating).
    static func stemSet(_ s: String) -> Set<String> {
        Set(words(s).map { String($0.prefix(6)) })
    }

    static func words(_ s: String) -> Set<String> {
        Set(s.lowercased().components(separatedBy: CharacterSet.alphanumerics.inverted).filter { $0.count > 2 })
    }
}
