import Foundation
import GroundOneCore
import GroundOneEngines

/// Injected-error case study (D30, §8): GroundOne flags, the generator rewrites, GroundOne re-checks. The injected
/// position and wrong string (from experiments/demo/scripts/inject_errors.py) are the ground truth, independent of
/// GroundOne. Results are reported as "accepted by GroundOne", never as "correct".
enum CaseStudy {
    struct Item: Decodable {
        let id: String
        let task: String
        let kind: String
        let doc: String
        let answer_injected: String
        let answer_original: String
        let injected: String
        let wrong: String
        let right: String?
        let original: String?
    }

    static let taskPrompt = [
        "Summary": "Write a short summary of the document.",
        "QA": "Answer the question contained in the document, using only the passages it provides.",
        "Data2txt": "Write a short overview of the business described by the structured data in the document.",
    ]

    static func words(_ s: String) -> Set<String> {
        Set(s.lowercased().components(separatedBy: CharacterSet.alphanumerics.inverted).filter { $0.count > 2 })
    }

    static func jaccard(_ a: String, _ b: String) -> Double {
        let x = words(a), y = words(b)
        return x.isEmpty || y.isEmpty ? 0 : Double(x.intersection(y).count) / Double(x.union(y).count)
    }

    /// Is the injected error still in this text? Swaps: the wrong string; fabricated: a sentence close to it.
    static func errorPresent(_ item: Item, text: String, sentences: [String]) -> Bool {
        if item.kind == "fabricated" { return sentences.contains { jaccard($0, item.injected) >= 0.5 } }
        return text.contains(item.wrong)
    }

    static func injectedIndex(_ item: Item, _ v: Verdicts) -> Int? {
        if item.kind == "fabricated" {
            return v.sentences.max { jaccard($0.text, item.injected) < jaccard($1.text, item.injected) }?.index
        }
        return v.sentences.first { $0.text.contains(item.wrong) }?.index
    }

    static func run(_ args: [String]) async throws {
        let opts = Options(args)
        let run = opts["--verifier"] ?? "g1-3b-b1"
        let n = Int(opts["--n"] ?? "100") ?? 100
        let name = opts["--name"] ?? "casestudy-\(run)"
        let input = Workspace.demo.appendingPathComponent("casestudy/injected.jsonl")
        let items = try String(contentsOf: input, encoding: .utf8).split(separator: "\n").prefix(n)
            .map { try JSONDecoder().decode(Item.self, from: Data($0.utf8)) }
        let outDir = Workspace.demo.appendingPathComponent("casestudy/\(name)")
        if FileManager.default.fileExists(atPath: outDir.path) { throw CLIError.usage("\(outDir.path) exists: results are create-only") }
        try FileManager.default.createDirectory(at: outDir, withIntermediateDirectories: true)

        let t0 = Date()
        let g1 = try await GroundOneModel.load(run: run)
        let gen = try await MLXGenerator.load()
        let load = Date().timeIntervalSince(t0)
        let afterLoad = Memory.stats()
        Memory.resetPeak()
        let orch = Orchestrator(retriever: nil, generator: gen, verifier: GroundOneVerifier(model: g1),
                                judge: LocalJudge(model: g1), calibratedThreshold: g1.info.calibration.threshold,
                                memory: { Memory.stats() })
        let policy = Policy(name: "casestudy-strict", verifier: run, blocking: [.contradicted, .notMentioned],
                            maxAttempts: 2, onFailure: .highlight)
        let audit = AuditLog(url: outDir.appendingPathComponent("audit.jsonl"))
        let rows = outDir.appendingPathComponent("rows.jsonl")
        FileManager.default.createFile(atPath: rows.path, contents: nil)
        let handle = try FileHandle(forWritingTo: rows)
        for (i, item) in items.enumerated() {
            let req = Orchestrator.Request(question: taskPrompt[item.task]!, task: taskPrompt[item.task], document: item.doc,
                                           initialAnswer: item.answer_injected, compareWithJudge: true)
            let rec = try await orch.execute(req, policy: policy)
            try await audit.append(rec)
            let d0 = rec.drafts[0].verdicts
            let inj = injectedIndex(item, d0)
            let g1Flag = inj.flatMap { d0.sentences[$0].label }.map { $0 != .supported }
            let judgeLabel = inj.flatMap { rec.judge?.labels[$0] ?? nil }
            let otherScored = d0.sentences.filter { $0.scored && $0.index != inj }
            let falseAlarms = otherScored.filter { $0.label != .supported }.count
            let present = rec.drafts.map { d in errorPresent(item, text: d.text, sentences: d.verdicts.sentences.map(\.text)) }
            let finalText = rec.drafts.last!.text
            let kept = otherScored.filter { finalText.contains($0.text) }.count
            let row: [String: Any] = [
                "id": item.id, "task": item.task, "kind": item.kind, "injected_sentence_found": inj != nil,
                "g1_flags_injected": g1Flag as Any, "g1_label_injected": inj.flatMap { d0.sentences[$0].label?.rawValue } as Any,
                "g1_p_supported_injected": inj.flatMap { d0.sentences[$0].pSupported } as Any,
                "judge_label_injected": judgeLabel?.rawValue as Any, "judge_parsed": rec.judge.map { $0.labels.values.allSatisfy { $0 != nil } } as Any,
                "g1_false_alarms_draft0": falseAlarms, "other_scored_sentences": otherScored.count,
                "other_sentences_kept_verbatim": kept, "error_present_by_round": present, "rounds": rec.rounds,
                "status": rec.status.rawValue, "restored_right": item.right.map { finalText.contains($0) } as Any,
                "flagged_by_round": rec.drafts.map { $0.verdicts.sentences.filter { policy.isBlocking($0.label) }.count },
                "verification_s": rec.timings.verification, "generation_s": rec.timings.generation,
                "judge_s": rec.timings.judge as Any, "judge_generated_tokens": rec.judge?.generatedTokens as Any,
                "verifier_input_tokens": d0.inputTokens, "K": d0.scored.count, "final_text": finalText,
                "mlx_peak_gb": rec.memory?.mlxPeakGB as Any,
            ]
            try handle.write(contentsOf: JSONSerialization.data(withJSONObject: row, options: [.sortedKeys]) + Data([0x0A]))
            print("[\(i + 1)/\(items.count)] \(item.kind) \(item.task) flag=\(g1Flag.map(String.init) ?? "?") judge=\(judgeLabel?.letter ?? "?") present=\(present) status=\(rec.status.rawValue) verify=\(rec.timings.verification.map { String(format: "%.2f", $0) }) judge=\(String(format: "%.1f", rec.timings.judge ?? 0))s")
            fflush(stdout)
        }
        try handle.close()
        let meta: [String: Any] = ["verifier": run, "generator": gen.name, "answers": items.count, "load_seconds": load,
                                   "memory_after_load": ["mlx_active_gb": afterLoad.mlxActiveGB, "resident_gb": afterLoad.residentGB],
                                   "memory_peak_during_loop": ["mlx_peak_gb": Memory.stats().mlxPeakGB, "resident_peak_gb": Memory.stats().residentGB],
                                   "policy": ["blocking": ["contradicted", "not_mentioned"], "max_attempts": 2, "on_failure": "highlight"],
                                   "judge": "Qwen2.5-3B 8-bit base without the adapter, B0a terse prompt, greedy",
                                   "build": "Release", "seconds": Date().timeIntervalSince(t0)]
        try JSONSerialization.data(withJSONObject: meta, options: [.prettyPrinted, .sortedKeys])
            .write(to: outDir.appendingPathComponent("meta.json"))
        print("done: \(outDir.path)")
    }
}
