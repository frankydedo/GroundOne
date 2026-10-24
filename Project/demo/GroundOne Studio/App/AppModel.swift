import Foundation
import GroundOneCore
import GroundOneEngines
import Observation

/// One question and everything that happens to it, updated live while the loop runs.
@MainActor @Observable
final class Turn: Identifiable {
    let id = UUID()
    let question: String
    var stage: String?
    var partial = ""
    var passages: [Passage] = []
    var drafts: [Draft] = []
    var judge: JudgeVerdicts?
    var record: QueryRecord?
    var error: String?
    var links: [Int: [SourceLink]]?
    var linksLoading = false
    var selectedDraft: Int?

    init(question: String) { self.question = question }

    var running: Bool { record == nil && error == nil }
    var shownDraft: Draft? { selectedDraft.flatMap { i in drafts.indices.contains(i) ? drafts[i] : nil } ?? drafts.last }
}

enum SidebarSection: String, CaseIterable, Identifiable {
    case ask = "Ask", library = "Library", policies = "Policies", measurements = "Measurements", audit = "Audit log"
    var id: String { rawValue }
    var symbol: String {
        switch self {
        case .ask: "text.bubble"
        case .library: "books.vertical"
        case .policies: "slider.horizontal.3"
        case .measurements: "chart.bar.xaxis"
        case .audit: "list.bullet.rectangle"
        }
    }
}

/// App state. All engine calls go through the engines' own serial containers; the UI never touches MLX directly.
@MainActor @Observable
final class AppModel {
    enum Phase: Equatable { case idle, loading(String), ready, failed(String) }

    var phase: Phase = .idle
    var section: SidebarSection? = .ask
    var verifierRun = "g1-3b-b1"
    var policies: [Policy] = Policy.builtIn
    var policyName = Policy.strict.name
    var compareWithJudge = true
    var turns: [Turn] = []
    var documents: [LibraryIndex.Doc] = []
    var ingesting: String?
    var loadSeconds: Double?
    var memory: MemoryStats?

    let fake = ProcessInfo.processInfo.arguments.contains("-fakeEngines") || UserDefaults.standard.bool(forKey: "fakeEngines")
    private var g1: GroundOneModel?
    private var generator: (any Generator)?
    private var embedder: Embedder?
    private(set) var index: LibraryIndex?
    private var attributor: PassageAttributor?
    private var orchestrator: Orchestrator?
    private(set) var audit: AuditLog
    let corpus = "library"

    init() {
        Workspace.mode = .app
        audit = AuditLog(url: Workspace.demo.appendingPathComponent(
            ProcessInfo.processInfo.arguments.contains("-fakeEngines") ? "audit/app-uitest.jsonl" : "audit/app.jsonl"))
        loadPolicies()
    }

    var policy: Policy { policies.first { $0.name == policyName } ?? .strict }
    var verifierName: String { g1?.name ?? (fake ? "fake verifier" : verifierRun) }
    var calibration: Calibration? { g1?.info.calibration }

    // MARK: loading

    func load() async {
        guard phase == .idle || phase.isFailed else { return }
        let t0 = Date()
        if fake {
            orchestrator = Orchestrator(retriever: Fakes.Retriever(), generator: Fakes.Generator(), verifier: Fakes.Verifier(),
                                        judge: Fakes.Judge(), calibratedThreshold: 0.925)
            documents = [LibraryIndex.Doc(id: "Hu 2022 - LoRA_ingested.pdf", title: "Hu 2022 - LoRA", path: "", passages: 2)]
            phase = .ready
            loadSeconds = 0
            return
        }
        do {
            phase = .loading("Loading GroundOne (\(verifierRun))…")
            let g1 = try await GroundOneModel.load(run: verifierRun)
            phase = .loading("Loading the generator (Qwen2.5-3B-Instruct 4-bit)…")
            let gen = try await MLXGenerator.load()
            phase = .loading("Loading the embedding model…")
            let emb = try await Embedder.load()
            let index = try LibraryIndex(url: Workspace.demo.appendingPathComponent(
                "index/\(corpus)-\(ModelCatalog.embedder.split(separator: "/").last!).sqlite"))
            self.g1 = g1; generator = gen; embedder = emb; self.index = index
            attributor = PassageAttributor(verifier: GroundOneVerifier(model: g1))
            rebuildOrchestrator()
            documents = index.documents()
            loadSeconds = Date().timeIntervalSince(t0)
            memory = Memory.stats()
            phase = .ready
        } catch {
            phase = .failed("Could not load the models: \(error.localizedDescription)")
        }
    }

    func switchVerifier(to run: String) async {
        guard run != verifierRun || g1 == nil, !fake else { return }
        verifierRun = run
        phase = .loading("Loading GroundOne (\(run))…")
        do {
            g1 = nil
            let g1 = try await GroundOneModel.load(run: run)
            self.g1 = g1
            attributor = PassageAttributor(verifier: GroundOneVerifier(model: g1))
            rebuildOrchestrator()
            memory = Memory.stats()
            phase = .ready
        } catch {
            phase = .failed("Could not load \(run): \(error.localizedDescription)")
        }
    }

    private func rebuildOrchestrator() {
        guard let g1, let generator, let index else { return }
        orchestrator = Orchestrator(retriever: HybridRetriever(index: index, embedder: embedder), generator: generator,
                                    verifier: GroundOneVerifier(model: g1), judge: LocalJudge(model: g1),
                                    calibratedThreshold: g1.info.calibration.threshold, memory: { Memory.stats() })
    }

    // MARK: asking

    func ask(_ question: String) {
        let q = question.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !q.isEmpty, let orchestrator, phase == .ready else { return }
        let turn = Turn(question: q)
        turns.append(turn)
        let policy = self.policy
        let req = Orchestrator.Request(question: q, compareWithJudge: compareWithJudge)
        let audit = self.audit
        Task {
            do {
                for try await ev in orchestrator.run(req, policy: policy) {
                    switch ev {
                    case .stage(let s): turn.stage = s
                    case .retrieved(let p, _): turn.passages = p
                    case .partial(let round, let text): if round == 0 { turn.partial = text }
                    case .draft(let d): turn.drafts.append(d); turn.selectedDraft = nil
                    case .judge(let j): turn.judge = j
                    case .finished(let r):
                        turn.record = r
                        turn.stage = nil
                        memory = r.memory
                        if r.policy.auditLog { try? await audit.append(r) }
                    }
                }
            } catch {
                turn.error = error.localizedDescription
                turn.stage = nil
            }
        }
    }

    /// Source links for the shown draft, computed on demand (k extra GroundOne passes) and cached.
    func loadLinks(for turn: Turn) {
        guard let draft = turn.shownDraft, !turn.passages.isEmpty, !turn.linksLoading else { return }
        let segs = draft.verdicts.sentences.map { Segment(start: $0.start, end: $0.end, text: $0.text, checkable: $0.scored) }
        if fake {
            turn.links = [0: [SourceLink(sentence: 0, kind: .supported, passage: turn.passages[0], probability: 0.97,
                                         spanStart: 0, spanEnd: 60, spanText: String(turn.passages[0].text.prefix(60)))]]
            return
        }
        guard let attributor else { return }
        turn.linksLoading = true
        let key = "\(turn.id)-\(draft.round)"
        let passages = turn.passages
        Task {
            turn.links = try? await attributor.links(answer: segs, passages: passages, key: key)
            turn.linksLoading = false
        }
    }

    // MARK: library

    func addFiles(_ urls: [URL]) {
        guard let index else { return }
        let embedder = self.embedder
        Task {
            for u in urls {
                ingesting = u.lastPathComponent
                let ok = u.startAccessingSecurityScopedResource()
                _ = try? await index.add(file: u, title: u.deletingPathExtension().lastPathComponent
                    .replacingOccurrences(of: "_ingested", with: ""), embedder: embedder)
                if ok { u.stopAccessingSecurityScopedResource() }
                documents = index.documents()
            }
            ingesting = nil
        }
    }

    func remove(_ doc: LibraryIndex.Doc) {
        try? index?.remove(docID: doc.id)
        documents = index?.documents() ?? documents.filter { $0 != doc }
    }

    // MARK: policies

    var policyFolder: URL { Workspace.demo.appendingPathComponent("policies") }

    func loadPolicies() {
        var list = Policy.builtIn
        for dir in [policyFolder] {
            for f in (try? FileManager.default.contentsOfDirectory(at: dir, includingPropertiesForKeys: nil)) ?? []
            where f.pathExtension == "json" {
                if let p = try? JSONDecoder().decode(Policy.self, from: Data(contentsOf: f)), !list.contains(where: { $0.name == p.name }) {
                    list.append(p)
                }
            }
        }
        policies = list
    }

    func save(_ policy: Policy) {
        if let i = policies.firstIndex(where: { $0.name == policy.name }) { policies[i] = policy } else { policies.append(policy) }
        try? FileManager.default.createDirectory(at: policyFolder, withIntermediateDirectories: true)
        let enc = JSONEncoder()
        enc.outputFormatting = [.prettyPrinted, .sortedKeys]
        try? enc.encode(policy).write(to: policyFolder.appendingPathComponent("\(policy.name).json"))
    }

    var sessionRecords: [QueryRecord] { turns.compactMap(\.record) }
}

extension AppModel.Phase {
    var isFailed: Bool { if case .failed = self { true } else { false } }
}
