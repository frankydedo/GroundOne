---
type: source
author: "Apple Inc."
date: 2026
venue: "Apple technical specifications page (retrieved 2026-10-11)"
url: "https://www.apple.com/macbook-pro/specs/"
tags: [source, vendor-spec, hardware, apple-silicon, m5, m5-pro, m5-max, unified-memory, bandwidth]
---
# Apple 2026 – MacBook Pro Tech Specs (M5, M5 Pro, M5 Max)

**Raw file**: `raw/local_inference/Apple 2026 - MacBook Pro tech specs (M5 family)_ingested.md`

## Overview
Apple's specification page for the current MacBook Pro, retrieved 2026-10-11 (M5 family). Citable source for the laptop rows of the Ch. 2 hardware table; the thesis machine (M4, 2024) has its own page ([[Apple 2024 - MacBook Pro 14-inch M4 tech specs]]).

## Key Insights
| Chip | Memory bandwidth | Unified memory |
| --- | --- | --- |
| M5 (10-core GPU) | 153 GB/s | 16, 24 or 32 GB |
| M5 Pro | 307 GB/s | 24, 48 or 64 GB |
| M5 Max (32-core GPU) | 460 GB/s | 36 GB |
| M5 Max (40-core GPU) | 614 GB/s | 48, 64 or 128 GB |
- All M5 chips list GPU Neural Accelerators. No compute figures and no prices on the page.

## Relevance to GroundOne
- A laptop can now reach 128 GB and 614 GB/s (M5 Max): five times the thesis machine's bandwidth and eight times its memory. The base M5 laptop (153 GB/s) is the closest successor of the thesis machine; Apple measures it 3.3–4.1× faster in prefill and 1.19–1.27× in generation than the M4 ([[Apple ML Research 2025 - Exploring LLMs with MLX and the neural accelerators in the M5 GPU]]).

## Links
- Concepts: [[Local Inference Hardware]], [[Apple Silicon and MLX]], [[Prefill and Decode]]
- Related sources: [[Apple 2026 - Mac mini tech specs]], [[Apple 2025 - Mac Studio (2025) tech specs]]
