---
type: source
author: "Damien Sileo (tasksource)"
date: 2026-10-09
venue: "Hugging Face dataset card, tasksource/tasksource-jev-typed-decisions, revision 477db75 (retrieved 2026-10-10)"
url: "https://huggingface.co/datasets/tasksource/tasksource-jev-typed-decisions"
tags: [source, dataset-card, training-data, decision-models, tasksource, jev, typed-decisions]
---
# Sileo 2026 – tasksource-jev-typed-decisions

**Raw file**: `raw/Sileo 2026 - tasksource-jev-typed-decisions dataset card_ingested.md`

## Overview
A training corpus for Jev-style decision models: **about 2.5 million typed decisions from 670 sources** (over 300 dataset families), recast from the tasksource catalogue (Sileo, LREC-COLING 2024) into one schema: `state`, `question`, `kind` (`choice`, `score`, `noul`), `options`, and `target` (a distribution over options, or `[p]` for `noul`). Labels come from the source datasets ("not a teacher model"). Soft targets are kept where sources have mean ratings or at least five annotator votes (STS, ChaosNLI, civil_comments and others).
- `default`: a steered mix of about 1M train rows (1,031,657), 15,550 validation and 16,247 test.
- `full`: every row that passed the build (2,529,342 train).
- `filtered-full`: 1.3M rows with commercial-licence gating, benchmark-overlap filters and a GLM-5.3-Flash review.
- `vision`: a multimodal pilot (66,085 train).

Licence: `other`; each row carries its source's licence and a `license_use` field (commercial / non-commercial / unspecified).

## Key Insights
1. **Construction against shortcuts.** Options are shuffled per row. Validation and test rows whose content appears in train are removed. Derived questions are chosen without looking at the answers. Evaluation benchmarks (BIG-bench, MMLU, BLiMP, MATH test) are left out. Up to 10 % of each classification task is packed into multi-question states sharing a `group_id`.
2. **Jev shapes the mixture, not the labels.** In `full`, per-task **audit weights come from a check of Jev on 200 examples per task**: ×1.5 for hard tasks with gold correct by construction, ×0.5 for near-solved tasks and for judgment-call tasks. In `default`, each source's score multiplies label correctness, a "zone of proximal development" term (**how much probability the decision models Jev and Liquid D1 give the gold answer**), interest and cleanliness judged by Jev yes/no checks, ×0.6 for two-option tasks, and ×2 for sources picked by hand.
3. **Format shares (full).** 47 % classification, 30 % multiple choice, 3 % token labelling, 10 % graded (soft labels), 10 % procedural. Buckets in `default` include 9 % long documents and fact-checking, and 10 % NLI.
4. **Sibling dataset.** `tasksource/procedural-typed-decisions` adds exact counting, arithmetic, retrieval, state tracking, routing among up to 60 options, and exact posteriors under uncertain roles.
5. **Licence caution.** The card calls itself "a best-effort aid, not legal advice". The vision config is a mixed-licence research pilot (FigureQA rows are flagged `redistribution: prohibited`).

## Relevance to GroundOne
- **Training-data lineage of the open baseline.** [[Rizzo-Flow]] did **not** train on this corpus. Its training documentation lists the sibling `tasksource/procedural-typed-decisions` (11 configs, rule-exact labels), plus Open-Jev and jev-bench ([[Rizzo-Flow training]]).
- **Indirect teacher influence.** Labels come from real datasets, but source weights depend on Jev's and Liquid D1's probabilities. A model trained on `default` inherits a selection bias towards what those models find "interesting", even without distillation.
- **Overlap risk for GroundOne's tests.** The card does not say whether VitaminC, LLM-AggreFact sources or RAGTruth are among the 670 sources (that would need `sources.yaml`, not ingested). Any baseline trained on this corpus and evaluated on T2/T3 would need that check.
- GroundOne's own training set is RAGTruth only and frozen ([[Datasets for GroundOne]]); this corpus is related work, not a candidate.

## Links
- Concepts: [[Rizzo-Flow]], [[Decision-Model Benchmarks]], [[Hugging Face decision-models Tag]], [[Jev]], [[Datasets for GroundOne]]
- Related sources: [[Rizzo-Flow training]], [[Rizzo-Flow README]]
