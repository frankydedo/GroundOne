---
type: source
author: "Tony Z. Zhao, Eric Wallace, Shi Feng, Dan Klein, Sameer Singh"
date: 2021
venue: "ICML 2021 (arXiv 2102.09690)"
url: "https://arxiv.org/abs/2102.09690"
tags: [source, paper, calibration, contextual-calibration, few-shot, label-bias, gpt-3]
---
# Zhao 2021 – Calibrate Before Use: Improving Few-Shot Performance of Language Models

**Raw file**: `raw/Zhao 2021 - Calibrate Before Use_ingested.pdf`

## Overview
GPT-3's few-shot accuracy swings from near chance to near state of the art depending on the prompt format, the choice of training examples and even their order (§3, Figs. 1–3). The paper traces this instability to a **bias of the LM towards particular answers**, which mostly shifts the output distribution (§4). It proposes **contextual calibration**: estimate that bias by feeding a *content-free* input such as "N/A" with the same prompt, then fit an affine correction that makes the prediction for that input uniform (§5). No labelled data is needed. Across text classification, fact retrieval (LAMA) and information extraction, it raises GPT-3 and GPT-2 accuracy by up to 30.0 points absolute and lowers variance across prompts (Table 1, Fig. 6).

## Key Insights
1. **Three biases (§4).**
   - *Majority label bias*: the model favours answers that are frequent among the in-context examples (Fig. 4).
   - *Recency bias*: it favours answers near the end of the prompt. This can outweigh the majority bias.
   - *Common token bias*: it favours tokens frequent in pre-training, e.g. "America" in LAMA or common class names in DBPedia.
   Their net effect is usually a **shift** of the output distribution. Fig. 5: on SST-2, a threshold of 0.68 instead of 0.5 would give 94 % accuracy from the same scores.
2. **Method (§5).** New probabilities $\hat q = \mathrm{softmax}(W\hat p + b)$, with $W$ restricted to a diagonal ("vector scaling", after Guo 2017). Contextual calibration sets $W = \mathrm{diag}(\hat p_\text{cf})^{-1}$ and $b = 0$, where $\hat p_\text{cf}$ is the label-name probability (renormalised over the labels) for the content-free input. The paper averages three such inputs: "N/A", "[MASK]" and the empty string. For generation only the first token is calibrated (footnotes 6–7).
3. **Not statistical calibration.** Footnote 4 says explicitly that the goal is to remove a bias in the decision, like zeroing a scale, and is "distinct from statistical calibration" of confidence (Brier, Guo). The method is judged by **accuracy**, not ECE.
4. **Results (§5.1–5.2).**
   - It improves mean and worst-case accuracy; GPT-3 2.7B sometimes beats uncalibrated 175B by up to 19.3 points.
   - It removes the 0-shot → 1-shot drop caused by majority label bias, and reduces variance across 15 prompt formats (Fig. 7).
   - It comes close to an "oracle" diagonal $W$ fitted on validation data (Fig. 8).
   - It mitigates, but does not eliminate, prompt engineering.

## Relevance to GroundOne
- **GroundOne's per-class bias is the supervised version of contextual calibration.** The calibration map is $\mathrm{softmax}(z/T + b)$ with $b_\text{supported} = 0$ and one bias per remaining letter, fitted by NLL on dev (`calibration.py`, D23/D24). Dividing probabilities by $\hat p_\text{cf}$ (Zhao) is the same as adding $-\log \hat p_\text{cf}$ to the logits. So both methods move the decision boundary with a per-class offset. GroundOne fits the offset with labels on dev; Zhao infers it with no labels from a content-free probe.
- Zhao's footnote 4 matches the split in D24: **decisions** use the raw (balanced) output, while **calibrated probabilities** are used for ECE, risk–coverage and the served threshold τ on P(supported). The bias corrects a boundary shift; the temperature corrects confidence. In early runs the probabilities were squeezed and shifted per task, which temperature alone could not fix.
- Zhao's Fig. 5 is the argument behind the served threshold. A well-ranked but shifted score needs a moved threshold, not a new model. GroundOne fits τ ≈ 0.90–0.94 on calibrated P(supported) on dev (D27).
- **Possible baseline idea (not run):** contextual calibration for the *untrained* B1 readout, using an empty or "N/A" sentence before the " Verdict:" marker. It would show how much of B1's near-chance performance (T1 three-way 0.372 / 0.437) is a removable letter prior rather than a lack of judgement. Cheap and inference-only.
- The common-token bias also explains why the full-vocabulary token in B2 skews towards " A".

## Links
- Concepts: [[Calibration]], [[Letter-Token Readout]], [[Expected Calibration Error]], [[Selective Prediction]]
- Related sources: [[Guo 2017 - On Calibration of Modern Neural Networks]] (vector/matrix scaling), [[Zheng 2024 - LLMs Are Not Robust Multiple Choice Selectors]] (PriDe, label-free prior removal), [[Kadavath 2022 - Language Models (Mostly) Know What They Know]]
- Thesis context: [[GroundOne]], [[System One Models]]
