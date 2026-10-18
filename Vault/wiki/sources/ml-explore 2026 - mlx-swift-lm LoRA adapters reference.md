---
type: source
author: "Apple ML Explore (ml-explore)"
date: 2026
venue: "Reference document in the ml-explore/mlx-swift-lm repository (skills/mlx-swift-lm/references/lora-adapters.md), main branch at release 3.32.3 (2026-09-30); retrieved 2026-10-18"
url: "https://github.com/ml-explore/mlx-swift-lm/blob/main/skills/mlx-swift-lm/references/lora-adapters.md"
tags: [source, mlx-swift, lora, dora, adapters, quantization, demo]
---
# ml-explore 2026 – mlx-swift-lm LoRA adapters reference

**Raw file**: `raw/demo/ml-explore 2026 - mlx-swift-lm LoRA adapters reference_ingested.md`

## Overview
The repository's own reference for LoRA and DoRA in MLX Swift LM. It documents the types (`LoRAConfiguration`, `LoRAContainer`, `LoRAModel`, `LoRALinear`, `QLoRALinear`, `DoRALinear`, `QDoRALinear`), the `adapter_config.json` format, and the operations to load, apply, fuse and remove an adapter at runtime. Fetched to settle the questions that the [[Apple ML Explore 2026 - MLX Swift LM, LLMs and VLMs with MLX Swift (GitHub README)|README]] left open.

## Key Insights
- **Adapter format = mlx-lm format.** `adapter_config.json` has `fine_tune_type`, `num_layers` and `lora_parameters` {`rank`, `scale`, `dropout`, optional `keys`}, the same keys that Python `mlx-lm` writes (and that GroundOne's runs contain: `lora`, 36 layers, rank 16, scale 2.0, dropout 0.05 for the 3B). Weights are `adapters.safetensors` in the same directory.
- **Loading:** `LoRAContainer.from(directory:)` then `adapter.load(into: model)`, which replaces `Linear` with `LoRALinear` and `QuantizedLinear` with `QLoRALinear` (LoRA over a quantised base, as GroundOne was trained).
- **Fuse and unload:** `adapter.fuse(with: model)` merges permanently; `adapter.unload(from: model)` restores the original layers. Loading and unloading at runtime makes it possible to use one base model both as a generator (no adapter) and as a verifier (adapter).
- **Forward:** `y = Wx + scale · (dropout(x) A B)`; dropout is inactive in evaluation mode (`ModelContext` sets it; direct calls need `model.train(false)`).
- `keys = nil` means all linear layers, which matches GroundOne's "LoRA on all linear layers".

## Relevance to GroundOne
- Removes the main unknown of the Swift port: the trained adapters can be loaded as they are, with no fusion or conversion ([[Demo Runtime Choice]], [[Demo Application]]). Numerical parity with Python is still to be shown by the conformance test.
- The load/unload pair supports the "shared base" option of the demo: one 8-bit Qwen2.5-3B in memory for both roles.

## Links
- Concepts: [[LoRA]], [[MLX Ecosystem]], [[Demo Application]], [[Demo Runtime Choice]], [[Quantization]]
- Related sources: [[ml-explore 2026 - mlx-swift-lm Qwen2 model source]], [[Apple WWDC 2025 - Explore large language models on Apple silicon with MLX]], [[Hu 2022 - LoRA]]
