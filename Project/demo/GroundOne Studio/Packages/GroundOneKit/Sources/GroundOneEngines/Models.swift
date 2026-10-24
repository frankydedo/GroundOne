import Foundation
import GroundOneCore
import MLX
import MLXLLM
import MLXLMCommon

/// The models the demo uses. All are read from the local Hugging Face cache or from outputs/models.
public enum ModelCatalog {
    public static let generator = "mlx-community/Qwen2.5-3B-Instruct-4bit"
    public static let embedder = "BAAI/bge-small-en-v1.5"  // chosen by the retrieval check (decision 3)
    public static let verifiers = ["g1-3b-b1", "g1-05b-b1"]

    public struct VerifierInfo: Sendable {
        public let run: String
        public let baseRepo: String
        public let adapterDir: URL
        public let calibration: Calibration
    }

    public static func verifier(_ run: String) throws -> VerifierInfo {
        let dir = Workspace.models.appendingPathComponent(run)
        struct Meta: Decodable { let base_model: String; let design: String? }
        let meta = try JSONDecoder().decode(Meta.self, from: Data(contentsOf: dir.appendingPathComponent("groundone.json")))
        let best = dir.appendingPathComponent("best")
        return VerifierInfo(run: run, baseRepo: meta.base_model, adapterDir: best,
                            calibration: try Calibration.load(best.appendingPathComponent("calibration.json")))
    }

    public static func loadLLM(_ repo: String) async throws -> ModelContainer {
        Runtime.configure()
        return try await LLMModelFactory.shared.loadContainer(from: try Workspace.snapshot(repo), using: TransformersLoader())
    }
}

/// MLX memory limits, as `backend.py` sets them (cache 1 GB): without a cache limit MLX keeps freed buffers of every
/// size it has seen, and variable-length inputs (ingestion, long answers) grow the process to swap.
public enum Runtime {
    nonisolated(unsafe) static var configured = false

    public static func configure(cacheGB: Double = 1, memoryGB: Double = 11) {
        guard !configured else { return }
        configured = true
        MLX.Memory.cacheLimit = Int(cacheGB * 1e9)
        MLX.Memory.memoryLimit = Int(memoryGB * 1e9)
    }
}

/// One-line memory readout for the timing panel and the audit log.
public enum Memory {
    public static func stats() -> MemoryStats {
        MemoryStats(mlxActiveGB: Double(MLX.Memory.activeMemory) / 1e9, mlxPeakGB: Double(MLX.Memory.peakMemory) / 1e9,
                    residentGB: residentGB())
    }

    public static func resetPeak() { MLX.Memory.peakMemory = 0 }

    static func residentGB() -> Double {
        var info = mach_task_basic_info()
        var count = mach_msg_type_number_t(MemoryLayout<mach_task_basic_info>.size) / 4
        let kr = withUnsafeMutablePointer(to: &info) {
            $0.withMemoryRebound(to: integer_t.self, capacity: Int(count)) {
                task_info(mach_task_self_, task_flavor_t(MACH_TASK_BASIC_INFO), $0, &count)
            }
        }
        return kr == KERN_SUCCESS ? Double(info.resident_size_max) / 1e9 : 0
    }
}
