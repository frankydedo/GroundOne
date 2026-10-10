---
type: source
author: "Cho Yin Yong"
date: 2026-10
venue: "Hugging Face dataset card, choyiny/decidebench v1.1, revision 0739e9b (retrieved 2026-10-10)"
url: "https://huggingface.co/datasets/choyiny/decidebench"
tags: [source, dataset-card, benchmark, decision-models, cost, latency, jev, laya]
---
# Yong 2026 – DecideBench dataset card

**Raw file**: `raw/Yong 2026 - DecideBench dataset card_ingested.md`

## Overview
DecideBench measures **accuracy, cost per decision and latency together** for 20 decision models (TEV both hosted and self-hosted) and 3 general-purpose LLMs. It reports Pareto frontiers instead of a single ranking. **400 multiple-choice decisions in 200 contrastive pairs**, 50 in each of 8 task families: action review, agent routing, **claim support**, content moderation, returns policy, review sentiment, support intent, ticket triage. Each item has a state, a question and 3–6 options with one-sentence descriptions. The two halves of a pair differ by one small edit that flips the answer (a negation, a date one day past a window), so topic matching gets one half wrong. *Pair accuracy* counts pairs with both halves right. Results were measured from 2026-09-28 to 2026-10-09. Code MIT, data CC BY 4.0.

**Claude wrote every item**; none comes from public datasets. Test labels were validated structurally and spot-checked, and the worked examples were checked by two other models.

## Key Insights
1. **Headline results** (accuracy / pair accuracy):

| Entry | Accuracy | Pair acc. | `claim_support` | Cost per 1M tasks | p50 latency |
| --- | ---: | ---: | ---: | ---: | ---: |
| DeepSeek-V4-Flash (general LLM) | 99.8 % | 99.5 % | 100 % | $197.28 | 1,866 ms |
| **JEV** (hosted, via AI Space) | **98.0 %** | 96.0 % | 96 % | $32.26 | 639 ms |
| GPT-6 Luna (OpenAI Decisions) | 97.2 % | 94.5 % | 98 % | $52.82 | 126 ms |
| imajev-4b (best open, self-hosted) | 95.0 % | 90.5 % | 94 % | $28.57 | 499 ms |
| TEV (self-hosted) | 92.8 % | 86.0 % | 90 % | $46.82 | 823 ms |
| Jeff Qwen3.5-0.8B (self-hosted) | 71.2 % | 49.5 % | 82 % | $9.84 | 43 ms |
| **Laya typed-decisions 421M** (zero-shot) | **59.8 %** | 36.5 % | 76 % | $5.45 | 97 ms |
| GLiNER2.5-Decide 340M | 57.0 % | 30.5 % | 52 % | $14.96 | 255 ms |
| CLM-v0.1-8B (zero-shot) | 41.0 % | 11.0 % | 44 % | $10.46 | 156 ms |
| Julia-1 144M (zero-shot) | 34.8 % | 8.0 % | 24 % | $3.31 | 58 ms |
| Random | 22.2 % | 4.5 % | 36 % | – | – |

2. **Encoders score 35–60 %.** Laya, GLiNER2.5-Decide, CLM and Julia-1 often give both halves of a contrastive pair the same answer: they match topic, not the decisive detail.
3. **JEV is the cheapest model above 95 %.** The general LLMs that beat it cost 6–14× more. JEV's zero-shot accuracy (98.2 %) equals its accuracy with worked examples.
4. **Protocol.** Chat models get TEV's system prompt and answer with one letter at temperature 0. One solved example per option is shown before each item where an entry can take it. **Laya, CLM and Julia-1 run zero-shot**, because these encoders have no place for examples. Self-hosted entries ran on an NVIDIA L4 and are priced by GPU time at $0.81/h. Self-hosted latency is measured on the GPU box at 4 requests in flight, so a serial server reports about 4× its per-request time. Hosted latency includes the network.
5. **Limitations stated.** An LM wrote the items; a careful reader could dispute a few labels (TEV and JEV miss the same 6 items, 3 of them arguable). 400 items give wide family-level intervals. The items are public, so later models may be trained on them (a canary string is provided).

## Relevance to GroundOne
- **Claim support is the nearest family to groundedness**, but it has only 50 items, document-free short states, and LLM-written labels. It does not measure sentence-level, three-way verification of RAG answers. Jev reaches 96 %, Laya 76 %, a 0.8B decoder 82 %.
- **Contrastive pairs are the right probe for GroundOne's blind spot.** A one-edit pair is exactly a sentence that copies the source but alters a detail. Pair accuracy, not plain accuracy, exposes topic matching. GroundOne's error analysis (contradicted recall 0.24 / 0.36 in the high-overlap bin) measures the same weakness from another angle ([[GroundOne Results]]).
- **Cost and latency on a common footing** (one GPU type, one price) is a cleaner protocol than mixing runtimes. GroundOne's latency claims stay within one runtime for the same reason.
- **Evidence quality:** LLM-written items and labels, and an unequal protocol (examples for decoders, none for encoders). Encoder results are therefore a lower bound.

## Links
- Concepts: [[Decision-Model Benchmarks]], [[Hugging Face decision-models Tag]], [[Laya]], [[Jev]], [[CLM]], [[Groundedness Verification]]
- Related sources: [[Benchmark Heaven 2026 - JevBench v1.6.1 dataset card]], [[morrenhale 2026 - Decision benchmark Jev vs Laya vs Julia-1 dataset card]]
