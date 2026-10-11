---
title: "Artificial Analysis - Announcing the Openness Index"
url: https://artificialanalysis.ai/articles/announcing-artificial-analysis-openness-index
published: 2025-12-01
accessed: 2026-10-11
extracted_with: trafilatura 2.3.1
---

December 1, 2025

# Introducing the Artificial Analysis Openness Index

We're introducing the Artificial Analysis Openness Index - a standardized, independently-assessed measure of how 'open' AI models are across their availability and transparency around methodology and data.

Openness is critical for stakeholders across the AI ecosystem - it allows:

- Researchers to understand the inputs and behaviors of models with greater nuance, and to build and iterate on innovations in methodology and training
- Developers to host and use models in the most appropriate way for their use case, and train models to replicate or augment model capabilities
- Consumers to understand models' provenance, biases, and other implications of training data or methodology

Openness Index Scoring (selected models)

## Why an Openness Index is Needed

The AI ecosystem and industry place strong value on openness and visibility of progress, but there is a key gap in the communication and understanding of these same concepts. Today, openness is hard to describe or navigate, and is frequently misunderstood.

Models are commonly referred to as 'open' or 'closed' based on whether you can access their weights. However, accessing and using a model involves more nuance than weights alone, due to licensing requirements. Further, to fully analyze or replicate a model there's much more to the story.

We believe that AI model builders deserve better metrics to communicate how open their models are, and what role they're intended to serve in the AI ecosystem. These same metrics also support consumers and developers in understanding openness and making choices about which models to use or build with.

Modern language models differ across architecture, training data, methodology, and code. Yet there's often little transparency about these decisions, inputs, and tradeoffs, making it difficult for researchers to replicate or build on work. Innovations and transparent releases such as DeepSeek R1 have accelerated progress by sharing the 'how' of their models.

## Methodology

We developed a qualitative rubric approach to the Index which reflects our view of the key things making models 'open' or 'closed' today beyond just the model weights.

We recognize that openness involves tradeoffs. Competition and safety considerations could both prevent sharing information, regulatory compliance may require access or usage limitations, and some data may be appropriate for training but not disclosure. The Index measures degree of openness without presuming an 'optimal' score for any particular scenario.

- To understand model availability and model transparency, we analyze the openness of the model weights, pre-training data, post-training data and methodology. We consider both how access to these is shared and the licensing that governs their use
- The Artificial Analysis Openness Index uses a points system to categorize models across these areas which is then summed into the model's Artificial Analysis Openness Index score. This score supports comparison between models with higher scores indicating greater overall openness

Openness Index High-level Methodology

[Download detailed methodology document (PDF)](https://artificialanalysis.ai/downloads/AA-Openness-Index-Spec_V1-0.pdf)

## Initial Findings

Today's AI models show a wide range of degrees of openness, but no models we evaluated for the release of the Openness Index reached the full possible score on the Index.

- Few models and providers take a fully open approach. We see a strong and growing ecosystem of open weights models, including leading models from Chinese labs such as Kimi K2, Minimax M2, and DeepSeek V3.2. However, releases of data and methodology are much rarer - OpenAI’s gpt-oss family is a prominent example of open weights and Apache 2.0 licensing, but minimal disclosure otherwise.
- OLMo from Allen AI (AI2) leads the Openness Index at launch. Living up to AI2’s mission to provide ‘truly open’ research, the OLMo family achieves the top score of 89 on the Index by prioritizing full replicability and permissive licensing across weights, training data, and code. With the recent launch of OLMo 3, this included the latest version of AI2’s data, utilities and software, full details on reasoning model training, and the new Dolci post-training dataset.
- The NVIDIA Nemotron family is also highly open. Models such as NVIDIA Nemotron Nano 9B v2 reach a score of 67 on the Index due to their release alongside extensive technical reports detailing their training process, open source tooling for building models, and the Nemotron-CC and Nemotron post-training datasets. Model Availability versus Model Transparency (selected models)

## Using the Openness Index

The Artificial Analysis Openness Index can be used in conjunction with our intelligence measurement to fully understand model options. We hope that this will create a reference point for researchers and labs to navigate tradeoffs and benefits around greater openness in the model ecosystem.

Explore the full Openness Index rankings on our [Openness Index evaluation page](https://artificialanalysis.ai/evaluations/artificial-analysis-openness-index).

#### Read the latest

[Announcing Harvey LAB-AA v1.1: adding hallucination checks to raise the bar for agentic legal workHarvey LAB-AA v1.1 adds hallucination auditing with a new Hallucination-Gated All-Pass Rate headline metric, a three-judge grading panel, and Harvey's latest private dataset with improved tasks and criteria.October 8, 2026](https://artificialanalysis.ai/articles/harvey-lab-aa-v1-1)

[Introducing trusted-access models to the Artificial Analysis Cyber IndexGPT-6 Sol (Daybreak Blue) now leads the Cyber IndexOctober 8, 2026](https://artificialanalysis.ai/articles/trusted-access-models-cyber-index)

[Anthropic has released Claude Haiku 5.5Claude Haiku 5.5 scores 43 on the Artificial Analysis Intelligence Index, up 26 points one year after the last Haiku releaseOctober 7, 2026](https://artificialanalysis.ai/articles/claude-haiku-5-5)
