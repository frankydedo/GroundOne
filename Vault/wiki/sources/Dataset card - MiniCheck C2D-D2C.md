---
type: source
author: "Liyan Tang et al. (Hugging Face dataset card, lytang/C2D-and-D2C-MiniCheck)"
date: 2026-10-05
url: https://huggingface.co/datasets/lytang/C2D-and-D2C-MiniCheck
tags: [source, dataset-card, synthetic-data, training-data, minicheck, licence]
---
# Dataset card - MiniCheck C2D-D2C

**Raw file**: `raw/Dataset card - MiniCheck C2D-D2C_ingested.md` (accessed 2026-10-05).

## Overview
The Hugging Face card of the synthetic training data used for [[MiniCheck]]. Short: YAML metadata plus two definitions. Concept page: [[MiniCheck Synthetic Data]].

## Key Insights (as stated in the card)
- **Splits**: `c2d` 7,076 examples, `d2c` 7,319 examples (14,395 total). Download 2.29 MB.
- **Schema**: `claim`, `doc`, `label` (int).
- **Licence**: `mit`. This resolves the "licence not stated in the paper" note in [[Tang 2024 - MiniCheck]].
- **C2D**: starts from a human-written claim; generates synthetic documents that require checking multiple facts in the claim against multiple sentences each.
- **D2C**: starts from a human-written document; generates claims and pairs them with portions of the document, again requiring multi-sentence, multi-fact reasoning.
- The card does not state the generator model; the paper says GPT-4 ([[Tang 2024 - MiniCheck]]).

## Relevance to GroundOne
MIT licence: free to use for fine-tuning and to redistribute derived data. Using all 14,395 pairs makes the comparison with [[MiniCheck]] data-matched.

## Links
[[MiniCheck Synthetic Data]], [[MiniCheck]], [[Tang 2024 - MiniCheck]], [[Datasets for GroundOne]], [[GroundOne 2026 - EDA report]]
