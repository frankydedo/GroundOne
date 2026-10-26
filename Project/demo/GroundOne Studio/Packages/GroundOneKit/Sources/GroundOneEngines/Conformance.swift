import Foundation
import GroundOneCore

/// The conformance gate (demo_architecture.md §5.3): the Swift port must reproduce the Python fixtures exported by
/// `groundone.tools.export_fixtures` (token ids, marker positions, logits, calibrated probabilities, served labels).
public enum Conformance {
    struct Fixture: Decodable {
        struct Item: Decodable {
            let id: String
            let doc: String
            let sentences: [String]
            let scored: [Bool]
            let ids: [Int]
            let positions: [Int]
            let logits: [[Double]]
            let probs: [[Double]]
            let labels: [Int]
        }
        let adapter: String
        let tokenizer_probe: [String: [Int]]
        let items: [Item]
    }

    public struct Report: Codable, Sendable {
        public var run: String
        public var answers: Int
        public var markers: Int
        public var tokenizerProbeIdentical: Bool
        public var idsIdentical: Int
        public var positionsIdentical: Int
        public var maxAbsLogitDelta: Double
        public var maxAbsProbDelta: Double
        public var probsWithin001: Double
        public var labelsIdentical: Double
        public var labelDisagreementsOutsideTau: Int
        public var meanSecondsPerAnswer: Double
        /// Prefix cache (D32): largest probability difference between the cold pass and the cached passes (document
        /// read and cached, then reused), on the same ids.
        public var cachedMaxAbsProbDelta: Double = 0
        public var loadSeconds: Double
        public var passed: Bool
        public var firstMismatches: [String]

        public var summary: String {
            """
            conformance \(run): \(passed ? "PASS" : "FAIL")
              answers \(answers), markers \(markers), tokenizer probe identical \(tokenizerProbeIdentical)
              token ids identical \(idsIdentical)/\(answers), marker positions identical \(positionsIdentical)/\(answers)
              max |Δlogit| \(String(format: "%.4f", maxAbsLogitDelta)), max |Δp| \(String(format: "%.4f", maxAbsProbDelta)), share |Δp|<0.01 \(String(format: "%.4f", probsWithin001))
              served labels identical \(String(format: "%.4f", labelsIdentical)), disagreements farther than 0.01 from τ \(labelDisagreementsOutsideTau)
              load \(String(format: "%.1f", loadSeconds)) s, mean \(String(format: "%.3f", meanSecondsPerAnswer)) s per answer
            """
        }
    }

    public static func run(run: String, limit: Int? = nil, model given: GroundOneModel? = nil) async throws -> Report {
        let url = Workspace.demo.appendingPathComponent("fixtures/conformance-\(run).json")
        let fx = try JSONDecoder().decode(Fixture.self, from: Data(contentsOf: url))
        let t0 = Date()
        let model: GroundOneModel
        if let given { model = given } else { model = try await GroundOneModel.load(run: run) }
        let load = Date().timeIntervalSince(t0)
        let cal = model.info.calibration
        let probe = fx.tokenizer_probe.allSatisfy { model.encoder.encode($0.key) == $0.value }
        var r = Report(run: run, answers: 0, markers: 0, tokenizerProbeIdentical: probe, idsIdentical: 0,
                       positionsIdentical: 0, maxAbsLogitDelta: 0, maxAbsProbDelta: 0, probsWithin001: 0,
                       labelsIdentical: 0, labelDisagreementsOutsideTau: 0, meanSecondsPerAnswer: 0, loadSeconds: load,
                       passed: false, firstMismatches: [])
        var within = 0, sameLabel = 0, seconds = 0.0
        for item in fx.items.prefix(limit ?? fx.items.count) {
            let (ids, pos) = MarkedPrompt.encode(model.encoder, document: item.doc, sentences: item.sentences, scored: item.scored)
            r.answers += 1
            if ids == item.ids { r.idsIdentical += 1 } else if r.firstMismatches.count < 5 {
                let k = Array(zip(ids, item.ids)).firstIndex { $0.0 != $0.1 } ?? min(ids.count, item.ids.count)
                r.firstMismatches.append("\(item.id): ids differ at \(k) (swift \(ids.count) tokens, python \(item.ids.count))")
            }
            if pos == item.positions { r.positionsIdentical += 1 }
            // Logits are always computed on the Python ids, so a tokenizer difference does not hide a model difference.
            let t = Date()
            let logits = try await model.scorePositions(ids: item.ids, positions: item.positions).logits
            seconds += Date().timeIntervalSince(t)
            let head = model.encoder.encode(MarkedPrompt.head(document: item.doc)).count
            for _ in 0..<2 {   // first call reads and caches the document, the second reuses it
                let c = try await model.scorePositions(ids: item.ids, positions: item.positions, prefixLength: head).logits
                for (a, b) in zip(c, logits) {
                    r.cachedMaxAbsProbDelta = max(r.cachedMaxAbsProbDelta, zip(cal.probs(a), cal.probs(b)).map { abs($0 - $1) }.max()!)
                }
            }
            for (k, (lg, ref)) in zip(logits, item.logits).enumerated() {
                r.markers += 1
                r.maxAbsLogitDelta = max(r.maxAbsLogitDelta, zip(lg, ref).map { abs($0 - $1) }.max()!)
                let p = cal.probs(lg)
                let dp = zip(p, item.probs[k]).map { abs($0 - $1) }.max()!
                r.maxAbsProbDelta = max(r.maxAbsProbDelta, dp)
                if dp < 0.01 { within += 1 }
                let label = Decision.decide(p, threshold: cal.threshold).index
                if label == item.labels[k] { sameLabel += 1 } else if abs(item.probs[k][0] - cal.threshold) > 0.01 {
                    r.labelDisagreementsOutsideTau += 1
                }
            }
        }
        r.probsWithin001 = Double(within) / Double(max(r.markers, 1))
        r.labelsIdentical = Double(sameLabel) / Double(max(r.markers, 1))
        r.meanSecondsPerAnswer = seconds / Double(max(r.answers, 1))
        r.passed = r.idsIdentical == r.answers && r.positionsIdentical == r.answers && r.probsWithin001 == 1
            && r.labelsIdentical >= 0.995 && r.labelDisagreementsOutsideTau == 0 && r.cachedMaxAbsProbDelta < 0.01
        let out = Workspace.demo.appendingPathComponent("results/conformance-\(run).json")
        try FileManager.default.createDirectory(at: out.deletingLastPathComponent(), withIntermediateDirectories: true)
        let enc = JSONEncoder()
        enc.outputFormatting = [.prettyPrinted, .sortedKeys]
        try enc.encode(r).write(to: out)
        return r
    }
}
