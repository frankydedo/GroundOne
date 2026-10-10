---
type: source
author: "pranaysuyash (Hugging Face user)"
date: 2026-09-23
venue: "Hugging Face dataset card, pranaysuyash/laya-formatting-fragility, revision 8e2e053 (retrieved 2026-10-10)"
url: "https://huggingface.co/datasets/pranaysuyash/laya-formatting-fragility"
tags: [source, dataset-card, robustness, formatting-sensitivity, decision-models, laya, jev]
---
# pranaysuyash 2026 – Laya Formatting Fragility

**Raw file**: `raw/pranaysuyash 2026 - Laya Formatting Fragility dataset card_ingested.md`

## Overview
A perturbation suite for typed decision models: **480 rows = 40 hand-written, unambiguous base cases × 12 format variants**, across four families (news topic, support department, urgency score 0–3, safety-gate yes/no). Each row pair differs in exactly one formatting axis while the gold stays fixed:
- **phrasing**: three surface forms of the same situation;
- **order**: options in forward vs reversed order;
- **key variant**: semantic option keys vs abstract aliases (`A1..An`, `L0..L3`).

Flip rates compare answers **by option position** within each row's own criteria. Systems: **laya 0.3.5**, **AgentJev-0.6B** (local, shared-prefix runtime) and **jev-1.13.0** (hosted). Measured 2026-09-22/23 with a corrected harness (v2).

## Key Insights
1. **Results:**

| Metric | laya 0.3.5 | AgentJev-0.6B | jev-1.13.0 |
| --- | ---: | ---: | ---: |
| Overall accuracy | 72.7 % | 72.5 % | **90.2 %** |
| Order flip rate | **22.5 %** | 0.0 % | 2.9 % |
| Accuracy forward / reversed | 68.3 / 77.1 % | 72.5 / 72.5 % | 90.8 / 89.6 % |
| Key-rename flip rate | **32.8 %** | 20.0 % | 8.3 % |
| Accuracy semantic / abstract keys | 73.9 / 64.4 % | 71.1 / 70.0 % | 93.9 / 86.7 % |
| Phrasing flip rate | 15.0 % | 23.7 % | 3.7 % |
| p50 latency, 1 question | 20.4 ms (offline) | 26.2 ms (offline) | 863 ms (network) |

2. **Order sensitivity depends on the architecture.** AgentJev's candidate head is permutation-equivariant and shows exactly 0.0 % order flips. Laya is order-sensitive, and reversed order is 8.8 points *more* accurate: a position bias, not noise.
3. **The hosted generalist is the most format-stable** (2.9–8.3 % flips) and leads accuracy by 17+ points. The card's own reading: the case for local models rests on latency, cost, offline operation and fine-tunability, not on zero-shot quality.
4. **Descriptions are load-bearing.** With option descriptions present, key renames cause mild accuracy drops. Reported below-chance collapses under abstract keys likely involve options without descriptions.
5. **Harness errors in the first release.** The first card reported a Laya key-rename flip rate of 87.2 % (now 32.8 %) and an order flip rate of 21.7 % (now 22.5 %). Answers had been compared as raw strings across different label spaces. Community evaluations can be wrong by a factor of more than two before correction.

## Relevance to GroundOne
- **Most of these axes do not apply to GroundOne.** Its prompt, letter mapping (A/B/C) and option order are fixed and trained, not supplied by the caller. Order and key-rename perturbations are therefore out of scope by design.
- **Phrasing is the axis that does apply.** A paraphrase of the answer sentence or of the document should not change the verdict. GroundOne has no paraphrase-robustness test; the thesis should list it as a limitation.
- **Small suite (40 base cases).** The flip rates show direction, not precise magnitudes. The correction note is a reminder to recheck third-party numbers before citing them.

## Links
- Concepts: [[Laya]], [[Decision-Model Benchmarks]], [[Letter-Token Readout]], [[Jev]], [[Hugging Face decision-models Tag]]
- Related sources: [[Azizi 2026 - Labels Override Definitions in Jev-Style Typed Decision Models (arXiv 2610.02586)]], [[Zheng 2024 - LLMs Are Not Robust Multiple Choice Selectors]]
