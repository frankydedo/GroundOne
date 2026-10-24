import Charts
import GroundOneCore
import GroundOneEngines
import SwiftUI
import UniformTypeIdentifiers

/// Measurement mode (§8): per-query timings of this session, export as JSONL, and the injected-error case study.
struct MeasurementsView: View {
    @Environment(AppModel.self) private var model
    @State private var exporting = false
    @State private var exportDoc: JSONLDocument?

    struct Row: Identifiable {
        let id: UUID
        let question: String
        let k: Int
        let generation: Double
        let verification: Double
        let judge: Double?
        let rounds: Int
        let status: String
        let peak: Double
    }

    var rows: [Row] {
        model.sessionRecords.map { r in
            Row(id: r.id, question: r.question, k: r.drafts.first?.verdicts.scored.count ?? 0,
                generation: r.timings.generation.reduce(0, +), verification: r.timings.verification.reduce(0, +),
                judge: r.timings.judge, rounds: r.rounds, status: r.status.rawValue, peak: r.memory?.mlxPeakGB ?? 0)
        }
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                HStack {
                    VStack(alignment: .leading) {
                        Text("Measurements").font(.title2.bold())
                        Text("This session: \(rows.count) question\(rows.count == 1 ? "" : "s"). Case-study numbers come from the command-line runs, not from this window.")
                            .font(.caption).foregroundStyle(.secondary)
                    }
                    Spacer()
                    Button {
                        exportDoc = JSONLDocument(records: model.sessionRecords)
                        exporting = true
                    } label: { Label("Export JSONL", systemImage: "square.and.arrow.up") }
                        .disabled(rows.isEmpty)
                        .accessibilityIdentifier("export-button")
                }
                if !rows.isEmpty {
                    Chart {
                        ForEach(rows) { r in
                            BarMark(x: .value("Question", String(r.question.prefix(18))), y: .value("s", r.generation))
                                .foregroundStyle(by: .value("Kind", "Generation"))
                            BarMark(x: .value("Question", String(r.question.prefix(18))), y: .value("s", r.verification))
                                .foregroundStyle(by: .value("Kind", "GroundOne"))
                        }
                    }
                    .chartForegroundStyleScale(["Generation": Color(red: 0.55, green: 0.55, blue: 0.62), "GroundOne": Palette.groundOne])
                    .chartYAxisLabel("seconds")
                    .frame(height: 220)
                    Table(rows) {
                        TableColumn("Question") { Text($0.question).lineLimit(1) }
                        TableColumn("K") { Text("\($0.k)").monospacedDigit() }.width(30)
                        TableColumn("Generation") { Text($0.generation.s).monospacedDigit() }.width(80)
                        TableColumn("GroundOne") { Text($0.verification.s).monospacedDigit() }.width(80)
                        TableColumn("Judge") { Text($0.judge?.s ?? "–").monospacedDigit() }.width(70)
                        TableColumn("Rewrites") { Text("\($0.rounds)").monospacedDigit() }.width(60)
                        TableColumn("Status") { Text($0.status) }.width(80)
                        TableColumn("MLX peak") { Text(String(format: "%.2f GB", $0.peak)).monospacedDigit() }.width(70)
                    }
                    .frame(height: CGFloat(rows.count) * 26 + 34)
                    .accessibilityIdentifier("session-table")
                }
                CaseStudySummary()
            }
            .padding(20)
        }
        .navigationTitle("Measurements")
        .fileExporter(isPresented: $exporting, document: exportDoc, contentType: .json, defaultFilename: "groundone-session.jsonl") { _ in }
    }
}

struct JSONLDocument: FileDocument {
    static let readableContentTypes: [UTType] = [.json]
    var data: Data

    init(records: [QueryRecord]) {
        let enc = JSONEncoder()
        enc.dateEncodingStrategy = .iso8601
        data = records.compactMap { try? enc.encode($0) }.reduce(into: Data()) { $0.append($1); $0.append(0x0A) }
    }

    init(configuration: ReadConfiguration) throws { data = configuration.file.regularFileContents ?? Data() }
    func fileWrapper(configuration: WriteConfiguration) throws -> FileWrapper { FileWrapper(regularFileWithContents: data) }
}

/// Summary written by experiments/demo/scripts/casestudy_report.py from the command-line case study.
struct CaseStudySummary: View {
    @State private var summary: [String: Any]?

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Injected-error case study").font(.headline)
            if let s = summary {
                ForEach(s.keys.sorted(), id: \.self) { k in
                    if let v = s[k] as? [String: Any] {
                        Text(k).font(.subheadline.weight(.semibold)).padding(.top, 4)
                        ForEach(v.keys.sorted(), id: \.self) { kk in
                            HStack {
                                Text(kk).font(.caption).foregroundStyle(.secondary)
                                Spacer()
                                Text(format(v[kk])).font(.caption.monospacedDigit())
                            }
                        }
                    }
                }
            } else {
                Text("No case-study summary yet (outputs/demo/casestudy/summary.json).").font(.caption).foregroundStyle(.secondary)
            }
        }
        .padding(14)
        .background(RoundedRectangle(cornerRadius: 12).fill(Color(nsColor: .controlBackgroundColor)))
        .task {
            let url = Workspace.demo.appendingPathComponent("casestudy/summary.json")
            if let d = try? Data(contentsOf: url) { summary = try? JSONSerialization.jsonObject(with: d) as? [String: Any] }
        }
    }

    func format(_ v: Any?) -> String {
        if let d = v as? Double { return d < 1 && d > 0 ? String(format: "%.3f", d) : String(format: "%.2f", d) }
        if let i = v as? Int { return "\(i)" }
        return v.map { "\($0)" } ?? "–"
    }
}
