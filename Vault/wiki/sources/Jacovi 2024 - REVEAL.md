---
type: source
author: "Alon Jacovi, Yonatan Bitton, Bernd Bohnet, Jonathan Herzig, Or Honovich, Michael Tseng, Michael Collins, Roee Aharoni, Mor Geva"
date: 2024
venue: "ACL 2024 (Long Papers), pp. 4615–4634"
url: https://arxiv.org/abs/2402.00559
tags: [source, paper, dataset, benchmark, chain-of-thought, attribution, reasoning-verification, llm-aggrefact]
---
# Jacovi 2024 - REVEAL

**Raw file**: `raw/Jacovi 2024 - REVEAL (A Chain-of-Thought Is as Strong as Its Weakest Link)_ingested.pdf`
**Data**: huggingface.co/datasets/google/reveal. The authors ask users to respect their anti-contamination constraints.

REVEAL (**Re**asoning **Ve**rification **E**valu**a**tion) is a benchmark for verifiers of **chain-of-thought (CoT)** answers. Each step is labelled for relevance, type (attribution / logical / both), **attribution to retrieved Wikipedia paragraphs**, and logical correctness. Its attribution step–evidence pairs are the **Reveal** sub-dataset of [[LLM-AggreFact]].

## Overview
- **Questions (§4)**: 704 questions in REVEAL-Eval, drawn evenly from **StrategyQA, MuSiQue (2-hop), Sports Understanding (BIG-bench) and Fermi**.
- **CoT generators**: **Flan-PaLM-540B, GPT-3 (text-davinci-003), Flan-UL2-20B**, with few-shot in-domain CoT prompts. REVEAL-Eval has 1,002 CoT answers and 3,360 steps.
- **Evidence retrieval (Step 2)**: for each attribution step, 3 Wikipedia paragraphs: 2 from GTR (dense) and 1 from BM25. The queries are **decontextualized** versions of the step. Annotation of a step stops at the first paragraph that supports or contradicts it.
- **Attribution labels (§2)**: *fully attributable* ("strictly according to the given source, all of the information in the claim is correct"), *partially attributable*, *contradictory*, *unsupported*. This follows AIS (Rashkin et al.).
- **Annotators (§4)**: a pool of **13 English-speaking annotators, 5 annotations per item**, each with a free-text justification. About 5% of the labels were filled in by the authors.
- **Agreement (§5)**: **Krippendorff's α = 0.49** (attribution) and **0.46** (logic).
  - CoTs with any step where fewer than 3 of 5 annotators agree go to **REVEAL-Open** (18% of CoTs). That subset is not used for evaluation.
  - **REVEAL-Eval** keeps the high-agreement items.
- **Statistics (Table 1, Fig. 5)**:
  - REVEAL-Eval has **3,502 step–evidence pairs**, with an average evidence length of **103 words**.
  - Pair labels: 24.7% fully attributable, 65.4% unsupported, 6.5% contradictory, 3.4% partial.
  - Step level: 43.8% of attribution steps are fully attributable.

## Key insights
- Attribution is the main failure point of CoT answers: 77.3% of CoTs have a step that is not fully attributable, while 18.5% have a logically incorrect step.
- **"Unsupported" is often a retrieval failure**. In a manual study of 40 unsupported steps (§5.1), only 19 were factually wrong. Of the other 21, 13 needed extra world knowledge or reasoning and 6 had irrelevant evidence. The authors estimate that **about half of the unsupported cases come from imperfect retrieval**.
- Verifiers struggle most with logical-correctness steps.

## How it appears in LLM-AggreFact
- **Claim** = one CoT step, a single sentence. **Document** = one retrieved Wikipedia paragraph of about 100 words. Our EDA gives a median of 112 and p90 of 223 Qwen tokens.
- **Label mapping**: only *fully attributable* is supported (MiniCheck App. C.2). Our EDA test gives **23.4% supported**, which matches the 24.7% pair-level rate.
- The split is 50/50 dev/test (1,656 / 1,710) with no question shared between them (MiniCheck §4.1).

## Caveats
- Many negatives are **true claims paired with an unhelpful paragraph**. The label measures grounding in *this* paragraph, not truth. A verifier that uses parametric knowledge will be penalized, which is correct for groundedness but should be understood when reading results.
- Agreement is only moderate (α ≈ 0.49), even after the low-agreement items were removed.
- The domain is open-domain trivia and estimation questions with very short contexts. It is not RAG answers.

## Relevance to GroundOne
- It is a clean **short-context** test of strict grounding: the model must refuse support when the paragraph is merely on-topic. This failure mode matters in local RAG, where retrieved chunks are topically related but lack the specific fact.
- The very low supported rate (23%) is the mirror image of RAGTruth (92%). A single global threshold must work on both, which is why the macro balanced accuracy is informative.

## Links
[[LLM-AggreFact]], [[LLM-AggreFact Sub-datasets]], [[Groundedness Verification]], [[Natural Language Inference]], [[Retrieval-Augmented Generation]], [[Tang 2024 - MiniCheck]], [[GroundOne]]
