---
type: source
author: "Simone Rizzo (Rizzo AI Academy)"
date: 2026-09-25
url: https://github.com/Rizzo-AI-Academy/rizzo-flow/blob/main/docs/training.md
tags:
  - rizzo-flow
  - lora
  - qlora
  - training
  - soft-labels
language: it
---
# Rizzo-Flow training

Raw file: `raw/Rizzo-Flow training_ingested.md` (Italian; `docs/training.md`, "Fine-tuning LoRA / QLoRA di Spark-X2.5-4B").

## Overview
Step-by-step guide to reproduce the LoRA/QLoRA fine-tune of Spark-X2.5-4B (and 1.7B) for [[Rizzo-Flow]] on an NVIDIA GPU, and to evaluate it on `LocalLLaMA/typed-decisions`. **Snapshot caveat**: the document states that as of 25 Sept 2026 the full run had *not* been executed (first run stopped at step 20/1770, no checkpoint). The [[Rizzo-Flow README]] reports the completed run (41 min on an RTX PRO 6000), so this file documents the pipeline and pre-training checks, not final quality numbers.

## Key Insights

### Training objective (identical to inference)
1. Prompt compiled by the server's own `compile_request` (prompt `spark-decisions-v3`): a training example is byte-for-byte what the model sees in production.
2. One forward pass; read the logits of the **allowed letters only** at the last real position.
3. **Loss = soft cross-entropy**: `loss = −Σₖ targetₖ · log softmax(letter_logits)ₖ`. Target can be one-hot, soft (split human votes), or an exact probability (e.g. 0.667).
4. Only LoRA adapters receive gradients; no other vocabulary token is supervised ("teach to move probability between letters, not to write"). Implementation projects only the last-position hidden state onto the letter rows of the embedding (no full-vocabulary logits).

### Targets
| Type | Target |
| --- | --- |
| `noul` | `[1 − p, p]` (A = no, B = yes) |
| `choice` / `score` | probability per option / level |
| hard human label | one-hot with **label smoothing 0.03** |
| soft human label (`soft_label`) | the vote distribution as is |
| programmatic label (tasksource, Open-Jev) | as is, no smoothing |

### Data
- Sources: `tasksource/procedural-typed-decisions` (11 configs, rule-exact labels), `ZefanCai/Open-Jev` release-v2 (programmatic oracles), `Praveenrajus/jev-bench` (12 of 22 configs, human labels incl. `fever_evidence`, `boolq`, `paws`, `strategyqa_grounded`). **No Jev/TypeSafe labels** (no distillation).
- Exclusions with reasons: noisy Mind2Web, licence issues, configs with > 26 options, `workflow-controls-v1` (same workflows as the benchmark), all test/ood/calibration splits.
- **Contamination filter**: any training state containing a ≥ 60-character string from evaluation sets (typed-decisions test, smoke, perturbations, SemIf authored144/perturbations108/shape777; 703 strings) is dropped; script aborts if a fixture is missing. Result: 0 contaminated states.
- Per-group caps (tasksource 1,400, jev-bench 800, Open-Jev 700 train questions), seed 0. Prompts > 2,048 tokens **dropped, never truncated** (133 train).
- Final: **28,321 train questions, 14.74M tokens** (median 460, max 2,043); dev 2,604. Deterministic build with sha256.

### LoRA / optimisation
- r **16**, α **32**, dropout 0.05, bias none; all attention and MLP linears of 36 layers; embeddings and `lm_head` excluded because they are **tied** (changing them would change the input too). 32.4M trainable (0.8% of 4B).
- AdamW, lr **5e-5** (jev-bench found low lr ~3e-5 better for calibration/generalisation than 1e-4), weight decay 0, linear warmup 3% + cosine to 0, grad-clip 1.0, **16 questions per optimiser step**, 1 epoch = 1,770 steps, seed 0.
- Batch ≤ 8 questions and ≤ 4,096 padded tokens per forward (8,192 OOM on 16 GB); right padding; gradient checkpointing; length-bucketed batches. Model uses eager attention only (quadratic memory) and RoPE positions from `cache_position`, so no sequence packing.
- Pre-flight forward+backward on the two heaviest batches: 2×2043 → 11.48 GiB, 4×1024 → 10.86 GiB.

### Measured on RTX 5060 Ti 16 GB (Windows 10), 25 Sept 2026
- Throughput ~740 prompt tokens/s → 5.5–6.7 h per epoch (LoRA BF16 and QLoRA same speed; compute-bound).
- transformers ↔ llama.cpp parity: 0 token mismatches, 0 argmax flips on 40 decisions, median |Δp| 0.0003, max 0.082 (only on uncertain answers).
- Untrained dev baseline (600 q): loss 1.914, accuracy 0.545. 10-step smoke run: dev loss 1.95 → 1.14.
- **QLoRA NF4 base is much weaker**: on 48 dev questions loss 2.88 vs 1.88, accuracy 0.40 vs 0.54; peak memory 9.0 vs 11.5 GiB. A QLoRA adapter merged into BF16 weights is not exactly the trained model.
- GGUF export pipeline reproduces the official GGUF bit-for-bit (290 tensors) for the base model.
- Starting point on typed-decisions (untrained): Spark 4B Q8_0 accuracy 0.574, KL 2.899, Brier 0.480, p50 201 ms; Jev 1.13.0 (card) 0.727 / 1.442 / 0.148 / 710 ms; prior 0.470 / 0.347 / 0.189. Main weakness `agent_trace_observability` 0.366 (p ≈ 0.9999 on "Critical").

## Relevance to GroundOne
- Closest template for GroundOne's training code: **soft CE restricted to answer-letter logits, last-position readout, LoRA only, prompt identical between training and inference**. GroundOne uses the same idea for two letters (A = supported / B = not supported) on [[Qwen2.5]] 0.5B/3B with MLX.
- Design details worth copying: soft targets where label distributions exist; label smoothing (0.03) for hard human labels; contamination filtering by substring; drop rather than truncate long prompts; parity check between training and serving runtimes; keep `lm_head` frozen when embeddings are tied (true for Qwen2.5 0.5B).
- QLoRA result (NF4 base weaker by 14 points before training) is a caution for quantised-base fine-tuning on the Mac ([[LoRA]]).

## Links
- [[Rizzo-Flow]], [[Rizzo-Flow README]], [[LoRA]], [[Calibration]], [[SemIf]]
