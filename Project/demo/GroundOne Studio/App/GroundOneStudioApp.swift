import GroundOneCore
import SwiftUI

@main
struct GroundOneStudioApp: App {
    @State private var model = AppModel()

    var body: some Scene {
        WindowGroup("GroundOne Studio") {
            ContentView()
                .environment(model)
                .frame(minWidth: 1100, minHeight: 720)
                .task { await model.load() }
        }
        .windowToolbarStyle(.unified)
        .commands {
            CommandGroup(replacing: .newItem) {}
        }
    }
}

/// Verdict colours, shared by every view (green supported, red contradicted, amber not mentioned, grey unscored).
enum Palette {
    static func color(_ label: Verdict?) -> Color {
        switch label {
        case .supported: Color(red: 0.13, green: 0.55, blue: 0.33)
        case .contradicted: Color(red: 0.80, green: 0.18, blue: 0.20)
        case .notMentioned: Color(red: 0.85, green: 0.52, blue: 0.05)
        case nil: .secondary
        }
    }

    static func symbol(_ label: Verdict?) -> String {
        switch label {
        case .supported: "checkmark.circle.fill"
        case .contradicted: "xmark.octagon.fill"
        case .notMentioned: "questionmark.circle.fill"
        case nil: "minus.circle"
        }
    }

    static let groundOne = Color(red: 0.12, green: 0.37, blue: 0.75)
}

extension Double {
    var s: String { String(format: self < 10 ? "%.2f s" : "%.1f s", self) }
    var pct: String { String(format: "%.0f%%", self * 100) }
    var p2: String { String(format: "%.2f", self) }
}
typealias Verdict = GroundOneCore.Label
extension SourceLink: @retroactive Identifiable { public var id: Int { hashValue } }
