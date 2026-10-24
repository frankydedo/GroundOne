import Foundation

/// `best/calibration.json` written by `groundone calibrate-b`: temperature, per-class bias and the served threshold τ.
public struct Calibration: Codable, Sendable {
    public var temperature: Double
    public var bias: [Double]
    public var threshold: Double
    public var fingerprint: String

    public init(temperature: Double, bias: [Double], threshold: Double, fingerprint: String = "") {
        self.temperature = temperature; self.bias = bias; self.threshold = threshold; self.fingerprint = fingerprint
    }

    public static func load(_ url: URL) throws -> Calibration {
        struct File: Decodable {
            let fingerprint: String
            let temperatures: [String: Double]
            let biases: [String: [Double]]?
            let thresholds: [String: Double]?
        }
        let f = try JSONDecoder().decode(File.self, from: Data(contentsOf: url))
        guard let t = f.temperatures["three"], let tau = f.thresholds?["three"] else {
            throw CocoaError(.fileReadCorruptFile, userInfo: [NSFilePathErrorKey: url.path])
        }
        return Calibration(temperature: t, bias: f.biases?["three"] ?? [0, 0, 0], threshold: tau,
                           fingerprint: f.fingerprint)
    }

    /// softmax(logits / T + b), as `calibration.affine_probs`.
    public func probs(_ logits: [Double]) -> [Double] {
        Decision.softmax(zip(logits, bias).map { $0 / temperature + $1 })
    }
}

public enum Decision {
    public static func softmax(_ xs: [Double]) -> [Double] {
        let m = xs.max() ?? 0
        let e = xs.map { Foundation.exp($0 - m) }
        let s = e.reduce(0, +)
        return e.map { $0 / s }
    }

    /// The served rule (D27): supported iff P(supported) ≥ τ, else the more probable of contradicted / not mentioned.
    public static func decide(_ p: [Double], threshold tau: Double) -> Label {
        if p[0] >= tau { return .supported }
        return p[1] >= p[2] ? .contradicted : .notMentioned
    }
}
