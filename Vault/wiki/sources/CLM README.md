---
type: source
author: "Contrastive-LM (Jacky Kwok et al.)"
date: 2026-09
url: https://github.com/Contrastive-LM/CLM
tags:
  - system-one
  - clm
  - bi-encoder
  - repository
  - related-work
---
# CLM README

Raw file: `raw/CLM README_ingested.md`. Local clone: `SystemOne_repos/CLM` (results verified in `examples/t_rex/results/*.json`).

## Overview
README of the CLM inference repository (Apache 2.0). It serves **CLM-8B** behind a **TypeSafe-compatible API** (`POST /v1/systemone` with `Noul` / `Choice` / `Score` questions, plus `POST /v1/rank`). Architecture and training text largely repeat the [[Kwok 2026 - Contrastive Language Models|blog]]. Serving stack: `vllm serve Qwen/Qwen3-8B --runner pooling` on a GPU (port 8090) + `clm-serve` (FastAPI, heads on CPU or GPU, port 8700). Reference head `CLM_v0.1-8B.pt` (75 MB). States > 2,048 tokens are truncated by default.

## Key Insights
- **How typed questions map to CLM**: a question is a state plus a closed set of candidate texts (option descriptions); the softmax over cosine scores is the distribution. `Score` = expected level index; `confidence` = top probability minus mean of the others. Temperature is a request parameter (divides logits), not a fitted calibration.
- **`clm-raw` ablation model**: cosine in the raw encoder space, without trained heads.
- **Vector cache** (reserved slab on device, LRU): measured on one RTX 4090, server-side p50, fixed action set: new state every call 28.6 → 28.0 ms (3 actions) and 28.8 → 28.1 ms (50 actions); revisited states 1.7–2.0 ms → 0.6–0.7 ms. I.e. a fresh state always pays the ~28 ms encoder call.
- **Fine-tuning**: `train/finetune.py` trains only the projection heads on a frozen encoder; a DeepSWE held-out reproduction is claimed as 31/38 = 81.6% (best-of-4 with released heads and embeddings).
- **Branch scope**: the scaling experiments, data pipelines and paper figures are *not* in this repo ("live in the research repo's `main` branch"), so the scaling-law and zero-shot figures cannot be reproduced from it.

### Verified: T-Rex result files (`examples/t_rex/results/`)
The only zero-shot comparison shipped with raw outputs. Setup (from `examples/t_rex/README.md`): deterministic clone of the Chrome dino game, 5 seeds × 60 s, real time, 6 requests in flight; a physics planner **labels each action safe/unsafe and names the best one in the prompt** ("jump: Safe ... Best."); the shield replaces unsafe answers. CLM on one RTX 4090 (2026-09-23); Jev `jev-1.13.0` via the hosted API (2026-09-22).

| Metric (mean over 5 seeds) | CLM | Jev |
| --- | ---: | ---: |
| Survived / deaths | 5/5, 0 | 5/5, 0 |
| **Agreement with planner's best move** | **0.658** (per seed 0.635–0.680) | **0.987** (0.985–0.989) |
| Shield interventions + saves (summary total) | 4,883 | 28 |
| Client latency p50 | 16.5 ms | 149.8 ms |
| Model time p50 | 2.6 ms | 131.9 ms |
| Decisions per run | 3,341.8 | 1,119.0 |

Reading: survival is a property of the **shielded system**, not of the model (the README itself says agreement and intervention rows "measure the model"). On a task where the correct answer is literally written in the option description, CLM picks it about two times in three, Jev almost always. The README's headline "performs on par with Jev" is therefore not supported by its own shipped result file on the decision-quality metric; only the latency advantage (~9× client-side, local GPU vs remote API) is supported.

## Relevance to GroundOne
- Not runnable on the thesis hardware (needs vLLM + CUDA and an 8B encoder) → cited as related work, not a baseline.
- Strong evidence-quality example for the thesis: a speed claim that holds and a quality claim that, on the one reproducible benchmark, does not. Supports the thesis position that a System One verifier must be judged on **decision quality and calibration**, not latency alone (see [[Calibration]]).
- The T-Rex failure mode (missing an answer that is spelled out in the candidate text) is consistent with the inference that a bi-encoder with independent state/candidate embeddings is weak at fine-grained conditional reading, which is what [[Groundedness Verification]] needs.

## Links
- [[CLM]], [[Kwok 2026 - Contrastive Language Models]], [[System One Models]], [[Jev]], [[Jev Input and Output Format]]
