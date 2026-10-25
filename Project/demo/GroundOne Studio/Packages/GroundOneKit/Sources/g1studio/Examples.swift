import Foundation
import GroundOneCore
import GroundOneEngines

/// Runs candidate questions through the app flow (native answer → GroundOne + judge) to choose the example questions.
enum Examples {
    static func run(_ args: [String]) async throws {
        let questions = try JSONDecoder().decode([String].self, from: Data(contentsOf: URL(fileURLWithPath: args[0])))
        let g1 = try await GroundOneModel.load(run: "g1-3b-b1")
        let gen = try await MLXGenerator.load()
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
            out.append(["question": q, "words": words, "K": scored.count, "labels": counts, "judge_disagreements": disagree,
                        "generation_s": v.generation.seconds, "groundone_s": v.verdicts!.seconds, "judge_s": v.judge!.seconds])
        }
        try JSONSerialization.data(withJSONObject: out, options: [.prettyPrinted, .sortedKeys])
            .write(to: Workspace.demo.appendingPathComponent("results/example_candidates.json"))
    }
}
