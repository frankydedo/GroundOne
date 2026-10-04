---
type: source
author: "Liyan Tang, Philippe Laban, Greg Durrett"
date: 2024
venue: "Web leaderboard (llm-aggrefact.github.io), benchmark from MiniCheck (EMNLP 2024); accessed 2026-10-05"
url: https://llm-aggrefact.github.io/
tags: [source, leaderboard, benchmark, fact-checking, grounding, baselines]
---
# Tang 2024 - LLM-AggreFact Leaderboard

**Raw file**: `raw/Tang 2024 - LLM-AggreFact Leaderboard_ingested.md`. This is a markdown capture of the site. The full 39-model table was extracted from data embedded in the page; by default the site shows only 11 models.

This is the live leaderboard for [[LLM-AggreFact]]. The site describes the benchmark as aggregating **11** public grounded-factuality datasets. The paper version had 10 ([[Tang 2024 - MiniCheck]]); the leaderboard adds **RAGTruth** as a column. The score is **balanced accuracy (BAcc)** per dataset, and the "Average" column is the unweighted mean of the 11 BAcc values (capture note).

## Overview
- **Columns**: CNN, XSum (from AggreFact-SOTA); MediaS, MeetB (from TofuEval); WiCE; REVEAL; ClaimVerify; FactCheck(-GPT); ExpertQA; LFQA; RAGTruth.
- **Not in the capture**: the expanded "Benchmark Details", Team and Citation sections, the per-dataset sizes of the RAGTruth subset, and the evaluation protocol (threshold, prompt). For those, see [[Tang 2024 - MiniCheck]].

## Selected rows (Average BAcc; RAGTruth column in brackets)
| Rank | Model | Size | Avg | RAGTruth |
|---|---|---|---|---|
| 1 | Bespoke-MiniCheck-7B | 7B | **77.4** | 84.0 |
| 2 | Claude-3.5 Sonnet | – | 77.2 | 86.1 |
| 4 | Granite Guardian 3.3 | 8B | 76.5 | 82.2 |
| 6 | gpt-4o-2024-05-13 | – | 75.9 | 84.3 |
| 7 | Qwen2.5-72B-Instruct | 72B | 75.6 | 81.9 |
| 8 | FactCG-DeBERTa-L | 0.4B | 75.6 | 82.3 |
| 10 | **MiniCheck-Flan-T5-L** | 0.8B | **75.0** | 78.0 |
| 15 | gpt-4o-mini | – | 74.0 | 81.6 |
| 17 | MiniCheck-RoBERTa-L | 0.4B | 73.5 | 77.2 |
| 18 | MiniCheck-DeBERTa-L | 0.4B | 73.1 | 78.8 |
| 19 | **Qwen2.5-7B-Instruct** | 7B | 72.8 | 76.5 |
| 21 | **HHEM-2.1-open** | 0.1B | **71.8** | 69.9 |
| 24 | **AlignScore** | 0.4B | **70.5** | 71.7 |
| 25 | Llama-3.1-8B-Instruct | 8B | 70.3 | 73.6 |
| 26 | GPT-3.5-Turbo | – | 70.1 | 75.6 |
| 33 | **Qwen2.5-0.5B-Instruct** | 0.5B | **64.2** | 51.6 |
| 38 | Llama-3.2-3B-Instruct | 3B | 60.0 | 63.0 |
| 39 | Llama-3.2-1B-Instruct | 1B | 50.3 | 50.9 |

The full table of 39 rows is in the raw file.

## Key insights
1. **Small specialized checkers sit near frontier LLMs.** The best small (<1B) entries score about 75 (FactCG-DeBERTa-L 75.6, MiniCheck-FT5 75.0), within about 2.5 points of the top entry (77.4).
2. **Zero-shot small general LLMs are weak.** Qwen2.5-0.5B-Instruct scores 64.2 on average and **51.6 on RAGTruth** (near chance), and Llama-3.2-1B is at chance (50.3). This is the gap a fine-tuned GroundOne has to close.
3. **The RAGTruth column is relatively easy for strong models** (80–86) but separates small models: AlignScore 71.7, HHEM 69.9, Qwen2.5-0.5B 51.6.
4. **ExpertQA is hard for every model**: all scores fall in 49.9–61.0, which points to label noise or a task ceiling.

The leaderboard does not say which prompt or threshold produced each LLM entry. These are reported numbers, not reproduced ones.

## Relevance to GroundOne
- **Direct baseline table**: GroundOne-0.5B should be compared with **Qwen2.5-0.5B-Instruct (64.2)**, the same backbone run zero-shot. GroundOne-3B has no exact match: **Qwen2.5-3B is not on the leaderboard**; the closest are Llama-3.2-3B (60.0) and Qwen2.5-7B (72.8).
- **Targets**: about 70.5 (AlignScore), 71.8 (HHEM-2.1-open), 75.0 (MiniCheck-FT5) and 77.4 (Bespoke-MiniCheck-7B, the best open model).
- **Model sizes as listed**: HHEM-2.1-open "0.1B", MiniCheck-FT5 "0.8B", AlignScore "0.4B". Note that HHEM's card names flan-t5-base as its base model ([[HHEM]]).
- **Leaderboard links** (for running baselines): `lytang/MiniCheck-Flan-T5-Large`, `lytang/MiniCheck-RoBERTa-Large`, `lytang/MiniCheck-DeBERTa-v3-Large`, `bespokelabs/Bespoke-Minicheck-7B`, `vectara/hallucination_evaluation_model`, `github.com/yuh-zha/AlignScore`.
- **Licence of the benchmark data**: not stated in the capture.

## Links
- Concepts: [[LLM-AggreFact]], [[MiniCheck]], [[HHEM]], [[AlignScore]], [[RAGTruth]], [[Groundedness Verification]], [[Hallucination Detection]], [[LLM-as-a-Judge]], [[Qwen2.5]]
- Related sources: [[Tang 2024 - MiniCheck]], [[Vectara 2024 - HHEM-2.1-Open model card]], [[Zha 2023 - AlignScore]], [[Niu 2024 - RAGTruth]]
