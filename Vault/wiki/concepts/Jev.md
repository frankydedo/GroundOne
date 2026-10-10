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
> **Evidence note (lint 2026-10-05):** the speed, cost and calibration figures below are **vendor claims** (TypeSafe, launch material and videos). The only independent measurement in this wiki is the 30-example MLflow test ([[Jev vs LLMs Cost Comparison]]). Treat them as claims, not results. *(Superseded 2026-10-10: large independent evaluations now exist; see "Independent evaluations" below. Speed and cost ratios remain vendor claims.)*

- **Fast and cheap (claimed)**: Because it doesn't autoregressively generate output tokens, TypeSafe reports response times of 70–500 ms and a price of $0.042 / MTok input, marketed as "up to 193x faster and 444x cheaper" than traditional LLMs. The comparison baseline behind these ratios is not specified.
- **Calibrated confidence (claimed)**: TypeSafe states that RL with Calibrated Decisions makes the probabilities reflect true confidence, enabling thresholds. No public calibration measurement (e.g. [[Expected Calibration Error]]) is available *(superseded 2026-10-10: Deußer 2026 and morrenhale measure it, see below)*; open reproductions did not reproduce RLCD ([[SemIf]], [[Rizzo-Flow]]).
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

## Independent evaluations (ingest 2026-10-10)
All on the pinned `jev-1.13.0`; see [[Decision-Model Benchmarks]] for protocol quality.
- **[[Deusser 2026 - Evaluating and Benchmarking the System One Model Jev (arXiv 2609.37647)|Deußer 2026]]** (University of Bonn): 37 datasets, 346,009 requests, US$9.15. Zero-shot 95–99 % on IMDB, SST-2, HellaSwag, ARC. Above Qwen3.8-27B (letter readout on identical requests) on 27 of 37 datasets and above Gemma-4-E4B on all 37. **[[LLM-AggreFact]] 78.6** mean balanced accuracy (Qwen3.8-27B 76.9). Choice probabilities well calibrated (pooled ECE 0.028); single `noul` probabilities slightly under-confident; multi-label `noul` over-predicts yes. Binary probabilities rank well but sit badly against a fixed 0.5 threshold: thresholds tuned on training data raise UNFAIR-ToS micro-F1 from 0.50 to 0.75. Possible contamination: Jev is better on MMLU's calculation-heavy subjects than on the rest, unlike the open models.
- **[[morrenhale 2026 - Decision benchmark Jev vs Laya vs Julia-1 dataset card|morrenhale]]**: 19,776 decisions on five public datasets. Accuracy **0.775**, ECE **0.105** (Laya 0.590 / 0.222; Julia-1 0.727 / 0.172). typed-decisions 0.732 with ECE 0.038. Hosted p50 322.9 ms including network.
- **[[Yong 2026 - DecideBench dataset card|DecideBench]]**: **98.0 %** on 400 Claude-written contrastive items (pair accuracy 96.0 %, zero-shot 98.2 %), the cheapest model above 95 % ($32.26 per million tasks); p50 639 ms through a gateway. General LLMs score 99.2–99.8 % at 6–14× the cost.
- **[[Benchmark Heaven 2026 - JevBench v1.6.1 dataset card|JevBench v1.6.1]]**: capability rank 4, composite rank 2 of 94 systems; intelligence 63.6, calibration 90.6. Quyet-1.0-Large (open, Gemma-4-31B letter readout) ranks first on capability.
- **[[pranaysuyash 2026 - Laya Formatting Fragility dataset card|Formatting fragility]]**: the most format-stable system tested (2.9–8.3 % flips; accuracy 90.2 % vs Laya 72.7 %).
- **[[Azizi 2026 - Labels Override Definitions in Jev-Style Typed Decision Models (arXiv 2610.02586)|Azizi 2026]]** did not run Jev; it cites Sun et al. (2026), who found that renaming Jev's options changes its answers.
- **Reading.** Jev's accuracy and calibration hold up independently on short, well-scoped decisions. Weak spots are long or multi-step inputs, low-resource languages, noisy labels and rubric judgments of generated text. Jev figures quoted on third-party vendor cards (e.g. ECE 0.144 or 0.246 on the [[Laya]] card) disagree with direct measurement.

## More independent evaluations and open alternatives (ingest 2026-10-10, `decision-model` tag)
- **As a judge** (CMU): 8th of 15 LLM judges, 1.7 points behind GPT-6 at 277× lower fee and 0.15 s median latency; HaluEval QA 87.3 % vs 88.4 %; large gaps where verdicts must be derived (logic −27.6) ([[Li 2026 - JEV-as-a-Judge (arXiv 2609.26550)]]).
- **As an alignment-failure detector**: median AUROC 0.886 zero-shot over 31 benchmarks; pooled ECE 0.047 but per-benchmark ECE 0.168 ([[Guo 2026 - Just Ask Jev (arXiv 2609.29429)]]).
- **On the Decision Index 0.2.1** (Jev 1.13.0): response-level RAGTruth F1 0.765, ANLI macro-F1 0.748, ContractNLI 0.717, HoVer 0.729 ([[multimodalart 2026 - Jev Decision Index (Hugging Face Space)]]).
- **Open-weight competitors from established organisations** now match or beat it on parts of that index (vendor-reported): Perplexity's pplx-decider-v1.1 (61.56 vs 57.9 overall), Cloudflare's Clef (RAGTruth 79.4 vs 76.5 in Cloudflare's run). Clef also gives an open, inspectable version of the decoder-plus-head design attributed to Jev ([[Cloudflare 2026 - Clef model card]], [[Perplexity 2026 - pplx-decider-v1.1-27b model card]], [[Decision-Model Landscape (Hugging Face, 2026)]]).
- **Distilled clones**: autotrust's "JEV" models are trained on Jev 1.13 output distributions and disclaim affiliation with TypeSafe; their headline metrics measure agreement with Jev, not accuracy.

## Related Concepts
- [[When System One Beats an LLM]]
- Open alternatives: [[SemIf]], [[Rizzo-Flow]], [[CLM]], [[Jevlike]], [[Laya]]
- [[Decision-Model Benchmarks]], [[Hugging Face decision-models Tag]]
- [[Groundedness Verification]] (the thesis task; the MLflow test used Jev for a similar factual-correctness judgement)
- [[System One Models]]
- [[Reinforcement Learning with Calibrated Decisions]]
- [[TypeSafe AI]]
- [[LangChain]]
- Sources: [[What Is Jev A Guide to TypeSafe AI]], [[Introducing System One Models and Jev]], [[JEV Video Description]], [[Jevs Architecture Unmasked]], [[Can Jev replace your LLM judge]]
