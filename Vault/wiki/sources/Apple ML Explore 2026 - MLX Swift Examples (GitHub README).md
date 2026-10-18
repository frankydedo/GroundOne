---
type: source
author: "Apple ML Explore (ml-explore)"
date: 2026
venue: "GitHub repository README, ml-explore/mlx-swift-examples (retrieved 2026-10-18)"
url: "https://github.com/ml-explore/mlx-swift-examples"
tags: [source, mlx, mlx-swift, swift, examples, ios, macos, lora, metal-kernels, demo]
---
# Apple ML Explore 2026 – MLX Swift Examples

**Raw file**: `raw/demo/Apple ML Explore 2026 - MLX Swift Examples (GitHub README)_ingested.md`

## Overview
The official collection of example applications and command-line tools for [[Apple ML Explore 2026 - MLX Swift (GitHub README)|MLX Swift]]. The language-model examples use models implemented in [[Apple ML Explore 2026 - MLX Swift LM, LLMs and VLMs with MLX Swift (GitHub README)|MLX Swift LM]], to which the reusable LLM/VLM libraries have moved. Previous URLs and tags still work, but all future updates to those libraries happen in mlx-swift-lm.

## Key Insights
- **Applications** (most run on both iOS and macOS): MNISTTrainer; **LLMBasic** (minimal: load the model and evaluate a prompt); **LLMEval** (downloads an LLM and tokenizer from Hugging Face, preset prompts, tool integration, "detailed statistics on the run"); **MLXChatExample** (chat app with LLMs and VLMs); **LoRATrainingExample** (macOS: downloads an LLM and fine-tunes it with LoRA); StableDiffusionExample.
- **Tools**: `llm-tool` (text generation with Hugging Face LLMs), `image-tool`, `mnist-tool`, LinearModelTraining. Run from Xcode or with `./mlx-run llm-tool --prompt ...`; `mlx-run` locates the Xcode-built binaries.
- **Numerical computing examples**: CurveFit (`MLX.grad`), HeatTransfer (compiled `roll`), Mandelbrot (plain vs compiled MLX vs a custom Metal kernel through `MLXFast.metalKernel`). This shows that `compile` and custom kernels are exposed in Swift.
- **Reusable libraries still here**: `StableDiffusion`, `MLXMNIST`.
- No supported-model list, release dates or star counts are given.

## Relevance to GroundOne
- **Templates for the demo** ([[Demo Application]]). LLMBasic is the minimal skeleton for loading a local model in an app; LLMEval shows run statistics (useful for showing latency in the UI); MLXChatExample is a SwiftUI chat app with a generator, close to the RAG front-end the demo needs.
- **LoRATrainingExample** shows LoRA in Swift on macOS. GroundOne trains in Python, so the app only needs to *load* adapters or fused weights, not train. The example still shows that LoRA layers exist in the Swift stack.
- **Custom Metal kernels and `compile` in Swift** mean that a Python optimisation, if ever needed, has a Swift counterpart. This supports the parity argument in [[Demo Runtime Choice]].
- **Maturity signal**: an official, multi-app example suite maintained alongside the library, which is weaker evidence than shipping products but stronger than the two examples of [[oxiglade 2026 - mlx-rs, unofficial Rust bindings to MLX (GitHub README)|mlx-rs]].

## Links
- Concepts: [[MLX Ecosystem]], [[Demo Application]], [[Demo Runtime Choice]], [[Apple Silicon and MLX]], [[LoRA]], [[On-Device Inference]]
- Related sources: [[Apple ML Explore 2026 - MLX Swift (GitHub README)]], [[Apple ML Explore 2026 - MLX Swift LM, LLMs and VLMs with MLX Swift (GitHub README)]], [[Apple WWDC 2025 - Get started with MLX for Apple silicon]]
