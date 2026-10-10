---
type: source
author: "ngxson (ggml-org / llama.cpp maintainers)"
date: 2026
venue: "GitHub pull request ggml-org/llama.cpp #29818, merged 2026-10-02 (merge commit a4cb4c6); retrieved 2026-10-10 via the GitHub API"
url: "https://github.com/ggml-org/llama.cpp/pull/29818"
tags: [source, software, llama-cpp, on-device, decision-models, system-one, gguf, shared-prefix]
---
# ggml-org 2026 – llama.cpp PR 29818 systemone API

**Raw file**: `raw/ggml-org 2026 - llama.cpp PR 29818 systemone API_ingested.md` (PR title, metadata and body)

## Overview
The pull request "llama, server: add /v1/systemone API (models: laya, julia-1, lev, openjev, kev)" adds native support for decision models to [[llama.cpp README (ggml-org)|llama.cpp]]'s `llama-server`. It was **merged on 2026-10-02**. Pre-converted GGUFs are published under `ggml-org` (OpenJev, lev, Laya, Julia-1, Kev-4B), and later ggml-org GGUFs in the tag (Clef, Clef-Flash, Bespoke-Nimble-9B-v3) point to the same API.

## Key Insights
1. **What a decision model is, for llama.cpp.** "'Decision models' are just fancy wrappers around traditional embedding models (BERT/Qwen/etc), so changes to support them are kept to be as small and as self-contained as possible." The server switches input/output handling on a `{arch}.decision.type` GGUF metadata key; libllama gains a decision head on the graph.
2. **Shared prefix supported.** Checked items include "support parallel shared prompt prefix (only for causal models)" and vision input. Clef support was "planned as a follow-up".
3. **Parity.** On one test request with five questions, reference vs llama.cpp probabilities agree to a worst absolute difference of 1.8e-4 (OpenJev), 8.4e-4 (Laya), 1.3e-3 (Kev-4B), 5.2e-3 (lev) and 2.2e-2 (Julia-1). Input-token counts match except for lev (576 vs 1,194).
4. The PR declares that most of the code is AI-written, with the design owned by the author.

## Relevance to GroundOne
- **Decision models are now first-class in the most widely used local runtime.** The locality pillar no longer depends on bespoke Python servers: a GGUF decision model can be served on a Mac (Metal) or CPU behind the same `/v1/systemone` contract that GroundOne's compatibility route and [[Rizzo-Flow]] expose ([[On-Device Inference]]).
- **Framing.** llama.cpp's maintainers treat decision models as embedding models plus a head, i.e. a prefill-only workload. This matches the thesis account that a System One saves the decode phase entirely ([[Prefill and Decode]]).
- GroundOne's marker readout (K verdicts at K positions in one sequence) is not one of the supported patterns; supporting it would need logits at several positions of one sequence, which llama.cpp exposes for embeddings but the PR does not wire to `/v1/systemone`.

## Links
- Concepts: [[On-Device Inference]], [[Apple Silicon and MLX]], [[Decision-Model Landscape (Hugging Face, 2026)]], [[Jev Input and Output Format]]
- Related sources: [[llama.cpp README (ggml-org)]], [[Palmer 2026 - Kev-4B model card]], [[Convai Innovations 2026 - Laya model card]]
