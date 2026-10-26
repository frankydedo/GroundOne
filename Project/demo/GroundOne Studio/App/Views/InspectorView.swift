import Charts
import GroundOneCore
import SwiftUI

/// Right-hand panel: actions and numbers for the whole answer, or for the selected sentence(s).
struct InspectorView: View {
    let turn: Turn?

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                if let turn, let v = turn.shown {
                    if turn.selection.isEmpty {
                        AnswerPanel(turn: turn, version: v)
                    } else {
                        SentencePanel(turn: turn, version: v, indices: turn.selection.sorted())
                    }
                } else if let turn, turn.busy {
                    Text("Generating the answer…").foregroundStyle(.secondary)
                } else {
                    Text("Ask a question. The answer appears as the generator wrote it; verification and rewriting are here.")
                        .foregroundStyle(.secondary)
                }
            }
            .padding(16)
            .frame(maxWidth: .infinity, alignment: .leading)
        }
    }
}

struct PanelSection<Content: View>: View {
    let title: String
    @ViewBuilder let content: Content
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title.uppercased()).font(.caption.weight(.semibold)).foregroundStyle(.secondary)
            content
        }
    }
}

struct Stat: View {
    let title: String
    let value: String
    var color: Color = .primary
    var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(title).font(.caption).foregroundStyle(.secondary)
            Text(value).font(.title3.weight(.semibold).monospacedDigit()).foregroundStyle(color)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}

/// No sentence selected: verify the whole answer, compare with the judge, fix flagged sentences, sources.
struct AnswerPanel: View {
    @Environment(AppModel.self) private var model
    let turn: Turn
    let version: Version

    var body: some View {
        if version.verdicts == nil || version.judge == nil {
        PanelSection(title: "Verify") {
            if version.verdicts == nil {
                Button { model.verify(turn, judge: false) } label: {
                    Label("Verify with GroundOne", systemImage: "checkmark.shield").frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent).tint(Palette.groundOne).controlSize(.large)
                .disabled(turn.busy)
                .accessibilityIdentifier("verify-g1")
                Button { model.verify(turn, judge: true) } label: {
                    Label("Verify with GroundOne + LLM judge", systemImage: "scalemass").frame(maxWidth: .infinity)
                }
                .controlSize(.large)
                .disabled(turn.busy)
                .accessibilityIdentifier("verify-judge")
                Text("GroundOne reads the documents and the whole answer once and scores every sentence. The LLM judge is the same base model without the adapter, asked to write one verdict per sentence.")
                    .font(.caption).foregroundStyle(.secondary)
            } else if version.judge == nil {
                Button { model.verify(turn, judge: true) } label: {
                    Label("Add the LLM judge comparison", systemImage: "scalemass").frame(maxWidth: .infinity)
                }
                .disabled(turn.busy)
                .accessibilityIdentifier("verify-judge")
            }
        }
        }
        if let v = version.verdicts {
            VerdictSummary(version: version, verdicts: v)
            TimingSummary(turn: turn, version: version)
            if version.judge != nil { JudgeSummary(version: version, verdicts: v) }
            PanelSection(title: "Fix") {
                let flagged = model.flagged(version)
                Button { model.fixFlagged(turn) } label: {
                    Label(flagged.isEmpty ? "Nothing to fix" : "Fix \(flagged.count) flagged sentence\(flagged.count == 1 ? "" : "s")",
                          systemImage: "wand.and.stars").frame(maxWidth: .infinity)
                }
                .controlSize(.large)
                .disabled(flagged.isEmpty || turn.busy || !turn.isLatest)
                .accessibilityIdentifier("fix-flagged")
                Text("Policy \(model.policy.name): rewrites \(model.policy.blocking.map(\.display).joined(separator: " and ")) sentences, up to \(model.policy.maxAttempts) round\(model.policy.maxAttempts == 1 ? "" : "s"). Contradicted sentences are corrected from the source; unsupported ones are rewritten from it or removed. The new version is verified again.")
                    .font(.caption).foregroundStyle(.secondary)
            }
        } else {
            TimingSummary(turn: turn, version: version)
        }
        Text("Click a sentence for its details and actions; ⌘-click to select several.").font(.caption).foregroundStyle(.secondary)
        SourcesList(turn: turn)
    }
}

struct VerdictSummary: View {
    let version: Version
    let verdicts: Verdicts
    var body: some View {
        PanelSection(title: "GroundOne verdicts") {
            let scored = verdicts.scored
            Grid(alignment: .leading, horizontalSpacing: 12, verticalSpacing: 6) {
                ForEach(Verdict.allCases, id: \.self) { l in
                    GridRow {
                        Label(l.display, systemImage: Palette.symbol(l)).foregroundStyle(Palette.color(l))
                        Text("\(scored.filter { $0.label == l }.count)").monospacedDigit()
                    }
                }
                GridRow {
                    Label("not checked", systemImage: Palette.symbol(nil)).foregroundStyle(.secondary)
                    Text("\(verdicts.sentences.count - scored.count)").monospacedDigit().foregroundStyle(.secondary)
                }
            }
            .font(.callout)
            .accessibilityElement(children: .contain)
            .accessibilityIdentifier("verdict-summary")
            Text("Supported iff calibrated P(supported) ≥ τ = \(String(format: "%.3f", verdicts.threshold)).").font(.caption).foregroundStyle(.secondary)
        }
    }
}

struct TimingSummary: View {
    let turn: Turn
    let version: Version
    var body: some View {
        PanelSection(title: "Time") {
            Grid(alignment: .leading, horizontalSpacing: 12, verticalSpacing: 10) {
                GridRow {
                    Stat(title: version.origin == .generated ? "Generation" : "Rewriting", value: version.generation.seconds.s)
                    Stat(title: "Retrieval", value: turn.record.retrievalSeconds.s)
                }
                if let v = version.verdicts {
                    GridRow {
                        Stat(title: "GroundOne (\(v.scored.count) sentences)", value: v.seconds.s, color: Palette.groundOne)
                        if let j = version.judge {
                            Stat(title: "LLM judge (\(j.generatedTokens) tokens)", value: j.seconds.s, color: Palette.judge)
                        } else {
                            Stat(title: "LLM judge", value: "–")
                        }
                    }
                }
            }
            .accessibilityElement(children: .contain)
            .accessibilityIdentifier("timing-summary")
            if let v = version.verdicts, let j = version.judge, v.seconds > 0 {
                Text(String(format: "On this answer the LLM judge took %.1f× as long as GroundOne and generated %d tokens; GroundOne generated none.",
                            j.seconds / v.seconds, j.generatedTokens))
                    .font(.caption).foregroundStyle(.secondary)
            }
            if let v = version.verdicts, let c = v.cachedTokens, c > 0 {
                Text("The sources were already read for an earlier verification: GroundOne reused \(c) cached tokens and read only the answer\(version.judge?.cachedTokens ?? 0 > 0 ? " (the LLM judge too)" : "").")
                    .font(.caption).foregroundStyle(.secondary)
                    .accessibilityIdentifier("prefix-cache-note")
            }
        }
    }
}

struct JudgeSummary: View {
    let version: Version
    let verdicts: Verdicts
    var body: some View {
        PanelSection(title: "GroundOne vs LLM judge") {
            let scored = verdicts.scored
            let j = version.judge!
            let agree = scored.filter { j.labels[$0.index] == $0.label }.count
            Text("Same verdict on \(agree) of \(scored.count) sentences").font(.callout)
                .accessibilityIdentifier("judge-agreement")
            let disagreements = scored.filter { j.labels[$0.index] != $0.label }
            if !disagreements.isEmpty {
                ForEach(disagreements, id: \.index) { s in
                    HStack(alignment: .top, spacing: 6) {
                        Text("[\(s.index + 1)]").font(.caption.monospacedDigit()).foregroundStyle(.secondary)
                        VStack(alignment: .leading, spacing: 2) {
                            Text(s.text).font(.caption).lineLimit(2)
                            HStack {
                                Label(s.label?.display ?? "–", systemImage: Palette.symbol(s.label)).foregroundStyle(Palette.color(s.label))
                                let jl = j.labels[s.index] ?? nil
                                Label("LLM judge: \(jl?.display ?? "unparsed")", systemImage: Palette.symbol(jl)).foregroundStyle(Palette.color(jl))
                            }
                            .font(.caption)
                        }
                    }
                }
            }
        }
    }
}

/// One or more sentences selected: their verdicts, the judge, evidence, rewriting.
struct SentencePanel: View {
    @Environment(AppModel.self) private var model
    let turn: Turn
    let version: Version
    let indices: [Int]

    var body: some View {
        let sentences = indices.compactMap { version.sentences[safe: $0] }
        HStack {
            Text(sentences.count == 1 ? "Sentence \(indices[0] + 1)" : "\(sentences.count) sentences").font(.headline)
            Spacer()
            Button("Deselect") { turn.selection = [] }.buttonStyle(.link)
        }
        ForEach(sentences, id: \.index) { s in
            SentenceDetail(sentence: s, judge: version.judge, verified: version.verdicts != nil,
                           groundOneSeconds: version.verdicts?.seconds, k: version.verdicts?.scored.count ?? 0)
        }
        PanelSection(title: "Actions") {
            if version.verdicts == nil {
                Button { model.verify(turn, judge: false) } label: {
                    Label("Verify the answer with GroundOne", systemImage: "checkmark.shield").frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent).tint(Palette.groundOne)
                .disabled(turn.busy)
                Button { model.verify(turn, judge: true) } label: {
                    Label("Verify with GroundOne + LLM judge", systemImage: "scalemass").frame(maxWidth: .infinity)
                }
                .disabled(turn.busy)
            }
            if sentences.count == 1 {
                Button { model.findEvidence(turn, sentence: indices[0]) } label: {
                    Label(turn.evidenceLoading ? "Finding evidence…" : "Find evidence", systemImage: "doc.text.magnifyingglass")
                        .frame(maxWidth: .infinity)
                }
                .disabled(turn.evidenceLoading)
                .accessibilityIdentifier("find-evidence")
            }
            Button { model.fix(turn, indices: indices) } label: {
                Label(sentences.count == 1 ? "Rewrite this sentence" : "Rewrite \(sentences.count) sentences", systemImage: "wand.and.stars")
                    .frame(maxWidth: .infinity)
            }
            .disabled(turn.busy || !turn.isLatest)
            .accessibilityIdentifier("rewrite-selected")
            Text("Find evidence verifies the answer against each retrieved passage (one GroundOne pass per passage) and opens the passage where the sentence is most supported or contradicted. Rewriting uses the closest part of the documents and is verified again.")
                .font(.caption).foregroundStyle(.secondary)
        }
    }
}

struct SentenceDetail: View {
    let sentence: SentenceVerdict
    let judge: JudgeVerdicts?
    let verified: Bool
    let groundOneSeconds: Double?
    let k: Int

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("“\(sentence.text)”").font(.callout).italic().textSelection(.enabled)
            if !sentence.scored, verified {
                Label("Not checked: no checkable content", systemImage: Palette.symbol(nil)).font(.caption).foregroundStyle(.secondary)
            } else if let p = sentence.probs {
                Label("GroundOne: \(sentence.label?.display ?? "–")", systemImage: Palette.symbol(sentence.label))
                    .foregroundStyle(Palette.color(sentence.label)).font(.callout.weight(.medium))
                    .accessibilityIdentifier("sentence-verdict")
                ProbabilityBar(p: p).frame(height: 8)
                HStack(spacing: 10) {
                    ForEach(0..<3, id: \.self) { i in
                        Text("\(Verdict(index: i).display) \(p[i].p2)").font(.caption.monospacedDigit()).foregroundStyle(.secondary)
                    }
                }
                if let jl = judge?.labels[sentence.index] {
                    Label("LLM judge: \(jl?.display ?? "unparsed")", systemImage: Palette.symbol(jl ?? nil))
                        .foregroundStyle(Palette.color(jl ?? nil)).font(.callout)
                }
                if let t = groundOneSeconds {
                    Text("Scored with the other \(max(k - 1, 0)) sentences in one GroundOne pass of \(t.s)\(judge.map { "; the LLM judge took \($0.seconds.s) for the whole answer" } ?? "").")
                        .font(.caption).foregroundStyle(.secondary)
                }
            } else {
                Text("Not verified yet.").font(.caption).foregroundStyle(.secondary)
            }
        }
        .padding(10)
        .background(RoundedRectangle(cornerRadius: 8).fill(Color.secondary.opacity(0.07)))
    }
}

/// The retrieved passages: the documents GroundOne reads. A click opens the preview.
struct SourcesList: View {
    @Environment(AppModel.self) private var model
    let turn: Turn
    @State private var open = false

    var body: some View {
        DisclosureGroup(isExpanded: $open) {
            VStack(alignment: .leading, spacing: 8) {
                ForEach(Array(turn.record.passages.enumerated()), id: \.offset) { i, p in
                    Button {
                        model.preview = DocumentPreviewRequest(title: p.title, path: p.fileURL?.path, highlight: String(p.text.prefix(120)),
                                                               kind: nil, note: "Retrieved passage \(i + 1)", sentence: nil,
                                                               fallbackText: p.text)
                    } label: {
                        VStack(alignment: .leading, spacing: 2) {
                            Text("\(i + 1). \(p.title)").font(.caption.weight(.semibold)).lineLimit(1)
                            Text(p.text).font(.caption).foregroundStyle(.secondary).lineLimit(3)
                        }
                    }
                    .buttonStyle(.plain)
                }
            }
            .padding(.top, 4)
        } label: {
            Text("SOURCES (\(turn.record.passages.count) passages)").font(.caption.weight(.semibold)).foregroundStyle(.secondary)
        }
    }
}
