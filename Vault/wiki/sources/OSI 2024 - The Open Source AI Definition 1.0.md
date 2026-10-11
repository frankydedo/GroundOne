---
type: source
author: "Open Source Initiative (OSI)"
date: 2024-10-28
venue: "OSI, The Open Source AI Definition, version 1.0, web page (retrieved 2026-10-11)"
url: "https://opensource.org/ai/open-source-ai-definition"
tags: [source, definition, open-source, open-weight, licences, training-data]
---
# OSI 2024 – The Open Source AI Definition 1.0

**Raw file**: `raw/local_inference/OSI 2024 - The Open Source AI Definition 1.0_ingested.md`

## Overview
Version 1.0 (28 October 2024) of the **Open Source AI Definition (OSAID)** by the Open Source Initiative, the body that maintains the Open Source Definition for software. It defines when an AI system, model or set of weights may be called "Open Source". It requires the four freedoms (use, study, modify, share) and access to the "preferred form to make modifications": **data information, code and parameters**. The extraction is complete for the normative text; FAQ, checklist and endorsement pages are linked but not included.

## Key Insights
1. **Four freedoms (derived from the Free Software Definition).** Use the system for any purpose without permission; **Study** how it works and inspect its components; **Modify** it for any purpose, including changing its output; **Share** it, modified or not, for any purpose. They apply both to whole systems and to discrete elements (model, weights).
2. **Preferred form to make modifications** (all three required):
   - **Data Information:** enough detail about the training data that "a skilled person can build a substantially equivalent system". This means a complete description of all training data (including unshareable data: provenance, scope, selection, labelling, filtering), a list of public training data and where to get it, and a list of third-party data (including paid data). Under OSI-approved terms.
   - **Code:** the complete source code to train and run the system (data processing and filtering, training with arguments and settings, validation and testing, tokenizers, hyperparameter search, inference code, architecture). Under OSI-approved licences.
   - **Parameters:** weights and configuration, possibly including intermediate checkpoints and final optimizer state. Under OSI-approved terms.
3. **Data itself need not be released.** Only *data information* is required, not the data. This is the definition's main compromise: unshareable data is allowed if it is fully described.
4. **Models and weights.** An AI model = architecture + parameters + inference code. "Open Source models" and "Open Source weights" must include the data information and code used to derive the parameters. **Weights alone do not qualify.**
5. **Copyleft allowed.** Terms may require modified versions to be released under the same terms.
6. **Definitions.** "AI system" and "machine learning" are taken from OECD texts (OECD/LEGAL/0449, 2024).
7. **Legal mechanism left open.** The OSAID does not prescribe a legal instrument for freeing parameters, and expects clarity "over time".

**Quality notes.** A primary normative text from the standard-setting body. It is a definition, not a measurement; whether a given model complies requires checking its release against the checklist (not ingested). It is contested in the community (e.g. the "data information, not data" compromise), but the raw file contains no such debate.

## Relevance to GroundOne
- **Terminology for the thesis.** Under the OSAID, a model that releases weights (even under Apache 2.0) without full data information and training code is **not** "Open Source AI". Qwen2.5 publishes weights and a technical report, but the report does not release or fully describe the 18T-token pre-training corpus ([[Qwen2.5]]). The thesis should therefore call Qwen2.5 **open-weight** and avoid "open-source model". This inference from the definition should be verified against OSI's checklist before being stated as fact.
- **Licence nuance per size.** Even the weights differ: Qwen2.5-0.5B is Apache 2.0, while Qwen2.5-3B is under the "Qwen Research" licence ([[Qwen2.5]]). The 3B base therefore does not grant OSAID's "use for any purpose" freedom, which matters if GroundOne's 3B adapter is distributed or used commercially ([[Open-Weight Models|Model Licences]]).
- **What GroundOne itself could release.** GroundOne's own layer (training code, dataset-construction code, the data-plan description, LoRA adapters) could in principle meet the code and data-information parts, subject to the licences of RAGTruth, LLM-AggreFact (gated) and VitaminC. This would not make the whole system OSAID-compliant, because the base model's pre-training data is not described.
- **Locality does not need OSAID.** Running locally requires downloadable weights and a permissive enough licence, not full openness. The definition belongs in the thesis's terminology and licence discussion, not as a requirement of the locality pillar.

## Links
- Concepts: [[Qwen2.5]], [[LoRA]], [[Datasets for GroundOne]], [[Open-Weight Models|Open Source AI Definition]] (proposed), [[Open-Weight Models]] (proposed), [[Open-Weight Models|Model Licences]] (proposed)
- Related sources: [[Artificial Analysis - Announcing the Openness Index]], [[Stanford CRFM 2024 - Foundation models under the EU AI Act]], [[WilmerHale 2025 - Commission guidelines for providers of general-purpose AI models]], [[Qwen Team 2024 - Qwen2.5 Technical Report]]
