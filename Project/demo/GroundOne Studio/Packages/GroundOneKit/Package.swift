// swift-tools-version: 6.0
import PackageDescription

// GroundOneCore has no ML imports (testable with `swift test`); GroundOneEngines runs MLX and must be built with
// xcodebuild, which compiles the Metal shaders (SwiftPM on the command line cannot). The conformance gate runs as
// `g1studio verify-fixture` against the fixtures exported by Python.
let package = Package(
    name: "GroundOneKit",
    platforms: [.macOS(.v15)],
    products: [
        .library(name: "GroundOneCore", targets: ["GroundOneCore"]),
        .library(name: "GroundOneEngines", targets: ["GroundOneEngines"]),
        .executable(name: "g1studio", targets: ["g1studio"]),
    ],
    dependencies: [
        .package(url: "https://github.com/ml-explore/mlx-swift-lm", exact: "3.32.3"),
        .package(url: "https://github.com/huggingface/swift-transformers", exact: "1.3.5"),
    ],
    targets: [
        .target(name: "GroundOneCore"),
        .target(
            name: "GroundOneEngines",
            dependencies: [
                "GroundOneCore",
                .product(name: "MLXLLM", package: "mlx-swift-lm"),
                .product(name: "MLXLMCommon", package: "mlx-swift-lm"),
                .product(name: "MLXEmbedders", package: "mlx-swift-lm"),
                .product(name: "Tokenizers", package: "swift-transformers"),
            ]),
        .executableTarget(name: "g1studio", dependencies: ["GroundOneCore", "GroundOneEngines"]),
        .testTarget(name: "GroundOneCoreTests", dependencies: ["GroundOneCore"]),
    ]
)
