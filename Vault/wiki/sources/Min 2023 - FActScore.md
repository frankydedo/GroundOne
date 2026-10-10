---
type: source
author: "Sewon Min, Kalpesh Krishna, Xinxi Lyu, Mike Lewis, Wen-tau Yih, Pang Wei Koh, Mohit Iyyer, Luke Zettlemoyer, Hannaneh Hajishirzi"
date: 2023
venue: "EMNLP 2023 (arXiv 2305.14251)"
url: "https://arxiv.org/abs/2305.14251"
tags: [source, paper, factuality, atomic-facts, long-form, evaluation, retrieval, hallucination]
---
# Min 2023 – FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long Form Text Generation

**Raw file**: `raw/Min 2023 - FActScore_ingested.pdf`

## Overview
FActScore evaluates the **factual precision of long-form generations** by breaking a generation into **atomic facts** (short sentences that each carry one piece of information) and computing the **fraction supported by a given knowledge source** (abstract, §3.1). The authors annotate people biographies from InstructGPT, ChatGPT and the search-augmented PerplexityAI against English Wikipedia, then build an automatic estimator (retrieval + an LM judge) with **less than 2% error**, and use it to score 6,500 generations from 13 LMs that would have cost about $26K to annotate by hand (abstract, §4).

## Key Insights
1. **Atomic fact as the unit (§3.1).** A sentence often mixes supported and unsupported information: ChatGPT sentences carry 4.4 facts on average and 40% mix supported and unsupported ones (footnote 2). A sentence-level label must therefore be either "partial support" (subjective, low agreement) or strict "all must be supported", which scores both generations in Fig. 1 as 0 although one is far more accurate.
2. **Support relative to a knowledge source (§3.1).** Truth is defined as support by a chosen trusted source C, not global truth. FActScore(M) = E_x[ (1/|A_y|) Σ_a 1[a supported by C] ] over responding prompts. Assumptions: support is undebatable, facts weigh equally, the source is self-consistent. It measures **precision only**, not recall.
3. **Human results (§3.4, Table 1).** FActScores of **42.5% (InstructGPT), 58.3% (ChatGPT), 71.5% (PerplexityAI)**. Annotators labelled facts Supported / Not-supported / Irrelevant at about $4 per generation, with 88–96% agreement. Precision drops for rarer entities (ChatGPT 80% → 16%) and for facts later in the generation (Fig. 2).
4. **Retrieval does not guarantee faithfulness (§3.4, Table 2).** PerplexityAI's errors include single-sentence contradictions (33%) and page-level contradictions (23%); its citations hardly correlate with precision (36.0% of supported vs 37.6% of unsupported sentences carry citations).
5. **Automatic estimator (§4.1).** Variants: No-context LM, **Retrieve→LM** (retrieve k passages, ask "True or False?"), nonparametric probability (NP), and the Retrieve→LM + NP ensemble. The verdict is made by **comparing the conditional probabilities of "True" and "False"** when logits are available, and by parsing the generated text otherwise (ChatGPT).
6. **Estimator findings (§4.2, Table 3).** Retrieval is essential; Retrieve→LM alone can overestimate FActScore by up to 17%; the ensemble with NP reduces error. ChatGPT is not always the best evaluator.

## Relevance to GroundOne
- **Granularity choice.** FActScore argues for atomic facts; GroundOne uses **sentences** (pysbd segmentation plus a checkable-content rule). The thesis should cite both sides: FActScore shows sentences can mix supported and unsupported content, while [[Tang 2024 - MiniCheck|MiniCheck]] (§7.1) found no consistent gain from atomic decomposition at 2–4× the cost. GroundOne's three-way verdict per sentence partly absorbs mixed sentences: a sentence with one unsupported detail is not "supported" ([[Groundedness Verification]]).
- **Same notion of truth.** "Supported by a given knowledge source" is exactly GroundOne's groundedness: support by the retrieved document, regardless of world truth ([[Hallucination Detection]]).
- **Logit readout as a judge.** FActScore's evaluator reads P(True) vs P(False) from an LM after the evidence: a binary, zero-shot ancestor of GroundOne's restricted A/B/C readout. GroundOne adds fine-tuning on the decision, a third class and all K verdicts in one pass ([[System One Models]]).
- **Cost argument.** Human checking costs $4 per generation and an API-judge pipeline still decodes per fact; a local single-pass verifier makes per-sentence checking cheap enough to run on every answer ([[On-Device Inference]]).
- **Not the same task.** FActScore verifies against Wikipedia retrieved after generation (factuality); GroundOne verifies against the document the generator was given (faithfulness).

## Links
- Concepts: [[Groundedness Verification]], [[Hallucination Detection]], [[LLM-as-a-Judge]], [[Retrieval-Augmented Generation]], [[System One Models]]
- Related sources: [[Laban 2022 - SummaC]], [[Huang 2023 - A Survey on Hallucination in LLMs]], [[Tang 2024 - MiniCheck]], [[Wang 2024 - Factcheck-Bench]], [[Kamoi 2023 - WiCE]], [[Kadavath 2022 - Language Models (Mostly) Know What They Know]], [[Liu 2023 - Evaluating Verifiability in Generative Search Engines]]
