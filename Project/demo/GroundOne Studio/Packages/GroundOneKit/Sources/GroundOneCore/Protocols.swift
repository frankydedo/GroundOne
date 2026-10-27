import Foundation

/// The ports of the architecture (demo_architecture.md §3). Core only knows these; engines implement them.
public protocol Retriever: Sendable {
    func search(_ query: String, k: Int) async throws -> [Passage]
}

public protocol Generator: Sendable {
    var name: String { get }
    /// Streams text chunks, then one `.done` with the statistics.
    func generate(system: String, user: String, maxTokens: Int) -> AsyncThrowingStream<GenerationEvent, Error>
}

/// Implemented by GroundOne: one forward pass per call.
public protocol Verifier: Sendable {
    var name: String { get }
    func verify(document: String, sentences: [Segment]) async throws -> Verdicts
    /// Starts reading `document` into the verifier's prefix cache in the background (default: nothing).
    func prefetch(document: String)
}

extension Verifier {
    public func prefetch(document: String) {}
}

/// The generative judge of the comparison mode (B0a terse prompt, base model without the adapter).
public protocol Judge: Sendable {
    var name: String { get }
    func judge(document: String, sentences: [String], check: [Int]) async throws -> JudgeVerdicts
}

public protocol Attributor: Sendable {
    func sources(for sentence: SentenceVerdict, passages: [Passage]) async throws -> [SourceLink]
}

/// Token encoding as the training code does it (`tokenizer.encode(text, add_special_tokens=False)`).
public protocol TokenEncoder: Sendable {
    func encode(_ text: String) -> [Int]
}

extension Generator {
    /// Collects the whole stream.
    public func complete(system: String, user: String, maxTokens: Int) async throws -> (String, GenerationStats) {
        var text = ""
        var stats = GenerationStats()
        for try await event in generate(system: system, user: user, maxTokens: maxTokens) {
            switch event {
            case .text(let t): text += t
            case .done(let s): stats = s
            }
        }
        return (text, stats)
    }
}
