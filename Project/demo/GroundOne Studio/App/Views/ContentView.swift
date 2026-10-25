import GroundOneCore
import SwiftUI

struct ContentView: View {
    @Environment(AppModel.self) private var model
    @State private var renaming: Chat?
    @State private var newTitle = ""
    @State private var deleting: Chat?

    var body: some View {
        @Bindable var model = model
        NavigationSplitView {
            List(selection: $model.sidebar) {
                Section {
                    ForEach(model.chats) { chat in
                        VStack(alignment: .leading, spacing: 1) {
                            Text(chat.title).lineLimit(1)
                            Text("\(chat.turns.count) question\(chat.turns.count == 1 ? "" : "s") · \(chat.updated.formatted(date: .abbreviated, time: .shortened))")
                                .font(.caption2).foregroundStyle(.secondary)
                        }
                        .tag(SidebarItem.chat(chat.id))
                        .accessibilityIdentifier("chat-row")
                        .contextMenu {
                            Button("Rename chat…") { newTitle = chat.title; renaming = chat }
                            Button("Delete chat…", role: .destructive) { deleting = chat }
                        }
                    }
                } header: {
                    HStack {
                        Text("Chats")
                        Spacer()
                        Button { model.newChat() } label: { Image(systemName: "square.and.pencil") }
                            .buttonStyle(.borderless)
                            .help("New chat")
                            .accessibilityIdentifier("new-chat")
                    }
                }
                Section("Workspace") {
                    ForEach(SidebarSection.tools) { s in
                        Label(s.rawValue, systemImage: s.symbol).tag(SidebarItem.section(s))
                            .accessibilityIdentifier("sidebar-\(s.rawValue)")
                    }
                }
            }
            .navigationSplitViewColumnWidth(min: 200, ideal: 230)
            .safeAreaInset(edge: .bottom) { EngineStatus().padding(10) }
        } detail: {
            switch model.sidebar {
            case .section(.library): LibraryView()
            case .section(.policies): PoliciesView()
            case .section(.stats): StatsView()
            case .section(.audit): AuditView()
            default: AskView()
            }
        }
        .sheet(item: $model.preview) { DocumentPreview(request: $0) }
        .alert("Rename chat", isPresented: Binding(get: { renaming != nil }, set: { if !$0 { renaming = nil } })) {
            TextField("Title", text: $newTitle)
            Button("Rename") { if let c = renaming { model.rename(c, to: newTitle) }; renaming = nil }
            Button("Cancel", role: .cancel) { renaming = nil }
        }
        .confirmationDialog("Delete “\(deleting?.title ?? "")”?", isPresented: Binding(get: { deleting != nil }, set: { if !$0 { deleting = nil } })) {
            Button("Delete chat", role: .destructive) { if let c = deleting { model.delete(c) }; deleting = nil }
        } message: {
            Text("The conversation is removed. Its verifications stay in the audit log and in Stats.")
        }
        .toolbar {
            ToolbarItem(placement: .navigation) {
                Button { model.newChat() } label: { Label("New chat", systemImage: "square.and.pencil") }
                    .keyboardShortcut("n")
            }
        }
    }
}

/// Bottom of the sidebar: what is loaded, and that everything runs on this Mac.
struct EngineStatus: View {
    @Environment(AppModel.self) private var model

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            switch model.phase {
            case .idle, .loading:
                HStack(spacing: 6) {
                    ProgressView().controlSize(.small)
                    Text(model.phase.loadingText).font(.caption).foregroundStyle(.secondary).lineLimit(2)
                }
            case .ready:
                Label("Models ready", systemImage: "checkmark.seal.fill").font(.caption.bold()).foregroundStyle(Palette.groundOne)
                    .accessibilityIdentifier("models-ready")
                Text(model.verifierName).font(.caption2).foregroundStyle(.secondary)
                if let m = model.memory {
                    Text(String(format: "MLX %.1f GB · peak %.1f GB", m.mlxActiveGB, m.mlxPeakGB)).font(.caption2).foregroundStyle(.secondary)
                }
            case .failed(let e):
                Label(e, systemImage: "exclamationmark.triangle.fill").font(.caption).foregroundStyle(.red)
            }
            Label("Local only · no network", systemImage: "lock.laptopcomputer").font(.caption2).foregroundStyle(.secondary)
            if model.fake { Text("FAKE ENGINES (UI test)").font(.caption2.bold()).foregroundStyle(.orange) }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}

extension AppModel.Phase {
    var loadingText: String {
        if case .loading(let s) = self { return s }
        return "Starting…"
    }
}
