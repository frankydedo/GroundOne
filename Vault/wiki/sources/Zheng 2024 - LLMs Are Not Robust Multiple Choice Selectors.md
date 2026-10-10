---
type: source
author: "Chujie Zheng, Hao Zhou, Fandong Meng, Jie Zhou, Minlie Huang"
date: 2024
venue: "ICLR 2024 (arXiv 2309.03882)"
url: "https://arxiv.org/abs/2309.03882"
tags: [source, paper, mcq, selection-bias, token-bias, debiasing, logit-readout, llm]
---
# Zheng 2024 – Large Language Models Are Not Robust Multiple Choice Selectors

**Raw file**: `raw/Zheng 2024 - LLMs Are Not Robust Multiple Choice Selectors_ingested.pdf`

## Overview
The paper shows that LLMs answering multiple-choice questions (MCQs) have a **selection bias**: they prefer certain option IDs ("A", "C") regardless of content. The study covers 20 decoder-only LLMs (LLaMA, Llama-2(-chat), Vicuna, Falcon, gpt-3.5-turbo) on MMLU, ARC-Challenge and CommonsenseQA, 0-shot and 5-shot (§2.1). For open models the prediction is the argmax of the option-ID token probabilities, exactly the letter readout used by MCQ harnesses. The main cause is **token bias**, an a-priori probability mass on specific ID tokens, rather than position bias (§2.4). The proposed fix, **PriDe**, estimates that prior without labels and divides it out at inference time (§3).

## Key Insights
1. **Moving the gold answer changes accuracy a lot.** In 0-shot MMLU, putting every gold answer at position A lifts llama-30B from 53.1 to 68.2 (+15.2); putting it at D drops gpt-3.5-turbo from 67.2 to 60.9 (Table 1). On 1,000 balanced MMLU items llama-30B picks A/B/C/D 34.6 / 27.3 / 22.3 / 15.8 % of the time (χ² p ≪ 10⁻⁴; §1).
2. **Metric.** Selection bias is measured as the standard deviation of per-option recalls (**RStd**), which is robust to label imbalance and tracks sensitivity to answer moving (§2.2, Fig. 2).
3. **Token bias, not position bias, is the main cause (§2.4).** Removing the IDs and scoring option contents directly cuts RStd sharply (gpt-3.5-turbo MMLU 5.5 → 1.0), while shuffling the ID order barely changes it (5.1). Other ID symbols (a/b/c/d, 1/2/3/4, (A)…) do not help (Table 2). The remaining position bias is irregular across models and tasks.
4. **Cheap fixes do not work.** Removing IDs lowers accuracy in most cases because cloze-style scoring is a worse MCQ prompt (§2.5). An explicit "options are shuffled" instruction and chain-of-thought leave the bias in place (Table 2, §2.6). The bias is fairly stable within a model across domains (§2.3), and in-context examples can reduce it but also change its direction (Fig. 3).
5. **PriDe (§3).** The observed distribution is modelled as prior over IDs × debiased distribution over contents (Eq. 2–3). Averaging log-probabilities over cyclic permutations of the contents on a small share of test items (e.g. 5 %) estimates the prior (Eq. 7). The remaining items are debiased by dividing out the global prior (Eq. 8, Algorithm 1). It beats full and cyclic permutation at equal cost (Fig. 4), transfers across domains (Fig. 5), and changes mostly low-confidence predictions, usually to the original top-2 (§4.3).

## Relevance to GroundOne
- GroundOne's verdict is a **letter readout** (A = supported, B = contradicted, C = not mentioned), so it inherits the token-bias question. Unlike an MCQ benchmark, the letter-to-class mapping is **fixed**: "A" always means supported. Any prior mass on "A" is therefore confounded with a prior on the class "supported", and cannot show up as sensitivity to option order.
- For the **trained** model, two mechanisms absorb such a prior: the class-weighted loss over the three letters, and the dev-fitted **per-class bias** of the calibration map, $\mathrm{softmax}(z/T + b)$. The bias plays the role of PriDe's $\log P_\text{prior}$, but it is fitted with labels on dev instead of being estimated label-free. See [[Calibration]].
- For the **untrained or generative** systems, token bias is a real confound. B2 (the full-vocabulary token at the marker) is skewed towards " A" (0.5B: 11,407 " A" vs 487 " B"), and the B0d-verbal 0.5B resolves its tied, unlabelled vectors to A. Both inflate "supported" without any real judgement.
- **Not tested in GroundOne:** permuting the letter assignment (e.g. A = not mentioned) for the untrained B1 or the judges. It would separate content judgement from letter preference. It is a cheap inference-only ablation and could go in the limitations or Ch. 8.
- Zheng's metric RStd (spread of per-class recalls) is close to what GroundOne already reports: per-class recall and macro (balanced) recall.

## Links
- Concepts: [[Letter-Token Readout]], [[Calibration]], [[System One Models]], [[LLM-as-a-Judge]]
- Related sources: [[Wang 2024 - My Answer is C (first-token probabilities vs text answers)]], [[Zhao 2021 - Calibrate Before Use]], [[Zheng 2023 - Judging LLM-as-a-Judge]] (position bias of pairwise judges), [[Kadavath 2022 - Language Models (Mostly) Know What They Know]]
- Thesis context: [[GroundOne]]
