import Foundation
import GroundOneCore
import MLX
import MLXEmbedders
import MLXLMCommon

/// Dense embeddings for retrieval: a small retrieval-trained model on MLX (decision 3), loaded from the local cache.
public final class Embedder: @unchecked Sendable {
    public let container: EmbedderModelContainer
    public let repo: String
    /// Query prefix the model was trained with (asymmetric retrieval); passages are embedded as is.
    let queryPrefix: String

    public static func load(repo: String = ModelCatalog.embedder) async throws -> Embedder {
        Runtime.configure()
        let dir = try Workspace.snapshot(repo)
        let container = try await EmbedderModelFactory.shared.loadContainer(from: dir, using: TransformersLoader())
        let prefix = repo.contains("Qwen3-Embedding")
            ? "Instruct: Given a question, retrieve passages that answer the question\nQuery:"
            : (repo.contains("bge") ? "Represent this sentence for searching relevant passages: " : "")
        return Embedder(container: container, repo: repo, queryPrefix: prefix)
    }

    init(container: EmbedderModelContainer, repo: String, queryPrefix: String) {
        self.container = container; self.repo = repo; self.queryPrefix = queryPrefix
    }

    public func embed(query: String) async throws -> [Float] { try await embed([queryPrefix + query])[0] }

    /// L2-normalised vectors, one forward pass per text (no padding, so pooling sees only real tokens).
    public func embed(_ texts: [String], maxTokens: Int = 512) async throws -> [[Float]] {
        try await container.perform { context in
            texts.map { text in
                var ids = context.tokenizer.encode(text: text, addSpecialTokens: true)
                if ids.count > maxTokens { ids = Array(ids.prefix(maxTokens)) }
                let x = MLXArray(ids.map { Int32($0) }).expandedDimensions(axis: 0)
                let out = context.model(x, positionIds: nil, tokenTypeIds: MLXArray.zeros(like: x), attentionMask: MLXArray.ones(like: x))
                let v = context.pooling(out, normalize: true)
                eval(v)
                return v[0].asArray(Float.self)
            }
        }
    }
}
