---
type: source
author: "Akari Asai, Zeqiu Wu, Yizhong Wang, Avirup Sil, Hannaneh Hajishirzi"
date: 2024
venue: "ICLR 2024 (ingested file is the arXiv 2310.11511v1 preprint)"
url: https://arxiv.org/abs/2310.11511
tags: [source, paper, rag, self-reflection, critic, reflection-tokens, groundedness]
---
# Asai 2024 - Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection

**Raw file**: `raw/Asai 2024 - Self-RAG_ingested.pdf` · Code/models: https://selfrag.github.io/

## Overview
Self-RAG trains a single LM (Llama2 7B / 13B) to decide **when to retrieve** and to **critique** retrieved passages and its own output by generating special **reflection tokens** added to the vocabulary (§3, Table 1 p.4):

| Token | Input | Values | Meaning |
| --- | --- | --- | --- |
| `Retrieve` | x / x,y | yes, no, continue | retrieve now? |
| `IsRel` | x, d | relevant, irrelevant | passage d useful for x |
| `IsSup` | x, d, y | fully supported, partially supported, no support | all verification-worthy statements in y are supported by d |
| `IsUse` | x, y | 5,4,3,2,1 | usefulness |

`IsSup` is exactly a per-segment groundedness label. A segment is **one sentence** in their experiments (footnote 3, p.3).

Training (§3.2): GPT-4 is prompted to label reflection tokens (4k–20k examples per token type); a **critic** LM (Llama2-7B) is trained on these; the critic then annotates 150k instruction/output pairs offline, and the **generator** is trained with the standard next-token objective on text interleaved with reflection tokens. No critic is needed at inference.

## Key Insights
1. **Critic tokens are read as probabilities.** At inference the score of each critique group is the **normalised probability of the most desirable token** among that group's tokens, s = p(r̂) / Σ p(r_i) (Eq. 4, p.6). Retrieval is triggered when the normalised probability of `Retrieve=Yes` exceeds a threshold (§3.3). Segment ranking uses p(y_t) + a weighted sum of `IsRel`, `IsSup`, `IsUse` scores (default weights 1.0, 1.0, 0.5; §4.3 p.7), with segment-level beam search (beam 2).
2. **Critic quality (claimed)**: the critic reaches ">90% agreement with GPT-4-based predictions on most reflection token categories" (§3.2.1 p.5, details in appendix Table 5, not read). "Manual assessment reveals that GPT-4 reflection token predictions show high agreement with human evaluations" (p.5), no number given in the main text.
3. **Human check of `IsSup`/`IsRel`** (50 samples each, PopQA and Bio, Fig. 4d p.10): IsRel 95.0 / 90.0, IsSup 90.0 / 85.0 (% agreement with annotators). Small sample.
4. **Main results (Table 2 p.8, measured)**: Self-RAG 13B: PopQA 55.8, TriviaQA 69.3, PubHealth 74.5, ARC-C 73.1, Bio FactScore 80.2, ASQA citation precision/recall 70.3 / 71.3. Self-RAG 7B ASQA citation precision 66.9 vs Ret-ChatGPT 65.1 and plain retrieval-augmented Llama2-13B 2.3. Standard RAG baselines "struggle to improve citation accuracy".
5. **Ablation**: removing `IsSup` from beam scoring drops ASQA em 32.1 → 30.6 and PopQA 45.5 → 44.1 (Fig. 3a, p.9); raising the `IsSup` weight raises citation precision but lowers MAUVE fluency (Fig. 3b): more fluent, longer generations contain more unsupported claims (p.9–10).
6. **Why standard RAG still hallucinates** (§1): it retrieves a fixed number of passages regardless of need, may use irrelevant passages, and "the output is not guaranteed to be consistent with retrieved relevant passages" since models are not trained to follow them.
7. **Limitation (Ethical Concerns p.11)**: Self-RAG "can still generate outputs that are not fully supported by the citations".
8. **Not stated**: wall-clock latency or cost of reflection-token decoding and parallel per-passage generation (inference uses vLLM, p.7); calibration of reflection-token probabilities.

## Relevance to GroundOne
- **Learned critic token ≈ logit readout.** Self-RAG's `IsSup` judgement is exactly GroundOne's question (is this sentence supported by this passage?) and it is consumed as a **normalised probability over a closed set of special tokens** (Eq. 4), the same mechanism as GroundOne reading the logits of answer letters. Differences:
  - Self-RAG's critic is **inside the generator** and the token is produced during decoding (interleaved with generation, per passage, with beam search); GroundOne is a **separate verifier** that does one prefill-only forward pass per (context, sentence) and generates nothing ([[Prefill and Decode]], [[System One Models]]).
  - Self-RAG requires retraining the generator; GroundOne is generator-agnostic (verifies any RAG answer, e.g. the Qwen2.5-3B generator in the demo).
  - Self-RAG uses three support levels; GroundOne's label set and its [[Calibration]] are design choices to compare against.
- **How faithfulness is judged**: offline by GPT-4 labels distilled into a 7B critic; online by the generator's own `IsSup` probability. Evaluation of groundedness is indirect (ASQA citation precision/recall, FactScore), not a dedicated sentence-level benchmark like [[RAGTruth]] or [[LLM-AggreFact]].
- **Self-enhancement risk**: a model critiquing its own output is the setting where [[LLM-as-a-Judge]] self-enhancement bias is a concern ([[Zheng 2023 - Judging LLM-as-a-Judge]]); an independent verifier avoids it. (The Self-RAG paper does not measure this.)
- **Distillation recipe precedent**: GPT-4 labels → small critic is the same pattern as training a small verifier on LLM- or human-labelled support data.

## Links
- Concepts: [[Retrieval-Augmented Generation]], [[Groundedness Verification]], [[Hallucination Detection]], [[LLM-as-a-Judge]], [[System One Models]], [[Prefill and Decode]], [[Calibration]]
- Related sources: [[Lewis 2020 - Retrieval-Augmented Generation]], [[Saad-Falcon 2024 - ARES]], [[Es 2024 - RAGAS]]
