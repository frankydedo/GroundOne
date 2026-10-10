---
type: source
author: "Pritam Deka (Queen's University Belfast)"
date: 2026
venue: "arXiv 2610.02486 v1 (1 Oct 2026)"
url: "https://arxiv.org/abs/2610.02486"
tags: [source, paper, system-one, decision-models, encoder, rlcd, cross-entropy, temperature-scaling, calibration, biomedical, option-order]
---
# Deka 2026 – From Retrieval to Typed Decisions (SBERT2S1)

**Raw file**: `raw/Deka 2026 - From Retrieval to Typed Decisions SBERT2S1 (arXiv 2610.02486)_ingested.pdf`

## Overview
The paper asks whether biomedical sentence encoders trained for retrieval are good starting points for typed decision models ("answer schema-constrained questions about a text in one forward pass and return probabilities meant to be thresholded"). It introduces **SBERT2S1** (converting Sentence-Transformers encoders into bi-encoder B, cross-head C and prior-fused residual PFR decision models), **BIODECIDE** (a biomedical typed-decision suite) and **MEDLINE-S1** (242,986 training decisions from NLM indexing). Single author; three seeds per configuration; Holm-corrected tests. It is the most careful published ablation of the open **RLCD recipe** (the one released with [[Laya]]).

## Key Insights
1. **Heads.** The cross head C beats PFR by 1.3–2.4 seen-task points under all five objectives and by 3.8–10.2 on held-out tasks. The bi-encoder B matches C on seen tasks but loses 9.4 held-out points; its value is precomputed state embeddings. PFR (which keeps the retrieval prior) is almost option-order invariant: a random permutation changes 0.3 % of answers vs 15.7 % for C.
2. **RLCD trails plain cross-entropy.** On S-PubMedBERT-MS-MARCO, CE, a proper-scoring objective and a reparameterised estimator are within one point; the released RLCD recipe (PG) trails CE by **3.0 (PFR) and 2.5 (C) points** (Holm p = .005), with a fourfold larger seed SD for PFR. Cause: its reward normalisation makes the score-function estimator 3.6–3.8, 5.7–6.1 and 14–15× too large at noise σ = 0.4, 0.25, 0.1. A leave-one-out baseline (PG-LOO) recovers most of the gap (+2.5 / +1.5).
3. **No calibration benefit after temperature scaling.** RLCD has the lowest raw ECE (7.0 vs 9.3 for CE with PFR), but after temperature scaling all objectives lie between 3.6 and 4.4 (×100) and RLCD has the worst NLL. "Any benefit claimed for a training objective must therefore survive temperature scaling."
4. **Encoders vs LLMs.** Fine-tuned encoders beat zero-shot Gemma-4-31B and Qwen3.8-27B on seen tasks (70.2 for S-PubMedBERT C with CE, 75.0 for fine-tuned Laya-large, vs 65.7 / 57.4) with better post-scaling ECE (3.8–4.3 vs 8.5–9.1), but the LLMs win on held-out tasks (Gemma 52.6 vs 31.0) and the clinical track. Escalating the 20 % least confident questions to Gemma raises macro accuracy from 59.5 to 68.4 (retrospective budget, not a validated threshold).
5. **Speed.** A ten-question request takes 6.6 ms (C), 15.2 ms (PFR) and 22.7 ms (Laya-large) for the forward pass, batch 1, on an MI300X.

## Relevance to GroundOne
- **Independent support for GroundOne's training choice.** GroundOne trains with class-weighted cross-entropy restricted to the answer letters and calibrates post hoc with temperature + bias ([[Calibration]]). Deka shows that, once temperature scaling is applied, the open RLCD recipe brings no calibration advantage over CE and costs accuracy ([[Reinforcement Learning with Calibrated Decisions]]).
- **Seed variance.** RLCD's fourfold seed SD is another data point for [[Fine-tuning Instability and Seeds]].
- **Specialists vs LLMs are complementary**: in-domain a small specialist wins, out of domain the large LLM wins, matching GroundOne's T1 vs T3 pattern ([[When System One Beats an LLM]]).

## Links
- Concepts: [[Reinforcement Learning with Calibrated Decisions]], [[Calibration]], [[System One Models]], [[Laya]], [[Fine-tuning Instability and Seeds]], [[Selective Prediction]]
- Related sources: [[Nandakishore 2026 - Laya as a Typed Probabilistic Assessor (arXiv 2609.33843)]], [[Convai Innovations 2026 - Laya model card]], [[Guo 2017 - On Calibration of Modern Neural Networks]]
