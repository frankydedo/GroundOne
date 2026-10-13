---
type: source
author: "Salvatore Sanfilippo (antirez) and contributors"
date: 2026
venue: "GitHub repository README, antirez/ds4 (MIT; repository created 2026-05-06; retrieved 2026-10-13)"
url: "https://github.com/antirez/ds4"
tags: [source, inference-engine, local-inference, deepseek, moe, kv-cache, ssd-streaming, metal, cuda, rocm]
---
# antirez 2026 – DwarfStar (ds4): a local inference engine for a few large open models

**Raw file**: `raw/local_inference/antirez 2026 - ds4, DeepSeek 4 Flash and PRO local inference engine (GitHub README)_ingested.md`

## Overview
DwarfStar (`ds4`) is a small native inference engine, deliberately narrow ("not a general GGUF runner"), optimised first for DeepSeek V4 Flash and also for DeepSeek V4.1 Flash, V4 PRO, GLM 5.2/5.3, GLM 5.3 Flash and Qwen3.8 Flash Next. Model support is "intentionally opportunistic": it follows the best open weights for 128 GB laptops and 256/512 GB workstations. Self-described as beta, developed "with strong assistance from AI coding agents", and indebted to llama.cpp/GGML (parts of quant layouts and kernels retained under MIT).

## Key Insights
- **Hardware targets**: Metal on Macs with 96 GB or more (primary); NVIDIA CUDA with the DGX Spark as main goal, multi-GPU Ada Lovelace (eight L40S: about 126 tok/s aggregate generation with 16 sessions); ROCm on Strix Halo (Framework Desktop).
- **SSD streaming**: smaller machines stream weights from SSD; also needed for full GLM 5.x on 128 GB systems. Qwen3.8's GGUF keeps 95.37 GiB of BF16 n-gram tables on disk, read directly rather than loaded into RAM.
- **Disk KV cache**: sessions saved in `~/.ds4/kvcache`; "compatible local KV snapshots avoid rebuilding the prompt" (no repeated prefill). The README warns that saved conversations may contain private information.
- **Distributed**: two 128 GB Macs over RDMA with tensor parallelism; pipeline parallelism across machines.
- **Speculative decoding** (MTP heads, DSpark) is opt-in; "not every workload benefits".
- **Motivations** listed by the author: capable open-weight models now fit high-end personal machines; routed experts tolerate aggressive quantisation; compressed KV caches and fast SSDs make long contexts practical; specialised engines for a few models.
- Speed figures are in the repository's benchmark pages (M5 Max 128 GB sweep); not extracted here.

## Relevance to GroundOne
- Evidence of the **specialised-engine trend** in local inference: give up generality to push the memory wall (Ch. 2 §2.5.2).
- The **disk KV cache attacks repeated prefill**, the same cost GroundOne avoids by reading document and answer once for all K decisions ([[Prefill and Decode]], [[KV Cache]]).
- Targets the same hardware classes compared in Ch. 2 (Mac, DGX Spark, Strix Halo): [[Local Inference Hardware]].

## Links
- Concepts: [[On-Device Inference]], [[Local Inference Hardware]], [[Prefill and Decode]], [[KV Cache]], [[Mixture of Experts]], [[Quantization]]
- Related: [[JustVugg 2026 - Colibri, frontier MoE models with experts streamed from disk (GitHub README)]], [[Alizadeh 2024 - LLM in a flash]], [[llama.cpp README (ggml-org)]]
