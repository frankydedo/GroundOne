---
type: source
author: "Tobias Deußer, Lorenz Sparrenberg, Rafet Sifa (University of Bonn, Lamarr Institute, Fraunhofer IAIS)"
date: 2026-09-29
venue: "arXiv 2609.37647 [cs.CL], preprint"
url: "https://arxiv.org/abs/2609.37647"
tags: [source, paper, jev, benchmark, calibration, selective-prediction, thresholds, llm-aggrefact, decision-models]
---
# Deußer 2026 – Evaluating and Benchmarking the System One Model Jev

**Raw file**: `raw/Deusser 2026 - Evaluating and Benchmarking the System One Model Jev (arXiv 2609.37647)_ingested.pdf`

## Overview
An independent academic evaluation of [[Jev]] (pinned `jev-1.13.0`); the authors know of no earlier systematic evaluation on public benchmarks. Jev is run **zero-shot on 37 datasets** (classification, routing, NLI and grounding, reading comprehension, commonsense, moderation and legal, rubric scoring). Each dataset has one frozen template, tested on 20 training or validation examples before the run. Full evaluation splits: **346,009 requests for US$9.15**. Two open-weight reference models are scored on **identical requests** through their exact next-token probabilities over single-token option codes: **Qwen3.8-27B** and **Gemma-4-E4B**. This is a letter-token readout ([[Letter-Token Readout]]). Code and all raw responses are released (GitHub, Zenodo).

## Key Insights
1. **Accuracy.** Jev reaches 95–99 % on IMDB, SST-2, HellaSwag and ARC, and 86.7 % on Belebele across 122 languages. It **beats Qwen3.8-27B on 27 of 37 datasets** (11 of them outside the bootstrap intervals, none of Qwen's 9 leads) and Gemma-4-E4B on all 37. Weak spots: Emotion (58.5 %), SST-5 (57.9 %), AfriXNLI (64.0 %), AGB-DE legal voidness (F1 0.204), long or multi-step BIG-bench tasks.
2. **Grounding (the result closest to GroundOne).** On **[[LLM-AggreFact]]** (test, 29,320 claims, `noul`, threshold 0.5), the mean of per-source balanced accuracies is **78.6 %** for Jev [0.776, 0.796], ranging from 59.8 % (ExpertQA) to 90.6 % (Reveal). Qwen3.8-27B: 76.9 %; Gemma-4-E4B: 75.6 %. ECE: 0.128 / 0.202 / 0.156. ANLI 73.9 % (R1 81.4 %, R3 67.7 %); PAWS 85.0 %.
3. **Calibration by primitive.**
   - **Choice:** well calibrated (pooled ECE 0.028 over 22 datasets and 279,925 answers; median per dataset 0.028). Where miscalibrated, it is almost always over-confident (20 of 22 datasets). ECE correlates with low accuracy (Spearman ρ = −0.83). Qwen pooled 0.063; Gemma 0.208, strongly over-confident.
   - **Single `noul`:** slightly **under-confident**. Mean P(yes) is 0.465 against an observed yes-rate of 0.518 (ECE 0.052), so positives often fall below 0.5.
   - **Multi-label `noul` fan-out:** over-predicts yes (mean P(yes) 0.209 vs 0.041 observed; ECE 0.168), because each `noul` is answered in isolation.
4. **Good ranking, badly placed threshold.** Binary probabilities rank well (e.g. prompt injection AUROC 0.982, but recall only 50 % at 0.5). **Thresholds tuned on 1,000 training examples** raise UNFAIR-ToS micro-F1 from 0.499 to 0.748, GoEmotions macro-F1 from 0.243 to 0.353 (median tuned threshold 0.86), and ToxicChat jailbreak F1 from 0.717 to 0.833. AGB-DE does not improve: there the problem is separation (AUROC 0.784), not placement. Tuning helps the open models in the same way, though not always (Qwen jailbreak F1 0.743 → 0.726).
5. **Selective prediction works.** At 50 % coverage accuracy rises from 79.7 % to 96.3 % on Banking77 and from 73.9 % to 86.9 % on ANLI. Qwen's confidence is nearly as useful; Gemma's much less.
6. **Possible contamination.** Jev is *more* accurate on MMLU's calculation-heavy subjects than on the rest (94.3 % vs 91.3 %), while both open models, and all three models on C-Eval, find them harder. Rotating options leaves accuracy unchanged; withholding the question drops it to 31.5 %. This rules out shallow memorisation but not memorised question–answer pairs. The authors treat Jev's results on long-established English benchmarks with caution.
7. **Cost and protocol.** 630 input tokens per request on average; mean client-side latency 0.36 s at 32 concurrent connections. Multi-question requests cost little extra: 765 tokens for 28 `noul` questions vs 559 for one. All questions in a request share the state but are answered independently.
8. **Limitations stated.** One untuned template per dataset; the open models answer in a single forward pass without thinking; a fixed 0.5 threshold except in the tuning table; one run per request, no run-to-run variance; latency includes the network.

## Relevance to GroundOne
- **T2 comparison with a closed System One.** Same test split (29,320), same metric (mean per-source balanced accuracy at threshold 0.5), different prompt. Jev **78.6** > Qwen3.8-27B zero-shot letter readout **76.9** > Gemma-4-E4B **75.6** > GroundOne 3B **74.8** > [[MiniCheck]] **74.0** > GroundOne 0.5B **70.1** ([[GroundOne Results]]). The thesis can say that GroundOne 3B is on par with MiniCheck, but it is **not** the strongest System One on LLM-AggreFact: a closed hosted model and a zero-shot 27B readout are higher. The caveats: Jev's training data are unknown, the prompts differ, and the 27B model needs a GPU cluster, not a 16 GB laptop. GroundOne's specialist advantage is established in domain (T1), not on T2.
- **Dev-fitted thresholds.** Good ranking with a misplaced 0.5 threshold is exactly the case D27 addresses. GroundOne fits τ on calibrated P(supported) on dev (τ ≈ 0.90–0.94). Deußer shows the same need on a commercial model and on open readouts ([[Calibration]], [[Selective Prediction]]).
- **Under-confident binary probabilities are not unique to small models.** Jev's single `noul` probabilities sit below the diagonal. Calibration has to be measured per deployment, never assumed from the vendor.
- **Protocol model.** Frozen templates tested on a few non-test items, full splits, bootstrap intervals and released raw responses are the standard GroundOne's evaluation follows.

## Links
- Concepts: [[Jev]], [[Decision-Model Benchmarks]], [[LLM-AggreFact]], [[Calibration]], [[Selective Prediction]], [[Letter-Token Readout]], [[When System One Beats an LLM]]
- Related sources: [[Tang 2024 - LLM-AggreFact Leaderboard]], [[Azizi 2026 - Labels Override Definitions in Jev-Style Typed Decision Models (arXiv 2610.02586)]], [[Can Jev replace your LLM judge]]
