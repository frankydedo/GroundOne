---
type: source
author: "Apple Inc."
date: 2024
venue: "Apple Support technical specifications page (retrieved 2026-10-10)"
url: "https://support.apple.com/en-us/121552"
tags: [source, vendor-spec, hardware, apple-silicon, m4, unified-memory, bandwidth, on-device]
---
# Apple 2024 – MacBook Pro (14-inch, M4, 2024) Tech Specs

**Raw file**: `raw/Apple 2024 - MacBook Pro 14-inch M4 tech specs_ingested.md`

## Overview
Apple's official technical specifications for the 14-inch MacBook Pro with the base **M4** chip (introduced 2024), retrieved on 2026-10-10. This is the **thesis machine**: base M4, 10-core CPU, 10-core GPU, **16 GB unified memory**, **120 GB/s memory bandwidth**. The page is the citable vendor source for the hardware numbers used in the thesis.

## Key Insights (specs relevant to on-device inference)
| Item | Specification (as stated by Apple) |
| --- | --- |
| Chip | Apple M4 |
| CPU | 10-core: 4 performance + 6 efficiency cores |
| GPU | 10-core, hardware-accelerated ray tracing |
| Neural Engine | 16-core |
| **Memory bandwidth** | **120 GB/s** |
| **Memory** | **16 GB or 24 GB unified memory**, configurable to 24 GB or 32 GB |
| Storage | 512 GB or 1 TB SSD, configurable to 1 TB or 2 TB |
| Battery / power | 72.4 Wh lithium-polymer battery; 70 W USB-C adapter |
| Apple Intelligence | supported (listed under the chip) |

- The acoustic test configuration is "M4, 10-core CPU, 10-core GPU, 16GB unified memory, 1TB storage"; battery-life tests used a 24 GB machine.
- The page gives no peak TFLOPS figure for the GPU or the Neural Engine, and no SoC power envelope beyond the adapter rating. Compute numbers, if needed, must come from another citable source.

## Relevance to GroundOne
- **Citable hardware facts.** The thesis states the machine as "Apple M4, 10-core CPU, 10-core GPU, 16 GB unified memory, 120 GB/s" with this page as the source, as required by the locality pillar ("all specifications to be taken from vendor documentation and cited"). See [[Apple Silicon and MLX]].
- **Bandwidth bounds decode.** At batch 1, each decode step reads all weights once. With 120 GB/s, 8-bit weights of about 0.5 GB (0.5B) and about 3.3 GB (3B) give lower bounds of about 4 ms and 27 ms per generated token. The measured decode times on this machine (≈6–7 ms and ≈32–42 ms per token) sit above these bounds, consistent with memory-bound decoding ([[Prefill and Decode]]). GroundOne's single prefill is compute-bound instead, which is why it is not limited by this number.
- **16 GB is the co-residence budget.** Generator, verifier, retriever, OS and KV caches must share 16 GB; GroundOne training peaked at 2.6 GB (0.5B) and 5.9 GB (3B) ([[On-Device Inference]]).
- **Energy context.** GroundOne draws about 16 W of SoC power during verification, small next to the 70 W adapter; 33 J per verified answer (3B) is about 0.009 Wh, i.e. about 8,000 verifications per 72.4 Wh battery charge if nothing else ran (arithmetic, ignoring display and idle power). See [[Energy of LLM Inference]].

## Links
- Concepts: [[Apple Silicon and MLX]], [[On-Device Inference]], [[Prefill and Decode]], [[Energy of LLM Inference]]
- Related sources: [[MLX README (ml-explore)]], [[Alizadeh 2024 - LLM in a flash]], [[Gunter 2024 - Apple Intelligence Foundation Language Models]]
