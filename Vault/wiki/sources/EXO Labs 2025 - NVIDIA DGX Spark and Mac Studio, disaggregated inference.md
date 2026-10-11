---
type: source
author: "EXO Labs"
date: 2025
venue: "EXO Labs blog (publication date not given on the page; retrieved 2026-10-11)"
url: "https://blog.exolabs.net/nvidia-dgx-spark/"
tags: [source, blog, vendor-measurement, hardware, dgx-spark, mac-studio, m3-ultra, prefill, decode, disaggregated-inference, kv-cache]
---
# EXO Labs 2025 – NVIDIA DGX Spark and Mac Studio: Disaggregated Prefill and Decode

**Raw file**: `raw/local_inference/EXO Labs 2025 - NVIDIA DGX Spark and Mac Studio, disaggregated inference_ingested.md`

## Overview
A blog post by EXO Labs, which sells distributed-inference software. With early access to two DGX Spark units, they run **prefill on a DGX Spark** (compute-rich) and **decode on an M3 Ultra Mac Studio** (bandwidth-rich) for the same request. The KV cache is streamed **layer by layer** over 10 GbE so that the transfer overlaps with the computation of later layers. The post is the clearest consumer-hardware illustration of the prefill/decode split: one device wins prefill by 3.8x, the other wins decode by 3.4x.

## Key Insights
1. **Hardware as described by EXO** (not vendor pages): DGX Spark "~100 TFLOPs of FP16", 128 GB at 273 GB/s; Mac Studio M3 Ultra "512GB of unified memory at 819 GB/s", GPU "~26 TFLOPs of FP16". Summary: "**The DGX Spark has 4x the compute, the Mac Studio has 3x the memory bandwidth.**" The 273 and 819 GB/s values match the vendor pages ([[NVIDIA - DGX Spark hardware overview]], [[Apple 2025 - Mac Studio (2025) tech specs]]). The TFLOPS values are EXO's and are not stated on either vendor page.
2. **Phase analysis.** Prefill builds the KV cache. For long prompts its compute grows as Θ(s²) while data moved grows as Θ(s) (with FlashAttention), so arithmetic intensity grows with prompt length: **prefill is compute-bound**. Decode does vector-matrix products: **decode is memory-bound**. TTFT is set by prefill and tokens/s by decode.
3. **Hiding the KV transfer.** Overlap requires t_send < t_comp. With P = 100 TFLOPS and B = 10 Gb/s, P/B = 10,000, giving a minimum prompt length s > 10,000·q/K, where q is the KV bit-width and K = c1/c2 depends on attention design: K = 2 (MHA, Llama-2 7B), 8 (GQA, Llama-3 8B), 16 (Llama-3 70B, Qwen-2.5 72B). With 8-bit KV: s > 5k (K = 16), > 10k (K = 8), > 40k (K = 2) tokens.
4. **Measurement: Llama-3.1 8B, FP16, 8,192-token prompt, 32 generated tokens.**

| Configuration | Prefill | Generation | Total | Speedup |
| --- | --- | --- | --- | --- |
| DGX Spark | 1.47 s | 2.87 s | 4.34 s | 1.9x |
| M3 Ultra Mac Studio | 5.57 s | 0.85 s | 6.42 s | 1.0x (baseline) |
| DGX Spark + M3 Ultra | 1.47 s | 0.85 s | 2.32 s | 2.8x |

   Derived rates (arithmetic): prefill about **5,570 tok/s (Spark)** vs about **1,470 tok/s (M3 Ultra)**; decode about **11 tok/s (Spark)** vs about **38 tok/s (M3 Ultra)**. With 16 GB of FP16 weights, decode reads about 180 GB/s on the Spark (about 65% of 273 GB/s) and about 600 GB/s on the M3 Ultra (about 73% of 819 GB/s). Both are consistent with a bandwidth-bound decode.

**Caveats.** The authors sell the software being shown. The results come from early-access units and a single configuration (one model, one prompt length), with no repetitions, variance or software versions reported. The publication date is not on the page.

## Relevance to GroundOne
- **The thesis argument in one table.** The post shows on real consumer hardware that the prefill device and the decode device are chosen by different specs (compute vs bandwidth). A System One's whole workload is prefill: GroundOne's verdict is one forward pass with no decode. On a compute-rich box such as the Spark it would gain most of the 3.8x prefill advantage, and it has no use for the M3 Ultra's decode advantage ([[Prefill and Decode]], [[System One Models]]).
- **Reverse view for judges.** A generative judge that writes a rationale pays the decode phase, which is the bandwidth-bound part. On the thesis M4 (120 GB/s, [[Apple 2024 - MacBook Pro 14-inch M4 tech specs]]) this is the expensive phase, which is why GroundOne's latency advantage over verbose judges grows with output length.
- **Caution on the Θ(s²) argument.** EXO's compute-bound argument is made for **long** contexts (thousands of tokens). GroundOne's prompts are hundreds of tokens (for example S ≈ 637). There, prefill is efficient mainly because many tokens share each weight read (matrix-matrix rather than vector-matrix), not because of the quadratic attention term. The thesis should phrase it that way.
- **Does not apply:** the disaggregation itself (two machines, a 10 GbE link, KV streaming) is the opposite of the thesis's single-laptop locality setting. It only works for prompts above about 5k–40k tokens anyway (item 3).

## Links
- Concepts: [[Prefill and Decode]], [[KV Cache]], [[On-Device Inference]], [[Apple Silicon and MLX]], [[Local Inference Hardware]] (proposed), [[Prefill and Decode|Memory Bandwidth Bound]] (proposed), [[Local Inference Hardware|Disaggregated Inference]] (proposed)
- Related sources: [[NVIDIA - DGX Spark hardware overview]], [[Apple 2025 - Mac Studio (2025) tech specs]], [[Patel 2024 - Splitwise (prefill vs decode phases)]], [[Pope 2023 - Efficiently Scaling Transformer Inference]], [[Apple ML Research 2025 - Exploring LLMs with MLX and the neural accelerators in the M5 GPU]]
