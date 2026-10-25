import AppKit
import GroundOneCore
import SwiftUI

/// One question: the answer as the generator wrote it, its versions, and, once verified, sentences tinted by verdict.
/// Sentences are clickable (⌘-click to select several); details and actions are in the inspector.
struct TurnView: View {
    @Environment(AppModel.self) private var model
    let turn: Turn
    let selected: Bool

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(turn.question)
                .font(.title3.weight(.semibold))
                .accessibilityIdentifier("turn-question")
            if let e = turn.error {
                Label(e, systemImage: "exclamationmark.triangle").foregroundStyle(.red)
            }
            if turn.record.versions.isEmpty {
                if !turn.partial.isEmpty {
                    Text(turn.partial).font(.body).lineSpacing(5)
                        .frame(maxWidth: .infinity, alignment: .leading)
                }
            } else if let v = turn.shown {
                if turn.record.versions.count > 1 { VersionPicker(turn: turn) }
                StatusLine(version: v)
                AnswerText(turn: turn, version: v)
                    .accessibilityIdentifier("answer-text")
            }
            if let stage = turn.stage {
                HStack(spacing: 8) {
                    ProgressView().controlSize(.small)
                    Text(stage).font(.callout).foregroundStyle(stage.contains("GroundOne") ? Palette.groundOne : .secondary)
                }
                .accessibilityIdentifier("turn-stage")
            }
        }
        .padding(18)
        .background(RoundedRectangle(cornerRadius: 14).fill(Color(nsColor: .controlBackgroundColor)))
        .overlay(RoundedRectangle(cornerRadius: 14).stroke(selected ? Palette.groundOne.opacity(0.5) : Color.secondary.opacity(0.15),
                                                           lineWidth: selected ? 2 : 1))
    }
}

struct VersionPicker: View {
    let turn: Turn
    var body: some View {
        Picker("Version", selection: Binding(get: { turn.shownIndex ?? 0 }, set: { turn.versionIndex = $0; turn.selection = [] })) {
            ForEach(turn.record.versions.indices, id: \.self) { i in
                Text(i == 0 ? "Generated" : "Fix \(i)").tag(i)
            }
        }
        .pickerStyle(.segmented)
        .labelsHidden()
        .frame(maxWidth: 380)
        .accessibilityIdentifier("version-picker")
    }
}

/// One line under the question: native or verified, counts by verdict.
struct StatusLine: View {
    let version: Version

    var body: some View {
        HStack(spacing: 12) {
            if let v = version.verdicts {
                let scored = v.scored
                Label("Verified by GroundOne\(version.judge != nil ? " and the judge" : "")", systemImage: "checkmark.shield")
                    .foregroundStyle(Palette.groundOne)
                ForEach(Verdict.allCases, id: \.self) { l in
                    let n = scored.filter { $0.label == l }.count
                    if n > 0 { Label("\(n)", systemImage: Palette.symbol(l)).foregroundStyle(Palette.color(l)).help(l.display) }
                }
            } else {
                Label(version.origin == .generated ? "Generated answer · not verified" : "Rewritten · not verified",
                      systemImage: "text.alignleft").foregroundStyle(.secondary)
            }
            Spacer()
            Text("\(version.text.split(whereSeparator: \.isWhitespace).count) words").foregroundStyle(.secondary)
        }
        .font(.callout)
        .accessibilityElement(children: .ignore)
        .accessibilityLabel(version.verdicts == nil ? "not verified" : "verified")
        .accessibilityIdentifier("status-line")
    }
}

/// The answer as running text; every sentence is a link that selects it.
struct AnswerText: View {
    @Environment(AppModel.self) private var model
    let turn: Turn
    let version: Version

    var body: some View {
        Text(attributed)
            .font(.body)
            .lineSpacing(5)
            .tint(.primary)
            .frame(maxWidth: .infinity, alignment: .leading)
            .environment(\.openURL, OpenURLAction { url in
                guard url.scheme == "g1s", let i = Int(url.host() ?? "") else { return .systemAction }
                select(i)
                return .handled
            })
    }

    func select(_ i: Int) {
        model.selectedTurn = turn.id
        if NSEvent.modifierFlags.contains(.command) || NSEvent.modifierFlags.contains(.shift) {
            if turn.selection.contains(i) { turn.selection.remove(i) } else { turn.selection.insert(i) }
        } else {
            turn.selection = turn.selection == [i] ? [] : [i]
        }
    }

    var attributed: AttributedString {
        var a = AttributedString(version.text)
        let verified = version.verdicts != nil
        for s in version.sentences {
            guard let r = Range(NSRange(location: s.start, length: s.end - s.start), in: a) else { continue }
            a[r].link = URL(string: "g1s://\(s.index)")
            if turn.selection.contains(s.index) {
                a[r].backgroundColor = Palette.selection
            } else if verified, s.scored {
                a[r].backgroundColor = Palette.color(s.label).opacity(s.label == .supported ? 0.12 : 0.22)
            }
            if verified, !s.scored { a[r].foregroundColor = .secondary }
            if verified, s.scored, s.label != .supported {
                a[r].underlineStyle = .single
                a[r].underlineColor = NSColor(Palette.color(s.label))
            }
        }
        return a
    }
}

/// Stacked bar of the three calibrated probabilities.
struct ProbabilityBar: View {
    let p: [Double]
    var body: some View {
        GeometryReader { g in
            HStack(spacing: 1) {
                ForEach(0..<3, id: \.self) { k in
                    Rectangle().fill(Palette.color(Verdict(index: k))).frame(width: max(0, g.size.width * p[k] - 1))
                }
            }
            .clipShape(Capsule())
        }
    }
}
