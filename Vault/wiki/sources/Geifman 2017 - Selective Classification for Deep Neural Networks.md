---
type: source
author: "Yonatan Geifman, Ran El-Yaniv"
date: 2017
venue: "NeurIPS 2017 (NIPS); arXiv 1705.08500"
url: "https://arxiv.org/abs/1705.08500"
tags: [source, paper, selective-prediction, abstention, risk-coverage, reject-option]
---
# Geifman 2017 – Selective Classification for Deep Neural Networks

**Raw file**: `raw/Geifman 2017 - Selective Classification for Deep Neural Networks_ingested.pdf`

## Overview
Brings **selective classification**, also called the reject option, to deep networks. A classifier is paired with a selection function that can say "don't know". The authors give an algorithm, **SGR (Selection with Guaranteed Risk)**. Given a trained network, a confidence score and a target risk $r^*$, it picks a threshold that guarantees the selective error stays below $r^*$ **with probability $1-\delta$**, while keeping coverage as high as possible (abstract, §3).

## Key Insights
1. **Formalism (§2).**
   - A selective classifier $(f,g)$ outputs $f(x)$ if $g(x)=1$, otherwise abstains.
   - **Coverage** $\phi(f,g)=\mathbb E[g(x)]$.
   - **Selective risk** $R(f,g)=\mathbb E[\ell(f(x),y)\,g(x)]/\phi(f,g)$ (Eq. 1).
   - Trading risk against coverage gives the **risk–coverage curve**, which describes the whole performance profile.
2. **Threshold rule (Eq. 3).** $g_\theta(x)=\mathbb 1[\kappa_f(x)\ge\theta]$ for a confidence-rate function $\kappa_f$. Only the **ranking** of $\kappa$ matters, not its absolute values. An ideal $\kappa$ is monotone in the true loss (§4).
3. **SGR (Algorithm 1, Lemma 3.1, Theorem 3.2).** It sorts validation points by $\kappa$ and binary-searches $\theta$. At each step it computes a numerical binomial tail bound $B^*$ on the true risk, at confidence $\delta/\lceil\log_2 m\rceil$ (union bound), and keeps the threshold whose bound is below $r^*$.
4. **Confidence functions (§4–5).** **Softmax response (SR)**, $\max_j f(x\mid j)$, vs. MC-dropout variance. On CIFAR they are nearly identical. On ImageNet SR is clearly better: at 60% coverage, top-1 error is 10% for SR vs. >20% for MC-dropout (Fig. 2).
5. **Results (Tables 1–2, δ = 0.001).**
   - CIFAR-10 (VGG-16, 93.5% accuracy): a guaranteed **1% error at about 78% coverage**; test risk was always below the bound.
   - CIFAR-100: 2% risk at about 21% coverage, 10% at about 60%.
   - ImageNet: **2% top-5 error guaranteed with probability 99.9% at almost 60% coverage** (abstract).
6. **The scalar AURC is not defined in this paper.** The area under the risk–coverage curve (AURC) was introduced in later work by the same group. Here the curve itself and the SGR guarantees are the contribution.

## Relevance to GroundOne
- GroundOne should be evaluated as a **selective predictor**, not only as a classifier. Each sentence verdict has a confidence, so the system can auto-accept or flag confident sentences and **escalate uncertain ones** to an LLM judge or a human, as in the hybrid of [[When System One Beats an LLM]]. Report risk–coverage curves and AURC. See [[Selective Prediction]].
- **SGR gives a deployable guarantee.** An example statement: "on held-out RAG data, among sentences marked *supported* above θ, the unsupported rate is ≤ 5% with probability 99.9%, at X% coverage." This is stronger and easier to explain than ECE alone. It needs a held-out set that matches deployment (independent of the one used to fit temperature, ideally).
- SR is the natural $\kappa$ for GroundOne: $\max(p_A,p_B)$ after the restricted 2-way softmax. Temperature scaling does **not** change the ranking, so it leaves the risk–coverage curve unchanged. Calibration (ECE) and selective performance (AURC) therefore measure different things and should both be reported.
- The CIFAR-100 rows show the limit: when the base classifier is weak, low risk is only reachable at low coverage. The same is likely for a 0.5B verifier on hard, subtle unsupported claims.

## Links
- Concepts: [[Selective Prediction]], [[Calibration]], [[Expected Calibration Error]]
- Related sources: [[Guo 2017 - On Calibration of Modern Neural Networks]], [[Tian 2023 - Just Ask for Calibration]]
- Thesis context: [[System One Models]], [[When System One Beats an LLM]], [[Groundedness Verification]], [[Reinforcement Learning with Calibrated Decisions]]
