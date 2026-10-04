---
type: concept
tags: [open-source, model, jev, system-one, logit-readout]
---
# SemIf

**SemIf** ("semantic ifs"; formerly **OpenJev**) is an independent open-source project (MIT, by TheoLeeCJ and contributors) exploring the [[System One Models]] paradigm. It reproduces the **interface pattern** of [[Jev]] (runtime-defined criteria and typed options in, probabilities out, no generation) with frozen open models. It does not reproduce Jev's undisclosed model or its RLCD training.

Repository: https://github.com/TheoLeeCJ/SemIf (local: `SystemOne_repos/SemIf`). Sources: [[SemIf README]], [[SemIf RESULTS]].

## Design
- **Direct option-logit readout**: one forward pass over state + criterion + options; the declared option logits are read and normalised. No answer token sampled, no JSON parsing.
- Default model: frozen **Qwen3.5-4B** (pinned revision), BF16. Model ladder also includes Qwen3-0.6B and MiniCPM5-2B (browser/WebGPU demo, GGUF quantised), and a Qwen3.8-27B EXL3 bridge.
- Execution modes: fresh `direct`, serial **prefix reuse**, and `shared` (state prefilled once, criteria as **parallel suffixes**) — see [[KV Cache]], [[Prefill and Decode]].
- Backends: PyTorch CUDA, **MLX** and PyTorch **MPS** for Apple Silicon, llama.cpp (CPU).
- Optional per-workload **temperature scaling**.
- Auditable: frozen fixtures (authored 144, perturbations 108, shape777), prompt hashes, row-level outputs committed.

## Results (one RTX 3090, frozen BF16)
- Quality, direct Qwen3.5-4B: authored 0.813 balanced acc.; **WANLI 0.637**; TypeSafe subset 0.845 vs published Jev 0.883 (102 rows, Jev not run); Every judgment grid 0.806. Native Qwen3-Reranker-4B clearly worse for decisions (−0.188 authored, −0.115 WANLI).
- Size ladder (authored / TypeSafe): 0.6B 0.440 / 0.407; 2B 0.686 / 0.637; 4B 0.813 / 0.845. 27B EXL3: 0.958 authored.
- Readout vs generation: 21 criteria in **1.023 s** (0 output tokens) vs 5.332 s for a compact yes/no JSON array (111 tokens); 18/21 agreement.
- Shared state: 2.33 → 10.75 (serial prefix) → **20.03 decisions/s** (parallel suffixes) on 777 decisions; 5–6/777 argmax drift.
- Calibration (out-of-fold ECE): authored 0.068 → 0.038; **WANLI 0.208 → 0.069**; Every 0.050 → 0.047.

## Limitations (stated)
- Option-order sensitivity: 10 argmax flips under option reversal on 36 cases.
- One confident (> 0.8) wrong non-`insufficient` answer on the 36-row missing-evidence set → not operationally calibrated.
- RLCD, Jev's architecture, Jev latency/cost and the full 711-row TypeSafe benchmark not reproduced.
- Up to 16 options per question.
- Stated next step: targeted training for decision semantics and calibration against the frozen baselines.

## Relevance to GroundOne
- Belongs to the same family as GroundOne (LM-head logit readout); GroundOne is a fine-tuned, single-task instance of the "next phase" SemIf proposes.
- WANLI (NLI) is SemIf's weakest and worst-calibrated workload, motivating fine-tuning for [[Groundedness Verification]] and temperature scaling for [[Calibration]].
- Runnable zero-shot on the M4 Mac via MLX. Superseded as the strongest open baseline on SemIf's own fixtures by the fine-tuned [[Rizzo-Flow]] on perturbations (0.946 vs 0.766), but SemIf remains better on missing evidence (0.861 vs 0.583).

## Related
- [[GroundOne]], [[Jevlike]], [[Rizzo-Flow]], [[CLM]], [[When System One Beats an LLM]]
