---
type: concept
tags: [concept, apple-silicon, m4, mlx, unified-memory, memory-bandwidth, hardware, runtime, groundone]
---
# Apple Silicon and MLX

The hardware and runtime on which [[GroundOne]] is built and measured: an Apple M4 laptop with unified memory, running models through Apple's MLX framework. See [[On-Device Inference]] for the wider local-vs-remote picture.

## The thesis machine (vendor-cited)
MacBook Pro 14-inch (M4, 2024), per [[Apple 2024 - MacBook Pro 14-inch M4 tech specs|Apple's tech specs]] (support.apple.com/en-us/121552, retrieved 2026-10-10):

| Item | Value |
| --- | --- |
| Chip | Apple M4 |
| CPU | 10-core (4 performance + 6 efficiency) |
| GPU | 10-core |
| Neural Engine | 16-core |
| Unified memory | **16 GB** (options 24 / 32 GB) |
| Memory bandwidth | **120 GB/s** |
| Battery | 72.4 Wh |

Apple's page gives no TFLOPS figure; compute throughput is characterised here by measured prefill speed instead.

## Unified memory
On Apple silicon the CPU, GPU and Neural Engine share one pool of DRAM. MLX builds on this: "Arrays in MLX live in shared memory. Operations on MLX arrays can be performed on any of the supported device types without transferring data" ([[MLX README (ml-explore)|MLX README]]). Consequences for GroundOne:
- there is no separate VRAM limit, but weights, KV caches, activations, the OS and any co-resident generator all share the same 16 GB;
- LLM in a flash describes this hierarchy as flash (~100 GB, ~1 GB/s random read) below DRAM (~10 GB, ~100 GB/s) ([[Alizadeh 2024 - LLM in a flash|Alizadeh 2024]] Fig. 2a); GroundOne stays fully in DRAM by using 0.5B and 3B models in 8-bit (training peaks 2.6 GB and 5.9 GB).

## Why memory bandwidth bounds decode
At batch 1, each decode step is a matrix–vector product that reads every weight once, so time per token ≥ weight bytes / bandwidth ([[Prefill and Decode]]; [[Pope 2023 - Efficiently Scaling Transformer Inference|Pope 2023]]).
- 8-bit [[Qwen2.5]]-0.5B ≈ 0.5 GB → ≥ 0.5 / 120 ≈ **4 ms/token**; measured ≈ 6–7 ms/token.
- 8-bit Qwen2.5-3B ≈ 3.3 GB → ≥ **27 ms/token**; measured ≈ 32–42 ms/token.
- Prefill is a matrix–matrix product over all prompt tokens and is compute-bound: ≈ 0.33–0.37 ms/token (0.5B) and ≈ 2.1–2.2 ms/token (3B). **One decode step costs about as much as prefilling 14–21 tokens** on this machine (Phase 0 and preliminary measurements).

This is the hardware root of the System One argument: a model that reads all K verdicts from one prefill sidesteps the bandwidth bound that limits every generative judge. It also explains the energy pattern: GroundOne's compute-bound pass draws more power (16 W) than memory-bound decoding (11–14 W) ([[Energy of LLM Inference]], [[Patel 2024 - Splitwise (prefill vs decode phases)|Splitwise]]).

## MLX design (Hannun et al., 2023)
From the [[MLX README (ml-explore)|README]]:
- NumPy-like Python API; C++, C and Swift APIs; `mlx.nn` and `mlx.optimizers` modelled on PyTorch;
- composable function transformations (autodiff, vectorisation, graph optimisation);
- **lazy computation** and **dynamic graphs** (shape changes do not trigger slow recompilation);
- devices: CPU and GPU (Metal). The Neural Engine is not an MLX target; Apple's own on-device model runs on the ANE instead ([[Gunter 2024 - Apple Intelligence Foundation Language Models|Gunter 2024]] §5.2);
- recent versions also ship CUDA and CPU-only Linux backends.

## How GroundOne uses it
- `mlx-lm` for model loading, 8-bit affine quantisation, [[LoRA]] training (r16 on all linear layers) and inference.
- All MLX calls run on **one long-lived worker thread** (Metal contexts must not hop threads); requests are serialised and parallelism is inside a request.
- Design (b) runs one forward pass per answer and applies the output head only at the " Verdict:" markers; design (a) uses the `mlx_lm` prompt cache with trimming ([[KV Cache]]).
- Long jobs run under a memory guard (kill if free memory < 2 GB or swap grows > 3 GB): on 16 GB of unified memory, memory pressure is the operational risk.
- Latency claims are made only between systems measured in-process in MLX. [[Rizzo-Flow]] runs on [[llama.cpp README (ggml-org)|llama.cpp]] (Metal backend, Q4, over HTTP), so no latency claim is made against it.

## Links
- Concepts: [[On-Device Inference]], [[Prefill and Decode]], [[KV Cache]], [[Energy of LLM Inference]], [[Qwen2.5]], [[LoRA]], [[GroundOne]]
- Sources: [[Apple 2024 - MacBook Pro 14-inch M4 tech specs]], [[MLX README (ml-explore)]], [[llama.cpp README (ggml-org)]], [[Alizadeh 2024 - LLM in a flash]], [[Gunter 2024 - Apple Intelligence Foundation Language Models]], [[Pope 2023 - Efficiently Scaling Transformer Inference]]
