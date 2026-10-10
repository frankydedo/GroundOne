---
type: source
author: "Hugging Face Hub API (listing compiled for this wiki)"
date: 2026-10-10
venue: "https://huggingface.co/api/models?filter=decision-model, all pages, deduplicated; fetched 2026-10-10"
url: "https://huggingface.co/models?other=decision-model"
tags: [source, dataset, hugging-face, decision-models, ecosystem, survey-data]
---
# Hugging Face 2026 – decision-model tag listing (2026-10-10)

**Raw file**: `raw/Hugging Face 2026 - decision-model tag listing (2026-10-10)_ingested.json`

## Overview
The full listing of models carrying the Hub tag `decision-model` (singular), as returned by the Hub API query `api/models?filter=decision-model` on 2026-10-10 (the `other=` parameter used by the web URL does not work in the API). One record per model: `id`, `likes`, `downloads`, `pipeline_tag`, `library_name`, `tags`, `createdAt`. It is the data behind [[Decision-Model Landscape (Hugging Face, 2026)]]. Likes and downloads are a snapshot and drift daily.

## Key numbers (computed from the file)
- **1,529 models from 610 authors.** Created 2026-09 (862) and 2026-10 up to the 10th (665); two older outliers (2026-06-07, 2026-08-20).
- **Libraries** (`library_name`): transformers 392, none declared 344, peft 221, mlx 150, gguf 83, laya 54, onnx 42, pytorch 38, jevify 29, coreml 18, transformers.js 16, llama.cpp 15, coreai 14.
- **Pipelines**: text-classification 686, none 416, image-text-to-text 130, zero-shot-classification 127, text-generation 110.
- **Tags**: system-one 499, calibration 388, gguf 322, lora 319, typed-decisions 273, jev 228, mlx 163, laya 130, onnx 114, apple-silicon 103, on-device 56, coreml 35, hallucination-detection 11.
- **Names**: 304 model ids contain "jev", 146 contain "laya".
- **Licences**: apache-2.0 1,186; cc-by-nc-4.0 94.
- **Base models** (direct `base_model:` tags): Qwen 460 (Qwen3.5-4B alone 102), Laya checkpoints 109, Gemma 68, ModernBERT/mmBERT/Ettin encoders 63, LiquidAI 30, other (mostly community decision models) 685.
- **Popularity is concentrated.** 14,912 likes in total, of which the top three models hold 7,980 (autotrust/JEV-27B-VL 3,726, autotrust/GEV-26B-Decide 2,277, Cloudflare/clef 1,977); 931 models have zero likes; the median is 0. 4.68M downloads in total, of which the top three (all autotrust) hold 2.79M.
- **Top uploaders** by count: mradermacher 63 (quantisations), mstrasser 32, Praveenrajus 30, prithivMLmods 26, startlux-models 21, vllm-sr 20, ollaya-dev 20.
- **arXiv tags**: 39 models carry at least one; most point to backbone papers (ModernBERT, mmBERT, LFM2, GLiNER2). Decision-model papers tagged: 2609.29429 ([[Guo 2026 - Just Ask Jev (arXiv 2609.29429)]]), 2609.26550 ([[Li 2026 - JEV-as-a-Judge (arXiv 2609.26550)]]), 2610.02486 ([[Deka 2026 - From Retrieval to Typed Decisions SBERT2S1 (arXiv 2610.02486)]]); also 2607.02512 (Program-as-Weights, fuzzy functions compiled into adapters for a 0.6B interpreter) and 2609.08183 (NeoHorse-1, agentic post-training), not decision-model papers.

## Relevance to GroundOne
Quantifies the ecosystem GroundOne would be published into, and shows that only about 0.7 % of it (11 models) is tagged for hallucination detection.

## Links
[[Decision-Model Landscape (Hugging Face, 2026)]], [[Hugging Face decision-models Tag]]
