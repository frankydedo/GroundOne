---
type: concept
tags: [system-one, open-source, logit-readout, lora, baseline, jev]
---
# Rizzo-Flow

**Rizzo Flow** is an open-source (Apache-2.0), local-first [[System One Models|System One]] server by Simone Rizzo / Rizzo AI Academy ([[jev_simone_rizzo]]). It exposes the same HTTP interface as [[Jev]] (`POST /v1/systemone`), so TypeSafe clients can point at `localhost`, plus a richer native API (`POST /v1/decisions`). Inspired by [[SemIf]]. Repo: https://github.com/Rizzo-AI-Academy/rizzo-flow (local: `SystemOne_repos/rizzo-flow`).

## Design
- **Model**: XHToken **Spark-X2.5-4B** (default) or **1.7B**, Apache-2.0, native 1M-token context (default limit 8,192 per question). Since 2026-09-25 the default weights include Rizzo-Flow's own LoRA fine-tune (`rizzoaiacademy/rizzo-flow`, `rizzo-flow-1.7b`); `--weights base` gives the originals.
- **Runtime**: llama.cpp b11081 via ctypes (Metal, CUDA, Vulkan, ROCm, SYCL, CPU); quantisations Q8_0 (default, 4.4 GB), Q4_K_M, BF16. **MLX** runtime still available (`--backend mlx`), bit-identical weights.
- **Readout**: each option → one uppercase letter (single token, checked at request time; ≤ 26 slots). One forward pass; softmax over the allowed letters' logits at the answer position. No sampling, no parsing.
- **Shared-prefix KV branching**: the state is prefilled once; all question branches share its [[KV Cache]] cells and run as one unpadded micro-batch ([[Prefill and Decode]]). E.g. 8 yes/no questions on a 218-token contract: 136 ms total.
- **Primitives**: `boolean`, `choice`, `score` (probability-weighted level), `numeric` (anchors, median, out-of-range probabilities); built-in abstention options (`__insufficient__`, `__below_range__`, `__above_range__`) with typed `status`.
- **Calibration**: per-primitive temperature scaling (`rizzo calibrate`) bound to a fingerprint of weights + precision + runtime + backend + prompt.

## Fine-tuning (see [[Rizzo-Flow training]])
- **Objective**: soft cross-entropy between a target distribution and the softmax over **answer-letter logits** at the last prompt position, `−Σₖ targetₖ log softmax(z_letters)ₖ`; prompt identical to inference. Targets: exact probabilities for programmatic labels, vote distributions for soft human labels, one-hot with 0.03 label smoothing for hard human labels.
- **[[LoRA]]**: r 16, α 32, dropout 0.05, all attention+MLP linears; embeddings/`lm_head` frozen (tied). 32.4M params (4B), 16.7M (1.7B).
- **Data**: 28,321 public questions (tasksource, Open-Jev, jev-bench), no Jev outputs, substring contamination filter.
- **Schedule**: AdamW 5e-5, 3% warmup + cosine, 16 questions/step, 1 epoch (1,770 steps): 41 min (4B), 19 min (1.7B) on an RTX PRO 6000.

## Measured results (maintainers; Windows 10 + RTX 5060 Ti unless noted)
| Benchmark | Base 4B | Fine-tuned 4B | Fine-tuned 1.7B | Reference |
| --- | ---: | ---: | ---: | ---: |
| typed-decisions accuracy (2,000 decisions) | 0.574 | **0.648** [+0.050, +0.101] | 0.544 (+0.014, n.s.) | Jev card 0.727 |
| typed-decisions ECE | 0.349 | **0.112** | 0.169 | – |
| typed-decisions Brier / KL | 0.480 / 2.899 | 0.205 / 0.452 | 0.275 / 0.694 | Jev 0.148 / 1.442 |
| SemIf `authored144` | 0.812 | 0.845 | – | SemIf Q8 0.819 (tied) |
| SemIf `perturbations108` | 0.848 | **0.946** | – | SemIf 0.766 |
| Missing evidence (36 rows) | 0.750 | **0.583** (worse) | – | SemIf 0.861 |
| Latency, short decision (Q8_0) | 49/52 ms p50/p95 | same | 25/27 ms (base) | – |
| Shared-state throughput `shape777` | 20.99 dec/s (vs 2.60 fresh) | same | 31.59 (base) | SemIf 3090: 20.03 |

Only Apple number: MLX on M4 Pro, Q8, older prompt v2: 254 ms per short decision, 3.92 dec/s shared.

## Stated limitations
- Uncalibrated by default; `status: ok` ≠ correct; Jev confidence thresholds do not transfer.
- Under-uses abstention; 5–6 confident wrong answers of 36 on missing evidence (SemIf 1).
- Residual position bias, no permutation debiasing; Q8_0 shared-prefix scoring flips near-ties (13/777).
- 1.7B fine-tune improves probabilities but not accuracy.
- Gold labels of typed-decisions come from a ~4B teacher; Jev numbers taken from a dataset card.
- Tested by maintainers only on Windows + NVIDIA; one resident model; not hardened.

## Relevance to GroundOne
- **External baseline**: same family as GroundOne (LM-head letter readout), runs on the M4 Mac (MLX or llama.cpp Metal), Jev-compatible API → a `noul` question per RAG sentence is a direct zero-shot baseline for [[Groundedness Verification]].
- Its training objective is the published analogue of GroundOne's; its results suggest fine-tuning mainly improves [[Calibration]] and robustness, with accuracy gains that shrink at small scale — a risk for the 0.5B model.
- Its regression on missing evidence is the failure mode that matters most for [[Hallucination Detection]].

## Related
- [[GroundOne]], [[Rizzo-Flow README]], [[Rizzo-Flow training]], [[SemIf]], [[CLM]], [[System One Models]], [[Jev Input and Output Format]]
