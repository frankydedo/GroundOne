import Foundation
import GroundOneCore
import MLX
import MLXLLM
import MLXLMCommon

/// Greedy generation from chat messages (temperature 0, as `mlx_lm.generate` in the thesis measurements).
enum Greedy {
    static func run(_ container: ModelContainer, messages: [[String: any Sendable]], maxTokens: Int,
                    onChunk: @Sendable (String) -> Void) async throws -> (String, GenerationStats) {
        let tokenizer = await container.tokenizer
        let prompt = try tokenizer.applyChatTemplate(messages: messages)
        let input = LMInput(tokens: MLXArray(prompt.map { Int32($0) }))
        let t0 = Date()
        var first: Double?
        var text = ""
        var stats = GenerationStats(promptTokens: prompt.count)
        let stream = try await container.generate(input: input,
                                                  parameters: GenerateParameters(maxTokens: maxTokens, temperature: 0))
        for await ev in stream {
            switch ev {
            case .chunk(let c):
                if first == nil { first = Date().timeIntervalSince(t0) }
                text += c
                onChunk(c)
            case .info(let info):
                stats.generatedTokens = info.generationTokenCount
            default: break
            }
        }
        stats.timeToFirstToken = first ?? 0
        stats.seconds = Date().timeIntervalSince(t0)
        return (text, stats)
    }
}

/// The answer generator: Qwen2.5-3B-Instruct 4-bit (decision 2), separate from GroundOne's weights.
public final class MLXGenerator: Generator, @unchecked Sendable {
    public let container: ModelContainer
    public let name: String

    public static func load(repo: String = ModelCatalog.generator) async throws -> MLXGenerator {
        MLXGenerator(container: try await ModelCatalog.loadLLM(repo), name: repo)
    }

    init(container: ModelContainer, name: String) { self.container = container; self.name = name }

    public func generate(system: String, user: String, maxTokens: Int) -> AsyncThrowingStream<GenerationEvent, Error> {
        let container = self.container
        return AsyncThrowingStream { cont in
            let task = Task {
                do {
                    let (_, stats) = try await Greedy.run(
                        container, messages: [["role": "system", "content": system], ["role": "user", "content": user]],
                        maxTokens: maxTokens) { cont.yield(.text($0)) }
                    cont.yield(.done(stats))
                    cont.finish()
                } catch {
                    cont.finish(throwing: error)
                }
            }
            cont.onTermination = { _ in task.cancel() }
        }
    }
}
