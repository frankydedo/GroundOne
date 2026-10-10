---
type: concept
tags: [jev, ai-model, system-one]
---
# Jev

**Jev** is a highly efficient AI model representing a new class of architectures known as [[System One Models]]. Unlike Large Language Models (LLMs), Jev does not generate text. It functions as an intelligent decision-making engine. It was created by [[TypeSafe AI]], a lab founded by Diogo Almeida, and named after William Stanley Jevons.

## Core Capabilities
Given a "State" (unstructured text data) and "Instructions" (natural language), Jev can only output:
- **Boolean values** (Noul / True/False)
- **Numerical scores** (e.g., rating from 1-10)
- **Categorical choices** (selecting an option from a predefined list)

## Advantages
> **Evidence note (lint 2026-10-05):** the speed, cost and calibration figures below are **vendor claims** (TypeSafe, launch material and videos). The only independent measurement in this wiki is the 30-example MLflow test ([[Jev vs LLMs Cost Comparison]]). Treat them as claims, not results.

- **Fast and cheap (claimed)**: Because it doesn't autoregressively generate output tokens, TypeSafe reports response times of 70–500 ms and a price of $0.042 / MTok input, marketed as "up to 193x faster and 444x cheaper" than traditional LLMs. The comparison baseline behind these ratios is not specified.
- **Calibrated confidence (claimed)**: TypeSafe states that RL with Calibrated Decisions makes the probabilities reflect true confidence, enabling thresholds. No public calibration measurement (e.g. [[Expected Calibration Error]]) is available; open reproductions did not reproduce RLCD ([[SemIf]], [[Rizzo-Flow]]).
- **Zero Schema Hallucinations**: Since outputs are type-safe by design, Jev cannot generate an invalid type (though it can still make incorrect decisions).

## Use Cases & Integrations
- **Real-time processing**: AI agents playing games (e.g., Doom), autonomous driving simulations.
- **Agentic Routing & Guardrails**: Quickly deciding which LLM or MCP tool an agent should call. In [[LangChain]], this is facilitated by `ModelRouterMiddleware` and `AutoModeMiddleware`.
- **Data Extraction**: Extracting structured metadata, scores, and categories from large volumes of unstructured text almost instantaneously.
- **LLM-as-a-Judge / Evaluation**: Used in pipelines like MLflow to evaluate factual correctness of answers at scale. It offers extremely low cost and latency with high accuracy, though it lacks the ability to generate textual rationale.

## Architecture & Training
Jev is closed: everything below except the team is **inferred** by third parties (black-box probing in [[Jevs Architecture Unmasked]], commentary in [[jev_simone_rizzo]]) or stated by the vendor without technical detail.
- Created by a team including Diogo Almeida (co-inventor of RLHF).
- **Backbone**: Inferred to use a sparse **[[Mixture of Experts]]** (MoE) transformer to maintain high capacity with low latency.
- **Shared State**: The input state is processed once and stored in the **[[KV Cache]]**. Multiple question branches can then attend to this state in parallel without recomputing it.
- **Readout Head**: It takes a base decoder-only LLM (like Qwen 3.5), truncates it before the final token probability generation (logits), and attaches a fixed output head that provides direct numerical probabilities.
- **Listwise Processing**: Option choices interact before a decision is made, meaning the model reads them together as a context rather than scoring them in isolation.
- **Parallel Sampling**: Jev generates all outputs in a single query.
- Trained using Supervised Fine-Tuning (SFT) followed by [[Reinforcement Learning with Calibrated Decisions]].

## Related Concepts
- [[When System One Beats an LLM]]
- Open alternatives: [[SemIf]], [[Rizzo-Flow]], [[CLM]], [[Jevlike]]
- [[Groundedness Verification]] (the thesis task; the MLflow test used Jev for a similar factual-correctness judgement)
- [[System One Models]]
- [[Reinforcement Learning with Calibrated Decisions]]
- [[TypeSafe AI]]
- [[LangChain]]
- Sources: [[What Is Jev A Guide to TypeSafe AI]], [[Introducing System One Models and Jev]], [[JEV Video Description]], [[Jevs Architecture Unmasked]], [[Can Jev replace your LLM judge]]
