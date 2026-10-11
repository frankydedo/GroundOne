---
type: source
author: "NVIDIA Corporation"
date: 2026
venue: "NVIDIA GeForce compare page (retrieved 2026-10-11)"
url: "https://www.nvidia.com/en-us/geforce/graphics-cards/compare/"
tags: [source, vendor-spec, hardware, gpu, rtx-50, vram, bandwidth]
---
# NVIDIA 2026 – Compare GeForce Graphics Cards (specifications)

**Raw file**: `raw/local_inference/NVIDIA 2026 - GeForce graphics cards compare specs_ingested.md`

## Overview
NVIDIA's comparison table of GeForce cards, retrieved 2026-10-11. Only the RTX 50 series rows list memory bandwidth; older series list memory size and interface width only.

## Key Insights (RTX 50 series)
| Card | Memory | Interface | Bandwidth |
| --- | --- | --- | --- |
| RTX 5090 | 32 GB GDDR7 | 512-bit | 1,792 GB/s |
| RTX 5080 | 16 GB GDDR7 | 256-bit | 960 GB/s |
| RTX 5070 Ti | 16 GB GDDR7 | 256-bit | 896 GB/s |
| RTX 5070 | 12 GB GDDR7 | 192-bit | 672 GB/s |
| RTX 5060 Ti | 16 / 8 GB GDDR7 | 128-bit | 448 GB/s |
| RTX 5060 | 8 GB GDDR7 | 128-bit | 448 GB/s |
| RTX 5050 | 8 GB GDDR6 | 128-bit | 320 GB/s |
- The RTX 5090 product page's structured data lists a price of 1,999 (US dollars, MSRP); street prices are not on NVIDIA's pages.
- RTX 3090/4090 bandwidth is not listed on the current pages, so the thesis does not plot them.

## Relevance to GroundOne
- Discrete cards have up to 15× the thesis machine's bandwidth but at most 32 GB: the decode floor of a 3B 8-bit judge would be 1.8 ms per token on an RTX 5090, yet still non-zero; a System One pays none of it ([[Local Inference Hardware]], [[Prefill and Decode]]).

## Links
- Concepts: [[Local Inference Hardware]], [[Prefill and Decode]], [[Quantization]]
