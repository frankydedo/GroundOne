---
title: "Presenc 2026 - Local LLM tokens-per-second benchmarks"
url: https://presenc.ai/research/local-llm-tokens-per-second-benchmarks-2026
published: 2026-10-02
accessed: 2026-10-11
extracted_with: trafilatura 2.3.1
---

## Why Local LLM Throughput Matters in 2026

Local LLM inference moved from hobbyist territory to production-relevant once three things lined up: NVIDIA shipped DGX Spark, Apple put up to 128GB of unified memory in the M5 Max Mac Studio and up to 512GB in the M5 Ultra, and open-weight models such as Qwen 3, Llama 4 and gpt-oss became good enough for common tasks. Tokens per second (tps) is the number that decides whether a deployment is interactive (above about 30 tps for chat), batch-only (8 to 30 tps), or impractical. This page consolidates published, attributable measurements. It was revised on October 2, 2026 to replace earlier estimated bands with measured figures, several of which were much lower for DGX Spark on dense models.

## Key Findings

1. On small models the RTX 5090 is the fastest single device. The llama.cpp scoreboard records 290 to 300 tps generation on Llama 2 7B Q4\_0, against about 120 tps for the M5 Max. Under Ollama the 5090 runs Llama 3.1 8B at about 150 tps and DGX Spark runs it at 38 tps.
2. DGX Spark is slow on large dense models. Ollama measured Llama 3.1 70B at 4.4 tps and Qwen3 32B at 9.4 tps. Its 273 GB/s memory bandwidth is the limit.
3. DGX Spark is fast on large sparse models. The llama.cpp community measured gpt-oss 120B, a mixture-of-experts model, at 60.6 tps at empty context and 40.6 tps at 32K context. Only a fraction of the weights is read per token, so bandwidth matters less.
4. The RTX 5090 cannot hold a 70B model at Q4, which is about 43GB, in its 32GB of VRAM. We found no reproducible single-card measurement with CPU offload. Two cards run Llama 3.3 70B at about 27 tps.
5. Apple's advantage is memory bandwidth: 460 or 614 GB/s on M5 Max and 1.2 TB/s on M5 Ultra. That favours generation on dense models that do not fit in a 32GB card.

## Measured Generation Speed by Hardware and Model

Each cell is one published measurement, in tokens per second for generation. Rows use different backends and quantisations, so compare within a row, not across rows.

| Model and test | RTX 5090 (32GB) | DGX Spark (128GB) | Mac Studio M5 Max | Mac Studio M5 Ultra | Measured by | 
|---|---|---|---|---|---|
| Llama 2 7B Q4\_0, llama.cpp | 290 to 300 | not listed | 119.9 | not listed | llama.cpp scoreboard | 
| Llama 3.1 8B Q4\_K\_M, Ollama | 150.0 | 38.0 | not published | not published | Database Mart (5090), Ollama (Spark) | 
| gpt-oss 20B, Ollama | 205 | 49.7 | not published | not published | LMSYS | 
| gpt-oss 20B, llama.cpp | not listed | 60.9 | not published | not published | llama.cpp discussion | 
| Gemma 3 27B Q4, Ollama | 47.3 | 10.8 | not published | not published | Database Mart (5090), Ollama (Spark) | 
| Qwen3.8-27B | 59 | not published | 65 to 69 (secondary, MLX) | 48 | MacStories; Context Studios for M5 Max | 
| 32B class, Ollama | 57.2 (QwQ 32B) | 9.4 (Qwen3 32B) | not published | not published | Database Mart (5090), Ollama (Spark) | 
| Llama 3.1 70B, Ollama | does not fit on one card | 4.4 | not published | 40 to 52 (early community, unverified) | Ollama; PromptQuorum for M5 Ultra | 
| gpt-oss 120B, llama.cpp | does not fit | 60.6 (40.6 at 32K context) | not published | not published | llama.cpp discussion | 

"Not published" means we found no attributable measurement, not that the device cannot run the model. Device-specific pages carry more detail: [RTX 5090](https://presenc.ai/research/rtx-5090-local-llm-benchmarks-2026), [Mac Studio M5 Ultra](https://presenc.ai/research/mac-studio-m5-ultra-local-llm-benchmarks-2026), [AMD Strix Halo](https://presenc.ai/research/amd-strix-halo-local-llm-benchmarks-2026), and [NVIDIA RTX Spark](https://presenc.ai/research/nvidia-rtx-spark-local-llm-benchmarks-2026), which has no independent benchmark yet.

## What Is a Good Tokens-per-Second Number

Above about 30 tps feels interactive for chat. Between 8 and 30 tps is usable for batch work and patient users. Below about 8 tps is impractical for anything a person waits on. By that measure the RTX 5090 is interactive on everything that fits in 32GB, DGX Spark is interactive on small models and on sparse models up to 120B, and DGX Spark is not interactive on dense 32B or 70B models.

## Prompt Processing vs Generation

Two numbers matter. Prompt processing (prefill) is dominated by compute. Generation (decode) is dominated by memory bandwidth. On Llama 2 7B the llama.cpp scoreboard shows the RTX 5090 processing prompts at about 14,000 to 15,000 tps and the M5 Max at 3,220 tps. DGX Spark processes Llama 3.1 8B prompts at 7,614 tps under Ollama and gpt-oss 120B prompts at about 1,956 tps under llama.cpp. For agent workloads with large context windows, prefill is the bottleneck and CUDA hardware keeps an advantage.

## Reasoning Models and Thinking Tokens

Reasoning models emit long internal traces before the visible answer, so wall-clock time is set by generation speed over the whole trace. For a 32B-class reasoning model that emits 2,000 thinking tokens and a 200-token answer, the measured speeds above imply about 38 seconds on an RTX 5090 (57.2 tps on QwQ 32B) and about 234 seconds on DGX Spark (9.4 tps on Qwen3 32B). These are arithmetic from the measured rates, not separate measurements.

## Brand Visibility Implications

Three implications for brand teams. First, interactive speeds on 7B to 32B models make local LLMs practical for agents and RAG, so a real share of brand queries is answered by a model that never calls a cloud API. Second, large sparse open-weight models such as gpt-oss 120B now run at usable speed on a desktop device, which widens the set of models whose training-time picture of a brand reaches users directly. Third, local models answer from what they learned in training, with no retrieval unless the user adds it, so what the open-weight model already knows about a brand is what the user gets. See [the local LLM brand visibility blind spot page](https://presenc.ai/research/local-llm-brand-visibility-blind-spot-2026) for what this means operationally.

## Methodology

Every figure is a published measurement attributed to who ran it: the llama.cpp community scoreboards for [CUDA](https://github.com/ggml-org/llama.cpp/discussions/15013) and [Apple Silicon](https://github.com/ggml-org/llama.cpp/discussions/4167), the [llama.cpp DGX Spark thread](https://github.com/ggml-org/llama.cpp/discussions/16578), [Ollama's DGX Spark results](https://ollama.com/blog/nvidia-spark-performance), [LMSYS](https://www.lmsys.org/blog/2025-10-13-nvidia-dgx-spark/), [Database Mart's RTX 5090 runs](https://www.databasemart.com/blog/ollama-gpu-benchmark-rtx5090), and the [MacStories M5 Ultra review](https://www.macstories.net/stories/m5-ultra-mac-studio-review-the-dream-mac-for-local-ai-agents/). Two cells come from single secondary sources and are labelled. Results vary with backend, quantisation, context length and software version: DGX Spark figures in particular have risen with software updates since October 2025. None of these are Presenc AI measurements. Last update: October 2026.

## How Presenc AI Helps

Presenc AI tracks how AI models describe and recommend your brand, including the open-weight models that people run locally. Because a local model answers from [training data](https://presenc.ai/glossary/training-data), measuring what those models already say about you is the practical way to see this surface.
