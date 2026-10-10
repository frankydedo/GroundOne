---
type: source
author: "Angel Luis Robles-Fernández (Kansas Biological Survey, University of Kansas)"
date: 2026-09-27
venue: "Manuscript hosted at sciev.org (not on arXiv at retrieval, 2026-10-10)"
url: "https://sciev.org/static/sciev-paper.pdf"
tags: [source, paper, manuscript, decision-models, masked-diffusion, llada, scifact, calibration, evidence-controls, sciev]
---
# Robles-Fernández 2026 – Sciev: Typed Scientific Decisions Without Generation

**Raw file**: `raw/Robles-Fernandez 2026 - Sciev Typed Scientific Decisions Without Generation (manuscript, sciev.org)_ingested.pdf`

## Overview
The manuscript behind [[Robles-Fernandez 2026 - Sciev model card|Sciev]]. Specialist heads read the hidden states of a **frozen LLaDA-8B-Instruct** masked-diffusion backbone. The backbone is used as an encoder of one observed sequence: it neither masks the answer nor runs a denoising loop. Two arms share one head-training recipe and three head seeds: the unadapted backbone ("frozen", fr) and one archival adapted comparator ("da"). Evaluation: an internal scientific battery with constructed reference labels, GPQA, and SciFact. The whole study is recorded as a fingerprinted ledger of 60 evaluation reports. Single author; no peer review.

## Key Insights
1. **Readout.** Context, instructions and options are encoded as one sequence. For `noul` and `score`, the mean-pooled final-layer representation of each option span goes through a shared MLP scorer. For `choice`, a learned query pools each option span at four layers (−1, −9, −17, −25). Probabilities are a softmax over option scores with a dev-fitted temperature. All options come from the same forward pass, but **a request with several questions is processed as several decisions, not one shared forward pass**.
2. **Canonical option order.** Option token sequences are sorted lexicographically and remapped, so any permutation of the options gives the same input: permutation invariance by construction. The author notes this is not semantic robustness, since renaming options or paraphrasing changes the input.
3. **Internal accuracy overstates evidence use.** Frozen arm: 97.0 % / 92.5 % / 85.9 % for choice / noul / score. **With the passage removed, the choice head still agrees with the reference on 87.5 % of items.**
4. **SciFact transfer.** 332 claim–abstract pairs (134 SUPPORT, 69 CONTRADICT, 129 NEI); abstracts are given, no retrieval. Binary SUPPORT vs not: frozen **0.483 ± 0.023**, below the 0.596 majority reference; adapted 0.709 ± 0.020. Three-way: 0.479 vs 0.444 (majority 0.404). GPQA stays weak for both arms (about 0.29).
5. **Calibration does not transfer.** Mean internal ECE for the frozen arm is 0.018 / 0.013 / 0.037 (choice / noul / score), but 0.236 on GPQA and **0.280 on SciFact binary**, with temperatures fitted on internal dev data.
6. **Limitations stated.** External results are selection-informed, not confirmatory. Benchmark text in backbone pretraining cannot be excluded. There is no ranking against proprietary or other open System Ones and **no controlled latency benchmark**. Nothing establishes that an 8B diffusion backbone is necessary or more efficient than smaller encoders.

## Relevance to GroundOne
- **Evidence-removal controls should accompany any accuracy claim.** Sciev's passage-removed control and GroundOne's sentence-only classifier (0.570 three-way on T1) both measure how much can be predicted without reading the evidence.
- **Calibration is distribution-bound.** Internal ECE of about 0.01–0.04 becomes 0.28 on SciFact, the same pattern as GroundOne's calibration not transferring from RAGTruth to VitaminC ([[Calibration]]).
- **Claim verification needs domain adaptation.** The frozen backbone is below majority on SciFact binary; only the adapted arm is useful. This parallels GroundOne's finding that training, not the untrained readout, produces the gain ([[Groundedness Verification]]).
- One pass per decision, without a shared context across questions, is costlier for many decisions per document than GroundOne's marker readout ([[System One Models]]).

## Links
- Concepts: [[System One Models]], [[Decision-Model Benchmarks]], [[Calibration]], [[Groundedness Verification]], [[Hugging Face decision-models Tag]]
- Related sources: [[Robles-Fernandez 2026 - Sciev model card]], [[Guo 2017 - On Calibration of Modern Neural Networks]]
