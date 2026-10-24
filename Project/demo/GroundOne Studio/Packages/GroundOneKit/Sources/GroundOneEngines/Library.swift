import Foundation
import GroundOneCore
import NaturalLanguage
import PDFKit
import SQLite3

/// Splits source files into passages that keep their origin (file, page, character range) for the source links (§4c).
public enum Ingestion {
    public struct Page: Sendable { public let index: Int?; public let text: String }

    public static func pages(of url: URL) throws -> [Page] {
        switch url.pathExtension.lowercased() {
        case "pdf":
            guard let doc = PDFDocument(url: url) else { throw CocoaError(.fileReadCorruptFile, userInfo: [NSFilePathErrorKey: url.path]) }
            return (0..<doc.pageCount).compactMap { i in doc.page(at: i)?.string.map { Page(index: i, text: $0) } }
        default:
            return [Page(index: nil, text: try String(contentsOf: url, encoding: .utf8))]
        }
    }

    /// Sentence-aligned chunks of about `words` words. Offsets are UTF-16 offsets into the page text.
    public static func chunk(_ text: String, words target: Int = 140) -> [(start: Int, end: Int, text: String)] {
        let tok = NLTokenizer(unit: .sentence)
        tok.string = text
        var out: [(Int, Int, String)] = []
        var start: Int?
        var end = 0
        var count = 0
        let ns = text as NSString
        tok.enumerateTokens(in: text.startIndex..<text.endIndex) { range, _ in
            let r = NSRange(range, in: text)
            if start == nil { start = r.location }
            end = r.upperBound
            count += ns.substring(with: r).split(whereSeparator: \.isWhitespace).count
            if count >= target {
                out.append((start!, end, ns.substring(with: NSRange(location: start!, length: end - start!))))
                start = nil
                count = 0
            }
            return true
        }
        if let s = start, count > 15 { out.append((s, end, ns.substring(with: NSRange(location: s, length: end - s)))) }
        return out.map { ($0.0, $0.1, clean($0.2)) }.filter { $0.2.split(separator: " ").count > 15 }
    }

    /// PDF text has hard line breaks and hyphenation at line ends; join them for the models (offsets stay on the raw text).
    static func clean(_ s: String) -> String {
        s.replacingOccurrences(of: "-\n", with: "")
            .replacingOccurrences(of: #"\s+"#, with: " ", options: .regularExpression)
            .trimmingCharacters(in: .whitespaces)
    }
}

/// SQLite index: FTS5 (BM25) over passage text plus one embedding blob per passage. One file per corpus.
public final class LibraryIndex: @unchecked Sendable {
    public let url: URL
    var db: OpaquePointer?
    let lock = NSLock()

    public init(url: URL) throws {
        self.url = url
        try FileManager.default.createDirectory(at: url.deletingLastPathComponent(), withIntermediateDirectories: true)
        guard sqlite3_open(url.path, &db) == SQLITE_OK else { throw LibraryError.sqlite("open \(url.path)") }
        try exec("""
            CREATE TABLE IF NOT EXISTS docs(id TEXT PRIMARY KEY, title TEXT, path TEXT, added REAL);
            CREATE TABLE IF NOT EXISTS passages(rowid INTEGER PRIMARY KEY, id TEXT UNIQUE, doc TEXT, title TEXT, text TEXT,
                path TEXT, page INTEGER, start INTEGER, end INTEGER, emb BLOB);
            CREATE VIRTUAL TABLE IF NOT EXISTS fts USING fts5(text, content='passages', content_rowid='rowid',
                tokenize='porter unicode61');
            """)
    }

    deinit { sqlite3_close(db) }

    public enum LibraryError: Error { case sqlite(String) }

    func exec(_ sql: String) throws {
        var err: UnsafeMutablePointer<CChar>?
        if sqlite3_exec(db, sql, nil, nil, &err) != SQLITE_OK {
            let m = err.map { String(cString: $0) } ?? "?"
            sqlite3_free(err)
            throw LibraryError.sqlite(m)
        }
    }

    public struct Doc: Sendable, Identifiable, Hashable {
        public let id: String
        public let title: String
        public let path: String
        public let passages: Int

        public init(id: String, title: String, path: String, passages: Int) {
            self.id = id; self.title = title; self.path = path; self.passages = passages
        }
    }

    public func documents() -> [Doc] {
        lock.withLock {
            var out: [Doc] = []
            var st: OpaquePointer?
            sqlite3_prepare_v2(db, "SELECT d.id, d.title, d.path, (SELECT count(*) FROM passages p WHERE p.doc = d.id) FROM docs d ORDER BY d.added DESC", -1, &st, nil)
            while sqlite3_step(st) == SQLITE_ROW {
                out.append(Doc(id: col(st, 0), title: col(st, 1), path: col(st, 2), passages: Int(sqlite3_column_int(st, 3))))
            }
            sqlite3_finalize(st)
            return out
        }
    }

    public func contains(docID: String) -> Bool { documents().contains { $0.id == docID } }

    public var passageCount: Int {
        lock.withLock {
            var st: OpaquePointer?
            sqlite3_prepare_v2(db, "SELECT count(*) FROM passages", -1, &st, nil)
            defer { sqlite3_finalize(st) }
            return sqlite3_step(st) == SQLITE_ROW ? Int(sqlite3_column_int(st, 0)) : 0
        }
    }

    /// Adds a file: pages → passages → embeddings. Returns the number of passages.
    @discardableResult
    public func add(file url: URL, title: String? = nil, embedder: Embedder?) async throws -> Int {
        let docID = url.lastPathComponent
        if contains(docID: docID) { return 0 }
        var passages: [Passage] = []
        for page in try Ingestion.pages(of: url) {
            for (k, c) in Ingestion.chunk(page.text).enumerated() {
                passages.append(Passage(id: "\(docID)#\(page.index ?? 0)-\(k)", docID: docID,
                                        title: title ?? url.deletingPathExtension().lastPathComponent, text: c.text,
                                        fileURL: url, page: page.index, start: c.start, end: c.end))
            }
        }
        let embeddings = try await embedder?.embed(passages.map(\.text))
        try lock.withLock {
            try exec("BEGIN")
            var st: OpaquePointer?
            sqlite3_prepare_v2(db, "INSERT INTO docs VALUES(?,?,?,?)", -1, &st, nil)
            bind(st, 1, docID); bind(st, 2, title ?? url.deletingPathExtension().lastPathComponent); bind(st, 3, url.path)
            sqlite3_bind_double(st, 4, Date().timeIntervalSince1970)
            sqlite3_step(st); sqlite3_finalize(st)
            sqlite3_prepare_v2(db, "INSERT INTO passages(id, doc, title, text, path, page, start, end, emb) VALUES(?,?,?,?,?,?,?,?,?)", -1, &st, nil)
            for (i, p) in passages.enumerated() {
                sqlite3_reset(st)
                bind(st, 1, p.id); bind(st, 2, p.docID); bind(st, 3, p.title); bind(st, 4, p.text); bind(st, 5, url.path)
                sqlite3_bind_int(st, 6, Int32(p.page ?? -1)); sqlite3_bind_int(st, 7, Int32(p.start)); sqlite3_bind_int(st, 8, Int32(p.end))
                if let e = embeddings?[i] {
                    _ = e.withUnsafeBytes { sqlite3_bind_blob(st, 9, $0.baseAddress, Int32($0.count), SQLITE_TRANSIENT) }
                } else {
                    sqlite3_bind_null(st, 9)
                }
                sqlite3_step(st)
            }
            sqlite3_finalize(st)
            try exec("INSERT INTO fts(fts) VALUES('rebuild'); COMMIT")
        }
        return passages.count
    }

    /// Points a document and its passages at a new file location (used when the app's copy of the library is installed).
    public func relocate(docID: String, to path: String) throws {
        lock.withLock {
            var st: OpaquePointer?
            for sql in ["UPDATE passages SET path = ? WHERE doc = ?", "UPDATE docs SET path = ? WHERE id = ?"] {
                sqlite3_prepare_v2(db, sql, -1, &st, nil); bind(st, 1, path); bind(st, 2, docID); sqlite3_step(st); sqlite3_finalize(st)
            }
        }
    }

    public func remove(docID: String) throws {
        try lock.withLock {
            var st: OpaquePointer?
            for sql in ["DELETE FROM passages WHERE doc = ?", "DELETE FROM docs WHERE id = ?"] {
                sqlite3_prepare_v2(db, sql, -1, &st, nil); bind(st, 1, docID); sqlite3_step(st); sqlite3_finalize(st)
            }
            try exec("INSERT INTO fts(fts) VALUES('rebuild')")
        }
    }

    /// BM25 ranking from FTS5 (terms OR-ed, so a question does not need every word to match).
    func bm25(_ query: String, limit: Int) -> [(Int64, Double)] {
        let terms = query.lowercased().components(separatedBy: CharacterSet.alphanumerics.inverted)
            .filter { $0.count > 2 && !Self.stop.contains($0) }
        guard !terms.isEmpty else { return [] }
        let match = terms.map { "\"\($0)\"" }.joined(separator: " OR ")
        return lock.withLock {
            var out: [(Int64, Double)] = []
            var st: OpaquePointer?
            sqlite3_prepare_v2(db, "SELECT rowid, bm25(fts) FROM fts WHERE fts MATCH ? ORDER BY bm25(fts) LIMIT ?", -1, &st, nil)
            bind(st, 1, match); sqlite3_bind_int(st, 2, Int32(limit))
            while sqlite3_step(st) == SQLITE_ROW { out.append((sqlite3_column_int64(st, 0), -sqlite3_column_double(st, 1))) }
            sqlite3_finalize(st)
            return out
        }
    }

    /// Exhaustive cosine similarity (vectors are normalised); fine for thousands of passages.
    func dense(_ q: [Float], limit: Int) -> [(Int64, Double)] {
        lock.withLock {
            var scored: [(Int64, Double)] = []
            var st: OpaquePointer?
            sqlite3_prepare_v2(db, "SELECT rowid, emb FROM passages WHERE emb IS NOT NULL", -1, &st, nil)
            while sqlite3_step(st) == SQLITE_ROW {
                let n = Int(sqlite3_column_bytes(st, 1)) / 4
                guard n == q.count, let p = sqlite3_column_blob(st, 1) else { continue }
                let v = p.bindMemory(to: Float.self, capacity: n)
                var dot: Float = 0
                for i in 0..<n { dot += v[i] * q[i] }
                scored.append((sqlite3_column_int64(st, 0), Double(dot)))
            }
            sqlite3_finalize(st)
            return Array(scored.sorted { $0.1 > $1.1 }.prefix(limit))
        }
    }

    func passages(_ rowids: [Int64]) -> [Int64: Passage] {
        lock.withLock {
            var out: [Int64: Passage] = [:]
            var st: OpaquePointer?
            sqlite3_prepare_v2(db, "SELECT rowid, id, doc, title, text, path, page, start, end FROM passages WHERE rowid = ?", -1, &st, nil)
            for r in rowids {
                sqlite3_reset(st); sqlite3_bind_int64(st, 1, r)
                if sqlite3_step(st) == SQLITE_ROW {
                    let page = Int(sqlite3_column_int(st, 6))
                    out[r] = Passage(id: col(st, 1), docID: col(st, 2), title: col(st, 3), text: col(st, 4),
                                     fileURL: URL(fileURLWithPath: col(st, 5)), page: page < 0 ? nil : page,
                                     start: Int(sqlite3_column_int(st, 7)), end: Int(sqlite3_column_int(st, 8)))
                }
            }
            sqlite3_finalize(st)
            return out
        }
    }

    static let stop: Set<String> = ["the", "and", "for", "are", "was", "what", "which", "who", "how", "does", "did", "with",
                                    "this", "that", "from", "into", "about", "why", "when", "where", "can", "use", "used"]
}

private let SQLITE_TRANSIENT = unsafeBitCast(-1, to: sqlite3_destructor_type.self)
private func bind(_ st: OpaquePointer?, _ i: Int32, _ s: String) { sqlite3_bind_text(st, i, s, -1, SQLITE_TRANSIENT) }
private func col(_ st: OpaquePointer?, _ i: Int32) -> String { sqlite3_column_text(st, i).map { String(cString: $0) } ?? "" }

/// Hybrid retriever: BM25 and dense rankings fused by reciprocal rank fusion (k = 60).
public struct HybridRetriever: Retriever {
    public let index: LibraryIndex
    public let embedder: Embedder?
    public var mode: Mode = .hybrid

    public enum Mode: String, Sendable, CaseIterable { case hybrid, bm25, dense }

    public init(index: LibraryIndex, embedder: Embedder?, mode: Mode = .hybrid) {
        self.index = index; self.embedder = embedder; self.mode = mode
    }

    public func search(_ query: String, k: Int) async throws -> [Passage] {
        let pool = max(50, k * 10)
        let lexical = mode == .dense ? [] : index.bm25(query, limit: pool)
        var semantic: [(Int64, Double)] = []
        if mode != .bm25, let embedder { semantic = index.dense(try await embedder.embed(query: query), limit: pool) }
        var fused: [Int64: Double] = [:]
        for list in [lexical, semantic] {
            for (rank, (id, _)) in list.enumerated() { fused[id, default: 0] += 1.0 / Double(60 + rank + 1) }
        }
        let top = fused.sorted { $0.value > $1.value }.prefix(k)
        let rows = index.passages(top.map(\.key))
        return top.compactMap { id, score in rows[id].map { var p = $0; p.score = score; return p } }
    }
}
