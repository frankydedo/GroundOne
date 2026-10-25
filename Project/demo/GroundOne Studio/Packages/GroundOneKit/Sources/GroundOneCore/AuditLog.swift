import Foundation

/// Append-only JSONL audit log: question, passages, every draft with its verdicts, policy and timings (§4 step 8).
public actor AuditLog {
    public nonisolated let url: URL
    let encoder: JSONEncoder

    public init(url: URL) {
        self.url = url
        encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        encoder.outputFormatting = [.sortedKeys, .withoutEscapingSlashes]
    }

    public func append<T: Encodable>(_ record: T) throws {
        try FileManager.default.createDirectory(at: url.deletingLastPathComponent(), withIntermediateDirectories: true)
        var data = try encoder.encode(record)
        data.append(0x0A)
        if let h = try? FileHandle(forWritingTo: url) {
            defer { try? h.close() }
            try h.seekToEnd()
            try h.write(contentsOf: data)
        } else {
            try data.write(to: url)
        }
    }

    public static func read(_ url: URL) throws -> [QueryRecord] {
        let d = JSONDecoder()
        d.dateDecodingStrategy = .iso8601
        return try String(contentsOf: url, encoding: .utf8).split(separator: "\n").map {
            try d.decode(QueryRecord.self, from: Data($0.utf8))
        }
    }
}
