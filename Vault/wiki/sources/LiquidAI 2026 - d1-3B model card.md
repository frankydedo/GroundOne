---
type: source
author: "Liquid AI"
date: 2026
venue: "Hugging Face model cards LiquidAI/d1-3B (revision 051bcc4) and LiquidAI/d1-omni-600M (revision 02b55d7), retrieved 2026-10-10; repository code prompt.py and runner.py"
url: "https://huggingface.co/LiquidAI/d1-3B"
tags: [source, model-card, system-one, decision-models, established-org, letter-readout, shared-prefix, edge, apple-silicon, d1]
---
# LiquidAI 2026 – d1-3B model card

**Raw file**: `raw/LiquidAI 2026 - d1-3B model card_ingested.md`
**Supplementary raw files**: `raw/LiquidAI 2026 - d1-omni-600M model card_ingested.md`, `raw/LiquidAI 2026 - d1-3B readout code (prompt.py, runner.py)_ingested.md`

## Overview
**d1** ("open d1") is Liquid AI's family of edge decision models, released 2026-10-05 under the LFM Open License v1.0 (not Apache; see the Core ML port for the revenue clause). Two checkpoints:
- **d1-3B**: 3.12B parameters, built on LFM2.5-VL-3B (hybrid LFM2 backbone plus a 400M SigLIP2 vision encoder), 32,768-token context. Text, JSON and images.
- **d1-omni-600M**: 587M parameters, built on LFM2.5-Encoder-350M (a 381M shared trunk and decision head, a 94M vision encoder, a 112M FastConformer audio encoder), 16,384-token context. Text, images or up to 30 s of speech. Called "an early research release"; no speed numbers.

Both take the Decision Index schema (`noul`, `choice`, `score`) and return `{"answers", "usage": {"output_tokens": 0}}`. All numbers are vendor-measured.

## Key Insights
1. **d1-3B is a letter-code readout over the LM head (verified in code).** `prompt.py` states: "A System One decision is a single forward pass that stops at the answer slot … the answer is a softmax over its options' tokens."
   - Options are rendered with single-token codes (A..Z, then 00..99, then fallbacks), `noul` reads the max over `yes/Yes/YES` vs `no/No/NO`, `score` reads digits 0–9.
   - Each option's score is the max log-probability over its token forms; a softmax over these scores (optionally after calibration) gives the distribution. This is family (b) of [[System One Models]], the same family as [[GroundOne]], [[SemIf]] and [[Rizzo-Flow]] ([[Letter-Token Readout]]).
2. **Shared state as a tree, in one pass (verified in code).** `runner.py` encodes the state once as a **trunk** and each question as a **branch**; a tree-attention kernel (`hybrid.py`) lets each branch attend to the trunk and to itself, packs branches with no padding, and reads logits at each branch's end. "Nothing is cached, copied or padded." Requests with one question and no image are packed together under a token budget. This is GroundOne's design (a) (shared prefix plus one question per decision; [[KV Cache]]) implemented as a single tree-masked forward pass instead of a replicated KV cache.
3. **d1-omni-600M is an encoder with per-option markers.** Its Core ML export exposes `marker_pos`, `marker_mask` and `qtype` inputs and outputs one logit per marker ([[FluidInference 2026 - d1-omni-600M Core ML model card]]): family (d), like [[Laya]]. Text answers use per-type temperatures stored in `config.json`; image and audio answers are the raw softmax.
4. **Speed on edge hardware (d1-3B, warm, one request at a time).**
   | Hardware | 1 question | 3 questions, one pass | 3.4k-token state | 384 px image | 64 states packed |
   |---|---:|---:|---:|---:|---:|
   | Apple M5 Pro (`mps`) | 30 ms | 41 ms | 640 ms | 62 ms | 78 / s |
   | NVIDIA Jetson Orin Nano | 50 ms | 73 ms | 1,640 ms | 202 ms | 38 / s |
   | NVIDIA RTX 4090 (CUDA graphs) | 8 ms | 21 ms | 102 ms | 17 ms | 475 / s |
5. **Quality (vendor, official scorer, not leaderboard submissions).** Decision Index 0.2.1: d1-3B 48.57, which the card calls the best decision model under 10B (Winnow-12B 50.02 is the only row above it); d1-omni-600M 15.95. "Benchmarks as decisions" mean (7 tasks without HelpSteer2): d1-3B 82.9, d1-omni-600M 78.4. On XNLI d1-3B scores 85.0; on PubMedQA 66.0. The d1-3B card's 8-task mean (77.1) includes HelpSteer2, which the omni card drops because it "may overlap with d1-omni-600M's training data".
6. **Vision as decisions.** 11 image benchmarks, mean 74.1 vs 73.9 for the base VLM; with the images removed the same questions score 45.1.
7. **Numerics.** The omni model was trained in float32; float16 kept the same top answer on all 243 text, 214 image and 416 audio check rows, while bfloat16 changed 0.8 % of text and 1.7 % of audio answers.

## Relevance to GroundOne
- **An established lab ships GroundOne's readout family at GroundOne's scale.** d1-3B is a 3B decoder, restricted letter readout, multi-question single pass, with Apple-Silicon latencies. It is the closest industrial analogue of GroundOne-3B, but general-purpose and zero-shot, not specialised on groundedness.
- **Design (a) vs design (b).** d1 shares the state across questions with tree attention (one branch per question). GroundOne's design (b) goes further for its task: the K questions are the answer's own sentences, so a single linear sequence with a marker after each sentence suffices and no branching is needed.
- **No groundedness benchmark.** The card reports no RAGTruth, LLM-AggreFact or claim-verification number; XNLI (85.0) is the closest. A d1-3B zero-shot run on T1/T2 would be a cheap, relevant baseline (licence permitting).
- **Locality pillar.** 30 ms per decision and 640 ms for a 3.4k-token state on an M5 Pro; compare GroundOne's 0.41 s / 2.57 s per answer at K ≥ 14 on an M4 ([[GroundOne Results]]). Different chips, tasks and runtimes: context only.

## Links
- Concepts: [[System One Models]], [[Letter-Token Readout]], [[Decision-Model Landscape (Hugging Face, 2026)]], [[On-Device Inference]], [[Apple Silicon and MLX]], [[KV Cache]]
- Related sources: [[FluidInference 2026 - d1-omni-600M Core ML model card]], [[multimodalart 2026 - Jev Decision Index (Hugging Face Space)]]
