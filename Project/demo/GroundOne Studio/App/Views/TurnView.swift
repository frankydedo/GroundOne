import GroundOneCore
import SwiftUI

struct TurnView: View {
    @Environment(AppModel.self) private var model
    let turn: Turn
    let selected: Bool
    @State private var showDetails = true
    @State private var source: SourceLink?

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(turn.question)
                .font(.title3.weight(.semibold))
                .accessibilityIdentifier("turn-question")
            if let stage = turn.stage {
                HStack(spacing: 8) {
                    ProgressView().controlSize(.small)
                    Text(stage).font(.callout).foregroundStyle(stage.contains("GroundOne") ? Palette.groundOne : .secondary)
                }
                .accessibilityIdentifier("turn-stage")
            }
            if let e = turn.error {
                Label(e, systemImage: "exclamationmark.triangle").foregroundStyle(.red)
            }
            if turn.drafts.isEmpty, !turn.partial.isEmpty {
                Text(turn.partial).foregroundStyle(.secondary).textSelection(.enabled)
            }
            if let draft = turn.shownDraft {
                if turn.drafts.count > 1 { DraftPicker(turn: turn) }
                if let rec = turn.record, turn.selectedDraft == nil || turn.selectedDraft == turn.drafts.count - 1 {
                    StatusBanner(record: rec)
                }
                if let rec = turn.record, rec.status == .abstained || rec.status == .hidden,
                   turn.selectedDraft == nil || turn.selectedDraft == turn.drafts.count - 1 {
                    Text(rec.displayed).font(.body).padding(12).frame(maxWidth: .infinity, alignment: .leading)
                        .background(RoundedRectangle(cornerRadius: 10).fill(.quaternary.opacity(0.5)))
                        .accessibilityIdentifier("displayed-answer")
                    Text("GroundOne's view of the last draft:").font(.caption).foregroundStyle(.secondary)
                }
                VerifiedText(draft: draft)
                    .accessibilityIdentifier("verified-answer")
                DisclosureGroup(isExpanded: $showDetails) {
                    SentenceTable(turn: turn, draft: draft, source: $source)
                } label: {
                    HStack {
                        Text("Sentences").font(.callout.weight(.medium))
                        Spacer()
                        Text("GroundOne \(draft.verdicts.seconds.s) · \(draft.verdicts.inputTokens) tokens · 0 generated")
                            .font(.caption).foregroundStyle(Palette.groundOne)
                    }
                }
                .accessibilityIdentifier("sentence-details")
            }
        }
        .padding(18)
        .background(RoundedRectangle(cornerRadius: 14).fill(Color(nsColor: .controlBackgroundColor)))
        .overlay(RoundedRectangle(cornerRadius: 14).stroke(selected ? Palette.groundOne.opacity(0.5) : Color.secondary.opacity(0.15), lineWidth: selected ? 2 : 1))
        .sheet(item: $source) { SourceViewer(link: $0) }
    }
}

struct DraftPicker: View {
    let turn: Turn
    var body: some View {
        Picker("Draft", selection: Binding(get: { turn.selectedDraft ?? turn.drafts.count - 1 }, set: { turn.selectedDraft = $0; turn.links = nil })) {
            ForEach(turn.drafts.indices, id: \.self) { i in
                Text(i == 0 ? "First draft" : "Rewrite \(i)").tag(i)
            }
        }
        .pickerStyle(.segmented)
        .labelsHidden()
        .frame(maxWidth: 360)
        .accessibilityIdentifier("draft-picker")
    }
}

struct StatusBanner: View {
    let record: QueryRecord
    var body: some View {
        let (text, color, symbol): (String, Color, String) = switch record.status {
        case .accepted: (record.rounds == 0 ? "Accepted by GroundOne" : "Accepted by GroundOne after \(record.rounds) rewrite\(record.rounds == 1 ? "" : "s")", Palette.color(.supported), "checkmark.shield.fill")
        case .highlighted: ("Shown with flagged sentences highlighted (policy: highlight)", Palette.color(.notMentioned), "highlighter")
        case .hidden: ("Flagged sentences hidden (policy: hide)", Palette.color(.notMentioned), "eye.slash")
        case .abstained: ("Abstained: no draft passed GroundOne (policy: abstain)", Palette.color(.contradicted), "hand.raised.fill")
        }
        Label(text, systemImage: symbol)
            .font(.callout.weight(.medium))
            .foregroundStyle(color)
            .padding(.horizontal, 10).padding(.vertical, 5)
            .background(Capsule().fill(color.opacity(0.12)))
            .accessibilityElement(children: .ignore)
            .accessibilityLabel(text)
            .accessibilityIdentifier("status-banner")
    }
}

/// The answer as running text, each checked sentence tinted by its GroundOne verdict.
struct VerifiedText: View {
    let draft: Draft
    var body: some View {
        Text(attributed).font(.body).lineSpacing(4).textSelection(.enabled)
            .frame(maxWidth: .infinity, alignment: .leading)
    }

    var attributed: AttributedString {
        var a = AttributedString(draft.text)
        for s in draft.verdicts.sentences {
            guard let r = Range(NSRange(location: s.start, length: s.end - s.start), in: a) else { continue }
            if s.scored {
                a[r].backgroundColor = Palette.color(s.label).opacity(s.label == .supported ? 0.10 : 0.20)
                if s.label != .supported {
                    a[r].underlineStyle = .single
                    a[r].underlineColor = NSColor(Palette.color(s.label))
                }
            } else {
                a[r].foregroundColor = .secondary
            }
        }
        return a
    }
}

struct SentenceTable: View {
    @Environment(AppModel.self) private var model
    let turn: Turn
    let draft: Draft
    @Binding var source: SourceLink?

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            ForEach(draft.verdicts.sentences, id: \.index) { s in
                SentenceRow(sentence: s, judge: draft.round == 0 ? turn.judge?.labels[s.index] ?? nil : nil,
                            judged: draft.round == 0 && turn.judge != nil, links: turn.links?[s.index] ?? [],
                            showProbabilities: turn.record?.policy.showProbabilities ?? true, source: $source)
            }
            if !turn.passages.isEmpty {
                HStack {
                    if turn.links == nil {
                        Button {
                            model.loadLinks(for: turn)
                        } label: {
                            Label(turn.linksLoading ? "Finding evidence…" : "Find evidence in the sources", systemImage: "link")
                        }
                        .disabled(turn.linksLoading)
                        .accessibilityIdentifier("find-evidence")
                    }
                    Text("Evidence suggested by GroundOne (one pass per passage; not evaluated)").font(.caption).foregroundStyle(.secondary)
                }
                .padding(.top, 4)
            }
        }
        .padding(.top, 6)
    }
}

struct SentenceRow: View {
    let sentence: SentenceVerdict
    let judge: Verdict?
    let judged: Bool
    let links: [SourceLink]
    let showProbabilities: Bool
    @Binding var source: SourceLink?
    @State private var hover = false

    var body: some View {
        HStack(alignment: .top, spacing: 10) {
            Image(systemName: Palette.symbol(sentence.label)).foregroundStyle(Palette.color(sentence.label)).font(.body)
                .frame(width: 18)
            VStack(alignment: .leading, spacing: 5) {
                Text("[\(sentence.index + 1)] \(sentence.text)").font(.callout).foregroundStyle(sentence.scored ? .primary : .secondary)
                HStack(spacing: 8) {
                    if let p = sentence.probs, showProbabilities {
                        ProbabilityBar(p: p).frame(width: 120, height: 7)
                        Text("P(supported) \(p[0].p2)").font(.caption.monospacedDigit()).foregroundStyle(.secondary)
                    } else if !sentence.scored {
                        Text("not checked (no checkable content)").font(.caption).foregroundStyle(.secondary)
                    }
                    if judged, sentence.scored {
                        Text("Judge: \(judge?.display ?? "unparsed")")
                            .font(.caption.weight(.medium))
                            .padding(.horizontal, 6).padding(.vertical, 1)
                            .background(Capsule().strokeBorder(Palette.color(judge).opacity(0.6)))
                            .foregroundStyle(Palette.color(judge))
                    }
                    ForEach(links, id: \.self) { l in
                        Button { source = l } label: {
                            Label("\(l.kind == .supported ? "Supported by" : "Contradicted by") \(l.passage.title)\(l.passage.page.map { " p.\($0 + 1)" } ?? "")",
                                  systemImage: "arrow.up.right.square")
                                .font(.caption)
                        }
                        .buttonStyle(.link)
                        .foregroundStyle(Palette.color(l.kind))
                        .accessibilityIdentifier("source-link")
                    }
                }
            }
        }
        .padding(8)
        .background(RoundedRectangle(cornerRadius: 8).fill(hover ? Color.secondary.opacity(0.08) : .clear))
        .onHover { hover = $0 }
        .help(sentence.probs.map { p in
            "GroundOne (calibrated): supported \(p[0].p2), contradicted \(p[1].p2), not mentioned \(p[2].p2)"
        } ?? "Not checked: the sentence has no checkable content")
        .accessibilityElement(children: .contain)
        .accessibilityIdentifier("sentence-row")
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
