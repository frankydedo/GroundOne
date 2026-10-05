---
type: source
author: "Yuxia Wang, Revanth Gangi Reddy, Zain Muhammad Mujahid, Arnav Arora, Aleksandr Rubashevskii, Jiahui Geng, Osama Mohammed Afzal, Liangming Pan, Nadav Borenstein, Aditya Pillai, Isabelle Augenstein, Iryna Gurevych, Preslav Nakov"
date: 2024
venue: "Findings of EMNLP 2024, pp. 14199–14230"
url: https://arxiv.org/abs/2311.09000
tags: [source, paper, dataset, benchmark, fact-checking, claim-decomposition, stance, llm-aggrefact]
---
# Wang 2024 - Factcheck-Bench

**Raw file**: `raw/Wang 2024 - Factcheck-Bench (FactCheck-GPT)_ingested.pdf`
**Code/data**: github.com/yuxiaw/Factcheck-GPT

Factcheck-Bench is a fine-grained annotation framework and benchmark for fact-checking **ChatGPT responses** in eight steps: decompose, decontextualize, check-worthiness, evidence retrieval, **stance detection**, correction decision, claim correction and response revision. The authors also propose the **Factcheck-GPT** pipeline. The (atomic claim, evidence snippet, stance) triplets are the **FactCheck-GPT** sub-dataset of [[LLM-AggreFact]].

## Overview
- **Responses (§3.1)**: from **ChatGPT (GPT-3.5-Turbo)**. The questions come from user-reported hallucinations posted on Twitter plus in-house brainstorming (45), and from dolly-15k closed and open QA.
  - The data was **selected to be fact-intensive and likely false**: the authors kept examples with automatic FActScore < 0.2.
  - 110 examples were selected and **94 annotated**.
- **Decomposition**: responses are split into sentences, then into **decontextualized atomic claims** (one fact each). Of 678 claims, 661 are check-worthy.
- **Evidence**: for each claim, ChatGPT-generated queries go to **Google search**. Passages are re-ranked (lexical plus Sentence-BERT), and the **top-5 snippets** are kept per claim. This gives **3,305 (claim, evidence, stance) triplets** (Table 1).
- **Stance labels (§2)**:
  - **completely support** (the evidence entails the claim);
  - **partially support**;
  - **refute** (a clear opposite fact about the same event);
  - **irrelevant** (does not mention the fact).
- **Stance distribution (Fig. 2)**: irrelevant 2,057, completely support 696, partially support 391, refute 161.
- **Annotators (§3.2)**: **10 in-house annotators**: MSc and PhD students, postdocs and professors familiar with fact-checking.
  - They work in pairs. Each annotates independently, then the pair consolidates, discussing until consensus.
  - A third rater joins the stance step, and items with no consensus are discarded.
  - **No agreement coefficient is reported.**

## Key insights
- About a quarter of claims (159/661) are factually wrong. For a third (222), the automatic evidence was not enough to decide and manual search was needed. 30 claims remained undetermined (§3.3).
- Automatic retrieval struggles with long-tail facts and with evidence for false-premise claims.
- Factcheck-GPT outperforms popular LLM fact-checkers on the subtasks (§4), although LLMs remain weak at stance detection and correction.

## How it appears in LLM-AggreFact
- **Claim** = one decontextualized **atomic claim**. **Document** = **one** Google evidence snippet. Our EDA gives a median of 117 and p90 of 169 Qwen tokens, the shortest documents in the benchmark together with Reveal.
- **Label mapping**: only *completely support* is supported. Partial, refute and irrelevant are all unsupported (MiniCheck App. C.2). Our EDA test gives **24.0% supported**, consistent with 696/3,305 ≈ 21%.
- The split is 50/50 dev/test (1,537 / 1,566) with no query shared between them (MiniCheck §4.1).

## Caveats
- **Most negatives are "irrelevant" evidence** (about 62% of all triplets). The sub-dataset is largely a test of rejecting off-topic snippets, plus a minority of real contradictions. A true claim paired with an irrelevant snippet is labelled unsupported.
- Claims are atomic and decontextualized by the dataset pipeline, so they are easier to parse than raw RAG sentences.
- The responses were selected to contain errors, so the domain is adversarially chosen open-domain QA.

## Relevance to GroundOne
- It tests the **precision side** of grounding: the verifier must not mark a claim as supported just because the snippet is about the same entity. A model that relies on topical overlap will fail here.
- It is small and short-context and fits any token cap.

## Links
[[LLM-AggreFact]], [[LLM-AggreFact Sub-datasets]], [[Groundedness Verification]], [[Hallucination Detection]], [[Natural Language Inference]], [[Kamoi 2023 - WiCE]], [[GroundOne]]
