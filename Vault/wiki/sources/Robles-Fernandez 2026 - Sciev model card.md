---
type: source
author: "Angel Luis Robles-Fernández (alrobles)"
date: 2026
venue: "Hugging Face model card, alrobles/sciev, revision c47ddeb (retrieved 2026-10-10)"
url: "https://huggingface.co/alrobles/sciev"
tags: [source, model-card, decision-models, masked-diffusion, llada, scientific-ml, calibration, sciev]
---
# Robles-Fernández 2026 – Sciev model card

**Raw file**: `raw/Robles-Fernandez 2026 - Sciev model card_ingested.md`

## Overview
Sciev is an open "System-One" scientific decision layer: **typed decision heads on a frozen LLaDA-8B-Instruct masked-diffusion backbone**. A state plus typed questions (`choice` / `noul` / `score`) give structured decisions with probabilities "in **one forward pass per decision**", with no generation and no parsing. Released heads: `fr_choice.pt` (AttnPoolHead, 67.2M), `fr_noul.pt` (MLP, 16.8M), `fr_score.pt` (MLP with an ordinal auxiliary loss, 16.8M), plus experimental "adapted-arm" heads (`da_*`). The backbone is downloaded separately and keeps its own licence. Code and heads: Apache-2.0. The manuscript is hosted at sciev.org, "in preparation for arXiv submission" ([[Robles-Fernandez 2026 - Sciev Typed Scientific Decisions Without Generation (manuscript, sciev.org)]]).

## Key Insights
1. **Results (matched study, 3 head seeds), frozen vs adapted arm:**
   - internal choice (n = 448): 0.970 vs 0.961
   - internal noul (n = 1,200): 0.925 vs 0.913
   - internal score (n = 1,218): 0.859 vs 0.779
   - GPQA main (n = 441): 0.295 vs 0.288
   - **SciFact noul (n = 332): 0.483 vs 0.709**
2. **Caveats stated by the author.** The internal battery uses constructed distractors and synthetic score labels. **With the passage removed, the frozen choice head still agrees with the reference on 87.5 % of items.** The adapted heads use one archival LoRA adapter whose loss is not LLaDA's native estimator. External evaluations informed candidate selection, so they are exploratory, not an untouched test. Temperatures must be fitted on held-out dev data for the target distribution.

## Relevance to GroundOne
- **A third backbone family for System Ones**: a diffusion LM with trained heads, beside encoders with per-option heads ([[Laya]]) and decoder letter readouts (GroundOne). See [[System One Models]].
- **The closest result to GroundOne's task is weak.** SciFact binary verification with the release heads is 0.483, below the 0.596 majority reference given in the manuscript. High internal accuracy did not imply evidence use: the passage-removed control shows strong evidence-independent predictability. GroundOne's sentence-only classifier control (0.570 three-way on T1) addresses the same risk.

## Links
- Concepts: [[System One Models]], [[Decision-Model Benchmarks]], [[Hugging Face decision-models Tag]], [[Calibration]]
- Related sources: [[Robles-Fernandez 2026 - Sciev Typed Scientific Decisions Without Generation (manuscript, sciev.org)]]
