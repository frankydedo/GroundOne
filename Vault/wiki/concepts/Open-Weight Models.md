---
type: concept
tags: [concept, open-weight, open-source-ai, licences, osi, eu-ai-act, capability-gap, qwen, locality-pillar]
---
# Open-Weight Models

Models whose trained weights are published for download and local use. **Open-weight is not open source**: the Open Source Initiative's definition also requires the code and enough information about the data to rebuild the model. Open weights are what make local inference, fine-tuning and logit access possible, and hence what makes [[GroundOne]] possible.

## Definitions
- **OSI Open Source AI Definition 1.0 (2024)**: four freedoms (use, study, modify, share). The "preferred form for modification" must include data information, code and parameters. Weights alone do not qualify; the data itself need not be released ([[OSI 2024 - The Open Source AI Definition 1.0]]).
- **Openness as a scale.** Artificial Analysis's Openness Index scores weights, pre-training data, post-training data, methodology and licence. OLMo scores 89, Nemotron Nano 9B v2 67; no model reaches the maximum; gpt-oss has Apache-2.0 weights but discloses little else ([[Artificial Analysis - Announcing the Openness Index]]).
- **Terminology for the thesis**: Qwen2.5 is **open-weight**, not open source. Licences differ by size: the 0.5B is Apache 2.0, the 3B is under the Qwen Research licence ([[Qwen2.5]]).

## The capability gap is closing
| Measure | Finding | Source |
| --- | --- | --- |
| Chatbot Arena | closed lead fell from 8.04 % (Jan 2024) to 1.70 % (Feb 2025) | [[Stanford HAI 2025 - AI Index Report, Technical performance]] |
| Epoch Capabilities Index | Jan–May 2026: open models lag by 4 months on average (6 under a strict criterion), 8 ECI points (90 % CI 7–11); 3 months over 2023–Oct 2025 | [[Epoch AI - Open vs closed capability gap (ECI)]] |
| Consumer-GPU models | models that fit one consumer GPU (≤ 27–28B on an RTX 4090, ≤ 40B on an RTX 5090) reach frontier performance after 6–12 months; open models improve faster on Arena (+125 vs +80 Elo/yr) | [[Epoch AI 2025 - Frontier AI performance becomes accessible on consumer hardware within a year]], [[Epoch AI 2025 - What's the best model you can run on a single consumer GPU]] |
| Small models | smallest model above 60 % MMLU: PaLM 540B (2022) → Phi-3-mini 3.8B (2024), 142× fewer parameters | Stanford HAI 2025 |

Drivers named by Epoch: open labs scale compute as fast as closed ones, distillation, and growing GPU memory. Caveat: the comparison counts only models whose full weights fit, which biases against [[Mixture of Experts]] models. The open leaders in the ECI table are mostly Chinese labs (top open: Kimi K2.6, 151.6 vs GPT-5.5 Pro 159.4).

## EU AI Act and open models
- **General-purpose AI models**: presumed above 10^23 training FLOPs (about 1B parameters); systemic-risk presumption at 10^25 FLOPs. Obligations for GPAI providers apply from 2 Aug 2025, enforcement from 2 Aug 2026 ([[WilmerHale 2025 - Commission guidelines for providers of general-purpose AI models|WilmerHale 2025]], secondary; cite the Commission guidelines).
- **Open-source exemption**: requires a free licence, no monetisation and no systemic risk; copyright duties and the training-data summary still apply ([[Stanford CRFM 2024 - Foundation models under the EU AI Act|CRFM 2024]], WilmerHale). Research and prototyping before market placement are excluded.
- **Fine-tuners**: become providers only if the fine-tuning uses more than one third of the original training compute. GroundOne's LoRA runs are orders of magnitude below that (WilmerHale page; own 6ND estimate: Qwen2.5-3B ≈ 3×10^23 FLOPs).

## Relevance to GroundOne
- Open weights are a precondition of the locality pillar: no download, no local model; no logits, no System One readout or calibration ([[On-Device Inference]]).
- The closing gap supports the motivation of Ch. 1: capable models now run on consumer hardware, so a local pipeline is realistic and a local verifier is needed.
- The thesis should state licences precisely (Apache 2.0 vs Qwen Research) and use "open-weight" consistently.

## Links
- Concepts: [[Qwen2.5]], [[Small Language Models]], [[On-Device Inference]], [[Local Inference Hardware]], [[Privacy and Data Sovereignty]], [[LoRA]], [[Mixture of Experts]]

## Snapshot of 2026-10-20 (Artificial Analysis Intelligence Index v4.3.2)
- Best closed 58 (Claude Opus 5.5) vs best open-weight 46 (MiMo-V2.6-Pro); several open-weight models (DeepSeek V4.1 Flash, GLM-5.3, Kimi K3) match mid-tier closed models; all of them are "large", while the only "small" model in the chart (Qwen3.8 27B) scores 34 ([[Artificial Analysis 2026 - Intelligence Index snapshot (2026-10-20)]]). Used in thesis Ch. 2 §2.2.2 next to the Epoch AI trend.

## Licences of the GroundOne components (2026-10-22)
- Qwen2.5-0.5B Apache 2.0 vs Qwen2.5-3B Qwen Research License (research and evaluation only): GroundOne 3B and the 3B demo generator are research-only; d1-3B's LFM Open License 1.0 caps commercial use at USD 10 M revenue ([[Licences 2026 - GroundOne components (collected 2026-10-22)]]).
