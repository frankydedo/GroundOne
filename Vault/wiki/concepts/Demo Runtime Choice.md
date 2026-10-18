---
type: concept
tags: [concept, demo, swift, mlx-swift, rust, tauri, candle, llama-cpp, core-ml, foundation-models, decision]
---
# Demo Runtime Choice

Why the GroundOne demo is a native macOS app in **Swift/SwiftUI with MLX Swift** (decision D28, 2026-10-18, `Project/docs/demo_architecture.md` §2), and what the alternatives would have cost. This page collects the evidence for the thesis justification.

## The requirement that decides
The demo must run retrieval, a generator and the GroundOne verifier **in one local process**, and the verifier must produce **the same probabilities as in the thesis**: the adapters, the calibration (temperature, per-class bias, τ) and the model fingerprint are tied to MLX 8-bit weights and to the prompt version ([[Calibration]], [[Letter-Token Readout]]). Any runtime that changes weights or kernels re-opens the experiment.

## Options and evidence
| Option | What the sources say | Consequence for GroundOne |
| --- | --- | --- |
| **A. Swift + MLX Swift** | Official Apple bindings over the same C++ core via mlx-c; "all core features apply equally to MLX Swift" ([[Apple ML Explore 2026 - MLX Swift (GitHub README)]], [[Apple WWDC 2025 - Get started with MLX for Apple silicon]]); Qwen2 implemented, mlx-lm adapters load as they are ([[ml-explore 2026 - mlx-swift-lm Qwen2 model source]], [[ml-explore 2026 - mlx-swift-lm LoRA adapters reference]]) | Same weights and kernels; parity checked by a conformance test; no retraining or recalibration |
| B. Python app (existing package) | LM Studio ships a Python mlx-lm engine with a bundled Python 3.11 ([[LM Studio 2026 - mlx-engine, LM Studio Apple MLX engine (GitHub README)]]) | Exact parity, lowest effort; but an interpreter, a server and a browser tab: shows that the experiment can be served, less that a product can be built |
| C. Rust: Tauri + mlx-rs or candle | mlx-rs is community-maintained, two examples, no Qwen or LoRA mentioned ([[oxiglade 2026 - mlx-rs, unofficial Rust bindings to MLX (GitHub README)]]); candle's README documents CPU, CUDA and WASM, not Metal, lists Qwen1.5/Qwen3 but not Qwen2.5, LoRA via a third-party crate ([[Hugging Face 2026 - candle, minimalist ML framework for Rust (GitHub README)]]); Tauri gives a cross-platform web-view UI under 600 KB ([[Tauri 2026 - What is Tauri]]) | Readout and adapter loading to rebuild; for candle, weights remapped and parity to prove; cross-platform UI does not help while inference is tied to the Apple GPU |
| D. llama.cpp / GGUF | widest hardware coverage ([[llama.cpp README (ggml-org)]]) | conversion and requantisation: the calibration must be refitted on dev; future work (Ch. 9) |
| Core ML | conversion with coremltools; CPU/GPU/Neural Engine ([[Apple 2026 - Core ML documentation]]) | numerics change, calibration breaks; future work |
| Foundation Models | on-device and Private Cloud Compute models, guided generation, tools; no logit access documented ([[Apple 2026 - Foundation Models framework documentation]]) | cannot host the verifier; at most an alternative generator, with PCC off for locality |

## Portability, stated precisely
- Swift itself runs on Linux, Windows and Android ([[Swift.org 2026 - Platform support]]); **SwiftUI** and Metal are Apple-only.
- MLX runs on macOS 14+ (Metal), Linux with CUDA and Linux CPU; **no Windows** ([[Apple ML Explore 2026 - MLX documentation, build and install]]). MLX Swift has a CMake build for Linux (CPU, CUDA).
- Hence the non-UI core of the app could in principle run on Linux; the UI could not. The architecture keeps engines behind protocols so that a llama.cpp backend can be added later.

## Costs of A, to state in the thesis
- Apple-only UI; Xcode needed because SwiftPM on the command line cannot build the Metal shaders; `mlx.metallib` must ship with the binary; Metal JIT cold start.
- `mlx-swift-lm` 3.x introduced breaking changes: pin the version (3.32.3).
- Tokenisation goes through swift-transformers, not Python `tokenizers`: token ids are part of the conformance test.
- pysbd has no Swift port ([[Sadvilkar - pySBD, rule-based sentence boundary detection (GitHub README)]]); NLTokenizer's algorithm is undocumented ([[Apple 2026 - NLTokenizer documentation]]).

## Links
- [[Demo Application]], [[MLX Ecosystem]], [[Apple Silicon and MLX]], [[On-Device Inference]], [[Local Inference Hardware]]
