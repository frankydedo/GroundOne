import GroundOneCore
import PDFKit
import SwiftUI

struct AuditView: View {
    @Environment(AppModel.self) private var model
    @State private var records: [QueryRecord] = []
    @State private var selected: QueryRecord.ID?

    var body: some View {
        HSplitView {
            List(records.reversed(), selection: $selected) { r in
                VStack(alignment: .leading, spacing: 2) {
                    Text(r.question).lineLimit(1)
                    Text("\(r.date.formatted(date: .abbreviated, time: .shortened)) · \(r.policy.name) · \(r.status.rawValue) · \(r.rounds) rewrite\(r.rounds == 1 ? "" : "s")")
                        .font(.caption).foregroundStyle(.secondary)
                }
                .tag(r.id)
            }
            .frame(minWidth: 280, maxWidth: 380)
            .accessibilityIdentifier("audit-list")
            ScrollView {
                if let r = records.first(where: { $0.id == selected }) {
                    VStack(alignment: .leading, spacing: 10) {
                        Text(r.question).font(.title3.bold())
                        Text("Verifier \(r.verifier) · generator \(r.generator) · policy \(r.policy.name) (τ \(r.policy.tau(calibrated: r.drafts.first?.verdicts.threshold ?? 0).p2))")
                            .font(.caption).foregroundStyle(.secondary)
                        ForEach(r.drafts, id: \.round) { d in
                            VStack(alignment: .leading, spacing: 4) {
                                Text(d.round == 0 ? "First draft" : "Rewrite \(d.round) (sentences \(d.rewriteRequest.map { String($0 + 1) }.joined(separator: ", ")))")
                                    .font(.headline)
                                ForEach(d.verdicts.sentences, id: \.index) { s in
                                    Label("[\(s.index + 1)] \(s.text)", systemImage: Palette.symbol(s.label))
                                        .foregroundStyle(Palette.color(s.label)).font(.callout)
                                }
                                if let raw = d.rewriteRaw {
                                    Text("Generator output: \(raw)").font(.caption.monospaced()).foregroundStyle(.secondary)
                                }
                            }
                            .padding(.vertical, 4)
                        }
                        Text("Final status: \(r.status.rawValue)").font(.headline)
                        Text(r.displayed).textSelection(.enabled)
                    }
                    .padding(18)
                    .frame(maxWidth: .infinity, alignment: .leading)
                } else {
                    Text("Every question, draft, verdict and policy decision is appended to \(model.audit.url.path).")
                        .font(.callout).foregroundStyle(.secondary).padding()
                }
            }
        }
        .navigationTitle("Audit log")
        .task(id: model.sessionRecords.count) {
            records = (try? AuditLog.read(model.audit.url)) ?? []
        }
    }
}

/// Opens the source of a link: the PDF at the page, with the suggested span highlighted (§4c).
struct SourceViewer: View {
    let link: SourceLink
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Label(link.kind == .supported ? "Supported by" : "Contradicted by", systemImage: Palette.symbol(link.kind))
                    .foregroundStyle(Palette.color(link.kind)).font(.headline)
                Text("\(link.passage.title)\(link.passage.page.map { ", page \($0 + 1)" } ?? "")").font(.headline)
                Spacer()
                Text("GroundOne P = \(link.probability.p2)").font(.caption.monospacedDigit()).foregroundStyle(.secondary)
                Button("Done") { dismiss() }.keyboardShortcut(.defaultAction)
            }
            Text("“\(link.spanText)”").font(.callout).italic().padding(8)
                .background(RoundedRectangle(cornerRadius: 8).fill(Palette.color(link.kind).opacity(0.12)))
            if let url = link.passage.fileURL, url.pathExtension.lowercased() == "pdf", FileManager.default.fileExists(atPath: url.path) {
                PDFKitView(url: url, page: link.passage.page ?? 0, span: link.spanText, color: NSColor(Palette.color(link.kind)))
            } else {
                ScrollView { Text(link.passage.text).textSelection(.enabled).padding() }
            }
            Text("Evidence suggested by GroundOne: the passage where the sentence is most supported (or contradicted), and its closest sentence. Not evaluated.")
                .font(.caption2).foregroundStyle(.tertiary)
        }
        .padding(16)
        .frame(width: 820, height: 760)
    }
}

struct PDFKitView: NSViewRepresentable {
    let url: URL
    let page: Int
    let span: String
    let color: NSColor

    func makeNSView(context: Context) -> PDFView {
        let v = PDFView()
        v.autoScales = true
        guard let doc = PDFDocument(url: url) else { return v }
        v.document = doc
        let target = doc.page(at: min(page, doc.pageCount - 1))
        // The passage text is whitespace-normalised; match its words in the page text allowing any whitespace or
        // end-of-line hyphenation between them.
        let words = span.split(whereSeparator: { $0.isWhitespace }).map { NSRegularExpression.escapedPattern(for: String($0)) }
        var selection: PDFSelection?
        if let target, let text = target.string, words.count >= 2 {
            let ns = text as NSString
            func find(_ w: ArraySlice<String>, from: Int) -> NSRange? {
                let pattern = w.joined(separator: #"[\s\-]*\s*"#)
                guard let re = try? NSRegularExpression(pattern: pattern, options: [.caseInsensitive]) else { return nil }
                return re.firstMatch(in: text, range: NSRange(location: from, length: ns.length - from))?.range
            }
            // Start and end of the sentence matched separately: line-end hyphenation can break the middle.
            let k = min(5, words.count)
            if let a = find(words.prefix(k), from: 0) {
                let b = find(words.suffix(k), from: a.location) ?? a
                selection = target.selection(for: NSRange(location: a.location, length: max(a.upperBound, b.upperBound) - a.location))
            }
        }
        if let sel = selection {
            sel.color = color.withAlphaComponent(0.35)
            v.highlightedSelections = [sel]
            v.go(to: sel)
        } else if let target {
            v.go(to: target)
        }
        return v
    }

    func updateNSView(_ nsView: PDFView, context: Context) {}
}
