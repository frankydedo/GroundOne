---
type: source
author: "Patrick Lewis, Ethan Perez, Aleksandra Piktus, Fabio Petroni, Vladimir Karpukhin, Naman Goyal, Heinrich Küttler, Mike Lewis, Wen-tau Yih, Tim Rocktäschel, Sebastian Riedel, Douwe Kiela"
date: 2020
venue: "NeurIPS 2020 (ingested file: arXiv 2005.11401v4)"
url: https://arxiv.org/abs/2005.11401
tags: [source, paper, rag, retrieval, knowledge-intensive-nlp, fact-verification]
---
# Lewis 2020 - Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks

**Raw file**: `raw/Lewis 2020 - Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks_ingested.pdf`

## Overview
The paper that named **[[Retrieval-Augmented Generation]] (RAG)**. It combines a *parametric memory* (BART-large seq2seq generator, ~400M parameters) with a *non-parametric memory* (a dense vector index of 21M 100-word Wikipedia chunks, Dec. 2018 dump) accessed by a DPR bi-encoder retriever (§2.2–2.3, §3). Retriever (query encoder only) and generator are fine-tuned end-to-end, treating the retrieved document as a latent variable marginalised over the top-K documents (§2.1, §2.4). The document encoder and index are kept fixed (§2.4).

Two variants (§2.1):
- **RAG-Sequence**: the same document conditions the whole output; marginalise at sequence level.
- **RAG-Token**: a different document can be used for each output token; marginalise per token.

## Key Insights
1. **Motivation is hallucination and provenance.** Parametric-only LMs "cannot easily expand or revise their memory, can't straightforwardly provide insight into their predictions, and may produce hallucinations" (§1, p.1). Retrieval memory is human-readable and human-writable (§5, p.9).
2. **Measured QA results**: RAG sets SOTA on open-domain QA: NQ 44.5 EM (RAG-Seq), WebQuestions 45.5, CuratedTrec 52.2 (Table 1, p.6). It answers 11.8% of NQ questions correctly even when the answer is in no retrieved document (p.6), i.e. part of the answer comes from **parametric memory, not the context**, which is exactly the unsupported content a groundedness verifier must catch.
3. **Measured factuality (human eval)**: on Jeopardy question generation (452 pairs), RAG judged more factual than BART in 42.7% of cases vs 7.1% the other way (Table 4, p.8). "RAG models hallucinate less" than BART on MS-MARCO is a *qualitative claim* (§4.2, p.6).
4. **FEVER as classification via single-token labels**: FEVER labels (supports/refutes/not enough info) are mapped to **single output tokens** and trained directly on claim–class pairs (§3.4, p.5); RAG reaches 72.5% (3-way) and 89.5% (2-way) label accuracy, within 4.3% / 2.7% of pipeline SOTA that use gold-evidence supervision (Table 2, p.6; §4.4). The paper also notes RAG can do sequence classification "by considering the target class as a target sequence of length one" (§2.1, p.3).
5. **Retrieval quality is imperfect**: on FEVER the top retrieved doc is from a gold article in 71% of cases; a gold article is in the top 10 in 90% (§4.4, p.7). So even a good retriever leaves ~10–30% of cases where the generator lacks the right evidence.
6. **Index hot-swapping**: replacing the 2018 index with a 2016 one updates world knowledge without retraining (70% vs 68% accuracy on matched world-leader questions; 4–12% on mismatched) (§4.5, p.8).
7. **More retrieved docs is not monotonically better**: RAG-Token NQ performance peaks at ~10 docs (Fig. 3, p.8).
8. **Limitations (stated, Broader Impact p.10)**: the knowledge source (Wikipedia) "will probably never be entirely factual and completely devoid of bias"; misuse concerns similar to GPT-2. No latency or cost figures are reported (not stated).

## Relevance to GroundOne
- **Why verification is needed**: RAG's own design lets the generator mix parametric knowledge with retrieved text (insight 2). That is useful for QA accuracy but means a RAG answer can be *correct yet ungrounded* or *fluent yet unsupported*. GroundOne's sentence-level "is this supported by the retrieved context?" check targets exactly this gap. See [[Groundedness Verification]], [[Hallucination Detection]].
- **Precedent for label-as-token readout**: Lewis et al. already cast FEVER verification as predicting a single label token (insight 4). GroundOne's logit readout of answer letters is the inference-time analogue: one forward pass, read the logits of the label tokens, no generation ([[System One Models]], [[Prefill and Decode]]).
- **How faithfulness is judged here**: only by downstream metrics (EM, BLEU/ROUGE, FEVER accuracy) and a small human factuality study. There is no automatic, per-sentence faithfulness metric; that gap is what later work ([[RAG Evaluation Frameworks]], [[RAGTruth]], [[LLM-AggreFact]]) fills.
- **Pipeline context for the demo**: the GroundOne demo (Qwen2.5-3B generator + GroundOne verifier) is a modern decoder-only instance of the retriever → generator pattern introduced here, with a verifier added after generation ([[Retrieval-Augmented Generation]]).

## Links
- Concepts: [[Retrieval-Augmented Generation]], [[RAG Evaluation Frameworks]], [[Groundedness Verification]], [[Hallucination Detection]], [[System One Models]], [[Prefill and Decode]]
- Related sources: [[Asai 2024 - Self-RAG]], [[Es 2024 - RAGAS]], [[Saad-Falcon 2024 - ARES]]
