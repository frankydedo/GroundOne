---
type: source
author: "TheoLeeCJ and contributors"
date: 2026-09-22
url: https://github.com/TheoLeeCJ/SemIf
tags:
  - system-one
  - semif
  - logit-readout
  - repository
---
# SemIf README

Raw file: `raw/SemIf README_ingested.md`. Local clone: `SystemOne_repos/SemIf`.

## Overview
README of [[SemIf]] ("Semantic ifs from open models, on a 3090 at home"; formerly **OpenJev**; MIT; independent of TypeSafe). It reproduces the **interface pattern** of [[Jev]] with frozen open models: runtime-defined criteria and typed options in, **option probabilities read directly from the model's native option logits** in one forward pass out. No answer token is sampled, no JSON parsing. It explicitly does *not* reproduce Jev's model or training. Latest changes listed (2026-09-22): PyTorch/MPS scoring for Apple Silicon, a Qwen3.8-27B EXL3 bridge, per-workload temperature calibration.

## Key Insights

### Design
- Default model: frozen **Qwen3.5-4B** (pinned revision), BF16, CUDA. Backends: PyTorch CUDA, **MLX** (`--backend mlx`, direct/serial-prefix/parallel-shared modes on Apple Silicon), PyTorch MPS, llama.cpp GGUF on CPU.
- Modes: `direct` (fresh), serial **prefix reuse**, `shared` (prefill the state once, evaluate criteria as **parallel suffixes**).
- Every result row carries the model revision and a `prompt_sha256`; fixtures, runners and row-level outputs are committed.
- Up to 16 options per question (per [[Rizzo-Flow README]]).

### Measured (one RTX 3090, same frozen 4B model)
- **Readout vs generation**, one owned state, 21 binary criteria: direct typed logits median **1.023 s, 0 output tokens** vs compact autoregressive JSON array of yes/no **5.332 s, 111 tokens** (TTFT 0.489 s), 5.21×. The arrays agreed with direct argmax on **18/21** — a systems comparison, not semantic equivalence.
- **Shared state**, 37 states × 21 criteria = 777 decisions: fresh 2.33 dec/s (333.1 s); serial prefix reuse 10.75 (72.3 s); parallel suffixes **20.03** (38.8 s); native reranker 1.86. BF16 reuse changed 5–6 of 777 argmaxes.
- **Quality** (native BF16 direct logits): see the tables in [[SemIf RESULTS]] — authored 144 rows 0.813 balanced acc.; WANLI 256 rows 0.637; TypeSafe subset 102 rows 0.845 vs Jev 0.883 (Jev value from published records, not run).
- **Model ladder**: Qwen3-0.6B 0.440 authored / 0.407 TypeSafe; MiniCPM5-2B 0.686 / 0.637; Qwen3.5-4B 0.813 / 0.845.
- **27B EXL3 bridge**: 0.958 on authored-144 (system-level comparison; family, size, quantization and runtime all differ); 84.43% agreement with the 4B on the 777-decision fixture.
- **Calibration** (per-workload temperature scaling, out-of-fold): authored ECE 0.068 → 0.038 (T 1.23); **WANLI 0.208 → 0.069 (T 2.50)**; Every 0.050 → 0.047 (T 1.71). Calibration does not change the selected option; only the WANLI improvement is clear (intervals overlap elsewhere).

## Relevance to GroundOne
- Closest open precedent for GroundOne's readout: **logit readout of answer options on a decoder LM, no generation**. SemIf is zero-shot (frozen); GroundOne adds LoRA fine-tuning.
- **WANLI** (NLI) is the closest workload to sentence-level entailment, and it is where a frozen 4B is weakest (0.637) and worst calibrated (raw ECE 0.208). This directly motivates fine-tuning for [[Groundedness Verification]] and temperature scaling for [[Calibration]].
- The 18/21 agreement between readout and generated JSON warns that a readout-vs-generation latency comparison must also report agreement; GroundOne's single-token generation control addresses this.
- Shared-prefix numbers support the GroundOne hypothesis that readout's advantage grows with the number of claims per shared context ([[KV Cache]], [[Prefill and Decode]]).
- MLX backend exists, so SemIf is runnable on the M4 Mac as a zero-shot reference.

## Links
- [[SemIf]], [[SemIf RESULTS]], [[Rizzo-Flow]], [[System One Models]], [[Jev]], [[When System One Beats an LLM]]
