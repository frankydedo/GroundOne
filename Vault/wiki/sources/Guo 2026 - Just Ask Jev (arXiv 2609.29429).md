---
type: source
author: "Ruoqi Guo, Yi Liu, Gelei Deng, Yuekang Li, Lida Zhao, Yutao Wu, Simin Chen, Ying Zhang, Leo Yu Zhang (Griffith, NTU, UNSW, Deakin, GMU, Wake Forest)"
date: 2026
venue: "arXiv 2609.29429 v1 (24 Sep 2026); under review at ICLR 2027"
url: "https://arxiv.org/abs/2609.29429"
tags: [source, paper, system-one, jev, rlcd, alignment, hallucination-detection, calibration, auroc, base-rate]
---
# Guo 2026 – Just Ask Jev: RLCD as a Zero-Shot Detector of AI Alignment Failures

**Raw file**: `raw/Guo 2026 - Just Ask Jev RLCD as a Zero-Shot Detector of AI Alignment Failures (arXiv 2609.29429)_ingested.pdf`

## Overview
RLCDAlignBench evaluates [[Jev]] as a zero-shot detector of ten alignment failures (sycophancy, jailbreaks, deception, prompt injection, **hallucination**, privacy violation, social bias, reward hacking, concealing uncertainty, power seeking) over 44 benchmarks and five target models, labelled by each benchmark's scorer and, on two, by humans. The key design separates *what Jev is asked* (question wording, answer type) from *what Jev sees* (fields of the input state). Code and cached answers are released. Three models on the decision-model tag cite it (devops-thiago "classone" checkpoints).

## Key Insights
1. **Generic question, good ranking.** One generic `noul` question read as P(yes) reaches a median AUROC of **0.886** over the 31 benchmarks with a `noul` form, above supervised TF-IDF and length baselines on 25. Targeted wording adds only +0.006 [−0.004, +0.015] AUROC out of sample; context that *encodes the label* (e.g. PrivacyLens's secret list, 0.79 → 0.95) matters much more.
2. **Hallucination (target model Llama-3.2-3B, six benchmarks).** Per-type median generic AUROC 0.823; per benchmark: RAGTruth 0.788, LLM-AggreFact (A) 0.755, LLM-AggreFact (B) 0.886, SummEdits 0.859, multi-turn LLM-AggreFact 0.617, multi-turn RAGTruth 0.976. **Caveat:** these are new responses from Llama-3.2-3B, not the original datasets' responses; the RAGTruth set (300 items) is labelled by a GPT-4o judge (unvalidated), the LLM-AggreFact sets (150 each) by a rule against gold.
3. **Calibrated when pooled, not within a benchmark.** Pooled over benchmarks, ECE is 0.047. The median **per-benchmark ECE is 0.168** against 0.074 under perfect calibration, and 24 of 31 benchmarks exceed the null's 95th percentile. Cause: a **base-rate mismatch** (Jev's mean probability misses each benchmark's positive rate by a median of 0.125) while ranking stays good (median AUROC 0.905 within files). A label-free prior-shift correction does not fix it.
4. **A few labels fix the threshold.** Median F1 rises from 0.706 at t = 0.5 to 0.822 with a cross-validated threshold and 0.793 with 10 labelled items; the median F1-optimal threshold is 0.35.
5. **Cost.** One pass over the 19 judge-scored benchmarks costs $0.30 vs $18.96 for their LLM judges at list prices (63× less). Against human labels on StrongREJECT, Cohen's κ 0.809 vs 0.811 for the reference scorer.

## Relevance to GroundOne
- **"Calibrated" is workload-relative.** A model calibrated on its training mix can be badly calibrated on a new base rate: this is the mechanism behind GroundOne's failure to transfer calibration from RAGTruth to VitaminC, and the reason GroundOne fits τ on dev ([[Calibration]], [[Selective Prediction]]). Cite with [[Li 2026 - JEV-as-a-Judge (arXiv 2609.26550)|Li 2026]].
- **Report AUROC alongside thresholded metrics.** Jev's ranking survives where its thresholds do not, the same separation GroundOne draws between AUROC/AURC and ECE ([[Expected Calibration Error]]).
- **Hallucination detection with a general System One is decent but not specialist-level** on RAG-style grounding (RAGTruth 0.788, LLM-AggreFact 0.755–0.886 AUROC on small, re-generated sets). Not comparable with GroundOne's T1/T2 numbers (different responses and labels).

## Links
- Concepts: [[Hallucination Detection]], [[Calibration]], [[Expected Calibration Error]], [[Selective Prediction]], [[Jev]], [[Reinforcement Learning with Calibrated Decisions]], [[Decision-Model Benchmarks]]
- Related sources: [[Li 2026 - JEV-as-a-Judge (arXiv 2609.26550)]], [[Niu 2024 - RAGTruth]], [[Tang 2024 - LLM-AggreFact Leaderboard]]
