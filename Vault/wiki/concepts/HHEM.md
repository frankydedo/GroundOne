---
type: concept
tags: [concept, model, hallucination-detection, encoder, baseline, vendor, cpu]
---
# HHEM

**HHEM** (Hughes Hallucination Evaluation Model) is Vectara's family of premise/hypothesis consistency classifiers for RAG. **HHEM-2.1-Open** is the open-weights version ([[Vectara 2024 - HHEM-2.1-Open model card]]). HHEM-2.3 is commercial: it is available only through Vectara's platform, is multilingual, and powers Vectara's hallucination leaderboard.

## Key facts (HHEM-2.1-Open)
| Property | Value | Source |
|---|---|---|
| Licence | **Apache-2.0** (gated download: company and country fields) | model card |
| Base model | `google/flan-t5-base` | model card |
| Size | "0.1B" (leaderboard). The card only says <600 MB RAM at fp32 | leaderboard, card |
| Context | claimed **"unlimited"** (HHEM-1.0 was capped at 512 tokens); mechanism not stated | card |
| Output | score in [0,1]; two neurons `hallucinated` / `consistent`; 1 = fully supported | card |
| Speed (vendor) | about 1.5 s for a 2k-token input on a modern x86 CPU | card |
| Training data | **not stated** | – |

## Usage
```python
from transformers import AutoModelForSequenceClassification
m = AutoModelForSequenceClassification.from_pretrained(
    'vectara/hallucination_evaluation_model', trust_remote_code=True)
m.predict([(premise, hypothesis), ...])   # use predict(), not m(pairs)
```
The pipeline prompt template is `"<pad> Determine if the hypothesis is true given the premise?\n\nPremise: {text1}\n\nHypothesis: {text2}"`, with the flan-t5-base tokenizer.

On a Mac it should run on CPU through PyTorch. MPS support and Mac latency are **not stated** and need to be measured. *(Measured: it runs on PyTorch MPS, separate env with `transformers` < 4.50.)*

## Reported performance
- **Vendor (card)**, balanced accuracy:
  - AggreFact-SOTA **76.55**
  - RAGTruth-Summ **64.42**
  - RAGTruth-QA **74.28**
  - The GPT-4 zero-shot comparison on the same data is 73.78 / 62.62 / 74.11.
  - Threshold and split are not stated.
- **Independent ([[LLM-AggreFact]] leaderboard)**: average BAcc **71.8** (rank 21 of 39). Its RAGTruth column is 69.9, about 4 points below GPT-4o (75.9 average) and 3 points below MiniCheck-FT5.

## Relevance to GroundOne
- It is the **most deployable baseline**: permissively licensed, small, CPU-friendly, and with the same (context, sentence) → P(supported) interface. Its `consistent` probability can go straight into the AUROC and ECE computation for the comparison ([[Calibration]], [[Expected Calibration Error]]).
- It was meant as a **latency reference** on the M4. *(Outcome: measured sentence by sentence without batching, 2.52 s per answer at K ≥ 14; not comparable with GroundOne's in-process MLX timing, so no latency claim is made.)*
- **Caveats**: the training data is undisclosed, so overlap with RAGTruth or AggreFact cannot be ruled out. The "unlimited context" claim is unexplained. Treat the vendor's comparisons with GPT-4 as claims, not measurements.

## Links
[[Vectara 2024 - HHEM-2.1-Open model card]], [[Tang 2024 - LLM-AggreFact Leaderboard]], [[LLM-AggreFact]], [[RAGTruth]], [[MiniCheck]], [[AlignScore]], [[Hallucination Detection]], [[Groundedness Verification]], [[When System One Beats an LLM]], [[GroundOne]]

## Measured in the thesis (2026-10-10)
HHEM-2.1-open: T1 AUROC 0.821, T3 AUROC 0.795 (binary only). See [[GroundOne Results]], [[Datasets for GroundOne]].
