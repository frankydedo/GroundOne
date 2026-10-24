import Foundation

/// A policy file (demo_architecture.md §7). Recorded in every audit entry.
public struct Policy: Codable, Sendable, Hashable, Identifiable {
    public enum Threshold: Codable, Sendable, Hashable {
        case calibrated
        case value(Double)

        public init(from decoder: Decoder) throws {
            let c = try decoder.singleValueContainer()
            if let v = try? c.decode(Double.self) { self = .value(v) } else { self = .calibrated }
        }

        public func encode(to encoder: Encoder) throws {
            var c = encoder.singleValueContainer()
            switch self {
            case .calibrated: try c.encode("calibrated")
            case .value(let v): try c.encode(v)
            }
        }
    }

    public enum OnFailure: String, Codable, Sendable, CaseIterable {
        case highlight, hide, abstain
    }

    public var name: String
    public var verifier: String
    public var threshold: Threshold
    public var blocking: [Label]
    public var maxAttempts: Int
    public var onFailure: OnFailure
    public var showProbabilities: Bool
    public var auditLog: Bool

    public var id: String { name }

    enum CodingKeys: String, CodingKey {
        case name, verifier, threshold, blocking
        case maxAttempts = "max_attempts"
        case onFailure = "on_failure"
        case showProbabilities = "show_probabilities"
        case auditLog = "audit_log"
    }

    public init(name: String, verifier: String = "g1-3b-b1", threshold: Threshold = .calibrated,
                blocking: [Label] = [.contradicted, .notMentioned], maxAttempts: Int = 2,
                onFailure: OnFailure = .highlight, showProbabilities: Bool = true, auditLog: Bool = true) {
        self.name = name; self.verifier = verifier; self.threshold = threshold; self.blocking = blocking
        self.maxAttempts = maxAttempts; self.onFailure = onFailure; self.showProbabilities = showProbabilities
        self.auditLog = auditLog
    }

    /// Strict and lenient are the two policies derived from the three probabilities in the thesis (D20).
    public static let strict = Policy(name: "strict", blocking: [.contradicted, .notMentioned], onFailure: .abstain)
    public static let lenient = Policy(name: "lenient", blocking: [.contradicted], onFailure: .highlight)
    public static let observe = Policy(name: "observe (no revision)", blocking: [.contradicted, .notMentioned],
                                       maxAttempts: 0, onFailure: .highlight)
    public static let builtIn: [Policy] = [.strict, .lenient, .observe]

    public func tau(calibrated: Double) -> Double {
        switch threshold {
        case .calibrated: calibrated
        case .value(let v): v
        }
    }

    public func isBlocking(_ label: Label?) -> Bool {
        guard let label else { return false }
        return blocking.contains(label)
    }
}
