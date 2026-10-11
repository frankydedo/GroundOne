---
type: source
author: "Epoch AI (Venkat Somala, Luke Emberson)"
date: 2025-08-15
venue: "Epoch AI Data Insight, web page (retrieved 2026-10-11)"
url: "https://epoch.ai/data-insights/consumer-gpu-model-gap"
tags: [source, data-insight, open-weight, consumer-hardware, local-inference, benchmarks, vram, quantization, kv-cache]
---
# Epoch AI 2025 – Frontier AI performance becomes accessible on consumer hardware within a year

**Raw file**: `raw/local_inference/Epoch AI 2025 - Frontier AI performance becomes accessible on consumer hardware within a year_ingested.md`

## Overview
An Epoch AI data insight (15 August 2025) measuring how long it takes for the best **open-weight model that fits on a single consumer GPU** to match the **absolute frontier** on four metrics: GPQA-Diamond, MMLU-Pro, the Artificial Analysis Intelligence Index and LM Arena Elo. Headline: with one RTX 5090 (under $2,500) anyone can run models matching the frontier of **6 to 12 months earlier**. The page includes a methodology section (hardware ceiling, data sources, regression, assumptions) and two large data tables (consumer-runnable open models, frontier models). Authors are named in the companion post [[Epoch AI 2025 - What's the best model you can run on a single consumer GPU]]. The extraction is clean; the two tables (~300 table lines) are not reproduced here.

## Key Insights
1. **Lag (headline, "Learn more").** Leading open models runnable on a single consumer GPU match frontier models after an average lag of **6–12 months**. This is consistent with Epoch's earlier estimate of a **5–22 month** lag for open-weight models of any size. Epoch warns that small open models are more likely to be optimised for specific benchmarks, so the real-world lag "may be somewhat longer".
2. **Drivers.** Open-weight models scale compute at a rate comparable to the closed frontier; distillation; continuing GPU progress.
3. **Hardware ceiling (Analysis).** VRAM usage = weights + KV cache + runtime overhead, with weights quantised to 4 bits (**0.54 bytes/parameter** on average), an **8k-token context** with INT8 KV cache for a Llama-class model (**~6.6 GiB**), and **~2 GiB** overhead. Marketed VRAM converted to GiB: RTX 4090 24 GB ≈ 22.37 GiB, RTX 5090 32 GB ≈ 29.80 GiB. Result: a theoretical ceiling of **~27B parameters** for the 4090 (13.6 + 6.6 + 2.0 ≈ 22.2 GiB) and **~40B** for the 5090. The selection step uses **≤ 28B** (4090 era) and **≤ 40B** (5090 era).
4. **Trend slopes.** On LM Arena Elo, consumer-runnable open models improve by **+125 Elo/year** vs **+80 Elo/year** for frontier models. Regression of top-1 score on release date, 90% CIs from 500 bootstrap samples; linear and logistic fits give "highly similar" results.
5. **Score sources.** Priority: Artificial Analysis, then the Epoch Benchmarking Hub, then developer-reported results ("slightly higher than third-party evaluations"). The OpenLLM Leaderboard (ended February 2025) was used to find candidate models.
6. **Assumptions and biases.** Only models whose full weights fit in GPU memory are counted, which biases the analysis against sparse (MoE) models. Offloading or more extreme quantisation could fit larger models at a cost in speed or quality. The 8k context is optimistic for reasoning models: output lengths grow **2.2×/year** (non-reasoning) and **5×/year** (reasoning), and a 20K-token output would need a ~15 GiB KV cache.
7. **Table data (examples, not exhaustive).** The consumer-model table lists e.g. Qwen2.5 32B (2024-09-17; GPQA-D 47, MMLU-Pro 70), Phi-4 15B (GPQA-D 57.5), Qwen3 30B-A3B-2507 reasoning (GPQA-D 71, MMLU-Pro 81) and gpt-oss-20B (2025-08-05; GPQA-D 62, MMLU-Pro 74). It covers 4B–40B models only; nothing at the 0.5B–3B scale used by GroundOne.

**Quality notes.** Independent analyst work with public code (Colab link) and stated assumptions, but it mixes evaluation sources. Small inconsistencies: the ceiling is computed as ~27B but the selection uses ≤ 28B; the 8k KV cache is given as 6.6 GiB in the method and as "6 GiB" in the assumptions paragraph. As a 2025 snapshot, the specific models and scores are already dated in October 2026.

## Relevance to GroundOne
- **Supports the locality pillar (general capability).** An independent source for the claim that capable open-weight models run on consumer hardware and trail the frontier by about a year. Useful in Ch. 1–2 to say that local inference is no longer limited to toy models ([[Open-Weight Models]], [[Local Inference Hardware]]).
- **Reusable memory model.** The weights + KV cache + overhead decomposition is the same budget GroundOne faces on the 16 GB unified-memory M4 ([[On-Device Inference]], [[KV Cache]]). The difference: a Mac shares the 16 GB with the OS, generator and retriever, whereas Epoch assumes a dedicated GPU.
- **Does not directly apply to GroundOne's argument.** The frontier-lag metric measures broad knowledge and reasoning (GPQA, MMLU-Pro, Arena). GroundOne is a narrow 0.5B/3B specialist whose case rests on task specialisation, not on general capability. The page should be cited for context on the local ecosystem, not as evidence that small models verify well.
- **Benchmark-overfitting caveat.** Epoch's warning that small open models overfit public benchmarks supports the thesis's use of frozen held-out test sets (T1–T3) instead of public leaderboards.

## Links
- Concepts: [[On-Device Inference]], [[KV Cache]], [[Mixture of Experts]], [[Qwen2.5]], [[Open-Weight Models]] (proposed), [[Local Inference Hardware]] (proposed), [[Open-Weight Models|Open-Closed Capability Gap]] (proposed), [[Quantization]] (proposed)
- Related sources: [[Epoch AI 2025 - What's the best model you can run on a single consumer GPU]], [[Epoch AI - Open vs closed capability gap (ECI)]], [[Stanford HAI 2025 - AI Index Report, Technical performance]]
