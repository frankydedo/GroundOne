---
title: "WilmerHale 2025 - Commission guidelines for providers of general-purpose AI models"
url: https://www.wilmerhale.com/en/insights/blogs/wilmerhale-privacy-and-cybersecurity-law/20250724-european-commission-issues-guidelines-for-providers-of-general-purpose-ai-models
published: 2025-07-24
accessed: 2026-10-11
extracted_with: trafilatura 2.3.1
---

On July 18, 2025, the European Commission published its [guidelines](https://digital-strategy.ec.europa.eu/en/policies/guidelines-gpai-providers) on the scope of obligations for providers of general-purpose artificial intelligence (GPAI) models under Regulation (EU) 2024/1689 (AI Act). The publication of these GPAI guidelines complements the release of the [GPAI Code of Practice](https://digital-strategy.ec.europa.eu/en/policies/contents-code-gpai), a voluntary compliance mechanism that plays a central role in the interim regulatory landscape. The code offers practical guidance to AI model providers on how to fulfill core requirements of the AI Act, with a particular focus on the requirements in Articles 53 and 55 regarding transparency, copyright compliance and systemic risk mitigation (see our previous [blog post](https://www.wilmerhale.com/en/insights/blogs/wilmerhale-privacy-and-cybersecurity-law/20250715-another-eu-ai-act-milestone-nearly-final-version-of-the-general-purpose-ai-code-of-practice-published) for more details).

This blog post outlines the GPAI guidelines’ key provisions and definitions. The release of the guidelines marks another critical step toward the AI Act’s phased implementation. Designed to clarify legal obligations for GPAI providers, the guidelines provide technical and procedural clarity on what compliance will require starting August 2, 2025, when obligations for GPAI providers take effect. The European Commission will review the guidelines periodically to reflect technological advances and enforcement experience.

**Background**

- **AI Act.** As explained in a previous [blog post](https://www.wilmerhale.com/en/insights/blogs/wilmerhale-privacy-and-cybersecurity-law/20241002-navigating-generative-ai-under-the-european-unions-artificial-intelligence-act), the AI Act introduces specific obligations for providers of GPAI models, which are capable of performing a wide range of tasks and integrating into various systems.
  - **GPAI Provider Obligations.** Providers of GPAI models must maintain detailed technical documentation, publish summaries of training data, comply with European Union (EU) copyright law, and share information with regulators and downstream users.
  - **GPAI Models With Systemic Risk.** Providers offering GPAI models with systemic risk face stricter requirements, including model evaluations, risk mitigation, incident reporting and cybersecurity measures.
- **GPAI Guidelines.** The guidelines interpret the AI Act’s provisions regarding GPAI models, helping developers to determine whether their models fall within the scope of the act and to understand what their responsibilities are. To that end, the guidelines clarify what constitutes a GPAI model, how to estimate training compute, who qualifies as a provider and what it means to place a model on the market.

**What Qualifies as a GPAI Model?**

The AI Act defines a GPAI model as an AI model––a concept that the act leaves undefined––that displays significant generality and is capable of competently performing a wide range of distinct tasks regardless of the way the model is placed on the market, and that can be integrated into a variety of downstream systems or applications. The concept of a GPAI model excludes AI models that are used for research, development or prototyping activities before they are placed on the market (Article 3(63), AI Act).

The European Commission considers that, given the wide variety of capabilities and use cases for GPAI models, it is not feasible to provide a precise list of capabilities that a model must display or tasks that it must be able to perform to be considered a GPAI model. Instead, the European Commission’s approach is to set an indicative criterion for identifying GPAI models by considering the amount of computational resources used to train the model and the modalities of the model.

- **Training Compute.** One of the more notable features of the guidelines is the use of “training compute” as a core metric for determining whether a model qualifies as a GPAI model within the meaning of the AI Act. The guidelines define such training compute as the cumulative number of floating point operations per second (FLOPs)—computing operations—used to train a model. This approach is intended to offer providers a consistent benchmark for determining their regulatory responsibilities.
- **Compute Threshold Defined.** The guidelines stipulate that models exceeding 10^23 FLOPs are presumptively considered GPAI models within the meaning of the AI Act. This threshold aligns with models that are capable of generative tasks (text, image, video) and are trained with approximately one billion parameters. Models that cross the 10^25 FLOPs threshold are presumed to carry systemic risk. Providers must notify the European Commission’s AI Office within two weeks of meeting this threshold. A significant number of providers globally have developed models that surpass this threshold. The European Commission may also consider whether a GPAI model presents systemic risk, based on various technical criteria that the European Commission may amend in the future.
- **Estimation.** Providers must maintain records documenting their compute estimation methodology, which can be hardware-based (e.g., GPU tracking) or architecture-based, provided that accuracy falls within a 30% error margin.

**Modification Can Create Provider Obligations**

The AI Act notes that GPAI models may be modified or fine-tuned into new models without specifying the conditions under which downstream modifiers should be considered providers of the modified GPAI models (Recital 97, AI Act). The European Commission considers that not every modification leads to the downstream modifier being deemed the provider.

- **Significant Change.** Entities making modifications to an existing GPAI model that lead to a “significant change” in the model’s generality, capabilities or systemic risk may be considered providers under the AI Act. This is particularly relevant for commercial actors repurposing GPAI models for sector-specific tools, including in health tech, finance and marketing.
- **Threshold.** An indicative criterion for when a downstream modifier is considered the provider of a GPAI model is that the training compute used for the modification is greater than one-third of the training compute of the original model. Where original compute metrics are unavailable, alternative criteria apply. If the original model presents a systemic risk, the threshold should be replaced with one-third of the threshold for a model being presumed to present such a risk (i.e., currently 10^25 FLOPs). Otherwise, it should be replaced with one-third of the threshold for a model being presumed to be a GPAI model (i.e., currently 10^23 FLOPs).

**Open-Source Exemptions**

For providers of AI models that are released under a free and open-source license, as long as the model does not present a systemic risk, the AI Act provides exemptions from the following obligations (Articles 53 and 54, AI Act):

- The obligation to draw up and keep up-to-date the technical documentation of the model, including its training and testing process and the results of its evaluation.
- The obligation to draw up and keep up-to-date information and documentation and make them available to providers of AI systems who intend to integrate the GPAI model into their systems.
- The obligation to appoint an authorized representative for providers of models established outside the European Union.

The guidelines clarify that these exemptions apply provided the following cumulative conditions are met:

- The model is released under a license allowing unrestricted access, use, modification and distribution. Information about model parameters, including the details of the weights, architecture and model usage, must be made publicly available.
- The provider does not monetize the model, directly or indirectly. Monetization includes models that are dual licensed or that require user data in exchange for access. However, the European Commission considers that monetization does not include models provided together with purely optional paid services that do not affect the usability or free usage of the model (e.g., a business model that offers commercial services unrelated to the open-source license). Likewise, monetization does not include paid services or support made available alongside the model, without any purchase obligation, as long as the model’s usage and its free and open access are guaranteed. Such services or support could include premium versions of the model with advanced features or additional tools, update systems, extensions, or plug-ins that help users work with the open-source model or extend its functionality.
- The model does not meet the systemic risk threshold.

**Life Cycle Compliance and Documentation**

The guidelines reinforce that the provider’s obligations span the full life cycle of a model, from the initial pretraining run through to market deployment. Documentation under Article 53(1) must be kept current and made available to downstream deployers and regulatory authorities.

The guidelines also specify that this documentation should:

- Be drawn up for each model placed on the EU market.
- Include information on training methodologies, compute usage and distribution channels.
- Address how providers comply with EU copyright law, including rights reservations under Directive (EU) 2019/790, which governs the lawful use of protected content in training data. Open-source models are not exempted from the obligation to put in place a policy to comply with EU copyright law. Such policy must be applied throughout the entire life cycle of each of the provider’s relevant models. Providers may choose to develop one policy and apply it to all of their relevant models.

**Next Steps**

- **Phased Implementation.** The AI Act’s obligations for GPAI models will apply starting August 2, 2025. Providers of GPAI models placed on the market after this date will instantaneously be required to comply. However, the European Commission’s enforcement powers will apply only as from August 2, 2026. During this one-year enforcement gap, the European Commission will still be able to enforce the AI Act’s provisions for GPAI models, based on a “qualified alert” issued by the “scientific panel,” an advisory body composed of independent AI experts (Article 90(2), AI Act). Providers of GPAI models placed on the market before August 2, 2025, will be expected to comply as from August 2, 2027.
- **Code of Practice.** Providers adopting the GPAI Code of Practice may benefit from smoother supervisory interactions with the European Commission’s AI Office. Participation can also serve as evidence of good-faith efforts to comply with the AI Act during the transition period.
  -  Specifically, the European Commission’s [Q&A](https://digital-strategy.ec.europa.eu/en/faqs/questions-and-answers-code-practice-general-purpose-ai) on the GPAI Code of Practice indicates that even if providers do not implement all commitments immediately after signing the code, the AI Office will not consider them to have broken their commitments and will not reproach them for violating the AI Act.
  - However, as explained above, from August 2, 2026, the European Commission will use fines and other penalties to enforce full compliance with all obligations for providers of GPAI models.
- **Enforcement and Penalties.** Enforcement tools include requests for documentation, model evaluations, risk mitigation orders and fines. Noncompliance can result in fines of up to €15 million or 3% of global revenue, whichever is higher (Article 101, AI Act).

*For more information on this or other AI matters, please contact one of the authors.  The authors would like to thank Jess Miller for her assistance in preparing this blog post.*
