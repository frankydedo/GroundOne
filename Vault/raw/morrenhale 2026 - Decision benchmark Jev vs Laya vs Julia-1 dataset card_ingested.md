Source: https://huggingface.co/datasets/morrenhale/decision-benchmark-jev-laya-julia (revision d68bd4b41099ea3ab73ad5b9182072428fae333a) — retrieved 2026-10-10

---
license: cc-by-4.0
task_categories:
  - text-classification
language:
  - en
  - multilingual
tags:
  - benchmark
  - decision-models
  - jev
  - laya
  - julia-1
  - calibration
size_categories:
  - 10K<n<100K
---

# Decision-Model Benchmark 2026-09-27: jev vs laya vs Julia-1-ONNX

Raw data behind the head-to-head benchmark of three decision engines: 19,776 decisions × 3 engines
(59,328 inferences), 0 inference failures. Everything needed to audit or re-score the run.

## Contents

- `manifests/*.jsonl` — frozen test manifests (19,776 decisions): question wording, criteria, option
  order (`keys`), gold key, per-dataset row ids. `manifests/meta.json` records source URLs and
  SHA-256 of every dataset file (typed-decisions pinned rev `c76749ec…`).
- `predictions/{jev,laya,julia-onnx}.jsonl` — 19,776 rows each: predicted key, full probability
  vector over `keys`, gold, latency_ms, engine-specific traces (julia tournament rounds/final
  candidates; jev input_tokens).
- `predictions/*.latency.jsonl` — 250 rows per engine from dedicated serial runs (one engine at a
  time, jev single in-flight). The only latency numbers reported publicly come from these files.
- `results.json` — all computed metrics: accuracy, macro-F1, Brier, clipped NLL, ECE, p(gold)=0,
  per-dataset and per-slice breakdowns, paired-bootstrap deltas (20,000 resamples,
  target-stratified, seed 20260927).

## Test sets (gold comes from the datasets themselves)

| Dataset | Decisions | Source |
|---|---:|---|
| typed-decisions | 2,000 | `LocalLLaMA/typed-decisions` test parquet (official TypeSafe/Julia suite: 600 choice, 800 score, 600 noul) |
| AG News | 7,600 | full test split |
| DAIR Emotion | 2,000 | full test split |
| Banking77 | 3,076 | full test split (77 options per call) |
| MASSIVE scenario | 5,100 | 51 locales × 100 rows, deterministic SHA256-based selection, seed 20260927 |

Question wording and criteria are identical across engines and frozen in the manifests.

## Engines

- **jev-1.13.0** — TypeSafe hosted API (`POST /v1/systemone`)
- **laya 0.3.20** — `NandhaKishorM/laya` shipped `Router`, base zero-shot (the `laya-typed-decisions`
  fine-tuned checkpoint was deliberately excluded: train-on-test on this suite)
- **Julia-1-ONNX** — `SupersonicLabs/Julia-1-ONNX` published `model.onnx` + `model.onnx.data` on
  onnxruntime CPU, native `julia.data.sequence` encoding (strict, max_length=1024, head_length=512);
  >20 options via the official `julia.router.Router` tournament (width=20, survivors=2).
  ONNX↔torch parity verified: argmax 40/40, max |Δlogit| 0.000258.

## Scoring conventions (matters for calibration metrics)

- jev returns probability maps with sum drift up to 0.01 (display rounding is the working
  hypothesis — see the run's error notes); 416 rows affected. laya probabilities pass through
  display rounding (round(4)). All vectors are renormalized before scoring.
- julia Banking77 probabilities are conditional on the final tournament candidate set
  (`probability_scope=final_candidates`) — the vendor's documented Router behavior.
- NLL is clipped; ECE is 15 equal-width bins.

## Caveats

- MASSIVE uses bare label names as criteria (hard zero-shot). The Julia-1 card's 71.5% used scenario
  descriptions — not comparable to the 0.402 measured here.
- Reported latency is end-to-end deployment latency on different hardware (jev: hosted API +
  network RTT; laya: Apple MPS, torch 2.14; julia: onnxruntime CPU), not compute-normalized speed.
- Vendor-claim checks and the full write-up live in the companion report (`BENCHMARK.md` in the
  release zip).

## License

Published dataset rows remain under their original dataset licenses (typed-decisions, AG News,
DAIR Emotion, Banking77, MASSIVE). Prediction and manifest files are CC-BY-4.0.
