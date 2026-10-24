import GroundOneCore
import SwiftUI

struct ContentView: View {
    @Environment(AppModel.self) private var model

    var body: some View {
        @Bindable var model = model
        NavigationSplitView {
            List(SidebarSection.allCases, selection: $model.section) { s in
                Label(s.rawValue, systemImage: s.symbol).tag(s)
                    .accessibilityIdentifier("sidebar-\(s.rawValue)")
            }
            .navigationSplitViewColumnWidth(min: 170, ideal: 190)
            .safeAreaInset(edge: .bottom) { EngineStatus().padding(10) }
        } detail: {
            switch model.section ?? .ask {
            case .ask: AskView()
            case .library: LibraryView()
            case .policies: PoliciesView()
            case .measurements: MeasurementsView()
            case .audit: AuditView()
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
