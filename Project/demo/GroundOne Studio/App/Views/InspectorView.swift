import Charts
import GroundOneCore
import SwiftUI

/// Right-hand panel for the selected question: timing and memory, judge comparison, retrieved passages.
struct InspectorView: View {
    let turn: Turn?
    @State private var tab = 0

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            Picker("", selection: $tab) {
                Text("Timing").tag(0); Text("Judge").tag(1); Text("Passages").tag(2)
            }
            .pickerStyle(.segmented)
            .labelsHidden()
            .padding(12)
            .accessibilityIdentifier("inspector-tabs")
            Divider()
            ScrollView {
                if let turn {
                    switch tab {
                    case 0: TimingPanel(turn: turn)
                    case 1: JudgePanel(turn: turn)
                    default: PassagesPanel(turn: turn)
                    }
                } else {
                    Text("Ask a question to see how the time is spent.").foregroundStyle(.secondary).padding()
                }
            }
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

struct TimingPanel: View {
    let turn: Turn

    struct Bar: Identifiable {
        let id = UUID()
        let step: String
        let kind: String
        let seconds: Double
    }

    var bars: [Bar] {
        var out: [Bar] = []
        if let r = turn.record, r.timings.retrieval > 0 { out.append(Bar(step: "Retrieval", kind: "Retrieval", seconds: r.timings.retrieval)) }
        for d in turn.drafts {
            let name = d.round == 0 ? "Draft" : "Rewrite \(d.round)"
            if d.generation.seconds > 0 { out.append(Bar(step: name, kind: "Generation", seconds: d.generation.seconds)) }
            out.append(Bar(step: name, kind: "GroundOne", seconds: d.verdicts.seconds))
        }
        if let j = turn.judge { out.append(Bar(step: "Judge", kind: "Judge (comparison)", seconds: j.seconds)) }
        return out
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            let gen = turn.drafts.map(\.generation.seconds).reduce(0, +)
            let ver = turn.drafts.map(\.verdicts.seconds).reduce(0, +)
            Grid(alignment: .leading, horizontalSpacing: 12, verticalSpacing: 12) {
                GridRow {
                    Stat(title: "Generation", value: gen.s)
                    Stat(title: "GroundOne", value: ver.s, color: Palette.groundOne)
                }
                GridRow {
                    Stat(title: "Share of verification", value: gen + ver > 0 ? (ver / (gen + ver)).pct : "–", color: Palette.groundOne)
                    Stat(title: "Rewrites", value: "\(max(turn.drafts.count - 1, 0))")
                }
                if let r = turn.record {
                    GridRow {
                        Stat(title: "Total", value: r.timings.total.s)
                        Stat(title: "MLX peak memory", value: String(format: "%.2f GB", r.memory?.mlxPeakGB ?? 0))
                    }
                }
            }
            .accessibilityElement(children: .contain)
            .accessibilityIdentifier("timing-stats")
            Chart(bars) { b in
                BarMark(x: .value("Seconds", b.seconds), y: .value("Step", b.step))
                    .foregroundStyle(by: .value("Kind", b.kind))
            }
            .chartForegroundStyleScale([
                "Retrieval": Color.gray, "Generation": Color(red: 0.55, green: 0.55, blue: 0.62),
                "GroundOne": Palette.groundOne, "Judge (comparison)": Color(red: 0.62, green: 0.36, blue: 0.70),
            ])
            .chartXAxisLabel("seconds")
            .frame(height: CGFloat(max(bars.count, 2)) * 34 + 40)
            if let d = turn.drafts.first {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Per draft").font(.headline)
                    ForEach(turn.drafts, id: \.round) { d in
                        Text("\(d.round == 0 ? "Draft" : "Rewrite \(d.round)"): \(d.generation.generatedTokens) tokens generated in \(d.generation.seconds.s); GroundOne read \(d.verdicts.inputTokens) tokens and scored \(d.verdicts.scored.count) sentences in \(d.verdicts.seconds.s)")
                            .font(.caption).foregroundStyle(.secondary)
                    }
                    if d.generation.timeToFirstToken > 0 {
                        Text("Time to first token: \(d.generation.timeToFirstToken.s)").font(.caption).foregroundStyle(.secondary)
                    }
                }
            }
            Text("All three models run in this process on the GPU, one call at a time, so the times are not confounded by contention.")
                .font(.caption2).foregroundStyle(.tertiary)
        }
        .padding(14)
    }
}

/// Mandatory comparison (§1): the same base model without the adapter, prompted as the B0a terse judge.
struct JudgePanel: View {
    let turn: Turn

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            if let j = turn.judge, let d = turn.drafts.first {
                let scored = d.verdicts.scored
                let agree = scored.filter { j.labels[$0.index] == $0.label }.count
                Grid(alignment: .leading, horizontalSpacing: 12, verticalSpacing: 12) {
                    GridRow {
                        Stat(title: "GroundOne", value: d.verdicts.seconds.s, color: Palette.groundOne)
                        Stat(title: "Generative judge", value: j.seconds.s, color: Color(red: 0.62, green: 0.36, blue: 0.70))
                    }
                    GridRow {
                        Stat(title: "Tokens generated", value: "0 vs \(j.generatedTokens)")
                        Stat(title: "Agreement", value: "\(agree)/\(scored.count)")
                    }
                }
                .accessibilityElement(children: .contain)
                .accessibilityIdentifier("judge-stats")
                if d.verdicts.seconds > 0 {
                    Text(String(format: "The judge took %.1f× as long as GroundOne on this answer.", j.seconds / d.verdicts.seconds))
                        .font(.callout)
                }
                Divider()
                ForEach(scored, id: \.index) { s in
                    HStack(alignment: .top) {
                        Text("[\(s.index + 1)]").font(.caption.monospacedDigit()).foregroundStyle(.secondary).frame(width: 26, alignment: .leading)
                        VStack(alignment: .leading, spacing: 3) {
                            Text(s.text).font(.caption).lineLimit(2)
                            HStack(spacing: 10) {
                                Label(s.label?.display ?? "–", systemImage: Palette.symbol(s.label)).foregroundStyle(Palette.color(s.label))
                                let jl = j.labels[s.index] ?? nil
                                Label("judge: \(jl?.display ?? "unparsed")", systemImage: Palette.symbol(jl)).foregroundStyle(Palette.color(jl))
                            }
                            .font(.caption)
                        }
                    }
                }
                DisclosureGroup("Raw judge output") {
                    Text(j.rawText).font(.caption.monospaced()).textSelection(.enabled).frame(maxWidth: .infinity, alignment: .leading)
                }
                .font(.caption)
                Text("Judge: Qwen2.5-3B base without the LoRA adapter, terse prompt of baseline B0a, greedy decoding. It runs on the same weights as GroundOne, so it costs no extra memory and never leaves the machine.")
                    .font(.caption2).foregroundStyle(.tertiary)
            } else if turn.running {
                Text("The judge runs after GroundOne's first verification.").foregroundStyle(.secondary)
            } else {
                Text("Judge comparison was off for this question.").foregroundStyle(.secondary)
            }
        }
        .padding(14)
    }
}

struct PassagesPanel: View {
    let turn: Turn
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            if turn.passages.isEmpty { Text("No passages yet.").foregroundStyle(.secondary) }
            ForEach(Array(turn.passages.enumerated()), id: \.offset) { i, p in
                VStack(alignment: .leading, spacing: 4) {
                    Text("passage \(i + 1) · \(p.title)\(p.page.map { " · p.\($0 + 1)" } ?? "")").font(.caption.weight(.semibold))
                    Text(p.text).font(.caption).foregroundStyle(.secondary).lineLimit(8).textSelection(.enabled)
                }
                Divider()
            }
            if !turn.passages.isEmpty {
                Text("These passages, with the question, are the document GroundOne reads (hybrid retrieval: BM25 + embeddings, reciprocal rank fusion).")
                    .font(.caption2).foregroundStyle(.tertiary)
            }
        }
        .padding(14)
    }
}
