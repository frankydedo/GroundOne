---
type: source
author: "Apple ML Explore (ml-explore)"
date: 2026
venue: "Source file Libraries/MLXLLM/Models/Qwen2.swift in ml-explore/mlx-swift-lm, main branch at release 3.32.3 (2026-09-30); MIT; retrieved 2026-10-18"
url: "https://github.com/ml-explore/mlx-swift-lm/blob/main/Libraries/MLXLLM/Models/Qwen2.swift"
tags: [source, mlx-swift, qwen2, model-implementation, readout, demo]
---
# ml-explore 2026 – mlx-swift-lm Qwen2 model source

**Raw file**: `raw/demo/ml-explore 2026 - mlx-swift-lm Qwen2 model source_ingested.md`

## Overview
The 276-line Swift implementation of the Qwen2 architecture (used by Qwen2.5) in MLX Swift LM. The `Models` directory of the same release lists about 60 architectures, among them Qwen2, Qwen3, Qwen3.5, Llama, LFM2 and Gemma 3/4.

## Key Insights
- **Qwen2 is supported** natively (`Qwen2Model`, `Qwen2Configuration` decoded from the Hugging Face `config.json`, `tie_word_embeddings` honoured).
- **Hidden states are reachable.** `Qwen2Model.model` is `public` (`Qwen2ModelInner`), and its `callAsFunction(_ inputs:, cache:)` returns the final hidden states after the last RMSNorm, for every position.
- **The output head is not public.** `lm_head` (a `Linear?`, absent when embeddings are tied, as in Qwen2.5 0.5B and 3B) and `embed_tokens` are internal to the module; the full `callAsFunction` applies the head to all positions. To apply the head only at chosen positions, an app either reads the embedding weights from the parameter tree or keeps its own copy of this file.
- `loraLayers` exposes the attention and MLP projections to the LoRA machinery ([[ml-explore 2026 - mlx-swift-lm LoRA adapters reference]]).

## Relevance to GroundOne
- GroundOne's readout ([[Letter-Token Readout]], `readout.py`) gathers the hidden states at the " Verdict:" markers and applies the head there, restricted to A/B/C. With this file the Swift port is: `model.model(ids)` → gather marker rows → multiply by the three embedding rows (tied head) → calibration. No architecture code has to be written.
- Applying the full head to every position would also work but computes 151k logits per token for nothing; the restricted readout is the same optimisation as in Python.

## Links
- Concepts: [[Qwen2.5]], [[Letter-Token Readout]], [[MLX Ecosystem]], [[Demo Application]]
- Related sources: [[Apple ML Explore 2026 - MLX Swift LM, LLMs and VLMs with MLX Swift (GitHub README)]], [[ml-explore 2026 - mlx-swift-lm LoRA adapters reference]]
