---
type: source
author: "Selvan Sunitha Ravi, Bartosz Mielczarek, Anand Kannappan, Douwe Kiela, Rebecca Qian (Patronus AI, Contextual AI, Stanford)"
date: 2024
venue: "arXiv:2407.08488v2 (22 Jul 2024), preprint"
url: https://arxiv.org/abs/2407.08488
tags: [source, paper, hallucination-detection, llm-judge, fine-tuned-detector, benchmark, rag]
---
# Ravi 2024 - Lynx

**Raw file**: `raw/Ravi 2024 - Lynx_ingested.pdf` (13 pages, read in full)

**Lynx** is an open hallucination-detection LLM: Llama-3-Instruct, 8B and 70B, fine-tuned to output reasoning followed by a PASS/FAIL verdict. The paper also introduces **HaluBench**, a 15k-sample QA benchmark. Lynx is the representative of the "**fine-tuned generative judge**" family, the opposite design point from GroundOne's single-pass logit readout. See [[Hallucination Detection]] and [[LLM-as-a-Judge]].

## Overview
- **Definition (§3, §3.1)**: Lynx targets **intrinsic** hallucination only, meaning answers unfaithful to the context. Factuality against world knowledge is out of scope.
  - An answer is a hallucination if it is not supported by the context *given the question*.
  - Relevance of the context is **not** judged: an answer consistent with an irrelevant context counts as faithful, and an incorrect answer that is consistent with the context counts as faithful.
- **HaluBench (§3.2)**: 15k (question, context, answer, label) tuples.
  - **FinanceBench, DROP, CovidQA, PubMedQA**: 1k each, balanced. The hallucinated answers are **GPT-4o semantic perturbations** of gold answers: minimal edits that introduce an inconsistency.
  - **HaluEval qa_samples**: 10k.
  - **RAGTruth**: "the test split that comprised of 900 samples, of which 160 examples contain hallucinations".
  - Human check on 50 examples per perturbed dataset: agreement 0.90–0.96 (Table 2).
- **Training (§3.3, App. B)**:
  - 2,400 training and 800 validation examples, drawn from RAGTruth, DROP, CovidQA and PubMedQA (600 per subtask from train splits, half perturbed).
  - The targets include **GPT-4o-generated reasoning** (bullet points) plus a JSON verdict `{"REASONING": ..., "SCORE": "PASS"|"FAIL"}`.
  - 3 epochs, lr 5e-7, batch 256, on 32 H100s for 70B, with FSDP and flash attention.
  - Inference uses greedy decoding with up to **600 new tokens**, on vLLM with 8×H100 for 70B.

## Key results (Table 3, p.7; metric = accuracy)
| Model | RAGTruth | Overall HaluBench |
|---|---|---|
| GPT-4o | 84.3 | 86.5 |
| GPT-4-Turbo | 85.0 | 85.0 |
| Claude-3-Sonnet | 79.1 | 78.8 |
| GPT-3.5-Turbo | 50.7 | 58.7 |
| RAGAS Faithfulness (threshold 0.5) | 75.8 | 66.9 |
| Llama-3-Instruct-8B | 80.0 | 70.4 |
| Llama-3-Instruct-70B | 83.8 | 80.1 |
| **Lynx 8B** | 80.0 | **82.9** |
| **Lynx 70B** | 80.2 | **87.4** |

- Lynx-70B is **worse than its base model on RAGTruth** (80.2 vs 83.8). Adding 2k RAGTruth training samples raises RAGTruth to 85.8 but lowers the other splits, for an overall gain of about 0.4 points (Table 4, App. B.3).
- The base Llama-2-13B-chat is almost unusable as a judge because its output cannot be parsed (3.3% overall). Fine-tuning fixes the parsing (77.8%) (Table 5).

## Measured vs claimed
- The claim "outperforms GPT-4o" rests on +0.9 points of overall *accuracy* on the authors' own benchmark, which contains GPT-4o-generated perturbations and training data drawn from the same source distributions.
- Accuracy is reported **even on the imbalanced RAGTruth subset** (160 of 900 positive), where balanced accuracy would be more informative.

## Limitations (§6)
- QA only, no summarization.
- English only.
- Retrieval failures are out of scope.
- No world-knowledge factuality.

## Relevance to GroundOne
- **The opposite design point**: Lynx generates up to 600 tokens of reasoning per verdict and needs 8×H100 for 70B, whereas GroundOne returns one forward pass and reads the logits of the answer letters. This is a concrete example of the latency gap in [[When System One Beats an LLM]], and of the parse-failure risk that logit readout avoids (Table 5).
- **Response-level, not sentence-level**: Lynx judges a whole answer. Its numbers cannot be compared directly with sentence-level BAcc on [[LLM-AggreFact]].
- **Data-design idea**: GPT-4o "semantic perturbation" of gold answers into minimally different hallucinations is a cheap way to create hard negatives (compare C2D/D2C in [[MiniCheck]]).
- **RAGTruth split discrepancy**: Lynx says the RAGTruth test split has "900 samples", but [[Niu 2024 - RAGTruth]] defines 450 test instances (2,700 responses). Lynx's subset is presumably a sample; how it was drawn is not stated.
- **Licence**: not stated in the paper. Models and HaluBench are released on Hugging Face (`PatronusAI/Llama-3-Lynx-70B-Instruct`, `PatronusAI/HaluBench`).

## Links
- Concepts: [[Hallucination Detection]], [[Groundedness Verification]], [[LLM-as-a-Judge]], [[RAGTruth]], [[Retrieval-Augmented Generation]], [[When System One Beats an LLM]], [[System One Models]]
- Related sources: [[Niu 2024 - RAGTruth]], [[Tang 2024 - MiniCheck]], [[Vectara 2024 - HHEM-2.1-Open model card]]
