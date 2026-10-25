import AppKit
import GroundOneCore
import PDFKit
import SwiftUI

/// Every question and every action on it, from the audit log (one JSON line per action).
struct AuditView: View {
    @Environment(AppModel.self) private var model
    @State private var selected: StudioRecord.ID?

    var body: some View {
        HSplitView {
            List(model.history.reversed(), selection: $selected) { r in
                VStack(alignment: .leading, spacing: 2) {
                    Text(r.question).lineLimit(1)
                    Text("\(r.date.formatted(date: .abbreviated, time: .shortened)) · \(r.versions.count) version\(r.versions.count == 1 ? "" : "s") · last: \(r.event)")
                        .font(.caption).foregroundStyle(.secondary)
                }
                .tag(r.id)
            }
            .frame(minWidth: 280, maxWidth: 380)
            .accessibilityIdentifier("audit-list")
            ScrollView {
                if let r = model.history.first(where: { $0.id == selected }) {
                    VStack(alignment: .leading, spacing: 10) {
                        Text(r.question).font(.title3.bold())
                        Text("Verifier \(r.verifier) · generator \(r.generator) · policy \(r.policy) · \(r.passages.count) passages")
                            .font(.caption).foregroundStyle(.secondary)
                        ForEach(Array(r.versions.enumerated()), id: \.offset) { i, v in
                            VStack(alignment: .leading, spacing: 4) {
                                Text(i == 0 ? "Generated (\(v.generation.seconds.s))" : "Fix \(i): sentences \(v.rewritten.map { String($0 + 1) }.joined(separator: ", "))")
                                    .font(.headline)
                                ForEach(v.sentences, id: \.index) { s in
                                    Label("[\(s.index + 1)] \(s.text)", systemImage: Palette.symbol(v.verdicts == nil ? nil : s.label))
                                        .foregroundStyle(v.verdicts == nil ? Color.primary : Palette.color(s.label)).font(.callout)
                                }
                                if let log = v.rewriteLog {
                                    Text("Generator output: \(log)").font(.caption.monospaced()).foregroundStyle(.secondary)
                                }
                            }
                            .padding(.vertical, 4)
                        }
                    }
                    .padding(18)
                    .frame(maxWidth: .infinity, alignment: .leading)
                } else {
                    Text("Every question, version, verdict and rewrite is appended to \(model.audit.url.path).")
                        .font(.callout).foregroundStyle(.secondary).padding()
                }
            }
        }
        .navigationTitle("Audit log")
    }
}

/// A document of the library, with an optional highlighted span (the evidence for a sentence), scrolled into view.
struct DocumentPreview: View {
    let request: DocumentPreviewRequest
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack(alignment: .firstTextBaseline) {
                if let k = request.kind {
                    Label(k == .supported ? "Supported by" : k == .contradicted ? "Contradicted by" : "Closest passage",
                          systemImage: Palette.symbol(k)).foregroundStyle(Palette.color(k)).font(.headline)
                }
                Text(request.title).font(.headline).lineLimit(2)
                Spacer()
                Button("Done") { dismiss() }.keyboardShortcut(.defaultAction)
            }
            Text(request.note).font(.caption).foregroundStyle(.secondary)
            if let s = request.sentence {
                Text("Sentence: “\(s)”").font(.callout).italic()
                    .padding(8).frame(maxWidth: .infinity, alignment: .leading)
                    .background(RoundedRectangle(cornerRadius: 8).fill(Color.secondary.opacity(0.08)))
            }
            DocumentText(text: DocumentText.load(request), highlight: request.highlight,
                         color: NSColor(request.kind.map { Palette.color($0) } ?? Color.accentColor))
                .accessibilityIdentifier("document-preview")
        }
        .padding(16)
        .frame(width: 760, height: 640)
    }
}

/// Read-only text view; the highlight is found allowing any whitespace between its words, then scrolled to.
struct DocumentText: NSViewRepresentable {
    let text: String
    let highlight: String?
    var color: NSColor = .controlAccentColor

    static func load(_ r: DocumentPreviewRequest) -> String {
        if let p = r.path, p.hasSuffix(".txt") || p.hasSuffix(".md"), let t = try? String(contentsOfFile: p, encoding: .utf8) { return t }
        if let p = r.path, p.hasSuffix(".pdf"), let d = PDFDocument(url: URL(fileURLWithPath: p)) { return d.string ?? "" }
        return r.fallbackText ?? ""
    }

    func makeNSView(context: Context) -> NSScrollView {
        let scroll = NSTextView.scrollableTextView()
        if let tv = scroll.documentView as? NSTextView {
            tv.isEditable = false
            tv.isSelectable = true
            tv.textContainerInset = NSSize(width: 10, height: 12)
            tv.drawsBackground = true
            tv.backgroundColor = .textBackgroundColor
        }
        return scroll
    }

    func updateNSView(_ scroll: NSScrollView, context: Context) {
        guard let tv = scroll.documentView as? NSTextView else { return }
        let para = NSMutableParagraphStyle()
        para.lineSpacing = 4
        let attr = NSMutableAttributedString(string: text, attributes: [
            .font: NSFont.systemFont(ofSize: 14), .foregroundColor: NSColor.textColor, .paragraphStyle: para])
        var range: NSRange?
        if let h = highlight { range = Self.find(h, in: text) }
        if let r = range { attr.addAttribute(.backgroundColor, value: color.withAlphaComponent(0.35), range: r) }
        tv.textStorage?.setAttributedString(attr)
        if let r = range {
            DispatchQueue.main.async { tv.scrollRangeToVisible(r); tv.showFindIndicator(for: r) }
        }
    }

    static func find(_ span: String, in text: String) -> NSRange? {
        let words = span.split(whereSeparator: { $0.isWhitespace }).map { NSRegularExpression.escapedPattern(for: String($0)) }
        guard words.count >= 2 else { return nil }
        let ns = text as NSString
        func search(_ w: ArraySlice<String>, from: Int) -> NSRange? {
            guard let re = try? NSRegularExpression(pattern: w.joined(separator: #"[\s\-]*\s*"#), options: [.caseInsensitive]) else { return nil }
            return re.firstMatch(in: text, range: NSRange(location: from, length: ns.length - from))?.range
        }
        let k = min(6, words.count)
        guard let a = search(words.prefix(k), from: 0) else { return nil }
        let b = search(words.suffix(k), from: a.location) ?? a
        return NSRange(location: a.location, length: max(a.upperBound, b.upperBound) - a.location)
    }
}
