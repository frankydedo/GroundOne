---
type: concept
tags: [concept, model, factual-consistency, encoder, roberta, baseline]
---
# AlignScore

**AlignScore** ([[Zha 2023 - AlignScore]], ACL 2023) is a factual-consistency metric built on a RoBERTa "information alignment" function. The function was trained on **4.7M examples converted from 7 tasks**: NLI, fact verification, paraphrase, STS, QA, IR and summarization. Before [[MiniCheck]] it was the strongest specialized checker.

## Architecture
- **Backbone**: RoBERTa-base (125M) or **RoBERTa-large (355M)**, with three heads: 3-way (aligned / contradict / neutral), binary, and regression.
- **Score**:
  - The context is split into chunks of about **350 whitespace tokens** at sentence boundaries, because RoBERTa has a **512-token limit**. The claim is split into sentences.
  - Each claim sentence takes its maximum P(ALIGNED) over all chunks, from the 3-way head.
  - The final score is the **mean** over claim sentences.
  - The score lies in [0,1].
- **Training**: 3 epochs, batch 32, lr 1e-5 with AdamW. The large model took 532 GPU-hours on 4×A5000.

## Reported results
- **Own paper**:
  - SummaC AUC-ROC average 88.6, and BAcc 82.0 with thresholds tuned on validation.
  - TRUE AUC-ROC average 87.4, or 83.8 on the datasets not seen in training.
- **On [[LLM-AggreFact]]**:
  - 70.4 without threshold tuning ([[Tang 2024 - MiniCheck]] Table 2).
  - **72.2 with dev-tuned thresholds** (Table 7). It was the best prior specialized model in that setting.
  - Leaderboard: 70.5 average, 71.7 on RAGTruth.
- Fine-tuning AlignScore's RoBERTa on MiniCheck's 14K synthetic examples (MiniCheck-RBTA) raises it to 72.7. That gain comes from less than 0.3% of its original training data.

## Ablations worth citing
- The 3-way head beats the binary and regression heads.
- Chunk-level splitting beats both document-level (truncated) and sentence-level splitting.
- **Removing NLI training data improved the metric on most benchmarks** (short premises). Removing QA data hurt the most. See [[Natural Language Inference]].

## How to run
- Code at `github.com/yuh-zha/AlignScore`.
- Checkpoint hosting, licence and Mac/MPS support are **not stated** in the sources.
- At 355M parameters, inference on an M4 Mac should be feasible on CPU or MPS. This is an expectation, not something tested.

## Relevance to GroundOne
- It is the **classic encoder baseline**. It shows the chunk-and-aggregate workaround for short context windows, which a long-context decoder does not need.
- **Evidence for the data mix**: diverse alignment data beats NLI-only data, and QA-derived data matters most. This suggests GroundOne's training mix should not be dominated by MNLI-style short premises.
- **Gap**: AlignScore is about 4.5 BAcc behind the best small checkers on LLM-AggreFact. GroundOne should clearly beat it.

## Links
[[Zha 2023 - AlignScore]], [[MiniCheck]], [[HHEM]], [[LLM-AggreFact]], [[Natural Language Inference]], [[Hallucination Detection]], [[Groundedness Verification]], [[GroundOne]]
