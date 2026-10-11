---
type: source
author: "Google (Google for Developers blog)"
date: 2025-05-20
venue: "Google Developers Blog announcement (retrieved 2026-10-11)"
url: "https://developers.googleblog.com/en/introducing-gemma-3n/"
tags: [source, vendor-blog, open-weight, on-device, mobile, small-language-models, multimodal, privacy, memory]
---
# Google 2025 – Introducing Gemma 3n

**Raw file**: `raw/local_inference/Google 2025 - Introducing Gemma 3n_ingested.md`

## Overview
Google's announcement (20 May 2025, Google I/O) of an **early preview of Gemma 3n**, an open model with a new **mobile-first architecture** for on-device use on phones, tablets and laptops. It was co-developed with Qualcomm, MediaTek and Samsung System LSI, and the same architecture underlies the next **Gemini Nano**. The post describes memory-saving techniques (Per-Layer Embeddings, KV-cache sharing, activation quantisation, MatFormer nesting), multimodal input (audio, image, video, text), and access through Google AI Studio (cloud) and Google AI Edge (on device). Charts (Chatbot Arena Elo ranking; MMLU vs model size for mix'n'match) are referenced but their data did not survive extraction. Part of a list of "experiences you can build" is also missing.

## Key Insights
1. **Per-Layer Embeddings (PLE).** Raw parameter counts are **5B and 8B**, but the memory overhead is comparable to **2B and 4B** models: a "dynamic memory footprint of just **2 GB and 3 GB**". The model IDs suggest the E2B/E4B naming ("gemma-3n-e4b-it" in a link).
2. **Speed and quality (vendor claim).** "Starts responding approximately **1.5× faster** on mobile", with "significantly better quality" than **Gemma 3 4B**, thanks to PLE, **KV-cache (KVC) sharing** and advanced activation quantisation. "Starts responding" refers to time to first token, i.e. prefill.
3. **MatFormer "many-in-1".** A model with a 4B active memory footprint contains a nested 2B submodel. "Mix'n'match" creates intermediate submodels to trade quality against latency without hosting separate models. Details are deferred to a forthcoming technical report.
4. **Privacy-first and offline.** "Local execution enables features that respect user privacy and function reliably, even without an internet connection."
5. **Multimodal and multilingual.** Audio (speech recognition and speech translation), image, video and interleaved inputs (public audio implementation "coming soon"). **50.1% ChrF on WMT24++**.
6. **Access.** Preview via Google AI Studio (in-browser, i.e. cloud-hosted, text only at launch) and Google AI Edge for on-device text and image. The licence is not stated in the extracted text.

**Quality notes.** **Vendor marketing:** every performance claim (1.5× faster, "significantly better quality", Arena ranking) is Google's own and unverified in the text, with no device, prompt length or measurement protocol given. The 2 GB / 3 GB figures are "dynamic memory footprint" and the post does not say what is included (KV cache? vision and audio encoders?). This is a preview announcement from May 2025, and the final release may differ. The raw parameter counts (5B, 8B) exceed the 5B upper bound of [[Lu 2024 - Small Language Models, Survey, Measurements, and Insights (arXiv 2409.15790)|Lu 2024]]'s SLM definition, while the effective footprint falls inside it.

## Relevance to GroundOne
- **A major vendor endorses on-device inference with privacy as a selling point.** This supports the locality pillar's premise that local, offline, private inference is a mainstream design goal, alongside Apple's on-device model ([[Gunter 2024 - Apple Intelligence Foundation Language Models]]) ([[On-Device Inference]]).
- **Memory budgets of the same order.** The 2–3 GB footprints are comparable to GroundOne's 3B at 8-bit (weights about 3.3 GB). Small open models are being engineered around exactly the memory budget that a local verifier must share with a generator ([[Small Language Models]], [[Local Inference Hardware]]).
- **Time to first token is the advertised metric.** Google advertises "starts responding faster", a prefill-side metric. This is consistent with the thesis's point that prefill latency matters on device, and a System One's whole cost is that prefill ([[Prefill and Decode]]). It is a vendor claim with no protocol, so cite it only as an illustration.
- **Not used in the thesis.** Gemma 3n is a possible alternative base (open weights, multimodal) but was not evaluated. Its licence terms are not in this source and would need checking. Whether MLX supports its architecture (PLE, MatFormer) was not checked; this source says nothing about it ([[Apple Silicon and MLX]]).

## Links
- Concepts: [[On-Device Inference]], [[Prefill and Decode]], [[KV Cache]], [[Apple Silicon and MLX]], [[Small Language Models]] (proposed), [[Open-Weight Models]] (proposed), [[Local Inference Hardware]] (proposed), [[Quantization]] (proposed)
- Related sources: [[Gunter 2024 - Apple Intelligence Foundation Language Models]], [[Lu 2024 - Small Language Models, Survey, Measurements, and Insights (arXiv 2409.15790)]], [[Alizadeh 2024 - LLM in a flash]]
