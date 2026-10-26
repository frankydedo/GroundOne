import Foundation
import NaturalLanguage

/// One answer draft and GroundOne's verdicts on it.
public struct Draft: Codable, Sendable {
    public var round: Int
    public var text: String
    public var verdicts: Verdicts
    public var generation: GenerationStats
    /// Sentence indices of the previous draft sent back for rewriting, and what the generator returned.
    public var rewriteRequest: [Int]
    public var rewriteRaw: String?
}

public enum FinalStatus: String, Codable, Sendable {
    case accepted, highlighted, hidden, abstained
}

public struct MemoryStats: Codable, Sendable {
    public var mlxActiveGB: Double
    public var mlxPeakGB: Double
    public var residentGB: Double

    public init(mlxActiveGB: Double, mlxPeakGB: Double, residentGB: Double) {
        self.mlxActiveGB = mlxActiveGB; self.mlxPeakGB = mlxPeakGB; self.residentGB = residentGB
    }
}

public struct Timings: Codable, Sendable {
    public var retrieval: Double = 0
    public var generation: [Double] = []
    public var verification: [Double] = []
    public var judge: Double?
    public var total: Double = 0
}

/// Everything about one query: what the audit log stores and the timing panel shows.
public struct QueryRecord: Codable, Sendable, Identifiable {
    public var id = UUID()
    public var date = Date()
    public var question: String
    public var task: String?
    public var policy: Policy
    public var verifier: String
    public var generator: String
    public var passages: [Passage]
    public var document: String
    public var drafts: [Draft] = []
    public var status: FinalStatus = .accepted
    public var displayed: String = ""
    public var judge: JudgeVerdicts?
    public var timings = Timings()
    public var memory: MemoryStats?

    public var final: Draft? { drafts.last }
    public var rounds: Int { max(drafts.count - 1, 0) }
}

public enum LoopEvent: Sendable {
    case retrieved([Passage], seconds: Double)
    case stage(String)
    case partial(round: Int, text: String)
    case draft(Draft)
    case judge(JudgeVerdicts)
    case finished(QueryRecord)
}

/// Retrieve → generate → verify → policy → (rewrite flagged sentences → verify)* → final action (§4).
public struct Orchestrator: Sendable {
    public var retriever: Retriever?
    public var generator: Generator
    public var verifier: Verifier
    public var judge: Judge?
    public var calibratedThreshold: Double
    public var topK = 6
    public var maxTokens = 400
    public var revision: Revision.Style = .targeted
    public var memory: (@Sendable () -> MemoryStats)?

    public static let answerSystem = "You are a helpful assistant. Answer using only the DOCUMENT. Be concise."
    public static let reviseSystem = "You are a careful editor. You correct answers so that every sentence is supported by the DOCUMENT."
    public static let abstainMessage = "I could not produce an answer that the documents support."

    public init(retriever: Retriever?, generator: Generator, verifier: Verifier, judge: Judge?,
                calibratedThreshold: Double, memory: (@Sendable () -> MemoryStats)? = nil) {
        self.retriever = retriever; self.generator = generator; self.verifier = verifier; self.judge = judge
        self.calibratedThreshold = calibratedThreshold; self.memory = memory
    }

    /// Input of one run. With `document` set (T1 measurements), retrieval is skipped; `task` replaces the question
    /// as the generation instruction.
    public struct Request: Sendable {
        public var question: String
        public var task: String?
        public var document: String?
        public var initialAnswer: String?
        public var compareWithJudge: Bool

        public init(question: String, task: String? = nil, document: String? = nil, initialAnswer: String? = nil,
                    compareWithJudge: Bool = true) {
            self.question = question; self.task = task; self.document = document
            self.initialAnswer = initialAnswer; self.compareWithJudge = compareWithJudge
        }
    }

    public func run(_ req: Request, policy: Policy) -> AsyncThrowingStream<LoopEvent, Error> {
        AsyncThrowingStream { cont in
            let task = Task {
                do {
                    let record = try await execute(req, policy: policy) { cont.yield($0) }
                    cont.yield(.finished(record))
                    cont.finish()
                } catch {
                    cont.finish(throwing: error)
                }
            }
            cont.onTermination = { _ in task.cancel() }
        }
    }

    public func execute(_ req: Request, policy: Policy, emit: (LoopEvent) -> Void = { _ in }) async throws -> QueryRecord {
        let t0 = Date()
        var passages: [Passage] = []
        var document = req.document ?? ""
        var timings = Timings()
        if req.document == nil, let retriever {
            emit(.stage("Retrieving"))
            let t = Date()
            passages = try await retriever.search(req.question, k: topK)
            timings.retrieval = Date().timeIntervalSince(t)
            document = Documents.compose(question: req.question, passages: passages)
            emit(.retrieved(passages, seconds: timings.retrieval))
        }
        var rec = QueryRecord(question: req.question, task: req.task, policy: policy, verifier: verifier.name,
                              generator: generator.name, passages: passages, document: document)
        let tau = policy.tau(calibrated: calibratedThreshold)

        // Round 0: the first answer.
        var text: String
        var stats = GenerationStats()
        if let given = req.initialAnswer {
            text = given
        } else {
            emit(.stage("Generating"))
            text = ""
            let user = req.task.map { "\($0)\n\nDOCUMENT:\n\(document)" } ?? "DOCUMENT:\n\(document)\n\nQUESTION: \(req.question)"
            for try await ev in generator.generate(system: Self.answerSystem, user: user, maxTokens: maxTokens) {
                switch ev {
                case .text(let t):
                    text += t
                    emit(.partial(round: 0, text: text))
                case .done(let s): stats = s
                }
            }
            text = text.trimmingCharacters(in: .whitespacesAndNewlines)
        }
        timings.generation.append(stats.seconds)
        emit(.stage("Verifying with GroundOne"))
        var verdicts = try await verify(document: document, answer: text, tau: tau)
        timings.verification.append(verdicts.seconds)
        var draft = Draft(round: 0, text: text, verdicts: verdicts, generation: stats, rewriteRequest: [], rewriteRaw: nil)
        rec.drafts.append(draft)
        emit(.draft(draft))

        if req.compareWithJudge, let judge {
            emit(.stage("LLM judge (comparison)"))
            let segs = verdicts.sentences
            let j = try await judge.judge(document: document, sentences: segs.map(\.text),
                                          check: segs.filter(\.scored).map(\.index))
            rec.judge = j
            timings.judge = j.seconds
            emit(.judge(j))
        }

        // Rounds 1...max_attempts: rewrite only the blocking sentences, keep the others fixed, verify the whole answer.
        var round = 0
        while round < policy.maxAttempts {
            let flagged = verdicts.sentences.filter { policy.isBlocking($0.label) }
            if flagged.isEmpty { break }
            round += 1
            emit(.stage("Revising (round \(round))"))
            var raw: String
            var s = GenerationStats()
            if revision == .targeted {
                // One short request per flagged sentence, with only the relevant excerpt of the document.
                var repl: [Int: String] = [:]
                var logs: [String] = []
                for f in flagged {
                    let (out, st) = try await generator.complete(system: Revision.sentenceSystem,
                                                                 user: Revision.sentencePrompt(f, document: document),
                                                                 maxTokens: 90)
                    s.generatedTokens += st.generatedTokens
                    s.seconds += st.seconds
                    s.promptTokens += st.promptTokens
                    let fixed = Revision.cleanSentence(out)
                    logs.append("[\(f.index + 1)] \(fixed ?? "DELETE")")
                    // A contradicted sentence is corrected, never deleted: an unusable reply keeps it for the next round.
                    if let fixed { repl[f.index] = fixed } else if f.label != .contradicted { repl[f.index] = "" }
                }
                raw = logs.joined(separator: "\n")
                text = Revision.replace(repl, in: text, sentences: verdicts.sentences)
            } else {
                let user = Revision.prompt(document: document, question: req.task ?? req.question,
                                           sentences: verdicts.sentences, flagged: flagged)
                (raw, s) = try await generator.complete(system: Self.reviseSystem, user: user,
                                                        maxTokens: 60 * flagged.count + 40)
                text = Revision.apply(raw, to: text, sentences: verdicts.sentences, flagged: flagged.map(\.index))
            }
            emit(.partial(round: round, text: text))
            timings.generation.append(s.seconds)
            emit(.stage("Verifying with GroundOne (round \(round))"))
            verdicts = try await verify(document: document, answer: text, tau: tau)
            timings.verification.append(verdicts.seconds)
            draft = Draft(round: round, text: text, verdicts: verdicts, generation: s,
                          rewriteRequest: flagged.map(\.index), rewriteRaw: raw)
            rec.drafts.append(draft)
            emit(.draft(draft))
        }

        let blocking = verdicts.sentences.filter { policy.isBlocking($0.label) }
        if blocking.isEmpty {
            rec.status = .accepted
            rec.displayed = text
        } else {
            switch policy.onFailure {
            case .highlight:
                rec.status = .highlighted
                rec.displayed = text
            case .hide:
                rec.status = .hidden
                rec.displayed = Revision.remove(blocking.map { ($0.start, $0.end) }, from: text)
            case .abstain:
                rec.status = .abstained
                rec.displayed = Self.abstainMessage
            }
        }
        timings.total = Date().timeIntervalSince(t0)
        rec.timings = timings
        rec.memory = memory?()
        return rec
    }

    /// Segment with the training rule, one GroundOne pass, labels by the policy's threshold.
    func verify(document: String, answer: String, tau: Double) async throws -> Verdicts {
        let segs = Segmenter.segment(answer)
        var v = try await verifier.verify(document: document, sentences: segs)
        v.threshold = tau
        for i in v.sentences.indices where v.sentences[i].scored {
            if let p = v.sentences[i].probs { v.sentences[i].label = Decision.decide(p, threshold: tau) }
        }
        return v
    }
}

public enum Documents {
    /// The document GroundOne reads: the question and the numbered passages, in the RAGTruth QA layout it was trained on.
    public static func compose(question: String, passages: [Passage]) -> String {
        let body = passages.enumerated().map { "passage \($0.offset + 1): \($0.element.text)" }.joined(separator: "\n\n")
        return "Question: \(question)\n\n\(body)"
    }
}

/// Targeted rewriting (edit only what is flagged, as RARR does).
public enum Revision {
    /// targeted: one instruction per error type with the relevant excerpt of the document (default);
    /// uniform: the same instruction for every flagged sentence (kept as a control for the case study).
    public enum Style: String, Sendable { case targeted, uniform }

    public static let sentenceSystem = "You correct one sentence so that it agrees with a source text. You reply with the sentence only."

    /// Contradicted: correct the wrong facts from the source (no deletion). Not stated: rewrite from what the source says
    /// on that point, or DELETE if it says nothing on it.
    public static func sentencePrompt(_ f: SentenceVerdict, document: String) -> String {
        let excerpt = Evidence.excerpt(for: f.text, in: document, maxSentences: 3)
        if f.label == .contradicted {
            return """
                SOURCE: "\(excerpt)"

                SENTENCE: "\(f.text)"

                The SENTENCE contradicts the SOURCE. Write the corrected SENTENCE: keep its meaning and wording, but replace the wrong facts (numbers, names, dates, places) with the ones in the SOURCE. Write only the corrected sentence.
                """
        }
        return """
            SOURCE: "\(excerpt)"

            SENTENCE: "\(f.text)"

            The SOURCE does not state the SENTENCE. If the SOURCE says something on the same point, rewrite the SENTENCE so that it says only what the SOURCE says. If the SOURCE says nothing on that point, write DELETE. Write only the sentence, or DELETE.
            """
    }

    /// First line of the reply, without quotes or a leading label; nil for DELETE or an empty reply.
    public static func cleanSentence(_ reply: String) -> String? {
        var t = reply.trimmingCharacters(in: .whitespacesAndNewlines)
        t = t.components(separatedBy: .newlines).first { !$0.trimmingCharacters(in: .whitespaces).isEmpty } ?? ""
        t = t.replacingOccurrences(of: #"^\[\d+\]\s*"#, with: "", options: .regularExpression)
        t = t.replacingOccurrences(of: #"^\(?passage \d+\)?\s*:?\s*"#, with: "", options: [.regularExpression, .caseInsensitive])
        t = t.replacingOccurrences(of: #"^(corrected sentence|sentence|rewritten sentence)\s*:\s*"#, with: "",
                                   options: [.regularExpression, .caseInsensitive])
        t = t.trimmingCharacters(in: CharacterSet(charactersIn: "\"“”' ").union(.whitespaces))
        if t.isEmpty || t.uppercased().hasPrefix("DELETE") { return nil }
        return t
    }

    /// Replaces sentences in place by index ("" deletes), layout kept.
    public static func replace(_ repl: [Int: String], in answer: String, sentences: [SentenceVerdict]) -> String {
        var out = answer as NSString
        for s in sentences.sorted(by: { $0.start > $1.start }) {
            guard let r = repl[s.index] else { continue }
            out = out.replacingCharacters(in: NSRange(location: s.start, length: s.end - s.start), with: r) as NSString
        }
        return tidy(out as String)
    }

    public static func prompt(document: String, question: String, sentences: [SentenceVerdict],
                              flagged: [SentenceVerdict]) -> String {
        let numbered = sentences.map { "[\($0.index + 1)] \($0.text)" }.joined(separator: "\n")
        let problems = flagged.map {
            "[\($0.index + 1)] " + ($0.label == .contradicted ? "is contradicted by the DOCUMENT." : "is not stated in the DOCUMENT.")
        }.joined(separator: "\n")
        return """
            DOCUMENT:
            \(document)

            TASK: \(question)

            ANSWER (numbered sentences):
            \(numbered)

            A verifier found problems in these sentences:
            \(problems)

            Rewrite only these sentences so that each one states only what the DOCUMENT says. If the DOCUMENT gives no basis for a sentence, write DELETE. Reply with one line per sentence, in the form '[number] new sentence' or '[number] DELETE', and nothing else.
            """
    }

    static let line = try! NSRegularExpression(pattern: #"^\s*\[(\d+)\]\s*[:.\-]?\s*(.*)$"#)

    /// Parses '[n] text' / '[n] DELETE' lines; replaces the flagged sentences in place (layout kept), others untouched.
    public static func apply(_ raw: String, to answer: String, sentences: [SentenceVerdict], flagged: [Int]) -> String {
        var repl: [Int: String] = [:]
        for l in raw.components(separatedBy: .newlines) {
            let ns = l as NSString
            guard let m = line.firstMatch(in: l, range: NSRange(location: 0, length: ns.length)),
                  let n = Int(ns.substring(with: m.range(at: 1))), flagged.contains(n - 1), repl[n - 1] == nil else { continue }
            var t = ns.substring(with: m.range(at: 2)).trimmingCharacters(in: .whitespaces)
            if t.uppercased().hasPrefix("DELETE") { t = "" }
            repl[n - 1] = t
        }
        var out = answer as NSString
        for s in sentences.sorted(by: { $0.start > $1.start }) {
            guard let r = repl[s.index] else { continue }
            out = out.replacingCharacters(in: NSRange(location: s.start, length: s.end - s.start), with: r) as NSString
        }
        return tidy(out as String)
    }

    public static func remove(_ ranges: [(Int, Int)], from text: String) -> String {
        var out = text as NSString
        for (a, b) in ranges.sorted(by: { $0.0 > $1.0 }) {
            out = out.replacingCharacters(in: NSRange(location: a, length: b - a), with: "") as NSString
        }
        return tidy(out as String)
    }

    /// Removes double spaces and empty bullets left by deletions; keeps paragraph breaks (at most one blank line).
    static func tidy(_ s: String) -> String {
        s.components(separatedBy: "\n")
            .map { $0.replacingOccurrences(of: #" {2,}"#, with: " ", options: .regularExpression)
                .trimmingCharacters(in: .whitespaces) }
            .filter { !["-", "*", "•"].contains($0) }
            .joined(separator: "\n")
            .replacingOccurrences(of: #"\n{3,}"#, with: "\n\n", options: .regularExpression)
            .trimmingCharacters(in: .whitespacesAndNewlines)
    }
}

/// The part of a document closest to a sentence: its best-matching sentences by shared word stems weighted by rarity
/// (IDF), with the next sentence for context. Used to point the generator at the evidence when rewriting.
public enum Evidence {
    public static func excerpt(for sentence: String, in document: String, maxSentences: Int = 2) -> String {
        let spans = sentences(of: document)
        guard !spans.isEmpty else { return "" }
        let scores = scoresIDF(sentence, spans.map(\.1))
        let best = scores.indices.max { scores[$0] < scores[$1] }!
        let lo = maxSentences > 2 ? max(0, best - 1) : best
        let picked = spans[lo..<min(lo + maxSentences, spans.count)].map(\.1)
        return picked.joined(separator: " ").replacingOccurrences(of: #"\s+"#, with: " ", options: .regularExpression)
            .trimmingCharacters(in: .whitespaces)
    }

    public static func sentences(of text: String) -> [(NSRange, String)] {
        let tok = NLTokenizer(unit: .sentence)
        tok.string = text
        var out: [(NSRange, String)] = []
        tok.enumerateTokens(in: text.startIndex..<text.endIndex) { r, _ in
            out.append((NSRange(r, in: text), String(text[r])))
            return true
        }
        return out
    }

    public static func scoresIDF(_ query: String, _ candidates: [String]) -> [Double] {
        let stems = candidates.map(stemSet)
        var df: [String: Int] = [:]
        for s in stems { for w in s { df[w, default: 0] += 1 } }
        let n = Double(candidates.count)
        let target = stemSet(query)
        return stems.map { s in s.intersection(target).map { Foundation.log(1 + n / Double(df[$0]!)) }.reduce(0, +) }
    }

    /// Lower-cased words longer than two characters, cut to six (a crude stem: calibrates ~ calibrating).
    public static func stemSet(_ s: String) -> Set<String> {
        Set(s.lowercased().components(separatedBy: CharacterSet.alphanumerics.inverted).filter { $0.count > 2 }
            .map { String($0.prefix(6)) })
    }
}
