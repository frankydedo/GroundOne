---
type: source
author: "Apple ML Explore (MLX documentation)"
date: 2026
venue: "MLX documentation, Build and Install page (ml-explore.github.io; page metadata published 2023-01-01, content current at retrieval 2026-10-18)"
url: "https://ml-explore.github.io/mlx/build/html/install.html"
tags: [source, mlx, installation, platforms, metal, cuda, linux, cpu, build-options, demo]
---
# Apple ML Explore 2026 – MLX documentation: Build and Install

**Raw file**: `raw/demo/Apple ML Explore 2026 - MLX documentation, build and install_ingested.md`

## Overview
The official installation page of MLX. It lists the supported platforms and backends for the PyPI packages, the build-from-source procedure for the Python and C++ APIs, the CMake options (including binary-size reduction and Metal JIT) and troubleshooting for Rosetta (x86) shells. It is the citable source for "where MLX runs".

## Key Insights
| Target | Install | Requirements (as stated) |
| --- | --- | --- |
| **macOS, Apple silicon** (Metal) | `pip install mlx` | Apple silicon, native Python ≥ 3.10, **macOS ≥ 14.0** |
| **Linux + NVIDIA CUDA** | `pip install mlx[cuda12]` / `mlx[cuda13]` | NVIDIA architecture ≥ SM 7.5, driver ≥ 550.54.14 (≥ 580 for CUDA 13), CUDA toolkit ≥ 12.0, glibc ≥ 2.35, Python ≥ 3.10 |
| **Linux, CPU only** | `pip install mlx[cpu]` | glibc ≥ 2.35, Python ≥ 3.10 |
| **Windows** | not mentioned | page gives no Windows package or build instructions |

- The note "MLX is only available on devices running macOS >= 14.0 and higher" refers to the Apple package; Linux is covered by the CUDA and CPU packages.
- **Build from source**: C++20 compiler (e.g. Clang ≥ 15), CMake ≥ 3.25, Xcode ≥ 15 and macOS SDK ≥ 14; BLAS/LAPACK headers on Linux; `MLX_BUILD_CUDA=ON` for CUDA builds. The **C++ API must be built from source** (no binary package).
- **CMake options (defaults)**: `MLX_BUILD_METAL` ON, `MLX_BUILD_CPU` ON, `MLX_BUILD_SAFETENSORS` ON, `MLX_BUILD_GGUF` ON, `MLX_METAL_JIT` OFF, tests ON, examples/benchmarks/Python bindings OFF.
- **Deployment detail**: the built `mlx.metallib` must sit next to an executable statically linked to `libmlx.a`, or `METAL_PATH` must point to it.
- **Metal JIT**: `MLX_METAL_JIT=ON` shrinks the Metal library by compiling kernels at first use; cold start "from a few hundred millisecond to a few seconds", then cached by the system across reboots.
- **Native arm64 required**: a Rosetta (x86) Python or shell does not find a matching distribution and breaks the build.

## Relevance to GroundOne
- **Platform reach of any MLX-based demo**: macOS 14+ on Apple silicon (Metal), Linux CPU, Linux NVIDIA CUDA; no Windows. Choosing MLX, in any language, therefore means a Mac-first demo. This is consistent with the thesis machine and the locality pillar ([[Local Inference Hardware]], [[On-Device Inference]]). Cross-platform reach would require a different engine (llama.cpp, candle), at the cost of losing numerical parity with the MLX-trained model ([[Demo Runtime Choice]]).
- **Native arm64 requirement** already applies to the GroundOne venv (CLAUDE.md: native arm64 Python required for MLX); the same constraint holds for the app build.
- **Metal JIT cold start** is a UX consideration for the app's first verification. With default (non-JIT) builds the kernels are precompiled into the metallib.
- **GGUF/safetensors loaders are in the core**, so weight loading is available to every binding. The 8-bit MLX checkpoint and LoRA adapter are safetensors.

## Links
- Concepts: [[Apple Silicon and MLX]], [[MLX Ecosystem]], [[Demo Runtime Choice]], [[Local Inference Hardware]], [[On-Device Inference]]
- Related sources: [[MLX README (ml-explore)]], [[Apple ML Explore 2026 - MLX Swift (GitHub README)]], [[Apple ML Explore 2026 - MLX C API (GitHub README)]], [[oxiglade 2026 - mlx-rs, unofficial Rust bindings to MLX (GitHub README)]]
