---
type: source
author: "Adina Williams, Nikita Nangia, Samuel R. Bowman"
date: 2018
venue: "NAACL-HLT 2018 (arXiv:1704.05426v4)"
url: https://arxiv.org/abs/1704.05426
tags: [source, paper, dataset, nli, training-data]
---
# Williams 2018 - MultiNLI Broad-Coverage Challenge Corpus

**Raw file**: `raw/Williams 2018 - MultiNLI Broad-Coverage Challenge Corpus_ingested.pdf` (11 pages; read pp.1–8)

**MultiNLI (MNLI)** is a 433k-pair crowd-sourced [[Natural Language Inference]] corpus over **ten genres** of written and spoken American English. It is collected the same way as SNLI but is broader and harder. It is a standard NLI pretraining source and a candidate GroundOne training set.

## Overview
- **Collection (§2.1)**:
  - The premise is a single sentence from a source text.
  - A crowdworker writes three hypotheses: one *definitely correct* (ENTAILMENT), one that *might be correct* (NEUTRAL) and one *definitely incorrect* (CONTRADICTION). The classes are therefore balanced in the raw corpus.
  - 387 annotators worked through the Hybrid platform.
- **Genres (§2.1, Table 3)**:
  - **Matched** (in train, dev and test): Fiction, Government, Slate, Telephone, Travel.
  - **Mismatched** (dev and test only): 9/11, Face-to-face, Letters, OUP, Verbatim.
  - Nine genres come from OANC; Fiction is compiled from freely licensed works.
- **Validation (§2.1, Table 2)**:
  - Dev and test pairs receive 4 extra labels, and the gold label is a majority of 5.
  - 58.2% of validated pairs are unanimous. Gold = author's label in 92.6%.
  - 1.8% have no gold label (marked `-`) and "should not be used in standard evaluations".
- **Splits (§2.2, Table 3)**:
  - **Train 392,702**.
  - **Dev 20,000**: 2,000 per genre, i.e. 10k matched + 10k mismatched.
  - **Test 20,000**: labels are not distributed; it is evaluated through Kaggle.
  - No premise sentence appears in more than one split.
- **Lengths**: mean premise 22.3 tokens (max 401 words); hypotheses up to 70 words.
- **Licence (§2.2)**: "freely available ... for typical machine learning uses, and may be modified and redistributed". **Most of it is under the OANC licence (permissive).** Fiction pieces are under CC BY-SA 3.0 (*Seven Swords*) or CC BY 3.0 (*Living History*, *Password Incorrect*), and the rest are public domain in the US.

## Key results (2018 baselines, Table 4)
- ESIM trained on MNLI: **72.3 matched / 72.1 mismatched** test accuracy. CBOW about 65, BiLSTM about 67. The same models score 15 or more points higher on SNLI.
- Later context, from [[Nie 2020 - Adversarial NLI]]: RoBERTa reaches about 91 on the MNLI dev set.

## Relevance to GroundOne
- **Label mapping**: ENTAILMENT → supported; NEUTRAL and CONTRADICTION → unsupported. Drop `-` gold labels. The result is about 1:2 supported:unsupported.
- **Licence is the clearest of the candidate datasets**: permissive, and modification and redistribution are allowed (with CC BY-SA share-alike for one fiction work).
- **Format caveat**: premises are *single sentences* (mean 22 tokens). This is very different from RAG contexts of hundreds of words. [[AlignScore]] found that removing NLI data (MNLI among it) *improved* its metric, and attributed this to short premises ([[Zha 2023 - AlignScore]], Fig. 5). [[MiniCheck]] used ANLI rather than MNLI. Expect MNLI to help mainly as a warm-up or auxiliary source.
- **Evaluation**: since test labels are not released, use **dev-matched / dev-mismatched** for any in-domain NLI sanity check. That is common practice, not a recommendation from the source.

## Links
- Concepts: [[Natural Language Inference]], [[Groundedness Verification]], [[AlignScore]], [[MiniCheck]]
- Related sources: [[Nie 2020 - Adversarial NLI]], [[Zha 2023 - AlignScore]], [[Tang 2024 - MiniCheck]]
