---
type: source
author: "Tri Nguyen, Mir Rosenberg, Xia Song, Jianfeng Gao, Saurabh Tiwary, Rangan Majumder, Li Deng (Microsoft AI & Research)"
date: 2016
venue: "arXiv:1611.09268v1 (28 Nov 2016); footer: NIPS 2016, Barcelona"
url: https://arxiv.org/abs/1611.09268
tags: [source, paper, dataset, reading-comprehension, qa, web-search, ragtruth-upstream]
---
# Nguyen 2016 - MS MARCO

**Raw file**: `raw/Nguyen 2016 - MS MARCO_ingested.pdf` (first release paper, v1).

## Overview
**MS MARCO** (MAchine Reading COmprehension) is a large question-answering dataset built from **real anonymized Bing/Cortana user queries**, with context passages extracted from real web documents and **human-written answers**. It is the upstream source of the QA task in [[RAGTruth]], whose QA contexts are MS MARCO questions with 3 retrieved passages.

## Key Insights (as stated by the authors)
- **Release described**: 100,000 queries, 1M passages, links to 200K+ documents; the stated goal was one million queries.
- **Per query**: about 10 passages extracted from top-ranked web documents by a separate IR system; one or more human answers synthesised from the passages; a query-type tag (description, numeric, entity, person, location) from an SVM classifier with 90.31 % test accuracy.
- Queries were filtered to answer-seeking intent; the paper states both that the set was pruned to queries judges could answer **and** that a subset of unanswerable queries is included (the two statements sit side by side in the paper).
- **Query distribution**: 42.2 % contain "what", 15.3 % "how"; answer types: description 52.6 %, numeric 28.4 %, entity 10.5 %, location 5.7 %, person 2.7 % (Tables 3–4).
- Real queries are messy (typos, abbreviations) and web text can be noisy or conflicting across documents; answers may need multi-passage reasoning.
- **Baselines (Table 5, ROUGE-L, subset)**: best passage 0.351, DSSM-like ranking 0.177, seq2seq 0.089, memory network 0.119.
- **Licence**: not stated in the paper (dataset at msmarco.org).

## Relevance to GroundOne
- RAGTruth QA = MS MARCO questions + retrieved web passages, so it is the closest dataset to the GroundOne demo (a local RAG chat over retrieved passages; experiment X7 in [[Datasets for GroundOne]]).
- Because passages "may or may not be enough to answer the question", generators often add unsupported content; RAGTruth QA's hallucinations are mostly baseless rather than contradictory (only 0.5 % of QA test sentences are contradicted, [[GroundOne 2026 - EDA report]]).

## Links
[[RAGTruth]], [[Dataset card - RAGTruth README]], [[Datasets for GroundOne]], [[Retrieval-Augmented Generation]]
