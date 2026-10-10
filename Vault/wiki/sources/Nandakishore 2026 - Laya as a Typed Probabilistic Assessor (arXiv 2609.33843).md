---
type: source
author: "Gowthamkumar Nandakishore"
date: 2026-09-27
venue: "arXiv 2609.33843 [cs.AI], preprint"
url: "https://arxiv.org/abs/2609.33843"
tags: [source, paper, laya, calibration, selective-prediction, reproduction, preregistration, decision-models]
---
# Nandakishore 2026 – Laya as a Typed Probabilistic Assessor

**Raw file**: `raw/Nandakishore 2026 - Laya as a Typed Probabilistic Assessor (arXiv 2609.33843)_ingested.pdf`

## Overview
An independent reproduction of the **laya-typed-decisions** checkpoint ([[Laya]]), followed by a preregistered study of its calibration and of confidence-gated escalation. The benchmark is `LocalLLaMA/typed-decisions`: four synthetic workflow domains, 300 train and 100 test cases each, five typed questions per case, so 2,000 test decisions. Gold labels are the mean of **three samples from a roughly 4B-class teacher at temperature 0.7**, so every score measures agreement with that teacher, not correctness. Two tracks: **Track A** splits the official test set by case into a calibration half and an evaluation half (200 cases each); **Track B** retrains the checkpoint from the base model with the card's RLCD recipe on case-level splits. Intervals come from a case-level cluster bootstrap (10,000 resamples, BCa); 24 confirmatory tests use Benjamini–Hochberg FDR control. Hardware: Apple M5 Max, MPS.

The author states no affiliation with Convai Innovations, the benchmark publisher or TypeSafe (§13). The surname is close to the Laya developer's GitHub handle (NandhaKishorM); the files give no way to check the independence statement beyond the author's word.

## Key Insights
1. **The headline accuracy reproduces; one metric does not.** Accuracy 0.767 vs 0.766 on the card [0.7455, 0.7870]; Brier, ECE (0.214 vs 0.213), score MAE and all per-workflow and per-primitive accuracies within 0.004. **Soft accuracy does not**: 0.509 vs 0.471, with the interval excluding the card's value. Numeric precision, backend and every released harness version from 0.3.3 to 0.3.20 are ruled out; the cause is on the card side and remains open.
2. **The shipped checkpoint is under-confident, not over-confident.** Mean confidence is 0.553 at accuracy 0.767 (signed gap −0.214). Every occupied reliability bin of every primitive lies above the diagonal. When all bins have the same sign, every binned ECE variant collapses to |mean confidence − accuracy|, so the whole ECE family reads 0.214. Cause: the shipped per-option-count temperatures (1.25–1.98) **soften** the logits.
3. **One temperature fixes most of it.** A single temperature fitted on the calibration half, **T = 0.469** (sharpening), takes held-out ECE15 from 0.2035 to 0.0372 and NLL from 0.7027 to 0.5364. Per-primitive temperatures add almost nothing. Error-detection AUROC barely moves (0.766 → 0.780): calibration changes the confidence values, not their ranking.
4. **The preregistered selection rule picked an overfit calibrator.** Choosing by lowest fitting-split NLL selected isotonic regression (6–28 knots per curve). Its held-out NLL (0.7738) is worse than the uncalibrated model. The same happened on Track B, so it is a property of the rule at n = 200–240 cases. Hypothesis H2 therefore fails as frozen, although every temperature-family method improves significantly.
5. **The confidence gate misses its target out of sample.** The threshold τ = 0.70, chosen on the calibration half as the smallest value with accepted-set error ≤ 0.10 (0.0916 there), gives **0.1399** on the evaluation half at coverage 0.672. The cause is that calibrator and threshold were fitted on the same 1,000 decisions. With the one-parameter temperature, τ = 0.75 gives 0.100 out of sample at coverage 0.598. The confidence signal still beats random escalation by +6.5 accepted-set accuracy points. Requiring all five decisions of a case to be confident leaves 5.5 % coverage. One security decision is wrong at calibrated confidence 1.0.
6. **Robustness.** Four permutations of option order flip **6.75 %** of choice predictions. Lowercasing or a neutral prefix flips 1.4–1.7 %. Removing a load-bearing state field changes 49–66 % of that workflow's predictions and **lowers** mean confidence, the right direction for a gate. Reweighting to uniform gold labels costs about 0.08 accuracy, which therefore rides on skewed label priors.
7. **Calibrating on training data is contaminated.** Track B reproduces accuracy (0.771 vs 0.767, p = 0.57) and its clean identity configuration already has ECE 0.151 vs 0.214. Refitting temperatures on items the model was trained on degrades held-out ECE 3.7× (0.024 → 0.087).
8. **The benchmark ceiling.** The specialist (0.767) exceeds the teacher's self-agreement ceiling (0.735). The dataset card's own reading rule: well above 0.75 means a model has learned the teacher's quirks. No "beats the teacher" or "beats Jev" claim survives; the Jev row (0.727, ECE 0.144, signed gap +0.023) is third-party.
9. **No transfer to claim verification (E10, exploratory).** On 120 claims over 24 fictional workflow documents (60 supported, 60 not), with retrieval and one `noul` question per claim, accuracy is **0.617** [0.533, 0.683] against 0.858 on in-distribution `noul`. One in three unsupported claims is accepted; confidence AUROC is 0.589; no threshold reaches 10 % error. **Entity swaps and one-step inference are at chance (0.500)**; contradictions (0.750) and numbers (0.700) are detected best. Retrieval recall@5 is 0.84, so retrieval is not the whole explanation.
10. **Latency on Apple silicon:** p50 19.2 ms per decision (95.9 ms per five-question case), 54.3 decisions/s; batching does not raise throughput on MPS.

## Relevance to GroundOne
- **Calibration method choice.** A disjointly fitted parametric map (one temperature) generalises; isotonic regression fitted on about 1,000 decisions does not. This supports GroundOne's temperature + per-class bias fitted on dev, rather than a non-parametric calibrator ([[Calibration]]).
- **Direction of miscalibration is an operational quantity.** Two models with ECE 0.21 can fail in opposite directions. GroundOne reports reliability diagrams and the signed gap, not ECE alone ([[Expected Calibration Error]]).
- **Thresholds need re-validation.** A threshold that meets an error target in-sample can miss it out of sample when calibrator and threshold share data. GroundOne's served τ (D27) is fitted on dev and checked on T1; the dev set (9,996 decisions) is ten times larger than Nandakishore's calibration half.
- **Fitting on training data is the trap GroundOne avoids**: its calibration split is disjoint from training by source document ([[Datasets for GroundOne]]).
- **Groundedness is a different task.** A general typed-decision specialist fails out of distribution on claim verification. Its failures on entity swaps and inference match GroundOne's own blind spot (sentences that copy the source but alter a detail). This is the closest independent evidence that groundedness needs task-specific training ([[Groundedness Verification]]).
- **Statistics.** Case-level cluster bootstrap and FDR control across a test family mirror GroundOne's cluster bootstrap by source document ([[Statistical Significance and Bootstrap]]).

## Links
- Concepts: [[Laya]], [[Calibration]], [[Selective Prediction]], [[Expected Calibration Error]], [[Decision-Model Benchmarks]], [[Statistical Significance and Bootstrap]]
- Related sources: [[Convai Innovations 2026 - Laya model card]], [[Guo 2017 - On Calibration of Modern Neural Networks]], [[Geifman 2017 - Selective Classification for Deep Neural Networks]]
