import Charts
import GroundOneCore
import GroundOneEngines
import SwiftUI

/// Live and historical performance of the app, from every question in the audit log (this session included).
struct StatsView: View {
    @Environment(AppModel.self) private var model
    @AppStorage("statsPricingModel") private var pricingModel = Pricing.shared.defaultModel
    @State private var range = 0

    var checks: [Check] {
        let cutoff: Date? = range == 1 ? Calendar.current.startOfDay(for: Date()) : nil
        return Check.all(from: model.history).filter { cutoff == nil || $0.date >= cutoff! }
    }

    var body: some View {
        let cs = checks
        let p = Pricing.shared
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                HStack(alignment: .firstTextBaseline) {
                    VStack(alignment: .leading, spacing: 2) {
                        Text("Stats").font(.title2.bold())
                        Text("Every verification made in the app, from the audit log; updates live.").font(.caption).foregroundStyle(.secondary)
                    }
                    Spacer()
                    Picker("", selection: $range) { Text("All time").tag(0); Text("Today").tag(1) }
                        .pickerStyle(.segmented).labelsHidden().frame(width: 180)
                    Picker("Priced as", selection: $pricingModel) {
                        ForEach(p.models, id: \.self) { Text($0).tag($0) }
                    }
                    .frame(width: 240)
                    .help("Hosted model used to price the verifications done locally")
                }
                KPIRow(checks: cs, records: model.history, model: pricingModel)
                if cs.isEmpty {
                    Text("No verifications yet. Ask a question and verify the answer: the charts fill in as you go.")
                        .foregroundStyle(.secondary).padding(.vertical, 30)
                } else {
                    HStack(alignment: .top, spacing: 16) {
                        Card(title: "Verification time vs sentences per answer",
                             caption: "Each answer verified, once per system. GroundOne reads the answer once; the LLM judge writes a verdict per sentence.") {
                            TimeVsSentences(checks: cs)
                        }
                        Card(title: "Cost of the same verifications on a hosted LLM judge",
                             caption: "Cumulative, priced as \(pricingModel) (list prices, \(p.accessed)); local electricity subtracted.") {
                            SavedOverTime(checks: cs, model: pricingModel)
                        }
                    }
                    HStack(alignment: .top, spacing: 16) {
                        Card(title: "GroundOne verdicts", caption: "Checked sentences in all verified answers.") {
                            VerdictBars(checks: cs)
                        }
                        Card(title: "GroundOne vs LLM judge, same sentences",
                             caption: "Rows: GroundOne. Columns: LLM judge. Agreement on the diagonal.") {
                            AgreementMatrix(checks: cs)
                        }
                    }
                }
                OfflineBenchmark()
                Text(p.notes).font(.caption2).foregroundStyle(.tertiary)
            }
            .padding(20)
        }
        .navigationTitle("Stats")
    }
}

/// One verification of one answer version.
struct Check: Identifiable {
    let id = UUID()
    let date: Date
    let k: Int
    let groundOne: Double
    let judge: Double?
    let judgeTokens: Int?
    let inputTokens: Int
    let labels: [Verdict]
    let pairs: [(Verdict, Verdict?)]

    static func all(from records: [StudioRecord]) -> [Check] {
        records.flatMap { r in
            r.versions.compactMap { v -> Check? in
                guard let vd = v.verdicts else { return nil }
                let scored = vd.scored
                return Check(date: r.date, k: scored.count, groundOne: vd.seconds, judge: v.judge?.seconds,
                             judgeTokens: v.judge?.generatedTokens, inputTokens: vd.inputTokens,
                             labels: scored.compactMap(\.label),
                             pairs: v.judge.map { j in scored.compactMap { s in s.label.map { ($0, j.labels[s.index] ?? nil) } } } ?? [])
            }
        }
    }
}

struct Pricing {
    let prices: [String: [Double]]
    let defaultModel: String
    let instructionTokens: Double
    let judgeTokensPerSentence: Double
    let watts: Double
    let eurPerKWh: Double
    let usdPerEur: Double
    let accessed = "accessed 2026-10-19"
    let notes: String

    var models: [String] { prices.keys.sorted() }

    static let shared: Pricing = {
        struct File: Decodable {
            let usd_per_million_tokens: [String: [Double]]
            let default_model: String
            let instruction_tokens: Double
            let judge_tokens_per_sentence: Double
            let local_watts_during_verification: Double
            let eur_per_kwh: Double
            let usd_per_eur: Double
            let notes: String
        }
        let url = Bundle.main.url(forResource: "pricing", withExtension: "json")
        let f = url.flatMap { try? JSONDecoder().decode(File.self, from: Data(contentsOf: $0)) }
        return Pricing(prices: f?.usd_per_million_tokens ?? ["Claude Sonnet 5.5": [2, 10]], defaultModel: f?.default_model ?? "Claude Sonnet 5.5",
                       instructionTokens: f?.instruction_tokens ?? 150, judgeTokensPerSentence: f?.judge_tokens_per_sentence ?? 4.15,
                       watts: f?.local_watts_during_verification ?? 16.2, eurPerKWh: f?.eur_per_kwh ?? 0.2896,
                       usdPerEur: f?.usd_per_eur ?? 1.08, notes: f?.notes ?? "")
    }()

    func hosted(_ c: Check, model: String) -> Double {
        let p = prices[model] ?? [2, 10]
        let out = Double(c.judgeTokens ?? Int((judgeTokensPerSentence * Double(c.k)).rounded()))
        return ((Double(c.inputTokens) + instructionTokens) * p[0] + out * p[1]) / 1e6
    }

    func local(_ c: Check) -> Double { c.groundOne * watts / 3.6e6 * eurPerKWh * usdPerEur }
    func saved(_ c: Check, model: String) -> Double { hosted(c, model: model) - local(c) }
}

struct Card<Content: View>: View {
    let title: String
    let caption: String
    @ViewBuilder let content: Content
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title).font(.headline)
            Text(caption).font(.caption).foregroundStyle(.secondary)
            content.frame(height: 230)
        }
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color(nsColor: .controlBackgroundColor)))
    }
}

struct KPITile: View {
    let title: String
    let value: String
    var detail: String = ""
    var color: Color = .primary
    var body: some View {
        VStack(alignment: .leading, spacing: 3) {
            Text(title).font(.caption).foregroundStyle(.secondary)
            Text(value).font(.system(size: 22, weight: .semibold).monospacedDigit()).foregroundStyle(color)
            if !detail.isEmpty { Text(detail).font(.caption2).foregroundStyle(.secondary) }
        }
        .padding(12)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(RoundedRectangle(cornerRadius: 10).fill(Color(nsColor: .controlBackgroundColor)))
    }
}

struct KPIRow: View {
    let checks: [Check]
    let records: [StudioRecord]
    let model: String

    func median(_ xs: [Double]) -> Double? {
        let s = xs.sorted()
        return s.isEmpty ? nil : s[s.count / 2]
    }

    var body: some View {
        let p = Pricing.shared
        let g1 = median(checks.map(\.groundOne))
        let judged = checks.filter { $0.judge != nil }
        let jm = median(judged.compactMap(\.judge))
        let g1OnJudged = median(judged.map(\.groundOne))
        let pairs = checks.flatMap(\.pairs)
        let agree = pairs.filter { $0.0 == $0.1 }.count
        let saved = checks.map { p.saved($0, model: model) }.reduce(0, +)
        let tokens = checks.map { $0.judgeTokens ?? Int(p.judgeTokensPerSentence * Double($0.k)) }.reduce(0, +)
        let fixes = records.flatMap { $0.versions.filter { $0.origin == .fixed } }
        let peak = records.compactMap { $0.memory?.mlxPeakGB }.max()
        VStack(spacing: 10) {
            HStack(spacing: 10) {
                KPITile(title: "Questions", value: "\(records.count)", detail: "\(checks.count) verifications")
                KPITile(title: "Sentences checked", value: "\(checks.map(\.k).reduce(0, +))",
                        detail: checks.isEmpty ? "" : String(format: "%.1f per answer", Double(checks.map(\.k).reduce(0, +)) / Double(checks.count)))
                KPITile(title: "GroundOne, median", value: g1.map(\.s) ?? "–", detail: "one forward pass, 0 tokens generated", color: Palette.groundOne)
                KPITile(title: "LLM judge, median", value: jm.map(\.s) ?? "–",
                        detail: (jm != nil && g1OnJudged != nil) ? String(format: "%.1f× GroundOne on the same answers", jm! / g1OnJudged!) : "run “GroundOne + LLM judge” to compare",
                        color: Palette.judge)
            }
            HStack(spacing: 10) {
                KPITile(title: "Saved vs \(model)", value: String(format: "$%.4f", saved),
                        detail: checks.isEmpty ? "" : String(format: "$%.2f per 1,000 answers", saved / Double(checks.count) * 1000))
                KPITile(title: "LLM judge tokens not generated", value: "\(tokens)", detail: "what an LLM judge would have written")
                KPITile(title: "GroundOne–LLM judge agreement", value: pairs.isEmpty ? "–" : String(format: "%.0f%%", Double(agree) / Double(pairs.count) * 100),
                        detail: pairs.isEmpty ? "" : "\(agree) of \(pairs.count) sentences")
                KPITile(title: "Rewrites", value: "\(fixes.map(\.rewritten.count).reduce(0, +))",
                        detail: "\(fixes.count) fix\(fixes.count == 1 ? "" : "es")\(peak.map { String(format: " · MLX peak %.1f GB", $0) } ?? "")")
            }
        }
        .accessibilityElement(children: .contain)
        .accessibilityIdentifier("stats-kpis")
    }
}

/// Scatter of seconds against checked sentences, one point per answer and system; hover shows the nearest point.
struct TimeVsSentences: View {
    let checks: [Check]
    @State private var hover: (String, Int, Double)?

    struct Point: Identifiable {
        let id = UUID()
        let system: String
        let k: Int
        let seconds: Double
    }

    var points: [Point] {
        checks.map { Point(system: "GroundOne", k: $0.k, seconds: $0.groundOne) }
            + checks.compactMap { c in c.judge.map { Point(system: "LLM judge", k: c.k, seconds: $0) } }
    }

    var body: some View {
        Chart(points) { p in
            PointMark(x: .value("Sentences", p.k), y: .value("Seconds", p.seconds))
                .foregroundStyle(by: .value("System", p.system))
                .symbol(by: .value("System", p.system))
                .symbolSize(70)
        }
        .chartForegroundStyleScale(["GroundOne": Palette.groundOne, "LLM judge": Palette.judge])
        .chartXAxisLabel("checked sentences in the answer")
        .chartYAxisLabel("seconds")
        .chartLegend(position: .top, alignment: .leading)
        .chartOverlay { proxy in
            GeometryReader { geo in
                Rectangle().fill(.clear).contentShape(Rectangle())
                    .onContinuousHover { phase in
                        guard case .active(let loc) = phase, let plot = proxy.plotFrame else { hover = nil; return }
                        let origin = geo[plot].origin
                        let best = points.min { a, b in
                            dist(proxy, a, loc, origin) < dist(proxy, b, loc, origin)
                        }
                        hover = best.flatMap { dist(proxy, $0, loc, origin) < 30 ? ($0.system, $0.k, $0.seconds) : nil }
                    }
            }
        }
        .overlay(alignment: .topTrailing) {
            if let h = hover {
                Text("\(h.0): \(h.1) sentences, \(h.2.s)").font(.caption).padding(6)
                    .background(RoundedRectangle(cornerRadius: 6).fill(.regularMaterial))
            }
        }
    }

    func dist(_ proxy: ChartProxy, _ p: Point, _ loc: CGPoint, _ origin: CGPoint) -> CGFloat {
        guard let x = proxy.position(forX: p.k), let y = proxy.position(forY: p.seconds) else { return .infinity }
        return hypot(x + origin.x - loc.x, y + origin.y - loc.y)
    }
}

struct SavedOverTime: View {
    let checks: [Check]
    let model: String
    @State private var selected: Int?

    var body: some View {
        let p = Pricing.shared
        let sorted = checks.sorted { $0.date < $1.date }
        let cumulative = sorted.indices.map { i in sorted[...i].map { p.saved($0, model: model) }.reduce(0, +) }
        Chart {
            ForEach(Array(cumulative.enumerated()), id: \.offset) { i, v in
                LineMark(x: .value("Verification", i + 1), y: .value("USD", v)).foregroundStyle(Palette.groundOne)
                    .lineStyle(StrokeStyle(lineWidth: 2))
                PointMark(x: .value("Verification", i + 1), y: .value("USD", v)).foregroundStyle(Palette.groundOne).symbolSize(20)
            }
            if let s = selected, cumulative.indices.contains(s - 1) {
                RuleMark(x: .value("Verification", s)).foregroundStyle(.secondary.opacity(0.4))
                    .annotation(position: .top, alignment: .leading) {
                        Text(String(format: "after %d: $%.4f", s, cumulative[s - 1])).font(.caption)
                            .padding(4).background(RoundedRectangle(cornerRadius: 4).fill(.regularMaterial))
                    }
            }
        }
        .chartXSelection(value: $selected)
        .chartXAxisLabel("verifications, in order")
        .chartYAxisLabel("USD saved")
    }
}

struct VerdictBars: View {
    let checks: [Check]
    var body: some View {
        let all = checks.flatMap(\.labels)
        Chart(Verdict.allCases, id: \.self) { l in
            let n = all.filter { $0 == l }.count
            BarMark(x: .value("Sentences", n), y: .value("Verdict", l.display))
                .foregroundStyle(Palette.color(l))
                .cornerRadius(4)
                .annotation(position: .trailing) {
                    Text("\(n) (\(all.isEmpty ? 0 : n * 100 / all.count)%)").font(.caption).foregroundStyle(.secondary)
                }
        }
        .chartXAxisLabel("sentences")
    }
}

struct AgreementMatrix: View {
    let checks: [Check]
    var body: some View {
        let pairs = checks.flatMap(\.pairs)
        let cols: [String] = Verdict.allCases.map(\.display) + ["unparsed"]
        let maxCount = max(1, Verdict.allCases.flatMap { a in cols.map { b in pairs.filter { $0.0 == a && ($0.1?.display ?? "unparsed") == b }.count } }.max() ?? 1)
        if pairs.isEmpty {
            Text("Verify with “GroundOne + LLM judge” to compare the two on the same sentences.").foregroundStyle(.secondary)
                .frame(maxWidth: .infinity, maxHeight: .infinity)
        } else {
            Chart {
                ForEach(Verdict.allCases, id: \.self) { a in
                    ForEach(cols, id: \.self) { b in
                        let n = pairs.filter { $0.0 == a && ($0.1?.display ?? "unparsed") == b }.count
                        RectangleMark(x: .value("LLM judge", b), y: .value("GroundOne", a.display))
                            .foregroundStyle(Palette.groundOne.opacity(n == 0 ? 0.04 : 0.15 + 0.75 * Double(n) / Double(maxCount)))
                            .annotation(position: .overlay) {
                                Text("\(n)").font(.caption.monospacedDigit())
                                    .foregroundStyle(Double(n) / Double(maxCount) > 0.55 ? Color.white : Color.primary)
                            }
                    }
                }
            }
            .chartXAxisLabel("LLM judge")
            .chartYAxisLabel("GroundOne")
        }
    }
}

/// The offline case study (command line, injected errors), for reference next to the live numbers.
struct OfflineBenchmark: View {
    @State private var s: [String: Any]?

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Offline benchmark: 100 injected errors (T1 answers, GroundOne 3B)").font(.headline)
            if let s, let d = s["detection"] as? [String: Any], let e = s["error_survival"] as? [String: Any],
               let r = s["repairs"] as? [String: Any], let t = s["timing_seconds"] as? [String: Any] {
                HStack(spacing: 10) {
                    KPITile(title: "Errors flagged by GroundOne", value: pct(d["groundone_flags_injected_sentence"]))
                    KPITile(title: "Flagged by the LLM judge", value: pct(d["judge_flags_injected_sentence"]))
                    KPITile(title: "Errors left after Fix", value: pct(e["after_round_2_final"]))
                    KPITile(title: "Values restored from the source", value: "\(r["removed_errors_restored"] ?? "–")")
                    KPITile(title: "GroundOne vs LLM judge, median", value: "\(num(t["groundone_pass_median"])) s vs \(num(t["judge_median"])) s")
                }
                Text("Run with `g1studio casestudy`; the injected errors are the ground truth, independent of GroundOne. The answers were chosen among those GroundOne accepts, so detection is high by construction.")
                    .font(.caption).foregroundStyle(.secondary)
            } else {
                Text("Not available (install the case-study summary with `g1studio install`).").font(.caption).foregroundStyle(.secondary)
            }
        }
        .padding(14)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color(nsColor: .controlBackgroundColor)))
        .task {
            let url = Workspace.demo.appendingPathComponent("casestudy/summary_full.json")
            if let data = try? Data(contentsOf: url), let all = try? JSONSerialization.jsonObject(with: data) as? [String: Any] {
                s = all["casestudy-g1-3b-b1-set2"] as? [String: Any]
            }
        }
    }

    func pct(_ v: Any?) -> String { (v as? Double).map { String(format: "%.0f%%", $0 * 100) } ?? "–" }
    func num(_ v: Any?) -> String { (v as? Double).map { String(format: "%.2f", $0) } ?? "–" }
}
