---
type: source
author: "TheoLeeCJ and contributors"
date: 2026-09
url: https://github.com/TheoLeeCJ/SemIf/blob/main/docs/RESULTS.md
tags:
  - system-one
  - semif
  - evaluation
  - calibration
---
# SemIf RESULTS

Raw file: `raw/SemIf RESULTS_ingested.md` (= `docs/RESULTS.md`, "Phase 1 results").

## Overview
The detailed Phase 1 report of [[SemIf]]. Headline finding: open components reproduce the **interface pattern** of a semantic decision operator (runtime criteria, typed options, no decoding loop, shared-state computation) but **not** the full economic or calibration claims around [[Jev]]. Qwen3.5-4B direct option logits are the strongest baseline tested; the native Qwen3-Reranker-4B is a useful retrieval control, not a decision foundation. All timings on one RTX 3090.

## Key Insights

### Semantic quality (frozen, native BF16)
| Workload | Metric | Direct Qwen3.5-4B | Qwen3-Reranker-4B | Jev (published, not run) |
| --- | --- | ---: | ---: | ---: |
| Authored, 144 rows | mean family balanced acc. | **0.813** | 0.625 | — |
| WANLI, 256 rows | balanced acc. | **0.637** | 0.522 | — |
| TypeSafe subset, 102 rows / 20 cases | equal-case agreement | **0.845** | 0.560 | 0.883 |
| Every judgment grid, 36 rows | accuracy | **0.806** | 0.694 | — |
| Every action firewall, 10 actions | composed accuracy | 0.700 | 0.700 | — |

- Reranker gap is significant: −0.188 [−0.256, −0.120] authored, −0.115 [−0.184, −0.044] WANLI (source-group bootstrap).
- 3.8 pp gap to Jev on the TypeSafe subset is explicitly **not** a near-Jev claim: small selected sample, Jev not run, one metric. Total-variation distance to target distributions: direct 0.177, Jev 0.127, reranker 0.444.

### Robustness and confidence (36 owned base cases; direct 0.723, reranker 0.530)
| Variant | Direct acc. | Direct flips | Reranker acc. | Reranker flips |
| --- | ---: | ---: | ---: | ---: |
| Option reversal | 0.813 | 10 | 0.498 | 2 |
| Criterion wrapper | 0.706 | 9 | 0.647 | 9 |
| Irrelevant context | 0.821 | 4 | 0.563 | 13 |

- **Position bias is real** (10 flips under option reversal).
- On the 36-row **missing-evidence** set each system made one non-`insufficient` choice above 0.8 → scores "cannot be treated as Jev-like operational calibration".

### Systems benchmark (RTX 3090)
- 21 criteria, one state: direct readout **1.023 s**, no output tokens; compact yes/no JSON array **5.332 s**, 111 tokens, TTFT 0.489 s; agreement 18/21. A stricter minified-array prompt failed (repeated values, hit 128-token cap) and is reported as a failure. The older verbose comparison (1.066 vs 18.229 s) is no longer the headline.
- 777-decision fixture: fresh 2.33 dec/s, serial prefix 10.75, **parallel suffixes 20.03** (state p50 1.05 s), argmax drift 5–6/777; reranker 1.76–1.86 dec/s with 51–54/777 drift at batch 4/8 → batch shape is part of the evaluated system.
- Timings must not be divided into TypeSafe's service latency (different model, inputs, kernels, hardware).

### Reproduced vs not
- Reproduced: state + criteria → typed scores; no generation/parser; runtime-defined questions; shared-state reuse; a strong 4B open baseline.
- **Not** reproduced: Jev's architecture or parallel sampler; **RLCD** training ([[Reinforcement Learning with Calibrated Decisions]]); calibrated probabilities for operational thresholds; frontier-level semantics; TypeSafe latency/cost; the full 711-row benchmark.
- Stated next step: **targeted training for decision semantics and calibration**, against frozen baselines, after expanding external gold tasks and defining a held-out calibration target. "A generic reranker fine-tune would answer the wrong question."

## Relevance to GroundOne
- GroundOne is essentially the "next justified phase" SemIf names: targeted (LoRA) training of a letter-readout model for one decision type (sentence support), with a held-out calibration target.
- Evidence that zero-shot 4B readout is weak on NLI-like decisions (WANLI 0.637) and miscalibrated on missing evidence — both central to [[Hallucination Detection]] in RAG.
- Method lessons to adopt: report argmax drift between fresh and shared-prefix scoring; test option-order reversal; keep a missing-evidence/unsupported slice; give bootstrap intervals; separate retrieval ranking from decision accuracy.

## Links
- [[SemIf]], [[SemIf README]], [[Rizzo-Flow]], [[Calibration]], [[KV Cache]], [[When System One Beats an LLM]]
