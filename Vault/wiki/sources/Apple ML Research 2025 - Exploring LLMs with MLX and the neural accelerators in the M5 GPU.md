---
type: source
author: "Apple Machine Learning Research"
date: 2025-11-19
venue: "Apple Machine Learning Research blog, highlight post (retrieved 2026-10-11)"
url: "https://machinelearning.apple.com/research/exploring-llms-mlx-m5"
tags: [source, vendor-measurement, apple-silicon, mlx, m5, m4, neural-accelerators, prefill, decode, ttft, bandwidth, quantization, moe]
---
# Apple ML Research 2025 – Exploring LLMs with MLX and the Neural Accelerators in the M5 GPU

**Raw file**: `raw/local_inference/Apple ML Research 2025 - Exploring LLMs with MLX and the neural accelerators in the M5 GPU_ingested.md`

## Overview
Apple benchmarks LLM inference with **MLX** (`mlx_lm.generate`) on a **MacBook Pro M5 (24 GB)** against a "similarly configured" **MacBook Pro M4**, the thesis machine's chip. The M5 adds **Neural Accelerators inside each GPU core** (dedicated matrix-multiplication units), used by MLX through Metal 4 TensorOps / Metal Performance Primitives (requires macOS 26.2+). The post states the prefill/decode split as the vendor's own explanation: **"generating the first token is compute-bound"**, while **"generating subsequent tokens is bounded by memory bandwidth"**. Matrix-multiply hardware therefore speeds up TTFT about 3.3–4.1x but generation only about 1.2–1.3x.

## Key Insights
- **Setup:** prompt of 4,096 tokens; generation speed measured on 128 additional tokens. Models: Qwen3 1.7B and 8B (BF16), Qwen3 8B and 14B (4-bit), Qwen3-30B-A3B MoE (4-bit, 3B active), gpt-oss-20B (MXFP4).
- **Bandwidth (Apple):** **M4 120 GB/s, M5 153 GB/s (+28%)**.
- **Results (M5 vs M4, Table 1):**

| Model | TTFT speedup | Generation speedup | Memory (GB) |
| --- | --- | --- | --- |
| Qwen3-1.7B bf16 | 3.57x | 1.27x | 4.40 |
| Qwen3-8B bf16 | 3.62x | 1.24x | 17.46 |
| Qwen3-8B 4-bit | 3.97x | 1.24x | 5.61 |
| Qwen3-14B 4-bit | 4.06x | 1.19x | 9.16 |
| gpt-oss-20b MXFP4 | 3.33x | 1.24x | 12.08 |
| Qwen3-30B-A3B 4-bit | 3.52x | 1.25x | 17.31 |

- **The generation speedup (1.19–1.27x) is at or just below the bandwidth ratio (1.28x)**, as expected for a bandwidth-bound phase. The TTFT speedup (3.3–4.1x) follows the new matrix-multiply hardware, not bandwidth.
- **Absolute values on M5:** TTFT under 10 s for the dense 14B and under 3 s for the 30B MoE (4,096-token prompt). The absolute M4 numbers were in charts that are **not in the extraction**.
- A 24 GB MacBook Pro holds an 8B in BF16 or a 30B MoE at 4-bit with the workload under 18 GB. FLUX-dev 4-bit (12B) image generation is more than 3.8x faster on M5.
- **Vendor benchmark:** Apple measuring its own hardware and framework. There are no error bars, and "similarly configured" is not detailed. It is still the most authoritative statement of the M4 vs M5 behaviour.

## Relevance to GroundOne
- **The vendor confirms the thesis's central hardware argument** on the exact chip family used: TTFT (prefill) is compute-bound, generation is bandwidth-bound ([[Prefill and Decode]]). A System One's cost is TTFT only. A generative judge's cost is TTFT plus generation.
- **Asymmetric gains on next-generation hardware.** Moving from M4 to M5, prefill-type work sped up about 3.3–4.1x while decode sped up about 1.2x. A workload with no decode (GroundOne) should therefore benefit about three times more from this hardware generation than the decode part of a verbose judge. This is an **extrapolation**: Apple measured 1.7B–30B models with 4k prompts, while GroundOne uses 0.5B/3B in 8-bit with prompts of hundreds of tokens, where fixed overheads weigh more. It has not been measured for GroundOne and should be stated as an expectation.
- **M4 baseline numbers are citable.** The 120 GB/s M4 bandwidth here agrees with [[Apple 2024 - MacBook Pro 14-inch M4 tech specs]].
- **Memory sizes for co-residence.** An 8B 4-bit generator takes 5.61 GB in MLX. Next to GroundOne-3B (about 3.3 GB of weights) and a retriever, this would fit in the thesis's 16 GB budget ([[On-Device Inference]]).
- MLX quantisation via `mlx_lm.convert` takes seconds, the same toolchain GroundOne uses for 8-bit models ([[Apple Silicon and MLX]]).

## Links
- Concepts: [[Apple Silicon and MLX]], [[Prefill and Decode]], [[On-Device Inference]], [[Mixture of Experts]], [[KV Cache]], [[Local Inference Hardware]] (proposed), [[Prefill and Decode|Memory Bandwidth Bound]] (proposed), [[Quantization]] (proposed)
- Related sources: [[Apple 2024 - MacBook Pro 14-inch M4 tech specs]], [[MLX README (ml-explore)]], [[EXO Labs 2025 - NVIDIA DGX Spark and Mac Studio, disaggregated inference]], [[Rajesh 2025 - Local LLM inference on Apple Silicon, MLX vs MLC vs Ollama vs llama.cpp (arXiv 2511.05502)]], [[Gunter 2024 - Apple Intelligence Foundation Language Models]]
