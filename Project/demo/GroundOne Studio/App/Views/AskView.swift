import GroundOneCore
import SwiftUI

struct AskView: View {
    @Environment(AppModel.self) private var model
    @State private var question = ""
    @State private var inspected: Turn.ID?
    @State private var showInspector = true

    var body: some View {
        @Bindable var model = model
        VStack(spacing: 0) {
            ScrollViewReader { proxy in
                ScrollView {
                    LazyVStack(alignment: .leading, spacing: 22) {
                        if model.turns.isEmpty { EmptyAsk() }
                        ForEach(model.turns) { turn in
                            TurnView(turn: turn, selected: inspected == turn.id)
                                .id(turn.id)
                                .onTapGesture { inspected = turn.id }
                        }
                    }
                    .padding(24)
                    .frame(maxWidth: 860, alignment: .leading)
                    .frame(maxWidth: .infinity)
                }
                .onChange(of: model.turns.count) { _, _ in
                    if let last = model.turns.last { inspected = last.id; withAnimation { proxy.scrollTo(last.id, anchor: .top) } }
                }
            }
            Divider()
            HStack(spacing: 10) {
                TextField("Ask a question about your documents…", text: $question, axis: .vertical)
                    .textFieldStyle(.plain)
                    .font(.body)
                    .lineLimit(1...4)
                    .padding(10)
                    .background(RoundedRectangle(cornerRadius: 10).fill(Color(nsColor: .textBackgroundColor)))
                    .overlay(RoundedRectangle(cornerRadius: 10).stroke(.quaternary))
                    .onSubmit(send)
                    .accessibilityIdentifier("question-field")
                Button(action: send) {
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
                .help("Policy: which GroundOne verdicts block a sentence, how many rewrites, what to do on failure")
                .accessibilityIdentifier("policy-picker")
                Picker("Verifier", selection: Binding(get: { model.verifierRun }, set: { r in Task { await model.switchVerifier(to: r) } })) {
                    Text("GroundOne 3B").tag("g1-3b-b1")
                    Text("GroundOne 0.5B").tag("g1-05b-b1")
                }
                .disabled(model.fake)
                Toggle(isOn: $model.compareWithJudge) { Label("Judge comparison", systemImage: "scalemass") }
                    .help("Also judge the first draft with the generative judge (same base model, no adapter, B0a prompt)")
                    .accessibilityIdentifier("judge-toggle")
                Button { showInspector.toggle() } label: { Label("Inspector", systemImage: "sidebar.right") }
            }
        }
        .inspector(isPresented: $showInspector) {
            InspectorView(turn: model.turns.first { $0.id == inspected } ?? model.turns.last)
                .inspectorColumnWidth(min: 300, ideal: 360, max: 480)
        }
    }

    var canSend: Bool { model.phase == .ready && !question.trimmingCharacters(in: .whitespaces).isEmpty }

    func send() {
        guard canSend else { return }
        model.ask(question)
        question = ""
    }
}

struct EmptyAsk: View {
    @Environment(AppModel.self) private var model

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Ask your research library").font(.largeTitle.bold())
            Text("Every answer is checked sentence by sentence by GroundOne, in one forward pass, on this Mac. Flagged sentences are rewritten from the documents and checked again, as the selected policy says.")
                .foregroundStyle(.secondary)
            HStack(spacing: 14) {
                Legend(label: .supported); Legend(label: .contradicted); Legend(label: .notMentioned); Legend(label: nil)
            }
            .padding(.top, 4)
            Text("\(model.documents.count) document\(model.documents.count == 1 ? "" : "s") in the library · English only (the language GroundOne was trained on)")
                .font(.caption).foregroundStyle(.secondary)
        }
        .padding(.vertical, 40)
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
