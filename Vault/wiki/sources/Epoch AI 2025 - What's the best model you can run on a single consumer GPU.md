---
type: source
author: "Venkat Somala, Luke Emberson (Epoch AI)"
date: 2025-09-09
venue: "Epoch AI Substack newsletter post (retrieved 2026-10-11)"
url: "https://epochai.substack.com/p/whats-the-best-model-you-can-run"
tags: [source, newsletter, open-weight, consumer-hardware, local-inference, governance]
---
# Epoch AI 2025 – What's the best model you can run on a single consumer GPU?

**Raw file**: `raw/local_inference/Epoch AI 2025 - What's the best model you can run on a single consumer GPU_ingested.md`

## Overview
A short Substack summary (9 September 2025) of the Epoch data insight [[Epoch AI 2025 - Frontier AI performance becomes accessible on consumer hardware within a year]]. It restates the finding, gives three reasons for it, and adds governance implications and a forecast. Short text (about 300 words) with no methodology of its own; the full analysis is on the linked Epoch page.

## Key Insights
1. **Finding.** On GPQA Diamond, MMLU-Pro, the AA Intelligence Index and LMArena, models small enough for one consumer GPU (**≤ 28B parameters for the RTX 4090, ≤ 40B for the RTX 5090**) "consistently catch the frontier within 6–12 months".
2. **Three reasons.** (1) Open-weight models scale compute at a rate similar to the closed frontier; (2) distillation compresses larger models with little loss; (3) new GPU generations raise the size of models that fit locally.
3. **Governance.** Dangerous capabilities that appear at the frontier are likely to be "widely available and unrestricted in under a year", which complicates regulation.
4. **Forecast.** If the year-long lag holds, open models runnable at home should match **Grok 4** by mid-2026. The source does not check this (written September 2025), and this page does not either.
5. **Caution (footnote 1).** The best-scoring open model on a given benchmark is more likely to be overfit, so the lag in broad real-world use is likely longer. Rough equivalence: **gpt-oss-20B ≈ o1-mini (11-month gap) or Claude 3.5 Sonnet (13-month gap)**.

**Quality notes.** A secondary summary by the same authors as the data insight. It adds the explicit authorship, the Grok 4 forecast and the gpt-oss-20B comparison; everything else repeats the main page.

## Relevance to GroundOne
- A short, citable statement of the same trend as the main Epoch page: consumer hardware runs year-old frontier-level general models ([[Open-Weight Models]], [[Local Inference Hardware]]).
- The governance point (frontier capabilities spread through open weights within a year) is context for the regulation discussion ([[Open-Weight Models|EU AI Act]]), not for GroundOne's technical claims.
- As with the main page, the lag concerns general capability of 4B–40B models; it says nothing about 0.5B–3B task specialists like GroundOne.

## Links
- Concepts: [[On-Device Inference]], [[Open-Weight Models]] (proposed), [[Local Inference Hardware]] (proposed), [[Open-Weight Models|Open-Closed Capability Gap]] (proposed), [[Open-Weight Models|EU AI Act]] (proposed)
- Related sources: [[Epoch AI 2025 - Frontier AI performance becomes accessible on consumer hardware within a year]], [[Epoch AI - Open vs closed capability gap (ECI)]]
