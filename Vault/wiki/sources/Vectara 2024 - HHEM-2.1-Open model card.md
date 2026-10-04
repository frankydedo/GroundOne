---
type: source
author: "Vectara (Miaoran Li, Rogger Luo, Ofer Mendelevitch)"
date: 2024
venue: "Hugging Face model card (doi 10.57967/hf/3240); accessed 2026-10-05"
url: https://huggingface.co/vectara/hallucination_evaluation_model
tags: [source, model-card, hallucination-detection, encoder, t5, vendor]
---
# Vectara 2024 - HHEM-2.1-Open model card

**Raw file**: `raw/Vectara 2024 - HHEM-2.1-Open model card_ingested.md` (README captured from Hugging Face)

This is the model card for **HHEM-2.1-Open** (Hughes Hallucination Evaluation Model), Vectara's open, lightweight premise/hypothesis consistency classifier for RAG. It is a **vendor document**: the numbers are self-reported, and the card also promotes Vectara's commercial HHEM-2.3. Concept page: [[HHEM]].

## Overview
- **Licence**: **Apache-2.0**. The repo is gated: the extra fields are Company and Country.
- **Base model**: `google/flan-t5-base`. The tokenizer is flan-t5-base.
- **Input/output**: takes (premise, hypothesis) pairs and returns a score in [0,1], where 1 means the hypothesis is fully supported by the premise. There are two output neurons, `hallucinated` and `consistent`.
- **Prompt template (pipeline use)**: `"<pad> Determine if the hypothesis is true given the premise?\n\nPremise: {text1}\n\nHypothesis: {text2}"`
- **How to run**: `AutoModelForSequenceClassification.from_pretrained('vectara/hallucination_evaluation_model', trust_remote_code=True)`, then `model.predict(pairs)`. Calling `model(pairs)` directly is not the documented path. The `text-classification` pipeline also works with the template above.
- **Definition of hallucination**: the hypothesis is not supported by the premise. This is **asymmetric**, and a statement that is true in the world but unsupported by the premise still counts as hallucinated (the "factual but hallucinated" example, Paris vs Berlin).
- **Context length**: the card states that HHEM-2.1-Open has **"unlimited context length"**, whereas HHEM-1.0 was capped at 512 tokens. The card also says to ignore the T5 "sequence length is longer than the maximum" warning. How long contexts are handled internally is not stated.
- **Efficiency (vendor claim)**: under 600 MB RAM at fp32, and about **1.5 s for a 2k-token input on a modern x86 CPU**.

## Reported numbers (vendor-reported; the GPT baselines are zero-shot with a prompt from another paper)
| Benchmark | HHEM-1.0 BAcc | **HHEM-2.1-Open BAcc** | GPT-3.5-Turbo | GPT-4 06-13 |
|---|---|---|---|---|
| AggreFact-SOTA | 78.87 | **76.55** | 72.19 | 73.78 |
| RAGTruth-Summ | 53.36 | **64.42** | 58.49 | 62.62 |
| RAGTruth-QA | 52.58 | **74.28** | 56.16 | 74.11 |

The card also reports F1, recall and precision. For HHEM-2.1 on RAGTruth-QA these are F1 60.00 / R 54.38 / P 66.92. The threshold used, the split, and whether "positive" means hallucinated are **not stated**.

Independent measurement on [[LLM-AggreFact]] ([[Tang 2024 - LLM-AggreFact Leaderboard]]): **average BAcc 71.8**, RAGTruth column 69.9, listed at size "0.1B".

## Key insights
1. HHEM-2.1 trades a little AggreFact-SOTA accuracy (−2.3) for large gains on RAG data (+11 on RAGTruth-Summ, +21.7 on RAGTruth-QA), which the card attributes to the longer context.
2. The vendor's comparison against GPT-4 (+0.17 on RAGTruth-QA) is within noise. The independent leaderboard puts HHEM-2.1 well below GPT-4-class models (71.8 vs about 76).
3. The model is designed for CPU and consumer hardware, which makes it a natural **latency baseline** for a [[System One Models|System One]] verifier.

## Relevance to GroundOne
- **Baseline that runs locally on the M4 Mac**: Apache-2.0, small, PyTorch/transformers. Apple-Silicon or MPS support is **not stated** in the card. The x86 CPU latency figure (1.5 s per 2k tokens) is the vendor's and should be re-measured on the thesis hardware for the latency comparison.
- **Input format matches GroundOne's**: (context, sentence) pair, score in [0,1], with 1 meaning supported. HHEM's `consistent` probability maps directly to GroundOne's P(supported) for computing AUROC and ECE.
- **Caveats when comparing**:
  - The training data is **not stated**, so it may overlap with RAGTruth or AggreFact. The card does not say.
  - The "unlimited context" claim is not explained.
  - The size is ambiguous: the base model is flan-t5-base, while the leaderboard lists 0.1B. Report it as "flan-t5-base-derived, <600 MB fp32".

## Links
- Concepts: [[HHEM]], [[Hallucination Detection]], [[Groundedness Verification]], [[LLM-AggreFact]], [[RAGTruth]], [[Retrieval-Augmented Generation]], [[System One Models]], [[When System One Beats an LLM]]
- Related sources: [[Tang 2024 - LLM-AggreFact Leaderboard]], [[Niu 2024 - RAGTruth]], [[Tang 2024 - MiniCheck]]
