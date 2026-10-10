---
type: source
author: "FluidInference"
date: 2026
venue: "Hugging Face model card FluidInference/d1-omni-600m-coreml, revision 8ae382b (retrieved 2026-10-10)"
url: "https://huggingface.co/FluidInference/d1-omni-600m-coreml"
tags: [source, model-card, coreml, apple-neural-engine, on-device, decision-models, encoder, d1]
---
# FluidInference 2026 – d1-omni-600M Core ML model card

**Raw file**: `raw/FluidInference 2026 - d1-omni-600M Core ML model card_ingested.md`

## Overview
A Core ML conversion of the **text path** of Liquid AI's d1-omni-600M ([[LiquidAI 2026 - d1-3B model card]]): the LFM2.5 encoder trunk plus the decision head, answering yes/no, choice and score questions in one forward pass with zero generated tokens (vision and audio encoders not included). One fp16 multifunction package (729 MB); Swift runtime and demos in FluidInference's FluidUse. FluidInference has 14 repositories in the tag, mostly Core ML ports of other decision models (Laya, GLiNER2.5-Decide, Clef-flash, Verdict and others).

## Key Insights
1. **Interface reveals the readout.** Functions `L{tokens}_K{options}_B{batch}` take `input_ids`, `attention_mask`, `marker_pos`, `marker_mask` and `qtype`, and output one logit per marker slot; the host divides by the temperature from `config.json` and softmaxes over the used markers (yes/no reads as [no, yes]). d1-omni is therefore an **encoder with per-option marker positions** (family d of [[System One Models]]), unlike the decoder letter readout of d1-3B.
2. **Neural Engine numerics.** The ANE's fused `silu` is about 1.4 % off, which compounded over 16 SwiGLU MLPs flipped 41 of 492 Snake decisions vs PyTorch; rewriting SiLU as `x * 0.5 * (1 + tanh(x / 2))` reduced this to 2 of 492 (max |Δp| 0.017). 99.1 % of ops (1,140 of 1,150) run on the Neural Engine.
3. **Results on an Apple M5 Pro.** Civil Comments toxicity (5,000 comments, flag at P(toxic) ≥ 0.8): 95.4 % agreement with human labels (toxic recall 67.8 %, precision 82.4 %), 0 of 5,000 flags differing from PyTorch. Throughput: 102 comments/s on the ANE alone, 215 on the GPU (8 per call), 267 with ANE + GPU. A single question on the ANE takes about 4.6 ms at 64 tokens and 6.6 ms at 128.
4. **Licence.** LFM Open License v1.0: free to use and redistribute, but commercial use not licensed for entities with US$10M or more in annual revenue.

## Relevance to GroundOne
- **Decision models reach the Neural Engine.** A 600M encoder decision model runs almost entirely on the ANE at single-digit milliseconds per short decision: the low-power end of the locality pillar, beyond GPU/MLX ([[On-Device Inference]], [[Apple Silicon and MLX]]).
- **Short contexts only.** Buckets stop at 256 tokens; groundedness needs the whole retrieved document, so this path does not transfer to GroundOne's task without long-context buckets.
- **Precision can flip decisions.** The SiLU fix is a concrete example of hardware numerics changing typed decisions, a check (agreement vs reference on a fixed set) worth reporting for GroundOne's 8-bit MLX models.

## Links
- Concepts: [[On-Device Inference]], [[Apple Silicon and MLX]], [[System One Models]], [[Decision-Model Landscape (Hugging Face, 2026)]]
- Related sources: [[LiquidAI 2026 - d1-3B model card]], [[Gunter 2024 - Apple Intelligence Foundation Language Models]]
