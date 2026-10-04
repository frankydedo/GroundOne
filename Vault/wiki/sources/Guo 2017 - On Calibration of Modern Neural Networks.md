---
type: source
author: "Chuan Guo, Geoff Pleiss, Yu Sun, Kilian Q. Weinberger"
date: 2017
venue: "ICML 2017 (PMLR 70)"
url: "https://arxiv.org/abs/1706.04599"
tags: [source, paper, calibration, temperature-scaling, ece, reliability-diagram, nll]
---
# Guo 2017 – On Calibration of Modern Neural Networks

**Raw file**: `raw/Guo 2017 - On Calibration of Modern Neural Networks_ingested.pdf`

## Overview
The standard reference for **miscalibration of modern deep networks** and for **temperature scaling**. The paper shows that deep, high-capacity networks (ResNets, DenseNets) are **overconfident**: their average confidence is above their accuracy. Older, smaller networks such as LeNet were not. It then compares post-hoc fixes on vision and NLP classification. The conclusion is that a **single scalar temperature** fitted on a validation set is usually the most effective calibrator (abstract; §5).

## Key Insights
1. **Definitions (§2)**.
   - Perfect calibration: $P(\hat Y=Y\mid \hat P=p)=p\;\;\forall p$ (Eq. 1).
   - **Reliability diagram**: accuracy vs. confidence over $M$ equal-width bins $I_m=(\frac{m-1}{M},\frac{m}{M}]$. It does *not* show how many samples fall in each bin.
   - **ECE** $=\sum_m \frac{|B_m|}{n}\,|\mathrm{acc}(B_m)-\mathrm{conf}(B_m)|$ (Eq. 3), computed on the **top-label confidence** $\hat p=\max_k \mathrm{softmax}(z)_k$. **MCE** $=\max_m|\mathrm{acc}-\mathrm{conf}|$ (Eq. 5).
   - **NLL** $=-\sum_i\log\hat\pi(y_i\mid x_i)$ (Eq. 6), minimised in expectation only by the true conditional distribution.
2. **What causes miscalibration (§3, Fig. 2)**: more depth and width, Batch Normalization, and less weight decay all raise ECE even when they lower error. Mechanism (Fig. 3): after the training set is almost perfectly classified, the network keeps lowering NLL by becoming more confident. NLL overfits while 0/1 error still improves (CIFAR-100: error 29%→27% while test NLL rises). In the paper's words, "overfitting manifests in probabilistic error rather than classification error."
3. **Methods compared (§4)**:
   - binary: histogram binning, isotonic regression, BBQ ([[Naeini 2015 - Obtaining Well Calibrated Probabilities Using Bayesian Binning|Naeini 2015]]), Platt scaling $\sigma(az+b)$;
   - multiclass: matrix scaling, vector scaling, and **temperature scaling** $\hat q=\max_k\mathrm{softmax}(z/T)_k$ (Eq. 9), with $T$ fitted by NLL on the validation set.

   Because $T$ does not change the argmax, **temperature scaling does not change accuracy**.
4. **Results (Table 1, ECE with M = 15 bins)**: uncalibrated ECE is typically 4–10%. Temperature scaling gives the best or near-best result on vision tasks, e.g. CIFAR-100 ResNet-110: 16.53% → 1.26%, and ResNet-110 (SD): 12.67% → 0.96% (Fig. 4). On NLP tasks (20 News, Reuters, SST) it is comparable to the other methods. Vector scaling learns almost constant entries, so it reduces to temperature scaling: "network miscalibration is intrinsically low dimensional." Matrix scaling overfits when there are many classes. Binning methods can change class predictions and hurt accuracy.
5. **Practicalities (§5)**: temperature scaling is a 1-D convex problem that converges in about 10 conjugate-gradient iterations. It needs a **held-out validation set from the same distribution** (§4). They set $T=1$ during training and fit $T$ afterwards.

## Relevance to GroundOne
- This is the **default recipe** for GroundOne: train with cross-entropy on the restricted 2-way logits (A/B), then fit one temperature $T$ on a held-out calibration split, and report ECE, Brier, NLL and reliability diagrams before and after.
- Expect **overconfidence after LoRA fine-tuning**. Many epochs of cross-entropy on easy NLI-style pairs push NLL down through confidence, which is exactly the mechanism of §3. Track validation NLL separately from accuracy. Early stopping on NLL vs. on accuracy may pick different checkpoints.
- In the 2-class case, temperature scaling has one parameter and Platt has two (adds a bias). If base-rate shift between training and test is expected (RAG answers have a different supported/unsupported ratio than NLI training data), the bias matters. See [[Calibration]].
- Use equal-width M = 15 ECE to be comparable with Guo, **and** an equal-mass / adaptive ECE for robustness. See [[Expected Calibration Error]].
- Caveat: temperature scaling assumes the validation set matches deployment. Under domain shift (e.g. RAGTruth vs. NLI training data) the fitted $T$ may not transfer. Fit and test $T$ per domain.

## Links
- Concepts: [[Calibration]], [[Expected Calibration Error]], [[Selective Prediction]]
- Related sources: [[Naeini 2015 - Obtaining Well Calibrated Probabilities Using Bayesian Binning]], [[Kadavath 2022 - Language Models (Mostly) Know What They Know]], [[Tian 2023 - Just Ask for Calibration]], [[Geifman 2017 - Selective Classification for Deep Neural Networks]]
- Thesis context: [[System One Models]], [[Reinforcement Learning with Calibrated Decisions]], [[Groundedness Verification]]
