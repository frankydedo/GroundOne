---
type: source
author: "Davies Meyer (AI solutions / marketing agency blog, author not named)"
date: 2026-03-20
venue: "ai-solutions.daviesmeyer.com company blog (retrieved 2026-10-11)"
url: "https://ai-solutions.daviesmeyer.com/en/blog/mac-mini-m4-pro-lokale-ki-inferenz"
tags: [source, blog, low-quality, marketing, hardware, apple-silicon, mac-mini, m4-pro, unified-memory, price, local-inference]
---
# Davies Meyer 2026 – Mac Mini M4 Pro for Local AI: Which Models Run on 64 GB

**Raw file**: `raw/local_inference/Davies Meyer - Mac mini M4 Pro for local AI inference_ingested.md`

## Overview
A blog post by an agency that sells AI solutions. It is aimed at marketing teams and small companies and argues that the **Mac mini M4 Pro with 64 GB** unified memory is the "sweet spot" for local LLM inference. It gives a table of models with token rates and RAM use, a price, power claims and a 3-node "Mac mini cluster" example. The text is heavily cross-linked to the site's own glossary (SEO pattern). **No methodology, runtime versions, prompt lengths or sources** are given for any number, and several numbers conflict with each other or with independent measurements (see flags).

## Key Insights (as claimed; not verified)
- **Price:** Mac mini M4 Pro 64 GB "around €2,500" (March 2026, Europe). A "comparable Linux server with 48 GB+ VRAM" is claimed at €4,000–8,000.
- **Power:** "about 65 watts under full load", vs "NVIDIA A100 300–400 watts". No measurement is described.
- **Claimed token rates on M4 Pro 64 GB:**

| Model | Quantisation | Claimed tok/s | Claimed RAM |
| --- | --- | --- | --- |
| Llama 3.3 70B | Q4_K_M | 8–12 | ~42 GB |
| Qwen 2.5 32B | Q5_K_M | 18–25 | ~24 GB |
| Mistral Large 2 (123B) | Q3_K_M | 3–5 | ~58 GB |
| DeepSeek-R1 32B | Q4_K_M | 15–20 | ~20 GB |
| Phi-4 14B | Q8_0 | 35–45 | ~16 GB |
| Gemma 2 27B | Q5_K_M | 20–28 | ~22 GB |

- "MLX models … achieve up to 20% higher inference speed" than GGUF (unsourced; compare the 15% in [[Hardware Corner 2025 - How fast is the AI Max+ 395 for LLM inference]]).
- **Cluster example:** 3x Mac mini M4 Pro 64 GB (about €7,500, 192 GB combined, about 200 W) via Thunderbolt and EXO "enables Llama 3.1 405B in Q4". Compared with an "H100 server, €30,000+, 700+ W".
- **Limitations listed:** training is slow (LoRA "possible but slow"), about 70B at 4-bit is the ceiling, and it is unsuitable for high-concurrency serving.
- **Cost claim:** GPT-5 at "about $30 (input) or $120 (output)" per million tokens. This is **unverified** and should not be cited.

**Quality flags.**
1. **Implausible token rates (arithmetic check):** decode reads roughly the whole weight file per token. Llama 70B at about 42 GB x 8–12 tok/s needs about 340–500 GB/s of effective bandwidth. Phi-4 at about 16 GB x 35–45 tok/s needs about 560–720 GB/s. These are at or above the **546 GB/s of the top M4 Max** ([[Apple 2025 - Mac Studio (2025) tech specs]]), a higher-tier chip than the M4 Pro. Independent measurements on a 40-core M4 Max give only about 5.5–6.3 tok/s for a 70B model at Q8 (about 70 GB) ([[Hardware Corner 2025 - How fast is the AI Max+ 395 for LLM inference|Hardware Corner]]). The M4 Pro's own bandwidth is **not stated** in this source and should be cited from Apple's Mac mini spec page. The table should be treated as **not credible**.
2. **Self-contradictions:**
   - "models with up to 40 billion parameters run entirely in RAM" conflicts with its own table listing 70B (42 GB) and 123B (58 GB) models.
   - The cluster claim does not add up: its own 70B Q4 ≈ 42 GB rule scales to about 240 GB for 405B Q4 (arithmetic), more than the 192 GB of the 3-node cluster.
3. "Best-selling machine for local AI inference" is unsupported. The 65 W and A100/H100 comparisons are unsourced.
4. It is commercial content from a company selling AI services, and the euro prices depend on date and market.

## Relevance to GroundOne
- **Price point for the under-€3k class.** About €2,500 for a 64 GB Apple desktop (single unverified source) is a rough anchor between the thesis laptop and a Mac Studio. It should be confirmed from Apple's store page with a date before it goes in the thesis ([[Local Inference Hardware]]).
- **Same software stack as GroundOne.** An M4 Pro would run GroundOne's MLX code unchanged ([[Apple Silicon and MLX]]). However, the page gives no prefill/TTFT data, which is the only phase GroundOne uses.
- **Narrative only.** Its framing (data sovereignty, GDPR, no per-token cost, hybrid cloud/local) matches the thesis's locality pillar ([[On-Device Inference]]), but the page should not be cited for any number. Better sources: [[Apple ML Research 2025 - Exploring LLMs with MLX and the neural accelerators in the M5 GPU]] for MLX performance and vendor spec pages for hardware.

## Links
- Concepts: [[On-Device Inference]], [[Apple Silicon and MLX]], [[Prefill and Decode]], [[Energy of LLM Inference]], [[Local Inference Hardware]] (proposed), [[Local Inference Hardware|Unified Memory Architecture]] (proposed), [[Prefill and Decode|Memory Bandwidth Bound]] (proposed), [[Quantization]] (proposed)
- Related sources: [[Apple 2025 - Mac Studio (2025) tech specs]], [[Apple 2024 - MacBook Pro 14-inch M4 tech specs]], [[Hardware Corner 2025 - How fast is the AI Max+ 395 for LLM inference]], [[EXO Labs 2025 - NVIDIA DGX Spark and Mac Studio, disaggregated inference]], [[Corelab - Best GPU for local LLMs, VRAM tier list]]
