---
type: source
author: "Level1Techs forum users (thread started 2026)"
date: 2026-06-09
venue: "Level1Techs community forum thread (retrieved 2026-10-11)"
url: "https://forum.level1techs.com/t/asrock-intel-b60-24-gb-for-local-ai/251192"
tags: [source, forum, anecdotal, hardware, intel, arc-pro-b60, discrete-gpu, vram, bandwidth, software-stack, local-inference]
---
# Level1Techs – ASRock Intel Arc Pro B60 24 GB for Local AI (forum thread)

**Raw file**: `raw/local_inference/Level1Techs - ASRock Intel Arc Pro B60 24 GB for local AI_ingested.md`

## Overview
A **forum discussion**, not an article. A home user wants a cheap **24 GB** card (ASRock **Intel Arc Pro B60**) as an Ollama/Vulkan backend on Linux (CachyOS) for hobby agents ("Openclaw/Hermes": tool use, web scraping, email triage). Complex tasks would still go to OpenAI/Anthropic. Other users argue that a used RTX 3090 is much faster and that Intel's AI software stack is immature. Usernames are not preserved in the extraction, and the posts run together. Everything here is **anecdotal and unverified**.

## Key Insights (claims made by forum users)
- **Prices (Australia/Europe, mid-2026):**
  - Arc Pro B60 24 GB "under 1000 AUD / 640 euro"; about 650 AUD after the poster's tax deduction.
  - Used RTX 3090 about 1,500 AUD ("1.5x the price for a 5 year old card").
  - Used RX 6900 XT 650–750 AUD on eBay.
  - The poster also considers a Mac Studio with 96 GB and a 32 GB Mac mini ("expensive and hard to get right now").
- **Bandwidth argument:** "the memory bandwidth of the 3090 is 950 GB/s and the B60 is only 450 GB/s, the 3090 is going to give you 2–3 times the performance". Another user: "three to four times the speed of the B60 in AI workloads" (no models or numbers given). The bandwidth values are forum claims, not checked against vendor pages here.
- **Software-stack criticism (one experienced user):**
  - Intel directly supports only vLLM, through its own distribution (llm-scaler) that lags mainline by months.
  - Choosing between SYCL, Vulkan and OpenVINO is unpredictable per model.
  - llama.cpp fixes arrive in the order "CPU/CUDA first, then ROCm, then Vulkan/AMD, then Vulkan/Intel, then SYCL".
  - Intel abandoned Alchemist owners (IPEX-LLM) when Battlemage launched, so Battlemage support should be expected to end when Celestial ships.
  - Verdict: "fine as a hobbyist card … not ready for a serious work or production environment."
- **Arc Pro B70 owner:** "pretty decent for the price", best results with Vulkan on a model named "Qwen 3.6 27b" (name not verified). They value **SR-IOV** (partitioning one GPU across VMs) and report a multi-monitor driver bug.
- **Capacity rationale from the poster:** "people aren't aiming good local models at 20 GB, they're aiming to fit them in 24 GB because that's the memory size of the 3090". Target: 16–30B models, heavily quantised, with a 64k–128k context.
- A suggestion to run llama.cpp directly ("router mode") instead of Ollama for more tuning and speed.

## Relevance to GroundOne
- **Bandwidth sets decode speed even in hobbyist reasoning.** The forum's own argument (950 vs 450 GB/s, about 2–3x) is the decode-bound rule of thumb the thesis relies on ([[Prefill and Decode]]). It is informal support only; do not cite the numbers.
- **Software maturity is part of locality.** The thread is a concrete example that local inference depends on the vendor's software stack as much as on the silicon. GroundOne is MLX-only, and porting it to Intel or AMD would face exactly these runtime-fragmentation issues ([[Apple Silicon and MLX]], [[Local Inference Hardware|Local Inference Runtimes]]).
- **Hybrid local/cloud use is the norm.** The poster keeps "anything super complex" in the cloud and wants local models for cheap high-volume tasks such as classification and triage. This is the niche a System One fits: a cheap, local, single-pass decision ([[System One Models]]).
- **Capacity class not relevant to the verifier.** 24 GB targets a 16–30B generator. GroundOne needs under 6 GB.

## Links
- Concepts: [[On-Device Inference]], [[Prefill and Decode]], [[Apple Silicon and MLX]], [[System One Models]], [[Local Inference Hardware]] (proposed), [[Local Inference Hardware|Local Inference Runtimes]] (proposed), [[Prefill and Decode|Memory Bandwidth Bound]] (proposed), [[Quantization]] (proposed)
- Related sources: [[Corelab - Best GPU for local LLMs, VRAM tier list]], [[llama.cpp README (ggml-org)]], [[Rajesh 2025 - Local LLM inference on Apple Silicon, MLX vs MLC vs Ollama vs llama.cpp (arXiv 2511.05502)]], [[Davies Meyer - Mac mini M4 Pro for local AI inference]]
