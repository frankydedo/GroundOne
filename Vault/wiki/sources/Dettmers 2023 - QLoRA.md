---
type: source
author: "Tim Dettmers, Artidoro Pagnoni, Ari Holtzman, Luke Zettlemoyer"
date: 2023
venue: "NeurIPS 2023 (arXiv 2305.14314)"
url: "https://arxiv.org/abs/2305.14314"
tags: [source, paper, qlora, lora, quantization, peft, memory]
---
# Dettmers 2023 – QLoRA: Efficient Finetuning of Quantized LLMs

**Raw file**: `raw/Dettmers 2023 - QLoRA_ingested.pdf`

## Overview
QLoRA backpropagates through a **frozen 4-bit quantized base model** into LoRA adapters. This makes it possible to fine-tune a **65B model on a single 48 GB GPU**, compared with more than 780 GB for 16-bit full fine-tuning, while matching 16-bit performance (abstract, §1). The resulting Guanaco models reach 99.3% of ChatGPT on the Vicuna benchmark after 24 h on one GPU. The paper also reports more than 1,000 fine-tuning runs.

## Key Insights
1. **Three techniques (§3).**
   - **4-bit NormalFloat (NF4)**: a quantile-based data type that is information-theoretically optimal for zero-centred normal weights, with an exact zero.
   - **Double Quantization**: the quantization constants are themselves quantized (FP8, block size 256). This saves about **0.37 bits per parameter** (0.5 → 0.127), roughly 3 GB on a 65B model.
   - **Paged Optimizers**: NVIDIA unified memory pages optimizer states to CPU RAM to absorb memory spikes during gradient checkpointing.

   Storage is 4-bit, compute is BF16: weights are dequantized on the fly for each matmul.
2. **Where the training memory goes (§2, "Memory Requirement").** For LLaMA-7B at batch size 1, the LoRA parameters take 26 MB, but the **LoRA input gradients take 567 MB**. With **gradient checkpointing** these drop to about 18 MB per sequence. The 4-bit base model takes 5,048 MB. The conclusions: *gradient checkpointing is important*, while cutting the number of LoRA parameters saves almost nothing, so one can afford more adapters.
3. **Adapter placement matters most (§4, Fig. 2; Appendix A).** With the default LoRA on query/value only, they **could not match** full fine-tuning on large models. "LoRA on all linear transformer block layers are required to match full finetuning performance." With adapters on all layers, **LoRA r is unrelated to final performance** (Appendix A, Fig. 4, r ∈ {8…256}). LoRA dropout 0.05 helped 7B/13B models but not 33B/65B models.
4. **NF4 beats FP4 and Int4 (§4, Fig. 3, Table 2).** NF4 + DQ matches BF16 on zero-shot benchmarks. **4-bit QLoRA matches 16-bit LoRA and full fine-tuning** on GLUE and Super-NaturalInstructions (Table 3), e.g. T5-3B: BF16 54.3 vs. QLoRA NF4+DQ 55.3.
5. Side findings: data quality matters more than dataset size for chatbots. GPT-4-as-judge mostly agrees with human rankings, but only moderately at system level (Kendall τ 0.43). Current chatbot benchmarks are unreliable (§5–6).

## Relevance to GroundOne
- On a **16 GB unified-memory M4**, the QLoRA lessons carry over even though MLX uses its own affine group quantization rather than NF4:
  1. **Quantize the frozen base** (4- or 8-bit) to leave room for activations.
  2. **Turn on gradient checkpointing.** mlx-lm has `--grad-checkpoint`, which is off by default in mlx-lm 0.31.3.
  3. **Spend the budget on coverage, not rank.** Put adapters on all linear layers (and ideally on more blocks) before raising r.
- The thesis's earlier routing configs adapted only the last 8 blocks at rank 8. QLoRA's §4 result suggests an **ablation over `num_layers` (8 → all 24/36) and target modules**, which may matter more than any rank sweep. See [[LoRA]].
- Activation memory grows with sequence length. GroundOne's context + answer prefixes (about 250–650 tokens in the preliminary measurements) are short enough for 3B training on 16 GB with checkpointing and batch size 1 plus gradient accumulation. This is an expectation still to be confirmed, not a measurement.
- The GPT-4-judge-vs-human agreement result is useful background for [[LLM-as-a-Judge]].

## Links
- Concepts: [[LoRA]], [[Qwen2.5]], [[LLM-as-a-Judge]]
- Related sources: [[Hu 2022 - LoRA]], [[Qwen Team 2024 - Qwen2.5 Technical Report]]
- Thesis context: [[System One Models]], [[Groundedness Verification]]
