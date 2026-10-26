import GroundOneCore
import GroundOneEngines
import SwiftUI

struct AskView: View {
    @Environment(AppModel.self) private var model
    @State private var question = ""
    @State private var showInspector = true

    var body: some View {
        @Bindable var model = model
        VStack(spacing: 0) {
            ScrollViewReader { proxy in
                ScrollView {
                    LazyVStack(alignment: .leading, spacing: 22) {
                        if model.turns.isEmpty { EmptyAsk { ask($0) } }
                        ForEach(model.turns) { turn in
                            TurnView(turn: turn, selected: model.currentTurn?.id == turn.id)
                                .id(turn.id)
                                .onTapGesture { model.selectedTurn = turn.id }
                        }
                    }
                    .padding(24)
                    .frame(maxWidth: 860, alignment: .leading)
                    .frame(maxWidth: .infinity)
                }
                .onChange(of: model.turns.count) { _, _ in
                    if let last = model.turns.last { withAnimation { proxy.scrollTo(last.id, anchor: .top) } }
                }
            }
            Divider()
            HStack(spacing: 10) {
                TextField("Ask a question about the documents…", text: $question, axis: .vertical)
                    .textFieldStyle(.plain)
                    .lineLimit(1...4)
                    .padding(10)
                    .background(RoundedRectangle(cornerRadius: 10).fill(Color(nsColor: .textBackgroundColor)))
                    .overlay(RoundedRectangle(cornerRadius: 10).stroke(.quaternary))
                    .onSubmit { ask(question) }
                    .accessibilityIdentifier("question-field")
                Button { ask(question) } label: {
                    Label("Ask", systemImage: "arrow.up.circle.fill").labelStyle(.iconOnly).font(.system(size: 26))
                }
                .buttonStyle(.plain)
                .foregroundStyle(canSend ? Palette.groundOne : .secondary)
                .disabled(!canSend)
                .keyboardShortcut(.return, modifiers: .command)
                .accessibilityIdentifier("ask-button")
            }
            .padding(14)
        }
        .navigationTitle("Ask")
        .toolbar {
            ToolbarItemGroup {
                Picker("Policy", selection: $model.policyName) {
                    ForEach(model.policies) { Text($0.name).tag($0.name) }
                }
                .help("Policy: which verdicts Fix rewrites, how many rounds, threshold τ")
                Picker("Generator", selection: Binding(get: { model.generatorRepo }, set: { r in Task { await model.switchGenerator(to: r) } })) {
                    ForEach(ModelCatalog.generators, id: \.0) { Text($0.1).tag($0.0) }
                }
                .disabled(model.fake)
                .help("Generator of the answers and of the rewrites")
                .accessibilityIdentifier("generator-picker")
                Picker("Verifier", selection: Binding(get: { model.verifierRun }, set: { r in Task { await model.switchVerifier(to: r) } })) {
                    Text("GroundOne 3B").tag("g1-3b-b1")
                    Text("GroundOne 0.5B").tag("g1-05b-b1")
                }
                .disabled(model.fake)
                Button { showInspector.toggle() } label: { Label("Inspector", systemImage: "sidebar.right") }
            }
        }
        .inspector(isPresented: $showInspector) {
            InspectorView(turn: model.currentTurn)
                .inspectorColumnWidth(min: 320, ideal: 380, max: 520)
        }
    }

    var canSend: Bool { model.phase == .ready && !question.trimmingCharacters(in: .whitespaces).isEmpty }

    func ask(_ q: String) {
        guard model.phase == .ready, !q.trimmingCharacters(in: .whitespaces).isEmpty else { return }
        model.ask(q)
        question = ""
    }
}

/// Start page: what the app does, the verdict legend and example questions (a click asks them).
struct EmptyAsk: View {
    @Environment(AppModel.self) private var model
    let ask: (String) -> Void

    static let examples: [(String, String)] = [
        ("What are the side effects of clove tea for pregnant women?", "MS MARCO"),
        ("How do raffles work?", "MS MARCO"),
        ("What is the difference between the nervous system and the endocrine system?", "MS MARCO"),
        ("How does E-ZPass charge tolls?", "MS MARCO"),
        ("Why did Walmart oppose the religious freedom laws?", "news"),
        ("Who was Richie Benaud and what was his career?", "news"),
        ("What happened to Lauren Hill?", "news"),
    ]

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text("Ask the documents").font(.largeTitle.bold())
            Text("The answer appears as the generator wrote it. Then you choose: verify it with GroundOne (every sentence in one forward pass, on this Mac), or with GroundOne and an LLM judge to compare verdicts and times. Flagged or selected sentences can be rewritten from the sources.")
                .foregroundStyle(.secondary)
            HStack(spacing: 14) {
                Legend(label: .supported); Legend(label: .contradicted); Legend(label: .notMentioned); Legend(label: nil)
            }
            Text("Try one of these").font(.headline).padding(.top, 6)
            FlowLayout(spacing: 8) {
                ForEach(Self.examples, id: \.0) { q, src in
                    Button { ask(q) } label: {
                        HStack(spacing: 6) {
                            Text(q).lineLimit(2).multilineTextAlignment(.leading)
                            Text(src).font(.caption2).foregroundStyle(.secondary)
                        }
                        .padding(.horizontal, 10).padding(.vertical, 6)
                        .background(RoundedRectangle(cornerRadius: 8).fill(Color(nsColor: .controlBackgroundColor)))
                        .overlay(RoundedRectangle(cornerRadius: 8).stroke(.quaternary))
                    }
                    .buttonStyle(.plain)
                    .disabled(model.phase != .ready)
                    .accessibilityIdentifier("example-question")
                }
            }
            Text("\(model.documents.count) documents: news articles and MS MARCO web passages from the RAGTruth test set · English only")
                .font(.caption).foregroundStyle(.secondary)
        }
        .padding(.vertical, 30)
    }
}

struct Legend: View {
    let label: Verdict?
    var body: some View {
        Label(label?.display ?? "not checked", systemImage: Palette.symbol(label))
            .font(.callout)
            .foregroundStyle(Palette.color(label))
    }
}

/// Wraps its children onto new lines (example questions).
struct FlowLayout: Layout {
    var spacing: CGFloat = 8

    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) -> CGSize {
        let width = proposal.width ?? 800
        var x: CGFloat = 0, y: CGFloat = 0, row: CGFloat = 0
        for v in subviews {
            let s = v.sizeThatFits(ProposedViewSize(width: width, height: nil))
            if x > 0, x + s.width > width { x = 0; y += row + spacing; row = 0 }
            x += s.width + spacing
            row = max(row, s.height)
        }
        return CGSize(width: width, height: y + row)
    }

    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) {
        var x = bounds.minX, y = bounds.minY, row: CGFloat = 0
        for v in subviews {
            let s = v.sizeThatFits(ProposedViewSize(width: bounds.width, height: nil))
            if x > bounds.minX, x + s.width > bounds.maxX { x = bounds.minX; y += row + spacing; row = 0 }
            v.place(at: CGPoint(x: x, y: y), proposal: ProposedViewSize(s))
            x += s.width + spacing
            row = max(row, s.height)
        }
    }
}
