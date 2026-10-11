---
type: source
author: "European Parliament and Council of the European Union"
date: 2016-04-27
venue: "Official Journal of the European Union, L 119, 4.5.2016, p. 1–88; applies from 25 May 2018 (Art. 99(2)); EUR-Lex text retrieved 2026-10-11"
url: "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32016R0679"
tags: [source, legislation, gdpr, eu, privacy, data-protection, processor, third-country-transfers, cloud-ai, locality-pillar]
---
# EU 2016 – Regulation (EU) 2016/679, General Data Protection Regulation (GDPR)

**Raw file**: `raw/local_inference/EU 2016 - Regulation (EU) 2016-679, General Data Protection Regulation (GDPR)_ingested.md`

## Overview
The EU regulation on "the protection of natural persons with regard to the processing of personal data and on the free movement of such data", repealing Directive 95/46/EC. It was adopted on 27 April 2016, published in OJ L 119 on 4 May 2016, and has applied since **25 May 2018** (Art. 99(2)). The full text is long (99 articles and 173 recitals). This page extracts only the provisions that matter when a **document containing personal data is sent to a hosted AI provider** for inference, as opposed to processing it on the user's own machine. It is not a legal summary of the whole Regulation and not legal advice.

## Key Insights
1. **Scope (Arts. 2–3).** The Regulation applies to processing "wholly or partly by automated means" (Art. 2(1)). It does not apply to processing "by a natural person in the course of a purely personal or household activity" (Art. 2(2)(c)). It also applies to controllers or processors **outside the EU** that offer services to people in the Union (Art. 3(2)). Recital 26: the principles "should not apply to anonymous information", but pseudonymised data "should be considered to be information on an identifiable natural person".
2. **Definitions (Art. 4).**
   - **Personal data** (Art. 4(1)): "any information relating to an identified or identifiable natural person", directly or indirectly, e.g. by "a name, an identification number, location data, an online identifier".
   - **Processing** (Art. 4(2)): "any operation or set of operations which is performed on personal data", and the list explicitly includes "**disclosure by transmission**". Sending a document to an API is therefore processing in itself.
   - **Controller** (Art. 4(7)): the body that "determines the purposes and means of the processing". **Processor** (Art. 4(8)): one that "processes personal data on behalf of the controller". **Recipient** and **third party** are defined in Arts. 4(9)–4(10).
3. **Principles (Art. 5(1)).** These include **purpose limitation** ("collected for specified, explicit and legitimate purposes and not further processed in a manner that is incompatible with those purposes", (b)), **data minimisation** ("adequate, relevant and limited to what is necessary", (c)), **storage limitation** ("kept in a form which permits identification of data subjects for no longer than is necessary", (e)), and **integrity and confidentiality** ("appropriate security … including protection against unauthorised or unlawful processing", (f)). Under **accountability**, the controller must "be able to demonstrate compliance" (Art. 5(2)).
4. **Data protection by design and by default (Art. 25).** The controller shall implement "appropriate technical and organisational measures, such as pseudonymisation, which are designed to implement data-protection principles, such as data minimisation, in an effective manner" (Art. 25(1)). By default, "only personal data which are necessary for each specific purpose of the processing are processed", covering "the amount of personal data collected, the extent of their processing, the period of their storage and their accessibility" (Art. 25(2)).
5. **Processors (Art. 28).** The controller "shall use only processors providing sufficient guarantees" (Art. 28(1)), under a binding written contract (Art. 28(3), (9)). The processor:
   - acts "only on documented instructions from the controller, including with regard to transfers of personal data to a third country" (Art. 28(3)(a));
   - ensures confidentiality of its staff (Art. 28(3)(b));
   - deletes or returns all personal data at the end of the service (Art. 28(3)(g));
   - allows "audits, including inspections" (Art. 28(3)(h)).

   It may not engage sub-processors without authorisation (Art. 28(2), (4)). A processor that determines purposes and means itself "shall be considered to be a controller" (Art. 28(10)).
6. **Security (Art. 32).** Controller **and** processor must ensure "a level of security appropriate to the risk", including "the pseudonymisation and encryption of personal data" and "ongoing confidentiality, integrity, availability and resilience" (Art. 32(1)(a)–(b)). Account must be taken of the risks of "unauthorised disclosure of, or access to personal data transmitted, stored or otherwise processed" (Art. 32(2)). Art. 35 adds a **data protection impact assessment** for processing "in particular using new technologies" that is likely to be high-risk.
7. **Transfers to third countries (Arts. 44–49).** Any transfer outside the EU "shall take place only if … the conditions laid down in this Chapter are complied with", including onward transfers (Art. 44). The lawful routes are:
   - an **adequacy decision** by the Commission (Art. 45), which must be reviewed "at least every four years" (Art. 45(3)) and can be repealed or suspended (Art. 45(5));
   - **appropriate safeguards** such as standard data protection clauses or binding corporate rules, "on condition that enforceable data subject rights and effective legal remedies … are available" (Art. 46(1)–(2));
   - narrow **derogations**, e.g. explicit informed consent (Art. 49(1)(a)).
8. **Fines (Art. 83).** Breaches of Arts. 25–39 (which include by-design, processors and security) carry up to **€10,000,000 or 2%** of total worldwide annual turnover, whichever is higher (Art. 83(4)(a)). Breaches of the basic principles (Arts. 5, 6, 7, 9) and of the transfer rules (Arts. 44–49) carry up to **€20,000,000 or 4%** (Art. 83(5)(a), (c)). Whether Art. 25 and Art. 32 measures were implemented counts when setting a fine (Art. 83(2)(d)).

## Relevance to GroundOne
- **What a local verifier avoids by design.** If a RAG verifier is hosted, every check sends the retrieved document and the answer to a provider. That is "disclosure by transmission" (Art. 4(2)) to a **processor** and brings in Art. 28: a contract, sufficient guarantees, sub-processor control, deletion at the end of the service and audits. If the provider or its sub-processors are outside the EU, Chapter V applies as well (Arts. 44–49: adequacy, standard clauses or derogations, and adequacy can be revoked, Art. 45(5)). GroundOne runs entirely on the laptop. No recipient, processor or transfer exists, so these obligations **do not arise**. This is the regulatory form of the thesis's point that privacy becomes a technical property rather than a contractual one ([[Privacy and Data Sovereignty]], [[On-Device Inference]]).
- **Local inference as a by-design measure.** Keeping the data on the device is a direct way to meet data minimisation and restricted "accessibility" (Art. 5(1)(c), Art. 25(2)). It also removes the network transfer from the Art. 32(2) risk surface. The thesis can cite Art. 25 when it presents locality as a design property. It should not claim that the Regulation requires local inference.
- **What still applies (honest limits).** Local processing is still **processing**. An organisation that runs GroundOne on personal data remains a **controller**: it needs a lawful basis (Art. 6), must respect Art. 5, must secure the device (Art. 32; e.g. disk encryption, access control) and may need a DPIA (Art. 35). Only a purely personal use falls outside the Regulation (Art. 2(2)(c)). The GDPR also **does not forbid** hosted AI: with an Art. 28 contract and an Art. 45/46 transfer basis, it is lawful. The argument is about fewer obligations and fewer parties to trust, not about legality.
- **The GDPR covers only personal data.** Confidential documents without personal data, such as trade secrets or unpublished research drafts, are outside its scope (Art. 1, recital 26). For them the locality argument is about confidentiality and verifiability, as in the [[Navier-Stokes Credit Dispute (2026)]], not about the GDPR.
- **Hybrid set-ups.** Any split in which part of the pipeline runs remotely brings the processor and transfer obligations back for that part ([[Edge-Cloud Collaborative Inference]]). Apple's Private Cloud Compute is an engineering attempt to shrink what the provider can see ([[Apple Security 2024 - Private Cloud Compute, a new frontier for AI privacy in the cloud]]).

## Links
- Concepts: [[Privacy and Data Sovereignty]], [[On-Device Inference]], [[Navier-Stokes Credit Dispute (2026)]], [[Edge-Cloud Collaborative Inference]], [[Open-Weight Models]], [[Retrieval-Augmented Generation]]
- Related sources: [[Apple Security 2024 - Private Cloud Compute, a new frontier for AI privacy in the cloud]], [[Stanford CRFM 2024 - Foundation models under the EU AI Act]], [[Gunter 2024 - Apple Intelligence Foundation Language Models]]
