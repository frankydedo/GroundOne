---
type: source
author: "Abigail See, Peter J. Liu, Christopher D. Manning (Stanford University, Google Brain)"
date: 2017
venue: "ACL 2017 (Proceedings of the 55th Annual Meeting of the ACL, pp. 1073–1083, Vancouver)"
url: https://arxiv.org/abs/1704.04368
tags: [source, paper, summarization, cnn-dailymail, pointer-generator, ragtruth-upstream]
---
# See 2017 - Get To The Point

**Raw file**: `raw/See 2017 - Get To The Point (Pointer-Generator, CNN-DM non-anonymized)_ingested.pdf`.

## Overview
Introduces the **pointer-generator network with coverage** for abstractive summarisation and, importantly for us, establishes the **non-anonymised CNN/Daily Mail** summarisation setup that later work (including [[RAGTruth]]'s Summary task and AggreFact-CNN) builds on.

## Key Insights (as stated by the authors)
- **Dataset (§4)**: CNN/DM ([[Hermann 2015 - Teaching Machines to Read and Comprehend]], Nallapati et al. 2016): articles average **781 tokens**, summaries **3.75 sentences / 56 tokens**. Split: **287,226 train / 13,368 validation / 11,490 test** pairs.
- They use the **original text (non-anonymised)**, unlike prior published results on the anonymised version, arguing it is the more favourable problem because it needs no pre-processing. Scripts at `github.com/abisee/pointer-generator`.
- **Model**: a hybrid that can copy source words via a pointer or generate from the vocabulary (soft switch p_gen), plus a coverage vector (sum of past attention) with a coverage loss to stop repetition. Training truncates articles to 400 tokens and summaries to 100 (120 at test).
- **Results (Table 1, test ROUGE-1/2/L)**: pointer-generator + coverage 39.53 / 17.28 / 36.38; lead-3 baseline 40.34 / 17.70 / 36.57. Lead-3 stays ahead.
- **Observations**: the baseline seq2seq reproduces factual details inaccurately (e.g. "destabilize" for "thwart"), fabricates phrases and repeats itself. The final model copies whole article sentences 35 % of the time vs 1.3 % for reference summaries.

## Relevance to GroundOne
- Provenance of the CNN/DM summarisation data behind RAGTruth Summary contexts; the raw (non-anonymised) text in RAGTruth matches this setup (our observation from the README sample, not stated by RAGTruth).
- An early documented case of the error GroundOne must catch: fluent summaries with wrong factual details. Highly extractive generators (35 % copied sentences) also explain why many summary sentences are easy "supported" cases.

## Links
[[Hermann 2015 - Teaching Machines to Read and Comprehend]], [[RAGTruth]], [[Dataset card - RAGTruth README]], [[Datasets for GroundOne]], [[Hallucination Detection]]
