---
type: source
author: "Yuheng Zha, Yichi Yang, Ruichen Li, Zhiting Hu"
date: 2023
venue: "ACL 2023 (arXiv:2305.16739v1)"
url: https://arxiv.org/abs/2305.16739
tags: [source, paper, factual-consistency, metric, encoder, roberta, nli]
---
# Zha 2023 - AlignScore

**Raw file**: `raw/Zha 2023 - AlignScore_ingested.pdf` (19 pages; read pp.1–10, 14–15 and Table 9)

AlignScore is a factual-consistency metric built on a single **"information alignment" function**. It is a RoBERTa model trained on 4.7M examples that were converted from 7 different NLP tasks. To handle long contexts it splits the context into chunks and the claim into sentences, then aggregates. It was the strongest specialized fact-checker before [[MiniCheck]]. Concept page: [[AlignScore]].

## Overview
- **Definition (§3.1)**: text b is *aligned* with text a if all the information in b is present in a and does not contradict a.
- **Unified training data (Table 1, p.4)**: 15 datasets from 7 tasks, capped at 500k examples per dataset, for **4.7M examples** in total:
  - NLI: SNLI, MNLI, ANLI, DocNLI
  - Fact verification: NLI-style FEVER, VitaminC
  - Paraphrase: QQP, PAWS, WikiText-103 (synthetic)
  - STS: SICK, STS-B
  - QA: SQuAD v2, RACE
  - IR: MS MARCO
  - Summarization: WikiHow (synthetic)
- **Three output heads**: 3-way (aligned / contradict / neutral), binary, and regression. Training minimizes the sum of the three losses with λ = 1 each (§3.1).
- **Scoring (§3.2, Eq. 3)**:
  - The context is split into chunks of about 350 tokens (whitespace) at sentence boundaries. This is needed because **RoBERTa has a 512-token limit**.
  - The claim is split into sentences.
  - Each claim sentence takes its maximum P(ALIGNED) over all chunks, using the 3-way head. The score is the **mean** of these maxima over claim sentences.
- **Models (App. A.3, Table 6)**: AlignScore-base is RoBERTa-base, 125M, trained on 2×3090 for 100 GPU-h. AlignScore-large is **RoBERTa-large, 355M**, trained on 4×A5000 for 532 GPU-h. Both trained for 3 epochs, bs 32, lr 1e-5 with AdamW.

## Key results (authors' measurements)
- **SummaC benchmark (Table 2, AUC-ROC)**: AlignScore-large averages **88.6** (base 87.4), the best of all metrics. Balanced accuracy with thresholds tuned on validation (Table 9) is **82.0** for large and 80.6 for base.
- **TRUE benchmark (Table 3, AUC-ROC)**: AlignScore-large averages **87.4**. Excluding the datasets seen in training (AVG-ZS), it averages 83.8.
- **SummaC protocol (§4.2)**: tune the threshold on validation, then report balanced accuracy on test, plus AUC-ROC. This is the "threshold tuning" convention that [[MiniCheck]] later chose *not* to use for its headline numbers.
- **Comparison with LLM metrics (Table 5)**: the claim "matches or outperforms ChatGPT/GPT-4 metrics" rests on correlations taken from other papers, on SummEval and QAGS.

## Ablations (§4.5)
- The **3-way head** beats the binary and regression heads (Fig. 3).
- **Chunk-level splitting** beats document-level (truncated input) and sentence-level splitting (Fig. 4).
- **Removing NLI data *improves* performance on most benchmarks** (Fig. 5). The authors' explanation: NLI premises and hypotheses are short, and the other tasks have more and higher-quality data. Removing QA hurts the most, and fact verification is second.

## Limitations (p.10)
- No explanations or span localization.
- The rule-based synthetic data may be noisy.
- English only.

## Relevance to GroundOne
- **Encoder baseline**: on [[LLM-AggreFact]], AlignScore scores **70.4** in the paper (Table 2 of [[Tang 2024 - MiniCheck]], no threshold tuning) and **70.5** on the leaderboard. It scores 71.7 on the RAGTruth column.
- **Training-data warning**: the NLI ablation suggests that short-premise NLI data (MNLI, SNLI) may not transfer well to long-context grounding. This matters for choosing between ANLI and MNLI and for how much to weight them ([[Natural Language Inference]]). ANLI's multi-sentence contexts are closer to the target task than MNLI's single sentences.
- **Context handling**: GroundOne can cite AlignScore's chunk-and-max design (350-token chunks) as the standard fix for a 512-token encoder limit. A decoder like [[Qwen2.5]] can read the full context in one pass.
- **How to run**: code at `github.com/yuh-zha/AlignScore` (footnote 1). Checkpoint hosting, licence and Mac/MPS support are **not stated** in the paper.

## Links
- Concepts: [[AlignScore]], [[Natural Language Inference]], [[Hallucination Detection]], [[Groundedness Verification]], [[LLM-AggreFact]], [[MiniCheck]]
- Related sources: [[Tang 2024 - MiniCheck]], [[Tang 2024 - LLM-AggreFact Leaderboard]], [[Nie 2020 - Adversarial NLI]], [[Williams 2018 - MultiNLI Broad-Coverage Challenge Corpus]]
