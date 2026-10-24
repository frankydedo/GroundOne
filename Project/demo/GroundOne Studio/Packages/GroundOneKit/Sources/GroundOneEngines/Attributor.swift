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

    /// The passage sentence with the largest word overlap with the answer sentence.
    static func bestSpan(for sentence: String, in passage: String) -> (start: Int, end: Int, text: String) {
        let target = words(sentence)
        let tok = NLTokenizer(unit: .sentence)
        tok.string = passage
        var best = (0, (passage as NSString).length, passage)
        var bestScore = -1.0
        tok.enumerateTokens(in: passage.startIndex..<passage.endIndex) { range, _ in
            let s = String(passage[range])
            let w = words(s)
            let score = w.isEmpty ? 0 : Double(w.intersection(target).count) / Double(w.union(target).count).squareRoot()
            if score > bestScore {
                bestScore = score
                let r = NSRange(range, in: passage)
                best = (r.location, r.upperBound, s.trimmingCharacters(in: .whitespacesAndNewlines))
            }
            return true
        }
        return best
    }

    static func words(_ s: String) -> Set<String> {
        Set(s.lowercased().components(separatedBy: CharacterSet.alphanumerics.inverted).filter { $0.count > 2 })
    }
}
