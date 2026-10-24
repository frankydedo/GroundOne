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
        // The passage text is whitespace-normalised; search the first words, which survive line breaks in the PDF.
        let words = span.split(separator: " ").prefix(6).joined(separator: " ")
        let hits = doc.findString(words, withOptions: [.caseInsensitive]).filter { $0.pages.contains { $0 == target } }
        if let sel = hits.first {
            sel.extendForLineBoundaries()
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
