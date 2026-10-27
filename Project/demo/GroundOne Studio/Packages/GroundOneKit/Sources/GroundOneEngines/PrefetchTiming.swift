import Foundation
import GroundOneCore

/// What reading the sources ahead of the verification saves (`GroundOneModel.prefetch`), on the conformance fixture
/// answers (the 200 T1 latency answers): for each answer, from an empty cache, (1) the first verification as today,
/// (2) the prefetch alone, as the app runs it while the user reads the answer, then the verification, and (3) a
/// verification asked immediately after the prefetch has started (the user does not wait), which must cost no more
/// than (1). Writes outputs/demo/results/prefetch-<run>.json.
public enum PrefetchTiming {
    struct Row: Codable {
        let id: String
        let k: Int
        let headTokens: Int
        let promptTokens: Int
        let coldSeconds: Double
        let prefetchSeconds: Double
        let warmSeconds: Double
        let immediateSeconds: Double
        let warmCachedTokens: Int
        let maxAbsProbDelta: Double
    }

    struct Report: Codable {
        let run: String
        let answers: Int
        let medianColdSeconds: Double
        let medianPrefetchSeconds: Double
        let medianWarmSeconds: Double
        let medianImmediateSeconds: Double
        let coldOverWarm: Double
        let headHits: Int
        let maxAbsProbDelta: Double
        let byKBand: [String: [String: Double]]
        let rows: [Row]
    }

    static func median(_ x: [Double]) -> Double {
        guard !x.isEmpty else { return .nan }
        let s = x.sorted()
        return s.count % 2 == 1 ? s[s.count / 2] : (s[s.count / 2 - 1] + s[s.count / 2]) / 2
    }

    static func band(_ k: Int) -> String { k <= 4 ? "1-4" : k <= 8 ? "5-8" : k <= 13 ? "9-13" : ">=14" }

    public static func run(run: String, limit: Int? = nil) async throws -> String {
        let url = Workspace.demo.appendingPathComponent("fixtures/conformance-\(run).json")
        let fx = try JSONDecoder().decode(Conformance.Fixture.self, from: Data(contentsOf: url))
        let model = try await GroundOneModel.load(run: run)
        let cal = model.info.calibration
        let items = Array(fx.items.prefix(limit ?? fx.items.count))
        func timed<T>(_ f: () async throws -> T) async rethrows -> (T, Double) {
            let t = Date(); let v = try await f(); return (v, Date().timeIntervalSince(t))
        }
        if let w = items.first {   // warm-up: kernels compiled, weights resident
            _ = try await model.scorePositions(ids: w.ids, positions: w.positions)
        }
        var rows: [Row] = []
        for (n, item) in items.enumerated() {
            let headIds = model.encoder.encode(MarkedPrompt.head(document: item.doc))
            let head = headIds.count
            model.clearPrefixCache()
            let (cold, coldS) = try await timed { try await model.scorePositions(ids: item.ids, positions: item.positions, prefixLength: head) }
            model.clearPrefixCache()
            let (_, prefetchS) = await timed { model.prefetch(headIds: headIds); await model.awaitPrefetch() }
            let (warm, warmS) = try await timed { try await model.scorePositions(ids: item.ids, positions: item.positions, prefixLength: head) }
            model.clearPrefixCache()
            let (_, immS) = try await timed {
                model.prefetch(headIds: headIds)
                return try await model.scorePositions(ids: item.ids, positions: item.positions, prefixLength: head)
            }
            let dp = zip(cold.logits, warm.logits).map { a, b in zip(cal.probs(a), cal.probs(b)).map { abs($0 - $1) }.max()! }.max() ?? 0
            rows.append(Row(id: item.id, k: item.positions.count, headTokens: head, promptTokens: item.ids.count,
                            coldSeconds: coldS, prefetchSeconds: prefetchS, warmSeconds: warmS, immediateSeconds: immS,
                            warmCachedTokens: warm.cachedTokens, maxAbsProbDelta: dp))
            if (n + 1) % 25 == 0 { print("[\(n + 1)/\(items.count)] cold \(String(format: "%.3f", coldS)) s, warm \(String(format: "%.3f", warmS)) s") }
        }
        var bands: [String: [String: Double]] = [:]
        for b in ["1-4", "5-8", "9-13", ">=14"] {
            let r = rows.filter { band($0.k) == b }
            guard !r.isEmpty else { continue }
            bands[b] = ["answers": Double(r.count), "cold": median(r.map(\.coldSeconds)),
                        "prefetch": median(r.map(\.prefetchSeconds)), "warm": median(r.map(\.warmSeconds)),
                        "immediate": median(r.map(\.immediateSeconds))]
        }
        let report = Report(run: run, answers: rows.count, medianColdSeconds: median(rows.map(\.coldSeconds)),
                            medianPrefetchSeconds: median(rows.map(\.prefetchSeconds)),
                            medianWarmSeconds: median(rows.map(\.warmSeconds)),
                            medianImmediateSeconds: median(rows.map(\.immediateSeconds)),
                            coldOverWarm: median(rows.map(\.coldSeconds)) / median(rows.map(\.warmSeconds)),
                            headHits: rows.filter { $0.warmCachedTokens == $0.headTokens }.count,
                            maxAbsProbDelta: rows.map(\.maxAbsProbDelta).max() ?? 0, byKBand: bands, rows: rows)
        let out = Workspace.demo.appendingPathComponent("results/prefetch-\(run).json")
        let enc = JSONEncoder()
        enc.outputFormatting = [.prettyPrinted, .sortedKeys]
        try enc.encode(report).write(to: out)
        return """
            prefetch \(run): \(rows.count) answers, head found in the cache \(report.headHits)/\(rows.count), max |Δp| \(String(format: "%.4f", report.maxAbsProbDelta))
              medians: first verification cold \(String(format: "%.3f", report.medianColdSeconds)) s; prefetch \(String(format: "%.3f", report.medianPrefetchSeconds)) s, then verification \(String(format: "%.3f", report.medianWarmSeconds)) s (\(String(format: "%.1f", report.coldOverWarm))x); asked at once \(String(format: "%.3f", report.medianImmediateSeconds)) s
              → \(out.path)
            """
    }
}
