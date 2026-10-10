---
type: source
author: "Rotem Dror, Gili Baumer, Segev Shlomov, Roi Reichart"
date: 2018
venue: "ACL 2018 (Long Papers), pp. 1383–1392 (ACL Anthology P18-1128)"
url: "https://aclanthology.org/P18-1128/"
tags: [source, paper, statistics, significance-testing, bootstrap, multiple-comparisons, evaluation, methodology]
---
# Dror 2018 – The Hitchhiker's Guide to Testing Statistical Significance in Natural Language Processing

**Raw file**: `raw/Dror 2018 - The Hitchhiker's Guide to Testing Statistical Significance in NLP_ingested.pdf`

## Overview
An opinion and tutorial paper. It defines the hypothesis-testing setup for comparing two algorithms on one dataset (§2) and reviews parametric and non-parametric tests used in NLP (§3.2). It gives a decision tree for choosing a test (§3.3, Fig. 1), surveys how ACL and TACL 2017 papers actually test significance (§4), and lists open problems: dependent observations and cross-validation (§5). Code for all tests is released.

## Key Insights
1. **Setup (§2.1).** The test statistic is $\delta(X) = M(A,X) - M(B,X)$ for a metric M. The null hypothesis is $\delta \le 0$. The p-value is $\Pr(\delta(X) \ge \delta_\text{obs} \mid H_0)$, compared with a significance level α fixed in advance. Type I error means a false claim of superiority; power means 1 − Type II error.
2. **Choosing a test (§3, Fig. 1).**
   - If the distribution of δ is known (e.g. normal by the CLT for mean-type metrics), use a **parametric** test: the paired t-test.
   - Otherwise use **non-parametric** tests:
     - *sampling-free* ones are cheaper and less powerful: sign test, McNemar (paired binary outcomes; Cochran's Q for multi-class), Wilcoxon signed-rank;
     - *sampling-based* ones are more powerful and costlier: permutation / approximate randomisation, and the **paired bootstrap**.
   - The bootstrap "is less effective for small test sets", because it assumes the test set resembles the population (§3.2).
   - Normality can be checked with Shapiro-Wilk, Kolmogorov-Smirnov or Anderson-Darling (§3.1).
3. **Survey of 2017 papers (§4, Tables 2–3).**
   - Of 180 experimental ACL long papers, only 63 report a significance test, 21 of those do not name it, and 6 of the 42 that do use an inappropriate test (e.g. a t-test on non-mean metrics, or a bootstrap on a tiny test set).
   - Multiplicity: of 110 ACL papers that use several datasets, only 3 correct for multiple comparisons (all Bonferroni); TACL does slightly better, with 4 of 19.
   - "Significant" is often misused to mean "large" or "important".
4. **Open issues (§5).**
   - **Dependent observations.** Most tests assume i.i.d. examples, but NLP test sets contain sentences from the same document, author or debate (WSJ, Europarl). The effect is "hard to quantify".
   - **Cross-validation folds** are not independent. The authors propose per-fold p-values combined by replicability analysis (K-Bonferroni).

## Relevance to GroundOne
- **Choice of test.** GroundOne's metrics include macro (balanced) recall, AUROC, AURC and ECE. These are not means of per-item scores, so by Dror's tree a **sampling-based, non-parametric** test is right: the paired bootstrap. T1 (17,284 sentences, 447 source groups) is far from the small-sample regime where Dror warn against the bootstrap. The K ≥ 14 slice (93 groups) and single T2 datasets are closer to it.
- **Dependent observations (open issue 1) are handled by clustering.** GroundOne resamples whole leakage groups (source document, document, Wikipedia page), not sentences. This is the standard remedy Dror call for but do not spell out. It should be cited as such in Ch. 5.
- **Multiple comparisons are *not* corrected in GroundOne.** The bootstrap reports dozens of pairwise tests: systems × T1/T2/T3 × metrics × K bands. Most are far below α (p < 0.0005), so a Holm or Bonferroni correction would not change them. Borderline ones would not survive a correction: GroundOne 0.5B vs Rizzo-Flow on T2 is +0.062 [+0.001, +0.122], p = 0.047, after the 2026-10-10 audit fix. The thesis should either apply Holm–Bonferroni within each family of claims or state the number of tests and flag these p-values as uncorrected.
- **Wording.** In line with Dror's point on "significant": the thesis notes already reserve the word for bootstrap results ("on par" for T2 3B vs MiniCheck, +0.8 [−0.5, +2.1], p = 0.24).
- **Seed variance** is outside Dror's framework, which compares two fixed algorithm outputs. See [[Fine-tuning Instability and Seeds]] and [[Statistical Significance and Bootstrap]].

## Links
- Concepts: [[Statistical Significance and Bootstrap]], [[Fine-tuning Instability and Seeds]]
- Related sources: [[Koehn 2004 - Statistical Significance Tests for MT Evaluation (paired bootstrap)]], [[Berg-Kirkpatrick 2012 - An Empirical Investigation of Statistical Significance in NLP]], [[Dodge 2020 - Fine-Tuning Pretrained LMs (weight init, data order, early stopping)]]
- Thesis context: [[GroundOne]]
