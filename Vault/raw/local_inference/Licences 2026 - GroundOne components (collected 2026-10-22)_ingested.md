---
title: "Licences of the GroundOne components (collected 2026-10-22)"
accessed: 2026-10-22
note: "Hugging Face API (cardData.license, license tags, gating), GitHub licence API, MS MARCO and Yelp Open Dataset pages; full texts of the two non-standard model licences saved alongside"
---

# Licences of models, datasets and software used in GroundOne

## Models (Hugging Face API)

| Repository | license | license_name | gated |
| --- | --- | --- | --- |
| LiquidAI/d1-3B | other | lfm1.0 | False |
| Qwen/Qwen2.5-0.5B-Instruct | apache-2.0 |  | False |
| Qwen/Qwen2.5-3B-Instruct | other | qwen-research | False |
| lmstudio-community/Qwen2.5-0.5B-Instruct-MLX-8bit | apache-2.0 |  | False |
| lmstudio-community/Qwen2.5-3B-Instruct-MLX-8bit | other | qwen-research | False |
| lytang/MiniCheck-RoBERTa-Large | mit |  | False |
| mlx-community/Qwen2.5-3B-Instruct-4bit | other | qwen-research | False |
| rizzoaiacademy/rizzo-flow | apache-2.0 |  | False |
| vectara/hallucination_evaluation_model | apache-2.0 |  | False |

## Datasets

| Dataset | Licence | Notes |
| --- | --- | --- |
| lytang/LLM-AggreFact | cc-by-nd-4.0 | gated: auto; By clicking “Access repository” below, you confirm your understanding that this resource is permitted for use as an evaluation benchmark. Data in the  benchmark should not be used in pretraining or fine-tuning any NLP models. |
| tals/vitaminc | ['cc-by-sa-3.0'] | gated: False;  |
| ParticleMedia/RAGTruth (GitHub) | MIT | contexts from MS MARCO (QA), CNN/DailyMail and recent news (summarisation), Yelp Open Dataset (data-to-text) |

## Upstream sources of RAGTruth contexts

- MS MARCO (microsoft.github.io/msmarco): "The MS MARCO datasets are intended for non-commercial research purposes only to promote advancement in the field of artificial intelligence and related areas, and is made available free of charge without extending any license or other intellectual property rights."
- Yelp Open Dataset (business.yelp.com/data/resources/open-dataset): "The Yelp Open Dataset is a subset of Yelp data that is intended for educational use."
- CNN/DailyMail: news articles; no explicit licence on the texts was checked here.

## Software (GitHub licence API)

| Repository | SPDX |
| --- | --- |
| ml-explore/mlx | MIT |
| ml-explore/mlx-lm | MIT |
| ml-explore/mlx-swift | MIT |
| ml-explore/mlx-swift-lm | MIT |
| nipunsadvilkar/pySBD | MIT |
| pytorch/pytorch | NOASSERTION (BSD-style licence text) |
| huggingface/transformers | Apache-2.0 |
| ggml-org/llama.cpp | MIT |
| Rizzo-AI-Academy/rizzo-flow | Apache-2.0 (README: same licence as the Spark-X2.5 models it runs) |

## Key clauses of the non-standard model licences

- Qwen Research License (Qwen2.5-3B): "Non-Commercial" shall mean for research or evaluation purposes only. ... If you are commercially using the Materials, you shall request a license from us. Attribution notice required in copies.
- LFM Open License v1.0 (d1-3B): rights for Commercial Use are conditioned upon not exceeding the Threshold (annual revenue of USD 10,000,000 or more); qualified non-profits exempt for non-commercial/research purposes.
