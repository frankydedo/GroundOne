---
type: source
author: "Hugging Face and contributors"
date: 2026
venue: "GitHub repository README, huggingface/candle (LICENSE-MIT and LICENSE-APACHE files, i.e. dual MIT/Apache-2.0; retrieved 2026-10-18)"
url: "https://github.com/huggingface/candle"
tags: [source, ml-framework, rust, inference-engine, cuda, wasm, quantization, demo-runtime]
---
# Hugging Face 2026 – candle, a minimalist ML framework for Rust

**Raw file**: `raw/demo/Hugging Face 2026 - candle, minimalist ML framework for Rust (GitHub README)_ingested.md`

## Overview
Candle is a Rust tensor and model library "with a focus on performance (including GPU support) and ease of use", with a PyTorch-like API (`Tensor::randn`, `matmul`, `to_device`, `to_dtype`). Its stated goals are to "make serverless inference possible" with lightweight binaries, to "remove Python from production workloads" (Python overhead, the GIL), and to fit the Rust crates already in the HF ecosystem (safetensors, tokenizers). The workspace is split into `candle-core`, `candle-nn`, `candle-transformers`, `candle-kernels` (CUDA), `candle-flash-attn`, `candle-onnx`, `candle-datasets` and `candle-examples`.

## Key Insights
- **Backends documented in this README**: an optimised CPU backend (optional MKL on x86, Accelerate on Macs), a CUDA backend (multi-GPU via NCCL, optional cuDNN, an opt-in `cutile` feature for JIT-compiled CUDA kernels written in Rust) and WASM (models run in the browser). **The README does not mention Metal at all** (zero occurrences); any statement about candle on the Apple GPU needs a different source.
- **Model zoo**: LLaMA 1/2/3, Falcon, Gemma 1/2, Phi 1–3, Mistral, Mixtral, StableLM, Yi, Mamba, RWKV, StarCoder(2), T5, BERT/JinaBERT (sentence embeddings), Whisper, Stable Diffusion, YOLO, SAM, DINOv2 and others. For Qwen the list names **Qwen1.5, Qwen1.5 MoE and Qwen3 MoE** (quantised Qwen3 MoE 16B-A3B/32B-A3B); Qwen2/Qwen2.5 are not named in the README.
- **Formats and quantisation**: loads safetensors, npz, ggml and PyTorch files; quantisation uses "the llama.cpp quantized types" (GGUF).
- **Training** is listed as a feature ("Model training"); user-defined kernels (e.g. flash-attention v2) can be embedded.
- **LoRA** is not in core: the README points to the external `candle-lora` crate. Other ecosystem projects: `candle-vllm` and `vllm.rs` (OpenAI-compatible serving), `kalosm` (local models with controlled generation and in-memory vector DBs), `atoma-infer`.
- Common errors section shows the Mac build path is the Accelerate feature (missing `sgemm_`/`dgemm_` symbols on arm64 if the linker flag is absent).

## Relevance to GroundOne
- **A rejected runtime for the demo** ([[Demo Runtime Choice]]). A Rust stack (Tauri UI + candle) would have to (1) run Qwen2.5 on the Apple GPU through a Metal path that this source does not document, (2) re-implement LoRA through a third-party crate, and (3) abandon the MLX 8-bit weights and adapters actually trained and calibrated, re-quantising to llama.cpp types. Point (3) is the decisive one: the calibration (temperature, per-class bias, served threshold) is bound to the model fingerprint, so a different numeric stack would need its own parity check and recalibration.
- **What candle does well and GroundOne does not need**: CUDA/NCCL and WASM deployment, a wide model zoo for generation. GroundOne's readout needs only a forward pass with logits at marker positions on one Mac, which MLX Swift already provides in-process ([[MLX Ecosystem]]).
- Honest framing for the thesis: candle is a mature Rust option for CUDA and CPU; on Apple Silicon its maturity relative to MLX is not established by this source and must not be claimed either way.

## Links
- Concepts: [[Demo Runtime Choice]], [[Demo Application]], [[On-Device Inference]], [[Apple Silicon and MLX]], [[MLX Ecosystem]], [[Quantization]], [[Local Inference Hardware]]
- Related: [[Tauri 2026 - Tauri, desktop and mobile apps with a web frontend (GitHub README)]], [[oxiglade 2026 - mlx-rs, unofficial Rust bindings to MLX (GitHub README)]], [[llama.cpp README (ggml-org)]], [[MLX README (ml-explore)]]
