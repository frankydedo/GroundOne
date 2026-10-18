---
type: source
author: "Apple ML Explore (ml-explore); maintainer contact David Koski"
date: 2026
venue: "GitHub repository README, ml-explore/mlx-swift-lm (version 3.x on main, installation pinned to 3.32.3; retrieved 2026-10-18)"
url: "https://github.com/ml-explore/mlx-swift-lm"
tags: [source, mlx, mlx-swift, swift, llm, lora, quantization, tokenizer, foundation-models, guided-generation, demo]
---
# Apple ML Explore 2026 – MLX Swift LM: LLMs and VLMs with MLX Swift

**Raw file**: `raw/demo/Apple ML Explore 2026 - MLX Swift LM, LLMs and VLMs with MLX Swift (GitHub README)_ingested.md`

## Overview
MLX Swift LM is the official Swift package for building tools and applications with LLMs and VLMs on top of [[Apple ML Explore 2026 - MLX Swift (GitHub README)|MLX Swift]]. It is the Swift counterpart of Python `mlx-lm`: model loading, model implementations, generation, embeddings, LoRA and full fine-tuning. The libraries (`MLXLMCommon`, `MLXLLM`, `MLXVLM`, `MLXEmbedders`) were moved here from mlx-swift-examples. The `main` branch is a new major version, 3.x, which decouples the package from specific tokenizer and downloader packages, with breaking changes.

## Key Insights
- **Libraries**: `MLXLMCommon` (common API for LLM and VLM), `MLXLLM` and `MLXVLM` ("example implementations" of model architectures), `MLXEmbedders` (encoders and embedding models), `MLXGuidedGeneration` (grammar-constrained generation from JSON Schema or EBNF, "for any MLX model"), `MLXFoundationModels` (bridge to Apple's `FoundationModels.LanguageModel`/`LanguageModelSession`; needs the macOS/iOS/visionOS 27.0 SDK), `MLXScriptedLM` (scripted tokenizers and models to stub behaviour in tests without weights).
- **Fine-tuning**: "Low-rank (LoRA) and full model fine-tuning with support for quantized models."
- **Tokenizers and downloaders are pluggable** through protocol conformance; the quick start uses Hugging Face's `swift-huggingface` (≥ 0.9.0) and `swift-transformers` (`Tokenizers`, ≥ 1.3.0) through the `MLXHuggingFace` macros. The using guide covers "local-only weights" and custom downloaders.
- **Installation**: `.package(url: "https://github.com/ml-explore/mlx-swift-lm", .upToNextMinor(from: "3.32.3"))`; CI pins `swift-format` 603.0.0.
- **High-level API**: `#huggingFaceLoadModelContainer(configuration: LLMRegistry.gemma3_1B_qat_4bit)` then `ChatSession(model).respond(to:)`. The API shown is generation-oriented.
- **Docs** include "Porting and implementing models" and "Techniques for developing in mlx-swift-lm".
- **Not in the README**: the list of supported architectures (Qwen2/Qwen2.5 is not named), how a LoRA adapter trained with Python `mlx-lm` is loaded, and any API that returns logits or hidden states at chosen positions. These must be checked in the source or documentation.

## Relevance to GroundOne
- **The model layer for the demo** ([[Demo Runtime Choice]]). Reusing `MLXLLM`'s model implementation avoids porting Qwen2.5 by hand. The registry is not listed in this README, so Qwen2 support must be confirmed in the source (a model page or `LLMRegistry` entry) before relying on it.
- **Loading GroundOne weights.** The base is an MLX 8-bit checkpoint (`lmstudio-community/Qwen2.5-{0.5B,3B}-Instruct-MLX-8bit`) plus a LoRA `adapters.safetensors`. The README states LoRA support for quantized models but not compatibility with adapters saved by Python `mlx-lm`. The safer route for the app is to load local fused weights (see [[Apple WWDC 2025 - Explore large language models on Apple silicon with MLX]] on `mlx_lm.fuse`) or to apply the adapter at load time with a small loader. Fusing into 8-bit weights re-quantizes them, so fused and unfused probabilities may differ slightly. The conformance test should be run against whichever form is shipped.
- **Readout.** The chat and generation APIs are not enough. GroundOne needs one forward pass over the marked prompt and the A/B/C logits at every " Verdict:" marker ([[Letter-Token Readout]]). This needs direct access to the model module (call it on a token array, take hidden states or logits at chosen positions). The README neither confirms nor excludes this access; the open-source model classes suggest it is possible, but this is unverified.
- **Tokenizer parity risk.** Tokenization in the app goes through `swift-transformers`, not Python `tokenizers`. Token-ID equality on the frozen test prompts must be part of the conformance test.
- **Useful extras.** `MLXEmbedders` could supply the retriever's embedding model in-process. `MLXGuidedGeneration` and `MLXFoundationModels` could constrain or swap the generator in the [[Demo Application]].
- **Maturity.** Official and actively released (3.32.x), but the 3.x major version introduced breaking changes, so the version must be pinned.

## Links
- Concepts: [[MLX Ecosystem]], [[Demo Application]], [[Demo Runtime Choice]], [[LoRA]], [[Quantization]], [[Qwen2.5]], [[Constrained Decoding]], [[Letter-Token Readout]], [[Retrieval-Augmented Generation]]
- Related sources: [[Apple ML Explore 2026 - MLX Swift (GitHub README)]], [[Apple ML Explore 2026 - MLX Swift Examples (GitHub README)]], [[Apple WWDC 2025 - Explore large language models on Apple silicon with MLX]], [[Hu 2022 - LoRA]]

## Verified in the source (2026-10-18)
The three open points above were checked in the repository at release 3.32.3: Qwen2 is implemented (`Libraries/MLXLLM/Models/Qwen2.swift`), adapters in the mlx-lm format load with `LoRAContainer.from(directory:)` and can also be fused or unloaded, and the final hidden states are public through `Qwen2Model.model` while the head is internal. See [[ml-explore 2026 - mlx-swift-lm Qwen2 model source]] and [[ml-explore 2026 - mlx-swift-lm LoRA adapters reference]]. The "safer route" of fusing is therefore not needed.
