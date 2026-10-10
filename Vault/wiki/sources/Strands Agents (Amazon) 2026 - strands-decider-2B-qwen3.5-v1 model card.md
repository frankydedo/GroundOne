---
type: source
author: "Strands Agents (strands-labs; files mirrored under the amazon organisation)"
date: 2026
venue: "Hugging Face model card StrandsAgents/strands-decider-2B-qwen3.5-v1-2610, revision 216d1cc (identical card at amazon/strands-decider-2B-qwen3.5-v1-2610, revision 974685f), retrieved 2026-10-10"
url: "https://huggingface.co/StrandsAgents/strands-decider-2B-qwen3.5-v1-2610"
tags: [source, model-card, system-one, decision-models, established-org, lora, readout-head, seeds, model-soup, calibration, strands-decider]
---
# Strands Agents (Amazon) 2026 – strands-decider-2B-qwen3.5-v1 model card

**Raw file**: `raw/Strands Agents (Amazon) 2026 - strands-decider-2B-qwen3.5-v1 model card_ingested.md`

## Overview
A small (2B) open decision model "for agentic AI" from Strands Agents, the agent framework whose files are also published under the `amazon` Hugging Face organisation (the card says the same files are at `amazon/strands-decider-2B-qwen3.5-v1-2610`; it does not itself describe the corporate relationship). It answers `noul`, `choice` and `score` questions with calibrated confidences, for model routing, tool selection, argument checking, triage, guardrails and evaluations. Apache-2.0; code, recipe, data inventory and evaluations at `github.com/strands-labs/strands-decider`. First release 2026-10-09; earlier `strands-decider-2B-hobson-v19/v21` keep their names.

## Key Insights
1. **Architecture.** A LoRA adapter on `Qwen/Qwen3.5-2B-Base` plus a small readout head (`head.safetensors`) that scores the options of a typed question. Runs on `cuda`, `mps` or `cpu`; ships a local `/v1/systemone` server bound to 127.0.0.1.
2. **A seed soup.** The checkpoint averages three training runs (seeds 0, 1, 2) of the same recipe: each layer's LoRA update is the exact mean of the three (stored as one rank-48 adapter), and the three heads are stacked so the soup's option score is the mean of theirs. The soup is then calibrated like any checkpoint. "A soup needs no choice between seeds. It scores at or above its seeds' mean on most measures."
   | Measure | Seeds, mean ± SD | Soup |
   |---|---|---|
   | JevBench public, tasks right of 231 | 179.7 ± 3.8 | 180 |
   | JevBench ECE | 0.076 ± 0.014 | 0.072 |
   | HotpotQA (never trained on) | 0.823 ± 0.002 | 0.832 |
   | Held-out short tasks (6,000) | 0.650 ± 0.009 | 0.653 |
3. **Training.** 246,678 rows in nine parts: public short classification tasks (80,449), multi-step documents (12,909), generated documents, answer adequacy (HelpSteer2 + generated), code (24,533), "gap fill" rows including NLI and 119 sources of tasksource-jev-typed-decisions (96,638), and 22,168 synthetic **rule-application** rows (gold computed by code; kept only where gemma-4-31B and Claude both agree with the code). **Teacher:** gemma-4-31B-it output distributions are training targets where its answer equals the gold label. A KL term (weight 0.3) anchors the model to the released hobson-v19, not to the untrained base. One epoch per run on 8× A100 (about 79 min each). Training datasets listed in the metadata include `tals/vitaminc`, `tasksource/doc-nli` and `pietrolesci/nli_fever`.
4. **Contamination checks.** Licence check, a 13-gram overlap filter against JevBench public tasks, the Decision Index suite, HotpotQA dev and the held-out sets; the 4,096-token window; hand reading of samples.
5. **Calibration and limits (stated).** "Calibration is one temperature per primitive, fitted on held-out short classification. The confidence bands are established there only: measure on your own traffic before you trust a threshold." Questions are read less than documents (a changed question often keeps the same answer); long multi-step documents are the weak spot (JevBench hard tier far below easy); `score` and `noul` transfer poorly to unlike rubrics. On the Decision Index (balanced skill) the soup scores 30.82 with the training harness.
6. **Image path untrained.** With `--vision` the Qwen3.5 vision tower is kept and nothing is trained on images; without the image the model still answers with mean confidence 0.711 (NaturalBench) and 0.834 (POPE), ECE 0.211 and 0.334: "Do not use its confidence to detect a missing, blank or unreadable image."

## Relevance to GroundOne
- **Seed instability has an industrial answer.** GroundOne saw one collapsed seed out of three ([[Fine-tuning Instability and Seeds]]). Strands averages three seeds' LoRA deltas and heads into one checkpoint and reports seed means ± SD next to the soup, a reporting standard worth copying and a mitigation GroundOne could cite (it does not fix a collapsed seed, which would have to be excluded first).
- **Same scale and recipe family**: ~2B decoder + LoRA + small head + per-type temperature, like GroundOne's LoRA + restricted readout + temperature/bias ([[System One Models]], [[Calibration]]).
- **"Measure on your own traffic"** matches GroundOne's dev-fitted τ and its finding that calibration does not transfer to VitaminC ([[Selective Prediction]]).
- Training includes VitaminC: a contamination warning for T3 comparisons.

## Links
- Concepts: [[System One Models]], [[Decision-Model Landscape (Hugging Face, 2026)]], [[Fine-tuning Instability and Seeds]], [[Calibration]], [[Selective Prediction]], [[LoRA]]
- Related sources: [[Benchmark Heaven 2026 - JevBench v1.6.1 dataset card]], [[Sileo 2026 - tasksource-jev-typed-decisions dataset card]]
