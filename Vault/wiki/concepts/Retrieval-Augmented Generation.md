---
type: concept
tags: [rag, retrieval, generation, hallucination, on-device, verification]
---
# Retrieval-Augmented Generation

**Retrieval-Augmented Generation (RAG)** conditions a language model's output on passages retrieved from an external corpus at query time. The term and the first end-to-end formulation come from [[Lewis 2020 - Retrieval-Augmented Generation|Lewis et al. 2020]]: a DPR retriever (non-parametric memory, a dense index of 21M Wikipedia chunks) plus a BART generator (parametric memory), fine-tuned jointly. Modern practice usually skips joint training and simply prepends the top-k retrieved passages to the prompt of an off-the-shelf LLM ([[Es 2024 - RAGAS]] §1).

## Canonical pipeline and where verification sits
```
query → retriever (top-k chunks) → [optional rerank] → generator LLM → answer
                                                                   ↓
                                      verifier: is each answer sentence supported by the retrieved chunks?
                                                                   ↓
                                   show / flag / drop / regenerate unsupported sentences
```
- **Post-hoc, generator-agnostic verification** (GroundOne's position): after generation, each sentence is checked against the same retrieved context the generator saw. It can flag, hide, or trigger regeneration of unsupported sentences without modifying the generator. See [[Groundedness Verification]], [[Hallucination Detection]].
- **In-generator critique** ([[Asai 2024 - Self-RAG|Self-RAG]]): the generator itself emits reflection tokens (`IsRel`, `IsSup`, `IsUse`) during decoding and uses their probabilities to rank continuations. Requires retraining the generator.
- **Offline evaluation** ([[RAG Evaluation Frameworks]]: RAGAS, ARES): scores a whole RAG system on samples (faithfulness, answer relevance, context relevance) to compare configurations; not on the live request path.

## Why RAG still hallucinates
Evidence from the ingested sources:
1. **Retrieval misses**: in RAG-on-FEVER, the top retrieved document is from a gold article in only 71% of cases; a gold article is in the top 10 in 90% ([[Lewis 2020 - Retrieval-Augmented Generation|Lewis 2020]] §4.4). The generator then answers from incomplete evidence.
2. **Parametric leakage**: RAG answers 11.8% of NQ questions correctly when the answer is in no retrieved document (Lewis 2020 p.6), i.e. the model freely mixes memorised knowledge into a "grounded" answer. If memorised knowledge is wrong or stale, the answer is unsupported.
3. **No guarantee of consistency with the passages**: models "are not explicitly trained to leverage and follow facts from provided passages"; irrelevant retrieved passages can lead to low-quality generations ([[Asai 2024 - Self-RAG|Self-RAG]] §1).
4. **Fluency vs support trade-off**: in Self-RAG, pushing for more fluent/longer outputs lowers citation precision; more claims means more unsupported claims (Self-RAG p.9–10).
5. **Long contexts**: LLMs exploit information in the middle of long passages less well ([[Es 2024 - RAGAS|RAGAS]] §3, citing Liu et al. 2023), and LLMs struggle to pick the crucial sentences in long contexts (RAGAS §5).
6. **Knowledge source itself** may be wrong or biased (Lewis 2020, Broader Impact). Groundedness ≠ truth: a verifier checks support by the context, not world correctness.

The sentence-level annotated RAG hallucination data in [[RAGTruth]] and the grounding benchmarks aggregated in [[LLM-AggreFact]] give quantitative evidence of how often this happens (see those pages).

## Local / on-device RAG motivation
See [[On-Device Inference]] for the general local-vs-remote trade-off, runtimes (llama.cpp, MLX) and hardware limits; this section covers what is specific to RAG.
- **Privacy and data control**: documents never leave the device; hosted judges such as GPT-3.5/GPT-4 (used by RAGAS, ARES baselines, Self-RAG labelling) are excluded for sensitive data. RAGAS also notes token-probability methods are impossible for closed API models ([[Es 2024 - RAGAS|RAGAS]] §1–2).
- **Updatability**: knowledge can be updated by swapping the index without retraining (Lewis 2020 §4.5), useful for personal/enterprise corpora.
- **Budget constraint**: on a 16 GB Apple Silicon machine, the generator (e.g. Qwen2.5-3B) already uses most of the latency budget; a second generative LLM as judge would roughly double decode cost. A verifier that only does prefill + logit readout ([[Prefill and Decode]], [[KV Cache]]) fits the budget, which is the core argument of [[When System One Beats an LLM]] applied to RAG.
- **Hardware contrast**: ARES' judges needed GPUs with ~32 GB ([[Saad-Falcon 2024 - ARES|ARES]] §7); GroundOne targets a 16 GB M4 Mac ([[Apple Silicon and MLX]]).
- **Co-residence**: generator, retriever and verifier share the same 16 GB of unified memory; GroundOne's peaks (2.6 GB for 0.5B, 5.9 GB for 3B in training) leave room for a generator, but co-resident memory has not yet been measured.
- **Measured cost of verification on-device**: 0.41 s / 2.57 s per answer at K ≥ 14 and 5.5 J / 33 J per answer (0.5B / 3B) ([[Energy of LLM Inference]]).
- **RAG does not remove hallucinations**: the survey of [[Huang 2023 - A Survey on Hallucination in LLMs|Huang et al.]] (§6) attributes RAG hallucinations to retrieval failure and to a generation bottleneck (noisy context, context–knowledge conflicts, poor use of long contexts), which motivates a post-hoc verifier.

## GroundOne in this picture
GroundOne is a [[System One Models|System One]] verifier placed after the generator: for each (retrieved context, answer sentence) pair, one forward pass and a logit readout of answer letters give a support probability. Shared context can be prefilled once into the [[KV Cache]] and reused across all sentences of the answer. *(Superseded 2026-10-10: the default design (b) runs one forward pass per **answer**, with a " Verdict:" marker after each sentence, and reads three probabilities per sentence: supported / contradicted / not mentioned.)* The demo couples a Qwen2.5-3B generator with this verifier.

## Links
- Sources: [[Huang 2023 - A Survey on Hallucination in LLMs]], [[Lewis 2020 - Retrieval-Augmented Generation]], [[Asai 2024 - Self-RAG]], [[Es 2024 - RAGAS]], [[Saad-Falcon 2024 - ARES]]
- Concepts: [[On-Device Inference]], [[RAG Evaluation Frameworks]], [[Groundedness Verification]], [[Hallucination Detection]], [[LLM-as-a-Judge]], [[System One Models]], [[When System One Beats an LLM]], [[Calibration]], [[RAGTruth]], [[LLM-AggreFact]]
