---
type: source
author: "Convai Innovations (code on GitHub under NandhaKishorM)"
date: 2026
venue: "Hugging Face model card, convaiinnovations/laya, revision 7b928d8 (retrieved 2026-10-10)"
url: "https://huggingface.co/convaiinnovations/laya"
tags: [source, model-card, system-one, decision-models, encoder, calibration, vendor-claims, laya]
---
# Convai Innovations 2026 – Laya model card

**Raw file**: `raw/Convai Innovations 2026 - Laya model card_ingested.md`

## Overview
The vendor card of **[[Laya]]**, an open-weight (Apache-2.0) "non-autoregressive System 1 decision model". It takes a state plus typed questions (`choice`, `score`, `noul`) and returns typed answers with probabilities, using a Jev-style interface ([[Jev Input and Output Format]]). The repository holds three checkpoints: `laya` (English, ModernBERT-large, 421M, context 512), `laya-multilingual` (mmBERT-base, 322M, context 1,024, up to 8,192) and `laya-typed-decisions` (ModernBERT-large, 421M, fine-tuned on the typed-decisions benchmark). A `Router` picks the checkpoint by script and language. Package version described: laya 0.3.20; the checkpoints are unchanged from earlier versions.

Every number on the card is **measured by the vendor** (Tesla T4) unless marked otherwise. The Jev numbers are **third-party, "never measured here"** (the card says so itself).

## Key Insights
1. **Architecture.** A fully fine-tuned ModernBERT-large backbone (395M) plus a decision head trained from scratch: 2 transformer layers, an option-marker scorer and an act/escalate head. **Each option is scored at its own `[MASK]` token, then softmaxed over that question's options**, so the answer space is defined at request time. Token budget: English 512 per question, of which `head_max_len = 192` for the options, which leaves about 320 tokens for the state. "Every question in a call is answered in one single forward pass." The latency table (39.5 ms for 1 question, 158.6 ms for 10, 771 ms for 50) shows that cost grows with the number of questions. [[Azizi 2026 - Labels Override Definitions in Jev-Style Typed Decision Models (arXiv 2610.02586)|Azizi 2026]] reports that Laya builds **one input sequence per question**. So "one pass" means one batched call, not one shared context.
2. **Training: RLCD.** The policy reports a distribution. Exploration adds zero-mean Gaussian noise to the logits. The reward is a strictly proper scoring rule (log plus spherical, plus the ranked probability score for ordinal questions). Updates use REINFORCE with a group-mean baseline (GRPO-style). This is the card's version of [[Reinforcement Learning with Calibrated Decisions]]. Calibration temperatures are then fitted per type.
3. **Vendor comparison with Jev** (Laya measured, Jev third-party, "sample sizes and prompts differ"): typed-decisions 0.766 vs 0.727; AG News 0.950 vs 0.910; DAIR Emotion 0.595 vs 0.480; Banking77 0.425 vs 0.870; ECE 0.081 vs 0.246, where Laya's figure is **after temperature fitting**; p50 latency 32.8 ms (T4) vs 236–276 ms for Jev (hosted, end to end). The latency ratio compares a local GPU with a hosted API that includes the network, so it is not like-for-like.
4. **Internal inconsistencies.** The comparison table gives Jev ECE **0.246**. The typed-decisions table on the same card gives Jev ECE **0.144**, and adds that before temperature scaling the base checkpoint's raw ECE is higher (0.213 vs 0.144). Laya's 0.081 is therefore a post-temperature number set against a raw one.
5. **"Honest limits" stated by the vendor.**
   - The base checkpoints are **near chance on typed-decisions zero-shot**: 0.362 (English) and 0.352 (multilingual), against 0.318 random and 0.461 majority class. **The 0.766 belongs to the checkpoint fine-tuned on that benchmark's own training split.** "Laya is a fast base to specialise, not a zero-shot decision engine."
   - Many options: 77 options leave about 3–4 tokens per label (Banking77 0.425).
   - Ordinal `score` questions are the weakest primitive (SST-5 0.372).
   - **`noul` can follow its option labels instead of the state**, because it renders its two options as `false:` / `true:` (issue #156). Azizi 2026 traces this rendering problem in detail.
   - `action.act_probability` carries no usable signal (AUROC 0.30 against correctness on 396 decisions); `confidence` reaches 0.77.
   - **"Ships over-confident"**: refitting one temperature per (question type, option count) moves mean ECE from 0.466 to 0.081 (`laya`) and from 0.314 to 0.106 (`laya-multilingual`). For the typed-decisions checkpoint, [[Nandakishore 2026 - Laya as a Typed Probabilistic Assessor (arXiv 2609.33843)|Nandakishore 2026]] measures the **opposite direction**: it is uniformly under-confident.
6. **Long documents.** With `max_len=8192` on the multilingual checkpoint, 16 to 18 of 20 requests are answered correctly up to about 4,000 tokens of text; beyond that, 8 to 17 of 20. A 4,000-token input takes about 1.7 s on an Apple GPU.
7. **Serving.** `laya-serve` exposes the Jev-compatible `POST /v1/systemone` route. It binds `0.0.0.0` **with no authentication** unless `LAYA_API_KEY` is set.
8. **Script failure.** The English checkpoint scores 0.000 on Khmer at 0.952 mean confidence: confident and wrong, so confidence gating cannot catch it.

## Relevance to GroundOne
- **Different family, same contract.** Laya is an encoder with one `[MASK]` per option. GroundOne is a decoder that reads A/B/C letter logits at a marker after each sentence ([[Letter-Token Readout]]). See [[Laya]] for the comparison and [[System One Models]] for the taxonomy.
- **Context budget.** About 320 state tokens on the English checkpoint is too short for most retrieved documents. The multilingual checkpoint reaches 8,192 tokens, but the vendor's own table shows accuracy becoming erratic past about 4,000 tokens.
- **No shared context across questions.** Questions are batched as separate sequences, so the state is re-encoded for every question. GroundOne encodes the document once per answer and reads all K verdicts in that pass.
- **Vendor-claims hygiene.** The card mixes post-temperature with raw ECE, local GPU with hosted latency, and a train-split-specialised checkpoint with zero-shot competitors. These are the comparisons the thesis must avoid, and which its fairness caveats already exclude (no latency claim across runtimes; specialist vs zero-shot stated).

## Links
- Concepts: [[Laya]], [[System One Models]], [[Decision-Model Benchmarks]], [[Hugging Face decision-models Tag]], [[Calibration]], [[Reinforcement Learning with Calibrated Decisions]], [[Jev]]
- Independent evaluations: [[Nandakishore 2026 - Laya as a Typed Probabilistic Assessor (arXiv 2609.33843)]], [[Azizi 2026 - Labels Override Definitions in Jev-Style Typed Decision Models (arXiv 2610.02586)]], [[morrenhale 2026 - Decision benchmark Jev vs Laya vs Julia-1 dataset card]], [[Yong 2026 - DecideBench dataset card]], [[Benchmark Heaven 2026 - JevBench v1.6.1 dataset card]], [[pranaysuyash 2026 - Laya Formatting Fragility dataset card]], [[mlboydaisuke 2026 - Decision models on Core AI (JevBench public231) dataset card]]
