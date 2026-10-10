---
type: source
author: "Jared Palmer"
date: 2026
venue: "Hugging Face model card jaredpalmer/kev-4b (Kev 1.0), revision 6cfce5c (retrieved 2026-10-10)"
url: "https://huggingface.co/jaredpalmer/kev-4b"
tags: [source, model-card, system-one, decision-models, pointer-head, lora, shared-prefix, kv-cache, long-context, mlx, apple-silicon, calibration, kev]
---
# Palmer 2026 – Kev-4B model card

**Raw file**: `raw/Palmer 2026 - Kev-4B model card_ingested.md`

## Overview
Kev is an open (Apache-2.0) family of Jev-style decision models by Jared Palmer (sizes 0.5B–27B in the listing; this card covers Kev-4B, Kev 1.0, published 2026-09-24). It implements TypeSafe's `POST /v1/systemone` API so the TypeSafe SDK works unchanged, and it is one of the five model types natively served by llama.cpp ([[ggml-org 2026 - llama.cpp PR 29818 systemone API]]). Several other entrants build on Kev's code (Drex v1.5 serves through "the bundled Kev code"; dispositio fine-tunes Kev 0.8B). The card is unusually rigorous: dev/test separation, locked test reads, paired record-level bootstrap intervals and a pre-registered long-context rule.

## Key Insights
1. **Architecture.** "A causal language-model backbone run prefill-only, with a pointer head over the options." Backbone `Qwen/Qwen3.5-4B-Base` (32 layers: 24 Gated DeltaNet linear-attention, 8 full attention), **frozen**; LoRA rank 16, α 32 on attention, MLP and DeltaNet projections (33.8M parameters). The pointer head uses two projections to score **each option's closing token against the question's final token**; a softmax gives the probabilities. 1–255 options per question.
2. **Shared state, cached.** "Each question is answered as its own row that continues from the shared state, so questions cannot influence one another; the state is computed once and cached." This is exactly GroundOne's design (a): shared prefix plus one suffix per question ([[KV Cache]]).
3. **Training.** Five stages (base recipe of 12,576 records from ten public datasets plus generated policy minimal pairs and rule structures; dates and missing-evidence cases; 5,219 CFPB complaint narratives up to about 7k tokens; 6,000 programmatic "skills" records; 5,320 developer-tooling records), each replaying earlier data. Loss: **cross-entropy over each question's options**; option order shuffled, "none of the above" options and distractors inserted. "No output of Jev … was used." Calibration: **one temperature, T = 2.41**, fitted by NLL on held-out items of a training corpus; a pre-registered refit on held-out datasets (T = 2.30) was not adopted because it failed the rule (Brier interval below zero and lower ECE).
4. **Held-out results (selected).**
   | Panel | Kev-4B | Jev |
   |---|---|---|
   | breadth-v1 test, 14 never-trained datasets (3,089) | 0.690 | 0.757 |
   | breadth-v1 test, chance-corrected index [95 % CI] | 38.0 [35.5, 41.3] | 54.0 [51.2, 57.0] |
   | transfer-v4 locked test (656): accuracy / Brier | 0.838 / 0.224 | – |
   | transfer-v4 locked test: ECE / confident errors (p ≥ 0.9, wrong) | 0.017 / 1.5 % | – |
   | MMLU-Pro, 10 options | 0.565 | 0.840 |
   | Unanswerable items answered with p ≥ 0.9 | 0.00 | 0.09 |
   On trained families it is level with or above Jev (hard-v1 dev 0.786 vs 0.777; documents-v1 dev 0.891 vs 0.868). The card states that its largest gains are in distribution.
5. **Calibration is distribution-dependent.** ECE at T = 2.41: 0.029 on breadth-v1 test, 0.017 on transfer-v4 locked test, but 0.084–0.101 on trained skill and document families; "a single temperature cannot reorder confidences".
6. **Long documents.** Validated context 8,192 tokens by a rule fixed before the read. CUAD accuracy 0.837 at 8k, 0.823 at 16k (Δ −1.1 [−3.4, +1.2], just outside the −3 pp tolerance), 0.788 at 32k, 0.781 at 64k.
7. **Apple Silicon (MLX, bf16, M5 with 32 GB; three questions, state prefilled in 1,024-token chunks).**
   | State tokens | New state | Cached state | MLX peak (8.4 GB weights) |
   |---|---|---|---|
   | 8,192 | 6.6 s | 354 ms | 10.2 GB |
   | 16,384 | 14.0 s | 427 ms | 11.0 GB |
   | 65,000 | 84.5 s | 716 ms | 13.0 GB |
   The MLX path is within 0.018 of the fp32 evaluation path on 60 short-state questions, with no changed answers. On CUDA (H100), 5 questions on a 2,200-token state take 89.4 ms new / 22.5 ms repeated.

## Relevance to GroundOne
- **Independent confirmation that prefill dominates on device.** On an M5, a cached 8k state answers three questions in 354 ms while a new state costs 6.6 s. GroundOne reads all K verdicts in one pass over document plus answer, so it pays the prefill once per answer ([[Prefill and Decode]], [[On-Device Inference]]).
- **Reporting model.** Locked tests, pre-registered rules, paired record-level bootstrap and confident-error rates: the same discipline GroundOne follows with cluster bootstrap ([[Statistical Significance and Bootstrap]]).
- **CE + temperature works.** Kev uses plain cross-entropy over options and one temperature, no RL, like GroundOne; compare [[Deka 2026 - From Retrieval to Typed Decisions SBERT2S1 (arXiv 2610.02486)|Deka 2026]].
- **Pointer head vs letter readout.** Kev scores option tokens against the question token with a trained head (options defined at run time); GroundOne restricts the LM head to fixed letters (fixed, trained mapping).
- On the Decision Index RAGTruth task the Kev models are weak (Kev 4B 0.330, Kev 9B 0.462 F1, below the 0.518 always-hallucinated baseline; [[multimodalart 2026 - Jev Decision Index (Hugging Face Space)]]): a general decision model is not a grounding checker.

## Links
- Concepts: [[System One Models]], [[KV Cache]], [[On-Device Inference]], [[Apple Silicon and MLX]], [[Calibration]], [[Decision-Model Landscape (Hugging Face, 2026)]]
- Related sources: [[ggml-org 2026 - llama.cpp PR 29818 systemone API]], [[multimodalart 2026 - Jev Decision Index (Hugging Face Space)]]
