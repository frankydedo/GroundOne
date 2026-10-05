---
type: source
author: "Nelson F. Liu, Tianyi Zhang, Percy Liang"
date: 2023
venue: "Findings of EMNLP 2023, pp. 7001–7025"
url: https://arxiv.org/abs/2304.09848
tags: [source, paper, dataset, generative-search, citation, attribution, rag, llm-aggrefact]
---
# Liu 2023 - Evaluating Verifiability in Generative Search Engines

**Raw file**: `raw/Liu 2023 - Evaluating Verifiability in Generative Search Engines (ClaimVerify)_ingested.pdf`
**Data**: github.com/nelson-liu/evaluating-verifiability-in-generative-search-engines

This paper is a human audit of four commercial **generative search engines**: **Bing Chat, NeevaAI, perplexity.ai and YouChat**, scraped between late February and late March 2023. It measures fluency, perceived utility, **citation recall** and **citation precision**. Its sentence-level support judgements are the **ClaimVerify** sub-dataset of [[LLM-AggreFact]]. "ClaimVerify" is LLM-AggreFact's name for it, not the paper's.

## Overview
- **Queries (§3.2)**: 1,450 per system, from 12 distributions:
  - AllSouls essay questions, davinci-debate topics, ELI5 (KILT and Live), WikiHowKeywords (paraphrased by text-davinci-003);
  - 7 NaturalQuestions subdistributions.
- **Unit**: the response is segmented into **sentences**. Each sentence's in-line citations point to **webpages**.
- **Judgements (§2.3–2.4)**:
  1. Annotators remove statements that are not verification-worthy, e.g. "As a language model…" or questions to the user.
  2. For each remaining sentence they give a binary judgement: is it **fully supported by the union of its cited webpages**? This uses AIS: a generic hearer would affirm "According to cited webpages C_i, s_i", read within the context of the query and the response.
  3. For each citation they rate full, partial or no support.
- **Annotators (§3.3)**: **34 MTurk workers** who passed a qualification with individual feedback. Each pair is annotated **once**. Pay: $1.00 per query–response pair with citations, about $15/h.
- **Agreement**: 250 pairs were triple-annotated, giving **>82.0% pairwise agreement and 91.0 F1** on all judgements (App. E).

## Key results
- On average only **51.5%** of generated sentences are fully supported by their citations (citation recall), and **74.5%** of citations support their sentence (citation precision).
- Per system, recall ranges from 68.7 (perplexity.ai) to 11.1 (YouChat).
- Fluency (4.48) and perceived utility (4.50 out of 5) are high. **Citation precision is inversely correlated with perceived utility (r = −0.96)**. The authors hypothesize that systems that copy closely from sources cite more accurately but are judged less useful.

## How it appears in LLM-AggreFact
- **Claim** = one sentence of a generative-search answer. **Document** = the content of its cited webpage(s). The binary "fully supported" label is kept as it is (MiniCheck App. C.2).
- **Label balance (our EDA, test)**: **72.5% supported**, against 51.5% citation recall in the paper. A plausible but unverified explanation is that LLM-AggreFact keeps only cited sentences: uncited verification-worthy sentences count as unsupported in citation recall but have no document to pair with.
- **Length (our EDA)**: median **1,368** and p90 **4,743** Qwen tokens. This is the longest tail in LLM-AggreFact, because whole webpages are concatenated.
- Original splits are kept: dev 1,093, test 1,088.

## Caveats
- Single annotation per item. Agreement was checked on only a 250-pair subset.
- The annotator judged the sentence **in the context of the query and response**, but LLM-AggreFact gives the verifier only (document, sentence). Sentences with pronouns or ellipsis may be under-specified.
- Webpages from early-2023 scrapes contain navigation and boilerplate noise.

## Relevance to GroundOne
- It is the closest **retrieve-then-generate** setting in the benchmark after RAGTruth: production LLM systems answering over retrieved web documents, judged per sentence. This is structurally the local-RAG use case.
- It is the main **length stress test**: a large share of the documents exceed a 2,048-token cap, so the truncation or chunking policy will directly move this score.

## Links
[[LLM-AggreFact]], [[LLM-AggreFact Sub-datasets]], [[Retrieval-Augmented Generation]], [[Groundedness Verification]], [[Hallucination Detection]], [[Malaviya 2024 - ExpertQA]], [[Chen 2024 - Understanding Retrieval Augmentation for LFQA]], [[GroundOne]]
