---
type: source
author: "Edward Hu, Yelong Shen, Phillip Wallis, Zeyuan Allen-Zhu, Yuanzhi Li, Shean Wang, Lu Wang, Weizhu Chen (Microsoft)"
date: 2022
venue: "ICLR 2022 (arXiv 2106.09685)"
url: "https://arxiv.org/abs/2106.09685"
tags: [source, paper, lora, peft, fine-tuning]
---
# Hu 2022 – LoRA: Low-Rank Adaptation of Large Language Models

**Raw file**: `raw/Hu 2022 - LoRA_ingested.pdf`

## Overview
LoRA freezes the pretrained weights $W_0$ and learns a **low-rank update** $\Delta W=BA$ for chosen weight matrices. Here $B\in\mathbb R^{d\times r}$, $A\in\mathbb R^{r\times k}$ and $r\ll\min(d,k)$. The forward pass is $h=W_0x+BAx$ (Eq. 3, §4.1). On GPT-3 175B, LoRA cuts trainable parameters by about **10,000×** and GPU memory by about **3×** compared with full Adam fine-tuning. Quality matches or beats full fine-tuning on RoBERTa, DeBERTa, GPT-2 and GPT-3 (abstract).

## Key Insights
1. **Initialisation and scaling (§4.1).** $A$ starts Gaussian and $B$ starts at zero, so $\Delta W=0$ at step 0. The update is scaled by $\alpha/r$. "Tuning α is roughly the same as tuning the learning rate", so they set α to the first r tried and do not tune it.
2. **No extra inference latency (§4.1).** At deployment, $W=W_0+BA$ can be **merged**, so the network has the same shape and latency as the base model. Swapping tasks means subtracting $BA$ and adding $B'A'$. The downside (§4.2): with merged weights, one batch cannot easily mix inputs that use different adapters.
3. **Memory (§4.2).** With Adam, VRAM drops by up to 2/3 because frozen weights need no optimizer state. GPT-3 175B training VRAM goes from 1.2 TB to 350 GB. A checkpoint with r = 4 on $W_q,W_v$ shrinks from 350 GB to **35 MB**. Training is about 25% faster.
4. **Which matrices to adapt (§7.1, Table 5).** With a fixed budget of 18M parameters on GPT-3, spreading rank over **$W_q$ and $W_v$** (r = 4 each) beats putting it all into one matrix at r = 8. Adapting all four of $W_q,W_k,W_v,W_o$ at r = 2 is about as good (MultiNLI 91.7). The paper only adapts attention weights and leaves MLP adaptation to future work (§4.2).
5. **Rank (§7.2, Table 6).** Very small ranks are enough. With $\{W_q,W_v\}$, r = 1 already gives 73.4 on WikiSQL and 91.3 on MultiNLI, about the same as r = 64. Subspace analysis suggests $\Delta W$ has a very low "intrinsic rank". Caveat (footnote 6): this will not hold for every task, e.g. a different language from pretraining. On GPT-2 Medium the best rank was higher (r = 16 for validation loss, Appendix H.2).

## Relevance to GroundOne
- GroundOne fine-tunes Qwen2.5 0.5B/3B with LoRA on MLX. Because of the **merge property**, the trained verifier has exactly the base model's inference cost. The [[Prefill and Decode]] latency numbers measured on the base model therefore also apply to the fine-tuned model if adapters are fused (e.g. with `mlx_lm.fuse`). Unfused adapters add a small per-layer matmul.
- MultiNLI is one of LoRA's own benchmarks, and it is close to GroundOne's entailment-style task. Even tiny ranks reach full fine-tuning accuracy there, which suggests rank is **not** the main lever for a binary entailment head. Which layers and modules are adapted matters more. [[Dettmers 2023 - QLoRA|QLoRA]] makes the same point even more strongly.
- Hu's paper only adapts attention projections. Modern tooling, including the mlx-lm default, adapts all linear layers in the last N blocks. See [[LoRA]] for the 16 GB training checklist.
- Being able to swap adapters cheaply suggests a design: **one base model with several System One adapters** (grounding verifier, router, etc.) sharing weights in memory.

## Links
- Concepts: [[LoRA]], [[Qwen2.5]], [[Prefill and Decode]]
- Related sources: [[Dettmers 2023 - QLoRA]], [[Qwen Team 2024 - Qwen2.5 Technical Report]]
- Thesis context: [[System One Models]], [[Groundedness Verification]]
