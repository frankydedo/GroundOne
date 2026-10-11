---
type: source
author: "Rishi Bommasani, Alice Hau, Kevin Klyman, Percy Liang (Stanford CRFM)"
date: 2024-08-01
venue: "Stanford Center for Research on Foundation Models, blog post (retrieved 2026-10-11)"
url: "https://crfm.stanford.edu/2024/08/01/eu-ai-act.html"
tags: [source, policy, eu-ai-act, regulation, general-purpose-ai, open-models, systemic-risk]
---
# Stanford CRFM 2024 – Foundation models under the EU AI Act

**Raw file**: `raw/local_inference/Stanford CRFM 2024 - Foundation models under the EU AI Act_ingested.md`

## Overview
A Stanford CRFM analysis published on **1 August 2024**, the day the EU AI Act (Regulation (EU) 2024/1689) entered into force. (The YAML header says `published: 2025-05-02`, probably a page update; the URL, text and BibTeX give August 2024.) The authors **code** the Act's obligations for general-purpose AI (GPAI) models by type (disclosure vs substantive), recipient (government, downstream providers, public) and scope (all providers, open non-systemic, closed non-systemic, systemic-risk). They then compare the final Act with the European Parliament position of June 2023 and the Stanford proposal of December 2023. The extraction is complete except for the linked coding spreadsheet and any figures.

## Key Insights
1. **Structure of the Act.** More than 100 pages, **113 articles, 12 annexes**. GPAI obligations sit in **Chapter V (Articles 51–56)** with **Annexes XI–XIII**. GPAI obligations take effect **2 August 2025**; codes of practice were due by **2 May 2025** (Art. 56).
2. **GPAI definition.** A model "that displays significant generality and is capable to competently perform a wide range of distinct tasks… and that can be integrated into a variety of downstream systems". It **does not cover models used before release on the market for research, development and prototyping**.
3. **Coding result.** **25 requirements** across **4 classes** of GPAI provider. Most are **information disclosures** to governments and/or downstream providers. There is **one** public-facing disclosure: a "sufficiently detailed summary of training data".
4. **Systemic risk.** Substantive duties (model evaluation, risk mitigation, incident reporting, cybersecurity) apply mainly to systemic-risk models. Non-systemic GPAI has a single substantive duty: **copyright compliance**. The default presumption is **≥ 10^25 training FLOPs**. As of August 2024, Epoch estimates put **8 models** from 7 developers above it: Gemini 1.0 Ultra, Llama 3.1-405B, GPT-4, Mistral Large, Nemotron-4 340B, MegaScale, Inflection-2, Inflection-2.5. Annex XIII lists alternative criteria (data, evaluations, business users, registered end-users).
5. **Open-model exemption (Art. 53).** Many obligations "do not apply to providers of AI models that are released under a free and open-source licence", except for models with systemic risk. CRFM notes that open-weight models are often **not** released under OSI-compliant licences, which makes the licence question central.
6. **Comparison with earlier proposals.** The Parliament and Stanford texts stressed public transparency; the Act has only one public disclosure. The Act and the Stanford proposal share a two-tier structure, but the Act's default tiering criterion is compute, while Stanford's was demonstrated market impact. The Act has **no third-party auditor access** and **no adverse-event reporting**. Penalties: **3% of worldwide turnover or €15M** (whichever is greater), up from 2% / €10M in the Parliament position.

**Quality notes.** An expert academic policy analysis by authors involved in the legislative debate, so it argues partly for its own proposal. It is from August 2024 and predates the Commission's July 2025 GPAI guidelines, which add the 10^23 FLOPs indicative GPAI threshold and conditions for the open-source exemption ([[WilmerHale 2025 - Commission guidelines for providers of general-purpose AI models]]). Not legal advice.

## Relevance to GroundOne
- **GroundOne is outside the GPAI provider regime, as far as these sources show.** It is a research prototype that is not placed on the market, which the definition explicitly excludes. It is also a narrow verifier rather than a model with "significant generality". The thesis can say this briefly, citing the Act's definition, without claiming legal certainty.
- **Locality and privacy are a separate legal axis.** The AI Act regulates model providers. The privacy argument for local inference (documents never leave the device) rests mainly on GDPR, which the post mentions only as part of the EU regulatory background. Data-protection arguments should cite GDPR sources, not this page ([[On-Device Inference]]).
- **Licences matter for the exemption.** The open-source exemption depends on a free and open-source licence. Qwen2.5-0.5B (Apache 2.0) and Qwen2.5-3B ("Qwen Research" licence) differ here ([[Qwen2.5]], [[Open-Weight Models|Model Licences]]). This matters for whoever distributes the base model (Alibaba), not for a research user fine-tuning it locally.
- **Useful for Ch. 1–2 context.** Regulation targets large, centrally trained models (10^25 FLOPs). Small local models fall in the lighter tiers or outside the regime, one more reason the ecosystem of small open-weight models is relevant ([[Small Language Models]]).

## Links
- Concepts: [[On-Device Inference]], [[Qwen2.5]], [[Open-Weight Models|EU AI Act]] (proposed), [[Open-Weight Models]] (proposed), [[Open-Weight Models|Model Licences]] (proposed), [[Open-Weight Models|Open Source AI Definition]] (proposed)
- Related sources: [[WilmerHale 2025 - Commission guidelines for providers of general-purpose AI models]], [[OSI 2024 - The Open Source AI Definition 1.0]], [[Artificial Analysis - Announcing the Openness Index]]
