---
type: source
author: "Razvan Pascanu, Tomas Mikolov, Yoshua Bengio"
date: 2013
venue: "ICML 2013 (arXiv 1211.5063)"
url: "https://arxiv.org/abs/1211.5063"
tags: [source, paper, optimization, exploding-gradients, vanishing-gradients, gradient-clipping, rnn]
---
# Pascanu 2013 – On the Difficulty of Training Recurrent Neural Networks

**Raw file**: `raw/Pascanu 2013 - On the difficulty of training RNNs (gradient clipping)_ingested.pdf`

## Overview
The paper analyses the **exploding and vanishing gradient** problems of recurrent networks (Bengio et al. 1994) from three angles: analytical, dynamical-systems and geometric (§2). From that analysis it derives two remedies (§3):
- **gradient-norm clipping** against exploding gradients;
- a **soft-constraint regulariser** that keeps back-propagated error norms from vanishing.

Both are validated on pathological synthetic tasks, polyphonic music prediction and Penn Treebank language modelling (§4).

## Key Insights
1. **Mechanism (§2.1).** Gradients through time are products of Jacobians $\prod_k W_\text{rec}^\top \mathrm{diag}(\sigma'(x_k))$. If the largest singular value of $W_\text{rec}$ is below a bound (1/γ for a bounded σ′), long-term contributions vanish exponentially. A value above it is a necessary condition for them to explode.
2. **Geometry (§2.3, Fig. 6).** When gradients explode, curvature explodes along the same direction. The error surface then has **steep walls**. An ordinary SGD step that hits a wall is thrown far across the valley, undoing learning, while a bounded step returns to the smooth region beside the wall.
3. **Norm clipping (§3.2, Algorithm 1).** Compute $g = \partial E/\partial\theta$; if $\|g\| \ge$ threshold, rescale $g \leftarrow (\text{threshold}/\|g\|)\, g$. This keeps the direction and bounds the step. It is a variant of Mikolov's element-wise clipping with a better theoretical footing, since it always moves in a descent direction for the current mini-batch. The extra hyperparameter, the threshold, can be set from the average gradient norm over many updates; training was not very sensitive to it. Clipping can be seen as adapting the learning rate to the instantaneous gradient norm, so it reacts to abrupt spikes.
4. **Vanishing-gradient regulariser (§3.3).** A penalty that prefers Jacobians preserving the norm of the error signal in the relevant directions. It is a soft constraint, so it must be combined with clipping.
5. **Results (§4).** Clipping plus the regulariser solves synthetic long-memory tasks, with generalisation to longer sequences than seen in training. It reaches the state of the art on Penn Treebank at the time. Clipping improves both training and test error, which the authors read as clipping fixing an **optimisation** problem rather than acting as a regulariser.

## Relevance to GroundOne
- **The project's first diagnosis of the collapsed seed relies on this paper.** The notes say that `train.py` has no gradient clipping and no non-finite check. With LR 1e-4 and a class weight of 7.5 on "contradicted", one unlucky large update could push the LoRA weights into a region the optimiser does not leave. That is Pascanu's wall scenario (point 2), and norm clipping (Algorithm 1) is the textbook guard. MLX provides it as `mlx.optimizers.clip_grad_norm`.
- **Caveat: clipping may not be enough.** Pascanu's analysis concerns recurrent depth in time. GroundOne fine-tunes LoRA adapters on a pretrained transformer, the setting [[Mosbach 2021 - On the Stability of Fine-tuning BERT|Mosbach 2021]] studied. There, failed runs showed **vanishing** gradients and occurred despite global clipping. The observed symptom fits either story: loss stuck near ln 3 and a constant predictor from step 300. Only logged gradient norms can tell them apart. Clipping is cheap, though, and harmless when no spike occurs.
- **Threshold choice.** Following §3.2, the threshold should come from the gradient-norm statistics of a converged run (seed 1234 or 777), e.g. a high percentile of observed norms. That requires adding gradient-norm logging first.
- For the thesis (Ch. 5 / Ch. 7), the honest statement is: "The training loop uses no gradient clipping; one of three seeds collapsed. Clipping (Pascanu et al. 2013) and Adam bias correction with a longer warm-up (Mosbach et al. 2021) are the standard remedies; neither was tested within the experimental window." See [[Fine-tuning Instability and Seeds]].

## Links
- Concepts: [[Fine-tuning Instability and Seeds]]
- Related sources: [[Mosbach 2021 - On the Stability of Fine-tuning BERT]], [[Dodge 2020 - Fine-Tuning Pretrained LMs (weight init, data order, early stopping)]]
- Thesis context: [[GroundOne]], [[LoRA]]
