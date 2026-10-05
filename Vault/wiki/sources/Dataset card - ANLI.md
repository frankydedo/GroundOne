---
type: source
author: "Hugging Face dataset card for facebook/anli (dataset by Nie et al., Facebook AI Research)"
date: 2026-10-05
url: https://huggingface.co/datasets/facebook/anli
tags: [source, dataset-card, dataset, nli, anli, licence]
---
# Dataset card - ANLI

**Raw file**: `raw/Dataset card - ANLI_ingested.md` (README of `facebook/anli`, accessed 2026-10-05).

## Overview
The Hugging Face card for **[[ANLI]]** (Adversarial NLI). Most prose sections are "[More Information Needed]"; the useful content is the YAML metadata, the schema and the split table. Paper: [[Nie 2020 - Adversarial NLI]].

## Key Insights (as stated in the card)
- **Licence**: `cc-by-nc-4.0` (Attribution-NonCommercial), linked to the repository's LICENSE file. This resolves the "licence not stated in paper" note in [[Nie 2020 - Adversarial NLI]].
- **Collection**: "iterative, adversarial human-and-model-in-the-loop procedure"; three rounds, each with train/dev/test. Annotations tagged `crowdsourced` and `machine-generated`; source datasets `original` and `extended|hotpot_qa`.
- **Schema** (`plain_text` config): `uid`, `premise`, `hypothesis`, `label` (0 entailment, 1 neutral, 2 contradiction), `reason` (free-text annotator reason, often empty).
- **Splits**: train_r1 16,946 / dev_r1 1,000 / test_r1 1,000; train_r2 45,460 / 1,000 / 1,000; train_r3 100,459 / 1,200 / 1,200. Download 18.62 MB, generated 77.12 MB.
- Repository: `github.com/facebookresearch/anli`.

## Relevance to GroundOne
- CC BY-NC 4.0 permits non-commercial research use, including fine-tuning for the thesis; derived data must keep attribution and the non-commercial condition.
- Our EDA ([[GroundOne 2026 - EDA report]]) found the `reason` field filled for 16 % of pairs.

## Links
[[ANLI]], [[Natural Language Inference]], [[Nie 2020 - Adversarial NLI]], [[Datasets for GroundOne]], [[GroundOne 2026 - EDA report]]
