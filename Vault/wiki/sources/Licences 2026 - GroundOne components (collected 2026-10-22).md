---
type: source
author: "Hugging Face and GitHub licence metadata; Alibaba Cloud; Liquid AI; Microsoft (MS MARCO); Yelp"
date: 2026-10-22
venue: "Licence fields from the Hugging Face and GitHub APIs, full texts of the Qwen Research License and the LFM Open License v1.0, MS MARCO and Yelp Open Dataset terms"
tags: [source, licences, open-weight, datasets, locality-pillar, independence]
---
# Licences 2026 – GroundOne components (collected 2026-10-22)

**Raw files**: `raw/local_inference/Licences 2026 - GroundOne components (collected 2026-10-22)_ingested.md`, plus `Alibaba Cloud 2024 - Qwen Research License Agreement (Qwen2.5-3B)_ingested.txt` and `Liquid AI 2025 - LFM Open License v1.0 (d1-3B)_ingested.txt`

## Key Insights
- **Models:** Qwen2.5-0.5B-Instruct Apache 2.0; **Qwen2.5-3B-Instruct Qwen Research License** ("Non-Commercial shall mean for research or evaluation purposes only"; commercial use requires a licence from Alibaba Cloud; attribution notice); the MLX conversions (lmstudio-community 8-bit, mlx-community 4-bit) inherit them. MiniCheck-RoBERTa-Large MIT; HHEM-2.1-open Apache 2.0; Rizzo-Flow (Spark-X2.5 4B + LoRA) Apache 2.0; **d1-3B LFM Open License 1.0** (commercial use only below USD 10 M annual revenue).
- **Data:** RAGTruth annotations MIT, but contexts from MS MARCO ("non-commercial research purposes only"), Yelp Open Dataset ("intended for educational use") and CNN/DailyMail news; LLM-AggreFact CC BY-ND 4.0 with a gating condition (evaluation only, no pretraining or fine-tuning); VitaminC CC BY-SA 3.0.
- **Software:** MLX, mlx-lm, MLX Swift, mlx-swift-lm, pySBD, llama.cpp MIT; Transformers Apache 2.0; PyTorch BSD-style.

## Relevance to GroundOne
- Thesis Ch. 6 §"Licenze e condizioni d'uso" (Table 6.1): every component runs locally under licences that allow research use (independence holds legally too). **GroundOne 3B and the demo generator are research-only** (Qwen Research License); a commercial deployment would need the 0.5B (Apache 2.0 base) or another permissive base. The training contexts' upstream terms are a further reason to treat the adapters as research artefacts.

## Links
- [[Open-Weight Models]], [[Privacy and Data Sovereignty]], [[Qwen2.5]], [[RAGTruth]], [[LLM-AggreFact]], [[VitaminC]], [[Demo Application]]
