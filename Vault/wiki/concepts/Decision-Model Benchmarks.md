---
type: concept
tags: [benchmark, evaluation, decision-models, system-one, jev, laya, calibration, synthesis]
---
# Decision-Model Benchmarks

Independent evaluations of [[System One Models|decision models]] (Jev-style systems that return typed answers with probabilities) appeared within weeks of [[Jev]]'s release in September 2026. This page lists them, says what each measures and how much it can be trusted, and what they jointly say about open vs closed systems. Most of them are Hugging Face uploads under the [[Hugging Face decision-models Tag]].

## Overview
| Benchmark | What it measures | Size and protocol | Quality notes |
| --- | --- | --- | --- |
| **Deußer 2026** ([[Deusser 2026 - Evaluating and Benchmarking the System One Model Jev (arXiv 2609.37647)\|paper]]) | Jev zero-shot accuracy, calibration, selective prediction, thresholds, cost; open LLM letter readouts (Qwen3.8-27B, Gemma-4-E4B) on identical requests | 37 datasets, full splits, 346,009 requests; one frozen template per dataset; bootstrap CIs; raw responses released | Strongest protocol (academic, reproducible). Only Jev among System Ones; one template per dataset; Jev contamination not excluded (MMLU anomaly) |
| **DecideBench** ([[Yong 2026 - DecideBench dataset card\|card]]) | Accuracy, cost per decision, latency together; Pareto frontiers | 400 items in 200 contrastive pairs, 8 families; 20 decision models + 3 LLMs; L4 GPU for self-hosted | **All items written by Claude**, labels LM-checked; worked examples for decoders, none for encoders; pair accuracy exposes topic matching |
| **JevBench v1.6.1** ([[Benchmark Heaven 2026 - JevBench v1.6.1 dataset card\|card + leaderboard CSV]]) | Chance-corrected accuracy ("Intelligence"), calibration, speed, cost; capability and composite scores | 94 systems; public + **sealed** tiers | Independent maintainer, documented method; sealed items prevent reruns; costs modelled, latencies adjusted |
| **morrenhale** ([[morrenhale 2026 - Decision benchmark Jev vs Laya vs Julia-1 dataset card\|card + results JSON]]) | Jev vs Laya vs Julia-1: accuracy, macro-F1, Brier, NLL, ECE, latency | 19,776 decisions × 3 engines; 5 public datasets; frozen manifests; paired bootstrap | Well documented and auditable; latency on different hardware; Laya's train-on-test checkpoint excluded |
| **Laya formatting fragility** ([[pranaysuyash 2026 - Laya Formatting Fragility dataset card\|card]]) | Flip rates under option order, key renames, phrasing | 40 base cases × 12 variants | Small; first release had harness errors (since corrected) |
| **Core AI on Apple M4 Max** ([[mlboydaisuke 2026 - Decision models on Core AI (JevBench public231) dataset card\|card]]) | On-device accuracy, ECE, latency of 8 models (6 decision, 2 chat) on JevBench's public items | 231 items, int8, JevBench's own harness and scorer | Contended GPU; truncation for some models; per-item rows published |
| **typed-decisions** (via [[Nandakishore 2026 - Laya as a Typed Probabilistic Assessor (arXiv 2609.33843)\|Nandakishore 2026]] and the Laya card) | Agreement with a teacher on 4 synthetic workflow domains | 2,000 test decisions (400 cases × 5) | Gold = mean of 3 samples from a ~4B teacher; ceiling 0.735; a specialist fine-tuned on its train split exceeds the ceiling |
| **Sciev battery + SciFact** ([[Robles-Fernandez 2026 - Sciev Typed Scientific Decisions Without Generation (manuscript, sciev.org)\|manuscript]]) | Scientific typed decisions; SciFact claim verification | 448–1,218 internal items; SciFact 332 | Constructed labels; selection-informed external results; single author |
| **Jev Decision Index 0.2.1 / 0.3.1** ([[multimodalart 2026 - Jev Decision Index (Hugging Face Space)\|Space + methodology + results JSON]]) | Chance-corrected skill in 5 areas; separate calibration summary; includes **response-level RAGTruth**, ANLI, ContractNLI, HoVer | 120,340 requests, 43 benchmarks (38 in the index), 70 entrants + Jev on 0.2.1; 0.3 adds private same-skill (50 %) and new-domain (30 %) tiers | Community board; strict rules (no truncation, unanswered = wrong); private tiers unauditable; the leaderboard most vendor cards cite |
| **RLCDAlignBench** ([[Guo 2026 - Just Ask Jev (arXiv 2609.29429)\|Guo 2026]]) | Jev as zero-shot detector of 10 alignment failures, incl. hallucination | 44 benchmarks, 5 target models | Academic; re-generated responses with judge or rule labels; AUROC + ECE |
| **JEV-as-a-Judge** ([[Li 2026 - JEV-as-a-Judge (arXiv 2609.26550)\|Li 2026]]) | Jev vs 16 judges on preference, HaluEval factuality, final answers; confidence-gated cascade | 5,172 base judgments + live test | Academic; blinded human adjudication; fees and latency matched |
| Training corpus, not a benchmark: [[Sileo 2026 - tasksource-jev-typed-decisions dataset card\|tasksource-jev-typed-decisions]] | 2.5M typed decisions from 670 sources | – | Source weights depend on Jev and Liquid D1 probabilities |

## What they say about open vs closed systems
1. **Jev is at or near the top of every independent board.** DecideBench 98.0 % (cheapest model above 95 %); morrenhale 0.775 overall, the best of the three engines overall (best on 2 of 5 datasets; Julia-1 leads Banking77 and Emotion, Laya leads AG News); JevBench capability rank 4 and composite rank 2; Core AI public231 hard tier 0.730 (published row); Deußer: above Qwen3.8-27B on 27 of 37 datasets and above Gemma-4-E4B on all 37. Its calibration is also measured, not just claimed: choice ECE 0.028 pooled (Deußer), overall 0.105 (morrenhale).
2. **Large open decoders with option-letter readouts can match or beat it.** On JevBench, Quyet-1.0-Large (Gemma-4-31B, option-letter logits) has capability rank 1 (intelligence 73.4 vs Jev 63.6). Deußer's zero-shot Qwen3.8-27B readout leads Jev on 9 of 37 datasets, none of them outside the bootstrap intervals, and trails it on 27. These are 12–31B models on datacenter GPUs.
3. **Small open encoders lag far behind zero-shot.** [[Laya]]: 0.590 (morrenhale), 59.8 % (DecideBench), intelligence 1.79 (JevBench). On DecideBench, encoders (Laya, GLiNER2.5-Decide, [[CLM]], Julia-1) score 35–60 % and often answer both halves of a contrastive pair the same way. Exception: Julia-1 reaches 0.727 on morrenhale's public datasets but 34.8 % on DecideBench's novel, Claude-written items. One plausible reading, not tested, is that it fits well-known public datasets better than new items.
4. **Vendor numbers do not survive independent measurement unchanged.** Laya's 0.766 belongs to a checkpoint trained on that benchmark's own training split; its ECE comparison set a post-temperature number against a raw one; its "over-confident" warning has the wrong sign for the typed-decisions checkpoint (Nandakishore). Jev figures quoted third-party on vendor cards disagree with each other (ECE 0.144 vs 0.246) and with direct measurement (0.038 on typed-decisions).
5. **Robustness is a separate axis.** The hosted generalist is the most format-stable (Jev 2.9–8.3 % flips vs Laya 15–33 %). Every typed model tested ignores negated yes/no questions (Azizi). Label rendering, not the decision head, causes option-label bias.

## New self-reported numbers from model cards (ingest 2026-10-10, `decision-model` tag)
*All vendor- or author-measured unless stated; harnesses differ.*
| Source | Benchmark | Numbers |
|---|---|---|
| [[Cloudflare 2026 - Clef model card]] | Decision Index 0.2.1, internal run | RAGTruth F1: Clef 79.4, Jev 76.5, Clef-flash 35.6, Laya 48.8; median latency 209 / 524 / 39 / 6 ms |
| [[Perplexity 2026 - pplx-decider-v1.1-27b model card]] | Decision Index 0.2.1 | 61.56 (v1.1) vs 56.4 (v1) vs 57.9 (Jev, quoted) |
| [[LiquidAI 2026 - d1-3B model card]] | Decision Index 0.2.1, official scorer, not a board entry | d1-3B 48.57; d1-omni-600M 15.95 |
| [[KR Labs and vLLM Semantic Router 2026 - Vela 2.0 9B model card]] | RAGTruth (2,700 rows), example-F1 | Vela 9B 0.774, 0.3B 0.706; LettuceDetect v2 qwen-2b 0.817 (re-scored) |
| [[Strands Agents (Amazon) 2026 - strands-decider-2B-qwen3.5-v1 model card]] | JevBench public (231) | 180/231, Brier 0.280, ECE 0.072 (three-seed soup; seeds 179.7 ± 3.8) |
| [[Palmer 2026 - Kev-4B model card]] | own held-out suites; JevBench public | breadth-v1 test 0.690 vs Jev 0.757; JevBench 0.758 (hard 0.541) |
| [[tokimoa 2026 - uratori-ja-4b model card]] | own Japanese grounding set | 4B 0.872, 9B 0.897, Jev 0.903 (test, 802 items) |
| [[mlx-community 2026 - clef-flash-4bit model card]] | Decision Index, 2,000-request sample | 4-bit 54.65 vs bf16 55.63 on identical rows |

**Independent RAGTruth evidence from the board itself** ([[multimodalart 2026 - Jev Decision Index (Hugging Face Space)]]): the 22 entrants under 1B parameters have a median F1 of 0.44 and a best of 0.553 (chance 0.518); 31 of 70 are at or below chance; all 16 entrants of 15B or more exceed 0.6 (median 0.74).

## What none of them measures
- **None measures sentence-level groundedness of RAG answers**, i.e. three-way verdicts for every sentence of an answer against its retrieved document, as GroundOne does. *(Refined 2026-10-10: the Decision Index does measure **response-level** RAGTruth as a binary `noul` for 70 entrants; sentence-level, three-way verdicts remain unmeasured.)*
- Closest proxies:
  - **Decision Index RAGTruth** (response-level hallucinated-class F1 on the 2,700 test responses): Jev 0.765, pplx-decider-v1-27b 0.803; Clef 79.4 in Cloudflare's run; Vela 9B 0.774 example-F1 in its own harness. GroundOne's T1 covers 2,647 of these responses, so a response-level F1 can be computed for direct comparison.
  - **Deußer's LLM-AggreFact run** (binary claim grounding, same test split and metric as GroundOne's T2): Jev 78.6, Qwen3.8-27B 76.9, Gemma-4-E4B 75.6 mean balanced accuracy. GroundOne 3B scores 74.8 and MiniCheck 74.0 ([[GroundOne Results]]), with different prompts.
  - **DecideBench `claim_support`**: 50 items, Jev 96 %, Laya 76 %.
  - **Sciev on SciFact**: binary 0.483 frozen (below the 0.596 majority), 0.709 adapted.
  - **Nandakishore's claim-verification probe**: Laya 0.617, entity swaps and inference at chance.
- None measures multi-decision cost on one long shared context except indirectly: the Core AI run shows 40–220 s per question when a 3k-token state is re-prefilled for every question.

## Implications for the thesis
- The GroundOne T2 comparison should cite Deußer: on LLM-AggreFact, a closed System One and a zero-shot 27B readout are above GroundOne 3B. GroundOne's claim rests on in-domain T1, locality and per-sentence cost, not on beating every System One on T2 ([[When System One Beats an LLM]]).
- Reporting standards the better benchmarks share, and that GroundOne follows: frozen prompts, full splits, chance or balanced metrics, bootstrap intervals, released predictions, and explicit separation of specialist vs zero-shot rows.

## Links
- [[System One Models]], [[Jev]], [[Laya]], [[Hugging Face decision-models Tag]], [[Decision-Model Landscape (Hugging Face, 2026)]], [[Calibration]], [[Selective Prediction]], [[Letter-Token Readout]], [[On-Device Inference]], [[Groundedness Verification]], [[LLM-AggreFact]], [[Statistical Significance and Bootstrap]]
- Sources: [[Deusser 2026 - Evaluating and Benchmarking the System One Model Jev (arXiv 2609.37647)]], [[Yong 2026 - DecideBench dataset card]], [[Benchmark Heaven 2026 - JevBench v1.6.1 dataset card]], [[morrenhale 2026 - Decision benchmark Jev vs Laya vs Julia-1 dataset card]], [[pranaysuyash 2026 - Laya Formatting Fragility dataset card]], [[mlboydaisuke 2026 - Decision models on Core AI (JevBench public231) dataset card]], [[Nandakishore 2026 - Laya as a Typed Probabilistic Assessor (arXiv 2609.33843)]], [[Azizi 2026 - Labels Override Definitions in Jev-Style Typed Decision Models (arXiv 2610.02586)]], [[Robles-Fernandez 2026 - Sciev Typed Scientific Decisions Without Generation (manuscript, sciev.org)]], [[Sileo 2026 - tasksource-jev-typed-decisions dataset card]]
