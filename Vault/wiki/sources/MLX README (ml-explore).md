---
type: source
author: "Awni Hannun, Jagrit Digani, Angelos Katharopoulos, Ronan Collobert (Apple machine learning research)"
date: 2023
venue: "Software (GitHub README); cite as Hannun et al., MLX, 2023"
url: "https://github.com/ml-explore/mlx"
tags: [source, software, mlx, apple-silicon, unified-memory, runtime, on-device]
---
# MLX README (ml-explore)

**Raw file**: `raw/MLX README (ml-explore)_ingested.md`

## Overview
README of **MLX**, "an array framework for machine learning on Apple silicon, brought to you by Apple machine learning research". It is the runtime GroundOne uses for training, calibration, evaluation and inference. The README describes the design principles, points to examples (transformer LM training, LLaMA generation, LoRA fine-tuning, Stable Diffusion, Whisper) and gives install commands and the citation. Citation: Hannun, Digani, Katharopoulos, Collobert, *MLX: Efficient and flexible machine learning on Apple silicon*, 2023, github.com/ml-explore.

## Key Insights
1. **Familiar APIs.** A Python API that follows NumPy; C++, C and Swift APIs that mirror it; `mlx.nn` and `mlx.optimizers` that follow PyTorch.
2. **Composable function transformations** for automatic differentiation, vectorisation and graph optimisation (JAX-like).
3. **Lazy computation.** Arrays are materialised only when needed.
4. **Dynamic graphs.** Changing argument shapes does not trigger slow recompilation.
5. **Multi-device.** Operations run on the CPU or the GPU (the README lists these two; the Neural Engine is not a target).
6. **Unified memory model.** "Arrays in MLX live in shared memory. Operations on MLX arrays can be performed on any of the supported device types without transferring data." This is the feature that distinguishes MLX from frameworks built around discrete GPU memory.
7. **Platforms.** `pip install mlx` on macOS; the current README also lists a CUDA backend (`mlx[cuda]`) and a CPU-only Linux package.
8. **Inspiration.** NumPy, PyTorch, JAX and ArrayFire.

## Relevance to GroundOne
- **The thesis runtime.** All GroundOne models run in MLX (via `mlx-lm`) with 8-bit weights on the M4 GPU, in-process, on one long-lived worker thread (Metal contexts must not hop threads). Latency claims are made only between systems measured in the same MLX in-process setting. See [[Apple Silicon and MLX]].
- **Unified memory explains the setup.** Weights, KV cache and activations share the 16 GB of system memory with the OS and any co-resident generator, so model choice is bounded by memory capacity, and decode speed by memory bandwidth ([[On-Device Inference]], [[Prefill and Decode]]).
- **Prompt cache utilities** (`make_prompt_cache`, `trim_prompt_cache`, `LRUPromptCache` in `mlx_lm`) are documented in [[KV Cache]]; they implement GroundOne's design (a) fallback.
- **Rizzo-Flow** also ships an MLX backend, but the thesis runs it on [[llama.cpp README (ggml-org)|llama.cpp]] ([[Rizzo-Flow]]).

## Links
- Concepts: [[Apple Silicon and MLX]], [[On-Device Inference]], [[KV Cache]], [[Prefill and Decode]], [[LoRA]]
- Related sources: [[llama.cpp README (ggml-org)]], [[Apple 2024 - MacBook Pro 14-inch M4 tech specs]], [[Alizadeh 2024 - LLM in a flash]], [[Gunter 2024 - Apple Intelligence Foundation Language Models]]
