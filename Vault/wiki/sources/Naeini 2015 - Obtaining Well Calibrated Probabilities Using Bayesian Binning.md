---
type: source
author: "Mahdi Pakdaman Naeini, Gregory F. Cooper, Milos Hauskrecht"
date: 2015
venue: "AAAI 2015 (Proceedings of the 29th AAAI Conference on Artificial Intelligence, pp. 2901–2907)"
url: "https://github.com/pakdaman/calibration (code linked from the paper; paper in AAAI-15 proceedings)"
tags: [source, paper, calibration, ece, binary-classification, post-hoc-calibration]
---
# Naeini 2015 – Obtaining Well Calibrated Probabilities Using Bayesian Binning

**Raw file**: `raw/Naeini 2015 - Obtaining Well Calibrated Probabilities Using Bayesian Binning_ingested.pdf`

## Overview
Proposes **Bayesian Binning into Quantiles (BBQ)**, a non-parametric, post-hoc calibration method for **binary** classifiers, and is the paper usually cited as the origin of the **Expected Calibration Error (ECE)** and **Maximum Calibration Error (MCE)** metrics (later popularised by [[Guo 2017 - On Calibration of Modern Neural Networks|Guo et al. 2017]]).

Post-hoc calibration maps a classifier's raw score $y$ to a calibrated probability $P(z=1\mid y)$ without retraining the model. The paper groups existing methods into (p. 2901):
- **parametric**: Platt scaling, a sigmoid $\sigma(a\,y+b)$ fitted by maximum likelihood. Limitation: the sigmoid shape "only rarely fits the true distribution of predictions";
- **non-parametric**: histogram (quantile) binning (Zadrozny & Elkan 2001) and isotonic regression via PAV (Zadrozny & Elkan 2002). Limitations: a fixed number of bins / fixed boundaries, and an isotonicity assumption that is "violated in practice quite frequently".

## Key Insights
1. **BBQ = Bayesian model averaging over many equal-frequency binnings** (pp. 2902–2903). Each binning model $M$ (number of bins $B$, partition, per-bin Beta–binomial parameters) is scored with a BDeu-style marginal likelihood. The calibrated probability is the score-weighted average over models:
   $$P(z=1\mid y)=\sum_{i=1}^{T}\frac{\mathrm{Score}(M_i)}{\sum_j \mathrm{Score}(M_j)}\,P(z=1\mid y, M_i).$$
   The candidate bin counts range over $B\in\{\sqrt[3]{N}/C,\dots,C\sqrt[3]{N}\}$ with $C=10$, motivated by minimax results for histogram classifiers with $\Theta(\sqrt[3]{N})$ bins. This removes the need to pick one bin count.
2. **Definition of ECE and MCE** (p. 2903): predictions are sorted and split into $K$ bins ($K=10$ in their experiments).
   $$\mathrm{ECE}=\sum_{i=1}^{K}P(i)\,|o_i-e_i|,\qquad \mathrm{MCE}=\max_i |o_i-e_i|$$
   where $o_i$ is the observed fraction of positives in bin $i$, $e_i$ the mean predicted probability in bin $i$, and $P(i)$ the fraction of instances in bin $i$. Note that this is the **binary, positive-class** form, not the "top-label confidence" form used by Guo et al. See [[Expected Calibration Error]].
3. **Calibration and discrimination are separate** (Table 1b, p. 2904). A quadratic-kernel SVM has AUC 1.00 and accuracy 0.99 but ECE 0.14 and MCE 0.35. After calibration, AUC and accuracy stay the same while ECE goes to about 0.00.
4. **Results** (simulated: Table 1; 30 UCI/LibSVM datasets × LR/SVM/NB: Figs. 3–7, Friedman + Holm tests). BBQ is statistically better than histogram binning, Platt and isotonic regression on ECE and MCE. On RMSE it ties with isotonic regression. AUC and accuracy are statistically unchanged. Platt does badly when its sigmoid assumption is wrong (linear SVM on non-linear data: ECE 0.28, the same as uncalibrated).
5. A recurring observation: post-hoc calibration usually **keeps the ranking** (AUC). Platt is monotone, so its AUC equals that of the base classifier.

## Relevance to GroundOne
- GroundOne's verdict is a **binary** decision (supported vs. unsupported sentence) read from two letter logits A/B. The paper's binary setting fits directly: the score is the logit margin $z=\ell_A-\ell_B$, and Platt, histogram binning, isotonic regression and BBQ can all be fitted on it on a held-out calibration split.
- With two classes, **temperature scaling is Platt scaling without the bias** ($\sigma(z/T)$ vs. $\sigma(az+b)$). If the fine-tuned model is shifted (e.g. systematically biased towards "supported"), full Platt with a bias term may beat pure temperature scaling. Report both. See [[Calibration]].
- BBQ/isotonic are good **non-parametric ablations**, but [[Guo 2017 - On Calibration of Modern Neural Networks|Guo et al.]] found that simpler methods usually win on held-out data and that binning methods can change predictions.
- Use the ECE definition with care. Always state the binning (equal-width vs. equal-mass, number of bins) and whether it is computed on $P(\text{supported})$ or on top-label confidence. These give different numbers.

## Links
- Concepts: [[Calibration]], [[Expected Calibration Error]], [[Selective Prediction]]
- Related sources: [[Guo 2017 - On Calibration of Modern Neural Networks]], [[Kadavath 2022 - Language Models (Mostly) Know What They Know]], [[Tian 2023 - Just Ask for Calibration]]
- Thesis context: [[System One Models]], [[Groundedness Verification]], [[Reinforcement Learning with Calibrated Decisions]]
