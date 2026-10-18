---
type: concept
tags: [concept, mlx, mlx-swift, mlx-c, mlx-rs, mlx-lm, apple-silicon, bindings]
---
# MLX Ecosystem

The language bindings and libraries around Apple's MLX array framework, as of October 2026. Complements [[Apple Silicon and MLX]] (hardware and performance) with the software layers relevant to building an application ([[Demo Runtime Choice]]).

## Layers
- **C++ core** (`mlx`): arrays, lazy evaluation, unified memory with the device chosen per operation, `compile`, fast kernels (`mx.fast`: RMSNorm, RoPE, attention), group-wise quantisation ([[Apple WWDC 2025 - Get started with MLX for Apple silicon]], [[MLX README (ml-explore)]]).
- **mlx-c**: the official C API; arrays and ops only. Used by Swift and, through `mlx-sys`, by Rust ([[Apple ML Explore 2026 - MLX C API (GitHub README)]]).
- **Python**: `mlx` + `mlx-lm` (generation, LoRA training, unfused adapters, `mlx_lm.fuse`, prompt cache). The reference implementation; GroundOne is built on it.
- **Swift**: `mlx-swift` (bindings; version numbers follow MLX) and `mlx-swift-lm` 3.32.x (`MLXLMCommon`, `MLXLLM` with about 60 architectures including Qwen2, `MLXVLM`, `MLXEmbedders`, `MLXGuidedGeneration`, a bridge to Apple's Foundation Models; LoRA/DoRA load, fuse, unload) ([[Apple ML Explore 2026 - MLX Swift (GitHub README)]], [[Apple ML Explore 2026 - MLX Swift LM, LLMs and VLMs with MLX Swift (GitHub README)]], [[ml-explore 2026 - mlx-swift-lm LoRA adapters reference]], [[ml-explore 2026 - mlx-swift-lm Qwen2 model source]]). App templates in [[Apple ML Explore 2026 - MLX Swift Examples (GitHub README)]].
- **Rust**: `mlx-rs` (community, oxiglade; v0.32.0, 2026-09-12; two examples; autodiff can segfault) ([[oxiglade 2026 - mlx-rs, unofficial Rust bindings to MLX (GitHub README)]]).
- **Products**: LM Studio's MLX engine is Python mlx-lm with Outlines ([[LM Studio 2026 - mlx-engine, LM Studio Apple MLX engine (GitHub README)]]).

## Comparison
| Binding | Status | LLM support | LoRA | Readout access | Platforms |
| --- | --- | --- | --- | --- | --- |
| Python | official, reference | full | train, adapters, fuse | full module access | macOS 14+, Linux CPU/CUDA |
| Swift | official, Apple-maintained; breaking 3.x | ~60 architectures incl. Qwen2 | load (mlx-lm format), fuse, unload, train | hidden states public, head internal | Apple platforms; Linux CPU/CUDA via CMake |
| C | official | none (ops) | – | raw arrays | – |
| Rust | community | Mistral example | not mentioned | build from arrays | Metal flag; Linux not stated |

## Build facts that matter for an app
- SwiftPM on the command line cannot build the Metal shaders: build with Xcode or `xcodebuild`.
- The C++ API is build-from-source only; the app ships `mlx.metallib`; JIT compilation adds a cold start ([[Apple ML Explore 2026 - MLX documentation, build and install]]).
- MLX can end up linked twice in one process if two packages embed it ([[Apple ML Explore 2026 - MLX Swift (GitHub README)]]).
- In Swift the model sits in a container that is an actor managing concurrent access ([[Apple WWDC 2025 - Explore large language models on Apple silicon with MLX]]): the counterpart of GroundOne's single MLX worker thread.

## Links
- [[Apple Silicon and MLX]], [[Demo Runtime Choice]], [[Demo Application]], [[LoRA]], [[Quantization]]
