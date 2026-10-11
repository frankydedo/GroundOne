---
type: source
author: "Senyao Li, Haozhao Wang, Wenchao Xu, Rui Zhang, Song Guo, Jingling Yuan, Xian Zhong, Tianwei Zhang, Ruixuan Li (HUST, HKUST, WUT, NTU)"
date: 2025
venue: "arXiv preprint 2507.16731v1 (22 Jul 2025, cs.DC); no peer-reviewed venue stated"
url: "https://arxiv.org/abs/2507.16731"
tags: [source, paper, survey, preprint, edge-cloud, small-language-models, collaborative-inference, speculative-decoding, routing, uncertainty]
---
# Li 2025 – Collaborative Inference and Learning between Edge SLMs and Cloud LLMs: A Survey of Algorithms, Execution, and Open Challenges

**Raw file**: `raw/local_inference/Li 2025 - Collaborative Inference between Edge SLMs and Cloud LLMs, A Survey (arXiv 2507.16731)_ingested.pdf`

## Overview
A 36-page survey of **hybrid systems in which a small language model (SLM) on the edge device cooperates with a large model (LLM) in the cloud**, at inference and at training time. The authors argue that neither cloud-only deployment nor compressing models for the edge is enough, "due to concerns about latency, privacy, cost, and personalization" (abstract). The contribution is a taxonomy: for inference, **task assignment**, **task division** and **mixture** (task-level and token-level); for training, distillation, adapters, bidirectional learning and cloud-guided capability injection. It also lists datasets, benchmarks, privacy methods and industrial deployments.

## Key Insights
1. **Inference taxonomy (§2, Table 2, Fig. 2).**
   - *Task assignment* (§2.1): route each request wholly to the SLM or the LLM, using lightweight scorers, calibrated estimators or bandits; "simple and fast", but hard switching misroutes uncertain inputs.
   - *Task division* (§2.2): routing/forwarding (FrugalGPT cascades, Tabi with calibrated confidence), computation offloading, early exit.
   - *Task-level mixture* (§2.3): decomposition and orchestration across edge and cloud, history-enhanced inference and RAG with self-assessment (Self-RAG reflection tokens, CRAG's lightweight retrieval assessor, SlimPLM triggering retrieval only when the local answer is unreliable).
   - *Token-level mixture* (§2.4): edge draft + cloud verification (speculative decoding and variants), skeleton completion, token-tree verification.
2. **System 1 / System 2 routing (§2.1.1).** FS-GEN treats fast but uncertain SLMs as "System 1" and reliable LLMs as "System 2", invoked when ambiguity arises. LLMCascades accept edge predictions or escalate them to the cloud via voting and verification (§2.2.3).
3. **Hardware complementarity (§1.3.3).** Cloud: multi-GPU clusters (H100, NVLink) running models such as Llama 3 405B. Edge: smartphones with **6–16 GB RAM**, XR headsets, Jetson Orin, running small models for latency-critical tasks. SLMs are cast as "first-response agents or draft generators" that offload complex reasoning only when needed (§1.3.2).
4. **SLM definition (§1.3.2).** SLMs "emphasize responsiveness and local availability over broad reasoning" and, through distillation, LoRA and instruction tuning, "can approximate LLM outputs in narrow domains while maintaining low latency and data locality".
5. **Training-side collaboration (§3).** Pruning and quantization (§3.1), distillation and low-rank approximation (§3.2), adapter-based modular designs with LoRA as the communication bridge in federated settings, e.g. HETLoRA with heterogeneous ranks (§3.4).
6. **Privacy (§5.1).** Training-level protections (federated learning, keeping data local with adapters) and inference-level ones (RemoteRAG with a semantic differential-privacy metric, symbolic masking of sensitive content, privacy-preserving speculative decoding, keeping vector stores in private clouds).
7. **Industry signals (§1).** Qualcomm's 2023 Hybrid AI white papers; Alibaba's Walle system with 300+ tasks and over 10 billion daily invocations.
8. **Open challenge: uncertainty from logits (§6).** Collaborative systems depend on uncertainty estimation for early exit, fallback and switching, yet "normalized softmax probabilities obscure the raw evidential strength encoded in logits". The authors advocate **evidence-based uncertainty from unnormalised logits** (e.g. Dirichlet formulations separating epistemic and aleatoric uncertainty) for trust calibration and escalation.

## Relevance to GroundOne
- **Where GroundOne sits.** GroundOne is an edge-side small model, but it **does not collaborate with a cloud LLM**: the whole pipeline stays local. In this taxonomy it is closest to the SLM role in *task assignment* (a fast specialist that could, in principle, decide whether escalation is needed), but the thesis deliberately takes the stricter position of no cloud fallback. The survey is useful as the map of the alternative (hybrid) design the thesis rejects for locality reasons ([[On-Device Inference]], [[Edge-Cloud Collaborative Inference]]).
- **Support for specialised small models.** §1.3.2 states that SLMs fine-tuned with LoRA can approximate LLMs in narrow domains with low latency and data locality: the GroundOne premise in one sentence ([[Small Language Models]], [[LoRA]]).
- **System One framing.** FS-GEN's SLM-as-System-1 vocabulary (§2.1.1) is an independent use of the dual-process metaphor; GroundOne's "System One" is a narrower sense (one forward pass, no generated tokens) and should not be conflated with it ([[System One Models]]).
- **Logit-based confidence.** §6's call for uncertainty taken from logits rather than sampled text agrees with GroundOne's design (letter-logit readout, temperature + bias calibration, served threshold). GroundOne does not go as far as evidential/Dirichlet uncertainty; that is a possible future-work pointer ([[Letter-Token Readout]], [[Verbalised vs Logit Confidence]], [[Calibration]]).
- **Prefill/decode.** The survey motivates token-level collaboration by the latency of autoregressive decoding (§2.4) and mentions TTFT and per-token time, but gives no prefill/decode cost analysis.
- **Verification/hallucination.** No groundedness or hallucination-checking component on device. "Verification" means the cloud verifying edge draft tokens; hallucination appears only in passing (AutoMix, §2.4.1). CRAG's lightweight retrieval-quality assessor (§2.3.3) is the closest analogue to a local RAG checker, but it scores retrieved documents, not the generated answer ([[Groundedness Verification]]).
- **Quality caveats.** arXiv v1 preprint, no venue. Mostly a catalogue of methods with one-line descriptions. Some statements are inaccurate or unsourced: §1.3.1 says Qwen and DeepSeek are pretrained with masked language modelling (they are autoregressive); §1.3.2 defines SLMs as "millions to a few hundred million" parameters while §1.3.3 speaks of "billion-parameter SLMs (e.g., TinyBERT)"; §1.3.3 gives uncited figures ("90% accuracy in customer service", "LoRA boosting medical QA accuracy by 20%", "40% efficiency gains"). Cite it for the taxonomy only.

## Links
- Concepts: [[On-Device Inference]], [[System One Models]], [[LoRA]], [[Calibration]], [[Letter-Token Readout]], [[Verbalised vs Logit Confidence]], [[Retrieval-Augmented Generation]], [[Mixture of Experts]], [[Groundedness Verification]]; proposed: [[Edge-Cloud Collaborative Inference]], [[Small Language Models]], [[Edge-Cloud Collaborative Inference|Speculative Decoding]], [[Quantization]]
- Related sources: [[Qu 2024 - Mobile Edge Intelligence for LLMs, A Contemporary Survey (arXiv 2407.18921)]], [[Wang 2025 - Cognitive Edge Computing, Optimizing Large Models and AI Agents (arXiv 2501.03265)]], [[Asai 2024 - Self-RAG]], [[Hu 2022 - LoRA]]
