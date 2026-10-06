---
type: concept
tags: [concept, dataset, synthetic-data, training-data, minicheck, grounding]
---
# MiniCheck Synthetic Data (C2D / D2C)

> **Not used in the final GroundOne dataset (2026-10-06):** binary labels only; training uses [[RAGTruth]] alone. See [[Datasets for GroundOne]].

The **C2D** and **D2C** datasets are the GPT-4-generated training data of [[MiniCheck]] ([[Tang 2024 - MiniCheck]]), released on Hugging Face as `lytang/C2D-and-D2C-MiniCheck` ([[Dataset card - MiniCheck C2D-D2C]]). They are designed so that a claim can only be verified by checking **several facts against several sentences** of a document.

## How they are built
- **C2D (claim → document)**, 7,076 examples. Starts from about 400 human-written Wikipedia claims. GPT-4 decomposes each claim into atomic facts, expands each fact into a sentence pair, and writes a document; removing one supporting sentence produces an unsupported variant. Sub-claims are paired via the power set ([[Tang 2024 - MiniCheck]] §3).
- **D2C (document → claim)**, 7,319 examples. Starts from about 300 human-written Google News articles (Nov 2023 onward). GPT-4 summarises chunks into claims; augmentation removes sentences and pairs each claim with other chunks of the same document.
- **Labels come from construction**, not from human annotation: whether the needed sentence is present determines the label. Human spot-check agreement was 80 % (C2D) and 78 % (D2C) on 40 + 40 samples ([[Tang 2024 - MiniCheck]] App. A.3).
- Schema: `claim`, `doc`, `label` (binary). **Licence: MIT** ([[Dataset card - MiniCheck C2D-D2C]]).

## Measured properties (GroundOne Phase 1a EDA)
From [[GroundOne 2026 - EDA report]] (Qwen2.5 tokens):
- 14,395 pairs: C2D 7,076, D2C 7,319.
- Supported rate: **0.58 (C2D), 0.35 (D2C)** (consistent with the paper's 42 % / 65 % negatives).
- Document length: median **188 tokens** (p90 276); claims median 17 tokens; 2.34 claims per document.
- Much shorter than many [[LLM-AggreFact]] documents (test median 530; ClaimVerify/WiCE p90 3,600–4,700).
- **No overlap** (documents or claims) with LLM-AggreFact.
- Binary only: no three-way labels, no rules, ~2 claims per document (no natural K).

## Role in GroundOne
- **X1 training**: all 14,395 pairs, binary. Using the same synthetic data as MiniCheck makes the GroundOne-vs-MiniCheck comparison **data-matched**: differences then come from the backbone and readout (decoder + logit readout vs encoder), not the data.
- MiniCheck's training order (all but D2C for 2 epochs, then D2C for 1 epoch) is a reference schedule ([[MiniCheck]]).
- Not usable for X2–X5 or X7; at most a synthetic dev slice for X6.

## Links
[[MiniCheck]], [[Tang 2024 - MiniCheck]], [[Dataset card - MiniCheck C2D-D2C]], [[GroundOne 2026 - EDA report]], [[Datasets for GroundOne]], [[ANLI]], [[LLM-AggreFact]], [[GroundOne]]
