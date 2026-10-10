---
type: concept
tags: [calibration, uncertainty, evaluation, llm, groundone]
---
# Calibration

## Definition
A probabilistic predictor is **calibrated** if its stated confidence matches how often it is right. Among all predictions made with confidence $p$, a fraction $p$ should be correct:
$$P(\hat Y = Y \mid \hat P = p) = p \quad \forall p\in[0,1]$$
([[Guo 2017 - On Calibration of Modern Neural Networks|Guo et al. 2017]], Eq. 1; same idea in [[Naeini 2015 - Obtaining Well Calibrated Probabilities Using Bayesian Binning|Naeini et al. 2015]]).

**In plain words:** if the verifier says "90% supported" for 100 sentences, about 90 of them should really be supported. A model can be very *accurate* but badly *calibrated* (always 99.9% sure, sometimes wrong). It can also be well calibrated but useless: always "50%" on a balanced binary task has perfect ECE ([[Tian 2023 - Just Ask for Calibration|Tian 2023]], fn. 5). Calibration (do the numbers mean what they say?) and **discrimination/ranking** (are the right examples ranked above the wrong ones?) are **separate** properties, so measure both.

How to measure it: [[Expected Calibration Error]] (ECE/MCE, reliability diagrams), Brier score, NLL. How to use it: [[Selective Prediction]] (thresholds, abstention).

## Why modern networks and LLMs are miscalibrated
- **Capacity and NLL overfitting.** Deep networks keep lowering training NLL by becoming more confident after they already classify everything correctly. Depth, width, BatchNorm and less weight decay all raise ECE (Guo §3).
- **Pretrained LMs are fairly well calibrated *if the format is right*.** Explicit lettered options, each a single token, and few-shot prompts give calibrated multiple-choice and True/False probabilities. Calibration improves with size ([[Kadavath 2022 - Language Models (Mostly) Know What They Know|Kadavath 2022]] §2–3.2). A "none of the above" option and zero-shot self-evaluation hurt it (§3.1, §4).
- **RLHF / preference tuning makes logits overconfident.** The RL objective pushes mass onto the rewarded answer instead of matching frequencies. Kadavath §3.3: RLHF policies "naively seem miscalibrated", but one temperature $T=2.5$ largely fixes them. Tian Fig. 2: Llama-2-70B chat has worse ECE and AUC than its base model.
- **Small models are worse.** In Kadavath's sweep calibration error falls with size, and 800M was the smallest model tested. GroundOne's 0.5B/3B models should be expected to need explicit calibration.
- **Fine-tuning can introduce it.** Cross-entropy fine-tuning on easy pairs pushes logits to extremes, the same NLL-overfitting mechanism as above.
- **Distribution shift.** Calibration fitted on one domain (NLI data) may not hold on another (RAG answers). Calibration methods assume the validation set matches deployment (Guo §4).

## Verbalized vs. logit confidence
| | Logit / token-probability confidence | Verbalized confidence |
|---|---|---|
| What | probability of the answer token(s), e.g. $P(\text{A})$ vs $P(\text{B})$ | model *writes* "0.8" or "likely" |
| Cost | one forward pass, no generation | requires decoding (often 2 stages) |
| RLHF models | often overconfident (Tian Tables 1–5; Kadavath §3.3) | often better calibrated for large RLHF models, about 50% lower ECE (Tian) |
| Small/open models | usable with the right format + temperature scaling (Kadavath) | weaker; Llama-2-70B-Chat already inconsistent (Tian Table 5) |
| Fixable post hoc? | yes: temperature / Platt on logits | only via mapping tables (Tian's "Ling. 1S-opt") |

Note: for closed APIs Tian's "logit" baseline is estimated **by sampling** (10 samples), not read from logits. **GroundOne's position:** read the true restricted logits of a model **fine-tuned for the decision**, then calibrate them. This avoids decoding and does not rely on a large model's ability to verbalize confidence. A verbalizing [[LLM-as-a-Judge]] is the natural baseline to compare against. *(Superseded detail: the readout is now 3-way, A/B/C = supported / contradicted / not mentioned, not 2-way, and the calibration is temperature + per-class bias; see "GroundOne recipe (current)" below.)*

The comparison was run (equal-output judge B0d). Verbalised probabilities from same-size Qwen2.5 judges are nearly uninformative: the 3B writes one-hot vectors for 93 % of sentences. Logit-read judge probabilities are better (3B AUROC 0.68 vs 0.58) but far below GroundOne (0.94–0.97). Full analysis in [[Verbalised vs Logit Confidence]], with [[Xiong 2024 - Can LLMs Express Their Uncertainty|Xiong 2024]] as the main literature anchor.

## Post-hoc calibration methods
All are fitted on a **held-out calibration split** while the model stays frozen.
- **Temperature scaling** ([[Guo 2017 - On Calibration of Modern Neural Networks|Guo]] Eq. 9): $\hat q = \mathrm{softmax}(z/T)$, with one scalar $T>0$ fitted by minimising NLL. $T>1$ softens overconfident outputs. **The argmax and the ranking do not change**, so accuracy and AUROC/AURC stay the same. Often the best method in practice: "miscalibration is intrinsically low dimensional."
- **Platt scaling** (binary): $\hat q=\sigma(a z + b)$, fitted by NLL. With two classes and margin $z=\ell_A-\ell_B$, temperature scaling is Platt with $b=0$, $a=1/T$. The **bias $b$** can correct a shift in base rate between training and deployment.
- **Vector / matrix scaling**: multiclass generalisations of Platt. They overfit when there are many classes (Guo §5).
- **Non-parametric**: histogram binning, isotonic regression, **BBQ** (Bayesian averaging over binnings, [[Naeini 2015 - Obtaining Well Calibrated Probabilities Using Bayesian Binning|Naeini]]). More flexible, but they can change predictions, need more data, and in Guo's experiments usually did not beat temperature scaling.
- **Training-time**: proper scoring rules (log loss, Brier) as the objective. This is the idea behind [[Reinforcement Learning with Calibrated Decisions]] in [[Jev]].

## Contextual calibration and bias correction (decision calibration)
"Calibration" also names a different goal: removing a **bias in the decision**, not aligning confidence with accuracy.
- [[Zhao 2021 - Calibrate Before Use|Zhao et al. 2021]] show that GPT-3's few-shot predictions are shifted towards frequent, recent and pre-training-common labels (§4). **Contextual calibration** estimates the shift by scoring a content-free input ("N/A", "[MASK]", "") with the same prompt. It then applies $\hat q = \mathrm{softmax}(W\hat p)$ with $W = \mathrm{diag}(\hat p_\text{cf})^{-1}$, which makes the content-free prediction uniform. No labels are needed, and accuracy improves by up to 30 points (Table 1). Their footnote 4 stresses that this is distinct from statistical calibration.
- [[Zheng 2024 - LLMs Are Not Robust Multiple Choice Selectors|Zheng 2024]] (PriDe) do the same for MCQ option-ID priors, estimating the prior by permuting option contents on a few test items (§3).
- **Supervised equivalent: per-class bias.** Dividing by $\hat p_\text{cf}$ equals adding $-\log\hat p_\text{cf}$ to the logits. With labelled held-out data the offset can instead be fitted by NLL together with a temperature: $\mathrm{softmax}(z/T + b)$, i.e. temperature scaling plus a bias vector (a constrained form of vector scaling, Guo §4.2). The bias moves the **decision boundary**, which temperature alone cannot do, because temperature preserves the argmax.
- A shifted but well-ranked score can also be fixed by moving the **threshold**: Zhao Fig. 5 shows 94 % SST-2 accuracy at P(Positive) = 0.68 instead of 0.5.

See [[Letter-Token Readout]] for the letter-token biases these methods correct.

## GroundOne recipe (current)
*Updated 2026-10-10 from the checkpoint and D20–D27; replaces the 2-way plan below.*
1. **Train:** class-weighted cross-entropy over the restricted **3-way** logits {A, B, C} = supported / contradicted / not mentioned, at each " Verdict:" marker (design b, D22–D23).
2. **Calibrate (D23/D24):** temperature + per-class bias, $\mathrm{softmax}(z/T + b)$ with $b_\text{supported} = 0$, fitted by NLL on dev. The calibration is bound to the model fingerprint (adapter SHA + prompt version). The per-class bias is the supervised analogue of Zhao's contextual calibration.
3. **Use:** primary classification metrics use the **raw (balanced) decision**. Calibrated probabilities feed ECE, AURC and the **served threshold** τ on calibrated P(supported), fitted on dev by maximising three-way macro recall (τ ≈ 0.90–0.94, D27). The served label is "supported" iff P(supported) ≥ τ, otherwise the more probable of the other two.
4. **Results:** binary ECE on T1 0.30 → 0.019 (0.5B) and 0.18 → 0.019 (3B); run 2 0.23 → 0.020. Calibration **does not transfer** to VitaminC (T3). After the same calibration, generative judges also reach ECE 0.03–0.05 while their AUROC is 0.47–0.68. So ECE alone does not separate systems: report AUROC and AURC ([[Expected Calibration Error]], [[Selective Prediction]]).

## GroundOne recipe (earlier plan, superseded)
*Kept for history. Superseded by the 3-way design (D20, D22) and the temperature + bias calibration (D23/D24) above.*
1. Train: cross-entropy on the **restricted 2-way logits** $\{\ell_A,\ell_B\}$ (A = supported, B = not supported). Cross-entropy is a proper scoring rule, so a well-specified model trained this way is pushed towards calibration on the training distribution.
2. Calibrate: fit $T$ (and optionally a Platt bias) on a held-out split, **per domain** if possible.
3. Report before/after: ECE (equal-width M = 15 and equal-mass), Brier, NLL, reliability diagram, and, unaffected by $T$, AUROC and AURC.
4. Ablations: base vs. instruct starting checkpoint (RLHF effect), 0.5B vs. 3B (size effect), temperature-only vs. Platt (base-rate shift).

## Calibration is not intrinsic (evidence from decision models, ingest 2026-10-10)
Vendor claims of "calibrated by training" (RLCD) do not remove the need for post-hoc calibration on the target distribution:
- **[[Laya]] (RLCD-trained) ships in the wrong direction.** The typed-decisions checkpoint is uniformly **under-confident** (mean confidence 0.553 at accuracy 0.767), because its shipped temperatures (1.25–1.98) soften the logits. **One disjointly fitted temperature, T = 0.469**, takes held-out ECE from 0.204 to 0.037. Isotonic regression, chosen by lowest fitting-split NLL on about 1,000 decisions, overfits: its held-out NLL is worse than no calibration. Refitting temperatures on trained-on items triples held-out ECE ([[Nandakishore 2026 - Laya as a Typed Probabilistic Assessor (arXiv 2609.33843)|Nandakishore 2026]]). The vendor card itself reports over-confidence for the base checkpoints (ECE 0.466 → 0.081 after refitting). The direction depends on the checkpoint, and ECE alone hides it: when every bin errs the same way, all binned ECE variants collapse to |mean confidence − accuracy|.
- **[[Jev]]: good ranking, misplaced threshold.** Choice probabilities are well calibrated (pooled ECE 0.028), but single binary `noul` probabilities are under-confident (mean P(yes) 0.465 vs a 0.518 yes-rate). Multi-label fan-out over-predicts yes (0.209 vs 0.041). At the fixed 0.5 threshold, good AUROC turns into poor F1. **Thresholds tuned on 1,000 training examples** raise UNFAIR-ToS micro-F1 from 0.50 to 0.75; the same holds for open letter readouts ([[Deusser 2026 - Evaluating and Benchmarking the System One Model Jev (arXiv 2609.37647)|Deußer 2026]]).
- **Calibration does not transfer.** Sciev's internal ECE of 0.01–0.04 becomes 0.28 on SciFact ([[Robles-Fernandez 2026 - Sciev Typed Scientific Decisions Without Generation (manuscript, sciev.org)|Robles-Fernández 2026]]). Laya's ECE is 0.015 on AG News and 0.506 on Banking77 ([[morrenhale 2026 - Decision benchmark Jev vs Laya vs Julia-1 dataset card|morrenhale]]).
- **Thresholds fitted together with the calibrator can miss out of sample.** Laya's confidence gate met its 10 % error target on the fitting half (0.092) and missed it on held-out data (0.140). With the one-parameter temperature it landed on target (Nandakishore 2026).
- **Confidence can rank errors backwards under a systematic error** (label/definition conflict: error AUROC 0.24; [[Azizi 2026 - Labels Override Definitions in Jev-Style Typed Decision Models (arXiv 2610.02586)|Azizi 2026]]).

**What this supports in GroundOne's recipe.** A parametric map (temperature + per-class bias) fitted on a dev split disjoint from training, a **decision threshold fitted on dev** rather than a fixed 0.5 (D27), per-domain reporting (calibration stated not to transfer to T3), and AUROC/AURC and reliability diagrams alongside ECE. GroundOne's dev split (9,996 decisions) is ten times larger than the 1,000-decision fitting half in which Laya's isotonic calibrator and gate overfit.

## Links
- [[Expected Calibration Error]], [[Selective Prediction]], [[Reinforcement Learning with Calibrated Decisions]]
- [[GroundOne]], [[Groundedness Verification]], [[Hallucination Detection]], [[LLM-as-a-Judge]], [[System One Models]], [[When System One Beats an LLM]], [[Jev]], [[Qwen2.5]]
- Sources: [[Naeini 2015 - Obtaining Well Calibrated Probabilities Using Bayesian Binning]], [[Guo 2017 - On Calibration of Modern Neural Networks]], [[Kadavath 2022 - Language Models (Mostly) Know What They Know]], [[Tian 2023 - Just Ask for Calibration]], [[Geifman 2017 - Selective Classification for Deep Neural Networks]], [[Zhao 2021 - Calibrate Before Use]], [[Xiong 2024 - Can LLMs Express Their Uncertainty]], [[Zheng 2024 - LLMs Are Not Robust Multiple Choice Selectors]]
- Related concepts: [[Verbalised vs Logit Confidence]], [[Letter-Token Readout]], [[Statistical Significance and Bootstrap]], [[Laya]], [[Decision-Model Benchmarks]]
