---
type: source
author: "Apple (WWDC25 session 298, presented by Angelos of the MLX team)"
date: 2025-06-09
venue: "Apple WWDC 2025 session video and transcript (developer.apple.com; retrieved 2026-10-18)"
url: "https://developer.apple.com/videos/play/wwdc2025/298/"
tags: [source, wwdc, mlx, mlx-lm, mlx-swift, llm, quantization, lora, fuse, kv-cache, fine-tuning, on-device]
---
# Apple WWDC 2025 – Explore large language models on Apple silicon with MLX

**Raw file**: `raw/demo/Apple WWDC 2025 - Explore large language models on Apple silicon with MLX_ingested.md`

## Overview
An official WWDC25 session (about 20 minutes; the presenter introduces himself only as "Angelos, an engineer in the MLX team") on running and fine-tuning LLMs on a Mac with **MLX LM**, the Python package and CLI built on MLX. It covers text generation (CLI and Python API), the KV cache, quantization with `mlx_lm.convert`, LoRA fine-tuning with `mlx_lm.lora`, fusing adapters with `mlx_lm.fuse`, and the same workflow in **MLX Swift**. The examples use Mistral-7B-Instruct-v0.3 (4-bit) and DeepSeek-V3-0324 (4-bit). It is Apple's own description of the pipeline GroundOne uses for training.

## Key Insights
- **Languages**: MLX "provides core operations in C, C++, Python, and Swift, with high-level APIs in Python and Swift". Everything "from the higher-level language model APIs down to the Metal kernels" is open source.
- **Scale demo**: DeepSeek (≈670B parameters) at 4.5 bits per weight needs about 380 GB for weights alone, run on an M3 Ultra with 512 GB unified memory, "faster than reading speeds".
- **Python API**: `load` returns model and tokenizer (from Hugging Face or a local path); `generate` runs the token loop. The loaded model "isn't some opaque object": it is a structured MLX `nn` module whose layers, parameters and attention modules can be inspected and modified ("model surgery").
- **KV cache**: `make_prompt_cache(model)` creates an explicit cache that can be reused across generations, edited in place, saved, or swapped between conversations ([[KV Cache]]).
- **Quantization**: built in; `mlx_lm.convert --quantize --q-bits 4 --q-group-size 64`. A Python `quant_predicate` gives per-layer precision (example: `lm_head` and `embed_tokens` at 6 bits, the rest at 4 bits, since embedding and final projection "tend to be more sensitive to quantization") ([[Quantization]]).
- **Fine-tuning**: full or LoRA, one command (`mlx_lm.lora --train --data ... --iters ... --batch-size ...`), with config files for finer control and `--mask-prompt`. LoRA "can even train adapters on top of quantized models"; a 4-bit Mistral reduces weight memory by "about 3.5 times". Data never leaves the device ([[LoRA]], [[Privacy and Data Sovereignty]]).
- **Adapters at inference**: `mlx_lm.generate ... --adapter "adapters"` (unfused).
- **Fusing**: `mlx_lm.fuse --model ... --adapter-path ... --save-path ...` yields "a single self-contained model" with the base architecture and parameter count. "There's no need to manually dequantize or requantize anything. MLX handles that automatically and preserves the same quantization used during training."
- **Swift (MLX Swift LM)**: a 28-line program. `LLMModelFactory.shared.loadContainer(configuration: ModelConfiguration(id:))` returns a **model container, "an actor that safely manages concurrent access to the model and tokenizer"**; `context.processor.prepare(input: UserInput(prompt:))` tokenizes; `generate(...)` streams tokens. A KV cache is created with `context.model.newCache(parameters:)` and driven by a low-level `TokenIterator`. "Same workflow, the same capabilities, but now fully native in Swift."
- The session does not mention Qwen models, logits access, or loading Python-trained adapters in Swift.

## Relevance to GroundOne
- **Citable source for GroundOne's training stack**: LoRA on an MLX-quantized base (GroundOne: 8-bit Qwen2.5 base, LoRA on all linear layers), on-device, data never leaving the machine.
- **Fuse vs adapter for the demo.** Shipping a fused checkpoint simplifies loading in Swift (one self-contained model, no adapter code). The fuse step dequantizes and requantizes behind the scenes ("MLX handles that automatically"), so a fused 8-bit model is not bit-identical to base + unfused adapter. The Python reference for the conformance test must therefore use the *same* artefact the app ships, or the tolerance must cover the fusion error. This is an inference from the transcript, to verify empirically.
- **The container actor maps onto GroundOne's engine design.** `engine.py` runs all MLX calls on one long-lived worker thread with a lock; in Swift the same serialisation is given by an actor-owned model container ([[Demo Application]]).
- **Model inspectability** (Python, and by the parity claim Swift) is what makes the marker readout possible: hidden states can be taken at the " Verdict:" positions before the output head ([[Letter-Token Readout]]).
- **KV cache API** matches GroundOne's design (a) (`make_prompt_cache` is what `backend.py` imports) and the generator's multi-turn use in the demo.

## Links
- Concepts: [[Apple Silicon and MLX]], [[MLX Ecosystem]], [[On-Device Inference]], [[Quantization]], [[LoRA]], [[KV Cache]], [[Letter-Token Readout]], [[Demo Application]], [[Demo Runtime Choice]], [[Privacy and Data Sovereignty]]
- Related sources: [[Apple WWDC 2025 - Get started with MLX for Apple silicon]], [[Apple ML Explore 2026 - MLX Swift LM, LLMs and VLMs with MLX Swift (GitHub README)]], [[Hu 2022 - LoRA]], [[Dettmers 2023 - QLoRA]], [[MLX README (ml-explore)]]
