---
type: source
author: "Apple Inc."
date: 2025
venue: "Apple Support technical specifications page (page dated 2026-04-10; retrieved 2026-10-11)"
url: "https://support.apple.com/en-us/122211"
tags: [source, vendor-spec, hardware, apple-silicon, m4-max, m3-ultra, unified-memory, bandwidth, local-inference]
---
# Apple 2025 – Mac Studio (2025) Tech Specs

**Raw file**: `raw/local_inference/Apple 2025 - Mac Studio (2025) tech specs_ingested.md`

## Overview
Apple's official technical specifications for the **Mac Studio (2025)**, offered with an **M4 Max** or an **M3 Ultra** chip. It is the citable vendor source for the memory capacities and bandwidths of Apple's desktop machine most often used for local LLM inference. The page gives memory, bandwidth, core counts and the maximum continuous power, but **no TFLOPS figure and no price**. Most of the raw file is boilerplate (displays, ports, environment, built-in apps).

## Key Insights (vendor specifications)
| Configuration | CPU | GPU | Neural Engine | **Memory bandwidth** | **Unified memory** |
| --- | --- | --- | --- | --- | --- |
| M4 Max (base) | 14-core (10P + 4E) | 32-core | 16-core | **410 GB/s** | **36 GB** |
| M4 Max (upgrade) | 16-core | 40-core | 16-core | **546 GB/s** | **48, 64 or 128 GB** (these options only with this chip variant) |
| M3 Ultra (base) | 28-core (20P + 8E) | 60-core | 32-core | **819 GB/s** | **96 GB**, configurable to **256 GB** |
| M3 Ultra (upgrade) | 32-core | 80-core | 32-core | **819 GB/s** | as above |

- **Power:** maximum continuous power **480 W** (whole system; no SoC power figure). ENERGY STAR certified.
- Storage: 512 GB to 8 TB (M4 Max), 1 TB to 16 TB (M3 Ultra). Connectivity includes Thunderbolt 5 (up to 120 Gb/s) and 10 Gb Ethernet, which are relevant for multi-machine clusters such as EXO.
- **Memory ceiling on this retrieval: 256 GB.** Other sources describe an **M3 Ultra Mac Studio with 512 GB** ([[EXO Labs 2025 - NVIDIA DGX Spark and Mac Studio, disaggregated inference|EXO Labs]], [[Hardware Corner 2025 - How fast is the AI Max+ 395 for LLM inference|Hardware Corner]]). The page retrieved on 2026-10-11 (dated 2026-04-10) lists only 96 GB configurable to 256 GB. Either the 512 GB option was withdrawn after launch or the page was edited. The thesis should state capacities "as listed on the retrieval date" and not mix the two.
- Hardware Corner rounds the M3 Ultra bandwidth to "800 GB/s". The vendor figure is **819 GB/s**.

## Relevance to GroundOne
- **Bandwidth range of Apple desktops.** 410 to 819 GB/s is 3.4x to 6.8x the thesis M4's 120 GB/s ([[Apple 2024 - MacBook Pro 14-inch M4 tech specs]]). For a 3B 8-bit model (about 3.3 GB), the decode lower bound falls from about 27 ms/token (M4) to about 8 ms (410 GB/s) and about 4 ms (819 GB/s) (arithmetic). A **decoding** judge therefore gains a lot from these machines.
- **Prefill is a different story.** The page gives no compute figure. EXO Labs estimates the M3 Ultra GPU at about 26 TFLOPS FP16, about a quarter of a DGX Spark, so a prefill-only System One gains less from the M3 Ultra's bandwidth than a decoding judge does ([[Prefill and Decode]]).
- **Capacity far beyond need.** GroundOne's 3B peaks at 5.9 GB in training. A Mac Studio matters for the thesis as the upper end of "dedicated local inference machines" (large generators such as 70B dense or big MoE models), not as a requirement. The thesis's point is that the verifier fits next to the generator on a **16 GB laptop**.
- **Same software stack.** Unlike the DGX Spark or Strix Halo, GroundOne's MLX code would run unchanged here ([[Apple Silicon and MLX]]).

## Links
- Concepts: [[Apple Silicon and MLX]], [[On-Device Inference]], [[Prefill and Decode]], [[Energy of LLM Inference]], [[Local Inference Hardware]] (proposed), [[Local Inference Hardware|Unified Memory Architecture]] (proposed), [[Prefill and Decode|Memory Bandwidth Bound]] (proposed)
- Related sources: [[Apple 2024 - MacBook Pro 14-inch M4 tech specs]], [[NVIDIA - DGX Spark hardware overview]], [[EXO Labs 2025 - NVIDIA DGX Spark and Mac Studio, disaggregated inference]], [[Hardware Corner 2025 - How fast is the AI Max+ 395 for LLM inference]], [[Rajesh 2025 - Local LLM inference on Apple Silicon, MLX vs MLC vs Ollama vs llama.cpp (arXiv 2511.05502)]]
