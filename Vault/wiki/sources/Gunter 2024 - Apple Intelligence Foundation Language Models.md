---
type: source
author: "Apple Foundation Models team (Tom Gunter et al.; contributors listed alphabetically per section)"
date: 2024
venue: "Technical report, arXiv 2407.21075 (2024; the ingested PDF is arXiv v2)"
url: "https://arxiv.org/abs/2407.21075"
tags: [source, paper, technical-report, on-device, apple, lora, quantization, adapters]
---
# Gunter 2024 – Apple Intelligence Foundation Language Models

**Raw file**: `raw/Gunter 2024 - Apple Intelligence Foundation Language Models_ingested.pdf`

## Overview
Apple's technical report on the language models behind Apple Intelligence (iOS 18, iPadOS 18, macOS Sequoia): **AFM-on-device**, a dense decoder of about **3B parameters** that runs locally on iPhone, iPad and Mac, and **AFM-server**, a larger model served through Private Cloud Compute (§1). The report covers architecture, data, pre- and post-training, inference optimisation, evaluation and Responsible AI. Its central engineering idea is **one quantised base model specialised at runtime by swappable LoRA adapters** (§5).

## Key Insights
1. **Architecture (§2, Table 1).** AFM-on-device: model dimension 3,072, 26 layers, 24 query heads and **8 KV heads (GQA)** "to reduce the KV-cache memory footprint", head dimension 128, shared input/output embedding, RMSNorm, query/key norm, SwiGLU, RoPE base 500k. 2.58B non-embedding plus 0.15B embedding parameters; vocabulary 49k.
2. **Training (§3.2.1).** AFM-on-device is initialised from a pruned 6.4B model and distilled from it (target = 0.9 × teacher top-1 + 0.1 × true label) over 6.3T tokens. Pruning adds 0–2% on benchmarks; distillation adds about 5% on MMLU and 3% on GSM8K.
3. **Runtime-swappable adapters (§5.1).** LoRA adapters on all linear projections of attention and FFN, stored in 16 bits; a rank-16 adapter for the 3B model takes "10s of megabytes". Adapters are "dynamically loaded, temporarily cached in memory, and swapped", so one base model serves dozens of features.
4. **Quantisation with accuracy recovery (§5.2).** The base model is compressed to **under 4 bits per weight on average** (mixed 2-bit/4-bit, about 3.5 bpw achievable, **3.7 bpw in production**). Palettisation on the Apple Neural Engine: each group of 16 rows/columns shares a 16-value lookup table (4-bit, K-means); embeddings are 8-bit per-channel. **Accuracy-recovery LoRA adapters** (rank 16 found optimal; ranks 8/16/32 offered) are trained on about 10B tokens (≈0.15% of base training) to restore quality; feature adapters are initialised from them. The authors compare this to QLoRA, but the aim is switching adapters at inference, not cheap fine-tuning.
5. **Feature specialisation (§5.3).** Summarisation of emails, messages and notifications uses a LoRA adapter on the quantised on-device model, trained on synthetic summaries from AFM-server. Human graders score summaries on composition, comprehensiveness, **groundedness**, instruction following and harmfulness (§6.3).
6. **Quality (§6).** AFM-on-device scores 61.4 on HELM MMLU 5-shot (Table 2). In human side-by-side evaluation it obtains a 47.7% win rate against Phi-3-mini despite being 25% smaller, and outperforms Gemma-7B and Mistral-7B (§6.2.1, Fig. 3).
7. **Privacy framing (§1).** "We protect our users' privacy with powerful on-device processing and groundbreaking infrastructure like Private Cloud Compute"; no private user data is used in training.

## Relevance to GroundOne
- **A platform vendor validates the GroundOne recipe.** Apple ships a ~3B on-device model, quantised, specialised per task with rank-16 LoRA adapters on all linear layers. GroundOne uses the same pattern at the same scale: Qwen2.5 3B (and 0.5B), 8-bit MLX weights, LoRA r16 on all linear layers, a frozen base, one task per adapter. The thesis can cite this as evidence that "small base + task adapter" is the industrial design for local language features. See [[On-Device Inference]], [[LoRA]].
- **Groundedness is a product concern on-device.** Apple grades its on-device summaries for groundedness by human raters. A local verifier like GroundOne is the automatic, per-sentence version of that check, and it could run next to the generator on the same device ([[Groundedness Verification]]).
- **Differences to state honestly.** AFM-on-device runs on the Neural Engine with ~3.7 bpw palettisation; GroundOne runs on the M4 GPU through MLX with 8-bit affine quantisation. Apple's adapters generate text; GroundOne's adapter is trained as a three-way classifier read from letter logits, generating nothing ([[System One Models]]).
- **Hybrid local/remote.** Private Cloud Compute is Apple's answer to the capability gap of small models; the thesis's locality pillar takes the stricter position that the whole pipeline stays on the device ([[On-Device Inference]]).

## Links
- Concepts: [[On-Device Inference]], [[Apple Silicon and MLX]], [[LoRA]], [[KV Cache]], [[Groundedness Verification]], [[System One Models]]
- Related sources: [[Alizadeh 2024 - LLM in a flash]], [[Hu 2022 - LoRA]], [[Dettmers 2023 - QLoRA]], [[MLX README (ml-explore)]], [[Qwen Team 2024 - Qwen2.5 Technical Report]]
