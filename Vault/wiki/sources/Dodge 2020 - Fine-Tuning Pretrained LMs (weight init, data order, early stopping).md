---
type: source
author: "Jesse Dodge, Gabriel Ilharco, Roy Schwartz, Ali Farhadi, Hannaneh Hajishirzi, Noah A. Smith"
date: 2020
venue: "arXiv preprint 2002.06305"
url: "https://arxiv.org/abs/2002.06305"
tags: [source, paper, fine-tuning, random-seeds, variance, early-stopping, reproducibility, bert]
---
# Dodge 2020 – Fine-Tuning Pretrained Language Models: Weight Initializations, Data Orders, and Early Stopping

**Raw file**: `raw/Dodge 2020 - Fine-Tuning Pretrained LMs (weight init, data order, early stopping)_ingested.pdf`

## Overview
BERT-large is fine-tuned **2,100 times** on four GLUE tasks (MRPC, RTE, CoLA, SST-2), with fixed hyperparameters and **only the random seeds changed** (§2). Two seeds are crossed: one controls the **weight initialisation (WI)** of the new classification layer (2,048 parameters), the other the **training data order (DO)**. That gives 25 × 25 = 625 runs for each small task and 15 × 15 = 225 for SST. The paper measures how much seeds alone move results, which source matters more, and how to stop bad runs early. All training curves are released.

## Key Insights
1. **Seeds alone move results a lot (§3, Table 1).** The best of many seeds beats previously published BERT results with the same setup by about 7 points absolute on RTE and CoLA. On MRPC it beats newer models (XLNet, RoBERTa, ALBERT). Comparisons based on single reported numbers can therefore mislead.
2. **Expected validation performance (§3.1, Fig. 1).** The expected best-of-x score keeps rising with the number of trials x, even at the largest budgets. Small datasets show high variance at small budgets. Evaluating more often during training (ten times per epoch rather than once per epoch or at the end) raises expected performance and lowers variance, so the paper recommends frequent evaluation.
3. **WI and DO contribute comparably (§4.1, Table 3).** The expected standard deviation from varying either seed alone is close to the overall one.
4. **Some seeds are reliably better (§4.2, Fig. 3, Table 4).** The best and worst WI and DO seeds differ significantly (ANOVA p < 0.05). The distributions on MRPC and RTE are **bimodal**: one mode is a **diverged run** near the majority-class baseline. One WI seed is good across all four tasks (§4.3).
5. **Divergence is visible early (§5, Figs. 4–5).** Validation scores early in training are strongly rank-correlated with final scores; on the small tasks this already holds part-way through the first epoch. A simple rule helps: start t trials, evaluate after a fraction f of training, and continue the best p. It works best when stopping after 20–30 % of training and fully training about half of the budget's worth of runs (Fig. 6).

## Relevance to GroundOne
- **GroundOne's collapsed seed is a textbook Dodge divergence.** Run `g1-05b-s2` (seed 4321) of the 0.5B fell to a constant "supported" predictor: dev macro recall 0.333 at step 300, with training loss stuck near ln 3 ≈ 1.10. It was stopped at about step 470. Seeds 1234 and 777 converged to the same aggregates (T1 three-way 0.769 vs 0.767, AUROC 0.905 vs 0.907). This is Dodge's bimodal picture: when a run converges it lands in the same place, but some seeds diverge.
- **One seed controls both sources.** In `train.py` the single `seed` sets the LoRA initialisation (`mx.random.seed`) and the batch order (`make_batches`). So the collapse cannot be attributed to WI or DO without crossing them as Dodge do. Unlike BERT's new classification head, GroundOne has no randomly initialised head: the readout uses the pretrained LM head. Only the LoRA matrices are initialised at random.
- **Early detection already works.** Dev evaluation every 150 optimiser steps exposed the collapse by step 150–300 (dev predicted shares 0.22 / 0.00 / 0.78, then 1.00 / 0 / 0). This matches Dodge §5: divergence is visible within the first quarter of training.
- **Reporting.** Picking the converged seeds and silently dropping the diverged one would be the optimistic "best of x" Dodge warn about. The thesis discloses the stopped run (D26). With two converged runs out of three started, the collapse rate cannot be estimated: 1/3 has a very wide interval.
- **Seed variance vs test-set variance.** Dodge show seed variance comparable to or larger than many reported gains. GroundOne's run-1 vs run-2 spread (about 1.5 T2 macro points, 0.025 T3 AUROC, up to 10 points on single T2 datasets) is exactly the variance that a test-set bootstrap does not include. See [[Statistical Significance and Bootstrap]].

## Links
- Concepts: [[Fine-tuning Instability and Seeds]], [[Statistical Significance and Bootstrap]], [[LoRA]]
- Related sources: [[Mosbach 2021 - On the Stability of Fine-tuning BERT]] (cause of the failed runs), [[Pascanu 2013 - On the difficulty of training RNNs (gradient clipping)]], [[Berg-Kirkpatrick 2012 - An Empirical Investigation of Statistical Significance in NLP]], [[Hu 2022 - LoRA]]
- Thesis context: [[GroundOne]], [[Qwen2.5]]
