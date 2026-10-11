---
type: source
author: "WilmerHale (Privacy and Cybersecurity Law blog)"
date: 2025-07-24
venue: "WilmerHale law-firm blog post (retrieved 2026-10-11)"
url: "https://www.wilmerhale.com/en/insights/blogs/wilmerhale-privacy-and-cybersecurity-law/20250724-european-commission-issues-guidelines-for-providers-of-general-purpose-ai-models"
tags: [source, policy, eu-ai-act, regulation, general-purpose-ai, training-compute, fine-tuning, open-source-exemption]
---
# WilmerHale 2025 – Commission guidelines for providers of general-purpose AI models

**Raw file**: `raw/local_inference/WilmerHale 2025 - Commission guidelines for providers of general-purpose AI models_ingested.md`

## Overview
A law-firm summary (24 July 2025) of the **European Commission's guidelines of 18 July 2025** on the scope of obligations for providers of **general-purpose AI (GPAI) models** under the AI Act (Regulation (EU) 2024/1689). The guidelines complement the voluntary **GPAI Code of Practice**. The post covers the indicative compute thresholds, when a fine-tuner becomes a "provider", the conditions for the open-source exemption, life-cycle documentation, and the enforcement timeline. It is a secondary source; the Commission guidelines themselves were not ingested. The extraction is complete.

## Key Insights
1. **Indicative GPAI criterion: training compute.** Models trained with more than **10^23 FLOPs** that can generate text, images or video are presumed GPAI. This "aligns with" models of about **one billion parameters**. Above **10^25 FLOPs** a model is presumed to carry **systemic risk**, and the provider must notify the AI Office **within two weeks**. Compute estimates can be hardware-based or architecture-based, and must be accurate within **30%**.
2. **Fine-tuners as providers.** A downstream modifier becomes the provider of a *new* GPAI model only if the modification causes a "significant change". The indicative criterion: modification compute greater than **one third of the original model's training compute**. If that is unknown, one third of 10^25 FLOPs (systemic-risk originals) or of 10^23 FLOPs (other GPAI) is used instead.
3. **Open-source exemption (Arts. 53–54).** Exempts from technical documentation, from documentation for downstream integrators, and from appointing an EU representative. Three **cumulative** conditions: (a) a licence allowing unrestricted access, use, modification and distribution, with weights, architecture and usage information public; (b) **no monetisation**, direct or indirect (dual licensing or requiring user data counts; purely optional paid services do not); (c) below the systemic-risk threshold. **Copyright-policy obligations are not exempted.**
4. **Timeline.** Obligations apply from **2 August 2025**. Commission enforcement powers start **2 August 2026**; before that, enforcement is possible only on a "qualified alert" from the scientific panel (Art. 90(2)). Models placed on the market before 2 August 2025 must comply by **2 August 2027**.
5. **Penalties.** Up to **€15M or 3% of global revenue**, whichever is higher (Art. 101). This matches the CRFM figure.
6. **Research exclusion.** GPAI excludes models used for research, development or prototyping before being placed on the market (Art. 3(63)).

**Quality notes.** A reputable law firm, but a secondary summary written partly as client marketing. **Definitional error:** the post defines training compute as "the cumulative number of floating point operations **per second** (FLOPs)". Training compute is a cumulative count of operations, not a rate. Thresholds should be cited from the Commission guidelines themselves. Not legal advice.

## Relevance to GroundOne
- **LoRA fine-tuning does not make GroundOne a GPAI provider.** Back-of-envelope estimate (not in the source; 6·N·D rule with Qwen2.5's 18T pre-training tokens from [[Qwen2.5]]): the 3B base is about 3×10^23 FLOPs and the 0.5B about 5×10^22 FLOPs. A LoRA run on a single laptop is many orders of magnitude below one third of either. The modification criterion is therefore not met. In any case, GroundOne is a research prototype not placed on the market, and a narrow verifier ([[LoRA]]).
- **Interesting edge case.** By the same estimate, Qwen2.5-3B would sit above the 10^23 FLOPs GPAI presumption and the 0.5B below it. This concerns Alibaba as provider, not the thesis, and it rests on an estimate. Mention it only as an illustration, flagged as an estimate.
- **Licence conditions are stricter than "open weights".** The exemption requires unrestricted use and no monetisation. A research-only licence such as Qwen2.5-3B's "Qwen Research" licence would presumably not qualify ([[Open-Weight Models|Model Licences]]). This reinforces the open-weight vs open-source distinction drawn from [[OSI 2024 - The Open Source AI Definition 1.0]].
- **Not a locality argument.** The AI Act regulates providers, not where inference runs. Privacy benefits of local inference should be argued from data-protection law and threat models ([[On-Device Inference]]).

## Links
- Concepts: [[LoRA]], [[Qwen2.5]], [[On-Device Inference]], [[Open-Weight Models|EU AI Act]] (proposed), [[Open-Weight Models|Model Licences]] (proposed), [[Open-Weight Models]] (proposed)
- Related sources: [[Stanford CRFM 2024 - Foundation models under the EU AI Act]], [[OSI 2024 - The Open Source AI Definition 1.0]], [[Hu 2022 - LoRA]], [[Qwen Team 2024 - Qwen2.5 Technical Report]]
