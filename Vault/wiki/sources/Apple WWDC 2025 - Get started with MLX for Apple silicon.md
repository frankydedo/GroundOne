---
type: source
author: "Apple (WWDC25 session 315, presented by Awni of the MLX team)"
date: 2025-06-09
venue: "Apple WWDC 2025 session video and transcript (developer.apple.com; retrieved 2026-10-18)"
url: "https://developer.apple.com/videos/play/wwdc2025/315/"
tags: [source, wwdc, mlx, mlx-swift, unified-memory, lazy-evaluation, compile, metal-kernels, quantization, distributed, apple-silicon]
---
# Apple WWDC 2025 – Get started with MLX for Apple silicon

**Raw file**: `raw/demo/Apple WWDC 2025 - Get started with MLX for Apple silicon_ingested.md`

## Overview
An official WWDC25 introduction to MLX (the presenter introduces himself as "Awni"). It covers what MLX is, its Python basics, its key features (unified memory, lazy evaluation, function transformations, `mlx.nn` and `mlx.optimizers`), the performance tools (`mx.compile`, `mx.fast`, custom Metal kernels, quantization, `mx.distributed`) and a short introduction to MLX Swift. It is the companion of [[Apple WWDC 2025 - Explore large language models on Apple silicon with MLX]].

## Key Insights
- **Positioning**: open-source (MIT) array framework "purpose-built for Apple Silicon", running on the CPU or on the GPU through Metal. NumPy-like core API; higher-level API similar to PyTorch and JAX. An active Hugging Face community (`mlx-community`) uploads new models daily.
- **APIs**: "fully-featured Python API", a Swift API "which includes all the high-level packages for building and optimizing neural networks", plus C++ and C. Targets "Mac, iPhone, iPad, and Vision Pro".
- **Production use named by Apple**: "MLX is used by LM Studio, a popular application for generating text with large language models directly on your Mac" (see [[LM Studio 2026 - mlx-engine, LM Studio Apple MLX engine (GitHub README)]]).
- **Unified memory programming model**: arrays live in unified memory and are never copied; the *operation* takes a device/stream (`stream=mx.gpu` or `mx.cpu`), CPU and GPU ops can run in parallel, and dependencies are managed automatically.
- **Lazy evaluation**: operations build a graph; evaluation happens on `print`, conversion (`tolist()`) or `mx.eval`. This enables graph transformations and means "you only ever pay for what you use".
- **Function transformations**: `mx.grad` (composable, e.g. second derivatives) and `mx.compile` (fuses several kernel launches into one, saving memory bandwidth and overhead).
- **`mx.fast`**: tuned implementations of transformer building blocks: positional encodings (RoPE), normalisation (`rms_norm`), scaled dot-product attention with additive, Boolean or named masks. A custom Metal kernel API (`mx.fast.metal_kernel`) JIT-compiles user kernels that behave like any other lazy op.
- **Quantization**: `mx.quantize(w, bits, group_size)` with a shared scale and bias per group, `mx.quantized_matmul`, `mx.dequantize`; `nn.quantize(model, ...)` with an optional per-layer callback. Fewer bits and larger groups give smaller, faster models.
- **Distributed**: `mx.distributed` (e.g. `all_sum`) over Ethernet or Thunderbolt; `mlx.launch --hosts ...`.
- **MLX Swift**: added as an Xcode package dependency; "built on top of Metal and works great across macOS, iOS, iPadOS, visionOS"; APIs "intentionally similar" between Python and Swift; "All of the core features ... as well as the optimizations ... apply equally to MLX Swift."

## Relevance to GroundOne
- **Thesis Ch. 2 (local inference) citation** for unified memory and lazy evaluation as MLX's design choices on Apple silicon ([[Apple Silicon and MLX]], [[On-Device Inference]]).
- **Parity argument for the Swift demo.** Apple states that Swift exposes the same core features and optimisations (`compile`, `mx.fast`, quantization) as Python. The Qwen2.5 forward pass in Swift can therefore use the same fast RMSNorm, RoPE, attention and quantized-matmul kernels that `mlx-lm` uses in Python. This is the basis for expecting GroundOne's probabilities to be reproduced within a small tolerance rather than exactly ([[Demo Runtime Choice]]).
- **Lazy evaluation and the readout.** Because the graph is lazy, gathering hidden states only at marker positions before the output head avoids computing the full vocabulary logits at every token. This is the efficiency GroundOne's `readout.py` relies on, and it carries over to Swift.
- **Quantization semantics** (group-wise scale and bias) define what "MLX 8-bit" means for the GroundOne base checkpoints ([[Quantization]]).
- **LM Studio as a production precedent** for MLX in a shipping Mac app, cited by Apple itself.

## Links
- Concepts: [[Apple Silicon and MLX]], [[MLX Ecosystem]], [[On-Device Inference]], [[Quantization]], [[Letter-Token Readout]], [[Demo Runtime Choice]], [[Prefill and Decode]]
- Related sources: [[Apple WWDC 2025 - Explore large language models on Apple silicon with MLX]], [[Apple ML Explore 2026 - MLX Swift (GitHub README)]], [[MLX README (ml-explore)]], [[Apple ML Research 2025 - Exploring LLMs with MLX and the neural accelerators in the M5 GPU]], [[LM Studio 2026 - mlx-engine, LM Studio Apple MLX engine (GitHub README)]]
