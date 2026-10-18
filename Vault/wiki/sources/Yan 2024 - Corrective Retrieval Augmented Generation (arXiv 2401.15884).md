---
type: source
author: "Shi-Qi Yan, Jia-Chen Gu, Yun Zhu, Zhen-Hua Ling (USTC, UCLA, Google DeepMind)"
date: 2024
venue: "arXiv preprint only (2401.15884; the raw file is v3, 7 Oct 2024, and no peer-reviewed venue is stated on the PDF)"
url: "https://arxiv.org/abs/2401.15884"
tags: [source, paper, rag, retrieval-evaluator, corrective-rag, thresholds, web-search, verify-and-revise]
---
# Yan 2024 – Corrective Retrieval Augmented Generation (CRAG)

**Raw file**: `raw/demo/Yan 2024 - Corrective Retrieval Augmented Generation (arXiv 2401.15884)_ingested.pdf`

## Overview
CRAG makes RAG robust to **bad retrieval**. A lightweight **retrieval evaluator**, a fine-tuned T5-large of about 0.77B parameters, scores each retrieved document's relevance to the query. Two thresholds map the scores to one of three actions: **Correct** (refine the retrieved documents), **Incorrect** (discard them and search the web) or **Ambiguous** (combine both). The generator then answers from the corrected knowledge (§4, Fig. 2, Algorithm 1). The method is plug-and-play on top of standard RAG and Self-RAG and improves PopQA, Biography, PubHealth and ARC-Challenge (Table 1).

## Key Insights
1. **What is checked: the retrieval, before generation.** CRAG verifies the *input* to the generator (are these documents relevant?), not the generated answer. Correction means changing the context (filtering strips, adding web results), not rewriting the output. It is a one-shot gate, not an iterative loop.
2. **Feedback source: an external, specialised small model.** The evaluator is trained on PopQA relevance signals (positives labelled 1, negatives −1) and outputs a score in [−1, 1]. On PopQA it judges retrieval quality with **84.3% accuracy, against 58.0 / 62.4 / 64.7% for ChatGPT** (plain, CoT, few-shot) (Table 4, §5.5). The authors stress that it is much smaller than the 7B critic of [[Asai 2024 - Self-RAG|Self-RAG]] (§4.2).
3. **Three actions from two thresholds (§4.3, App. B.3).** Correct if at least one document is above the upper threshold, Incorrect if all are below the lower one, Ambiguous otherwise. The thresholds are **set empirically per dataset**: (0.59, −0.99) for PopQA, (0.5, −0.91) for PubHealth and ARC, (0.95, −0.91) for Biography. With only Correct and Incorrect, results were sensitive to evaluator errors; the Ambiguous band "significantly helps to mitigate the dependence on the accuracy of the retrieval evaluator" (§4.3). Removing any action lowers PopQA accuracy (Table 2).
4. **Knowledge refinement (§4.4).** Documents are split into strips of a few sentences, each strip is scored by the same evaluator (top-k 5, filter threshold −0.5) and the relevant strips are concatenated again. Web search uses queries rewritten by ChatGPT and prefers Wikipedia pages (§4.5).
5. **Results (§5.3, Table 1).** On the SelfRAG-LLaMA2-7b generator, CRAG beats RAG by 7.0 (PopQA accuracy), 14.9 (Biography FactScore), 36.6 (PubHealth) and 15.4 (ARC). Self-CRAG beats Self-RAG by 6.9 / 5.0 / 2.4 on PopQA / Biography / PubHealth. Giving RAG the same web results without the corrective gate helps less (Table 5), so the gain is attributed to the gating, not to the extra data.
6. **Cost (Table 6).** The estimate covers the generation phase only (retrieval and processing excluded): 26.5 → 27.2 TFLOPs per token and 0.363 → 0.512 s per PopQA instance for RAG → CRAG.
7. **Limitations (§6).** A separately fine-tuned evaluator is "inevitable", and the evaluator trained on PopQA is transferred to the other datasets. Web search adds an external, online dependency. The thresholds are hand-set, not calibrated.

## Relevance to GroundOne
- **Same design philosophy, other end of the pipeline.** CRAG is the RAG-side precedent for using a **small specialised evaluator** instead of a prompted LLM, and for showing that it is more accurate (84.3% vs 58–65% for ChatGPT). This mirrors the GroundOne thesis that a fine-tuned System One beats generative judges on its own narrow decision ([[System One Models]], [[LLM-as-a-Judge]]). CRAG checks *retrieval relevance before generation*; [[GroundOne]] checks *answer groundedness after generation*. The two are complementary and could share one local pipeline ([[Retrieval-Augmented Generation]]).
- **Thresholded actions are a policy layer.** CRAG's "score, then three actions decided by thresholds" is structurally the demo's policy: a calibrated P(supported) against τ, then highlight / hide / abstain or rewrite ([[Guardrails and Policies]]). The difference is that CRAG's thresholds are hand-tuned per dataset on uncalibrated scores, while GroundOne fits temperature, bias and τ on dev, bound to the model fingerprint ([[Calibration]], [[Selective Prediction]]). The value of CRAG's Ambiguous band, which reduces sensitivity to evaluator error, is an argument for keeping an intermediate action in the demo, such as highlighting rather than hiding when the probability falls in a band around τ.
- **A repair path the demo could add.** For sentences labelled *not mentioned*, CRAG suggests a remedy different from rewriting: re-retrieve or widen the context, then re-verify. The demo uses targeted rewriting, but noting this alternative keeps the design discussion honest ([[Verify-and-Revise Loops]]).
- **Locality.** CRAG's fallback is a commercial web search API and its query rewriter is ChatGPT. Both conflict with the demo's fully local setting, so only the evaluator-and-gate idea transfers ([[On-Device Inference]], [[Privacy and Data Sovereignty]]).

## Links
- Concepts: [[Retrieval-Augmented Generation]], [[Verify-and-Revise Loops]], [[Guardrails and Policies]], [[Selective Prediction]], [[Calibration]], [[System One Models]], [[Demo Application]]
- Related sources: [[Asai 2024 - Self-RAG]], [[Lewis 2020 - Retrieval-Augmented Generation]], [[Gao 2023 - RARR, Researching and Revising What Language Models Say (arXiv 2210.08726)]], [[Min 2023 - FActScore]]
