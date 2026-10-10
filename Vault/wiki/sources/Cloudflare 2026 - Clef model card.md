---
type: source
author: "Cloudflare (Workers AI team; blog by Michelle Chen, Alex Reneau, Kevin Flansburg / Kevin Jain)"
date: 2026
venue: "Hugging Face model card Cloudflare/clef, revision 0b33120 (retrieved 2026-10-10); Cloudflare blog posts of 2026-10-01 and 2026-10-09; release code joint_schema_model.py"
url: "https://huggingface.co/Cloudflare/clef"
tags: [source, model-card, system-one, decision-models, established-org, joint-head, calibration, ragtruth, vendor-claims, clef]
---
# Cloudflare 2026 – Clef model card

**Raw file**: `raw/Cloudflare 2026 - Clef model card_ingested.md`
**Supplementary raw files**: `raw/Cloudflare 2026 - Clef blog posts (2026-10-01 and 2026-10-09)_ingested.md` (article text of both announcements), `raw/Cloudflare 2026 - Clef joint_schema_model_ingested.py` (the released head and encoding code, revision 0b33120, with `joint_head_config.json` in its header)

## Overview
Clef is Cloudflare's family of open-weight (Apache-2.0) decision models, released on 2026-10-01 and hosted on Workers AI. It is the first entrant from a large, established infrastructure company under the [[Hugging Face decision-models Tag|decision-model tag]]. Clef takes a state (text, JSON, images or video) plus a schema of typed questions (`noul`, `choice`, `score`) and returns a probability for every allowed option of every question "in a single forward pass". The API is Jev/SystemOne-compatible (`/v1/systemone`, [[Jev Input and Output Format]]).
- **Clef**: post-trained from Qwen3.8-27B (with its vision encoder).
- **Clef-flash**: post-trained from Qwen3.5-9B.
- **Clef-omni** (2026-10-09): post-trained from Qwen3-Omni-30B-A3B-Instruct (mixture of experts), adds audio and video; speech-output weights are shipped but unused.

All benchmark numbers on the card are **Cloudflare's own internal runs** of the community [[multimodalart 2026 - Jev Decision Index (Hugging Face Space)|Decision Index]] 0.2.1 and of TypeSafe's workflow evals; none is an independent measurement.

## Key Insights
1. **Architecture (verified in the released code).** The prompt packs `STATE:` then a `SCHEMA FIELDS:` block listing every question and its options, then an assistant prefix, into **one causal sequence**. The backbone runs once (prefill only). A separate **joint schema head** (`hidden_size` 5120 → width 1024; 2 evidence-routing layers, 4 transformer-decoder layers, 16 heads) then:
   - mean-pools each question span and each option span from the backbone's last hidden states, and adds a lexical embedding of each option from the LM's output-embedding matrix;
   - lets every option query **cross-attend to the whole sequence** ("evidence routing");
   - lets the question ("field") vectors attend to each other and back to the sequence (joint cross-field attention);
   - scores options with a cosine plus an MLP residual, added to a "lexical prior" (cosine between option and question embeddings).
   Output: one logit per option; a softmax per question gives probabilities.
   This is the first **open-weight implementation of the family-(a) design** that was only *inferred* for [[Jev]] (decoder backbone + dedicated head, all questions over one shared prefill; [[System One Models]]).
2. **Training (blog, 2026-10-01).** The backbone is **frozen**; the routing head is trained jointly with **rank-256 LoRA adapters**. Loss: label-smoothed cross-entropy over valid options plus a **Brier loss** "to refine probability calibration". Data: internal synthetic datasets that permute field orders, prompts and schema structures. A secondary RL objective that Cloudflare also calls "Reinforcement Learning for Calibrated Decisions (RLCD)" gives partial credit to adjacent ordinal choices, rewards fully correct records and adds a reference penalty. The second post says the model was built "over the course of less than a week" (trained over a weekend).
3. **Context and modality.** 64k context claimed for hosted Clef (vs 32k for Jev); `encode_record` defaults to `max_length` 16,384. The 2026-10-09 post cuts the hosted Clef-flash window to 24k for pricing and says the weights were trained for 256k.
4. **Decision Index 0.2.1, Cloudflare's internal run (selected rows).**
   | Benchmark | Clef | Clef-flash | Jev | Laya |
   |---|---|---|---|---|
   | **RAGTruth (hallucination F1)** | **79.4** | 35.6 | 76.5 | 48.8 |
   | HoVer (accuracy) | 65.2 | 61.2 | 72.9 | 55.8 |
   | ANLI (macro-F1) | 69.8 | 59.1 | 74.8 | 48.7 |
   | ContractNLI (macro-F1) | 81.4 | 84.3 | 71.7 | 29.0 |
   | NLI4CT (macro-F1) | 82.9 | 78.6 | 84.1 | 47.7 |
   | Median latency (ms) | 209.3 | 38.8 | 524.1 | 5.8 |
   The same table includes a "DiffusionGemma Jev" (RAGTruth 70.4) and "Kev 9B" (46.2). Clef-flash's RAGTruth score (35.6) is below the always-"hallucinated" baseline of the Index (F1 0.518), so the smaller model fails on exactly the grounding task while scoring well on tool and intent tasks.
5. **Workflow evals** (TypeSafe Evals, consensus labels): Clef beats Jev on invoice processing (64.7 vs 61.8 exact actions) and security incidents (62.9 vs 61.7); Jev leads agent-trace observability (71.6 vs 68.5).
6. **Serving.** Tested on one H200 with torch 2.11 / transformers 5.10.2; SGLang support (PR #42721 per the second post). The second post reports hosted Clef latencies of 152 / 305 / 1,635 ms median at about 800 / 3,400 / 16,000 input tokens after serving optimisations.

## Relevance to GroundOne
- **A decision-model maker reports RAGTruth.** Clef 79.4 and Jev 76.5 F1 on the hallucinated class (response level, 2,700 test responses, zero-shot) are the closest published comparison points for GroundOne's T1. They are **not** GroundOne's metric: GroundOne reports sentence-level three-way balanced accuracy and AUROC, and is trained on RAGTruth train. A response-level F1 computed from GroundOne's sentence verdicts would make the comparison possible ([[RAGTruth]], [[Decision-Model Benchmarks]]).
- **Joint head vs letter readout.** Clef answers all questions from one shared prefill with a trained head; GroundOne answers K sentence verdicts from one pass with the LM head restricted to A/B/C at markers ([[Letter-Token Readout]]). Both are "many decisions, one prefill"; Clef's head can compare options and questions jointly, GroundOne's verdicts are independent by construction.
- **Calibration by loss.** Clef adds a Brier term in training; GroundOne uses post-hoc temperature + bias on dev ([[Calibration]]). No calibration measurement is reported on the card.
- **Size matters for grounding.** The 9B Clef-flash collapses on RAGTruth while the 27B does not. This supports the thesis reading that the gain comes from scale or specialisation, not from the System One interface itself ([[When System One Beats an LLM]]).
- **Locality.** The 9B variant runs on a 16 GB Mac in MLX 4-bit ([[mlx-community 2026 - clef-flash-4bit model card]]).

## Links
- Concepts: [[System One Models]], [[Decision-Model Landscape (Hugging Face, 2026)]], [[Decision-Model Benchmarks]], [[Jev]], [[RAGTruth]], [[Hallucination Detection]], [[Calibration]], [[On-Device Inference]]
- Related sources: [[multimodalart 2026 - Jev Decision Index (Hugging Face Space)]], [[mlx-community 2026 - clef-flash-4bit model card]], [[ggml-org 2026 - llama.cpp PR 29818 systemone API]]
