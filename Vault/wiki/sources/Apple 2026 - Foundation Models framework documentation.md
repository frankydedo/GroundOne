---
type: source
author: "Apple Inc."
date: 2026
venue: "Apple Developer Documentation, Foundation Models framework landing page (documentation JSON; retrieved 2026-10-18)"
url: "https://developer.apple.com/documentation/foundationmodels"
tags: [source, apple, on-device, llm-api, guided-generation, tool-calling, private-cloud-compute, demo-runtime]
---
# Apple 2026 – Foundation Models framework documentation

**Raw file**: `raw/demo/Apple 2026 - Foundation Models framework documentation_ingested.md`

## Overview
Landing page of Apple's Swift framework for language models: "Perform tasks with models that specialize in language understanding, structured output, and tool calling." It "provides access to any large language model, like the on-device and Private Cloud Compute models designed for Apple Intelligence". **Thin extraction**: only the overview paragraphs and the list of topic titles; no API signatures, model sizes, context lengths or device list (the device-list link was lost in extraction).

## Key Insights
- **Models**: the on-device Apple Intelligence model, Private Cloud Compute (PCC) for "more reasoning capabilities and context size", and "any server model provider". Requires a device that supports Apple Intelligence.
- **On-device use cases named**: summarisation, entity extraction, text and image understanding, refinement, dialogue for games, creative content.
- **Guided generation**: the `@Generable` macro defines Swift data structures and the framework "provides strong guarantees that the model generates instances of your type".
- **Tools**: the `Tool` protocol lets the model call app code, e.g. "searches a local or online database".
- **Dynamic profiles** select the model configuration per task and support abstractions "such as agents or skills".
- **Topic titles** (contents not extracted): Sessions and prompts, Session transcripts, Prompt attachments, Dynamic profiles, Structured output, Tools, System language model, Private Cloud Compute, **Custom language model provider**, Custom session properties, Safety, Performance and evaluation.

## Relevance to GroundOne
- **Cannot host GroundOne as specified, on the evidence here.** The documented API is generation-level (sessions, prompts, structured output); nothing on this page exposes per-token logits, hidden states or a forward pass with a readout at chosen positions, which design (b) needs (A/B/C logits at every " Verdict:" marker, zero generated tokens). Loading a custom Qwen2.5 base with a LoRA adapter is also not documented here. The "Custom language model provider" topic might allow plugging in a third-party model, but its contents are not in the raw; this must be checked before writing anything about it.
- **A plausible generator for the local RAG loop** ([[Demo Application]]): an on-device model that already ships with the OS costs no extra download and could write the answer that GroundOne verifies and the revise step rewrites. `@Generable` would give a typed revision output, and `Tool` could wrap the SQLite retriever. Caveats: Apple-Intelligence-capable hardware only, an optional PCC path that leaves the device (must be disabled to preserve the locality pillar), and an opaque model that is not the one evaluated in the thesis.
- **As a baseline, not a substitute**: guided generation of a three-way label is a single-token generative judge (cf. control B2), which the thesis already shows to be less accurate than the restricted readout with the same weights; with a different, general model it would be a B0-style judge.
- Background: the model behind this framework is a ~3B on-device model specialised by LoRA adapters ([[Gunter 2024 - Apple Intelligence Foundation Language Models]]), the same "small base + task adapter" pattern as GroundOne.

## Links
- Concepts: [[Demo Runtime Choice]], [[Demo Application]], [[On-Device Inference]], [[Apple Silicon and MLX]], [[Retrieval-Augmented Generation]], [[Local RAG Retrieval]]
- Related: [[Gunter 2024 - Apple Intelligence Foundation Language Models]], [[Apple Security 2024 - Private Cloud Compute, a new frontier for AI privacy in the cloud]], [[Apple 2026 - Core ML documentation]]
