---
type: source
author: "Artificial Analysis"
date: 2025-12-01
venue: "Artificial Analysis blog article (retrieved 2026-10-11)"
url: "https://artificialanalysis.ai/articles/announcing-artificial-analysis-openness-index"
tags: [source, blog, openness, open-weight, licences, transparency, training-data]
---
# Artificial Analysis – Announcing the Openness Index

**Raw file**: `raw/local_inference/Artificial Analysis - Announcing the Openness Index_ingested.md`

## Overview
Announcement (1 December 2025) of the **Artificial Analysis Openness Index**, a points-based, independently assessed rubric that scores how "open" a model is. It looks beyond whether the weights are downloadable to cover **licensing, pre-training data, post-training data and methodology**, grouped under "model availability" and "model transparency". The article gives the motivation, a high-level method and initial findings. Charts (scores of selected models, availability vs transparency) did not survive extraction, and the detailed rubric is in a linked PDF that was not ingested. The extraction ends with an unrelated "Read the latest" sidebar of October 2026 news items (boilerplate, ignored).

## Key Insights
1. **Motivation.** Models are usually called "open" or "closed" according to whether the weights can be accessed. Artificial Analysis argues this is insufficient: licensing restricts use, and replication needs data and method as well.
2. **Method.** A qualitative rubric scores openness of **weights, pre-training data, post-training data and methodology**, considering both *how access is shared* and *the licence governing use*. Points are summed into one score; higher means more open. No "optimal" score is presumed: competition, safety, regulation and data rights are acknowledged as legitimate reasons to withhold.
3. **Initial findings.**
   - No evaluated model reached the maximum score (the maximum is not stated in the text).
   - Open-weight releases are common (Kimi K2, MiniMax M2, DeepSeek V3.2 are named), but data and method releases are rare. **OpenAI's gpt-oss** is the example of open weights under **Apache 2.0** with minimal other disclosure.
   - **AI2's OLMo** leads with **89**: full replicability and permissive licensing across weights, training data and code (OLMo 3 includes the Dolci post-training dataset).
   - **NVIDIA Nemotron Nano 9B v2** scores **67**, thanks to technical reports, open tooling, and the Nemotron-CC and post-training datasets.
4. **Intended use.** To be read together with the Artificial Analysis Intelligence Index, to weigh capability against openness.

**Quality notes.** Artificial Analysis is a commercial benchmarking company, so this is its own product announcement. The scores are its assessments under its own rubric (version 1.0). Only two scores are given in the text, and Qwen models are not mentioned, so the extraction gives no score for Qwen2.5.

## Relevance to GroundOne
- **Vocabulary for the thesis.** It supports writing "**open-weight**" rather than "open-source" for Qwen2.5. Weight availability and openness of data and method are separate axes, and most open-weight models, Qwen included, release weights and a report but not the full training data ([[Open-Weight Models]], [[Open-Weight Models|Model Licences]]).
- **What locality actually needs.** For GroundOne's locality pillar, the necessary properties are weight availability, a licence that allows local fine-tuning and use, and logit access. Full data transparency (the OLMo end of the scale) is desirable for reproducibility but not required to run locally. The thesis can state this distinction explicitly.
- **Possible robustness note.** A fully open base (e.g. OLMo) would make the whole pipeline replicable down to pre-training data. The thesis does not use one; this can be listed as a limitation or future work, not as a claim.

## Links
- Concepts: [[Qwen2.5]], [[On-Device Inference]], [[Open-Weight Models]] (proposed), [[Open-Weight Models|Model Licences]] (proposed), [[Open-Weight Models|Open Source AI Definition]] (proposed)
- Related sources: [[OSI 2024 - The Open Source AI Definition 1.0]], [[Epoch AI - Open vs closed capability gap (ECI)]], [[Stanford CRFM 2024 - Foundation models under the EU AI Act]]
