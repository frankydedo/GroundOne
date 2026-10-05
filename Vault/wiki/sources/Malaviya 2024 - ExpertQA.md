---
type: source
author: "Chaitanya Malaviya, Subin Lee, Sihao Chen, Elizabeth Sieber, Mark Yatskar, Dan Roth"
date: 2024
venue: "NAACL 2024 (Long Papers), pp. 3025–3045"
url: https://arxiv.org/abs/2309.07852
tags: [source, paper, dataset, long-form-qa, attribution, expert-annotation, rag, llm-aggrefact]
---
# Malaviya 2024 - ExpertQA

**Raw file**: `raw/Malaviya 2024 - ExpertQA_ingested.pdf`
**Code/data**: github.com/chaitanyamalaviya/ExpertQA

ExpertQA collects **2,177 information-seeking questions written by domain experts in 32 fields**. Answers come from six attributed-QA systems, and **the same experts** judge each answer sentence ("claim") for attribution, factuality, informativeness, cite-worthiness and source reliability. The claim–evidence attribution judgements are the **ExpertQA** sub-dataset of [[LLM-AggreFact]].

## Overview
- **Experts (§2.1)**: recruited on Prolific, with formal education and at least 3 years of work experience in the field. 484 participants appear in the abstract and 524 experts in §2.1. Each wrote 5 questions, at least 2 of them scenario-based.
- **Fields**: 32. The largest share are high-stakes fields such as medicine and law (Fig. 2).
- **Systems (§3, Table 4)** produce six kinds of response:
  - **gpt4**: closed-book, with URLs generated from memory.
  - **bing_chat**: balanced mode.
  - **rr_sphere_gpt4 / rr_gs_gpt4**: retrieve-and-read with GPT-4 over Sphere (BM25) or Google search.
  - **post_hoc_sphere_gpt4 / post_hoc_gs_gpt4**: GPT-4 answers first, then evidence is retrieved for each claim.
- **Claims**: answer sentences from the spaCy splitter. At most 10 claims per answer, 5.79 on average.
- **Attribution label (Table 3)**: "Is the claim supported by its accompanying evidence?", one of **Complete / Partial or Incomplete / Missing / N/A (broken link)**. Experts then revise the claims.
- **Label reliability (§4.2)**: each claim is judged **once, by the expert who asked the question**. No inter-annotator coefficient is reported. Instead, the authors checked their own agreement with the reference labels on 60 Engineering and 60 Medicine questions and found **>85% agreement for most labels**.

## Key insights
- **Retrieve-and-read** gives the most complete attributions but leaves about 18% of cite-worthy claims uncited. **Post-hoc retrieval** cites every claim but more often incompletely. Closed-book gpt4 URLs point to mismatched content more than 60% of the time (§4.3).
- In medicine and law, about 35% and 31% of claims respectively have incomplete attribution. About 51% of medical claims cite sources that are not rated reliable.
- **AutoAIS** (the TRUE NLI model) has **high precision (0.88) but low recall (0.38)** against the expert labels. Fine-tuning on ExpertQA raises F1 from 0.53 to 0.86 (Table 6).
  - The NLI model needs every part of the claim to be verifiable from the evidence.
  - The experts, by contrast, apply **implicit world knowledge** (e.g. that calcium carbonate is an alkali) and **combine multiple evidences** (Table 7).

## How it appears in LLM-AggreFact
- **Claim** = one answer sentence. **Document** = the evidence attached to it, either a retrieved passage or webpage text. Our EDA gives a median of 185 and p90 of 1,138 Qwen tokens.
- **Label mapping**: only *Complete* is supported (MiniCheck App. C.2). Our EDA test gives **80.3% supported**.
- The split is 50/50 dev/test (3,773 / 3,702) with no question shared between them (MiniCheck §4.1).

## Caveats
- **This is the sub-dataset where every model scores lowest.** The LLM-AggreFact leaderboard ceiling is about 50–61 BAcc for every model ([[LLM-AggreFact]]).
- The paper's own analysis suggests why: the expert labels allow background knowledge and multi-source synthesis that a strict document-only verifier cannot reproduce, and each item has a single annotator. Part of the ceiling is probably **label noise or definition mismatch**, not model weakness.
- Post-hoc systems attach evidence after generation, so the claims were not written *from* the document. Read the "unsupported" labels in that light.

## Relevance to GroundOne
- It is the domain-expert, long-form RAG setting, which is relevant to the thesis motivation. Do not over-interpret small differences between models here.
- For GroundOne, the thesis should report ExpertQA but discuss it as partly measuring agreement with a looser, knowledge-aware notion of support.

## Links
[[LLM-AggreFact]], [[LLM-AggreFact Sub-datasets]], [[Retrieval-Augmented Generation]], [[Groundedness Verification]], [[Natural Language Inference]], [[Liu 2023 - Evaluating Verifiability in Generative Search Engines]], [[Chen 2024 - Understanding Retrieval Augmentation for LFQA]], [[GroundOne]]
