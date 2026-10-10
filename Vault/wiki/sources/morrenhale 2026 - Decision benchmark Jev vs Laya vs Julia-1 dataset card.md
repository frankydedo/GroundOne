---
type: source
author: "morrenhale (Hugging Face user)"
date: 2026-09-27
venue: "Hugging Face dataset card, morrenhale/decision-benchmark-jev-laya-julia, revision d68bd4b (retrieved 2026-10-10)"
url: "https://huggingface.co/datasets/morrenhale/decision-benchmark-jev-laya-julia"
tags: [source, dataset-card, benchmark, decision-models, calibration, jev, laya, julia-1]
---
# morrenhale 2026 – Decision benchmark Jev vs Laya vs Julia-1

**Raw file**: `raw/morrenhale 2026 - Decision benchmark Jev vs Laya vs Julia-1 dataset card_ingested.md`; data: `raw/morrenhale 2026 - Decision benchmark Jev vs Laya vs Julia-1 results_ingested.json` (all computed metrics)

## Overview
A head-to-head run of three decision engines on **19,776 decisions each** (59,328 inferences, 0 failures), with frozen manifests and all predictions published.
- **jev-1.13.0**: the TypeSafe hosted API.
- **laya 0.3.20**: the shipped `Router`, base checkpoints, zero-shot. The `laya-typed-decisions` checkpoint was **deliberately excluded as train-on-test** on this suite.
- **Julia-1-ONNX**: `model.onnx` on onnxruntime CPU; more than 20 options go through the vendor's tournament router.

Test sets, with gold from the datasets: typed-decisions (2,000; labelled on the card as the "official TypeSafe/Julia suite"), AG News (7,600), DAIR Emotion (2,000), Banking77 (3,076, 77 options per call), MASSIVE scenario (5,100; 51 locales × 100, bare label names as criteria). Metrics: accuracy, macro-F1, Brier, clipped NLL, ECE (15 equal-width bins), p(gold) = 0 counts, and paired target-stratified bootstrap deltas (20,000 resamples, seed 20260927). Probability vectors are renormalised before scoring; Jev's sum to 1 only within 0.01 on 416 rows.

## Key Insights
1. **Overall** (from the results JSON):

| Engine | Accuracy | Macro-F1 | ECE | Brier | p(gold) = 0 | p50 latency (serial probe, n = 250) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Jev 1.13.0 | **0.775** | 0.733 | **0.105** | 0.342 | 1,018 | 322.9 ms (hosted + network) |
| Laya (base, zero-shot) | 0.590 | 0.326 | 0.222 | 0.621 | 1,050 | 42.9 ms (Apple MPS) |
| Julia-1-ONNX | 0.727 | 0.709 | 0.172 | 0.436 | 144 | 16.1 ms (CPU) |

2. **Per dataset (accuracy):**
   - typed-decisions: Jev 0.732 (ECE 0.038), Laya 0.3615, Julia 0.7255. Jev − Laya = +0.3705 [+0.3465, +0.3945].
   - AG News: **Laya 0.927** (ECE 0.015) > Jev 0.892 > Julia 0.859.
   - Emotion: Julia 0.925, Laya 0.599, Jev 0.589. Julia is a large outlier the card does not explain.
   - Banking77: Julia 0.808, Jev 0.800, Laya 0.376 (ECE 0.506).
   - MASSIVE: Jev 0.677, Julia 0.402, Laya 0.302.
3. **The vendor numbers partly reproduce.** Laya's AG News (0.927 vs a claimed 0.950), Emotion (0.599 vs 0.595) and Banking77 (0.376 vs 0.425) land near the card. Its typed-decisions zero-shot number (0.3615) matches the vendor's own "near chance" admission. Jev's ECE on typed-decisions measured here (0.038) is far below the 0.144 and 0.246 attributed to Jev on the Laya card.
4. **Latency is not compute-normalised.** Jev is a hosted API with network round trip, Laya ran on Apple MPS, Julia on CPU.
5. **Provenance note.** This card calls typed-decisions the "official TypeSafe/Julia suite". [[Nandakishore 2026 - Laya as a Typed Probabilistic Assessor (arXiv 2609.33843)|Nandakishore 2026]] states that the dataset and its publisher are independent of TypeSafe. The two descriptions conflict.

## Relevance to GroundOne
- **The best-documented independent zero-shot comparison of an open encoder System One with Jev**: frozen manifests, predictions, paired bootstrap. It is a protocol model for third-party comparisons.
- **Open beats closed only on easy, well-represented tasks** (AG News). On fine-grained or many-option tasks the encoder collapses (Banking77, MASSIVE). This supports the thesis framing that open small models win by specialisation, not zero-shot breadth.
- **Calibration differs by task for the same engine** (Laya ECE 0.015 on AG News, 0.506 on Banking77). Calibration is a property of model × distribution, which is why GroundOne's calibration is fitted per domain on dev and reported as not transferring to T3 ([[Calibration]]).
- No groundedness task is included.

## Links
- Concepts: [[Decision-Model Benchmarks]], [[Laya]], [[Jev]], [[Calibration]], [[Hugging Face decision-models Tag]]
- Related sources: [[Convai Innovations 2026 - Laya model card]], [[Nandakishore 2026 - Laya as a Typed Probabilistic Assessor (arXiv 2609.33843)]], [[Yong 2026 - DecideBench dataset card]]
