---
type: concept
tags: [concept, groundedness, faithfulness, rag, evaluation-protocol, groundone]
---
# Groundedness Verification

**Groundedness verification** checks whether each statement in a generated answer is **supported by the retrieved context** that the generator was given. It is the "fact-checking on grounding documents" primitive of [[Tang 2024 - MiniCheck|MiniCheck]], and the core task of [[GroundOne]]. It is the context-faithfulness, sentence-level slice of [[Hallucination Detection]].

## Task definition (as used for GroundOne)
- **Input**: a context D (the retrieved passages for a [[Retrieval-Augmented Generation|RAG]] query, possibly with the question) and one sentence c_i of the generated answer.
- **Output**: P(supported | D, c_i). It is read from the logits of two answer letters after a single forward pass (a [[System One Models|System One]] readout), with no generated text.
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

  Recommendation for GroundOne: report (1) as the headline and (2) as analysis, and **never tune on test**. LLM-AggreFact has dev splits for this. RAGTruth has none, so a dev split must be carved out of its train split.
- **AUROC**: threshold-free ranking quality. AlignScore reports AUC-ROC on SummaC and TRUE. It is useful because a System One model outputs a probability.
- **Calibration**: [[Expected Calibration Error]] and reliability diagrams ([[Calibration]]). None of the baseline papers report these, so this is a differentiating axis for GroundOne.
- **Response- or span-level F1**: what RAGTruth and Lynx report. It is not directly comparable with sentence-level BAcc.
- **Cost and latency**: MiniCheck reports dollars per 13K test examples; HHEM reports about 1.5 s per 2k tokens on an x86 CPU. GroundOne should report latency per sentence and per response on the M4 Mac against the same baselines ([[When System One Beats an LLM]]).

## Reference numbers (LLM-AggreFact average BAcc)
| System | Type | Avg BAcc |
|---|---|---|
| Bespoke-MiniCheck-7B | fine-tuned 7B | 77.4 |
| GPT-4o (2024-05-13) | LLM judge | 75.9 |
| MiniCheck-Flan-T5-L | 0.8B checker | 75.0 |
| HHEM-2.1-open | small encoder | 71.8 |
| AlignScore | 355M encoder | 70.5 |
| Qwen2.5-0.5B-Instruct (zero-shot) | same backbone as GroundOne-0.5B | 64.2 |
Source: [[Tang 2024 - LLM-AggreFact Leaderboard]].

## Links
[[Hallucination Detection]], [[LLM-AggreFact]], [[RAGTruth]], [[Natural Language Inference]], [[MiniCheck]], [[HHEM]], [[AlignScore]], [[LLM-as-a-Judge]], [[Rizzo-Flow]], [[RAG Evaluation Frameworks]], [[Qwen2.5]], [[LoRA]]
