---
type: source
author: "Philippe Laban, Tobias Schnabel, Paul N. Bennett, Marti A. Hearst"
date: 2022
venue: "TACL 2022 (arXiv 2111.09525)"
url: "https://arxiv.org/abs/2111.09525"
tags: [source, paper, nli, inconsistency-detection, summarization, sentence-level, benchmark, balanced-accuracy]
---
# Laban 2022 – SummaC: Re-Visiting NLI-based Models for Inconsistency Detection in Summarization

**Raw file**: `raw/Laban 2022 - SummaC_ingested.pdf`

## Overview
Earlier work found that [[Natural Language Inference|NLI]] models perform poorly at detecting summaries that are inconsistent with their source document (e.g. 52% accuracy out of the box, §1). SummaC shows that the failure comes from a **granularity mismatch**: NLI models are trained on sentence pairs but were applied to whole documents. Splitting both document and summary into **sentences**, scoring every (document sentence, summary sentence) pair with an NLI model, and aggregating the scores makes NLI competitive. The paper also introduces the **SummaC Benchmark**, six summary-consistency datasets standardised as binary classification. SummaC-Conv reaches **74.4% balanced accuracy**, 5 points above the best prior method (abstract, Table 2).

## Key Insights
1. **NLI Pair Matrix (§3.1).** The document is split into M blocks and the summary into N; each pair gives entailment, contradiction and neutral probabilities, and the M × N entailment matrix is the input to aggregation. Fig. 1: whole-document NLI gives P(entail) = 0.91 to a summary whose third sentence is unsupported, while the sentence-level matrix shows no document sentence entails it.
2. **SummaC-ZS (§3.2).** Zero-shot: take the **max over document sentences** for each summary sentence (the strongest support), then the **mean over summary sentences**. No trained parameters; directly interpretable per sentence.
3. **SummaC-Conv (§3.3).** For each summary sentence, a histogram of its entailment scores over all document sentences (50 bins) goes through a learned 1-D convolution; scores are averaged. Trained on 10,000 synthetic FactCC pairs. Less sensitive to outliers than max, but less interpretable (§7).
4. **Benchmark and metric (§4, Table 1).** CoGenSumm, XSumFaith, Polytope, FactCC, SummEval, FRANK; positive rates range from 6% to 91%, so **balanced accuracy** is the primary metric with a **per-dataset threshold tuned on the validation split**; ROC-AUC is secondary (§4.2). Extrinsic and intrinsic hallucinations are both mapped to "inconsistent", and accurate-but-unsupported content counts as inconsistent (§2.1, §4.1).
5. **Results (Table 2).** Overall BAcc: MNLI-doc 61.3, FactCC-CLS 62.8, DAE 64.2, QuestEval 69.4, **SummaC-ZS 72.1**, **SummaC-Conv 74.4**. Throughput is about 430 documents/min against 6,200 for document-level MNLI.
6. **Ablations (§5.3).** The best NLI model is trained on **VitaminC + MNLI** (Table 3). Using the contradiction probability on top of entailment helps slightly for some NLI models (Table 4). **Finer granularity is better**: MNLI-based scores rise from 56.4% (full document) to 73.5% (sentence level); document granularity should not be finer than summary granularity (Table 5).

## Relevance to GroundOne
- **The direct ancestor of sentence-level verification.** GroundOne splits the RAG answer into sentences and gives each a verdict against the document. SummaC is the canonical evidence that sentence-level units are what make entailment-style checking work, and SummaC-ZS's "max over premises, then aggregate" is the template for turning sentence verdicts into an answer-level label ([[Groundedness Verification]], [[Hallucination Detection]]).
- **What GroundOne changes.** SummaC splits the *document* too and runs M × N encoder passes. GroundOne keeps the whole document as context in a decoder and reads all K sentence verdicts from **one forward pass**, so cross-sentence evidence in the document is available without chunking ([[Prefill and Decode]]).
- **Three classes, not just entailment.** SummaC mostly uses only P(entail) and finds that adding contradiction helps a little. GroundOne predicts supported / contradicted / not mentioned explicitly, in the spirit of NLI's three labels.
- **Protocol choices.** SummaC tunes thresholds per dataset on validation data; the LLM-AggreFact headline instead uses a fixed threshold. GroundOne reports the raw (balanced) decision as the headline and fits its served threshold only on dev, never on test.
- **VitaminC link.** The best SummaC NLI model is trained on VitaminC, which is also GroundOne's out-of-domain test T3 ([[VitaminC]]).

## Links
- Concepts: [[Groundedness Verification]], [[Hallucination Detection]], [[Natural Language Inference]], [[VitaminC]], [[LLM-AggreFact]]
- Related sources: [[Min 2023 - FActScore]], [[Huang 2023 - A Survey on Hallucination in LLMs]], [[Tang 2024 - MiniCheck]], [[Zha 2023 - AlignScore]], [[Schuster 2021 - VitaminC]], [[Williams 2018 - MultiNLI Broad-Coverage Challenge Corpus]]
