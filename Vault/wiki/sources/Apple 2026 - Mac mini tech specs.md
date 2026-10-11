---
type: source
author: "Apple Inc."
date: 2026
venue: "Apple technical specifications page (retrieved 2026-10-11)"
url: "https://www.apple.com/mac-mini/specs/"
tags: [source, vendor-spec, hardware, apple-silicon, m5, unified-memory, bandwidth, on-device]
---
# Apple 2026 – Mac mini Tech Specs (M5, M5 Pro)

**Raw file**: `raw/local_inference/Apple 2026 - Mac mini tech specs_ingested.md`

## Overview
Apple's specification page for the current Mac mini, retrieved 2026-10-11, when the lineup used the M5 family. Citable vendor source for the memory and bandwidth of the Mac mini in the hardware table of Ch. 2.

## Key Insights
| Chip | Memory bandwidth | Unified memory |
| --- | --- | --- |
| M5 | 153 GB/s (16 GB); the page states 170 GB/s for the 24 or 32 GB configurations | 16 GB, configurable to 24 or 32 GB |
| M5 Pro | 307 GB/s | 24 GB, configurable up to 48 or 64 GB |
- The M5 chips have "GPU Neural Accelerators" (matrix units in each GPU core), the feature behind Apple's 3.3–4.1× faster time to first token ([[Apple ML Research 2025 - Exploring LLMs with MLX and the neural accelerators in the M5 GPU]]).
- No price and no compute figure on the specs page; prices on the store page are rendered by script and were not extracted reliably.
- The 153 vs 170 GB/s distinction for the base M5 is as printed; the thesis figure uses 153 GB/s for the M5 (conservative).

## Relevance to GroundOne
- A Mac mini M5 Pro with 64 GB at 307 GB/s is the most capable Apple desktop below the Mac Studio, and has 2.6× the bandwidth of the thesis M4: the decode floor of a 3B 8-bit judge falls from about 27 ms to about 11 ms per token ([[Local Inference Hardware]]).

## Links
- Concepts: [[Local Inference Hardware]], [[Apple Silicon and MLX]], [[Prefill and Decode]]
- Related sources: [[Apple 2026 - MacBook Pro tech specs (M5 family)]], [[Apple 2025 - Mac Studio (2025) tech specs]], [[Apple 2024 - MacBook Pro 14-inch M4 tech specs]]
