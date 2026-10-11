---
type: concept
tags: [model, qwen, llm, licence, tokenizer, groundone]
---
# Qwen2.5

Alibaba's Qwen2.5 family is the backbone of [[GroundOne]] (0.5B and 3B, LoRA-fine-tuned on MLX) and of the demo's RAG generator (3B). Main source: [[Qwen Team 2024 - Qwen2.5 Technical Report]].

## Family
- **Open weights**: dense 0.5B, 1.5B, 3B, 7B, 14B, 32B, 72B, each as **base and instruct**, plus official quantized instruct versions. Distributed on HF, ModelScope and Kaggle.
- **API only**: Qwen2.5-Turbo and Qwen2.5-Plus (MoE). Turbo supports 1M-token context.
- Pretraining: **18T tokens** (Qwen2: 7T). Post-training: more than 1M SFT examples, then **offline DPO + online GRPO** (§4).
- Derived models: Qwen2.5-Math, Qwen2.5-Coder, QwQ.

## Architecture and licence per size (report Table 1, p. 3)
| Size | Layers | Q / KV heads | Tied emb. | Context / max generation | Licence |
|---|---|---|---|---|---|
| 0.5B | 24 | 14 / 2 | yes | 32K / 8K | **Apache 2.0** |
| 1.5B | 28 | 12 / 2 | yes | 32K / 8K | Apache 2.0 |
| 3B | 36 | 16 / 2 | yes | 32K / 8K | **Qwen Research** |
| 7B | 28 | 28 / 4 | no | 128K / 8K | Apache 2.0 |
| 14B | 48 | 40 / 8 | no | 128K / 8K | Apache 2.0 |
| 32B | 64 | 40 / 8 | no | 128K / 8K | Apache 2.0 |
| 72B | 80 | 64 / 8 | no | 128K / 8K | Qwen |

Common components: GQA, SwiGLU, RoPE (base 1,000,000 after long-context training), **QKV bias**, RMSNorm pre-norm (§2, §3.3).

From the local HF `config.json` files (thesis machine): **0.5B** hidden 896, head dim 64, FFN 4864. **3B** hidden 2048, head dim 128, FFN 11008. Both have vocab size 151,936, `max_position_embeddings` 32,768, bf16.

### Licence note (3B)
**Qwen2.5-3B is the only small size *not* under Apache 2.0.** The report lists it under the **"Qwen Research"** licence, and 72B under the "Qwen" licence. The report does not reproduce the licence terms. Read the `LICENSE` on the official HF model card before redistributing fine-tuned 3B weights or adapters, or before any commercial use. For the thesis (research use) this is presumably fine, but it should be **stated explicitly in the thesis**. An Apache-2.0 alternative at a similar scale is **1.5B**.

## Tokenizer
- Byte-level BPE, **151,643 regular tokens**, 22 control tokens (3 in earlier Qwen). Two of the control tokens are for tools. One vocabulary is shared across all sizes (§2).
- Implication for GroundOne: the answer-letter token IDs are identical for 0.5B and 3B. Still check them exactly ("A" vs " A" are different tokens) and make the training and inference templates end in the same position before the letter.

## Chat template (not in the report; from local `tokenizer_config.json` of `Qwen/Qwen2.5-3B-Instruct`)
- ChatML-style: `<|im_start|>system\n…<|im_end|>\n<|im_start|>user\n…<|im_end|>\n<|im_start|>assistant\n`.
- If no system message is given, it **inserts a default system prompt**: "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."
- A tool-calling branch adds a `# Tools` block with `<tools>` / `<tool_call>` XML tags.
- EOS `<|im_end|>`, pad `<|endoftext|>`.
- For GroundOne: always pass an explicit system prompt, or use the base model with a raw prompt, so the prefix is deterministic and shareable in the [[KV Cache]].

## Small-model capability (report §5)
- Base (Table 5): MMLU 0.5B 47.5 / 1.5B 60.9 / 3B 65.6; TruthfulQA 40.2 / 46.6 / 48.9; GSM8K 41.6 / 68.5 / 79.1.
- Instruct (Tables 9–10): 3B MMLU-redux 64.4, IFEval 58.2; 0.5B MMLU-redux 24.1, IFEval 27.9.
- The 0.5B instruct model is weak at following instructions zero-shot, which is one reason a **fine-tuned logit readout** may beat prompting it as a judge.

## Practical notes for GroundOne
- **GQA with 2 KV heads** (0.5B and 3B) makes the [[KV Cache]] tiny: about 12 KiB/token (0.5B) and about 36 KiB/token (3B) in FP16. Prefilling a shared context once is cheap to keep in memory.
- **32K native context** is far more than needed for context + answer.
- **Instruct checkpoints are preference-tuned (DPO/GRPO)**, so expect overconfident raw logits ([[Calibration]]; [[Kadavath 2022 - Language Models (Mostly) Know What They Know|Kadavath]] §3.3). Compare base vs. instruct as the starting point for LoRA.
- Preliminary on-device latency (thesis's own measurement, MLX 8-bit, M4 16 GB): see [[Prefill and Decode]].

## Links
- [[LoRA]], [[KV Cache]], [[Prefill and Decode]], [[Calibration]], [[GroundOne]], [[System One Models]], [[Groundedness Verification]]
- Sources: [[Qwen Team 2024 - Qwen2.5 Technical Report]], [[Hu 2022 - LoRA]], [[Dettmers 2023 - QLoRA]]

## Observed in GroundOne (2026-10-10)
After the marker " Verdict:", the fine-tuned model's most likely next token is the **spaced** letter (" A", " B", " C"), not the unspaced letters GroundOne reads; the three readout letters hold only about 4–5 % of the probability mass. Training with a loss restricted to the readout letters shapes their relative logits, not their absolute mass, so the readout behaves as a three-way classifier ([[Letter-Token Readout]]). Generating the token instead (control B2) loses 0.25 (0.5B) / 0.07 (3B) three-way accuracy.

## Licence and terminology (ingest 2026-10-11)
- Under the OSI definition Qwen2.5 is **open-weight, not open source**: weights are released, training code and data information are not ([[OSI 2024 - The Open Source AI Definition 1.0]], [[Open-Weight Models]]). The 0.5B is Apache 2.0; the 3B is under the Qwen Research licence. The thesis should use "open-weight" and state both licences.
- Lu 2024 measures Qwen2.5-3B-Instruct at 91.71 % on Needle-in-a-Haystack and notes that small models are trained far past Chinchilla ([[Lu 2024 - Small Language Models, Survey, Measurements, and Insights (arXiv 2409.15790)|Lu 2024]]; see [[Small Language Models]]).
- Under the EU AI Act, LoRA fine-tuning of Qwen2.5 is far below the one-third-of-training-compute threshold that would make the fine-tuner a model provider (own 6ND estimate ≈ 3×10^23 FLOPs for the 3B; [[WilmerHale 2025 - Commission guidelines for providers of general-purpose AI models]]).
