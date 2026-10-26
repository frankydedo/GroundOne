import Foundation
import MLX

/// Diagnostic: MLX's fused attention with the "causal" mode against an explicit boolean mask, for several queries
/// after cached keys (the prefix-cache case, D32). MLX 0.29.3 (Python) is wrong for some shapes; this checks the core
/// linked into the app.
public enum SDPACheck {
    public static func run(_ args: [String]) {
        MLXRandom.seed(0)
        var worst = (L: 0, offset: 0, err: Float(0))
        for (H, D) in [(14, 64), (16, 128)] {   // Qwen2.5 0.5B and 3B attention geometry (2 KV heads)
        for L in [2, 16, 33, 100, 128, 200, 300, 400, 501, 512, 700] {
            for off in [1, 31, 63, 100, 255, 257, 300, 523, 700, 1000] {
                let S = L + off
                let q = MLXRandom.normal([1, H, L, D]).asType(.bfloat16)
                let k = MLXRandom.normal([1, 2, S, D]).asType(.bfloat16)
                let v = MLXRandom.normal([1, 2, S, D]).asType(.bfloat16)
                let mask = MLXArray(0 ..< Int32(S)).expandedDimensions(axis: 0) .<= (MLXArray(0 ..< Int32(L)).expandedDimensions(axis: 1) + Int32(off))
                let a = MLXFast.scaledDotProductAttention(queries: q, keys: k, values: v, scale: 1 / Float(D).squareRoot(), mask: .causal)
                let b = MLXFast.scaledDotProductAttention(queries: q, keys: k, values: v, scale: 1 / Float(D).squareRoot(), mask: .array(mask))
                let err = abs(a.asType(.float32) - b.asType(.float32)).max().item(Float.self)
                if err > 0.02 { print("H=\(H) D=\(D) L=\(L) offset=\(off): max |causal - explicit| = \(err)") }
                if err > worst.err { worst = (L, off, err) }
            }
        }
        }
        print("worst: L=\(worst.L) offset=\(worst.offset) err=\(worst.err)")
    }
}
