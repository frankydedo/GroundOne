---
type: source
author: "mlboydaisuke (Hugging Face user; runs with coreai-kit by john-rocky)"
date: 2026-09-24
venue: "Hugging Face dataset card, mlboydaisuke/coreai-decision-models-public231, revision b7a859c (retrieved 2026-10-10)"
url: "https://huggingface.co/datasets/mlboydaisuke/coreai-decision-models-public231"
tags: [source, dataset-card, on-device, apple-silicon, core-ai, decision-models, latency, prefill, jevbench]
---
# mlboydaisuke 2026 – Decision models on Core AI (JevBench public231)

**Raw file**: `raw/mlboydaisuke 2026 - Decision models on Core AI (JevBench public231) dataset card_ingested.md`

## Overview
An independent, **on-device** run of eight models from the coreai-kit catalog on the 231 public items of JevBench (easy 48, standard 72, hard 111). Six are decision models; two are chat models asked zero-shot. Machine: **Apple M4 Max, 128 GB**, macOS 27.0, Core AI, **int8** bundles (the laya-multilingual encoder in fp16). JevBench's own harness (commit `2fa63fa`, v1.4.0) sent each item through its stock `typesafe` adapter to `decide-cli serve` on localhost, **one question per request**, and JevBench's own code scored the answers. Every per-item row is published; accuracy, ECE (top label, 10 bins) and latency can be recomputed. The runs date from 2026-09-24. This is not an official JevBench result.

## Key Insights
1. **Accuracy by tier** (hard-tier ECE in parentheses):
   - apus-decision-v1-4b: 1.000 / 0.986 / 0.559 (0.347)
   - system-one-scorer-4b: 1.000 / 0.861 / 0.505 (0.164)
   - decider-0.8b: 1.000 / 0.833 / 0.414
   - qwen3.5-2b-decision: 1.000 / 0.778 / 0.405
   - laya-multilingual: 0.896 / 0.403 / 0.342
   - Published reference rows on the same items, run on each entrant's own stack: Jev 1.13.0 1.000 / 0.986 / **0.730**; Winnow-12B 0.730 hard; SemIf 0.613 hard; Laya (ModernBERT-large) 0.958 / 0.694 / 0.351.
2. **Truncation.** The laya-multilingual bundle reads 256 input tokens, so 95 of 111 hard rows were cut (hard states reach 3,677 tokens). system-one-scorer-4b cuts the state to fit 384 tokens per row (70 of 111 hard rows at the cap).
3. **The re-prefill cost.** For the Qwen3.5-family hybrids (decider-0.8b, openthai-systemone, qwen3.5-2b-decision), "S=1 prefill; **a 3k-token hard state costs 40–220 s per question, re-prefilled for every question** at this kit commit". p95 latencies over all 231 requests: 29.10 s (decider-0.8b), 92.89 s (qwen3.5-2b-decision), 142.09 s (apus-decision-v1-4b, which shared the GPU with two other servers). The laya-multilingual encoder answers in a p50 of 0.02 s, but on truncated input.
4. **Latency is contended and reference only.** The GPU was not reserved, and three models ran as concurrent servers. A solo re-check of 30 items gave bit-identical probabilities at about 2× lower latency (median solo/concurrent ratio 0.43–0.52). The numbers apply to coreai-kit `adbc755`; the later 0.7.0 release was not re-run.
5. **Cascade analysis.** A device-to-hosted cascade is scored from these rows, but its thresholds were chosen on the same 231 items, so its accuracies are optimistic.

## Relevance to GroundOne
- **Direct evidence for one-pass, multi-decision scoring on Apple silicon.** Even on an M4 Max with 128 GB, re-prefilling a long state for every question makes small decoder System Ones take tens to hundreds of seconds per long-document question. GroundOne prefills the document once per answer and reads all K verdicts at markers in the same pass. On a 16 GB M4 it takes 0.41 s (0.5B) and 2.57 s (3B) per answer at K ≥ 14 ([[GroundOne Results]], [[Prefill and Decode]]). The runtimes and documents differ, so this is a contrast of designs, not a benchmark claim.
- **Truncation is the encoder's hidden cost.** A 256-token encoder can be fast only because it reads a fraction of the state. Grounded verification cannot drop most of the document ([[On-Device Inference]]).
- **Locality is feasible but not free.** int8 decision models run fully locally with JevBench-valid output, yet the hard tier stays well below the hosted Jev row. This matches the thesis position that local models need specialisation to compete.

## Links
- Concepts: [[On-Device Inference]], [[Apple Silicon and MLX]], [[Prefill and Decode]], [[KV Cache]], [[Decision-Model Benchmarks]], [[Laya]], [[SemIf]], [[Hugging Face decision-models Tag]]
- Related sources: [[Benchmark Heaven 2026 - JevBench v1.6.1 dataset card]], [[Patel 2024 - Splitwise (prefill vs decode phases)]]
