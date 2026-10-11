---
type: source
author: "PremAI (Prem Labs) blog; individual author not named in the extraction"
date: 2026-03-17
venue: "PremAI company blog, practitioner guide with vendor marketing (published 2026-03-17; retrieved 2026-10-11)"
url: "https://blog.premai.io/llm-quantization-guide-gguf-vs-awq-vs-gptq-vs-bitsandbytes-compared-2026"
tags: [source, blog, vendor-marketing, quantization, gguf, awq, gptq, bitsandbytes, qlora, local-inference]
---
# PremAI 2026 – LLM Quantization Guide: GGUF vs AWQ vs GPTQ vs bitsandbytes

**Raw file**: `raw/local_inference/PremAI 2026 - LLM quantization guide, GGUF vs AWQ vs GPTQ vs bitsandbytes_ingested.md`

## Overview
A practitioner guide to **post-training weight quantisation** for LLMs. It explains the basic min–max affine scheme and compares four widely used methods/formats:
- **GGUF**: the llama.cpp container with block-wise k-quants and i-quants.
- **AWQ**: activation-aware, protects salient weights.
- **GPTQ**: layer-wise, second-order (Hessian) error compensation.
- **bitsandbytes**: on-the-fly LLM.int8() and NF4, enabling QLoRA.

It includes command-line recipes for producing GGUF and AWQ quants. The publisher sells a fine-tuning/serving platform (Prem Studio), and the section "When Quantization Isn't the Answer" is an advertisement. The explanations of the methods are standard and correct in outline. The **quality percentages are largely unsourced** (see insight 3).

## Key Insights
1. **Why quantise.** "A 70B parameter model in FP16 takes 140GB of memory." Going from 16-bit to 4-bit shrinks weights by 75%. The basic scheme is `scale = (max − min)/(2^bits − 1)`, `q = round((w − min)/scale)`, reconstruction `q·scale + min`. Quantisation introduces reconstruction error, and the methods differ in where they spend precision.
2. **GGUF bits per weight.** Q4_0 ≈ 4.34, Q4_K_M ≈ 4.58, Q5_K_M ≈ 5.69, **Q8_0 ≈ 8.5 bits per weight**. Each block of weights stores its own scale. "K" variants assign different bit depths by layer sensitivity. "I" variants use an importance matrix, needed only "for aggressive quants (Q3 and below, IQ2, IQ3)".
3. **Claimed quality retention vs FP16 ("based on benchmarks across multiple sources", with no citation).** Q8_0 ~99%, Q5_K_M ~97%, Q4_K_M ~92%, Q3_K_M ~85%, Q2_K ~70%. The page never defines "quality". **Treat these as unsourced rules of thumb.**
4. **Measured comparison (attributed to JarvisLabs, Qwen2.5-32B on an H200, vLLM).**
   - FP16: 461 tok/s, HumanEval Pass@1 56.1%, perplexity 6.56.
   - AWQ without the Marlin kernel: 67 tok/s, 51.8%.
   - AWQ + Marlin: **741 tok/s**, 51.8%, perplexity 6.84.
   - GPTQ + Marlin: 712 tok/s, 46.3%, perplexity 6.90.
   - bitsandbytes: 168 tok/s, 51.8%, perplexity 6.67.
   - GGUF in vLLM: ~93 tok/s; Q4_K_M perplexity 6.74 (FAQ).

   The guide's lesson: the kernel matters as much as the format, since AWQ without Marlin is slower than FP16.
5. **Internal inconsistencies.**
   - The head-to-head table gives quality retention GGUF 92%, AWQ 95%, GPTQ 90% and bitsandbytes 95%+. Yet the guide's own JarvisLabs numbers give AWQ 92% of baseline Pass@1 (51.8/56.1), and in the FAQ GGUF Q4_K_M has a *lower* perplexity (6.74) than AWQ (6.84).
   - The "Apple Silicon (M1/M2/M3)" list is dated for a 2026 article.
6. **Training claim is too strong.** bitsandbytes is presented as the "only option that supports training (QLoRA)", and "you can't directly fine-tune pre-quantized weights". That holds only among the four tools compared. MLX also trains LoRA adapters on top of quantised (4-/8-bit) base weights, which is how GroundOne is trained. QLoRA itself: 4-bit NF4 base plus trainable adapters; a 65B model fine-tunable on a single 48 GB GPU ([[Dettmers 2023 - QLoRA]]).
7. **Practical guidance.** For "quality-critical applications (medical, legal, financial)" the guide recommends starting with Q5_K_M or 8-bit and testing on the specific task. It notes that a perplexity increase of "5–10% is typical for Q4" and that "Quantized models can fail on inputs outside the calibration distribution".

## Relevance to GroundOne
- **Background for the quantisation paragraph in Ch. 2.** GroundOne uses MLX **8-bit affine (group-wise scale and bias) quantisation** of the Qwen2.5 base and trains LoRA adapters on top ([[Apple Silicon and MLX]], [[LoRA]], [[Qwen2.5]]). This is closest in spirit to GGUF Q8_0 (block-wise 8-bit), which the guide places at "~99%" of FP16. That figure is unsourced here and must not be used as evidence for GroundOne.
- **Classification is not generation quality.** The guide measures perplexity and code Pass@1. GroundOne reads three letter logits at markers ([[Letter-Token Readout]]), and its calibration ([[Calibration]]) depends on logit values. For that readout, quantisation error could shift probabilities without changing the argmax. The open item already noted in [[Apple Silicon and MLX]] still stands: compare the 8-bit checkpoints against a bf16 reference (agreement and max |Δp|) before claiming quantisation is harmless.
- **Memory arithmetic for the 16 GB budget.** 8 bits ≈ 1 byte per weight plus scales, so ≈ 0.5 GB (0.5B) and ≈ 3.3 GB (3B), consistent with the 70B ≈ 140 GB FP16 arithmetic here ([[On-Device Inference]]).
- **Locality.** Quantisation is what makes local inference feasible on consumer hardware. The vendor's pitch for "data sovereignty" via a managed VPC deployment is marketing and is not the fully local setting of GroundOne ([[Privacy and Data Sovereignty]], proposed).

## Links
- Concepts: [[Quantization]] (proposed), [[On-Device Inference]], [[Apple Silicon and MLX]], [[LoRA]], [[Calibration]], [[Privacy and Data Sovereignty]] (proposed)
- Related sources: [[Dettmers 2023 - QLoRA]], [[llama.cpp README (ggml-org)]], [[Presenc 2026 - State of the llama.cpp ecosystem]], [[MLX README (ml-explore)]]
