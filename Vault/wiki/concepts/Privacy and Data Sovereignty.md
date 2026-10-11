---
type: concept
tags: [concept, privacy, data-sovereignty, gdpr, cloud-ai, local-inference, locality-pillar]
---
# Privacy and Data Sovereignty

Why it matters where a model runs. With **hosted inference**, every document and prompt is sent to a provider, and what happens to it afterwards (retention, logging, use for training, access by staff or authorities) is governed by contract and policy, which the user cannot inspect. With **local inference** the data never leaves the device, so the question does not arise ([[On-Device Inference]]). This is the first of the four reasons for locality given in the thesis introduction (privacy, offline use, stability, cost).

## What the sources say
- **Academic framing.** On-device inference "eliminates privacy leakage and the need for Internet connections" ([[Qu 2024 - Mobile Edge Intelligence for LLMs, A Contemporary Survey (arXiv 2407.18921)|Qu 2024]] §IV-A, peer-reviewed). Cloud AI has three structural limits: network dependency, privacy and data sovereignty (GDPR, HIPAA), and personalisation ([[Wang 2025 - Cognitive Edge Computing, Optimizing Large Models and AI Agents (arXiv 2501.03265)|Wang 2025]] §3.1; weak preprint, use only for framing). Edge SLMs tuned with LoRA keep "data locality" while approximating LLM outputs in narrow domains ([[Li 2025 - Collaborative Inference between Edge SLMs and Cloud LLMs, A Survey (arXiv 2507.16731)|Li 2025]] §1.3.2).
- **Vendors sell it.** Google markets Gemma 3n's on-device operation as privacy-preserving and offline-ready ([[Google 2025 - Introducing Gemma 3n]]); Apple pairs on-device models with Private Cloud Compute ([[Gunter 2024 - Apple Intelligence Foundation Language Models]]).
- **Concrete case.** In the [[Navier-Stokes Credit Dispute (2026)]], two mathematicians had written their unpublished drafts in OpenAI's Codex. OpenAI denied seeing their work but stated: "While unlikely, we cannot rule out that de-identified data derived from their usage of our products helped improve our models." Whether the drafts were eligible for training may have depended on consumer vs enterprise terms ([[Live Science 2026 - Why would you ruin your career, OpenAI Navier-Stokes claim|Live Science]]). No misuse is shown; the point is that neither user nor provider can verify the absence of it.
- **Regulation.** The EU AI Act and the GDPR shape what hosted providers must disclose; see [[Open-Weight Models]] (EU AI Act section) for the obligations on model providers.
- **Low-quality source.** [[DasRoot 2026 - Privacy-preserving AI, local LLMs vs cloud APIs]] gives the generic framing (local = full data control; cloud compliance depends on the provider) but looks generated and contains non-existent models and contradictory tables: do not cite.

## The honest version of the argument
1. Privacy with a hosted model is a **contractual guarantee**; with a local model it is a **technical** one.
2. The risk with hosted models is **unverifiability**, not proven misuse. The thesis should say exactly this.
3. Locality has costs (capability, memory, energy): see [[On-Device Inference]] and [[Local Inference Hardware]].

## Relevance to GroundOne
- GroundOne never sends a document anywhere: training, calibration, evaluation and serving all run on the laptop, and the network was used only to download public data and open weights once. A verifier is especially sensitive here, because it reads both the private document and the answer.
- Hybrid designs (local verifier, remote generator, or the reverse; [[Edge-Cloud Collaborative Inference]]) would reintroduce the problem for whichever half is remote.

## Links
- Concepts: [[On-Device Inference]], [[Navier-Stokes Credit Dispute (2026)]], [[Open-Weight Models]], [[Edge-Cloud Collaborative Inference]], [[Retrieval-Augmented Generation]]

## GDPR and the best-case hosted design (ingest 2026-10-11, second batch)
- **GDPR** ([[EU 2016 - Regulation (EU) 2016-679, General Data Protection Regulation (GDPR)|Regulation (EU) 2016/679]]): "processing" includes "disclosure by transmission" (Art. 4(2)); a hosted verifier makes the provider a processor (Art. 28 contract); non-EU providers need a transfer basis (Arts. 44–49; adequacy revocable, Art. 45(5)); fines up to €20M/4 % for Arts. 5–9 and 44–49 (Art. 83). A local verifier avoids Arts. 28 and 44–49 by design; Art. 5, lawful basis (Art. 6), security (Art. 32) and possibly a DPIA (Art. 35) still apply. Non-personal confidential documents fall outside the GDPR: there the argument is confidentiality.
- **Apple Private Cloud Compute** ([[Apple Security 2024 - Private Cloud Compute, a new frontier for AI privacy in the cloud]]): hosted AI needs plaintext, so end-to-end encryption is impossible; PCC answers with custom silicon, stateless computation, no privileged access, OHTTP relays and an attested transparency log. Residual trust remains (hardware, supply chain, attestation), verifiable by researchers, not users. Apple calls on-device processing "the cornerstone".
- Thesis use: Ch. 2 §2.1 (Table 2.1) cites both.
