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
                .preferredColorScheme(ProcessInfo.processInfo.arguments.contains("-lightAppearance") ? .light : nil)
        }
        .windowToolbarStyle(.unified)
        .commands {
            CommandGroup(replacing: .newItem) {}
        }
    }
}

/// Colours. Verdicts use the status palette (always shown with an icon and a label); the two systems compared in the
/// charts use the first two validated categorical slots (blue, orange), stepped for dark mode.
enum Palette {
    static func dynamic(_ light: UInt32, _ dark: UInt32) -> Color {
        Color(nsColor: NSColor(name: nil) { appearance in
            let hex = appearance.bestMatch(from: [.darkAqua, .aqua]) == .darkAqua ? dark : light
            return NSColor(srgbRed: CGFloat((hex >> 16) & 0xFF) / 255, green: CGFloat((hex >> 8) & 0xFF) / 255,
                           blue: CGFloat(hex & 0xFF) / 255, alpha: 1)
        })
    }

    static func color(_ label: Verdict?) -> Color {
        switch label {
        case .supported: dynamic(0x0CA30C, 0x0CA30C)
        case .contradicted: dynamic(0xD03B3B, 0xD03B3B)
        case .notMentioned: dynamic(0xEC835A, 0xEC835A)
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

    static let groundOne = dynamic(0x2A78D6, 0x3987E5)
    static let judge = dynamic(0xEB6834, 0xD95926)
    static let generation = dynamic(0x8C8C99, 0x7A7A86)
    static let selection = Color.accentColor.opacity(0.28)
}

extension Double {
    var s: String { String(format: self < 10 ? "%.2f s" : "%.1f s", self) }
    var pct: String { String(format: "%.0f%%", self * 100) }
    var p2: String { String(format: "%.2f", self) }
}
typealias Verdict = GroundOneCore.Label
extension SourceLink: @retroactive Identifiable { public var id: Int { hashValue } }
