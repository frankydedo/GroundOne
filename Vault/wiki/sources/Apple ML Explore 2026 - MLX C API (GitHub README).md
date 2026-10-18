---
type: source
author: "Apple ML Explore (ml-explore)"
date: 2026
venue: "GitHub repository README, ml-explore/mlx-c (retrieved 2026-10-18)"
url: "https://github.com/ml-explore/mlx-c"
tags: [source, mlx, mlx-c, c-api, ffi, bindings, apple-silicon, demo]
---
# Apple ML Explore 2026 – MLX C: the C API for MLX

**Raw file**: `raw/demo/Apple ML Explore 2026 - MLX C API (GitHub README)_ingested.md`

## Overview
MLX C is the official C API for MLX. It "can be used standalone or as a bridge to bind other languages to MLX"; the README gives MLX Swift as the example of a binding built on it. The README is short: a CMake build (`cmake -B build -DCMAKE_BUILD_TYPE=Release`, then `cmake --build build -j`), an example program (`./example`), and a link to the documentation at ml-explore.github.io/mlx-c.

## Key Insights
- **Role in the ecosystem**: the stable C layer between the C++ core and other languages. MLX Swift uses it (stated here); mlx-rs generates its `mlx-sys` crate from it (stated in [[oxiglade 2026 - mlx-rs, unofficial Rust bindings to MLX (GitHub README)|the mlx-rs README]]).
- **Official**: in the `ml-explore` organisation; build requires CMake.
- **Not stated**: API coverage, versioning, platforms beyond Apple silicon, any LLM-level functions. It is an array/op API, with no model loading, tokenizer or generation loop.

## Relevance to GroundOne
- **Explains why the non-Python bindings share Python's kernels.** Python MLX, MLX Swift (through MLX C) and mlx-rs (through `mlx-sys`) all end in the same C++ core and Metal kernels. Matching *versions*, not the language, decides kernel-level parity. This supports the conformance-test argument in [[Demo Runtime Choice]].
- **Not a practical app runtime on its own** for the demo: everything above arrays (Qwen2.5 model definition, safetensors/adapter loading, tokenizer, marker readout) would have to be written in C or in the host language. It matters as the foundation under Swift and Rust, not as an option of its own.
- **Risk for Rust**: a binding generated from MLX C trails both MLX C and the core, so features exposed in Python first may reach Rust late.

## Links
- Concepts: [[MLX Ecosystem]], [[Demo Runtime Choice]], [[Apple Silicon and MLX]]
- Related sources: [[Apple ML Explore 2026 - MLX Swift (GitHub README)]], [[oxiglade 2026 - mlx-rs, unofficial Rust bindings to MLX (GitHub README)]], [[Apple ML Explore 2026 - MLX documentation, build and install]], [[MLX README (ml-explore)]]
