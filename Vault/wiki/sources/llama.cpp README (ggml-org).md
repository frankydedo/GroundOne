---
type: source
author: "ggml-org (Georgi Gerganov and contributors)"
date: 2023
venue: "Software (GitHub README), MIT licence; README retrieved 2026"
url: "https://github.com/ggml-org/llama.cpp"
tags: [source, software, llama-cpp, ggml, gguf, quantization, runtime, on-device]
---
# llama.cpp README (ggml-org)

**Raw file**: `raw/llama.cpp README (ggml-org)_ingested.md`

## Overview
README of **llama.cpp**, "LLM inference in C/C++", built on the **ggml** tensor library (MIT licence). Its stated goal is "to enable LLM (and VLM) inference with minimal setup and state-of-the-art performance on a wide range of hardware – locally and in the cloud". It is the reference open runtime for local LLM inference and the runtime of [[Rizzo-Flow]] as used in the thesis. (The project start date, 2023, is general knowledge; the README itself does not state it.)

## Key Insights
1. **Plain C/C++ without dependencies.**
2. **"Apple silicon is a first-class citizen"**, optimised through ARM NEON, Accelerate and Metal.
3. **Integer quantisation at 1.5, 2, 3, 4, 5, 6 and 8 bits** "for faster inference and reduced memory use" (models are distributed in the GGUF format, as in the quick-start `-GGUF` model names).
4. **Many backends**: Metal (Apple silicon), CUDA, HIP, Vulkan, SYCL, OpenCL (Adreno), Hexagon (Snapdragon), CANN (Ascend), WebGPU, BLAS, RPC and others (backend table).
5. **CPU+GPU hybrid inference** to partially accelerate models larger than the GPU memory.
6. **Tools**: `llama cli` for interactive use and `llama serve`, an **OpenAI-compatible HTTP API server** with a built-in web UI; models can be pulled directly from Hugging Face (`-hf`).

## Relevance to GroundOne
- **Runtime of baseline B3.** Rizzo-Flow (Spark-X2.5-4B) runs in the thesis as a llama.cpp server with Q4 GGUF weights, queried over HTTP. GroundOne runs in-process in MLX with 8-bit weights. Because runtime, quantisation, model size and transport all differ, **no latency claim is made against Rizzo-Flow** (its 6.88 s per answer at K ≥ 14 is reported with this caveat). See [[Rizzo-Flow]].
- **History of local inference.** llama.cpp, GGUF quantisation and the distribution layers built on it (e.g. Ollama, LM Studio) are the main open path to local LLMs; MLX is Apple's own path. Both belong in the thesis overview of local runtimes ([[On-Device Inference]]).
- **Possible fair comparison.** A like-for-like latency comparison with Rizzo-Flow would need both systems served over HTTP (GroundOne's API now serves design b), or both in the same runtime.

## Links
- Concepts: [[On-Device Inference]], [[Apple Silicon and MLX]], [[Rizzo-Flow]], [[Prefill and Decode]]
- Related sources: [[MLX README (ml-explore)]], [[Rizzo-Flow README]], [[Alizadeh 2024 - LLM in a flash]]
