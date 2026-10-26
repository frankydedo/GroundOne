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
    /// Prefix cache (D32): KV states of the last few prompt heads (instructions + document), keyed by the adapter state
    /// and the head's token ids, least recently used first. Causal attention makes a cached head exactly reusable by
    /// any later prompt that starts with it: a rewritten answer on the same sources reads only the answer.
    private var prefixes: [(adapter: Bool, ids: [Int], state: PrefixState)] = []
    public var maxCachedPrefixes = 4
    public var prefixCacheEnabled = true

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

    /// One forward pass; raw A/B/C logits at each marker position (float32, as `score_positions`). With `prefixLength`
    /// the first tokens (instructions + document) come from the prefix cache when present, else they are read and
    /// cached; the pass then covers only the answer (`score_positions_from`). Returns the logits and the cached tokens.
    public func scorePositions(ids: [Int], positions: [Int], prefixLength: Int? = nil) async throws
        -> (logits: [[Double]], cachedTokens: Int)
    {
        guard !positions.isEmpty else { return ([], 0) }
        try await setAdapter(true)
        let letters = letterIDs
        let n = prefixCacheEnabled ? min(prefixLength ?? 0, positions.min()!) : 0
        let hit = n > 0 ? cachedPrefix(adapter: true, ids: Array(ids[..<n])) : nil
        let (logits, state) = try await container.perform { context -> ([[Double]], PrefixState?) in
            guard let qwen = context.model as? Qwen2Model else { throw ModelAdapterError.incompatibleModelType }
            let cache = n > 0 ? try Self.cache(context, qwen, ids: Array(ids[..<n]), state: hit) : nil
            let x = MLXArray(ids[n...].map { Int32($0) }).expandedDimensions(axis: 0)
            let h = qwen.model(x, cache: cache?.layers)[0]
            let rows = h[MLXArray(positions.map { Int32($0 - n) })]
            let full = try Self.head(qwen, rows)
            let lg = full[0..., MLXArray(letters.map { Int32($0) })].asType(.float32)
            eval(lg)
            return (lg.asArray(Float.self).chunked(3).map { $0.map(Double.init) }, cache?.fresh)
        }
        if let state { storePrefix(adapter: true, ids: Array(ids[..<n]), state: state) }
        return (logits, hit != nil ? n : 0)
    }

    /// KV caches holding `ids` already read: restored from `state`, or computed now (then `fresh` is the new state).
    static func cache(_ context: ModelContext, _ qwen: Qwen2Model, ids: [Int], state: PrefixState?) throws
        -> (layers: [KVCache], fresh: PrefixState?)
    {
        var layers = try context.model.newCache(parameters: nil)
        if let state {
            for i in layers.indices { layers[i].state = state.arrays[i] }   // sized exactly: new tokens reallocate, never mutated
            return (layers, nil)
        }
        let h = qwen.model(MLXArray(ids.map { Int32($0) }).expandedDimensions(axis: 0), cache: layers)
        eval(h)
        return (layers, PrefixState(layers.map(\.state)))
    }

    func cachedPrefix(adapter: Bool, ids: [Int]) -> PrefixState? {
        lock.withLock {
            guard let i = prefixes.firstIndex(where: { $0.adapter == adapter && $0.ids == ids }) else { return nil }
            let e = prefixes.remove(at: i)
            prefixes.append(e)
            return e.state
        }
    }

    func storePrefix(adapter: Bool, ids: [Int], state: PrefixState) {
        lock.withLock {
            prefixes.removeAll { $0.adapter == adapter && $0.ids == ids }
            prefixes.append((adapter, ids, state))
            if prefixes.count > maxCachedPrefixes { prefixes.removeFirst(prefixes.count - maxCachedPrefixes) }
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

/// KV state of a cached prompt prefix: per layer (keys, values). Read-only after creation.
final class PrefixState: @unchecked Sendable {
    let arrays: [[MLXArray]]
    init(_ arrays: [[MLXArray]]) { self.arrays = arrays }
}

extension GroundOneModel {
    /// Greedy generation for the local judge (adapter removed), with the same prefix-cache policy as GroundOne: the
    /// judge's instructions + document are reused when the same document is judged again.
    func judgeGenerate(messages: [[String: any Sendable]], document: String, maxTokens: Int) async throws
        -> (String, GenerationStats, Int)
    {
        let tokenizer = await container.tokenizer
        let prompt = try tokenizer.applyChatTemplate(messages: messages)
        var common = 0
        if prefixCacheEnabled {   // the judge prompt up to the end of the document: common prefix with a truncated prompt
            var head = messages
            head[1]["content"] = "\(JudgePrompt.instruction)\n\nDOCUMENT:\n\(document)"
            let h = try tokenizer.applyChatTemplate(messages: head)
            while common < min(h.count, prompt.count) - 1 && h[common] == prompt[common] { common += 1 }
        }
        let n = common
        let hit = n > 0 ? cachedPrefix(adapter: false, ids: Array(prompt[..<n])) : nil
        let t0 = Date()
        let (stream, fresh) = try await container.perform { context -> (AsyncStream<Generation>, PrefixState?) in
            guard let qwen = context.model as? Qwen2Model else { throw ModelAdapterError.incompatibleModelType }
            let cache = n > 0 ? try Self.cache(context, qwen, ids: Array(prompt[..<n]), state: hit) : nil
            let input = LMInput(tokens: MLXArray(prompt[n...].map { Int32($0) }))
            return (try MLXLMCommon.generate(input: input, cache: cache?.layers,
                                             parameters: GenerateParameters(maxTokens: maxTokens, temperature: 0),
                                             context: context), cache?.fresh)
        }
        if let fresh { storePrefix(adapter: false, ids: Array(prompt[..<n]), state: fresh) }
        var text = "", first: Double?
        var stats = GenerationStats(promptTokens: prompt.count)
        for await ev in stream {
            switch ev {
            case .chunk(let c):
                if first == nil { first = Date().timeIntervalSince(t0) }
                text += c
            case .info(let info): stats.generatedTokens = info.generationTokenCount
            default: break
            }
        }
        stats.timeToFirstToken = first ?? 0
        stats.seconds = Date().timeIntervalSince(t0)
        return (text, stats, hit != nil ? n : 0)
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
        let head = model.encoder.encode(MarkedPrompt.head(document: document)).count
        let (logits, cached) = try await model.scorePositions(ids: ids, positions: pos, prefixLength: head)
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
                        threshold: cal.threshold, model: name, cachedTokens: cached)
    }
}

/// B0a terse judge on GroundOne's base weights without the adapter: the judge measured in the thesis, locally.
public struct LocalJudge: Judge {
    public let model: GroundOneModel
    public var name: String { "LLM judge (\(model.info.baseRepo.split(separator: "/").last ?? ""), no adapter, B0a prompt)" }
    public init(model: GroundOneModel) { self.model = model }

    public func judge(document: String, sentences: [String], check: [Int]) async throws -> JudgeVerdicts {
        guard !check.isEmpty else { return JudgeVerdicts(labels: [:], rawText: "", inputTokens: 0, generatedTokens: 0, seconds: 0) }
        try await model.setAdapter(false)
        let user = JudgePrompt.user(document: document, sentences: sentences, check: check)
        let messages: [[String: any Sendable]] = [["role": "system", "content": MarkedPrompt.system], ["role": "user", "content": user]]
        let maxTokens = JudgePrompt.tokensPerSentence * check.count + 40
        let t0 = Date()
        let (text, stats, cached) = try await model.judgeGenerate(messages: messages, document: document, maxTokens: maxTokens)
        let seconds = Date().timeIntervalSince(t0)
        try await model.setAdapter(true)
        return JudgeVerdicts(labels: JudgePrompt.parse(text, check: check), rawText: text,
                             inputTokens: stats.promptTokens, generatedTokens: stats.generatedTokens, seconds: seconds,
                             cachedTokens: cached)
    }
}
