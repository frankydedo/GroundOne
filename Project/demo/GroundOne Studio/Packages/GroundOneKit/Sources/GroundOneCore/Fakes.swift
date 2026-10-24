import Foundation

/// Deterministic stand-ins for the engines: used by the UI tests (launch argument `-fakeEngines YES`) so the interface
/// can be exercised in seconds without loading models. Never used for any reported number.
public enum Fakes {
    public struct Retriever: GroundOneCore.Retriever {
        public let passages: [Passage]
        public init(passages: [Passage] = Fakes.passages) { self.passages = passages }
        public func search(_ query: String, k: Int) async throws -> [Passage] { Array(passages.prefix(k)) }
    }

    public struct Generator: GroundOneCore.Generator {
        public let name = "fake generator"
        public init() {}
        public func generate(system: String, user: String, maxTokens: Int) -> AsyncThrowingStream<GenerationEvent, Error> {
            let reply = user.contains("SENTENCE:")
                ? "The method was evaluated on three benchmarks."
                : "LoRA freezes the pretrained weights. It injects trainable low-rank matrices into each layer. The method was evaluated on twelve benchmarks in 2031."
            return AsyncThrowingStream { c in
                Task {
                    for w in reply.split(separator: " ", omittingEmptySubsequences: false) {
                        c.yield(.text(String(w) + " "))
                        try? await Task.sleep(for: .milliseconds(8))
                    }
                    c.yield(.done(GenerationStats(promptTokens: 300, generatedTokens: 30, timeToFirstToken: 0.05, seconds: 0.4)))
                    c.finish()
                }
            }
        }
    }

    /// Supported iff most content words of the sentence occur in the document; numbers absent from it → not mentioned.
    public struct Verifier: GroundOneCore.Verifier {
        public let name = "fake verifier"
        public init() {}
        public func verify(document: String, sentences: [Segment]) async throws -> Verdicts {
            let doc = Set(document.lowercased().components(separatedBy: CharacterSet.alphanumerics.inverted))
            let v = sentences.enumerated().map { i, s -> SentenceVerdict in
                guard s.checkable else { return SentenceVerdict(index: i, text: s.text, start: s.start, end: s.end, scored: false) }
                let w = s.text.lowercased().components(separatedBy: CharacterSet.alphanumerics.inverted).filter { $0.count > 2 }
                let share = Double(w.filter(doc.contains).count) / Double(max(w.count, 1))
                let p = share > 0.8 ? [0.97, 0.01, 0.02] : (share > 0.6 ? [0.3, 0.6, 0.1] : [0.1, 0.1, 0.8])
                return SentenceVerdict(index: i, text: s.text, start: s.start, end: s.end, scored: true, logits: p.map { log($0) },
                                       probs: p, label: Decision.decide(p, threshold: 0.925))
            }
            return Verdicts(sentences: v, inputTokens: 400, seconds: 0.05, threshold: 0.925, model: name)
        }
    }

    public struct Judge: GroundOneCore.Judge {
        public let name = "fake judge"
        public init() {}
        public func judge(document: String, sentences: [String], check: [Int]) async throws -> JudgeVerdicts {
            var l: [Int: Label?] = [:]
            for i in check { l[i] = i == check.last ? .contradicted : .supported }
            return JudgeVerdicts(labels: l, rawText: check.map { "\($0 + 1): A" }.joined(separator: "\n"),
                                 inputTokens: 420, generatedTokens: 4 * check.count, seconds: 0.8)
        }
    }

    public static let passages = [
        Passage(id: "lora#0-0", docID: "Hu 2022 - LoRA_ingested.pdf", title: "Hu 2022 - LoRA",
                text: "LoRA freezes the pretrained model weights and injects trainable rank decomposition matrices into each layer of the Transformer architecture. The method was evaluated on three benchmarks.",
                page: 0, start: 0, end: 180),
        Passage(id: "lora#1-0", docID: "Hu 2022 - LoRA_ingested.pdf", title: "Hu 2022 - LoRA",
                text: "Compared to GPT-3 175B fine-tuned with Adam, LoRA can reduce the number of trainable parameters by 10,000 times and the GPU memory requirement by 3 times.",
                page: 1, start: 0, end: 160),
    ]
}
