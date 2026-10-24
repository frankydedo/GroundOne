import Foundation

/// Where data lives. The command-line tools read the thesis workspace (`Project/`: adapters in outputs/models, fixtures
/// and results in outputs/demo). The app reads its own folder in Application Support, filled by `g1studio install`, so it
/// never needs access to the protected Desktop folder.
public enum Workspace {
    public enum Mode: Sendable { case workspace, app }
    nonisolated(unsafe) public static var mode: Mode = .workspace

    public static var appSupport: URL {
        FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask)[0]
            .appendingPathComponent("GroundOne Studio")
    }

    public static func project(from file: String = #filePath) -> URL {
        if let env = ProcessInfo.processInfo.environment["GROUNDONE_WORKSPACE"] { return URL(fileURLWithPath: env) }
        if let saved = UserDefaults.standard.string(forKey: "workspace"), !saved.isEmpty { return URL(fileURLWithPath: saved) }
        var dir = URL(fileURLWithPath: file).deletingLastPathComponent()
        while dir.path != "/" {
            if FileManager.default.fileExists(atPath: dir.appendingPathComponent("outputs/models").path) { return dir }
            dir = dir.deletingLastPathComponent()
        }
        return FileManager.default.homeDirectoryForCurrentUser.appendingPathComponent("Desktop/THESIS/Project")
    }

    public static var models: URL { mode == .app ? appSupport.appendingPathComponent("models") : project().appendingPathComponent("outputs/models") }
    public static var demo: URL { mode == .app ? appSupport : project().appendingPathComponent("outputs/demo") }
    public static var huggingFaceCache: URL {
        if let h = ProcessInfo.processInfo.environment["HF_HUB_CACHE"] { return URL(fileURLWithPath: h) }
        return FileManager.default.homeDirectoryForCurrentUser.appendingPathComponent(".cache/huggingface/hub")
    }

    /// Local snapshot directory of a Hugging Face repo in the cache (never downloads).
    public static func snapshot(_ repo: String) throws -> URL {
        let base = huggingFaceCache.appendingPathComponent("models--" + repo.replacingOccurrences(of: "/", with: "--"))
        let ref = (try? String(contentsOf: base.appendingPathComponent("refs/main"), encoding: .utf8))?
            .trimmingCharacters(in: .whitespacesAndNewlines)
        if let ref, FileManager.default.fileExists(atPath: base.appendingPathComponent("snapshots/\(ref)").path) {
            return base.appendingPathComponent("snapshots/\(ref)")
        }
        let snaps = (try? FileManager.default.contentsOfDirectory(atPath: base.appendingPathComponent("snapshots").path)) ?? []
        guard let first = snaps.sorted().first else {
            throw CocoaError(.fileNoSuchFile, userInfo: [NSFilePathErrorKey: base.path])
        }
        return base.appendingPathComponent("snapshots/\(first)")
    }
}
