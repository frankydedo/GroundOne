import GroundOneCore
import GroundOneEngines
import SwiftUI

/// The documents GroundOne can read: news articles and MS MARCO passages from the RAGTruth test set. A click shows the
/// document on the right.
struct LibraryView: View {
    @Environment(AppModel.self) private var model
    @State private var filter = ""
    @State private var selected: LibraryIndex.Doc.ID?
    @State private var kind = 0

    var shown: [LibraryIndex.Doc] {
        model.documents.filter { d in
            (kind == 0 || (kind == 1) == d.id.hasPrefix("news")) &&
                (filter.isEmpty || d.title.localizedCaseInsensitiveContains(filter))
        }.sorted { $0.title < $1.title }
    }

    var body: some View {
        HSplitView {
            VStack(alignment: .leading, spacing: 0) {
                VStack(alignment: .leading, spacing: 6) {
                    Text("Library").font(.title2.bold())
                    let news = model.documents.filter { $0.id.hasPrefix("news") }.count
                    Text("\(news) news articles · \(model.documents.count - news) MS MARCO passages · \(model.documents.map(\.passages).reduce(0, +)) indexed passages")
                        .font(.caption).foregroundStyle(.secondary)
                        .accessibilityIdentifier("library-summary")
                    Picker("", selection: $kind) {
                        Text("All").tag(0); Text("News").tag(1); Text("MS MARCO").tag(2)
                    }
                    .pickerStyle(.segmented).labelsHidden()
                }
                .padding(12)
                List(shown, selection: $selected) { d in
                    VStack(alignment: .leading, spacing: 2) {
                        Text(d.title).lineLimit(2)
                        Text(d.id.hasPrefix("news") ? "News article · \(d.passages) passages" : "MS MARCO passage")
                            .font(.caption).foregroundStyle(.secondary)
                    }
                    .tag(d.id)
                }
                .accessibilityIdentifier("library-list")
            }
            .frame(minWidth: 300, idealWidth: 360, maxWidth: 460)
            Group {
                if let d = model.documents.first(where: { $0.id == selected }) {
                    VStack(alignment: .leading, spacing: 8) {
                        Text(d.title).font(.headline)
                        Text(d.id.hasPrefix("news") ? "News article (CNN/Daily Mail), RAGTruth test set" : "MS MARCO web passage, RAGTruth test set")
                            .font(.caption).foregroundStyle(.secondary)
                        DocumentText(text: DocumentText.load(DocumentPreviewRequest(title: d.title, path: d.path, highlight: nil, kind: nil,
                                                                                     note: "", sentence: nil,
                                                                                     fallbackText: model.fake ? Fakes.passages.map(\.text).joined(separator: "\n\n") : nil)),
                                     highlight: nil)
                            .accessibilityIdentifier("library-preview")
                    }
                    .padding(14)
                } else {
                    Text("Select a document to read it.").foregroundStyle(.secondary).frame(maxWidth: .infinity, maxHeight: .infinity)
                }
            }
            .frame(minWidth: 420, maxWidth: .infinity, maxHeight: .infinity)
        }
        .searchable(text: $filter, prompt: "Filter documents")
        .navigationTitle("Library")
    }
}
