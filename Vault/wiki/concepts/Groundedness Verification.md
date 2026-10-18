---
type: concept
tags: [concept, groundedness, faithfulness, rag, evaluation-protocol, groundone]
---
# Groundedness Verification

**Groundedness verification** checks whether each statement in a generated answer is **supported by the retrieved context** that the generator was given. It is the "fact-checking on grounding documents" primitive of [[Tang 2024 - MiniCheck|MiniCheck]], and the core task of [[GroundOne]]. It is the context-faithfulness, sentence-level slice of [[Hallucination Detection]].

## Task definition (current, 2026-10-10)
GroundOne is a **sentence-level groundedness verifier with three classes** (decision D20):
- **Input**: the retrieved document D (with the question) and the generated answer, segmented into sentences c_1..c_K (pysbd plus a checkable-content rule shared by training and inference; sentences without checkable content get no verdict).
- **Output**: for every c_i, P(supported), P(contradicted), P(not mentioned), read from the logits of the letters A/B/C at a " Verdict:" marker after the sentence. All K verdicts come from **one forward pass** per answer, with no generated text ([[System One Models|System One]] readout, [[Prefill and Decode]]).
- **Classes**: *supported* (D entails c_i), *contradicted* (D conflicts with c_i; ≈ intrinsic hallucination / NLI contradiction), *not mentioned* (D neither supports nor contradicts c_i; ≈ extrinsic hallucination / NLI neutral). A binary support score and strict / lenient error policies are derived from the three probabilities. In the taxonomy of [[Huang 2023 - A Survey on Hallucination in LLMs|Huang et al.]] this is detection of *faithfulness hallucination, context inconsistency*.
- **Served label**: "supported" iff calibrated P(supported) ≥ τ, with τ fitted on dev (0.90–0.94).

The binary definition below is the original (pre-D20) version and is kept for history.

## Task definition (as used for GroundOne; superseded by the three-class definition above)
- **Input**: a context D (the retrieved passages for a [[Retrieval-Augmented Generation|RAG]] query, possibly with the question) and one sentence c_i of the generated answer.
- **Output**: P(supported | D, c_i). It is read from the logits of two answer letters after a single forward pass (a [[System One Models|System One]] readout), with no generated text. *(Superseded: three letters, one pass per answer.)*
- **Labels**:
  - *supported*: all the information in c_i is present in D and does not contradict it. This matches AlignScore's definition of "aligned".
  - *unsupported*: everything else. This covers both **contradiction (conflict)** and **neutral (baseless)**, following MiniCheck's mapping of ANLI neutral and contradiction to unsupported (§3.3), and Kamoi et al. / Sanyal et al. as cited there.
- **Strictness**: world knowledge does not rescue a sentence. "Factual but unsupported" counts as unsupported (HHEM card; RAGTruth `implicit_true`, Lynx §3.1).
- **Not judged**: whether the context is relevant to the question, and whether the answer is correct in the world. Lynx states the same scope.
- **Response-level aggregation (optional)**: a response is grounded only if every sentence is. MiniCheck likewise takes the maximum over documents for each sentence.

### Known complications
- **Context dependence of sentences**: pronouns and ellipsis can make a sentence uncheckable on its own. MiniCheck found that decontextualization did not help on LLM-AggreFact (±0–1.4 BAcc), but argues it can matter for RAG (§7.2).
- **Multi-sentence and multi-fact reasoning**: a single claim may need several facts drawn from several context sentences. This motivates MiniCheck's synthetic C2D/D2C data.
- **Long contexts**: encoder checkers chunk the context (AlignScore about 350 tokens, MiniCheck 400–500) and take the maximum over chunks. A decoder with a long context window can avoid chunking, but should be evaluated on contexts longer than those seen in training.
- **Converting span labels**: [[RAGTruth]] provides span labels. A sentence is unsupported if it overlaps any hallucinated span. This rule is GroundOne's own.

## Evaluation conventions
- **Balanced accuracy (BAcc)** = ½(TPR + TNR). This is the standard in SummaC, AlignScore, MiniCheck and [[LLM-AggreFact]]. It is needed because the fraction of unsupported examples ranges from **10% (CNN) to 77% (REVEAL)** across LLM-AggreFact datasets ([[Tang 2024 - MiniCheck]] Table 11).
- **Threshold choice**: there are two regimes.
  1. **No tuning**: a fixed threshold t = midpoint of the score range (0.5). This is the **LLM-AggreFact headline protocol**, meant to measure zero-shot deployability (MiniCheck §4.1).
  2. **Per-dataset tuning on the validation split**, then BAcc on test. This is the SummaC and AlignScore protocol, and MiniCheck's Table 7. It helps weaker metrics a lot (SummaC-CV +9.2) and MiniCheck-FT5 only a little (+0.4).

  Recommendation for GroundOne: report (1) as the headline and (2) as analysis, and **never tune on test**. LLM-AggreFact has dev splits for this *(but GroundOne does not use them: no fitting of any kind on LLM-AggreFact, D18; calibration and thresholds are fitted on the RAGTruth dev split)*. RAGTruth has none, so a dev split must be carved out of its train split.
- **AUROC**: threshold-free ranking quality. AlignScore reports AUC-ROC on SummaC and TRUE. It is useful because a System One model outputs a probability.
- **Calibration**: [[Expected Calibration Error]] and reliability diagrams ([[Calibration]]). None of the baseline papers report these, so this is a differentiating axis for GroundOne.
- **Response- or span-level F1**: what RAGTruth and Lynx report. It is not directly comparable with sentence-level BAcc.
- **Cost and latency**: MiniCheck reports dollars per 13K test examples; HHEM reports about 1.5 s per 2k tokens on an x86 CPU. GroundOne should report latency per sentence and per response on the M4 Mac against the same baselines ([[When System One Beats an LLM]]). *Done (2026-10-10):* at K ≥ 14, 0.41 s (0.5B) / 2.57 s (3B) per answer and 5.5 J / 33 J per answer, ≈2× / ≈6× faster than terse / verbose judges of the same size; no latency claim against encoders or [[Rizzo-Flow]] because runtimes differ ([[GroundOne Results]], [[Energy of LLM Inference]], [[On-Device Inference]]).

## Related formulations: SummaC and FActScore
- **[[Laban 2022 - SummaC|SummaC]]** (summary consistency, TACL 2022) splits *both* the document and the summary into sentences, scores every pair with an NLI model and aggregates (max over document sentences, then mean). It is the classic evidence that sentence-level units make entailment checking work (MNLI: 56.4% BAcc at full-document granularity vs 73.5% at sentence level, Table 5), and it introduced the balanced-accuracy-with-validation-threshold protocol. GroundOne keeps the sentence unit on the answer side but reads the whole document as one context, so no document chunking or M × N passes are needed.
- **[[Min 2023 - FActScore|FActScore]]** (EMNLP 2023) decomposes long generations into **atomic facts** and reports the fraction supported by a knowledge source, with "supported" defined relative to that source rather than world truth. Its definition of support matches groundedness; its unit is finer than GroundOne's sentence. Its automatic evaluator compares P(True) vs P(False) after retrieved passages, a zero-shot binary logit readout.
- MiniCheck's finding that atomic decomposition brings no consistent gain at 2–4× cost (§7.1) supports the sentence unit; FActScore's finding that 40% of ChatGPT sentences mix supported and unsupported facts is the counter-argument the thesis should acknowledge.

## Reference numbers (LLM-AggreFact average BAcc)
| System | Type | Avg BAcc |
|---|---|---|
| Bespoke-MiniCheck-7B | fine-tuned 7B | 77.4 |
| GPT-4o (2024-05-13) | LLM judge | 75.9 |
| MiniCheck-Flan-T5-L | 0.8B checker | 75.0 |
| HHEM-2.1-open | small encoder | 71.8 |
| AlignScore | 355M encoder | 70.5 |
| Qwen2.5-0.5B-Instruct (zero-shot) | same backbone as GroundOne-0.5B | 64.2 |
| Qwen2.5-7B-Instruct (zero-shot) | LLM judge | 72.8 |
| *GroundOne 3B (this thesis)* | *fine-tuned 3B System One* | *74.8* |
| *MiniCheck-RoBERTa (re-run in this thesis)* | *355M encoder* | *74.0* |
| *GroundOne 0.5B (this thesis)* | *fine-tuned 0.5B System One* | *70.1* |

Source: [[Tang 2024 - LLM-AggreFact Leaderboard]]; rows in italics are measured in this thesis ([[GroundOne Results]]): GroundOne 3B vs MiniCheck-RoBERTa is not a significant difference.

## Decision models and groundedness (ingest 2026-10-10, `decision-model` tag)
The 2026 decision-model wave touches groundedness in three ways. All numbers below are self-reported or community-board figures, at **response level**, not GroundOne's sentence-level three-way metric.
- **RAGTruth inside the Decision Index.** One `noul` per test response ("contains content not supported by the context"), all 2,700 responses, F1 on the hallucinated class, chance 0.518. Jev 0.765; best entrant pplx-decider-v1-27b 0.803; Cloudflare reports 79.4 for Clef and 35.6 for Clef-flash in its own run; no entrant under 1B exceeds 0.553 ([[multimodalart 2026 - Jev Decision Index (Hugging Face Space)]], [[Cloudflare 2026 - Clef model card]]).
- **Span-level decision models.** Vela 2.0 answers "Which spans of the answer are not supported by the context?" as a typed `span` question: RAGTruth example-F1 0.774 (9B) and 0.706 (0.3B), against 0.817 for the 2B generative LettuceDetect ([[KR Labs and vLLM Semantic Router 2026 - Vela 2.0 9B model card]]).
- **Groundedness-specialised decision models.** uratori-ja uses GroundOne's three labels (supported / contradicted / insufficient) in Japanese, with accuracy rising from 0.686 (0.31B) to 0.897 (9B) on its own set, Jev 0.903 ([[tokimoa 2026 - uratori-ja-4b model card]]).
- **Decision-only judges on evidence-grounded factuality.** Jev scores 87.3 % on 3,000 HaluEval QA answers against 88.4 % for GPT-6 at 0.36 % of the fee; label noise caps the measured ceiling ([[Li 2026 - JEV-as-a-Judge (arXiv 2609.26550)]]). On re-generated RAGTruth and LLM-AggreFact items Jev's AUROC is 0.788 and 0.755–0.886 ([[Guo 2026 - Just Ask Jev (arXiv 2609.29429)]]).
- **For the thesis.** (1) A response-level hallucinated-class F1 for GroundOne on its 2,647 T1 answers (any sentence not supported → hallucinated) would place it on the same scale as Clef, Jev, Vela and LettuceDetect, labelled as specialist vs zero-shot. (2) The size pattern (small general decision models at chance, ≥ 15B above 0.6) supports the specialisation argument. (3) Training sets of several open decision models include VitaminC or WiCE (pplx-decider, Strands), so they cannot be used as clean baselines on T2/T3.

## Links
[[Laban 2022 - SummaC]], [[Min 2023 - FActScore]], [[Huang 2023 - A Survey on Hallucination in LLMs]], [[Decision-Model Landscape (Hugging Face, 2026)]], [[Decision-Model Benchmarks]], [[On-Device Inference]], [[GroundOne Results]], [[Hallucination Detection]], [[LLM-AggreFact]], [[RAGTruth]], [[Natural Language Inference]], [[MiniCheck]], [[HHEM]], [[AlignScore]], [[LLM-as-a-Judge]], [[Rizzo-Flow]], [[RAG Evaluation Frameworks]], [[Qwen2.5]], [[LoRA]]

## As the critic of a repair loop (ingest 2026-10-18)
- Verify-and-revise methods (RARR, CRITIC, CoVe, Self-Refine) and guardrail toolkits use a verifier to gate or trigger rewrites; external feedback is what makes them work ([[Verify-and-Revise Loops]], [[Guardrails and Policies]]). NeMo Guardrails' fact-checking rail is a yes/no prompt on the whole response (about 80 % on MS MARCO), not a per-sentence calibrated verdict.
