---
type: source
author: "JustVugg and contributors"
date: 2026
venue: "GitHub repository README, JustVugg/colibri (Apache-2.0; repository created 2026-07-01; v2.0.0; retrieved 2026-10-13)"
url: "https://github.com/JustVugg/colibri"
tags: [source, inference-engine, local-inference, moe, ssd-streaming, expert-offloading, system-one, decision-model, cpu]
---
# JustVugg 2026 – colibri: frontier MoE models with experts streamed from disk

**Raw file**: `raw/local_inference/JustVugg 2026 - Colibri, frontier MoE models with experts streamed from disk (GitHub README)_ingested.md`

## Overview
colibri ("tiny engine, immense model") is a pure-C engine, one file per model family, no GPU required, that runs very large mixture-of-experts models on ordinary machines: it keeps the always-active part in RAM and streams the experts from disk when the router asks for them. Thirteen engines (GLM-5.2/5.3, Kimi K3, DeepSeek V4/V4.1 Flash, MiMo, Qwen3.6/3.8, OLMoE, Qwen-Image) plus **decision models**. OpenAI- and Anthropic-compatible local server, plus a Jev-compatible `/v1/systemone` endpoint.

## Key Insights
- **Expert tiers**: VRAM, RAM and NVMe; "placement only ever decides speed" (router decisions and weight precision are identical wherever an expert is). Per-layer LRU cache plus a hot set learned from the user's own usage; one `pread` per expert; router look-ahead prefetch (GLM-5.2 routing 71.6 % predictable one layer ahead); two NVMe drives +37.5 % decode.
- **Speeds (self-reported)**: GLM-5.2 (744B) 0.05–0.1 tok/s cold on a 25 GB laptop, 1.83 tok/s on a 128 GB Ryzen AI Max+ 395, 9.0–9.2 on 6× RTX 5090; Kimi K3 (2.8T) about 9.4 s per token with experts read at 6.3 GB/s; Qwen3.6-35B-A3B 6.0 tok/s CPU, 9.9 Vulkan iGPU, 30.0 CUDA; OLMoE 22–23 tok/s CPU. The README itself: "This is not fast."
- **System One section**: `/v1/systemone` answers typed questions with a probability per option and a confidence; "nothing is generated, so no answer can fall outside your list". Any chat model it runs can answer by scoring; "four questions about one document came back 5.7x faster than generating the same answers on the same CPU box" (Qwen3.6). Native decision models: **Laya** (0.85 GB; 219 ms for one question, 882 ms for three), **GLiNER2.5-Decide** (294 / 897 ms), **Clef** (Qwen3.8-27B with a decision head; 20.4 s per request in int8).
- Request and reply match TypeSafe's Jev ("Switching from Jev").

## Relevance to GroundOne
- **Memory capacity turned into a bandwidth limit**: SSD streaming (a few GB/s) makes decoding far slower, exactly as the decode floor predicts ([[Local Inference Hardware]], [[Prefill and Decode]]); same idea as [[Alizadeh 2024 - LLM in a flash]], applied to MoE ([[Mixture of Experts]]).
- **Independent echo of the System One speed-up**: 5.7× for reading vs generating four answers about one document (self-reported, different model and hardware); GroundOne measures about 2× (terse) and 6× (verbose) at K ≥ 14 ([[GroundOne Results]]). Cited in Ch. 2 §2.5.2 as a project-reported figure, not verified.
- The Jev-compatible `/v1/systemone` endpoint is the same interface GroundOne's `compat.py` implements: GroundOne could in principle be served by, or compared through, the same client ([[System One Models]], [[Decision-Model Landscape (Hugging Face, 2026)]]).
- Note the inconsistent latency figures across sources (Laya 219 ms here vs 19–43 ms on Apple MPS elsewhere): different hardware (CPU) and request shapes.

## Links
- Concepts: [[On-Device Inference]], [[Local Inference Hardware]], [[Mixture of Experts]], [[System One Models]], [[Laya]], [[Prefill and Decode]]
- Related: [[antirez 2026 - ds4, DeepSeek 4 Flash and PRO local inference engine (GitHub README)]], [[ggml-org 2026 - llama.cpp PR 29818 systemone API]], [[Cloudflare 2026 - Clef model card]]
