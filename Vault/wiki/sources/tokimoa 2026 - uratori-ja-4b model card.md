---
type: source
author: "tokimoa (individual developer)"
date: 2026
venue: "Hugging Face model card tokimoa/uratori-ja-4b (v1.1), revision 54700f5 (retrieved 2026-10-10)"
url: "https://huggingface.co/tokimoa/uratori-ja-4b"
tags: [source, model-card, system-one, decision-models, groundedness, rag, japanese, option-marker-head, calibration, mlx, selective-prediction, uratori]
---
# tokimoa 2026 – uratori-ja-4b model card

**Raw file**: `raw/tokimoa 2026 - uratori-ja-4b model card_ingested.md`

## Overview
A Japanese decision model trained for three jobs: **checking whether a claim or answer is supported by supplied evidence (grounding)**, comparing two documents (contradictions, meaning-changing edits, added claims), and judging retrieval results and answers in a RAG pipeline (relevance, sufficiency, faithfulness). It follows TypeSafe's `/v1/systemone` format. Sizes: 310M (CPU), 2B, 4B (this card) and 9B; MLX 8-bit and 4-bit versions exist. Apache-2.0. Single individual developer; evaluation set built by the same author with LLM drafts and a three-judge vote.

## Key Insights
1. **Architecture.** The text decoder of Qwen3.5-4B (vision tower removed) with a LoRA adapter (rank 32, all linear layers) merged into the weights, plus a **2-layer scoring head read at an added `<opt>` token after each option**. 4,096-token maximum input (longer inputs raise an error). Questions in one call share the state and are judged independently. Temperature scaling per question type and option count, fitted on a 600-item calibration split.
2. **The card's own example is GroundOne's label set.** A claim checked against evidence with options 支持 (supported), 矛盾 (contradicted) and 情報不足 (insufficient information), plus a separate yes/no contradiction question.
3. **Training.** Stage 1: JNLI converted to decision format (19,816 items). Stage 2: 49,668 synthetic items generated with DeepSeek V4.1 Flash over fictional business documents, Japanese government FAQs and Wikipedia, from 29 templates (grounding, comparison, RAG, writing, routing), about 17,000 of them minimal pairs. Stage 3 (v1.1): long documents (3,000–6,000 tokens) and passage selection. Loss: cross-entropy over each question's options, normalised per question type within a batch.
4. **Results on its own evaluation set (uratori-ja-eval).**
   | Model | Parameters | test (802) | challenge (300) |
   |---|---|---|---|
   | Jev 1.13.0 (API, 2026-10-05) | undisclosed | 0.903 | 0.900 |
   | uratori-ja-9b | 8.0B | 0.897 | 0.913 |
   | uratori-ja-4b | 4.2B | 0.872 | 0.870 |
   | uratori-ja-2b | 1.9B | 0.781 | 0.797 |
   | uratori-ja-310m | 0.31B | 0.686 | 0.693 |
   | majority label / random | – | 0.446 / 0.387 | 0.430 / 0.379 |
   The 4b scores ECE 0.032 and Brier 0.195 on test; grounding accuracy 0.873, RAG 0.848; minimal pairs (both right) 0.730. Selective accuracy: 0.983 on the 30 % most confident test items, 0.952 at 70 %.
5. **Long documents** (128 items, 3,000–6,000 tokens): 0.930 vs Jev 0.962; passage selection with a "none" option: 0.944 vs Jev 0.726. The MLX 8-bit version has "same accuracy as this model on the evaluation set"; 4-bit about 1 point lower.

## Relevance to GroundOne
- **A groundedness-specialised decision model with GroundOne's three-way labels**, released as a size ladder. The ladder (0.31B 0.686 → 2B 0.781 → 4B 0.872 → 9B 0.897, Jev 0.903) mirrors GroundOne's 0.5B → 3B gain on T1 (0.769 → 0.832): **model size is the main lever**, consistent with the thesis claim ([[GroundOne Results]]).
- **Design difference.** One question per row with an `<opt>`-token head; GroundOne reads K sentence verdicts in one pass with the LM head restricted to letters.
- **Evidence quality.** Self-built, LLM-generated evaluation set by the same author; single developer; Japanese only. Useful as a design and scaling data point, not as a benchmark.
- Selective-accuracy reporting (accuracy at coverage) is the format GroundOne uses for AURC ([[Selective Prediction]]).

## Links
- Concepts: [[Groundedness Verification]], [[Hallucination Detection]], [[System One Models]], [[Selective Prediction]], [[Decision-Model Landscape (Hugging Face, 2026)]]
- Related sources: [[KR Labs and vLLM Semantic Router 2026 - Vela 2.0 9B model card]]
