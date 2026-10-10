---
type: source
author: "Benchmark Heaven (method repository: fstandhartinger/jevbench)"
date: 2026-10-06
venue: "Hugging Face dataset card, benchmarkheaven/jevbench, revision 47bea8a (retrieved 2026-10-10); leaderboard snapshot generated 2026-10-05"
url: "https://huggingface.co/datasets/benchmarkheaven/jevbench"
tags: [source, dataset-card, leaderboard, benchmark, decision-models, calibration, jev, laya]
---
# Benchmark Heaven 2026 – JevBench v1.6.1 dataset card

**Raw file**: `raw/Benchmark Heaven 2026 - JevBench v1.6.1 dataset card_ingested.md`; data: `raw/Benchmark Heaven 2026 - JevBench v1.6.1 leaderboard_ingested.csv` (94 rows, one per evaluated system)

## Overview
JevBench is a leaderboard for decision models, including Jev-compatible systems, maintained by Benchmark Heaven "independently of TypeSafe AI". The method repository is `github.com/fstandhartinger/jevbench`, the same JevBench harness used in the [[mlboydaisuke 2026 - Decision models on Core AI (JevBench public231) dataset card|Core AI run]]. It scores four axes:
- **Intelligence**: chance-corrected accuracy on a frozen **public** tier and a **sealed** tier;
- **Calibration**: the distribution quality of the typed answers;
- **Speed**: p50 latency on a log scale, with a published adjustment for self-hosted runs;
- **Cost**: USD per 1,000 decisions, mostly **modelled estimates**, not invoices.

**Capability score** = the mean of Intelligence and Calibration. It is the headline on the open-weights board, and only systems inside a cost cap (USD 0.0646 per 1,000 decisions) and an adjusted latency cap (1.23 s) get a capability rank. **Composite score** = a weighted harmonic mean of the four axes with squared penalties. This is release v1.6.1 (2026-10-06, amended through 2026-10-08); the CSV snapshot predates the final publication (2026-10-05). The dataset holds aggregates only: no items, ids or predictions.

## Key Insights
1. **Sealed items prevent independent reruns.** Hosted endpoint versions can be opaque, and cost and latency are modelled or adjusted. The card warns not to compare scores across method versions, and that "a leaderboard score does not establish reliability on your workload".
2. **Selected rows from the leaderboard CSV** (94 rows: 92 ranked, 2 listed):

| System | Capability rank | Composite rank | Intelligence | Calibration |
| --- | ---: | ---: | ---: | ---: |
| Quyet-1.0-Large (Gemma-4-31B decoder, option-letter logits) | 1 | 3 | 73.4 | 90.0 |
| Sage 1.3.0 (Levanto Labs) | 2 | 1 | 65.6 | 91.6 |
| **Jev 1.13.0** (TypeSafe AI) | 4 | 2 | **63.6** | 90.6 |
| torchcast-decision-12b (Gemma-4-12B, option-letter logprob readout) | 5 | 5 | 60.5 | 82.9 |
| SemIf (Qwen3.5-4B) | 28 | 45 | 27.1 | 83.6 |
| Laya typed-decisions | not eligible | 73 | 5.47 | 83.0 |
| openJev Verdict (ModernBERT-base 151M) | 59 | 79 | 4.15 | 49.1 |
| **Laya** (ModernBERT-large 421M) | not eligible | 84 | **1.79** | 63.2 |
| Laya multilingual | 62 | 86 | 0.29 | 33.7 |
| CLM-8B | 60 | 88 | 0.13 | 40.0 |

3. **What the board shows.** The top of the open board is held by **large decoders with option-letter readouts** (Gemma-4-31B, Gemma-4-12B). One of them outranks Jev on capability. Small encoders with fixed heads cluster near zero chance-corrected intelligence. Laya's raw p50 on this board is 0.825 s, far from the vendor's 32.8 ms; latency depends on the runtime and the measurement site.
4. **Name collision.** A separate "metamorphic coherence benchmark" at jevbench.github.io measures a different property.

## Relevance to GroundOne
- **Decoder letter readouts lead the open field.** This is the family GroundOne belongs to ([[Letter-Token Readout]]). The leaders are 12–31B models on GPUs, not 0.5–3B models on a laptop.
- **Chance correction matters.** Laya's 1.79 means "barely above chance" on these items, which raw accuracy figures elsewhere hide. GroundOne reports balanced accuracy and AUROC for the same reason.
- **Not a groundedness benchmark.** The items are general typed decisions. No GroundOne result is comparable to it.
- **Evidence quality:** an independent maintainer with a documented method, but a sealed tier, modelled costs and adjusted latencies. Treat it as a coarse ranking, not as measurements.

## Links
- Concepts: [[Decision-Model Benchmarks]], [[Hugging Face decision-models Tag]], [[Laya]], [[Jev]], [[SemIf]], [[CLM]], [[System One Models]]
- Related sources: [[mlboydaisuke 2026 - Decision models on Core AI (JevBench public231) dataset card]], [[Yong 2026 - DecideBench dataset card]]
