---
type: source
author: "Presenc AI (no named author); figures compiled from third-party measurements"
date: 2026-10-02
venue: "Presenc AI research page, brand-visibility vendor blog (revised 2026-10-02; retrieved 2026-10-11)"
url: "https://presenc.ai/research/local-llm-tokens-per-second-benchmarks-2026"
tags: [source, blog, benchmark-compilation, local-inference, tokens-per-second, prefill, decode, memory-bandwidth, apple-silicon, dgx-spark, rtx-5090]
---
# Presenc 2026 – Local LLM Tokens-per-Second Benchmarks

**Raw file**: `raw/local_inference/Presenc 2026 - Local LLM tokens-per-second benchmarks_ingested.md`

## Overview
A compilation of **published generation and prompt-processing speeds** for local LLM inference on three classes of desktop hardware: NVIDIA RTX 5090 (32 GB), NVIDIA DGX Spark (128 GB) and Apple Mac Studio M5 Max / M5 Ultra. Each table cell is attributed to whoever measured it (llama.cpp community scoreboards, Ollama, LMSYS, Database Mart, MacStories, ...). The page states that "None of these are Presenc AI measurements". It was revised on 2026-10-02 "to replace earlier estimated bands with measured figures, several of which were much lower for DGX Spark on dense models". The publisher is the same brand-visibility vendor as [[Presenc 2026 - State of the llama.cpp ecosystem]], with a marketing section at the end. The content is nonetheless much better sourced than that page.

## Key Insights
1. **Generation (decode) speeds (table; compare within a row only, since backends and quantisations differ).**
   - Llama 2 7B Q4_0, llama.cpp: RTX 5090 **290–300 tps**, M5 Max **119.9 tps**.
   - Llama 3.1 8B Q4_K_M, Ollama: RTX 5090 150 tps, DGX Spark 38 tps.
   - 32B class, Ollama: RTX 5090 57.2 tps (QwQ 32B), DGX Spark 9.4 tps (Qwen3 32B).
   - Llama 3.1 70B, Ollama: DGX Spark 4.4 tps; M5 Ultra "40 to 52 (early community, unverified)"; it does not fit on one RTX 5090 (Q4 ≈ 43 GB > 32 GB VRAM). Two RTX 5090 cards run Llama 3.3 70B at about 27 tps.
   - gpt-oss 120B (MoE), llama.cpp: DGX Spark **60.6 tps** at empty context, 40.6 tps at 32K context.
2. **Bandwidth explains decode.** DGX Spark is slow on large dense models because of its **273 GB/s** memory bandwidth, and fast on sparse MoE models because only a fraction of the weights is read per token. Apple's advantage is bandwidth: "460 or 614 GB/s on M5 Max and 1.2 TB/s on M5 Ultra" (stated without an Apple citation on this page).
3. **Prefill vs decode (section "Prompt Processing vs Generation").** "Prompt processing (prefill) is dominated by compute. Generation (decode) is dominated by memory bandwidth." On Llama 2 7B the RTX 5090 processes prompts at about **14,000–15,000 tps** against **3,220 tps** for the M5 Max. DGX Spark reaches 7,614 tps on Llama 3.1 8B (Ollama) and about 1,956 tps on gpt-oss 120B (llama.cpp). "For agent workloads with large context windows, prefill is the bottleneck and CUDA hardware keeps an advantage."
4. **Interactivity thresholds.** Above about 30 tps "feels interactive" for chat, 8–30 tps is usable for batch work, and below about 8 tps is impractical. These are rules of thumb with no cited source.
5. **Cost of reasoning traces.** A 32B reasoning model that emits 2,000 thinking tokens plus a 200-token answer would take about **38 s** on an RTX 5090 (at 57.2 tps) and about **234 s** on DGX Spark (at 9.4 tps). The page labels these as "arithmetic from the measured rates, not separate measurements".
6. **Quality caveats.** Two cells come from single secondary sources (labelled). DGX Spark figures "have risen with software updates since October 2025". One row is labelled "Qwen3.8-27B", which looks like a typo or an unverified model name. The M5 Ultra 70B figure is explicitly "unverified". The thesis machine (base M4, 120 GB/s) is not in the table.

## Relevance to GroundOne
- **The prefill/decode split is the core argument.** The page gives independent, attributed numbers for the regime distinction GroundOne relies on ([[Prefill and Decode]]): decode is memory-bound and prefill is compute-bound. GroundOne generates **zero tokens**, so the interactivity thresholds in tokens per second (insight 4) do not apply to it. Its latency is set by one prefill, i.e. by prompt-processing throughput.
- **An honest caveat for the locality pillar.** Insight 3 shows that Apple Silicon is relatively weakest exactly where GroundOne spends its time: prefill (3,220 vs 14,000–15,000 tps on Llama 2 7B, M5 Max vs RTX 5090). The base M4 has lower bandwidth (120 GB/s, [[Apple 2024 - MacBook Pro 14-inch M4 tech specs]]) and fewer GPU cores than the M5 Max. The thesis should therefore not claim the Mac is a fast verifier platform in absolute terms. The defensible claim is that the verifier fits and runs within the memory and time budget of a 16 GB laptop ([[On-Device Inference]], [[Apple Silicon and MLX]]).
- **Generated tokens dominate the cost of generative judges.** Insight 5 is a clean third-party illustration of why reasoning or verbose judges are expensive on local hardware: wall-clock time scales with the number of generated tokens, which a System One avoids ([[System One Models]], [[LLM-as-a-Judge]], [[Energy of LLM Inference]]).
- Use the numbers only as context. Rows mix backends and quantisations, and the page itself warns against comparing across rows.

## Links
- Concepts: [[Prefill and Decode]], [[On-Device Inference]], [[Apple Silicon and MLX]], [[Energy of LLM Inference]], [[System One Models]], [[Mixture of Experts]], [[Quantization]] (proposed)
- Related sources: [[Presenc 2026 - State of the llama.cpp ecosystem]], [[Apple 2024 - MacBook Pro 14-inch M4 tech specs]], [[llama.cpp README (ggml-org)]], [[Alizadeh 2024 - LLM in a flash]]
