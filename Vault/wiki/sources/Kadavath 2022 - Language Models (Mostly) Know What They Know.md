---
type: source
author: "Saurav Kadavath, Tom Conerly, Amanda Askell, ..., Jared Kaplan (Anthropic)"
date: 2022
venue: "arXiv preprint 2207.05221 (Anthropic)"
url: "https://arxiv.org/abs/2207.05221"
tags: [source, paper, calibration, self-evaluation, p-true, rlhf, llm]
---
# Kadavath 2022 – Language Models (Mostly) Know What They Know

**Raw file**: `raw/Kadavath 2022 - Language Models (Mostly) Know What They Know_ingested.pdf`

## Overview
An Anthropic study of whether LLMs (800M, 3B, 12B and 52B pretrained models, plus RLHF policies) can judge how valid their own claims are. Three steps:
1. **Calibration on multiple-choice and True/False** questions when the format is right.
2. **Self-evaluation**: the model samples an answer, then is asked whether it is True or False. The probability on the "True" option is $P(\text{True})$.
3. **$P(\text{IK})$**: a value head trained to predict whether the model knows the answer, before any answer is proposed.

## Key Insights
1. **The lettered-option format gives calibrated probabilities (§2, p. 7; Figs. 4–6).** When the choices are shown explicitly and the model answers with a single letter token such as `(B)`, large models are well calibrated on BIG-Bench, MMLU, TruthfulQA, QuALITY and LogiQA. Calibration **improves with model size** and from 0-shot to few-shot. The authors say formatting is crucial because each option then maps to **a single token**, which avoids paraphrase ambiguity (§2).
2. **"None of the above" breaks it (§3.1, Fig. 7).** Replacing an option with "none of the above" hurts accuracy and calibration. Even the 52B model is biased against choosing it.
3. **True/False is well calibrated (§3.2, Fig. 8).** The format is "Proposed Answer: … Is the proposed answer: (A) True (B) False", and $P(\text{True})$ is read from the A/B option probabilities. The 52B model is very well calibrated except in the tails, where it is **overconfident**.
4. **RLHF policies look miscalibrated, and one temperature fixes much of it (§3.3, Fig. 9, p. 11).** A single $T=2.5$ for all evaluations "largely fixes calibration issues". The explanation: RL fine-tuning collapses predictions towards rewarded behaviour.
5. **Self-evaluation (§4).** Zero-shot $P(\text{True})$ on the model's own samples is poorly calibrated and tends to sit near 50%. Few-shot (20-shot) fixes most of this. More shots mainly improve **calibration** rather than AUROC. Showing five of the model's own samples before judging one ("brainstorming") improves short-answer tasks. Accuracy conditional on $P(\text{True})>0.5$ is much higher than base accuracy, and the gap **grows with size**: "verification is easier than generation."
6. **$P(\text{IK})$ (§5).** It is trained with a classification head on the last token. It is well calibrated in-distribution (TriviaQA) and generalises partly out of distribution, but is **underconfident OOD**. It **rises when relevant source material is put in context** (§5.3) and responds appropriately to correct and misleading hints (§5.4).
7. **Metrics used (Glossary, p. 5).**
   - ECE uses **10 equal-mass bins**, with only the top prediction for multiple choice. RMS calibration error is also reported.
   - AUROC measures discrimination and ignores calibration.
   - Brier score: chance level on a binary task is 0.25.

## Relevance to GroundOne
- GroundOne's readout is essentially Kadavath's **True/False P(True) format** applied to grounding: "Is this sentence supported by the context? (A) Yes (B) No", with the probability read from the A/B logits. This paper is the empirical basis for expecting that logits **restricted to the answer letters** carry calibrated signal, provided the options are explicit and single-token.
- Small models are the weak point. Calibration improves with size, and the smallest model here (800M) was the worst. GroundOne uses 0.5B and 3B, so **post-hoc temperature scaling and fine-tuning are essential**, not optional.
- If GroundOne starts from **Qwen2.5-Instruct** (post-trained with DPO and GRPO, see [[Qwen2.5]]), expect RLHF-style overconfidence. §3.3 suggests a single temperature recovers much of it. Comparing a base vs. an instruct starting checkpoint is a cheap ablation.
- §5.3 (P(IK) rises with source materials) supports the idea that the model's confidence depends on context. GroundOne turns this into an explicit, trained question about the retrieved context.
- Avoid an "unclear / none of the above" third option unless it is trained explicitly (§3.1).
- Report Brier score next to ECE, because Brier rewards discrimination as well as calibration. See [[Expected Calibration Error]].

## Links
- Concepts: [[Calibration]], [[Expected Calibration Error]], [[Selective Prediction]], [[Hallucination Detection]], [[LLM-as-a-Judge]]
- Related sources: [[Tian 2023 - Just Ask for Calibration]], [[Guo 2017 - On Calibration of Modern Neural Networks]]
- Thesis context: [[System One Models]], [[Groundedness Verification]], [[When System One Beats an LLM]]
