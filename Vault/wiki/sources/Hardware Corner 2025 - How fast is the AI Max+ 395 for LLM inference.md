---
type: source
author: "Hardware Corner (hardware-corner.net, author not named in the extraction)"
date: 2025-03-17
venue: "Hardware Corner, enthusiast hardware website (retrieved 2026-10-11)"
url: "https://www.hardware-corner.net/how-fast-ai-max-395-llm-20250317/"
tags: [source, web-article, hardware, amd, strix-halo, ryzen-ai-max, unified-memory, apple-silicon, local-inference, second-hand-benchmark]
---
# Hardware Corner 2025 – How Fast Will a Ryzen AI MAX+ 395 (Strix Halo) System Be for LLM Inference?

**Raw file**: `raw/local_inference/Hardware Corner 2025 - How fast is the AI Max+ 395 for LLM inference_ingested.md`

## Overview
A short, early (March 2025) enthusiast article about **AMD's Ryzen AI MAX+ 395 ("Strix Halo")**, an APU with a large shared LPDDR5X memory pool, written before Strix Halo systems were widely available. It reports second-hand early benchmark numbers (from a review of a Chinese mini-PC **prototype**) and compares them with an M4 Max MacBook Pro. Its argument is that Strix Halo's advantage is **capacity**, not speed: 70B models load but run at about 3 tok/s, so the sweet spot is 7B–32B. The tone is speculative ("could", "may", "remains uncertain").

## Key Insights
- **GPU memory allocation:** up to **96 GB in Windows** and **110 GB in Linux**, out of 128 GB system memory. The article contrasts this with consumer GPUs "capped at 24GB–48GB of VRAM".
- **Early Strix Halo measurement (second-hand):** prototype mini PC AXB35-2, 128 GB, **DeepSeek R1 Distill Llama-70B, Q8**, LM Studio 0.3.9, 2K context, Windows, no Flash Attention: **about 3 tok/s**.
- **Apple comparison (same model):** MacBook Pro **M4 Max, 40-core GPU, 128 GB**:

| Format / context | Decode tok/s |
| --- | --- |
| GGUF, no Flash Attention | 5.46 |
| MLX, 2K context | 6.29 |
| MLX, 8K context | 5.59 |
| MLX, 13K context | 6.31 |

- **Cross-reference (RTX 3090):** QwQ 32B at "around 20 tokens per second" (linked Hardware Corner guide, not reproduced here).
- **Bandwidth sanity check (arithmetic, not in the article):** a 70B model at Q8 is about 70 GB, so 6.3 tok/s means reading about 440 GB/s. That is about 81% of the 546 GB/s Apple lists for the 40-core M4 Max ([[Apple 2025 - Mac Studio (2025) tech specs]]), consistent with a **bandwidth-bound decode**. About 3 tok/s on Strix Halo means about 210 GB/s effective. The article itself gives **no Strix Halo bandwidth figure**.

**Quality flags.**
- The numbers are second-hand: the reviews are referred to but not reproduced. They come from a prototype with early software, and only **decode** speed is reported (no prompt processing / TTFT).
- The article says the M3 Ultra has "800GB/s"; Apple's figure is **819 GB/s**.
- "The upcoming 5090" is mentioned with "24GB or 48GB of VRAM" without saying which card has which. Corelab lists the RTX 5090 as 32 GB ([[Corelab - Best GPU for local LLMs, VRAM tier list]]), so this sentence should not be cited.
- It is an enthusiast site with no methodology section.

## Relevance to GroundOne
- **Capacity vs bandwidth.** The piece illustrates that a big shared memory pool lets large models **load** but does not make them **fast**. Decode speed follows bandwidth, which is the core of the thesis's hardware argument ([[Prefill and Decode]]).
- **MLX vs GGUF on the same Apple machine:** MLX was about 15% faster than GGUF in decode (6.29 vs 5.46 tok/s). This is weak, single-configuration support for using MLX on Apple Silicon ([[Apple Silicon and MLX]]).
- **Mostly not applicable to the verifier.** It reports only decode tokens/s for a 70B model, a regime GroundOne never enters: GroundOne runs 0.5B/3B models, one prefill and no decode. Strix Halo is relevant to the thesis only as one of the "dedicated local machine" families. Its vendor specs (bandwidth, price) must come from AMD or a review such as [[PCWorld - Framework Desktop review]].

## Links
- Concepts: [[On-Device Inference]], [[Apple Silicon and MLX]], [[Prefill and Decode]], [[Local Inference Hardware]] (proposed), [[Local Inference Hardware|Unified Memory Architecture]] (proposed), [[Prefill and Decode|Memory Bandwidth Bound]] (proposed), [[Quantization]] (proposed)
- Related sources: [[PCWorld - Framework Desktop review]], [[Apple 2025 - Mac Studio (2025) tech specs]], [[NVIDIA - DGX Spark hardware overview]], [[Corelab - Best GPU for local LLMs, VRAM tier list]]
