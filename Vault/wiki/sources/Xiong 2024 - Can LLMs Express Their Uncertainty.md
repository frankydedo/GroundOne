---
type: source
author: "Miao Xiong, Zhiyuan Hu, Xinyang Lu, Yifei Li, Jie Fu, Junxian He, Bryan Hooi"
date: 2024
venue: "ICLR 2024 (arXiv 2306.13063)"
url: "https://arxiv.org/abs/2306.13063"
tags: [source, paper, uncertainty, verbalized-confidence, calibration, failure-prediction, llm]
---
# Xiong 2024 – Can LLMs Express Their Uncertainty? An Empirical Evaluation of Confidence Elicitation in LLMs

**Raw file**: `raw/Xiong 2024 - Can LLMs Express Their Uncertainty_ingested.pdf`

## Overview
A systematic benchmark of **black-box confidence elicitation**: getting a confidence score from an LLM without logits or fine-tuning. The paper splits the design space into three parts (§3, Fig. 1):
- a **prompting strategy** for verbalised confidence: vanilla, CoT, Self-Probing, Multi-Step, Top-K;
- a **sampling strategy** for multiple responses: self-random, paraphrased prompts, misleading hints;
- an **aggregation strategy**: Consistency, Avg-Conf, Pair-Rank.

Confidence is evaluated on two separate tasks: **calibration (ECE)** and **failure prediction (AUROC, AUPRC-Positive/Negative)** (§4). The models are GPT-3, GPT-3.5, GPT-4, Vicuna-13B and LLaMA-2-70B-Chat, on eight datasets covering commonsense, arithmetic, symbolic, ethics and professional-law questions.

## Key Insights
1. **Verbalised confidence is overconfident and coarse (§5.1).** Stated confidences fall mostly in 80–100 % and in multiples of 5, much as humans talk (Fig. 2). Average ECE exceeds 0.377 for GPT-3, GPT-3.5 and Vicuna. GPT-4 has lower ECE, but its average AUROC is only 62.7 %, close to chance (Table 2).
2. **Low ECE does not mean useful confidence (§5.2).** Prompting strategies lower ECE, but failure prediction stays near AUROC 0.5. Example: GPT-4 with CoT on GSM8K reaches 93.6 % accuracy and a "near-optimal" ECE of 0.064 by giving **100 % confidence to every sample**, which cannot separate right from wrong answers. The authors read the lower ECE as a smaller gap between mean confidence and accuracy, not as better self-knowledge.
3. **Consistency across samples helps failure prediction (§5.3).** With five sampled responses plus consistency aggregation, GSM8K AUROC rises from 54.8 % to 92.7 % (Table 3). The gains flatten as M grows (Fig. 7), and cost scales linearly with M.
4. **Aggregators favour different metrics (§5.4).** Pair-Rank gives the lowest ECE (down to 0.028); Avg-Conf gives the best failure prediction (Table 4). No method wins everywhere. The practitioner recipe is Top-K prompt + self-random sampling + Avg-Conf or Pair-Rank (§6).
5. **White-box vs black-box (§B.1).** Token-probability methods (sequence, length-normalised and key-token probability) beat verbalised confidence, but the gap is narrow (e.g. AUROC 0.522 → 0.605), and nearly all methods stay at AUROC 0.5–0.6 on these reasoning tasks.
6. **Limits (§6).** Only QA with unique answers was studied; the authors suggest that combining black-box methods with limited logit access is promising.

## Relevance to GroundOne
- Xiong's §5.2 is the published version of GroundOne's **B0d finding that ECE alone is misleading**. After the same temperature + bias calibration, every judge reaches ECE 0.03–0.05, yet judge AUROC is 0.47–0.68, near chance for the 0.5B. GroundOne reaches 0.94–0.97. The thesis must therefore report AUROC and AURC next to ECE. See [[Expected Calibration Error]] and [[Selective Prediction]].
- **Coarse verbalised values, reproduced.** The B0d-verbal 3B writes a one-hot probability vector for 93 % of sentences (16 distinct vectors in 1,747). The 0.5B writes tied, uninformative vectors such as [1/3, 1/3, 1/3]. This matches Xiong's 80–100 % / multiples-of-5 pattern at the extreme that small open models produce.
- **White-box > black-box, reproduced.** For the 3B judge, logit-read probabilities (B0d-logit) beat verbalised ones: AUROC 0.681 vs 0.576, AURC 0.048 vs 0.062, at about a quarter of the latency (4.38 s vs 17.0 s per answer at K ≥ 14). Like Xiong, the gap between the two is small compared with the gap to a model trained for the decision.
- **Cost argument.** Xiong's best black-box methods need several sampled responses (M = 5–13) and long outputs. Per verdict that costs more decode than the verbose judge. GroundOne's probabilities cost one prefill and zero generated tokens. See [[Prefill and Decode]].
- **Scope caveat.** Xiong evaluate confidence in the model's *own* answer to reasoning questions. GroundOne's probabilities are about an external claim given a document (supported / contradicted / not mentioned). The direction of the findings transfers; the numbers do not.

## Links
- Concepts: [[Verbalised vs Logit Confidence]], [[Calibration]], [[Expected Calibration Error]], [[Selective Prediction]], [[LLM-as-a-Judge]]
- Related sources: [[Tian 2023 - Just Ask for Calibration]] (concurrent; Top-K prompt), [[Kadavath 2022 - Language Models (Mostly) Know What They Know]], [[Guo 2017 - On Calibration of Modern Neural Networks]], [[Naeini 2015 - Obtaining Well Calibrated Probabilities Using Bayesian Binning]]
- Thesis context: [[GroundOne]], [[System One Models]]
