---
type: concept
tags: [concept, quantization, gguf, mlx, awq, gptq, qlora, memory, on-device]
---
# Quantization

Storing model weights (and sometimes activations or the KV cache) with fewer bits than the 16-bit training format. On local hardware it serves two purposes at once: the model **fits** in memory, and **decode** gets faster, because decode time is dominated by reading the weights ([[Prefill and Decode]]). Weight-only quantisation is preferred on device for exactly this reason ([[Qu 2024 - Mobile Edge Intelligence for LLMs, A Contemporary Survey (arXiv 2407.18921)|Qu 2024]] §IV-A1).

## Memory arithmetic
- A 7B model takes 28 / 14 / 7 / 3.5 GB at FP32 / FP16 / INT8 / INT4 ([[Das 2026 - Large Models for Small Devices, Edge AI Deployment (arXiv 2608.15693)|Das 2026]]). Epoch's budget for a consumer GPU: weights at ~0.54 bytes/param (4-bit) + KV cache (~6.6 GiB at 8k context, INT8) + ~2 GiB overhead ([[Epoch AI 2025 - Frontier AI performance becomes accessible on consumer hardware within a year]]).
- Vendor claims of "200B models" on 128 GB machines assume about 4 bits per weight ([[NVIDIA - DGX Spark hardware overview]]).
- GroundOne: Qwen2.5 in MLX 8-bit, about 0.5 GB (0.5B) and 3.3 GB (3B) of weights ([[Apple Silicon and MLX]]).

## Formats and methods
| Format / method | Where | Notes |
| --- | --- | --- |
| GGUF k-quants (Q2_K … Q8_0; Q8_0 ≈ 8.5 bits/weight) | llama.cpp, Ollama, LM Studio | single file with tokenizer and chat template ([[Presenc 2026 - State of the llama.cpp ecosystem]], [[PremAI 2026 - LLM quantization guide, GGUF vs AWQ vs GPTQ vs bitsandbytes|PremAI 2026]]) |
| MLX affine 4/8-bit | MLX on Apple silicon | GroundOne's format; supports LoRA training on quantised weights |
| AWQ, GPTQ | GPU serving (vLLM) | the kernel matters as much as the format: AWQ without the Marlin kernel 67 tok/s, with it 741 (Qwen2.5-32B, H200; PremAI citing JarvisLabs) |
| bitsandbytes NF4 / QLoRA | PyTorch/CUDA | 4-bit training ([[Dettmers 2023 - QLoRA]]) |

## Quality does not fall monotonically with bits
- Qwen3.5 0.8B at Q5_K_M reaches 93.85 SQuAD F1, and for two of the tested models Q4_K_M scores best (Das 2026, ~100 items per evaluation, so noisy).
- Pruning interacts badly with k-quants: removing 1 % of MLP channels hurts quality and pruned GGUF files grow by 21–49 % because block alignment breaks (Das 2026).
- PremAI's "% of FP16 quality" table is unsourced and contradicts its own perplexity figures; its claim that only bitsandbytes supports training is wrong (MLX LoRA on 8-bit weights is a counterexample).

## Relevance to GroundOne
- 8-bit is a conservative choice for a **logit readout**: calibration and thresholds depend on the exact probabilities, not just on the argmax, so aggressive quantisation is riskier for a System One than for chat. Still open: an 8-bit vs bf16 check (agreement and max |Δp|) on the dev set.
- Quantisation helps decode much more than prefill; GroundOne's single prefill is compute-bound, so its gain from fewer bits is smaller than a generative judge's. This narrows, but does not remove, the speed advantage measured in [[GroundOne Results]].

## Links
- Concepts: [[Prefill and Decode]], [[Apple Silicon and MLX]], [[On-Device Inference]], [[Local Inference Hardware]], [[Small Language Models]], [[LoRA]], [[KV Cache]]

## Classic methods (ingest 2026-10-11, second batch)
- **LLM.int8()** (W8A8, outlier dimensions ≥ 6 kept in fp16): no loss up to 175B; saves memory but runs at 0.51× fp16 at hidden size 2048, faster only at 13B+; outliers control much of the attention mass ([[Dettmers 2022 - LLM.int8(), 8-bit Matrix Multiplication for Transformers at Scale (arXiv 2208.07339)|Dettmers 2022]]).
- **GPTQ** (3–4-bit, second-order, post-training): OPT-175B 4-bit 8.34 → 8.37 ppl; small models lose more (OPT-1.3B 14.63 → 15.47); 3.24× (A100) / 4.53× (A6000) faster decode from bandwidth, no compute reduction ([[Frantar 2023 - GPTQ, Accurate Post-Training Quantization for Generative Pre-trained Transformers (arXiv 2210.17323)|Frantar 2023]]).
- **AWQ** (4-bit, protect ~1 % salient channels by activation-aware scaling): Llama-2-7B INT4-g128 5.60 vs GPTQ 5.69 vs fp16 5.47; robust to calibration domain ([[Lin 2024 - AWQ, Activation-aware Weight Quantization for LLM Compression and Acceleration (arXiv 2306.00978)|Lin 2024]]).
- **Small models at low bits**: ≤ 3B models "unusable" at 3 bits on phones ([[Laskaridis 2024 - MELTing point, Mobile Evaluation of Language Transformers (arXiv 2403.12844)|MELT]]); MobileLLM W8A8 costs < 0.5 points ([[Liu 2024 - MobileLLM, Optimizing Sub-billion Parameter Language Models for On-Device Use Cases (arXiv 2402.14905)|Liu 2024]]). Phone NPUs need per-tensor INT8; QNN per-channel INT4 drops Qwen2-7B GSM8K from 77.4 to 22.3 (Xue 2024).
- **Thesis position**: weight-only 8-bit (MLX, group 64) is the conservative choice for a calibrated logit readout; it speeds up decode-heavy baselines more than GroundOne's prefill. The adapter is trained on the already-quantised base and served on the same base (no train/serve mismatch).
