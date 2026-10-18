---
type: source
author: "Apple ML Explore (ml-explore); initially developed by David Koski and Ronan Collobert, maintained by David Koski"
date: 2026
venue: "GitHub repository README, ml-explore/mlx-swift (retrieved 2026-10-18)"
url: "https://github.com/ml-explore/mlx-swift"
tags: [source, mlx, mlx-swift, swift, apple-silicon, runtime, metal, cuda, demo, on-device]
---
# Apple ML Explore 2026 – MLX Swift: the Swift API for MLX

**Raw file**: `raw/demo/Apple ML Explore 2026 - MLX Swift (GitHub README)_ingested.md`

## Overview
MLX Swift is the official Swift API for MLX, the array framework for machine learning on Apple silicon, published in the same `ml-explore` GitHub organisation as MLX itself. The README covers installation (Xcode, SwiftPM, `xcodebuild`, CMake), points to the example applications, and states two policies that matter for a port: the version numbers follow MLX, and every MLX (Python) capability should also exist in Swift. LLM and VLM implementations do not live in this package; they are in the separate [[Apple ML Explore 2026 - MLX Swift LM, LLMs and VLMs with MLX Swift (GitHub README)|mlx-swift-lm]] package.

## Key Insights
- **Official, Apple-maintained.** Lives in the `ml-explore` organisation. Initially developed by David Koski and Ronan Collobert, now maintained by David Koski. Built on top of MLX, whose initial developers are listed as Awni Hannun, Jagrit Digani, Angelos Katharopoulos and Ronan Collobert.
- **Parity policy**: "All capabilities in MLX (Python) should be available in MLX Swift"; missing ones are treated as issues. "Generally the MLX Swift version number corresponds to the same version number in MLX."
- **Architecture**: the build pulls in `Source/Cmlx/mlx` (the C++ core) and `Source/Cmlx/mlx-c` (the C API) as git submodules. Swift therefore calls the same C++ core through MLX C (confirmed by [[Apple ML Explore 2026 - MLX C API (GitHub README)|the MLX C README]]).
- **Libraries**: `MLX`, `MLXNN`, `MLXOptimizers`, `MLXRandom`, linked as needed.
- **Platforms and backends**: Xcode/SwiftPM on Apple platforms (the examples run on iOS and macOS); CMake build with Metal by default on macOS; native Linux build with the CPU backend by default; a CUDA GPU backend that "is exclusive to Linux". Windows is not mentioned.
- **Build caveats**: SwiftPM on the command line "cannot build the Metal shaders", so the final build must go through Xcode or `xcodebuild`. MLX is built as a library, so an app that links MLX and also links a framework that links MLX can end up with "two copies of MLX in the resulting process"; the fix is to build MLX as a Framework from `xcode/MLX.xcodeproj`.
- **Examples** listed: MNISTTrainer, MLXChatExample (LLMs and VLMs, iOS and macOS), LLMEval, StableDiffusionExample, `llm-tool` (CLI), plus "guidelines on porting models from MLX Python".
- The README does not give a release date, star count, a list of supported model architectures or anything about LoRA; these are in mlx-swift-lm or not stated.

## Relevance to GroundOne
- **Primary runtime candidate for the demo** ([[Demo Runtime Choice]]). It is the only MLX binding besides Python that is official and claims feature parity with Python, which is the main argument for Swift over [[oxiglade 2026 - mlx-rs, unofficial Rust bindings to MLX (GitHub README)|mlx-rs]].
- **Numerical parity.** Swift reaches the same C++ core and Metal kernels as Python MLX through MLX C. If the app pins the MLX Swift version that matches the MLX version used by `mlx-lm` in training and evaluation, the forward pass runs the same kernels. Remaining sources of divergence for the conformance test are the tokenizer, prompt rendering, segmentation and possible graph differences (fused or compiled ops); these are inferences, not claims of the README.
- **Logits and readout.** This package provides arrays, `MLXNN` modules and ops, enough to write the readout by hand (gather hidden states at the " Verdict:" marker positions, apply the output head, keep the A/B/C logits). The model definition itself must come from mlx-swift-lm or be ported.
- **Build risk.** The Metal-shader limitation of SwiftPM and the duplicate-MLX pitfall shape the project layout: one Xcode app target that links MLX once.
- **Platform reach.** Apple platforms, plus Linux (CPU and CUDA). The demo targets macOS on Apple silicon only ([[Local Inference Hardware]]).

## Links
- Concepts: [[Apple Silicon and MLX]], [[MLX Ecosystem]], [[Demo Application]], [[Demo Runtime Choice]], [[On-Device Inference]], [[Letter-Token Readout]]
- Related sources: [[MLX README (ml-explore)]], [[Apple ML Explore 2026 - MLX Swift LM, LLMs and VLMs with MLX Swift (GitHub README)]], [[Apple ML Explore 2026 - MLX Swift Examples (GitHub README)]], [[Apple ML Explore 2026 - MLX C API (GitHub README)]], [[Apple WWDC 2025 - Get started with MLX for Apple silicon]]
