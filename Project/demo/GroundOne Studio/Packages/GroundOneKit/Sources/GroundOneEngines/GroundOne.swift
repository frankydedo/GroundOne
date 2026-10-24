import Foundation
import GroundOneCore
import MLX
import MLXLLM
import MLXLMCommon
import MLXNN

/// GroundOne in-process: Qwen2.5 8-bit base + LoRA adapter, design-(b) prompt, A/B/C logits read at the markers
/// (`readout.py`), calibration and the served threshold from `calibration.json`.
public final class GroundOneModel: @unchecked Sendable {
    public let info: ModelCatalog.VerifierInfo
    public let container: ModelContainer
    let adapter: LoRAContainer
    public let encoder: PieceEncoder
    public let letterIDs: [Int]
    private let lock = NSLock()
    private var adapterLoaded = true

    public var name: String { "GroundOne \(info.run)" }

    public static func load(run: String) async throws -> GroundOneModel {
        let info = try ModelCatalog.verifier(run)
        let container = try await ModelCatalog.loadLLM(info.baseRepo)
        let adapter = try LoRAContainer.from(directory: info.adapterDir)
        try await container.perform { context in
            try adapter.load(into: context.model)
            context.model.train(false)
        }
        let tokenizer = await container.tokenizer
        let letters = try ["A", "B", "C"].map { L in
            let ids = tokenizer.encode(text: L, addSpecialTokens: false)
            guard ids.count == 1 else { throw ModelAdapterError.incompatibleModelType }
            return ids[0]
        }
        return GroundOneModel(info: info, container: container, adapter: adapter,
                              encoder: PieceEncoder(tokenizer: tokenizer), letterIDs: letters)
    }

    init(info: ModelCatalog.VerifierInfo, container: ModelContainer, adapter: LoRAContainer, encoder: PieceEncoder,
         letterIDs: [Int]) {
        self.info = info; self.container = container; self.adapter = adapter; self.encoder = encoder
        self.letterIDs = letterIDs
    }

    /// One forward pass; raw A/B/C logits at each marker position (float32, as `score_positions`).
    public func scorePositions(ids: [Int], positions: [Int]) async throws -> [[Double]] {
        guard !positions.isEmpty else { return [] }
        try await setAdapter(true)
        let letters = letterIDs
        return try await container.perform { context in
            guard let qwen = context.model as? Qwen2Model else { throw ModelAdapterError.incompatibleModelType }
            let x = MLXArray(ids.map { Int32($0) }).expandedDimensions(axis: 0)
            let h = qwen.model(x, cache: nil)[0]
            let rows = h[MLXArray(positions.map { Int32($0) })]
            let full = try Self.head(qwen, rows)
            let lg = full[0..., MLXArray(letters.map { Int32($0) })].asType(.float32)
            eval(lg)
            return lg.asArray(Float.self).chunked(3).map { $0.map(Double.init) }
        }
    }

    /// Output head: the tied embedding as a linear layer (Qwen2.5 0.5B and 3B), else the full forward is not needed.
    static func head(_ model: Qwen2Model, _ h: MLXArray) throws -> MLXArray {
        let modules = Dictionary(model.namedModules(), uniquingKeysWith: { a, _ in a })
        if let lm = modules["lm_head"] as? Linear { return lm(h) }
        guard let emb = modules["model.embed_tokens"] as? Embedding else { throw ModelAdapterError.incompatibleModelType }
        return emb.asLinear(h)
    }

    /// The local judge runs on the same weights with the adapter removed (`LoRAContainer.unload`).
    public func setAdapter(_ on: Bool) async throws {
        let change: Bool = lock.withLock {
            defer { adapterLoaded = on }
            return adapterLoaded != on
        }
        guard change else { return }
        let adapter = self.adapter
        try await container.perform { context in
            if on { try adapter.load(into: context.model) } else { adapter.unload(from: context.model) }
            context.model.train(false)
        }
    }
}

extension Array {
    func chunked(_ n: Int) -> [[Element]] {
        stride(from: 0, to: count, by: n).map { Array(self[$0..<Swift.min($0 + n, count)]) }
    }
}

/// The `Verifier` port implemented by GroundOne: segment-agnostic, one pass per answer.
public struct GroundOneVerifier: Verifier {
    public let model: GroundOneModel
    public var name: String { model.name }
    public init(model: GroundOneModel) { self.model = model }

    public func verify(document: String, sentences: [Segment]) async throws -> Verdicts {
        let t0 = Date()
        let (ids, pos) = MarkedPrompt.encode(model.encoder, document: document, sentences: sentences.map(\.text),
                                             scored: sentences.map(\.checkable))
        let logits = try await model.scorePositions(ids: ids, positions: pos)
        let cal = model.info.calibration
        var it = logits.makeIterator()
        let out = sentences.enumerated().map { i, s -> SentenceVerdict in
            guard s.checkable, let lg = it.next() else {
                return SentenceVerdict(index: i, text: s.text, start: s.start, end: s.end, scored: false)
            }
            let p = cal.probs(lg)
            return SentenceVerdict(index: i, text: s.text, start: s.start, end: s.end, scored: true, logits: lg,
                                   probs: p, label: Decision.decide(p, threshold: cal.threshold))
        }
        return Verdicts(sentences: out, inputTokens: ids.count, seconds: Date().timeIntervalSince(t0),
                        threshold: cal.threshold, model: name)
    }
}

/// B0a terse judge on GroundOne's base weights without the adapter: the judge measured in the thesis, locally.
public struct LocalJudge: Judge {
    public let model: GroundOneModel
    public var name: String { "Generative judge (\(model.info.baseRepo.split(separator: "/").last ?? ""), no adapter, B0a prompt)" }
    public init(model: GroundOneModel) { self.model = model }

    public func judge(document: String, sentences: [String], check: [Int]) async throws -> JudgeVerdicts {
        guard !check.isEmpty else { return JudgeVerdicts(labels: [:], rawText: "", inputTokens: 0, generatedTokens: 0, seconds: 0) }
        try await model.setAdapter(false)
        let user = JudgePrompt.user(document: document, sentences: sentences, check: check)
        let messages: [[String: any Sendable]] = [["role": "system", "content": MarkedPrompt.system], ["role": "user", "content": user]]
        let maxTokens = JudgePrompt.tokensPerSentence * check.count + 40
        let t0 = Date()
        let (text, stats) = try await Greedy.run(model.container, messages: messages, maxTokens: maxTokens) { _ in }
        let seconds = Date().timeIntervalSince(t0)
        try await model.setAdapter(true)
        return JudgeVerdicts(labels: JudgePrompt.parse(text, check: check), rawText: text,
                             inputTokens: stats.promptTokens, generatedTokens: stats.generatedTokens, seconds: seconds)
    }
}
