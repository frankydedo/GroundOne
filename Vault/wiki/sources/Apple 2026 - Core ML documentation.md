---
type: source
author: "Apple Inc."
date: 2026
venue: "Apple Developer Documentation, Core ML framework landing page (documentation JSON; retrieved 2026-10-18)"
url: "https://developer.apple.com/documentation/coreml"
tags: [source, apple, on-device, neural-engine, model-conversion, coremltools, demo-runtime]
---
# Apple 2026 – Core ML documentation

**Raw file**: `raw/demo/Apple 2026 - Core ML documentation_ingested.md`

## Overview
Landing page of Core ML, Apple's framework to "integrate machine learning models into your app". Core ML gives "a unified representation for all models" and runs predictions, training and fine-tuning "all on a person's device". **Thin extraction**: overview plus topic titles only; no API details, operator coverage or LLM-specific guidance.

## Key Insights
- **Model sources**: Create ML (bundled with Xcode) produces Core ML models directly; models from "a wide variety of other machine learning libraries" are converted with **coremltools**. On-device retraining/fine-tuning with the user's data is supported.
- **Compute**: Core ML uses **CPU, GPU and Neural Engine** "while minimizing its memory footprint and power consumption"; running strictly on device removes the network dependency (privacy, responsiveness).
- **Stack position**: foundation for Vision, Natural Language, Speech and SoundAnalysis; built on Accelerate, BNNS and Metal Performance Shaders.
- **Pointer to a newer framework**: "If your app integrates AI models using the latest architectures and inference techniques, see **CoreAI**." CoreAI is not described in the raw.
- **Topic titles** (not extracted): Core ML models, Model inputs and outputs, App integration, Model encryption, Compute devices, **Compute plan**, **Model state**, Model tensor, Model structure, Model deployments, Optimization.

## Relevance to GroundOne
- **Conversion path, not the first choice** ([[Demo Runtime Choice]]). Serving GroundOne through Core ML would mean merging the LoRA adapter into Qwen2.5, converting with coremltools, re-quantising, and exposing logits (or the final hidden states) at the marker positions. Every step changes the numerics relative to the MLX 8-bit model that was evaluated, and the calibration (temperature, per-class bias, served threshold) is bound to that model's fingerprint, so a Core ML build would require a parity test on the frozen sets and possibly recalibration.
- **What it would buy**: Neural Engine execution and the power savings Apple attributes to it; this is attractive for an energy argument but is not established for a 0.5B/3B decoder by this source. "Model state" suggests stateful (KV-cache-like) models are supported, but the raw gives no details.
- **Decision for the demo**: MLX Swift in-process reuses the exact trained artefacts; Core ML/ANE (or CoreAI) is future work and can be named as such in the thesis, without performance claims.

## Links
- Concepts: [[Demo Runtime Choice]], [[On-Device Inference]], [[Apple Silicon and MLX]], [[Local Inference Hardware]], [[Quantization]], [[MLX Ecosystem]]
- Related: [[Apple 2026 - Foundation Models framework documentation]], [[Gunter 2024 - Apple Intelligence Foundation Language Models]], [[Apple 2026 - NLEmbedding documentation]], [[Apple ML Research 2025 - Exploring LLMs with MLX and the neural accelerators in the M5 GPU]]
