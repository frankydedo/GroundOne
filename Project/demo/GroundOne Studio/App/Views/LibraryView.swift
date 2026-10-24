import GroundOneCore
import GroundOneEngines
import SwiftUI
import UniformTypeIdentifiers

struct LibraryView: View {
    @Environment(AppModel.self) private var model
    @State private var importing = false
    @State private var filter = ""

    var shown: [LibraryIndex.Doc] {
        filter.isEmpty ? model.documents : model.documents.filter { $0.title.localizedCaseInsensitiveContains(filter) }
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            HStack {
                VStack(alignment: .leading) {
                    Text("Library").font(.title2.bold())
                    Text("\(model.documents.count) documents · \(model.documents.map(\.passages).reduce(0, +)) passages · indexed with SQLite FTS5 and \(ModelCatalog.embedder.split(separator: "/").last ?? "")")
                        .font(.caption).foregroundStyle(.secondary)
                        .accessibilityIdentifier("library-summary")
                }
                Spacer()
                if let f = model.ingesting {
                    ProgressView().controlSize(.small)
                    Text("Indexing \(f)…").font(.caption).foregroundStyle(.secondary)
                }
                Button { importing = true } label: { Label("Add files…", systemImage: "plus") }
                    .disabled(model.phase != .ready || model.fake)
            }
            .padding(16)
            Divider()
            Table(shown) {
                TableColumn("Title") { d in
                    Label(d.title, systemImage: d.path.hasSuffix(".pdf") ? "doc.richtext" : "doc.plaintext")
                }
                TableColumn("Passages") { d in Text("\(d.passages)").monospacedDigit() }.width(80)
                TableColumn("") { d in
                    Button(role: .destructive) { model.remove(d) } label: { Image(systemName: "trash") }.buttonStyle(.borderless)
                }
                .width(30)
            }
            .searchable(text: $filter, prompt: "Filter documents")
        }
        .navigationTitle("Library")
        .fileImporter(isPresented: $importing, allowedContentTypes: [.pdf, .plainText, UTType(filenameExtension: "md") ?? .plainText],
                      allowsMultipleSelection: true) { result in
            if case .success(let urls) = result { model.addFiles(urls) }
        }
    }
}
