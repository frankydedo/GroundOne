---
type: concept
tags: [statistics, significance-testing, bootstrap, cluster-bootstrap, multiple-comparisons, evaluation, methodology, groundone]
---
# Statistical Significance and Bootstrap

## Why test
A test set is a sample. If system A beats system B by δ on it, the question is whether a new test set from the same distribution would show a similar win, or whether δ is chance. **Hypothesis testing** answers that: under the null hypothesis $H_0: \delta \le 0$, the **p-value** is $\Pr(\delta(X) \ge \delta_\text{obs} \mid H_0)$, compared with a level α fixed in advance (usually 0.05). A **confidence interval** gives the range of plausible true differences, and is usually more informative than a bare p ([[Dror 2018 - The Hitchhiker's Guide to Testing Statistical Significance in NLP|Dror 2018]] §2).

**In plain words:** a p-value says how surprising the observed gap would be if the systems were really equal. A 95 % interval that excludes 0 means the same thing as p < 0.05 (two-sided), and also shows how big the gap could be.

## Choosing a test (Dror 2018 §3)
- **Parametric (paired t-test)** if the statistic is approximately normal, e.g. a mean of per-item scores by the CLT.
- **Non-parametric, sampling-free:** sign test; **McNemar** for paired binary correctness (Cochran's Q for multi-class); Wilcoxon signed-rank.
- **Non-parametric, sampling-based:** permutation / approximate randomisation and the **paired bootstrap**. These work for any metric, including those that are not means (BLEU, F1, macro recall, AUROC, ECE). They are the default for NLP metrics, but less reliable on very small test sets.

## The bootstrap
- **Percentile CI** ([[Koehn 2004 - Statistical Significance Tests for MT Evaluation (paired bootstrap)|Koehn 2004]] §5). Resample the n test items with replacement B times, recompute the metric, and take the 2.5 / 97.5 percentiles. Assumption: resampling the test set approximates drawing new test sets. Validated on Europarl: 97 of 100 intervals covered the "true" BLEU.
- **Paired bootstrap** (Koehn §6). Use the *same* resampled indices for both systems and look at the distribution of the difference. Pairing cancels shared per-item difficulty and makes the test much more sensitive than comparing two separate intervals.
- **Re-centring** ([[Berg-Kirkpatrick 2012 - An Empirical Investigation of Statistical Significance in NLP|Berg-Kirkpatrick 2012]] §2.1). The bootstrap distribution is centred on δ_obs, not on 0. The one-sided p is the share of resamples with $\delta^{(i)} > 2\delta_\text{obs}$, or equivalently, when the distribution is symmetric, with $\delta^{(i)} < 0$.
- **Cluster (block) bootstrap.** If test items are dependent (sentences of one document, answers about one source), resample whole **clusters**. Koehn §3 showed that consecutive sentences are correlated (BLEU 21–37 % across consecutive blocks vs a narrow spread across broad samples). Dror §5 list dependent observations as the main open issue of NLP significance testing. Ignoring the dependence makes intervals too narrow.

## What significance does and does not mean
1. **Test size dominates, with diminishing returns** (Berg-Kirkpatrick §4.1): the p < 0.05 threshold falls from 3.00 F1 on 100 sentences to 0.22 F1 on 24K.
2. **Correlated systems reach significance with smaller gains** (Berg-Kirkpatrick §3). Variants of the same model can differ "significantly" by tiny amounts.
3. **In-domain calibrated, out-of-domain not** (Berg-Kirkpatrick §4.2). A p ≈ 0.05 on WSJ §23 predicts the Brown-corpus winner only 48 % of the time.
4. **Test-set resampling ignores training randomness.** The bootstrap treats both systems as fixed functions. Seed, data order and initialisation change the function itself. That variance can be as large as the gains being tested ([[Dodge 2020 - Fine-Tuning Pretrained LMs (weight init, data order, early stopping)|Dodge 2020]]). See [[Fine-tuning Instability and Seeds]].
5. **Multiple comparisons.** With many tests, some false positives at α = 0.05 are expected. Corrections: Bonferroni, Holm (uniformly more powerful), or replicability analysis across datasets. Only 3 of 110 multi-dataset ACL 2017 papers corrected (Dror §4).
6. **Wording.** "Significant" should keep its statistical meaning (Dror §4).

## What GroundOne does
- **Protocol** (`groundone bootstrap`, `eval/bootstrap.py`). No model is re-run: the bootstrap works from saved predictions and reproduces the point estimates. B = 2000, 95 % percentile intervals, two-sided bootstrap p.
- **Cluster resampling by leakage group:**
  - T1 and the latency subset: RAGTruth source document (447 groups on T1);
  - T2: document (8,329 groups), resampled **within each dataset** because the macro averages datasets;
  - T3: Wikipedia page (1,257 groups).
- **Paired** differences use the same resamples, on rows both systems scored. Rizzo-Flow's 7 skipped T2 items are dropped rather than counted as wrong (audit fix, 2026-10-10).
- **Claims it supports:**
  - On T1, GroundOne beats every baseline; 3B − 0.5B is +0.063 [+0.052, +0.076] three-way, and +0.116 [+0.050, +0.180] at K ≥ 14 (93 groups).
  - B2 vs readout: +0.248 / +0.071.
  - Speed-ups at K ≥ 14: 1.95× [1.82, 2.14] and 6.16× [5.72, 6.67] for the 0.5B.
- **Claims it tempers:**
  - T2 macro, 3B vs MiniCheck-RoBERTa: +0.8 [−0.5, +2.1], p = 0.24, so "on par", not "above".
  - T2 RAG subset, 0.5B vs RoBERTa: p = 0.74.
  - T1 AUROC, 0.5B vs Rizzo-Flow on its subsample: p = 0.15.
- **Caveat discovered by the bootstrap itself.** Run 1 (seed 1234) vs run 2 (seed 777) of the 0.5B, which share data, config and code, differ "significantly" on T2 macro (−0.013 [−0.024, −0.003]) and T3 AUROC (−0.025 [−0.037, −0.012]). On T1 they do not (+0.001 [−0.008, +0.011]). This is point 2 and point 4 at once: two maximally correlated systems, and a test that ignores seed variance. **Rule adopted:** differences between systems on T2/T3 smaller than the observed seed spread (about 1.5 T2 macro points, about 0.025 T3 AUROC, up to 10 points on single T2 datasets) are not claimed.

## Open gaps (for Ch. 5 / Ch. 7)
- **Multiplicity is not corrected.** Dozens of pairwise tests are reported. Most have p < 0.0005 and would survive Holm–Bonferroni. Borderline ones such as GroundOne 0.5B vs Rizzo-Flow on T2 (p = 0.047) would not. State the number of tests, or correct within each family of claims.
- **Seed variance is estimated from two converged runs only** (plus one collapsed run). A seed-aware interval would need more runs; a minimum is to report run 1 and run 2 side by side and treat their spread as a floor on meaningful differences.
- **Out-of-domain claims** (T3, single T2 datasets) should rely on effect sizes and consistency across systems, not on p-values alone (Berg-Kirkpatrick §4.2).
- State which bootstrap p variant is used (sign-flip count vs re-centred 2δ).

## Links
- Sources: [[Koehn 2004 - Statistical Significance Tests for MT Evaluation (paired bootstrap)]], [[Berg-Kirkpatrick 2012 - An Empirical Investigation of Statistical Significance in NLP]], [[Dror 2018 - The Hitchhiker's Guide to Testing Statistical Significance in NLP]], [[Dodge 2020 - Fine-Tuning Pretrained LMs (weight init, data order, early stopping)]]
- Concepts: [[Fine-tuning Instability and Seeds]], [[Expected Calibration Error]] (bootstrap CIs for ECE), [[Selective Prediction]]
- Thesis context: [[GroundOne]], [[RAGTruth]], [[LLM-AggreFact]], [[VitaminC]], [[MiniCheck]], [[Rizzo-Flow]]
