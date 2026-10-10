---
type: source
author: "Yubo Li, Yidi Miao, Ramayya Krishnan, Rema Padman (Carnegie Mellon University)"
date: 2026
venue: "arXiv 2609.26550 v4 (6 Oct 2026)"
url: "https://arxiv.org/abs/2609.26550"
tags: [source, paper, system-one, jev, llm-as-a-judge, selective-prediction, cascade, calibration, halueval, thresholds]
---
# Li 2026 – JEV-as-a-Judge: Accept When Confident, Escalate When Unsure

**Raw file**: `raw/Li 2026 - JEV-as-a-Judge Accept When Confident Escalate When Unsure (arXiv 2609.26550)_ingested.pdf`

## Overview
A CMU study of [[Jev]] 1.13 as a **decision-only judge**: it returns label probabilities instead of text, and its largest probability *q* decides whether to accept the verdict or escalate to a reasoning LLM judge. Jev is compared with sixteen judges (fourteen generative LLMs, two reward models) on 5,172 base judgments: pairwise preference (1,500 RewardBench, 350 JudgeBench pairs), **evidence-grounded factuality (3,000 HaluEval QA answers)** and final-answer adjudication (150), plus follow-ups and a pre-specified live test. Generative judges answer under Jev's output contract (verdict plus label probabilities, no rationale). A team member blind to labels adjudicated 163 disputed items of a 990-item subset.

## Key Insights
1. **Cheap, mid-pack in accuracy.** Pooled over 4,850 public judgments Jev ranks 8th of 15 LLM judges, 1.7 points behind GPT-6, at $0.044 per 1,000 judgments (277× cheaper than GPT-6's $12.182) and 0.15 s median latency (p95 0.24 s vs 3.86 s).
2. **Reading vs deriving.** Jev is within about two points of GPT-6 where "a verdict can be read off the text" (chat quality, refusals, evidence-grounded factuality) and trails by 7–28 points where it must be derived (expert knowledge −7.0, code −12.9, math −14.3, logic puzzles −27.6). JudgeBench: 78.6 vs 93.1.
3. **Evidence-grounded factuality (HaluEval QA, 3,000).** Jev 87.3 % vs GPT-6 88.4 % (−1.1 [−1.9, −0.3]); best is GPT-5.6 89.9; Qwen3.8-27B 87.8; Qwen3.5-27B local 84.7. Label noise is large: 24 of 26 adjudicated items that both judges "miss" carry labels the evidence does not support; with human labels on 240 answers, Jev 95.8 % vs GPT-6 98.3 %. Grounded summaries (400): 69.8 vs 69.3; reference-free prose (200): all judges near chance.
4. **Confidence locates errors.** Error-detection AUROC of *q*: 0.875 (RewardBench), 0.745 (JudgeBench), 0.827 (HaluEval). Where *q* ≥ 0.9, Jev and GPT-6 are nearly tied (94.7 % vs 94.4 % on 3,744 items). It weakens on style-adversarial pairs (0.76 vs 0.84).
5. **Probabilities need local fitting.** Brier 0.113 / 0.297 / 0.196 on the three tasks. Temperature scaling fitted on a small selection set **transfers unevenly**: NLL improves on HaluEval (0.496 → 0.304) but worsens on JudgeBench and RewardBench; fitted temperatures point in different directions (0.65, 2.15, 4.45): "every fit needs held-out validation".
6. **Frozen cascade.** With a threshold frozen in advance, accepting confident verdicts and escalating the rest is 0.9 points more accurate than GPT-6 on 1,610 held-out pairs at 41 % of its fee, escalating 31 %. Choosing the threshold by a **one-sided lower confidence bound** instead of a point estimate cuts the risk of losing more than two points from about 45 % to about 5 % with about 100 local labels. In a live test on two new workloads the cascade matches GPT-6 exactly while escalating 74 %.
7. Limitation stated: one proprietary Jev version; training overlap with the benchmarks unknown; not compute-matched.

## Relevance to GroundOne
- **Closest published analogue of GroundOne's served rule.** GroundOne serves "supported" iff calibrated P(supported) ≥ τ with τ fitted on dev ([[Selective Prediction]]). Li 2026 shows that (a) such thresholds should be validated locally, and (b) a lower-confidence-bound choice of τ is much safer than a point estimate. A cheap, citable improvement for the thesis's threshold section.
- **Evidence-grounded verification is where a decision-only judge is competitive** (within ~1 point of the strongest LLM judge on HaluEval QA), and where label noise caps measured accuracy: both support GroundOne's task choice ([[Groundedness Verification]], [[LLM-as-a-Judge]]).
- **Temperature transfer fails across workloads**, as GroundOne's calibration fails to transfer from RAGTruth to VitaminC ([[Calibration]]).
- Equal-output contract for generative judges mirrors GroundOne's B0d baseline.

## Links
- Concepts: [[LLM-as-a-Judge]], [[Selective Prediction]], [[Calibration]], [[Jev]], [[Groundedness Verification]], [[When System One Beats an LLM]], [[Decision-Model Benchmarks]]
- Related sources: [[Guo 2026 - Just Ask Jev (arXiv 2609.29429)]], [[Deusser 2026 - Evaluating and Benchmarking the System One Model Jev (arXiv 2609.37647)]], [[Geifman 2017 - Selective Classification for Deep Neural Networks]], [[Guo 2017 - On Calibration of Modern Neural Networks]]
