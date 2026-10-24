import Foundation

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
    public var topK = 5
    public var maxTokens = 400
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
            emit(.stage("Generative judge (comparison)"))
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
            let user = Revision.prompt(document: document, question: req.task ?? req.question,
                                       sentences: verdicts.sentences, flagged: flagged)
            let (raw, s) = try await generator.complete(system: Self.reviseSystem, user: user,
                                                        maxTokens: 60 * flagged.count + 40)
            text = Revision.apply(raw, to: text, sentences: verdicts.sentences, flagged: flagged.map(\.index))
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

    static func tidy(_ s: String) -> String {
        s.components(separatedBy: "\n")
            .map { $0.replacingOccurrences(of: #" {2,}"#, with: " ", options: .regularExpression)
                .trimmingCharacters(in: .whitespaces) }
            .filter { !$0.isEmpty && !["-", "*", "•"].contains($0) }
            .joined(separator: "\n")
    }
}
