---
type: source
author: "Yixin Nie, Adina Williams, Emily Dinan, Mohit Bansal, Jason Weston, Douwe Kiela"
date: 2020
venue: "ACL 2020 (arXiv:1910.14599v2)"
url: https://arxiv.org/abs/1910.14599
tags: [source, paper, dataset, nli, adversarial, training-data]
---
# Nie 2020 - Adversarial NLI

**Raw file**: `raw/Nie 2020 - Adversarial NLI_ingested.pdf` (17 pages; read the main text and Appendix C)

**ANLI** is a 3-way [[Natural Language Inference]] dataset (entailment / neutral / contradiction). It was collected in three adversarial rounds, A1–A3, with a *human-and-model-in-the-loop* procedure called **HAMLET**: annotators write hypotheses that fool the current best model, other humans verify them, and the model is retrained for the next round. It is one of GroundOne's candidate training sets, and [[MiniCheck]] already trains on a 21K hard subset of it.

## Overview
- **Procedure (§2.1–2.2, Fig. 1)**:
  - A writer receives a context and a target label and writes a hypothesis. The model's prediction is shown as feedback, and the writer gets up to 5 tries (R1) or 10 tries (R2/R3) to fool it.
  - If the model is fooled, the example is verified by 2 humans, with a third as tie-breaker.
  - **Train contains both model-fooling and model-correct examples, and training examples are not all verified.** Dev and test contain only verified, model-fooling examples. Test uses "exclusive" annotators and is balanced by label.
- **Rounds**:
  - **A1**: BERT-Large adversary trained on SNLI+MNLI. Contexts are 250–600-character Wikipedia passages via HotpotQA.
  - **A2**: RoBERTa ensemble trained on SNLI, MNLI, FEVER-NLI and A1. New Wikipedia contexts.
  - **A3**: stronger RoBERTa ensemble. Contexts from Wikipedia, news (Common Crawl), fiction, spoken text (MASC), WikiHow procedural text, and RTE5.
- **Sizes (Table 2, Table 9)**:
| Round | Train | Dev | Test |
|---|---|---|---|
| A1 | 16,946 | 1,000 | 1,000 |
| A2 | 45,460 | 1,000 | 1,000 |
| A3 | 100,459 | 1,200 | 1,200 |
| **ANLI** | **162,865** | **3,200** | **3,200** |

  Train label counts (E/N/C) are **52,111 / 68,789 / 41,965**. Dev and test are balanced: 1,070 / 1,068 / 1,062 each.
- **Agreement**: verifier Fleiss' κ is about 0.67–0.74 on dev and test (Table 10). Expert-flagged quality issues are rare, at 3–4% per round (§5).

## Key results (authors' measurements)
- **Hard by design (Table 3)**: RoBERTa trained on everything (S, M, F, ANLI) reaches A1 73.8, A2 48.9, A3 44.4, **ANLI 53.7**. Chance is 33%.
- **Hypothesis-only baselines** reach about 47 on ANLI after training on ANLI, against about 71 on SNLI (Table 6). ANLI has fewer annotation artefacts.
- **Adding ANLI does not hurt SNLI/MNLI** and gives state of the art at the time: MNLI-m/mm 91.0 / 90.7 with RoBERTa.
- **Adversarial data is more data-efficient** than standard NLI data at equal size (Table 5, Fig. 2). Verified examples are far more useful than unverified ones (Fig. 3).
- **Inference types (Table 7)**: about 58% of dev examples need reasoning or outside facts, and 27% are numerical or quantitative.

## Relevance to GroundOne
- **Label mapping**: entailment → *supported*; neutral and contradiction → *unsupported*. This is exactly MiniCheck's choice (§3.3 of [[Tang 2024 - MiniCheck]]). Training is then 2-class, about 32% / 68% supported / unsupported on train. Rebalance, or use class weights.
- **Why ANLI rather than plain MNLI**: ANLI has multi-sentence contexts and adversarially hard hypotheses. MiniCheck found that a **21K subset of ANLI examples that fooled the models** worked, while "training on more of ANLI was not effective". A useful prior for GroundOne: use the hard subset rather than all 163K.
- **Noise**: train includes unverified examples, which matters if GroundOne also targets calibration ([[Calibration]], [[Expected Calibration Error]]).
- **Context length**: contexts are short (A1/A2: 250–600 characters), so ANLI alone does not teach long-context grounding. Combine it with longer-context data (MiniCheck D2C, the RAGTruth training split).
- **Licence**: **not stated in the paper**. The data is distributed at `github.com/facebookresearch/anli`; check the licence there before redistributing derived data.

## Links
- Concepts: [[Natural Language Inference]], [[Groundedness Verification]], [[MiniCheck]], [[AlignScore]], [[Hallucination Detection]]
- Related sources: [[Williams 2018 - MultiNLI Broad-Coverage Challenge Corpus]], [[Tang 2024 - MiniCheck]], [[Zha 2023 - AlignScore]]
