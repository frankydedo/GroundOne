---
type: source
author: "Liyan Tang, Philippe Laban, Greg Durrett (Hugging Face dataset card, lytang/LLM-AggreFact)"
date: 2026-10-05
url: https://huggingface.co/datasets/lytang/LLM-AggreFact
tags: [source, dataset-card, benchmark, fact-checking, licence, gated]
---
# Dataset card - LLM-AggreFact

**Raw file**: `raw/Dataset card - LLM-AggreFact_ingested.md` (gated dataset; README read with authentication, accessed 2026-10-05).

## Overview
The Hugging Face card of the **[[LLM-AggreFact]]** benchmark from [[Tang 2024 - MiniCheck]]. It lists the 11 constituent datasets, the schema, the split sizes and the access conditions.

## Key Insights (as stated in the card)
- **Usage condition (gating prompt and body)**: "This resource is permitted for use as an evaluation benchmark. Data in the benchmark should not be used in pretraining or fine-tuning any NLP models." Access requires accepting this.
- **Licence (YAML)**: `cc-by-nd-4.0`.
- **Splits**: dev 30,420, test 29,320.
- **Schema**: `dataset`, `doc`, `claim`, `label` (1 = supported, 0 otherwise), `contamination_identifier` (64-character string added 05.03.2024, following Jacovi et al. 2023, to detect web-crawl contamination).
- **11 datasets**: AggreFact-CNN, AggreFact-XSum (SOTA sets), TofuEval-MediaSum, TofuEval-MeetingBank, WiCE, REVEAL, ClaimVerify, FactCheck-GPT, ExpertQA, LFQA, RAGTruth. (The field table still says "One of the 10 datasets", a leftover from the paper version.)
- **RAGTruth addition (update 08.09.2024)**: converted to the benchmark format, "non-checkworthy claims" removed, and "a randomly sampled subset of the training set from RAGTruth" placed in the **validation** set because the converted training set was too large.
- Claims are "mostly generated from recent generative models (except for one dataset of human-written claims), without any human intervention ... such as injecting certain error types".
- Leaderboard: llm-aggrefact.github.io, 35 models at the time of the update.

## Measured by us
[[GroundOne 2026 - EDA report]] confirms the card's RAGTruth statement: the dev RAGTruth part comes from RAGTruth train and the test part from RAGTruth test. Our per-sub-dataset counts sum exactly to the card's 29,320 test rows.

## Relevance to GroundOne
- **Evaluation only**: GroundOne must not train or fine-tune on any LLM-AggreFact data (dev included). Dev is used only for threshold/temperature selection, and **without** its RAGTruth sub-dataset.
- The `contamination_identifier` field can be used in the leakage check.

## Links
[[LLM-AggreFact]], [[LLM-AggreFact Sub-datasets]], [[RAGTruth]], [[Datasets for GroundOne]], [[Tang 2024 - MiniCheck]], [[Tang 2024 - LLM-AggreFact Leaderboard]], [[GroundOne 2026 - EDA report]]
