---
type: source
author: "Liyan Tang, Tanya Goyal, Alexander R. Fabbri, Philippe Laban, Jiacheng Xu, Semih Yavuz, Wojciech Kryściński, Justin F. Rousseau, Greg Durrett"
date: 2023
venue: "ACL 2023 (Long Papers), pp. 11626–11644"
url: https://arxiv.org/abs/2205.12854
tags: [source, paper, dataset, benchmark, summarization, factual-consistency, llm-aggrefact]
---
# Tang 2023 - AggreFact

**Raw file**: `raw/Tang 2023 - Understanding Factual Errors in Summarization (AggreFact)_ingested.pdf`
**Code/data**: github.com/Liyan06/AggreFact

"Understanding Factual Errors in Summarization: Errors, Summarizers, Datasets, Error Detectors". The paper builds **AggreFact**, a benchmark that aggregates nine existing human-annotated factual-consistency datasets for news summarization and stratifies them by the age of the summarizer. Its **FtSota** subsets (summaries from fine-tuned BART, PEGASUS and T5) are the **AggreFact-CNN** and **AggreFact-XSum** sub-datasets of [[LLM-AggreFact]].

## Overview
- **Base data (§2.2, Table 1)**: built on SummaC (Laban et al. 2022). It takes XSumFaith, FactCC, SummEval, FRANK and Polytope from SummaC and adds Wang'20, CLIFF, Goyal'21 and Cao'22. CoGenSumm is excluded because it is a ranking task.
- **Documents**: news articles from **CNN/DailyMail** and **XSum (BBC)**. The two subsets are kept separate because the summary styles differ: CNN/DM summaries are near-extractive and multi-sentence, while XSum summaries are a single highly abstractive sentence.
- **Summarizer strata (§2.1)**:
  - **Old**: pre-Transformer models such as Pointer-Generator and BottomUp.
  - **ExFormer**: early Transformers such as BERTSum and GPT-2.
  - **FtSota**: fine-tuned **BART, PEGASUS, T5**.
- **Labels**: binary consistent/inconsistent, "determined by human evaluations on the annotated datasets" (§2.1), so they are inherited from the source datasets and their different schemes:
  - Annotation granularity varies: summary-, sentence-, span-, entity- or word-level.
  - Polytope summaries flagged only with addition, omission or duplication errors are relabelled *consistent*, because those errors are not about factuality.
- **Annotators and agreement (Table 1)** are heterogeneous across the source datasets:
  - Wang'20: 3 crowd workers, κ 0.34/0.51.
  - CLIFF: 2 experts, κ 0.35/0.45.
  - Cao'22: 2 authors and 3 graduate students, κ 0.81.
  - Goyal'21: 2 authors, κ not reported.
- **Cleaning (§2.2)**: duplicates were removed. **100 instances** had conflicting labels across source datasets (98 between FRANK and XSumFaith). The authors corrected these by hand.
- **Metric**: balanced accuracy, with thresholds tuned on the validation split (§2.3). The FtSota benchmark (§3, Table 4) uses a **single threshold** per metric.

## Key insights
- Most annotated summaries come from **Old** models. Factuality metrics lose roughly **10 BAcc points on average** going from Old to FtSota on CNN/DM (§3). Gains reported on the category-agnostic SummaC therefore come mostly from easy, old-model errors.
- No metric wins on both CNN/DM and XSum FtSota (Table 4). Under the single threshold, QuestEval is best on CNN-FtSota and DAE on XSum-FtSota. ChatGPT-based metrics (zero-shot, CoT, DA, Star) are not better.
- Error-type distributions differ between datasets, even for the same summarizer (§4). The error-type boundaries in the source datasets are not consistent.

## FtSota split sizes (Tables 6–7)
| Subset | Source datasets (test count) | Val | Test |
|---|---|---|---|
| AggreFact-CNN-FtSota | Polytope 34, SummEval 200, FRANK 175, CLIFF 150 | 459 | **559** |
| AggreFact-XSum-FtSota | Wang'20 119, CLIFF 150, Goyal'21 50, Cao'22 239 | 777 | **558** |

LLM-AggreFact reports 558 test items for CNN, one fewer than Table 6. The difference is not explained in either source.

## How it appears in LLM-AggreFact
- **AggreFact-CNN** and **AggreFact-XSum** are the FtSota validation and test splits, used as they are. The binary labels are kept (MiniCheck App. C.2).
- **Claim** = the *whole summary*, not a single sentence. CNN/DM summaries are multi-sentence. The XSum summary is one sentence.
- **Claim author**: fine-tuned seq2seq summarizers (BART, PEGASUS, T5), **not** instruction-tuned LLMs.
- **"Supported"** = the summary is factually consistent with the article under the scheme of its source dataset.
- **Label balance (our EDA, test)**: CNN is **89.8% supported** and XSum **51.1% supported**.

## Caveats
- The labels come from 8 datasets with different guidelines, granularities and agreement levels, some of them low (κ ≈ 0.35). Treat them as noisy.
- CNN is very imbalanced (about 10% unsupported), so its balanced accuracy is driven by about 57 negatives. Expect high variance.
- The summarizers are pre-LLM and the documents are news. This is far from local-RAG answers.

## Relevance to GroundOne
- These two sub-datasets test **summary-level** consistency of news summaries. A sentence-level verifier needs an aggregation rule for multi-sentence CNN summaries, or must accept the whole summary as one claim.
- XSum's extrinsic hallucinations (facts plausible from world knowledge but absent from the article) are a good probe for whether GroundOne flags **unsupported-but-true** content, which it should under a strict grounding definition.

## Links
[[LLM-AggreFact]], [[LLM-AggreFact Sub-datasets]], [[Groundedness Verification]], [[Hallucination Detection]], [[Natural Language Inference]], [[Tang 2024 - MiniCheck]], [[Tang 2024 - TofuEval]], [[GroundOne]]
