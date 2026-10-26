import Foundation
import GroundOneCore
import GroundOneEngines

/// Runs questions through the app flow (native answer → GroundOne + judge → one rewrite of the flagged sentences →
/// GroundOne again) to choose the example questions and to compare generators.
/// Usage: g1studio examples <questions.json> [--generator repo] [--name examples-<label>]
enum Examples {
    static func run(_ args: [String]) async throws {
        let opts = Options(Array(args.dropFirst()))
        let questions = try JSONDecoder().decode([String].self, from: Data(contentsOf: URL(fileURLWithPath: args[0])))
        let repo = opts["--generator"] ?? ModelCatalog.generator
        let name = opts["--name"] ?? "example_candidates"
        Memory.resetPeak()
        let g1 = try await GroundOneModel.load(run: "g1-3b-b1")
        let gen = try await MLXGenerator.load(repo: repo)
        let emb = try await Embedder.load()
        let index = try LibraryIndex(url: Commands.indexURL(ModelCatalog.corpus, embedder: ModelCatalog.embedder))
        let session = StudioSession(retriever: HybridRetriever(index: index, embedder: emb), generator: gen,
                                    verifier: GroundOneVerifier(model: g1), judge: LocalJudge(model: g1),
                                    calibratedThreshold: g1.info.calibration.threshold)
        var out: [[String: Any]] = []
        for q in questions {
            var rec = StudioRecord(question: q, verifier: g1.name, generator: gen.name, policy: "strict")
            let v0 = try await session.answer(q, into: &rec) { _ in }
            let v = try await session.verify(v0, document: rec.document, withJudge: true)
            let scored = v.verdicts!.scored
            let counts = Dictionary(grouping: scored, by: { $0.label!.rawValue }).mapValues(\.count)
            let disagree = scored.filter { v.judge!.labels[$0.index] != $0.label }.count
            let words = v.text.split(whereSeparator: \.isWhitespace).count
            print("\n### \(q)\n  sources: \(Set(rec.passages.map(\.title)).sorted().prefix(4))\n  words \(words), K \(scored.count), G1 \(counts), judge disagrees on \(disagree); gen \(String(format: "%.1f", v.generation.seconds)) s, G1 \(String(format: "%.2f", v.verdicts!.seconds)) s, judge \(String(format: "%.1f", v.judge!.seconds)) s")
            for s in scored where s.label != .supported {
                print("  [\(s.label!.rawValue) \(String(format: "%.2f", s.probs![0]))] judge=\(v.judge!.labels[s.index]??.rawValue ?? "?") \(s.text.prefix(160))")
            }
            // one rewrite of the flagged sentences (strict: contradicted and not mentioned), then GroundOne again
            let flagged = scored.filter { $0.label != .supported }.map(\.index)
            var fix: [String: Any] = ["flagged": flagged.count]
            if !flagged.isEmpty {
                let f = try await session.fix(v, indices: flagged, document: rec.document)
                let fv = try await session.verify(f, document: rec.document, withJudge: false)
                let after = fv.verdicts!.scored
                let outcomes = (f.rewriteLog ?? "").split(separator: "\n").map { l -> String in
                    let t = l.split(separator: " ", maxSplits: 1).last.map(String.init) ?? ""
                    return ["DELETED", "UNCHANGED", "UNUSABLE"].contains(t) ? t.lowercased() : "rewritten"
                }
                fix = ["flagged": flagged.count, "outcomes": Dictionary(grouping: outcomes, by: { $0 }).mapValues(\.count),
                       "flagged_after": after.filter { $0.label != .supported }.count, "K_after": after.count,
                       "rewrite_s": f.generation.seconds, "groundone_after_s": fv.verdicts!.seconds,
                       "groundone_after_cached_tokens": fv.verdicts!.cachedTokens ?? 0]
                print("  fix: \(fix)")
            }
            out.append(["question": q, "words": words, "K": scored.count, "labels": counts, "judge_disagreements": disagree,
                        "generation_s": v.generation.seconds, "generated_tokens": v.generation.generatedTokens,
                        "groundone_s": v.verdicts!.seconds, "judge_s": v.judge!.seconds, "fix": fix])
        }
        let mem = Memory.stats()
        let summary: [String: Any] = ["generator": repo, "verifier": g1.name, "answers": out,
                                      "memory": ["mlx_active_gb": mem.mlxActiveGB, "mlx_peak_gb": mem.mlxPeakGB]]
        try FileManager.default.createDirectory(at: Workspace.demo.appendingPathComponent("results"), withIntermediateDirectories: true)
        try JSONSerialization.data(withJSONObject: summary, options: [.prettyPrinted, .sortedKeys])
            .write(to: Workspace.demo.appendingPathComponent("results/\(name).json"))
    }
}
