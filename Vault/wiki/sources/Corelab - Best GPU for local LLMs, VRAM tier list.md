---
type: source
author: "Core Lab Joe (corelab.tech)"
date: 2025-08-07
venue: "corelab.tech blog, affiliate buyer's guide (first published 2025-08-07, content labelled '2026' and 'April 2026 Edition'; retrieved 2026-10-11)"
url: "https://corelab.tech/llmgpu/"
tags: [source, blog, low-quality, affiliate, hardware, discrete-gpu, vram, nvidia, amd, intel, price, local-inference]
---
# Corelab – Best GPU for Local LLMs (2026): VRAM Tier List & Buyer's Guide

**Raw file**: `raw/local_inference/Corelab - Best GPU for local LLMs, VRAM tier list_ingested.md`

## Overview
A hobbyist buyer's guide to discrete GPUs (NVIDIA, AMD, Intel, used data-centre cards) and the Mac Studio for local LLMs. Its thesis is "**VRAM capacity first**": if a model does not fit in VRAM, performance collapses, for example "from 50 tokens/sec to 2 tokens/sec". It gives VRAM, board power, rough 7B tokens/s and US/CAD price ranges per card. **This is SEO/affiliate content** (Amazon and link-shortener affiliate links throughout). The tokens/s figures are unsourced estimates, and the page contains several factual errors and internal contradictions (see flags). Use it only as a **market snapshot of VRAM tiers and street prices**, never as a source of performance numbers.

## Key Insights (as stated by the page; not verified)
**Expanded comparison table ("April 2026 Edition"):**
| GPU | VRAM | Board power | "Tokens/sec (7B)" | Price (USD) |
| --- | --- | --- | --- | --- |
| RTX 5090 | 32 GB | 575 W | 75–100+ | $1,999+ |
| RTX 5080 | 16 GB | 360 W | 45–60 | $1,199+ |
| RTX 4090 | 24 GB | 450 W | 35–50 | $1,500–1,800 |
| RTX 3090 (used) | 24 GB | 350 W | 15–25 | $650–800 |
| RTX 4060 Ti 16GB | 16 GB | 160 W | 12–18 | $380–450 |
| RX 9070 XT | 16 GB | 300 W | 15–22 | $599+ |
| RX 7900 XTX | 24 GB | 355 W | 10–15 | $700–850 |
| Arc B770 | 16 GB | 240 W | 10–18 | $349 |
| Arc B580 | 12 GB | 190 W | 8–14 | $249 |
| Tesla P40 (used) | 24 GB | 250 W | 5–10 | $150 |

- **Rules of thumb on the page:**
  - Q4_K_M needs about 6 GB for 8B, about 20 GB for 34B and about 42 GB for 70B.
  - 70B in FP16 needs about 140 GB.
  - Add 20% for KV cache and context.
  - "16GB VRAM is basically the minimum usable" in 2026.
- **Mac Studio section:** unified memory means "the system RAM *is* the VRAM"; an M2 Ultra is said to generate about 15–20 tok/s vs 50+ on an RTX 4090 (unspecified model).
- **Dual used RTX 3090** (about $1,600, 48 GB) is presented as the value path for 70B models.
- **FAQ:** inference is "often memory-bound"; the 5090's GDDR7 bandwidth helps "Prompt Ingest". PCIe 5.0 barely matters once the model is loaded.

**Quality flags (errors and contradictions found in the text):**
- **Products and models that do not exist or are misnamed:**
  - "Mac Studio (M4 Ultra)" with 192 GB: the 2025 Mac Studio has M4 Max or M3 Ultra ([[Apple 2025 - Mac Studio (2025) tech specs]]).
  - "Llama-4-405B" and "Llama-3-405B".
  - "Intel B880" and "AMD RX 8800 XT".
  - "RTX 3090/9900 XTX".
  - The Arc A770 described as "the consumer version of the Arc Pro B70" (different generations).
- **Numbers that contradict each other:**
  - RTX 5090 is 60–90+ tok/s in one section and 75–100+ in another.
  - RTX 5080 is 40–55 vs 45–60 tok/s; RX 7900 XTX is 7–12 vs 10–15 tok/s.
  - RTX 4090 is $1,600–2,000 vs $1,500–1,800.
- **Estimates that cannot hold:**
  - The tok/s values are labelled "rough estimates for a 7B model in FP16". FP16 7B weights are about 14 GB and cannot fit on the 12 GB cards in the same table.
  - It says 16 GB is "the perfect home for 34B models at Q4_K_M", but its own rule says 34B needs about 20 GB.
  - It says dual 3090s (48 GB) run "Llama-3-70B at full precision", but its own figure is about 140 GB.
- **No methodology:** no runtime, quantisation or context length is given for any tok/s figure.
- **Prices:** US/CAD street prices that depend on date and market, and include used-market prices.

## Relevance to GroundOne
- **Mostly not applicable.** The guide is about fitting the largest possible **generator** into VRAM and quotes decode tokens/s only. GroundOne's verifier is small (0.5B/3B, about 0.5/3.3 GB in 8-bit) and runs no decode. Even the cheapest 8 GB card in the list would hold it.
- **Useful context only:** it documents that the mainstream consumer GPU market in 2025–2026 has **12–32 GB VRAM tiers** with US prices from about $250 to $2,000+. This frames the thesis's 16 GB laptop as a typical, not exceptional, memory budget ([[Local Inference Hardware]]).
- **Capacity vs bandwidth confusion.** Its ranking ("memory bandwidth affects speed, not capability") is right in spirit for decode. For a System One the relevant spec would be **compute (prefill)**, which the page never quantifies ([[Prefill and Decode]]).
- **Do not cite for numbers in the thesis.** Use vendor spec pages for VRAM/bandwidth/power, and independent benchmarks for speed.

## Links
- Concepts: [[On-Device Inference]], [[Prefill and Decode]], [[KV Cache]], [[Local Inference Hardware]] (proposed), [[Quantization]] (proposed), [[Prefill and Decode|Memory Bandwidth Bound]] (proposed)
- Related sources: [[Level1Techs - ASRock Intel Arc Pro B60 24 GB for local AI]], [[Hardware Corner 2025 - How fast is the AI Max+ 395 for LLM inference]], [[PCWorld - Framework Desktop review]], [[Apple 2025 - Mac Studio (2025) tech specs]], [[Davies Meyer - Mac mini M4 Pro for local AI inference]]
