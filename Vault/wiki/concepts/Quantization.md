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
