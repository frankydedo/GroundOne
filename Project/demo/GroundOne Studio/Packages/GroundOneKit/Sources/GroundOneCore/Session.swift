import Foundation

/// The app's step-by-step flow (author, 2026-10-25): the generator's native answer first; verification only on request
/// (GroundOne alone, or GroundOne and the generative judge); rewriting of flagged or selected sentences on request.
/// Every step produces a new `Version`; nothing is changed without the user asking.
public struct Version: Codable, Sendable, Identifiable {
    public enum Origin: String, Codable, Sendable { case generated, fixed }

    public var id = UUID()
    public var origin: Origin
    public var text: String
    public var generation: GenerationStats
    /// Sentence indices of the previous version that were rewritten (fixed versions only).
    public var rewritten: [Int] = []
    public var rewriteLog: String?
    /// Sentence indices of the previous version that the generator only repeated, even after the retry: kept, flagged.
    public var unchanged: [Int]?
    public var verdicts: Verdicts?
    public var judge: JudgeVerdicts?

    public init(origin: Origin, text: String, generation: GenerationStats) {
        self.origin = origin; self.text = text; self.generation = generation
    }

    /// Sentences of the text, with verdicts once verified.
    public var sentences: [SentenceVerdict] {
        verdicts?.sentences ?? Segmenter.segment(text).enumerated().map {
            SentenceVerdict(index: $0.offset, text: $0.element.text, start: $0.element.start, end: $0.element.end,
                            scored: $0.element.checkable)
        }
    }
}

/// One question in the app and its versions; what the audit log stores and the Stats view reads.
public struct StudioRecord: Codable, Sendable, Identifiable {
    public var id = UUID()
    public var date = Date()
    public var question: String
    public var passages: [Passage] = []
    public var document: String = ""
    public var retrievalSeconds: Double = 0
    public var versions: [Version] = []
    public var verifier: String
    public var generator: String
    public var policy: String
    public var memory: MemoryStats?
    /// Last action, for the audit log ("generated", "verified", "verified+judge", "fixed").
    public var event: String = "generated"

    public init(question: String, verifier: String, generator: String, policy: String) {
        self.question = question; self.verifier = verifier; self.generator = generator; self.policy = policy
    }
}

public enum LibraryPrompt {
    public static let system = "You are a helpful assistant who writes clear, well-organised answers using only the DOCUMENTS you are given."

    public static func user(question: String, document: String) -> String {
        """
        DOCUMENTS:
        \(document)

        QUESTION: \(question)

        Write a complete, detailed answer of at least 300 words (aim for about 400), organised in four or five paragraphs: \
        an opening paragraph that answers the question directly, then one paragraph for each aspect the DOCUMENTS cover, \
        then a short closing paragraph. Use only information from the DOCUMENTS, in your own words, and include the \
        specific facts they give (names, numbers, dates). Do not use Markdown, headings, bullet lists, links or code.
        """
    }

    public static let maxTokens = 900

    /// Markdown the generator may still emit is removed before the answer is shown and verified.
    public static func clean(_ text: String) -> String {
        text.components(separatedBy: "\n").map { line -> String in
            var l = line.replacingOccurrences(of: #"^\s{0,3}#{1,6}\s*"#, with: "", options: .regularExpression)
            l = l.replacingOccurrences(of: #"^\s*[-*•]\s+"#, with: "", options: .regularExpression)
            l = l.replacingOccurrences(of: "**", with: "").replacingOccurrences(of: "__", with: "")
            return l
        }.joined(separator: "\n").replacingOccurrences(of: #"\n{3,}"#, with: "\n\n", options: .regularExpression)
            .trimmingCharacters(in: .whitespacesAndNewlines)
    }
}

/// The steps, on top of the same engines as the automatic loop.
public struct StudioSession: Sendable {
    public var retriever: Retriever
    public var generator: Generator
    public var verifier: Verifier
    public var judge: Judge
    public var calibratedThreshold: Double
    public var topK = 6

    public init(retriever: Retriever, generator: Generator, verifier: Verifier, judge: Judge, calibratedThreshold: Double) {
        self.retriever = retriever; self.generator = generator; self.verifier = verifier; self.judge = judge
        self.calibratedThreshold = calibratedThreshold
    }

    /// Retrieval and the native answer, streamed through `partial`.
    public func answer(_ question: String, into rec: inout StudioRecord,
                       partial: @Sendable (String) -> Void) async throws -> Version {
        let t = Date()
        rec.passages = try await retriever.search(question, k: topK)
        rec.retrievalSeconds = Date().timeIntervalSince(t)
        rec.document = Documents.compose(question: question, passages: rec.passages)
        var text = ""
        var stats = GenerationStats()
        for try await ev in generator.generate(system: LibraryPrompt.system,
                                               user: LibraryPrompt.user(question: question, document: rec.document),
                                               maxTokens: LibraryPrompt.maxTokens) {
            switch ev {
            case .text(let c):
                text += c
                partial(text)
            case .done(let s): stats = s
            }
        }
        return Version(origin: .generated, text: LibraryPrompt.clean(text), generation: stats)
    }

    /// One GroundOne pass over the whole answer (all sentences at once), labels by τ; optionally the judge too.
    public func verify(_ v: Version, document: String, threshold: Double? = nil, withJudge: Bool) async throws -> Version {
        var out = v
        var verdicts = try await verifier.verify(document: document, sentences: Segmenter.segment(v.text))
        let tau = threshold ?? calibratedThreshold
        verdicts.threshold = tau
        for i in verdicts.sentences.indices where verdicts.sentences[i].scored {
            if let p = verdicts.sentences[i].probs { verdicts.sentences[i].label = Decision.decide(p, threshold: tau) }
        }
        out.verdicts = verdicts
        if withJudge {
            out.judge = try await judge.judge(document: document, sentences: verdicts.sentences.map(\.text),
                                              check: verdicts.sentences.filter(\.scored).map(\.index))
        }
        return out
    }

    /// Rewrites the given sentences (one short request each, by error type; unverified sentences are treated as not
    /// stated) and returns the new, unverified version.
    public func fix(_ v: Version, indices: [Int], document: String) async throws -> Version {
        let sentences = v.sentences
        var repl: [Int: String] = [:]
        var log: [String] = []
        var unchanged: [Int] = []
        var stats = GenerationStats()
        for i in indices where sentences.indices.contains(i) {
            var s = sentences[i]
            if s.label == nil || s.label == .supported { s.label = .notMentioned }
            let (fixed, outcome, st) = try await Revision.rewrite(s, document: document, generator: generator)
            stats.generatedTokens += st.generatedTokens
            stats.promptTokens += st.promptTokens
            stats.seconds += st.seconds
            log.append("[\(i + 1)] " + (outcome == .rewritten ? fixed! : outcome.rawValue.uppercased()))
            if outcome == .unchanged { unchanged.append(i) }
            if let fixed { repl[i] = fixed }
        }
        var nv = Version(origin: .fixed, text: Revision.replace(repl, in: v.text, sentences: sentences), generation: stats)
        nv.rewritten = indices
        nv.rewriteLog = log.joined(separator: "\n")
        nv.unchanged = unchanged.isEmpty ? nil : unchanged
        return nv
    }
}
