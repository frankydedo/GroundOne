---
type: source
author: "Shahul Es, Jithin James, Luis Espinosa-Anke, Steven Schockaert"
date: 2024
venue: "EACL 2024 System Demonstrations (venue not printed in the ingested file: arXiv 2309.15217v2)"
url: https://arxiv.org/abs/2309.15217
tags: [source, paper, rag, evaluation, faithfulness, llm-as-a-judge]
---
# Es 2024 - RAGAS: Automated Evaluation of Retrieval Augmented Generation

**Raw file**: `raw/Es 2024 - RAGAS_ingested.pdf` · Code: https://github.com/explodinggradients/ragas

## Overview
Ragas is a **reference-free** framework for evaluating RAG pipelines by prompting an LLM (all experiments use `gpt-3.5-turbo-16k`, §3 p.3). It defines three quality dimensions (§3):
- **Faithfulness**: the claims in the answer can be inferred from the retrieved context.
- **Answer relevance**: the answer addresses the question (does not judge factuality).
- **Context relevance**: the retrieved context is focused, with little irrelevant content.

It is integrated with llama-index and LangChain (§1 p.2). The authors also release **WikiEval**, 50 Wikipedia pages on post-2022 events, with question/context/answer triples and human pairwise judgements (§4).

## Key Insights
1. **Faithfulness algorithm (two LLM calls, §3 p.3)**:
   1. *Statement extraction*: the LLM decomposes each answer sentence into shorter, focused statements S(a_s(q)).
   2. *Verification*: a second prompt asks the LLM to decide, for each statement, whether it is supported by the context, giving "a brief explanation for each statement before arriving at the verdict (Yes/No)".
   3. Score **F = |V| / |S|**, the fraction of statements judged supported.
2. **Answer relevance** = mean cosine similarity between the original question and n questions the LLM regenerates from the answer, using `text-embedding-ada-002` embeddings (Eq. 1, p.3).
3. **Context relevance** = (# sentences the LLM extracts as needed) / (# sentences in context) (Eq. 2, p.4).
4. **Measured agreement with humans on WikiEval** (pairwise accuracy, Table 1 p.5): Ragas 0.95 / 0.78 / 0.70 (faithfulness / answer rel. / context rel.), vs a direct 0–10 "GPT Score" 0.72 / 0.52 / 0.63 and a "GPT Ranking" pairwise prompt 0.54 / 0.40 / 0.52. Decomposing into statements beats asking the LLM for a holistic score.
5. **Human inter-annotator agreement** on WikiEval: ~95% for faithfulness and context relevance, ~90% for answer relevance (two annotators, §4 p.4).
6. **WikiEval faithfulness pairs are easy by construction**: the "unfaithful" answer is ChatGPT answering *without* context (§4 p.4), so the 0.95 figure measures distinguishing context-grounded vs closed-book answers, not subtle sentence-level errors.
7. **Known LLM-judge issues noted in related work (§2)**: holistic scoring prompts are "sensitive to the design of the prompt"; pairwise selection is affected by answer order (citing Wang et al. 2023b). ChatGPT "often struggles" to select crucial sentences in long contexts (§5 p.5).
8. **Not stated**: cost, latency, token counts, calibration of scores, or results on any standard hallucination benchmark. Small evaluation set (50 pages).

## Relevance to GroundOne
- **How faithfulness is judged**: decompose answer into claims, then a generative LLM gives a Yes/No verdict per claim *after writing an explanation*. GroundOne does the same unit-level decision (per sentence) but as a **single forward pass with logit readout** of the answer letter, without the explanation step. Ragas' verification step is effectively the System Two version of GroundOne's task ([[When System One Beats an LLM]]).
- **Cost/latency of LLM judges**: Ragas faithfulness needs at least 2 generative calls per answer (extraction + verification with rationale), each producing many output tokens; this decode-heavy cost is what a readout model avoids ([[Prefill and Decode]], [[KV Cache]]). The paper itself gives no cost/latency numbers.
- **Biases**: depends on a proprietary API model (reproducibility, data privacy), prompt sensitivity (§2). Not suitable for an on-device RAG demo.
- **Baseline role**: Ragas faithfulness is a natural "generative LLM judge" baseline for the thesis; its score is a ratio, not a calibrated probability ([[Calibration]]).
- ARES later reports that Ragas ranks RAG systems less accurately than fine-tuned judges ([[Saad-Falcon 2024 - ARES]]).

## Links
- Concepts: [[RAG Evaluation Frameworks]], [[LLM-as-a-Judge]], [[Retrieval-Augmented Generation]], [[Groundedness Verification]], [[Hallucination Detection]], [[Calibration]]
- Related sources: [[Saad-Falcon 2024 - ARES]], [[Zheng 2023 - Judging LLM-as-a-Judge]], [[Lewis 2020 - Retrieval-Augmented Generation]]
