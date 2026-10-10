---
type: source
author: "KR Labs (makers of LettuceDetect) and the vLLM Semantic Router team"
date: 2026
venue: "Hugging Face model card vllm-sr/Vela-2.0-9B, revision 068425b (retrieved 2026-10-10), with EVALUATION.md and TRAINING.md"
url: "https://huggingface.co/vllm-sr/Vela-2.0-9B"
tags: [source, model-card, system-one, decision-models, hallucination-detection, span-detection, ragtruth, lettucedetect, routing, vela]
---
# KR Labs and vLLM Semantic Router 2026 – Vela 2.0 9B model card

**Raw file**: `raw/KR Labs and vLLM Semantic Router 2026 - Vela 2.0 9B model card_ingested.md` (README, then EVALUATION.md and TRAINING.md of the same revision)

## Overview
Vela 2.0 ("Towards Open Foundation Routing Models") is a family of four SystemOne-compatible decision models (0.3B encoder, 0.8B, 4B, 9B) for routing, safety and **span-level hallucination and PII detection**, led by KR Labs (the authors of the LettuceDetect hallucination detectors) and vLLM Semantic Router. The 9B member: 7.9B reported parameters, a 32-layer Qwen3.5 hybrid (Gated DeltaNet plus gated GQA), 16,384-token input, Apache-2.0. Question types: Choice, Noul, Score, plus **Span** (labelled character spans with probabilities) and **Set** (multi-label). The card's quickstart asks, in one request, for PII spans over the request, **"Which spans of the answer are not supported by the context?"** over the answer (given `state.source`), and a routing choice. All results are self-reported but come with paired 95 % bootstrap intervals and explicit selection disclosures.

## Key Insights
1. **Training (TRAINING.md).** Starts from Decision-2.0-Lux-9B (vLLM-SR's general decision model on Qwen3.5-9B). Three stages:
   - Stage 1, full fine-tune for 4,000 steps: safety and prompt-attack data (12.2 % of steps), **LettuceDetect prose + code hallucination spans (11.3 %)**, generated PII (27.8 %), general decisions, synthetic router-style questions (23.1 %, kept only when a blind re-label agrees), and Decision 2.0 replay (7.5 %) with a KL term to the base.
   - Stage 2, 3,000 steps: a new word-by-label **router span head** (PII, hallucination, toxic spans) with the backbone frozen.
   - Stage 3, 3,000 steps: a second, broad span head for open-label extraction, everything else frozen; router outputs checked bitwise identical on 700 rows.
2. **Hallucination results (EVALUATION.md).**
   | Model | Hallucination, 10,698 examples (example-F1) | RAGTruth, 2,700 rows (example-F1) |
   |---|---:|---:|
   | Vela 2.0 9B | 0.885 | 0.774 |
   | Vela 2.0 4B | 0.874 | 0.770 |
   | Vela 2.0 0.8B | 0.828 | 0.652 |
   | Vela 2.0 0.3B (encoder) | 0.848 | 0.706 |
   | Vela 1.0 specialists (one model per task) | 0.875 | 0.747 |
   | LettuceDetect v2 mmBERT-base (hallucination only) | 0.869 | 0.743 |
   | LettuceDetect v2 qwen-2b (generative, hallucination only) | **0.921** | **0.817** |
   The 9B is +3.0 [+0.5, +5.4] points above LettuceDetect v2 mmBERT on RAGTruth, but **below the 2B generative LettuceDetect** (0.817). LettuceDetect RAGTruth values were re-scored by Vela's authors on the same 2,700 rows and reproduce its cards; the 10,698-example values are taken from LettuceDetect's cards.
3. **The generalist pays for routing.** On the Jev Decision Index 0.2.1 the 9B scores 41.63 (41.09 without optional Noul calibration) against 46.23 for its own base Decision-2.0-Lux-9B: "the routing recipe trades part of the base model's general-decision score for the router tasks".
4. **Selection disclosures.** Decoder checkpoints, temperatures and thresholds were selected on dev data only. The **0.3B encoder** used test results in its final release selection, and its shipped 8K PII number uses a threshold floor lowered after the test effect was seen (test-blind: 0.896 instead of 0.929). The card states this openly; the 0.3B numbers are therefore optimistic.
5. **Other numbers.** Safety mean AUC over 14 sets 0.921 (GLiNER2.5-Decide 0.704, not trained on these families); prompt attacks on unseen families AUC 0.989; `fastino/fast-decisions` 62.5 (GLiNER2.5-Decide 62.9); open-extraction latency 2,288 ms per question on a 3K-token context on one A40.

## Relevance to GroundOne
- **The only decision-model family in the tag that is trained and evaluated for RAG hallucination detection.** Its RAGTruth number is response/example-level F1 on 2,700 test rows, the same unit as the Decision Index's RAGTruth task and the RAGTruth paper's response F1 ([[RAGTruth]]), not GroundOne's sentence-level three-way metric.
- **Reference ladder for T1 at response level:** LettuceDetect qwen-2b 0.817 > pplx-decider-v1-27b 0.803 > Clef 0.794 > Vela 9B 0.774 > Jev 0.765 > LettuceDetect mmBERT 0.743 > Vela 0.3B 0.706 ([[Cloudflare 2026 - Clef model card]], [[Perplexity 2026 - pplx-decider-v1.1-27b model card]], [[multimodalart 2026 - Jev Decision Index (Hugging Face Space)]]). The specialists (LettuceDetect, Vela) are trained on RAGTruth-derived data, like GroundOne; the generalists are not known to be trained on RAGTruth (their training data are undisclosed or, for pplx-decider, list no RAGTruth source). Different harnesses: not a ranking.
- **Spans vs sentences.** Vela returns unsupported spans; GroundOne returns one verdict per sentence and separates *contradicted* from *not mentioned*, which Vela's single `unsupported` label does not.
- **Specialist vs generalist trade-off** (point 3) is the same trade-off GroundOne shows with weak transfer to VitaminC.

## Links
- Concepts: [[Hallucination Detection]], [[Groundedness Verification]], [[RAGTruth]], [[Decision-Model Landscape (Hugging Face, 2026)]], [[Decision-Model Benchmarks]], [[System One Models]]
- Related sources: [[Niu 2024 - RAGTruth]], [[Cloudflare 2026 - Clef model card]], [[multimodalart 2026 - Jev Decision Index (Hugging Face Space)]]
