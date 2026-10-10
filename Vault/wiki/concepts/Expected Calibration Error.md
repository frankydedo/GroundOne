---
type: concept
tags: [calibration, metrics, evaluation, ece, brier, nll]
---
# Expected Calibration Error (ECE)

## Plain-language version
Sort all predictions by how confident the model was. Put them into buckets, e.g. 0–10%, 10–20%, …, 90–100%. In each bucket, compare **how confident the model said it was** (average confidence) with **how often it was actually right** (accuracy). ECE is the **average gap**, weighted by how many predictions fall in each bucket. ECE = 0.05 means that, on average, the stated confidence is off by 5 percentage points. Lower is better, and 0 is perfect.

A **reliability diagram** is the picture of this: bars of accuracy per bucket against the diagonal "accuracy = confidence". Bars below the diagonal mean **overconfidence**, bars above mean underconfidence.

## Formal definition
Partition $n$ predictions into $M$ bins $B_1,\dots,B_M$ by confidence $\hat p_i$:
$$\mathrm{acc}(B_m)=\frac{1}{|B_m|}\sum_{i\in B_m}\mathbb 1[\hat y_i=y_i],\qquad \mathrm{conf}(B_m)=\frac{1}{|B_m|}\sum_{i\in B_m}\hat p_i$$
$$\boxed{\mathrm{ECE}=\sum_{m=1}^{M}\frac{|B_m|}{n}\,\bigl|\mathrm{acc}(B_m)-\mathrm{conf}(B_m)\bigr|}\qquad \mathrm{MCE}=\max_{m}\bigl|\mathrm{acc}(B_m)-\mathrm{conf}(B_m)\bigr|$$
([[Guo 2017 - On Calibration of Modern Neural Networks|Guo 2017]] Eqs. 3, 5; originally [[Naeini 2015 - Obtaining Well Calibrated Probabilities Using Bayesian Binning|Naeini 2015]] p. 2903.) ECE estimates $\mathbb E_{\hat P}\bigl[|P(\hat Y=Y\mid\hat P=p)-p|\bigr]$ (Guo Eq. 2). MCE is the worst-case bin, relevant for high-risk use.

**Binary variant.** Naeini defines ECE on the probability of the **positive class**: $o_i$ = fraction of positives in bin $i$, $e_i$ = mean predicted $P(z=1)$. Guo defines it on the **top-label confidence** $\max_k \hat p_k\in[0.5,1]$ for binary. For GroundOne these give **different numbers**. State which one is used. Recommended: report ECE on $P(\text{supported})$ (all of [0,1], the operational score) and optionally top-label ECE for comparison with the literature.

## Binning choices
| Choice | Used by | Pros / cons |
|---|---|---|
| **Equal-width**, M = 15 | Guo 2017 (Table 1) | comparable to most deep-learning papers; bins in the low-confidence range may be nearly empty and noisy |
| **Equal-width**, M = 10 | common default | same issue |
| **Equal-mass (adaptive) bins**, 10 | [[Kadavath 2022 - Language Models (Mostly) Know What They Know|Kadavath 2022]] (glossary: "10 bins, with an equal number of predictions in each"); Naeini sorts predictions before binning | every bin has the same statistical weight, so the estimate is more stable when confidences pile up near 0/1 (typical after fine-tuning) |
| RMS calibration error | Kadavath (reported alongside) | squares the gaps; "better motivated theoretically" but less common |
| BBQ-style averaging over binnings | Naeini | avoids choosing M; used for *calibrating*, rarely for reporting |

"**Adaptive ECE**" in later literature means the equal-mass version. Report it next to equal-width ECE when most predictions are near 0 or 1.

## Companion metrics (always report with ECE)
- **Brier score**: $\frac1n\sum_i(\hat p_i-y_i)^2$ for binary $y_i\in\{0,1\}$. A proper scoring rule that combines calibration and discrimination. Chance level on a balanced binary task is **0.25** (Kadavath glossary). Tian reports it after temperature scaling ("BS-t").
- **NLL / log loss**: $-\frac1n\sum_i\log\hat\pi(y_i\mid x_i)$. Proper scoring rule, minimised in expectation only by the true conditional (Guo Eq. 6). It is the objective used to fit the temperature. It punishes confident mistakes very heavily, which is useful for spotting a few catastrophic overconfident errors.
- **AUROC**: ranking quality only, ignores calibration (Kadavath glossary).
- **AURC / risk–coverage**: how useful the confidence is for abstention. See [[Selective Prediction]].

## Pitfalls
1. **A constant predictor can have ECE = 0.** Always predicting 50% on a balanced binary set is perfectly calibrated and useless ([[Tian 2023 - Just Ask for Calibration|Tian]], fn. 5). Never report ECE without Brier/NLL and AUROC/AURC.
2. **Depends on binning.** M and equal-width vs. equal-mass change the value. Fix them in advance and report them.
3. **Biased and noisy on small sets.** With few examples per bin, the absolute gap is biased upwards. Report confidence intervals (bootstrap over examples) when comparing systems on test sets of a few hundred examples (e.g. per-dataset slices of LLM-AggreFact).
4. **Top-label vs. class-probability.** As above, binary top-label ECE ignores whether the model is miscalibrated on the "supported" side or the "unsupported" side.
5. **Temperature scaling can lower ECE without changing ranking.** Reporting ECE after TS ("ECE-t", Tian) separates fixable miscalibration from poor discrimination.
6. **Domain shift.** ECE measured on in-domain validation data says little about ECE on another benchmark. Evaluate on each test domain.
7. **Reliability diagrams hide bin counts** (Guo §2). Show a confidence histogram alongside, as in Guo Fig. 1.
8. **After post-hoc calibration, ECE stops discriminating between systems.** Measured in GroundOne's equal-output comparison (B0d, 200 T1 answers, the same temperature + per-class bias fitted on dev for every system):
   - all systems reach ECE 0.03–0.05: GroundOne 0.034 / 0.030, judges 0.039–0.051;
   - binary AUROC spans 0.47–0.68 for the judges and 0.94–0.97 for GroundOne;
   - AURC is 0.048–0.063 vs 0.005–0.009.

   An affine map can always pull mean confidence onto the base rate, even when the scores do not rank correct above wrong. The same effect in the literature: GPT-4 gets ECE 0.064 on GSM8K by stating 100 % for every answer ([[Xiong 2024 - Can LLMs Express Their Uncertainty|Xiong 2024]] §5.2). **Report AUROC and AURC next to ECE, always.** See [[Verbalised vs Logit Confidence]] and [[Selective Prediction]].

## GroundOne reporting checklist
- ECE on $P(\text{supported})$: equal-width (M = 15) **and** equal-mass (10 bins); MCE.
- Brier, NLL; AUROC; balanced accuracy.
- All of the above **before and after** temperature scaling, with $T$ fitted on a separate calibration split.
- Reliability diagram + confidence histogram per model (0.5B, 3B) and per benchmark.
- Bootstrap 95% CIs. GroundOne uses a **cluster** bootstrap by source document (B = 2000), because sentences of one answer are not independent. See [[Statistical Significance and Bootstrap]].
- Status (2026-10-10): binary ECE on T1 0.30 → 0.019 (0.5B) and 0.18 → 0.019 (3B) after temperature + per-class bias on dev; it does not transfer to VitaminC (T3). AUROC/AURC are reported alongside (pitfall 8).

## Links
- [[Calibration]], [[Selective Prediction]], [[GroundOne]], [[Groundedness Verification]], [[Hallucination Detection]], [[LLM-as-a-Judge]], [[Reinforcement Learning with Calibrated Decisions]], [[System One Models]]
- Sources: [[Naeini 2015 - Obtaining Well Calibrated Probabilities Using Bayesian Binning]], [[Guo 2017 - On Calibration of Modern Neural Networks]], [[Kadavath 2022 - Language Models (Mostly) Know What They Know]], [[Tian 2023 - Just Ask for Calibration]], [[Xiong 2024 - Can LLMs Express Their Uncertainty]]
- Related concepts: [[Verbalised vs Logit Confidence]], [[Statistical Significance and Bootstrap]]
