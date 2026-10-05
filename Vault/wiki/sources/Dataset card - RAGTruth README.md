---
type: source
author: "ParticleMedia (Yuanhao Wu, Cheng Niu et al.); GitHub README"
date: 2026-10-05
url: https://github.com/ParticleMedia/RAGTruth
tags: [source, dataset-card, dataset, rag, hallucination, span-level]
---
# Dataset card - RAGTruth README

**Raw file**: `raw/Dataset card - RAGTruth README_ingested.md` (README of `github.com/ParticleMedia/RAGTruth`, accessed 2026-10-05).

## Overview
The official README of **[[RAGTruth]]**: file format, field definitions, one example per task, and descriptive statistics by task and by generator. Paper: [[Niu 2024 - RAGTruth]].

## Key Insights (as stated in the README)
- **Files**: `response.jsonl` (one row per response: `id`, `source_id`, `model`, `temperature`, `labels` = list of spans with `start`, `end`, `text`, `label_type`, `due_to_null`, `implicit_true`, `meta`; `split` train/test; `quality`; `response`) and `source_info.jsonl` (`source_id`, `task_type` ∈ QA / Data2txt / Summary, `source`, `source_info`, `prompt`).
- **`implicit_true`**: the span is correct but not mentioned in the context. **`due_to_null`**: hallucination caused by a null value. **`quality`**: `incorrect_refusal` (refused despite relevant context) or `truncated`.
- **Task sources** (`source` field): QA from **MARCO** ([[Nguyen 2016 - MS MARCO]]); Data2txt from **Yelp** ([[Yelp Open Dataset]]) as structured JSON business records with reviews; Summary from **CNN/DM** ([[Hermann 2015 - Teaching Machines to Read and Comprehend]]) and recent news.
- **Prompts**: QA asks to answer "strictly based on" the passages and to reply "Unable to answer based on given passages." otherwise (the prompt text says "ten passages" although the sample has 3). Data2txt: "objective overview ... 100–200 words. Don't make up information." Summary: "Summarize the following news within N words". Llama/Mistral used `<s>[INST] {prompt} [/INST]`.
- **Statistics by task**:

| Task | Instances | Responses | Hallucinated responses | Spans |
|---|---|---|---|---|
| Summarization (CNN/DM) | 628 | 3,768 | 1,165 | 1,474 |
| Summarization (Recent News) | 315 | 1,890 | 521 | 598 |
| Question Answering | 989 | 5,934 | 1,724 | 2,927 |
| Data-to-text | 1,033 | 6,198 | 4,254 | 9,290 |
| **Overall** | **2,965** | **17,790** | **7,664** | **14,289** |

- **Statistics by generator** (hallucinated responses / spans): GPT-3.5-turbo-0613 401 / 533; GPT-4-0613 406 / 485; Llama-2-7B-chat 1,832 / 3,302; Llama-2-13B-chat 1,677 / 3,799; Llama-2-70B-chat 1,395 / 2,608; Mistral-7B-Instruct 1,953 / 3,562.
- **Updates**: 2024/02 more annotated hallucinations and the new `implicit_true` meta; 2024/06 training/evaluation code released.
- **Licence**: not stated in the README.

## Relevance to GroundOne
- `source_id` is the grouping key for carving a dev split from train (no context on both sides).
- `implicit_true` enables a third verification rule ("true world knowledge is acceptable"); `quality` lets us drop 173 bad responses ([[GroundOne 2026 - EDA report]]).
- Data2txt alone holds 9,290 of 14,289 spans (65 %), so pooled RAGTruth numbers are dominated by JSON inputs.

## Links
[[RAGTruth]], [[Niu 2024 - RAGTruth]], [[Nguyen 2016 - MS MARCO]], [[Hermann 2015 - Teaching Machines to Read and Comprehend]], [[See 2017 - Get To The Point]], [[Yelp Open Dataset]], [[Datasets for GroundOne]], [[GroundOne 2026 - EDA report]]
