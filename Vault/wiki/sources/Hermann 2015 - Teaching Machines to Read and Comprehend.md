---
type: source
author: "Karl Moritz Hermann, Tomáš Kočiský, Edward Grefenstette, Lasse Espeholt, Will Kay, Mustafa Suleyman, Phil Blunsom (Google DeepMind, University of Oxford)"
date: 2015
venue: "NIPS 2015 (venue not printed on the PDF's first page)"
url: https://arxiv.org/abs/1506.03340
tags: [source, paper, dataset, cnn-dailymail, reading-comprehension, news, ragtruth-upstream]
---
# Hermann 2015 - Teaching Machines to Read and Comprehend

**Raw file**: `raw/Hermann 2015 - Teaching Machines to Read and Comprehend_ingested.pdf`.

## Overview
The paper that created the **CNN/Daily Mail** corpus: news articles paired with their bullet-point highlights, turned into cloze-style reading-comprehension questions. The same article–highlight pairs later became the standard CNN/DM summarisation dataset ([[See 2017 - Get To The Point]]), which is one of the sources of the Summary task in [[RAGTruth]].

## Key Insights (as stated by the authors)
- **Collection**: 93k CNN and 220k Daily Mail articles; CNN from April 2007, Daily Mail from June 2010, both to end of April 2015. Validation = March 2015, test = April 2015. Articles over 2,000 tokens were filtered out.
- **Construction**: the highlights are abstractive summaries; each bullet becomes a cloze query by replacing one entity with a placeholder. About 1M data points in total.
- **Table 1**: CNN 90,266 / 1,220 / 1,093 documents (train/valid/test), 380,298 / 3,924 / 3,198 queries, ~762 tokens per document; Daily Mail 196,961 / 12,148 / 10,397 documents, 879,450 / 64,835 / 53,182 queries, ~813 tokens.
- **Anonymisation**: entities are replaced by coreference-based abstract markers (`ent381`), randomly permuted per example, so a model must use the document and cannot rely on world knowledge.
- **Results (Table 5, test accuracy CNN / DM)**: Attentive Reader 63.0 / 69.0, Impatient Reader 63.8 / 68.0, Deep LSTM 57.0 / 62.2, word-distance 50.9 / 55.5.
- Code to rebuild the data: `github.com/deepmind/rc-data`.

## Relevance to GroundOne
- Origin of the CNN/DM news articles that RAGTruth uses as Summary contexts (with recent news added). RAGTruth's sample shows raw, non-anonymised text ([[Dataset card - RAGTruth README]]).
- The anonymisation idea is the same concern GroundOne has: the verifier must judge against the **context**, not world knowledge (strict rule vs `implicit_true`).
- CNN/DM articles are also the source of [[LLM-AggreFact]]'s AggreFact-CNN sub-dataset (summaries from fine-tuned summarisers; see [[LLM-AggreFact Sub-datasets]]).

## Links
[[RAGTruth]], [[See 2017 - Get To The Point]], [[Dataset card - RAGTruth README]], [[Datasets for GroundOne]], [[LLM-AggreFact]]
