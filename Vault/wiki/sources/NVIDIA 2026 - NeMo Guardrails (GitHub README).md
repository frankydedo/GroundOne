---
type: source
author: "NVIDIA (NeMo Guardrails maintainers)"
date: 2026
venue: "GitHub README (NVIDIA-NeMo/Guardrails), accessed 2026-10-18; latest release stated as 0.24.1"
url: "https://github.com/NVIDIA-NeMo/Guardrails"
tags: [source, software, readme, guardrails, policy-layer, rails, colang, telemetry]
---
# NVIDIA 2026 – NeMo Guardrails (GitHub README)

**Raw file**: `raw/demo/NVIDIA 2026 - NeMo Guardrails (GitHub README)_ingested.md`

## Overview
The current README of the NeMo Guardrails library, the maintained software behind [[Rebedea 2023 - NeMo Guardrails, Controllable and Safe LLM Applications (arXiv 2310.10501)|Rebedea 2023]]. It is an open-source, Apache-2.0 Python toolkit (Python 3.10–3.13, `pip install nemoguardrails`, async-first) that adds **programmable guardrails between application code and the LLM**. The README lists five rail types, a configuration format (`config.yml` plus Colang `.co` files plus Python actions), a built-in library of rails, a CLI and HTTP server, optional LangChain integration, an evaluation tool, and an **anonymous telemetry** policy.

## Key Insights
1. **Five rail types (README "Types of Guardrails").** *Input rails* reject or alter user input, for example masking sensitive data. *Dialog rails* steer prompting and flows over canonical forms. *Retrieval rails* reject or alter retrieved RAG chunks. *Execution rails* wrap tool inputs and outputs. *Output rails* **reject the output, preventing it from being returned to the user, or alter it**.
2. **Configuration as policy.** A configuration declares the LLM(s) and any number of rails. A config with no rails simply forwards to the LLM. The example `config.yml` activates output flows `self check facts` and `self check hallucination` and input flows `check jailbreak` and `mask sensitive data on input`. Colang 1.0 is the default and Colang 2.0 is also supported.
3. **Built-in library.** The library covers LLM self-checking (input/output moderation, fact-checking, hallucination detection), NVIDIA safety models (content and topic safety), jailbreak and injection detection, and third-party integrations. The README names out-of-the-box integration with ActiveFence, PolicyAI, **AlignScore** and LangChain. It lists "hallucination detection for RAG applications (e.g., Got It AI, Patronus Lynx)" among the complementary approaches the toolkit aims to unify. The built-in rails "may or may not be suitable for a given production use case".
4. **Use cases.** RAG question answering ("enforce fact-checking and output moderation"), domain assistants, guarded LLM endpoints, and LangChain chains.
5. **Deployment.** A Python API (`RailsConfig.from_path`, `LLMRails.generate`), a server exposing `POST /v1/chat/completions` with a `config_id`, Docker, and a CLI (`chat`, `server`, `evaluate`, `actions-server`). The listed providers are mostly hosted or GPU endpoints (OpenAI, NIM, NVIDIA AI endpoints), and Llama 2, Falcon, Vicuna and Mosaic are named as supported models.
6. **Telemetry (README "Telemetry and Privacy").** The library sends **anonymous usage telemetry to NVIDIA by default**: one event at instantiation plus periodic heartbeats. The payload covers library and Python versions, OS, the names of configured engine providers, rail counts and categories, active built-in features and a random per-process UUID. Per the README, prompts, completions, model names and keys are not included. A local audit file is written to `~/.config/nemoguardrails/usage_stats.json`. The opt-out is `NEMO_GUARDRAILS_NO_USAGE_STATS=1`, `DO_NOT_TRACK=1`, or a `do_not_track` file, and it must be set before start-up. Third-party endpoints keep their own terms.
7. **Self-description.** The README claims to be the only guardrails toolkit that also models the dialogue, which allows fine-grained control over *when* a rail runs, for example fact-checking only for certain question types.

## Relevance to GroundOne
- **Reference design for the demo's policy layer.** The output-rail semantics ("reject … or alter") and the declarative config file correspond directly to the demo's configurable policy: which classes block, strict or lenient, τ, the action on failure, and an audit log. The thesis can cite NeMo Guardrails as the established pattern, to show that a policy layer over a verifier is standard practice, and position the demo's contribution in the *verifier* and the *revise step* ([[Guardrails and Policies]], [[Demo Application]]).
- **Where GroundOne would sit.** In NeMo terms, GroundOne is an **output rail for RAG groundedness**, filling the slot of `self check facts`, AlignScore or Lynx. Unlike the self-check rail it returns per-sentence three-way calibrated probabilities ([[Groundedness Verification]], [[AlignScore]], [[Calibration]]). A retrieval rail is also the natural slot for a CRAG-style relevance gate ([[Yan 2024 - Corrective Retrieval Augmented Generation (arXiv 2401.15884)|CRAG]]).
- **Why the demo implements its own layer.** NeMo Guardrails is a Python library and server, while the demo is a native Swift and MLX Swift macOS app. Using it would mean running a Python sidecar. This is an engineering inference from the README's requirements, not a claim made in the README.
- **Locality pillar.** Telemetry to NVIDIA is **on by default**. Even though it is anonymous and documented, a strictly local app that adopted the library would have to set the opt-out before start-up. This concrete example supports the thesis's point that "open source" does not automatically mean "nothing leaves the device" ([[Privacy and Data Sovereignty]], [[On-Device Inference]]).
- **Caveat.** A README is not peer-reviewed. Its claims (uniqueness, protection results in the linked vulnerability scan) are self-reported and are not verified here.

## Links
- Concepts: [[Guardrails and Policies]], [[Demo Application]], [[Groundedness Verification]], [[Hallucination Detection]], [[Privacy and Data Sovereignty]], [[On-Device Inference]], [[AlignScore]]
- Related sources: [[Rebedea 2023 - NeMo Guardrails, Controllable and Safe LLM Applications (arXiv 2310.10501)]], [[Ravi 2024 - Lynx]], [[Zha 2023 - AlignScore]], [[Yan 2024 - Corrective Retrieval Augmented Generation (arXiv 2401.15884)]]
