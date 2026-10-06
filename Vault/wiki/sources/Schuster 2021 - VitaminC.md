---
type: source
author: "Tal Schuster, Adam Fisch, Regina Barzilay"
date: 2021
venue: "NAACL 2021 (arXiv:2103.08541), pp. 624–643"
url: https://aclanthology.org/2021.naacl-main.52
data: https://huggingface.co/datasets/tals/vitaminc
licence: "data CC BY-SA 3.0 (HF card), code MIT"
tags: [source, paper, dataset, fact-verification, contrastive, three-way, test-data]
---
# Schuster 2021 - VitaminC

**Raw files**:
- `raw/Schuster 2021 - VitaminC_ingested.pdf` (20 pages; main text and Appendix A read);
- `raw/Dataset card - VitaminC_ingested.md` (HF card: licence `cc-by-sa-3.0`, English, task fact-checking / NLI).

**VitaminC** ("Get Your Vitamin C! Robust Fact Verification with Contrastive Evidence") is a fact-verification dataset: claim–evidence pairs labelled SUPPORTS / REFUTES / NOT ENOUGH INFO (NEI). It is built from Wikipedia revisions that change a fact. The two versions of the sentence (before and after the edit) are nearly identical, but one supports a claim and the other does not. In [[GroundOne]] it is the three-way test set T3 (see [[VitaminC]], [[Datasets for GroundOne]]).

## Construction (§3)
- **Factual revisions.**
  - Sources: the 5K most-viewed English Wikipedia articles (January 2020) plus the articles they link to (about 100 each), all FEVER articles, and COVID-19 articles (May 2020).
  - About 200M revisions in total. A BERT classifier pre-selected 305K edited sentences, and trained annotators marked those that really change a fact.
  - Sentences without self-contained context (table cells, list items) were filtered out.
- **Claims.** For each factual revision, annotators wrote two symmetric claims: one supported by the old sentence and refuted by the new one, and the reverse.
  - When an explicit contradiction was impossible, the pair was labelled **NEI**.
  - Revisions that only add or remove information got a single claim.
  - Annotators were told to avoid copying phrases and values, to limit word-overlap bias (e.g. "more than z cases" instead of "x cases").
- **Annotators.** 70 native English speakers (vendor: TransPerfect) wrote and reviewed the claims, with weekly sample checks and corrections.
- **Synthetic part.** Built from FEVER: annotators edit the refuting sentence so that it supports the false claim, and write a claim refuted by the edited sentence. It has SUPPORTS and REFUTES only, no NEI.
- **Splits.** Assigned randomly **by article**, consistent with FEVER for overlapping articles.

## Size (Table 2; real / synthetic)
| Split | SUPPORTS | REFUTES | NEI |
|---|---|---|---|
| Train | 124,864 / 60,850 | 71,108 / 60,850 | 52,981 / – |
| Dev | 21,102 / 10,382 | 12,146 / 10,382 | 9,042 / – |
| Test | 17,306 / 10,358 | 9,907 / 10,358 | 7,268 / – |

The real test set has 34,481 pairs, and its classes are **not balanced** (50 / 29 / 21 %).

## Label quality (Appendix A.2)
- Three extra annotators re-labelled 2,000 random pairs (dev and test, real and synthetic).
- Fleiss κ between the four annotations is **0.7065** (substantial). For comparison: FEVER 0.68, SNLI 0.70.
- About half of the real claims are about **numerical values** (COVID-19 cases, earnings, ratings, awards), because the source is revisions of frequently updated facts.

## Key results (authors' measurements)
- Training on VitaminC's contrastive pairs makes models more robust: **+10 % on adversarial fact verification and +6 % on adversarial NLI** (abstract, §5).
- Additional tasks defined on the same data: factual revision flagging, word-level rationale tagging, and factually consistent revision generation.

## Relevance for GroundOne
- **What it measures.** The **contradicted vs not_mentioned** boundary, with human labels of known reliability (κ = 0.71). RAGTruth does not report any agreement for its conflict vs baseless type (see [[RAGTruth]]).
- **Mapping.** SUPPORTS → supported, REFUTES → contradicted, NEI → not_mentioned.
- **Limits.**
  - The evidence is one Wikipedia sentence and the claims are single sentences, so K = 1 and it is not a RAG test.
  - Many numerical claims; Wikipedia domain.
  - GroundOne is not trained on it, so T3 measures transfer from RAGTruth.
- **Use.** Test only, real subset, sampled stratified by class (dataset plan, `Project/docs/dataset_plan.md`).
