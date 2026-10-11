---
type: source
author: "Mark Hachman (PCWorld / Foundry)"
date: 2025-08-07
venue: "PCWorld product review (retrieved 2026-10-11)"
url: "https://www.pcworld.com/article/2866400/framework-desktop-review.html"
tags: [source, review, hardware, amd, strix-halo, ryzen-ai-max, framework-desktop, unified-memory, local-inference, price]
---
# PCWorld 2025 – Framework Desktop Review

**Raw file**: `raw/local_inference/PCWorld - Framework Desktop review_ingested.md`

## Overview
A consumer review of the **Framework Desktop (DIY Edition)**, a 4.5-litre mini-ITX desktop built around AMD's **Ryzen AI Max / Max+ ("Strix Halo")** APU with up to 128 GB of soldered LPDDR5X. It gives dated **US prices** and a configuration list, plus two local-LLM measurements (Llama 4 Scout and gpt-oss-20B). Most of the review covers the build process, CPU/GPU and gaming benchmarks. The benchmark **charts are images and are missing from the extraction**, so only the numbers quoted in the text are available.

## Key Insights
**Configuration and prices (US, as of review date August 2025):**
| Item | As stated in the review |
| --- | --- |
| Processor options | Ryzen AI Max 385 (8-core, 32 GB) up to **Ryzen AI Max+ 395 (16-core, 32 threads, up to 5.1 GHz)** |
| Integrated GPU / NPU | Radeon 8060S; NPU "50 TOPS" |
| **Memory** | 32 GB (Max 385) / 64 GB / **128 GB** (Max+ 395), **LPDDR5X-8000, soldered** |
| Power | 400 W FlexATX PSU; chip "supports a TDP of 55 watts" (reviewer's statement) |
| Size / weight | 8.9 x 8.1 x 3.9 in (4.5 L), 6.8 lb |
| **Price** | **from $1,099** (Max 385) **to $1,999** (Max+ 395 option, described with 128 GB); review unit **$2,515** as tested (with SSD, Windows 11 Pro, extras) |

- **Memory allocation:** with AMD's beta Adrenalin driver, the 128 GB can be split as **32 GB for the OS and 96 GB as VRAM**. The early review drivers did not do this well and hurt AI results.
- **LLM measurements** (single sample prompt, the "woodchuck" query):

| Model (as named in review) | Download size | Decode | Time to first token |
| --- | --- | --- | --- |
| Llama 4 Scout 109B | 67 GB | **12.64 tok/s** | 0.62 s |
| OpenAI gpt-oss 20B | 11.3 GB | **53.9 tok/s** | 2.27 s |

- A UL Procyon-style LLM benchmark ("four relatively old models") improved by only 8.7% on Phi 3.5 with the updated driver. The other values are in the missing charts.

**Quality flags.**
- The **runtime, quantisation and prompt length are not stated**. TTFT is higher for the smaller model (2.27 s vs 0.62 s), which suggests model loading or a different setting is included, so the TTFT values are **not usable**.
- The review does not mention that both models are Mixture-of-Experts models (to be confirmed from their model cards). This matters: decode reads only the active experts, so 12.64 tok/s on a 67 GB file does **not** imply 67 GB x 12.64 ≈ 850 GB/s of bandwidth.
- **No memory-bandwidth figure** is given.
- Prices depend on the date, configuration and tariffs: the review notes the proposed US 100% chip tariffs and that the product was sold out through "sometime after October".
- The statement that Intel laptops always split RAM 50/50 between OS and GPU is a simplification and should not be cited.

## Relevance to GroundOne
- **Price anchor for the under-$3k class.** A 128 GB Strix Halo desktop for about $2,000 (about $2,500 configured) is the cheapest large-unified-memory option in these sources. It is useful for the thesis paragraph on "what local hardware a budget buys" ([[Local Inference Hardware]]).
- **MoE makes big models usable on moderate bandwidth.** The Scout/gpt-oss numbers show that sparse models can decode at usable speed on an APU ([[Mixture of Experts]]). This is relevant to the generator side of a local RAG stack, not to the verifier.
- **Does not apply to GroundOne directly.** There is no prefill throughput measurement, the stack is AMD/Windows (GroundOne is MLX-only), and the capacity (96 GB VRAM) is far beyond GroundOne's under-6 GB footprint. For a System One, compute throughput in prefill matters, and this review does not measure it.

## Links
- Concepts: [[On-Device Inference]], [[Mixture of Experts]], [[Prefill and Decode]], [[Local Inference Hardware]] (proposed), [[Local Inference Hardware|Unified Memory Architecture]] (proposed), [[Quantization]] (proposed)
- Related sources: [[Hardware Corner 2025 - How fast is the AI Max+ 395 for LLM inference]], [[NVIDIA - DGX Spark hardware overview]], [[Apple 2025 - Mac Studio (2025) tech specs]], [[Davies Meyer - Mac mini M4 Pro for local AI inference]], [[Corelab - Best GPU for local LLMs, VRAM tier list]]
