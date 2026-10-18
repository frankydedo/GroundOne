---
type: source
author: "oxiglade (community project) and contributors"
date: 2026
venue: "GitHub repository README, oxiglade/mlx-rs (MIT/Apache-2.0; 383 stars, created 2023-12-23, latest release v0.32.0 on 2026-09-12; retrieved 2026-10-18)"
url: "https://github.com/oxiglade/mlx-rs"
tags: [source, mlx, mlx-rs, rust, bindings, community, apple-silicon, demo, runtime-alternative]
---
# oxiglade 2026 – mlx-rs: unofficial Rust bindings to MLX

**Raw file**: `raw/demo/oxiglade 2026 - mlx-rs, unofficial Rust bindings to MLX (GitHub README)_ingested.md`

## Overview
mlx-rs provides Rust bindings for Apple's MLX, aiming at "a safe and idiomatic Rust interface". It is a community project (organisation `oxiglade`), not part of `ml-explore`. The README carries the banner "Project is in active development - contributors welcome!" and states that it "can be used to run MLX models in Rust". Metadata recorded at retrieval: 383 stars, repository created 2023-12-23, latest release v0.32.0 (2026-09-12).

## Key Insights
- **Status**: unofficial; active development; MSRV Rust 1.88.0; dual MIT/Apache-2.0 licence; docs hosted on GitHub Pages "due to known limitation of docsrs".
- **Versioning**: the `mlx-rs` crate follows MLX's version (v0.32.0 implies MLX 0.32); the `mlx-sys` crate follows `mlx-c`, "as that is the version from which the API is generated". So the Rust API is generated from the MLX C API.
- **Features** listed are MLX's own: lazy evaluation, dynamic graphs, CPU and GPU devices, unified memory. Feature flags: `metal` (GPU) and `accelerate`.
- **Examples**: only two, `mnist` (training) and `mistral` (text generation with pre-trained Mistral).
- **Known sharp edge**: automatic differentiation with closures that capture arrays from the outer scope "may cause segfaults"; all arrays must be passed explicitly as inputs. The authors are "actively working on improving this API".
- **Not mentioned**: Qwen2/Qwen2.5, LoRA or adapter loading, quantized-model loading, tokenizers, a model zoo, or a Linux/CUDA story.

## Relevance to GroundOne
- **The Rust + MLX alternative** in [[Demo Runtime Choice]]. Kernel-level parity is in principle the same as Swift (same core through MLX C), but everything above arrays (Qwen2.5 architecture, loading 8-bit safetensors and the LoRA adapter, tokenizer, marker readout) would have to be written or ported. MLX Swift LM already ships most of it.
- **Maturity and risk**: community-maintained, one model example, segfault caveats in autodiff (training only; the demo needs inference only), and no LoRA/quantization documentation. For a thesis demo with a fixed deadline this is more risk than Swift, whose bindings are official and claim parity with Python.
- **Logits access** would be available (it is an array library), but the readout path must be implemented from scratch.
- **What Rust would buy**: a cross-platform core and Tauri compatibility. MLX itself is Apple silicon/Linux only ([[Apple ML Explore 2026 - MLX documentation, build and install]]), so a Rust + MLX app would not gain Windows reach either.

## Links
- Concepts: [[MLX Ecosystem]], [[Demo Runtime Choice]], [[Demo Application]], [[Apple Silicon and MLX]], [[Quantization]], [[LoRA]]
- Related sources: [[Apple ML Explore 2026 - MLX C API (GitHub README)]], [[Apple ML Explore 2026 - MLX Swift (GitHub README)]], [[Hugging Face 2026 - candle, minimalist ML framework for Rust (GitHub README)]], [[llama.cpp README (ggml-org)]]
