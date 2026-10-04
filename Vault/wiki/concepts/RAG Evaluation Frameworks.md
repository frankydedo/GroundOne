---
type: concept
tags: [rag, evaluation, faithfulness, llm-as-a-judge, metrics]
---
# RAG Evaluation Frameworks

Frameworks that score a [[Retrieval-Augmented Generation]] system automatically, typically along three axes popularised by [[Es 2024 - RAGAS|RAGAS]] and adopted by [[Saad-Falcon 2024 - ARES|ARES]]:

| Axis | Question | Inputs |
| --- | --- | --- |
| **Faithfulness / groundedness** | Is the answer supported by the retrieved context? | context, answer |
| **Answer relevance** | Does the answer address the question? | question, answer |
| **Context relevance** | Is the retrieved context focused and pertinent? | question, context |

Faithfulness is the axis GroundOne addresses ([[Groundedness Verification]]).

## How faithfulness is scored

| Framework | Judge | Unit | Procedure | Output |
| --- | --- | --- | --- | --- |
| **RAGAS** ([[Es 2024 - RAGAS]]) | Prompted `gpt-3.5-turbo-16k` | Statements extracted from answer sentences | LLM call 1 extracts statements; call 2 gives a brief explanation then Yes/No per statement | F = supported / total statements |
| **ARES** ([[Saad-Falcon 2024 - ARES]]) | Fine-tuned DeBERTa-v3-Large + binary head, trained on FLAN-T5-XXL synthetic data | Whole query–passage–answer triple | Classifier label; system score = mean label, rectified with ~150–300 human labels via prediction-powered inference | System-level score + 95% CI |
| **Self-RAG** ([[Asai 2024 - Self-RAG]]) (not an eval framework, but an in-model critic) | The generator itself (Llama2 7B/13B), critic distilled from GPT-4 | One sentence/segment per passage | `IsSup` reflection token ∈ {fully, partially, no support}; normalised token probability | Per-segment probability |
| **GroundOne** (this thesis) | Qwen2.5 0.5B/3B + LoRA, [[System One Models|System One]] | One answer sentence vs retrieved context | Single forward pass, logit readout of answer letters, no generation | Per-sentence support probability |

## Measured evidence
- **Decomposition beats holistic scoring.** On WikiEval (50 pages), RAGAS faithfulness agrees with human pairwise judgements 0.95, vs 0.72 for asking ChatGPT for a 0–10 score and 0.54 for asking it to rank two answers (RAGAS Table 1). Caveat: unfaithful answers there were generated *without context*, an easy contrast.
- **Fine-tuned small judge beats prompted LLM judge for ranking.** ARES' Kendall's τ is on average 0.065 (context rel.) and 0.132 (answer rel.) higher than RAGAS, and ~0.06 higher than a few-shot GPT-3.5 judge (ARES §5.1, Table 1).
- **But per-example faithfulness is hard.** ARES' faithfulness judge on AIS attribution data is 62.5% (WoW) / 84.0% (CNN/DM) accurate per example, while its aggregate hallucination-rate estimate is within 2.5 points (ARES Table 2). Good system-level estimates can hide weak per-instance verification.
- **Domain shift.** ARES judges trained on NQ drop to τ 0.28–0.38 on code, cross-lingual and entity-extraction tasks (ARES §5.4).
- Human inter-annotator agreement on WikiEval faithfulness is ~95% (RAGAS §4).

## Design dimensions that matter for GroundOne
1. **Granularity**: answer-level (ARES), statement-level (RAGAS), sentence-level (Self-RAG, GroundOne). Finer granularity localises errors for the user interface of a RAG demo.
2. **Judge type**: prompted generative LLM (RAGAS) vs fine-tuned classifier (ARES) vs readout from a fine-tuned decoder (Self-RAG critic tokens, GroundOne). See [[LLM-as-a-Judge]].
3. **Purpose**: offline system comparison (RAGAS, ARES) vs online per-response gating (Self-RAG, GroundOne). Online use needs low latency and per-example accuracy, not only good averages.
4. **Cost**: RAGAS needs ≥2 generative calls per answer with rationales; ARES needs GPU fine-tuning (~32 GB) but cheap inference; neither reports per-call latency (not stated). GroundOne's claim is prefill-only cost ([[Prefill and Decode]], [[KV Cache]]).
5. **Confidence**: RAGAS outputs ratios; ARES gives CIs on system scores via PPI and lists using judge logits as future work; GroundOne outputs per-sentence probabilities whose [[Calibration]] must be measured.
6. **Benchmarks**: RAGAS (WikiEval) and ARES (KILT, SuperGLUE, AIS) use their own data; for groundedness specifically, [[LLM-AggreFact]] and [[RAGTruth]] are the standard targets.

## Links
- Sources: [[Es 2024 - RAGAS]], [[Saad-Falcon 2024 - ARES]], [[Asai 2024 - Self-RAG]], [[Zheng 2023 - Judging LLM-as-a-Judge]], [[Lewis 2020 - Retrieval-Augmented Generation]]
- Concepts: [[Retrieval-Augmented Generation]], [[LLM-as-a-Judge]], [[Groundedness Verification]], [[Hallucination Detection]], [[Calibration]], [[System One Models]], [[Jev]], [[When System One Beats an LLM]], [[KV Cache]], [[Prefill and Decode]], [[RAGTruth]], [[LLM-AggreFact]]
