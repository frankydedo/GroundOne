import Foundation
import GroundOneCore
import GroundOneEngines
import Observation

/// One question and its versions (native answer, fixes), updated live.
@MainActor @Observable
final class Turn: Identifiable {
    let id = UUID()
    var record: StudioRecord
    var partial = ""
    var stage: String?
    var error: String?
    var versionIndex: Int?
    var selection: Set<Int> = []
    /// Source links per version id, computed on request (k GroundOne passes, one per passage) and cached.
    var evidence: [UUID: [Int: [SourceLink]]] = [:]
    var evidenceLoading = false

    init(record: StudioRecord) { self.record = record }

    var question: String { record.question }
    var busy: Bool { stage != nil }
    var shownIndex: Int? { record.versions.isEmpty ? nil : min(versionIndex ?? record.versions.count - 1, record.versions.count - 1) }
    var shown: Version? { shownIndex.map { record.versions[$0] } }
    var isLatest: Bool { shownIndex == record.versions.count - 1 }
}

/// A conversation: its questions in order. Saved as one JSON file per chat; can be renamed, deleted and resumed.
@MainActor @Observable
final class Chat: Identifiable {
    let id: UUID
    var title: String
    var renamed: Bool
    let created: Date
    var updated: Date
    var turns: [Turn]

    init(id: UUID = UUID(), title: String = "New chat", renamed: Bool = false, created: Date = Date(), updated: Date = Date(),
         turns: [Turn] = []) {
        self.id = id; self.title = title; self.renamed = renamed; self.created = created; self.updated = updated; self.turns = turns
    }

    struct File: Codable {
        let id: UUID
        let title: String
        let renamed: Bool
        let created: Date
        let updated: Date
        let records: [StudioRecord]
    }

    var file: File { File(id: id, title: title, renamed: renamed, created: created, updated: updated, records: turns.map(\.record)) }
}

enum SidebarItem: Hashable {
    case chat(UUID)
    case section(SidebarSection)
}

enum SidebarSection: String, CaseIterable, Identifiable {
    case ask = "Ask", library = "Library", policies = "Policies", stats = "Stats", audit = "Audit log"
    var id: String { rawValue }
    static let tools: [SidebarSection] = [.library, .policies, .stats, .audit]
    var symbol: String {
        switch self {
        case .ask: "text.bubble"
        case .library: "books.vertical"
        case .policies: "slider.horizontal.3"
        case .stats: "chart.bar.xaxis"
        case .audit: "list.bullet.rectangle"
        }
    }
}

/// App state. Engines run through their own serial containers; the UI never touches MLX directly.
@MainActor @Observable
final class AppModel {
    enum Phase: Equatable { case idle, loading(String), ready, failed(String) }

    var phase: Phase = .idle
    var sidebar: SidebarItem?
    var chats: [Chat] = []
    var verifierRun = "g1-3b-b1"
    var generatorRepo = ModelCatalog.generator
    var policies: [Policy] = Policy.builtIn
    var policyName = Policy.strict.name
    var selectedTurn: Turn.ID?
    var documents: [LibraryIndex.Doc] = []
    var memory: MemoryStats?
    var preview: DocumentPreviewRequest?
    /// Every record ever written by the app (audit log), for Stats; updated live.
    var history: [StudioRecord] = []

    let fake = ProcessInfo.processInfo.arguments.contains("-fakeEngines")
    private var g1: GroundOneModel?
    private var generator: (any Generator)?
    private var embedder: Embedder?
    private(set) var index: LibraryIndex?
    private var attributor: PassageAttributor?
    private var session: StudioSession?
    let audit: AuditLog

    init() {
        Workspace.mode = .app
        audit = AuditLog(url: Workspace.demo.appendingPathComponent(
            ProcessInfo.processInfo.arguments.contains("-fakeEngines") ? "audit/studio-uitest.jsonl" : "audit/studio.jsonl"))
        loadPolicies()
        history = fake ? [] : Self.readHistory(audit.url)
        if fake, !ProcessInfo.processInfo.arguments.contains("-keepChats") { try? FileManager.default.removeItem(at: chatFolder) }
        loadChats()
        if chats.isEmpty { newChat() } else { sidebar = .chat(chats[0].id) }
    }

    // MARK: chats

    var chatFolder: URL { Workspace.demo.appendingPathComponent(fake ? "chats-uitest" : "chats") }

    func newChat() {
        if let c = chats.first, c.turns.isEmpty { sidebar = .chat(c.id); return }
        let c = Chat()
        chats.insert(c, at: 0)
        sidebar = .chat(c.id)
        selectedTurn = nil
    }

    func rename(_ chat: Chat, to title: String) {
        let t = title.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !t.isEmpty else { return }
        chat.title = t
        chat.renamed = true
        save(chat)
    }

    /// Removes the chat and its file. The audit log keeps its lines, so Stats still counts its verifications.
    func delete(_ chat: Chat) {
        try? FileManager.default.removeItem(at: chatFolder.appendingPathComponent("\(chat.id.uuidString).json"))
        chats.removeAll { $0.id == chat.id }
        if case .chat(let id) = sidebar, id == chat.id {
            if let first = chats.first { sidebar = .chat(first.id) } else { newChat() }
        }
    }

    func save(_ chat: Chat) {
        guard !chat.turns.isEmpty else { return }
        try? FileManager.default.createDirectory(at: chatFolder, withIntermediateDirectories: true)
        let enc = JSONEncoder()
        enc.dateEncodingStrategy = .iso8601
        try? enc.encode(chat.file).write(to: chatFolder.appendingPathComponent("\(chat.id.uuidString).json"), options: .atomic)
    }

    func loadChats() {
        let d = JSONDecoder()
        d.dateDecodingStrategy = .iso8601
        let files = (try? FileManager.default.contentsOfDirectory(at: chatFolder, includingPropertiesForKeys: nil)) ?? []
        chats = files.filter { $0.pathExtension == "json" }
            .compactMap { try? d.decode(Chat.File.self, from: Data(contentsOf: $0)) }
            .sorted { $0.updated > $1.updated }
            .map { f in Chat(id: f.id, title: f.title, renamed: f.renamed, created: f.created, updated: f.updated,
                             turns: f.records.map { Turn(record: $0) }) }
    }

    var policy: Policy { policies.first { $0.name == policyName } ?? .strict }
    var verifierName: String { g1?.name ?? (fake ? "fake verifier" : verifierRun) }
    var calibration: Calibration? { g1?.info.calibration }
    var tau: Double { policy.tau(calibrated: calibration?.threshold ?? 0.925) }
    var currentChat: Chat? {
        if case .chat(let id) = sidebar { return chats.first { $0.id == id } }
        return nil
    }
    var turns: [Turn] { currentChat?.turns ?? [] }
    var currentTurn: Turn? { turns.first { $0.id == selectedTurn } ?? turns.last }

    // MARK: loading

    func load() async {
        guard phase == .idle || phase.isFailed else { return }
        if fake {
            session = StudioSession(retriever: Fakes.Retriever(), generator: Fakes.Generator(), verifier: Fakes.Verifier(),
                                    judge: Fakes.Judge(), calibratedThreshold: 0.925)
            documents = [LibraryIndex.Doc(id: "fake-1", title: "LoRA freezes the pretrained weights", path: "", passages: 2)]
            phase = .ready
            return
        }
        do {
            phase = .loading("Loading GroundOne (\(verifierRun))…")
            let g1 = try await GroundOneModel.load(run: verifierRun)
            phase = .loading("Loading the generator (\(ModelCatalog.generatorLabel(generatorRepo)) 4-bit)…")
            let gen = try await MLXGenerator.load(repo: generatorRepo)
            phase = .loading("Loading the embedding model…")
            let emb = try await Embedder.load()
            let index = try LibraryIndex(url: Workspace.demo.appendingPathComponent(
                "index/\(ModelCatalog.corpus)-\(ModelCatalog.embedder.split(separator: "/").last!).sqlite"))
            self.g1 = g1; generator = gen; embedder = emb; self.index = index
            rebuildSession()
            documents = index.documents()
            memory = Memory.stats()
            phase = .ready
        } catch {
            phase = .failed("Could not load the models: \(error.localizedDescription)")
        }
    }

    func switchVerifier(to run: String) async {
        guard run != verifierRun, !fake else { return }
        verifierRun = run
        phase = .loading("Loading GroundOne (\(run))…")
        do {
            g1 = nil
            g1 = try await GroundOneModel.load(run: run)
            rebuildSession()
            memory = Memory.stats()
            phase = .ready
        } catch {
            phase = .failed("Could not load \(run): \(error.localizedDescription)")
        }
    }

    func switchGenerator(to repo: String) async {
        guard repo != generatorRepo, !fake else { return }
        let previous = generatorRepo
        generatorRepo = repo
        phase = .loading("Loading the generator (\(ModelCatalog.generatorLabel(repo)) 4-bit)…")
        do {
            generator = nil
            session = nil
            Memory.clearCache()
            generator = try await MLXGenerator.load(repo: repo)
            rebuildSession()
            memory = Memory.stats()
            phase = .ready
        } catch {
            generatorRepo = previous
            phase = .failed("Could not load \(repo): \(error.localizedDescription)")
        }
    }

    private func rebuildSession() {
        guard let g1, let generator, let index else { return }
        let verifier = GroundOneVerifier(model: g1)
        session = StudioSession(retriever: HybridRetriever(index: index, embedder: embedder), generator: generator,
                                verifier: verifier, judge: LocalJudge(model: g1), calibratedThreshold: g1.info.calibration.threshold)
        attributor = PassageAttributor(verifier: verifier)
    }

    // MARK: steps

    /// Retrieval and the generator's native answer; nothing is verified or changed.
    func ask(_ question: String) {
        let q = question.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !q.isEmpty, let session, phase == .ready else { return }
        if currentChat == nil { newChat() }
        guard let chat = currentChat else { return }
        let turn = Turn(record: StudioRecord(question: q, verifier: verifierName, generator: generator?.name ?? "fake generator",
                                             policy: policyName))
        chat.turns.append(turn)
        if !chat.renamed, chat.turns.count == 1 { chat.title = q.count > 48 ? String(q.prefix(47)) + "…" : q }
        selectedTurn = turn.id
        turn.stage = "Retrieving and generating"
        Task {
            do {
                var rec = turn.record
                let v = try await session.answer(q, into: &rec) { text in
                    Task { @MainActor in turn.partial = text }
                }
                rec.versions = [v]
                turn.record = rec
                finish(turn, event: "generated")
                session.prefetch(document: rec.document)   // read the sources while the user reads the answer
            } catch { fail(turn, error) }
        }
    }

    /// One GroundOne pass over the whole shown version; with `judge`, the generative judge on the same answer.
    func verify(_ turn: Turn, judge: Bool) {
        guard let session, let i = turn.shownIndex, !turn.busy else { return }
        turn.stage = judge ? "GroundOne and the LLM judge are verifying" : "GroundOne is verifying"
        let v = turn.record.versions[i]
        let doc = turn.record.document
        let tau = self.tau
        Task {
            do {
                var nv = try await session.verify(v, document: doc, threshold: tau, withJudge: judge)
                if !judge, let previous = v.judge { nv.judge = previous }
                turn.record.versions[i] = nv
                finish(turn, event: judge ? "verified+judge" : "verified")
            } catch { fail(turn, error) }
        }
    }

    /// Rewrites the given sentences of the latest version (by error type, one request each), then verifies the new
    /// version the same way the previous one was verified. `rounds` > 1 repeats on what is still flagged (policy).
    func fix(_ turn: Turn, indices: [Int], rounds: Int = 1) {
        guard let session, !turn.busy, !indices.isEmpty, let last = turn.record.versions.last else { return }
        let doc = turn.record.document
        let withJudge = last.judge != nil
        let tau = self.tau
        let policy = self.policy
        turn.stage = "Rewriting \(indices.count) sentence\(indices.count == 1 ? "" : "s")"
        Task {
            do {
                var current = last
                var todo = indices
                var repeated: Set<String> = []   // sentences the generator only repeated: not retried in later rounds
                for round in 0..<max(rounds, 1) {
                    if round > 0 { turn.stage = "Rewriting again (round \(round + 1))" }
                    let before = current.sentences
                    let fixed = try await session.fix(current, indices: todo, document: doc)
                    repeated.formUnion((fixed.unchanged ?? []).compactMap { before.indices.contains($0) ? before[$0].text : nil })
                    turn.stage = "GroundOne is verifying the rewrite"
                    current = try await session.verify(fixed, document: doc, threshold: tau, withJudge: withJudge)
                    turn.record.versions.append(current)
                    turn.versionIndex = nil
                    turn.selection = []
                    todo = current.verdicts?.sentences.filter { policy.isBlocking($0.label) && !repeated.contains($0.text) }
                        .map(\.index) ?? []
                    if todo.isEmpty { break }
                }
                finish(turn, event: "fixed")
            } catch { fail(turn, error) }
        }
    }

    func flagged(_ v: Version?) -> [Int] {
        v?.verdicts?.sentences.filter { policy.isBlocking($0.label) }.map(\.index) ?? []
    }

    func fixFlagged(_ turn: Turn) {
        fix(turn, indices: flagged(turn.record.versions.last), rounds: policy.maxAttempts)
    }

    /// Opens the document preview at the passage that best supports (or contradicts) the sentence, span highlighted.
    func findEvidence(_ turn: Turn, sentence: Int) {
        guard let v = turn.shown, !turn.record.passages.isEmpty, !turn.evidenceLoading else { return }
        if let links = turn.evidence[v.id] { openEvidence(links[sentence], sentence: v.sentences[safe: sentence]); return }
        if fake {
            let p = turn.record.passages[0]
            let l = SourceLink(sentence: sentence, kind: .supported, passage: p, probability: 0.97, spanStart: 0, spanEnd: 60,
                               spanText: String(p.text.prefix(60)))
            turn.evidence[v.id] = [sentence: [l]]
            openEvidence([l], sentence: v.sentences[safe: sentence])
            return
        }
        guard let attributor else { return }
        turn.evidenceLoading = true
        let segs = v.sentences.map { Segment(start: $0.start, end: $0.end, text: $0.text, checkable: $0.scored) }
        let passages = turn.record.passages
        let key = v.id.uuidString
        Task {
            let links = (try? await attributor.links(answer: segs, passages: passages, key: key)) ?? [:]
            turn.evidence[v.id] = links
            turn.evidenceLoading = false
            openEvidence(links[sentence], sentence: v.sentences[safe: sentence])
        }
    }

    private func openEvidence(_ links: [SourceLink]?, sentence: SentenceVerdict?) {
        guard let l = links?.first else {
            preview = DocumentPreviewRequest(title: "No evidence found", path: nil, highlight: nil, kind: nil,
                                             note: "No retrieved passage supports or contradicts this sentence above the threshold τ.",
                                             sentence: sentence?.text)
            return
        }
        preview = DocumentPreviewRequest(title: l.passage.title, path: l.passage.fileURL?.path, highlight: l.spanText, kind: l.kind,
                                         note: "GroundOne P(\(l.kind.display)) = \(String(format: "%.2f", l.probability)) in this passage · evidence suggested by GroundOne, not evaluated",
                                         sentence: sentence?.text, fallbackText: l.passage.text)
    }

    private func finish(_ turn: Turn, event: String) {
        turn.stage = nil
        turn.partial = ""
        if !fake { memory = Memory.stats() }
        turn.record.memory = memory
        turn.record.event = event
        turn.record.policy = policyName
        let rec = turn.record
        history.removeAll { $0.id == rec.id }
        history.append(rec)
        if let chat = chats.first(where: { $0.turns.contains { $0 === turn } }) {
            chat.updated = Date()
            save(chat)
        }
        let audit = self.audit
        Task { try? await audit.append(rec) }
    }

    private func fail(_ turn: Turn, _ error: Error) {
        turn.stage = nil
        turn.error = error.localizedDescription
    }

    // MARK: library

    func previewDocument(_ doc: LibraryIndex.Doc) {
        preview = DocumentPreviewRequest(title: doc.title, path: doc.path.isEmpty ? nil : doc.path, highlight: nil, kind: nil,
                                         note: "\(doc.passages) passage\(doc.passages == 1 ? "" : "s") in the index", sentence: nil,
                                         fallbackText: fake ? Fakes.passages.map(\.text).joined(separator: "\n\n") : nil)
    }

    // MARK: policies

    var policyFolder: URL { Workspace.demo.appendingPathComponent("policies") }

    func loadPolicies() {
        var list = Policy.builtIn.filter { $0.name != Policy.observe.name }
        for f in (try? FileManager.default.contentsOfDirectory(at: policyFolder, includingPropertiesForKeys: nil)) ?? []
        where f.pathExtension == "json" {
            if let p = try? JSONDecoder().decode(Policy.self, from: Data(contentsOf: f)), !list.contains(where: { $0.name == p.name }) {
                list.append(p)
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

    // MARK: history

    /// Last state of every question in the audit log (one line per action; the last line of an id wins).
    static func readHistory(_ url: URL) -> [StudioRecord] {
        guard let text = try? String(contentsOf: url, encoding: .utf8) else { return [] }
        let d = JSONDecoder()
        d.dateDecodingStrategy = .iso8601
        var byID: [UUID: StudioRecord] = [:]
        var order: [UUID] = []
        for line in text.split(separator: "\n") {
            guard let r = try? d.decode(StudioRecord.self, from: Data(line.utf8)) else { continue }
            if byID[r.id] == nil { order.append(r.id) }
            byID[r.id] = r
        }
        return order.compactMap { byID[$0] }
    }
}

struct DocumentPreviewRequest: Identifiable {
    let id = UUID()
    let title: String
    let path: String?
    let highlight: String?
    let kind: Label?
    let note: String
    let sentence: String?
    var fallbackText: String? = nil
}

extension AppModel.Phase {
    var isFailed: Bool { if case .failed = self { true } else { false } }
}

extension Array {
    subscript(safe i: Int) -> Element? { indices.contains(i) ? self[i] : nil }
}
