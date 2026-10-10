---
type: source
author: "mlx-community (Hugging Face organisation for MLX conversions)"
date: 2026
venue: "Hugging Face model card mlx-community/clef-flash-4bit, revision b5adbe2 (retrieved 2026-10-10)"
url: "https://huggingface.co/mlx-community/clef-flash-4bit"
tags: [source, model-card, mlx, apple-silicon, on-device, quantization, decision-models, clef]
---
# mlx-community 2026 – clef-flash-4bit model card

**Raw file**: `raw/mlx-community 2026 - clef-flash-4bit model card_ingested.md`

## Overview
An MLX conversion of Cloudflare's 9B decision model Clef-flash ([[Cloudflare 2026 - Clef model card]]) for Apple Silicon. The backbone is quantised to 4 bits (`mlx_vlm.convert -q --q-bits 4 --q-group-size 64`, vision tower kept in bf16); the joint schema head is copied unchanged (bf16) and run by a bundled `clef_mlx.py`. The card warns that generic text-generation tools (mlx-lm, mlx-vlm, LM Studio, Ollama) load the backbone but give meaningless output, because only `clef_mlx.py` runs the decision head. A local `/v1/systemone` server (127.0.0.1, no auth, one request at a time on the GPU) is included.

## Key Insights
1. **Memory and latency on an M5 Max (text input).**
   | Variant | Download | Peak memory 1k / 4k / 16k tokens | Latency 1k / 16k tokens | Minimum Mac RAM |
   |---|---|---|---|---|
   | clef-flash-4bit (9B) | 6.2 GB | 7.0 / 7.2 / 8.6 GB | 0.31 s / 7.0 s | 16 GB |
   | clef-flash-8bit (9B) | 10.7 GB | 11.4 / 11.6 / 13.0 GB | 0.34 s / 7.7 s | 24 GB (16 GB for short prompts) |
   | clef-4bit (27B) | 16.3 GB | 17.1 / 17.5 / 19.6 GB | 1.4 s / 26.0 s | 32 GB |
   | clef-8bit (27B) | 29.8 GB | 30.5 / 30.8 / 33.0 GB | 1.5 s / 32.0 s | 48 GB |
   macOS lets the GPU use about 70–75 % of RAM by default, so the minimum RAM is above the peak. The card adds that long prompts on base M-series chips "will be several times slower".
2. **Quantisation cost, measured.** On a stratified 2,000-request sample of the Decision Index 0.2.1 kit (no truncation; 15 over-length requests count as wrong): 4-bit 54.65 vs MLX bf16 55.63 on the same rows (about **1 index point**), 96.4 % same top answer as bf16 over 15,915 answers, mean max |Δp| 0.040, median latency 311 ms vs 339 ms. Cloudflare's published full-suite score is 57.07; the card attributes most of the remaining gap to sampling noise and harness differences, present already in bf16. Agreement is lowest on low-chance, many-option tasks.
3. **Parity spot check** vs the official PyTorch bf16 implementation: 10/10 top answers on text (max |Δp| 0.029), 9/9 on images and video (0.119).
4. Inputs are truncated to 16,384 tokens by default, like the reference; `truncate=False` returns an error instead.

## Relevance to GroundOne
- **A 9B decision model fits the thesis machine.** A 16 GB Mac can hold the 4-bit Clef-flash (peak 7.0–8.6 GB), the same memory class as GroundOne-3B 8-bit with a co-resident generator ([[Apple Silicon and MLX]]). Locality is not limited to sub-4B models.
- **But not for grounding.** Clef-flash's own RAGTruth score (35.6 F1) is below the always-hallucinated baseline, so the model that fits is not the one that verifies groundedness; the 27B Clef (79.4) needs 32 GB in 4-bit.
- **Latency scale.** 0.31 s for a 1k-token request and 7.0 s at 16k on an M5 Max, i.e. prefill-dominated cost growing with context, the regime GroundOne's single-pass design targets ([[Prefill and Decode]], [[On-Device Inference]]).
- **Quantisation methodology** (same-row comparison against bf16, agreement and |Δp|) is a template for reporting GroundOne's 8-bit choice.

## Links
- Concepts: [[Apple Silicon and MLX]], [[On-Device Inference]], [[Decision-Model Landscape (Hugging Face, 2026)]]
- Related sources: [[Cloudflare 2026 - Clef model card]], [[MLX README (ml-explore)]], [[multimodalart 2026 - Jev Decision Index (Hugging Face Space)]]
