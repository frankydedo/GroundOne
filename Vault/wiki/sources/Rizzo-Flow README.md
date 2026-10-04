---
type: source
author: "Simone Rizzo (Rizzo AI Academy) and contributors"
date: 2026-09-25
url: https://github.com/Rizzo-AI-Academy/rizzo-flow
tags:
  - system-one
  - rizzo-flow
  - logit-readout
  - lora
  - baseline
---
# Rizzo-Flow README

Raw file: `raw/Rizzo-Flow README_ingested.md`. Local clone: `SystemOne_repos/rizzo-flow`.

## Overview
README of [[Rizzo-Flow]] ("The open, local take on Jev"; Apache-2.0; by Simone Rizzo, cf. [[jev_simone_rizzo]]). A local, open-weights System One server with a **Jev-compatible HTTP API** (`POST /v1/systemone`) and a native API (`POST /v1/decisions`). Default model: **Spark-X2.5-4B** (also 1.7B) by XHToken, with Rizzo-Flow's own **LoRA fine-tune** for typed decisions merged in (default since 2026-09-25). Runtime: **llama.cpp** b11081 (Metal/CUDA/Vulkan/ROCm/SYCL/CPU), with **MLX** still available as `--backend mlx` (the original runtime until 2026-09-21). Explicitly inspired by [[SemIf]]; does not reproduce Jev's architecture or RLCD.

## Key Insights

### Mechanism
1. Every question becomes **multiple choice**; each option is one uppercase letter, verified at request time to be a single token in context → at most **26 answer slots**.
2. The state is at the start of the prompt and **prefilled once**; question branches **share the state's KV cache cells** (no copy) and run in one unpadded micro-batch ([[KV Cache]], [[Prefill and Decode]]).
3. Only the **logits of the allowed letters** at one position per question are read. Nothing sampled.
4. Python turns logits into typed output: softmax, optional temperature, expected values, abstention policy, schema-validated JSON.
"Zero generated tokens is not zero latency": ~50 ms for one short decision, ~1 s for 21 questions on a 2,000-token state (RTX 5060 Ti, 8 bit).

### Primitives
- Native: `boolean`, `choice` (≤ 26), `score` (ordered levels → probability-weighted score), `numeric` (anchors → expected value, median, out-of-range probabilities). Built-in **abstention** (`__insufficient__`, `__below_range__`, `__above_range__`) with `status` `ok / insufficient_evidence / out_of_range / uncertain`.
- Jev-compatible: `noul`, `choice`, `score` (≤ 10 levels), no abstention; `confidence = (n·p_max − 1)/(n − 1)`, which describes distribution shape, **not** probability of being right.

### Fine-tune (summary; details in [[Rizzo-Flow training]])
- Loss: **soft cross-entropy** between a target distribution and the softmax over the answer-letter logits at the last prompt position, same prompts (`spark-decisions-v3`) as inference. LoRA r 16, α 32, all attention+MLP linears; 32.4M trainable params (4B), 16.7M (1.7B).
- 28,321 public questions (tasksource procedural-typed-decisions, Open-Jev, 12 jev-bench configs), **no Jev outputs**, contamination-filtered. 1 epoch, AdamW 5e-5, 16 questions/step, 1,770 steps: **41 min (4B) / 19 min (1.7B) on one RTX PRO 6000**.
- In-distribution dev accuracy (600 questions): 0.55 → ~0.85 (4B), 0.41 → ~0.82 (1.7B), read from a chart.

### Measured: typed-decisions test (400 cases, 2,000 decisions, 5 questions per shared state; llama.cpp CUDA, RTX 5060 Ti, Q8_0)
| Model | Acc ↑ | KL ↓ | Brier ↓ | ECE ↓ | p50/case |
| --- | ---: | ---: | ---: | ---: | ---: |
| Spark-X2.5-4B base | 0.574 | 2.899 | 0.480 | 0.349 | 201 ms |
| **Rizzo Flow 4B (FT)** | **0.648** | **0.452** | **0.205** | **0.112** | 195 ms |
| Rizzo Flow 4B Q4_K_M | 0.650 | 0.436 | 0.201 | 0.093 | 198 ms |
| Spark-X2.5-1.7B base | 0.530 | 3.031 | 0.496 | 0.348 | 117 ms |
| Rizzo Flow 1.7B (FT) | 0.544 | 0.694 | 0.275 | 0.169 | 109 ms |
| Jev 1.13.0 (dataset card, not re-measured) | 0.727 | 1.442 | 0.148 | – | – |

- 4B: +0.074 accuracy [+0.050, +0.101] (paired bootstrap); KL ÷6; 3 of 20 questions get worse.
- **1.7B: probabilities improve, accuracy does not** (+0.014 [−0.014, +0.043]).
- Gold labels come from a ~4B teacher model, not humans. Jev's KL/Brier use unstated formulas.

### Measured: SemIf fixtures (4B, llama.cpp CUDA, RTX 5060 Ti)
- Fine-tuned Q8_0: `authored144` **0.845** (SemIf Q8 0.819, tied: +0.027 [−0.038, +0.099]); `perturbations108` **0.946** (SemIf 0.766, +0.180 [+0.108, +0.267]); option-reversal/wrapper/irrelevant flips 1/1/1 (base 5/4/5, SemIf 9/7/4).
- **Missing evidence got worse**: 0.583 (base 0.750, SemIf 0.861), 5 confident (p ≥ 0.8) wrong answers out of 36 (SemIf 1).
- Base weights: 49/52 ms p50/p95 per short decision; **20.99 dec/s** shared on `shape777` vs 2.60 fresh; 13/777 argmax changes shared vs fresh at Q8_0 (all margins < 0.24); 5.6 GiB GPU memory.
- 1.7B base: 0.678 / 0.640, 18/36 flips under option reversal, 25–27 ms, 31.59 dec/s shared; −0.134 vs 4B.
- MLX history: M4 Pro Q8, prompt v2: 254/259 ms per short decision, 3.92 dec/s shared, authored 0.758 — the only Apple number, "two steps old".
- Prompt v3 (short system prompt + plain-text multiple choice) chosen on a dev half: authored 0.754 → 0.827, option-reversal flips 6 → 2; longer instructions did not help.

### Stated limitations
- Probabilities **uncalibrated by default**, fine-tune or not; temperature scaling (`rizzo calibrate`) is per primitive and bound to a fingerprint of weights, precision, runtime, backend and prompt.
- Under-uses abstention; confident answers on missing evidence; residual position bias (no permutation debiasing).
- 26 options max; one resident model, serialized requests; tested by maintainers only on Windows + NVIDIA; KV cache ~144 KiB/token on 4B under llama.cpp.
- Internal inconsistency: "Known limitations" says the fine-tune was measured on typed-decisions only, while the results section reports fine-tuned SemIf-fixture numbers (the limitation line looks stale).

## Relevance to GroundOne
- **External baseline**: same family as GroundOne (LM-head logit readout of answer letters), runnable on Apple Silicon via MLX or llama.cpp Metal; its fine-tuning objective (soft CE over letter logits, LoRA) is the closest published analogue to GroundOne's training.
- Key lesson: fine-tuning with soft targets mainly fixes **probability shape** (ECE 0.349 → 0.112) and robustness to perturbation, while accuracy gains are moderate and **vanish at 1.7B** — relevant to GroundOne's 0.5B/3B scale choice and to the [[Calibration]] hypothesis.
- Warning for [[Hallucination Detection]]: general typed-decision fine-tuning made the "insufficient evidence" case worse; GroundOne must measure the unsupported/missing-evidence slice explicitly.

## Links
- [[Rizzo-Flow]], [[Rizzo-Flow training]], [[SemIf]], [[Jev]], [[LoRA]], [[System One Models]]
