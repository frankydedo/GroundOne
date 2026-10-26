import Foundation

/// The three verdicts, in the letter order of the readout (A, B, C).
public enum Label: String, Codable, Sendable, CaseIterable {
    case supported
    case contradicted
    case notMentioned = "not_mentioned"

    public init(index: Int) { self = Label.allCases[index] }
    public var index: Int { Label.allCases.firstIndex(of: self)! }
    public var letter: String { ["A", "B", "C"][index] }
    public var display: String {
        switch self {
        case .supported: "supported"
        case .contradicted: "contradicted"
        case .notMentioned: "not mentioned"
        }
    }
}

/// A retrieved piece of a source file. `range` is the character range in the page (PDF) or file text.
public struct Passage: Codable, Sendable, Hashable, Identifiable {
    public var id: String
    public var docID: String
    public var title: String
    public var text: String
    public var fileURL: URL?
    public var page: Int?
    public var start: Int
    public var end: Int
    public var score: Double

    public init(id: String, docID: String, title: String, text: String, fileURL: URL? = nil, page: Int? = nil,
                start: Int = 0, end: Int = 0, score: Double = 0) {
        self.id = id; self.docID = docID; self.title = title; self.text = text; self.fileURL = fileURL
        self.page = page; self.start = start; self.end = end; self.score = score
    }
}

/// Verdict on one answer sentence. Unscored sentences (no checkable content) keep their place but carry no verdict.
public struct SentenceVerdict: Codable, Sendable, Hashable {
    public var index: Int
    public var text: String
    public var start: Int
    public var end: Int
    public var scored: Bool
    public var logits: [Double]?
    public var probs: [Double]?
    public var label: Label?

    public init(index: Int, text: String, start: Int, end: Int, scored: Bool, logits: [Double]? = nil,
                probs: [Double]? = nil, label: Label? = nil) {
        self.index = index; self.text = text; self.start = start; self.end = end; self.scored = scored
        self.logits = logits; self.probs = probs; self.label = label
    }

    public var pSupported: Double? { probs?[0] }
}

public struct Verdicts: Codable, Sendable {
    public var sentences: [SentenceVerdict]
    public var inputTokens: Int
    public var seconds: Double
    public var threshold: Double
    public var model: String
    /// Tokens read from the prefix cache (instructions + document already read for an earlier verification), D32.
    public var cachedTokens: Int?

    public init(sentences: [SentenceVerdict], inputTokens: Int, seconds: Double, threshold: Double, model: String,
                cachedTokens: Int? = nil) {
        self.sentences = sentences; self.inputTokens = inputTokens; self.seconds = seconds
        self.threshold = threshold; self.model = model; self.cachedTokens = cachedTokens
    }

    public var scored: [SentenceVerdict] { sentences.filter(\.scored) }
}

/// Output of the generative judge (B0a terse prompt): one letter per checked sentence, or nil if unparsed.
public struct JudgeVerdicts: Codable, Sendable {
    public var labels: [Int: Label?]
    public var rawText: String
    public var inputTokens: Int
    public var generatedTokens: Int
    public var seconds: Double
    /// Prompt tokens read from the judge's own prefix cache (same policy as GroundOne's), D32.
    public var cachedTokens: Int?

    public init(labels: [Int: Label?], rawText: String, inputTokens: Int, generatedTokens: Int, seconds: Double,
                cachedTokens: Int? = nil) {
        self.labels = labels; self.rawText = rawText; self.inputTokens = inputTokens
        self.generatedTokens = generatedTokens; self.seconds = seconds; self.cachedTokens = cachedTokens
    }
}

/// A link from an answer sentence to the passage span that supports or contradicts it (§4c; demonstrative only).
public struct SourceLink: Codable, Sendable, Hashable {
    public var sentence: Int
    public var kind: Label
    public var passage: Passage
    public var probability: Double
    public var spanStart: Int
    public var spanEnd: Int
    public var spanText: String

    public init(sentence: Int, kind: Label, passage: Passage, probability: Double, spanStart: Int, spanEnd: Int,
                spanText: String) {
        self.sentence = sentence; self.kind = kind; self.passage = passage; self.probability = probability
        self.spanStart = spanStart; self.spanEnd = spanEnd; self.spanText = spanText
    }
}

public struct GenerationStats: Codable, Sendable {
    public var promptTokens: Int
    public var generatedTokens: Int
    public var timeToFirstToken: Double
    public var seconds: Double

    public init(promptTokens: Int = 0, generatedTokens: Int = 0, timeToFirstToken: Double = 0, seconds: Double = 0) {
        self.promptTokens = promptTokens; self.generatedTokens = generatedTokens
        self.timeToFirstToken = timeToFirstToken; self.seconds = seconds
    }
}

public enum GenerationEvent: Sendable {
    case text(String)
    case done(GenerationStats)
}
