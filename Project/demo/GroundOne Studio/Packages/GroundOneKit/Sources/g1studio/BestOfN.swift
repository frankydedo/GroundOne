import Foundation
import GroundOneCore
import GroundOneEngines

/// Equal-compute baseline for the loop (§8): on fresh T1 answers, the verify-and-revise loop (greedy draft + up to two
/// targeted rewrites) vs best-of-N sampling (N answers at temperature 0.7, keep the first one GroundOne accepts).
/// Both are scored by GroundOne only ("accepted by GroundOne"), with their time and generated tokens.
enum BestOfN {
    struct Doc: Decodable { let id: String; let task: String; let doc: String }

    static func run(_ args: [String]) async throws {
        let opts = Options(args)
        let run = opts["--verifier"] ?? "g1-3b-b1"
        let n = Int(opts["--n"] ?? "60") ?? 60
        let samples = Int(opts["--samples"] ?? "3") ?? 3
        let out = Workspace.demo.appendingPathComponent("casestudy/bestofn-\(run).jsonl")
        if FileManager.default.fileExists(atPath: out.path) { throw CLIError.usage("\(out.path) exists: results are create-only") }
        // T1 documents, round robin over tasks, seed-free order of the frozen file.
        let t1 = Workspace.project().appendingPathComponent("data/processed/groundone/test_ragtruth.jsonl")
        let all = try String(contentsOf: t1, encoding: .utf8).split(separator: "\n").map { try JSONDecoder().decode(Doc.self, from: Data($0.utf8)) }
        var seen = Set<String>()
        var byTask: [String: [Doc]] = [:]
        for d in all where !seen.contains(d.doc) { seen.insert(d.doc); byTask[d.task, default: []].append(d) }
        let tasks = ["Summary", "QA", "Data2txt"]
        let docs = (0..<n).compactMap { i in byTask[tasks[i % 3]]?[safe: i / 3] }

        let g1 = try await GroundOneModel.load(run: run)
        let gen = try await MLXGenerator.load()
        let verifier = GroundOneVerifier(model: g1)
        let tau = g1.info.calibration.threshold
        let policy = Policy(name: "bestofn-strict", verifier: run, blocking: [.contradicted, .notMentioned], maxAttempts: 2, onFailure: .highlight)
        let orch = Orchestrator(retriever: nil, generator: gen, verifier: verifier, judge: nil, calibratedThreshold: tau)
        FileManager.default.createFile(atPath: out.path, contents: nil)
        let h = try FileHandle(forWritingTo: out)
        for (i, d) in docs.enumerated() {
            let task = CaseStudy.taskPrompt[d.task]!
            let user = "\(task)\n\nDOCUMENT:\n\(d.doc)"
            // Loop.
            let t0 = Date()
            let rec = try await orch.execute(.init(question: task, task: task, document: d.doc, compareWithJudge: false), policy: policy)
            let loopSeconds = Date().timeIntervalSince(t0)
            let loopTokens = rec.drafts.map(\.generation.generatedTokens).reduce(0, +)
            // Best-of-N: stop at the first sample GroundOne accepts.
            let t1 = Date()
            var accepted: Int?
            var tokens = 0
            var tried = 0
            for k in 0..<samples {
                let (text, s) = try await gen.sample(system: Orchestrator.answerSystem, user: user, maxTokens: 400, temperature: 0.7, seed: UInt64(1000 + k))
                tokens += s.generatedTokens
                tried += 1
                let v = try await verifier.verify(document: d.doc, sentences: Segmenter.segment(text.trimmingCharacters(in: .whitespacesAndNewlines)))
                if v.scored.allSatisfy({ !policy.isBlocking(Decision.decide($0.probs!, threshold: tau)) }) { accepted = k; break }
            }
            let bonSeconds = Date().timeIntervalSince(t1)
            let row: [String: Any] = [
                "id": d.id, "task": d.task,
                "loop_accepted": rec.status == .accepted, "loop_rounds": rec.rounds, "loop_seconds": loopSeconds,
                "loop_generated_tokens": loopTokens, "loop_first_draft_accepted": rec.drafts[0].verdicts.scored.allSatisfy { !policy.isBlocking($0.label) },
                "bon_accepted": accepted != nil, "bon_samples_used": tried, "bon_seconds": bonSeconds, "bon_generated_tokens": tokens,
            ]
            try h.write(contentsOf: JSONSerialization.data(withJSONObject: row, options: [.sortedKeys]) + Data([0x0A]))
            print("[\(i + 1)/\(docs.count)] \(d.task) loop: \(rec.status.rawValue) r\(rec.rounds) \(String(format: "%.1f", loopSeconds))s · best-of-\(samples): \(accepted.map { "accepted at \($0 + 1)" } ?? "none") \(String(format: "%.1f", bonSeconds))s")
        }
        try h.close()
    }
}

extension Array {
    subscript(safe i: Int) -> Element? { indices.contains(i) ? self[i] : nil }
}
