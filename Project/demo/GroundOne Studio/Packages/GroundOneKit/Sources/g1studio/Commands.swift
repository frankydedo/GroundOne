import Foundation
import GroundOneCore
import GroundOneEngines

enum Commands {
    static func verifyFixture(_ args: [String]) async throws {
        let run = args.first ?? "g1-3b-b1"
        let report = try await Conformance.run(run: run, limit: args.count > 1 ? Int(args[1]) : nil)
        print(report.summary)
    }

    static func indexURL(_ corpus: String, embedder: String) -> URL {
        let tag = embedder.split(separator: "/").last.map(String.init) ?? embedder
        return Workspace.demo.appendingPathComponent("index/\(corpus)-\(tag).sqlite")
    }

    /// g1studio ingest <corpus> <embedder repo> <files or folders...>
    static func ingest(_ args: [String]) async throws {
        guard args.count >= 3 else { throw CLIError.usage("ingest <corpus> <embedder> <paths...>") }
        let embedder = try await Embedder.load(repo: args[1])
        let index = try LibraryIndex(url: indexURL(args[0], embedder: args[1]))
        var files: [URL] = []
        for p in args.dropFirst(2) {
            let u = URL(fileURLWithPath: p)
            var dir: ObjCBool = false
            if FileManager.default.fileExists(atPath: u.path, isDirectory: &dir), dir.boolValue {
                files += try FileManager.default.contentsOfDirectory(at: u, includingPropertiesForKeys: nil)
                    .filter { ["pdf", "txt", "md"].contains($0.pathExtension.lowercased()) }
            } else {
                files.append(u)
            }
        }
        let t0 = Date()
        var total = 0
        for (i, f) in files.sorted(by: { $0.path < $1.path }).enumerated() {
            let n = try await index.add(file: f, title: Library.title(f), embedder: embedder)
            total += n
            print("[\(i + 1)/\(files.count)] \(f.lastPathComponent): \(n) passages")
        }
        print("indexed \(total) passages in \(String(format: "%.1f", Date().timeIntervalSince(t0))) s → \(index.url.path)")
    }

    /// Retrieval check for the embedding choice (decision 3): known-source questions over the research library.
    static func retrievalCheck(_ args: [String]) async throws {
        let embedders = args.isEmpty ? [ModelCatalog.embedder, "BAAI/bge-small-en-v1.5"] : args
        var report: [String: Any] = ["questions": RetrievalCheck.questions.map { ["q": $0.0, "source": $0.1] },
                                     "protocol": "research library (Vault/raw PDFs); hit@5 = the source paper is among the top-5 passages; MRR over the first passage from it"]
        for repo in embedders {
            let embedder = try await Embedder.load(repo: repo)
            let index = try LibraryIndex(url: indexURL("library", embedder: repo))
            for mode in HybridRetriever.Mode.allCases {
                let r = HybridRetriever(index: index, embedder: embedder, mode: mode)
                var hits = 0, rr = 0.0, secs = 0.0
                for (q, src) in RetrievalCheck.questions {
                    let t = Date()
                    let top = try await r.search(q, k: 5)
                    secs += Date().timeIntervalSince(t)
                    if let rank = top.firstIndex(where: { $0.docID.hasPrefix(src) }) { hits += 1; rr += 1 / Double(rank + 1) }
                }
                let n = Double(RetrievalCheck.questions.count)
                let key = mode == .bm25 ? "bm25" : "\(mode.rawValue) \(repo)"
                report[key] = ["hit@5": Double(hits) / n, "mrr": rr / n, "mean_seconds": secs / n]
                print(String(format: "%-60@ hit@5 %.2f  MRR %.2f  %.3f s/query", key as NSString, Double(hits) / n, rr / n, secs / n))
            }
        }
        let out = Workspace.demo.appendingPathComponent("results/retrieval_check.json")
        try JSONSerialization.data(withJSONObject: report, options: [.prettyPrinted, .sortedKeys]).write(to: out)
    }

    /// g1studio ask "<question>" [--verifier run] [--policy strict|lenient|observe] [--no-judge]
    static func ask(_ args: [String]) async throws {
        guard let q = args.first else { throw CLIError.usage("ask <question>") }
        let opts = Options(args.dropFirst())
        let stack = try await Stack.load(verifier: opts["--verifier"] ?? "g1-3b-b1", corpus: opts["--corpus"] ?? "library")
        let policy = Policy.builtIn.first { $0.name.hasPrefix(opts["--policy"] ?? "strict") } ?? .strict
        let rec = try await stack.orchestrator.execute(.init(question: q, compareWithJudge: opts["--no-judge"] == nil), policy: policy) { ev in
            if case .stage(let s) = ev { print("· \(s)") }
        }
        Report.print(rec)
        try await stack.audit.append(rec)
    }
}

enum CLIError: Error { case usage(String) }

struct Options {
    var values: [String: String] = [:]
    init<S: Sequence>(_ args: S) where S.Element == String {
        var it = Array(args).makeIterator()
        while let a = it.next() {
            if a.hasPrefix("--") {
                if ["--no-judge"].contains(a) { values[a] = "1" } else { values[a] = it.next() }
            }
        }
    }
    subscript(_ k: String) -> String? { values[k] }
}

enum Library {
    /// "Hu 2022 - LoRA_ingested.pdf" → "Hu 2022 - LoRA".
    static func title(_ url: URL) -> String {
        url.deletingPathExtension().lastPathComponent.replacingOccurrences(of: "_ingested", with: "")
    }
}

enum RetrievalCheck {
    static let questions: [(String, String)] = [
        ("How many fewer trainable parameters does low-rank adaptation need than full fine-tuning of GPT-3 175B?", "Hu 2022 - LoRA"),
        ("Which simple post-processing method fixes the miscalibration of modern neural networks?", "Guo 2017"),
        ("How does vLLM manage key-value cache memory to reduce fragmentation?", "Kwon 2023"),
        ("How is the factual precision of long-form text scored from atomic facts?", "Min 2023"),
        ("What are reflection tokens and how does the model decide when to retrieve?", "Asai 2024"),
        ("Which metrics evaluate a retrieval augmented generation pipeline without reference answers?", "Es 2024"),
        ("How often does a significant improvement on one test set also hold on another test set?", "Berg-Kirkpatrick 2012"),
        ("How can a language model larger than DRAM run by loading weights from flash memory?", "Alizadeh 2024"),
        ("How much more energy do multi-purpose generative models use than task-specific models?", "Luccioni 2024"),
        ("How many sentence pairs are in the Multi-Genre NLI corpus and which genres does it cover?", "Williams 2018"),
        ("How factually consistent are LLM summaries of topic-focused dialogues?", "Tang 2024"),
        ("Why are language models sensitive to the position of the options in multiple choice questions?", "Zheng 2024"),
    ]
}

/// Engines wired together: GroundOne (verifier and, with the adapter off, judge), generator, retriever, audit log.
struct Stack {
    let orchestrator: Orchestrator
    let audit: AuditLog

    static func load(verifier run: String, corpus: String) async throws -> Stack {
        let g1 = try await GroundOneModel.load(run: run)
        let gen = try await MLXGenerator.load()
        let embedder = try await Embedder.load()
        let index = try LibraryIndex(url: Commands.indexURL(corpus, embedder: ModelCatalog.embedder))
        let o = Orchestrator(retriever: HybridRetriever(index: index, embedder: embedder), generator: gen,
                             verifier: GroundOneVerifier(model: g1), judge: LocalJudge(model: g1),
                             calibratedThreshold: g1.info.calibration.threshold, memory: { Memory.stats() })
        return Stack(orchestrator: o, audit: AuditLog(url: Workspace.demo.appendingPathComponent("audit/cli.jsonl")))
    }
}

enum Report {
    static func print(_ r: QueryRecord) {
        Swift.print("\nQUESTION: \(r.question)")
        for p in r.passages { Swift.print("  [\(p.title) p.\((p.page ?? 0) + 1)] \(p.text.prefix(90))…") }
        for d in r.drafts {
            Swift.print("\n— draft \(d.round) (gen \(String(format: "%.1f", d.generation.seconds)) s, verify \(String(format: "%.2f", d.verdicts.seconds)) s, \(d.verdicts.inputTokens) tokens)")
            for s in d.verdicts.sentences {
                let tag = s.label.map { "\($0.display) \(String(format: "%.2f", s.pSupported ?? 0))" } ?? "unscored"
                Swift.print("  [\(tag)] \(s.text)")
            }
        }
        if let j = r.judge {
            Swift.print("\njudge (\(String(format: "%.1f", j.seconds)) s, \(j.generatedTokens) tokens): " +
                        j.labels.sorted { $0.key < $1.key }.map { "\($0.key + 1)=\($0.value?.letter ?? "?")" }.joined(separator: " "))
        }
        Swift.print("\nSTATUS: \(r.status.rawValue), rounds \(r.rounds), total \(String(format: "%.1f", r.timings.total)) s, " +
                    "MLX peak \(String(format: "%.2f", r.memory?.mlxPeakGB ?? 0)) GB\nDISPLAYED: \(r.displayed)")
    }
}

/// g1studio install: copies what the app needs into ~/Library/Application Support/GroundOne Studio (adapters with their
/// calibration, the library index with copies of its files, example policies, the case-study summary).
enum Install {
    static func run(_ args: [String]) throws {
        let fm = FileManager.default
        let dst = Workspace.appSupport
        try fm.createDirectory(at: dst, withIntermediateDirectories: true)
        func copy(_ a: URL, _ b: URL) throws {
            try fm.createDirectory(at: b.deletingLastPathComponent(), withIntermediateDirectories: true)
            if fm.fileExists(atPath: b.path) { try fm.removeItem(at: b) }
            try fm.copyItem(at: a, to: b)
        }
        for run in ModelCatalog.verifiers {
            let src = Workspace.models.appendingPathComponent(run)
            try copy(src.appendingPathComponent("groundone.json"), dst.appendingPathComponent("models/\(run)/groundone.json"))
            for f in ["adapters.safetensors", "adapter_config.json", "calibration.json", "groundone.json"] {
                let a = src.appendingPathComponent("best/\(f)")
                if fm.fileExists(atPath: a.path) { try copy(a, dst.appendingPathComponent("models/\(run)/best/\(f)")) }
            }
            print("model \(run)")
        }
        let policies = URL(fileURLWithPath: #filePath).deletingLastPathComponent().appendingPathComponent("../../../../Policies").standardized
        for f in (try? fm.contentsOfDirectory(at: policies, includingPropertiesForKeys: nil)) ?? [] where f.pathExtension == "json" {
            try copy(f, dst.appendingPathComponent("policies/\(f.lastPathComponent)"))
        }
        let summary = Workspace.demo.appendingPathComponent("casestudy/summary.json")
        if fm.fileExists(atPath: summary.path) { try copy(summary, dst.appendingPathComponent("casestudy/summary.json")) }
        // Index: copy the database, copy every source file into library/, point the rows at the copies.
        let tag = ModelCatalog.embedder.split(separator: "/").last!
        let srcIndex = Workspace.demo.appendingPathComponent("index/library-\(tag).sqlite")
        let dstIndex = dst.appendingPathComponent("index/library-\(tag).sqlite")
        try copy(srcIndex, dstIndex)
        let index = try LibraryIndex(url: dstIndex)
        var n = 0
        for d in index.documents() {
            let a = URL(fileURLWithPath: d.path)
            let b = dst.appendingPathComponent("library/\(a.lastPathComponent)")
            if fm.fileExists(atPath: a.path) { try copy(a, b); n += 1 }
            try index.relocate(docID: d.id, to: b.path)
        }
        print("index: \(index.documents().count) documents, \(n) files copied → \(dst.path)")
    }
}
