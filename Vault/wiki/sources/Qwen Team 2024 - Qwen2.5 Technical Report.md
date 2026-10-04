---
type: source
author: "Qwen Team (Alibaba)"
date: 2024
venue: "arXiv technical report 2412.15115 (v2, Jan 2025)"
url: "https://arxiv.org/abs/2412.15115"
tags: [source, paper, qwen, llm, model-card, licence]
---
# Qwen Team 2024 – Qwen2.5 Technical Report

**Raw file**: `raw/Qwen Team 2024 - Qwen2.5 Technical Report_ingested.pdf`

## Overview
The technical report for the Qwen2.5 family. **Open-weight dense models** come in 0.5B, 1.5B, 3B, 7B, 14B, 32B and 72B, each as a base and an instruct model, with quantized versions. **Proprietary MoE models** (Qwen2.5-Turbo and Qwen2.5-Plus) are served through an API (abstract, §1–2). Pretraining data grew from 7T (Qwen2) to **18T tokens**. Post-training uses more than 1M SFT examples plus two-stage RL: offline **DPO**, then online **GRPO** (§4).

## Key Insights
1. **Architecture (§2).** Decoder-only Transformer with **GQA**, SwiGLU, RoPE, **QKV bias** and RMSNorm (pre-norm).
2. **Table 1, p. 3: architecture and licence per size.**

| Size | Layers | Heads Q / KV | Tied emb. | Context / Generation | **Licence** |
|---|---|---|---|---|---|
| 0.5B | 24 | 14 / 2 | Yes | 32K / 8K | Apache 2.0 |
| 1.5B | 28 | 12 / 2 | Yes | 32K / 8K | Apache 2.0 |
| **3B** | 36 | 16 / 2 | Yes | 32K / 8K | **Qwen Research** |
| 7B | 28 | 28 / 4 | No | 128K / 8K | Apache 2.0 |
| 14B | 48 | 40 / 8 | No | 128K / 8K | Apache 2.0 |
| 32B | 64 | 40 / 8 | No | 128K / 8K | Apache 2.0 |
| 72B | 80 | 64 / 8 | No | 128K / 8K | Qwen |

3. **Tokenizer (§2).** Byte-level BPE with **151,643 regular tokens**. Control tokens grew from 3 to 22, including 2 for tool use. The vocabulary is **shared across all Qwen2.5 sizes**.
4. **Long context (§3.3).** Pretraining runs at 4,096 tokens and is then extended to 32,768 in the final stage, with RoPE base raised from 10,000 to 1,000,000 (ABF). YARN + Dual Chunk Attention give up to 131,072 tokens at inference for the larger models.
5. **Small-model results.** Base models (Table 5): Qwen2.5-0.5B MMLU 47.5, 3B 65.6; TruthfulQA 40.2 / 48.9. Instruct models (Tables 9–10): 3B-Instruct MMLU-redux 64.4, IFEval 58.2; 0.5B-Instruct MMLU-redux 24.1, IFEval 27.9. 3B is described as comparable to Qwen2-7B on several tasks (§5).
6. **Not in the report: the chat template.** The local `tokenizer_config.json` of `Qwen/Qwen2.5-3B-Instruct` (HF cache on the thesis machine) shows a **ChatML-style template** (`<|im_start|>role … <|im_end|>`). It inserts a default system prompt ("You are Qwen, created by Alibaba Cloud. You are a helpful assistant.") when none is given. EOS is `<|im_end|>`, pad is `<|endoftext|>`.

## Relevance to GroundOne
- **Licence warning: Qwen2.5-3B is *not* Apache 2.0.** Table 1 lists it under the "Qwen Research" licence. 0.5B (and 1.5B, 7B, 14B, 32B) are Apache 2.0. Before publishing fine-tuned 3B adapters or merged weights, or making any commercial claim, read the Qwen Research licence text on the model card. The report does not reproduce its terms. For a fully permissive story, 0.5B/1.5B/7B are the safe options.
- **GQA with only 2 KV heads** in 0.5B and 3B keeps the [[KV Cache]] very small. This favours the prefill-once, many-suffixes design. See [[Prefill and Decode]].
- **32K native context** is far more than GroundOne needs (context + answer of about 250–650 tokens in the preliminary measurements).
- **The shared tokenizer** means the answer-letter tokens (" A", " B", or "A"/"B" after a template) have the same IDs at every size. Still check the exact token IDs, because leading-space variants differ.
- **The default system prompt** gets prefilled too. Fix the template, including an explicit system prompt, so training and inference prefixes match token for token, and so the [[KV Cache]] prefix can be reused.
- Instruct models went through DPO and GRPO. Following [[Kadavath 2022 - Language Models (Mostly) Know What They Know|Kadavath §3.3]], expect overconfident raw logits and plan for temperature scaling. See [[Calibration]].

## Links
- Concepts: [[Qwen2.5]], [[LoRA]], [[KV Cache]], [[Prefill and Decode]], [[Calibration]]
- Related sources: [[Hu 2022 - LoRA]], [[Dettmers 2023 - QLoRA]]
- Thesis context: [[System One Models]], [[Groundedness Verification]]
