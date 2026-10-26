import Foundation
import GroundOneCore
import GroundOneEngines

/// Retrieval on the demo library: for each of the 150 real MS MARCO questions of T1, how many of its own passages
/// (typically three) the retriever returns among the top k, for BM25, dense and hybrid retrieval.
enum RetrievalT1 {
    struct Q: Decodable { let source_id: String; let question: String; let passages: Int }

    static func run(_ args: [String]) async throws {
        let qs = try JSONDecoder().decode([Q].self, from: Data(contentsOf: Workspace.demo.appendingPathComponent("corpus/questions.json")))
        let embedder = try await Embedder.load()
        let index = try LibraryIndex(url: Commands.indexURL(ModelCatalog.corpus, embedder: ModelCatalog.embedder))
        var report: [String: Any] = ["questions": qs.count, "k": 6,
                                     "protocol": "T1 library (147 news articles + 450 MS MARCO passages); query = the MS MARCO question; relevant = its own passages; per-document cap 3"]
        for mode in HybridRetriever.Mode.allCases {
            let r = HybridRetriever(index: index, embedder: embedder, mode: mode)
            var recall = 0.0, hit = 0, all = 0, secs = 0.0
            for q in qs {
                let t = Date()
                let top = try await r.search(q.question, k: 6)
                secs += Date().timeIntervalSince(t)
                let found = Set(top.filter { $0.docID.hasPrefix("msmarco-\(q.source_id)-") }.map(\.docID)).count
                recall += Double(found) / Double(max(q.passages, 1))
                if found > 0 { hit += 1 }
                if found == q.passages { all += 1 }
            }
            let n = Double(qs.count)
            report[mode.rawValue] = ["recall@6": recall / n, "hit@6": Double(hit) / n, "all_passages@6": Double(all) / n, "mean_seconds": secs / n]
            print(String(format: "%-7@ recall@6 %.3f  hit@6 %.3f  all@6 %.3f  %.3f s", mode.rawValue as NSString, recall / n, Double(hit) / n, Double(all) / n, secs / n))
        }
        try JSONSerialization.data(withJSONObject: report, options: [.prettyPrinted, .sortedKeys])
            .write(to: Workspace.demo.appendingPathComponent("results/retrieval_t1.json"))
    }
}
