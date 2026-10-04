---
type: source
author: "Lianmin Zheng, Wei-Lin Chiang, Ying Sheng, Siyuan Zhuang, Zhanghao Wu, Yonghao Zhuang, Zi Lin, Zhuohan Li, Dacheng Li, Eric P. Xing, Hao Zhang, Joseph E. Gonzalez, Ion Stoica"
date: 2023
venue: "NeurIPS 2023 Datasets and Benchmarks Track (arXiv 2306.05685v4)"
url: https://arxiv.org/abs/2306.05685
tags: [source, paper, llm-as-a-judge, evaluation, bias, mt-bench, chatbot-arena]
---
# Zheng 2023 - Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena

**Raw file**: `raw/Zheng 2023 - Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena_ingested.pdf`

## Overview
The paper that systematised **[[LLM-as-a-Judge]]**. It introduces **MT-Bench** (80 multi-turn questions, 8 categories) and **Chatbot Arena** (crowdsourced anonymous pairwise battles, ~30K votes), and studies whether strong LLMs (GPT-4, GPT-3.5, Claude-v1) can replace human preference judgements for open-ended chat answers (§2–4). Released: 80 questions, 3K expert votes, 30K conversations.

Three judge formats (§3.1 p.4): **pairwise comparison**, **single-answer grading** (score 1–10), **reference-guided grading**. Pairwise does not scale (pairs grow quadratically); single-answer scores may be unstable across judge models.

## Key Insights
1. **Agreement with humans (measured)**: GPT-4 agrees with expert humans 85% on MT-Bench non-tie votes (setup S2), higher than human–human agreement of 81% (Table 5 p.8, §4.2 p.7). On Chatbot Arena, GPT-4 vs crowd 87% (S2) (Table 6 p.8). With ties/inconsistent votes counted (S1), agreement is ~66% for both GPT-4–human and human–human. Agreement rises from 70% to ~100% as the quality gap between the two models grows (Fig. 2 p.8): judges are reliable on easy contrasts, much less on close ones.
2. **Position bias (measured, Table 2 p.5)**: consistency when swapping answer order is only 65.0% for GPT-4, 46.2% for GPT-3.5, 23.8% for Claude-v1 (default prompt); Claude-v1 favours the first position 75.0% of the time. Authors suspect the left-to-right causal architecture or training data (p.5).
3. **Verbosity bias (measured, Table 3 p.5)**: a "repetitive list" attack (padding answers with rephrased content) fools Claude-v1 and GPT-3.5 91.3% of the time, GPT-4 8.7% (23 answers).
4. **Self-enhancement bias (inconclusive)**: GPT-4 favours itself with a ~10% higher win rate and Claude-v1 ~25%, but GPT-3.5 does not; "our study cannot determine whether the models exhibit a self-enhancement bias" due to limited data (p.5).
5. **Limited reasoning when grading**: GPT-4 can be misled by the provided (wrong) answers on math it could solve alone. Reference-guided judging cuts the failure rate from 14/20 (70%) to 3/20 (15%); CoT only to 6/20 (Table 4 p.5, §3.4 p.6).
6. **Mitigations (§3.4)**: swap positions and only count consistent wins (conservative); few-shot examples raise GPT-4 consistency from 65.0% to 77.5% but **make API calls ~4× more expensive** (p.6) and may add new biases.
7. **Claimed advantages (§3.2)**: scalability and *explainability*: judges output explanations as well as scores. Human evaluation is "exceptionally slow and costly" (p.2). The paper gives **no per-judgement latency or dollar cost** (not stated) beyond the 4× few-shot note.
8. **Stated limitations (§6 p.9)**: focuses on helpfulness, neglects safety/honesty; collapses accuracy, relevance and creativity into a single score. A fine-tuned Vicuna-13B judge is only explored as preliminary (§3.4, Appendix F, not read).

## Relevance to GroundOne
- **Biases of generative judges are measured here**, giving the related-work chapter concrete numbers for why an LLM judge is not a free gold standard. For pointwise groundedness verification (one context, one sentence) pairwise position bias is less relevant, but **order sensitivity** (context vs. claim, option order of answer letters) and **verbosity** effects still apply, also to GroundOne's letter readout, which should be tested with permuted options ([[When System One Beats an LLM]] notes order flips in open-model direct logits).
- **Agreement framing**: "85% with humans vs 81% human–human" is the standard argument for LLM judges. It concerns preference on chat answers, not faithfulness; it does not transfer automatically to [[Groundedness Verification]], where benchmarks like [[LLM-AggreFact]] and [[RAGTruth]] are the right yardstick.
- **Cost/latency**: the paper motivates LLM judges by cost relative to humans, not relative to small models. Every judgement is a generative call with an explanation (decode-heavy, [[Prefill and Decode]]); GroundOne replaces this with one prefill-only pass per sentence, trading the rationale for speed ([[System One Models]]).
- **Reference-guided judging** (insight 5) parallels grounding: giving the judge the evidence reduces errors. GroundOne is always "reference-guided" (the retrieved context is the reference).

## Links
- Concepts: [[LLM-as-a-Judge]], [[RAG Evaluation Frameworks]], [[Groundedness Verification]], [[Calibration]], [[System One Models]], [[Jev]], [[When System One Beats an LLM]], [[Prefill and Decode]]
- Related sources: [[Es 2024 - RAGAS]], [[Saad-Falcon 2024 - ARES]], [[Asai 2024 - Self-RAG]]
