---
type: source
author: "Varun Rajesh, Om Jodhpurkar, Pooja Anbuselvan, Mantinder Singh, Ashok Jallepali, Shantanu Godbole, Pradeep Kumar Sharma, Hritvik Shrivastava (Persistent Systems)"
date: 2025-11
venue: "arXiv preprint 2511.05502 (not peer-reviewed)"
url: "https://arxiv.org/abs/2511.05502"
tags: [source, paper, preprint, apple-silicon, mlx, mlc-llm, llama-cpp, ollama, pytorch-mps, runtime-benchmark, ttft, kv-cache, quantization, local-inference]
---
# Rajesh 2025 – Production-Grade Local LLM Inference on Apple Silicon: A Comparative Study of MLX, MLC-LLM, Ollama, llama.cpp, and PyTorch MPS

**Raw file**: `raw/local_inference/Rajesh 2025 - Local LLM inference on Apple Silicon, MLX vs MLC vs Ollama vs llama.cpp (arXiv 2511.05502)_ingested.pdf`

*(The real title on page 1 also includes PyTorch MPS; the filename shortens it.)*

## Overview
An industry preprint (Persistent Systems, 12 pages) comparing five local LLM runtimes on one **Mac Studio M2 Ultra (24 CPU / 76 GPU cores, 192 GB)**: **MLX, MLC-LLM, llama.cpp, Ollama, PyTorch MPS**. It uses Qwen-2.5-Coder 3B (primary) and Qwen-2.5-7B-Instruct, with prompts from 1k to 100k tokens. It measures TTFT, decode throughput, latency percentiles, cold start, KV/prompt caching, quantisation support, streaming, concurrency, API surface and deployment effort. Conclusion: **MLX has the highest sustained decode throughput and the most stable per-token latency**, and MLC-LLM has lower TTFT at moderate prompt lengths (≤16k) and better serving features. MLX is recommended as the Apple-first default, with MLC as a complement for very long contexts.

## Key Insights
**Setup:** MLX v0.26, MLC-LLM commit 3d42929, llama.cpp b5963, Ollama v0.10.1, PyTorch 2.7.1 (MPS). FP16/bf16 baselines plus int8/int4 variants. Each run done N = 10 times; cold and warm starts separated; Spotlight, Time Machine and iCloud disabled.

| Runtime | Sustained decode (text) | Latency | Cold start | Long context (100k) |
| --- | --- | --- | --- | --- |
| **MLX** | **~230 tok/s** | 5–7 ms median, ~12 ms P99 per token; elsewhere "11–12 ms" inter-token | ~31 s | rotating KV (default 4k); ~40–50 GB at 100k |
| MLC-LLM | ~190 tok/s (~17% below MLX) | ~13 ms P99; lower TTFT at ≤16k | ~11 s (after one-time TVM compile of 20–30 min) | paged KV; ~500 tok/s prefill, ~190 tok/s decode at 100k; 128k in ~3 min; 70–85 GB for two overlapping 128k runs |
| llama.cpp | ~150 tok/s (short context only) | TTFT = full prefill | <0.5 s (cached GGUF) | collapses to ~1.2 tok/s at 32k |
| Ollama | 20–40 tok/s (figure: 35) | 9–14 ms inter-token streaming | ~0.6 s after service start | ~56 GB at 100k; prefix reuse: ~23% lower latency, ~80% cache hits |
| PyTorch MPS | ~7–9 tok/s (figure: 20) | — | ~3 s (small models) | 4 GB tensor cap, out-of-memory beyond ~2k tokens |

- **Quantisation:** MLC AWQ 4-bit for the 3B model used about 1.6 GB and gave about 210 tok/s vs about 190 tok/s in FP16. "Robust quantisation (especially 4-bit) reduces memory footprint by 2–3x." MLX supports mixed 3/4/6/8-bit.
- **No chunked prefill:** neither MLX nor MLC implements vLLM-style chunked prefill, so TTFT rises with input length.
- **External ceiling:** NVIDIA A100 + vLLM is cited as "~5–10x higher" throughput. The authors say this is contextual, not measured head-to-head.
- **Privacy:** all five runtimes run locally with no telemetry once the models are downloaded.

**Quality flags.**
1. **Internal inconsistencies:**
   - MLX latency is "5–7 ms median" in one place and "consistently 11–12 ms" in another.
   - PyTorch MPS is "~7–9 tok/s" in the text but **20** in Figure 1.
   - Ollama TTFT is ">50 s at 100k" in one place but "100k → 2.1 s" in another.
   - Ollama is called "an order of magnitude slower" than MLX, but the numbers give about 6x.
2. The headline **Figure 1 does not state the model (3B or 7B), the precision or the prompt length**, so the about 230 tok/s cannot be checked against a bandwidth bound.
3. Figure 3 (peak memory) is labelled **"illustrative"**.
4. **Every reference is numbered [20]**, a sign of an unedited draft.
5. "Appendix A" is announced but absent from the 12 pages.
6. It says MLX integrates with "Core ML" and the "Neural Engine". The MLX documentation describes CPU/GPU execution ([[MLX README (ml-explore)]]), so this claim is unsupported.
7. One machine, one model family, and an industry affiliation; not peer-reviewed.

## Relevance to GroundOne
- **Supports the runtime choice.** It is the only systematic comparison in the vault of Apple Silicon runtimes. MLX's top decode throughput and stable latency support building GroundOne on MLX ([[Apple Silicon and MLX]]). Given the quality flags, cite it for the qualitative ranking, not for exact numbers.
- **The metric GroundOne cares about is TTFT, where MLX is not the winner.** A System One's whole latency is one prefill (TTFT with zero decode). The paper finds MLC-LLM often has lower TTFT than MLX for prompts up to 16k. This is an honest caveat: GroundOne's latency might drop further on another runtime. It has not been tested and is not needed for the thesis claims, which compare systems on the same MLX stack.
- **Cold start matters for serving.** MLX loads in about 31 s, which justifies GroundOne's long-lived engine worker that keeps the model warm ([[GroundOne]]).
- **Long-context regime does not apply.** Its 32k–128k results concern chat history growth. GroundOne's inputs are a document plus an answer of hundreds to a few thousand tokens.
- **Different hardware class.** The M2 Ultra (192 GB) is a dedicated desktop, not the 16 GB M4 laptop, and the paper itself warns that results may differ on M1/M4.

## Links
- Concepts: [[Apple Silicon and MLX]], [[Prefill and Decode]], [[KV Cache]], [[On-Device Inference]], [[Local Inference Hardware|Local Inference Runtimes]] (proposed), [[Quantization]] (proposed), [[Local Inference Hardware]] (proposed)
- Related sources: [[MLX README (ml-explore)]], [[llama.cpp README (ggml-org)]], [[Kwon 2023 - PagedAttention vLLM]], [[Apple ML Research 2025 - Exploring LLMs with MLX and the neural accelerators in the M5 GPU]], [[Apple 2025 - Mac Studio (2025) tech specs]], [[Hardware Corner 2025 - How fast is the AI Max+ 395 for LLM inference]]
