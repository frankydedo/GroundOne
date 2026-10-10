---
type: source
author: "Marius Mosbach, Maksym Andriushchenko, Dietrich Klakow"
date: 2021
venue: "ICLR 2021 (arXiv 2006.04884)"
url: "https://arxiv.org/abs/2006.04884"
tags: [source, paper, fine-tuning, stability, optimization, vanishing-gradients, adam, bias-correction, bert]
---
# Mosbach 2021 – On the Stability of Fine-tuning BERT: Misconceptions, Explanations, and Strong Baselines

**Raw file**: `raw/Mosbach 2021 - On the Stability of Fine-tuning BERT_ingested.pdf`

## Overview
Fine-tuning BERT, RoBERTa or ALBERT many times with different seeds gives a large spread of results, including **failed runs** that end at or below the majority-class baseline (the definition is taken from Dodge 2020; §3). The paper tests the two usual explanations, catastrophic forgetting and small datasets, and rejects both as causes (§4). It shows that failures are an **optimisation problem with vanishing gradients early in training**, and that the remaining spread comes from generalisation (§5). It proposes a simple, more stable recipe (§6). The datasets are CoLA, MRPC, RTE and QNLI.

## Key Insights
1. **Not catastrophic forgetting (§4.1).** Failed runs do lose masked-LM ability, but only in the top ~10 of 24 layers, and successful runs do too, to a lesser degree (Fig. 2a–b). More telling, failed runs never learn the new task: training loss stays at the trivial value ≈ −ln(1/2) for binary tasks, and dev accuracy at the majority level (Fig. 2c).
2. **Not dataset size per se (§4.2).** On 1,000-example subsets, 3 epochs give many failed runs. Training for as many *iterations* as on the full set restores the original variance (Fig. 3). What matters is the number of updates and hence the effective learning-rate schedule.
3. **Failed runs have vanishing gradients (§5, Fig. 4).** In a failed run, the gradient norms of the bottom layers vanish and never recover. In a successful run, gradients are small at first and then grow, ending almost two orders of magnitude larger. Loss-surface plots show failed runs stuck in a "bad valley" separated by a barrier from the good minimum (Fig. 7).
4. **Adam without bias correction is a culprit (§5).** The original BERT recipe uses Adam **without bias correction**. Bias correction scales the step size by $\sqrt{1-\beta_2^t}/(1-\beta_1^t)$, which is well below 1 in the first iterations: an implicit warm-up (Eq. 1, Fig. 6). Turning it on makes BERT and ALBERT markedly more stable and tolerant of larger learning rates (Fig. 5). Note that BERT's default recipe *already* used global gradient clipping, and RoBERTa's used none (§3), so clipping alone did not prevent failures.
5. **Generalisation explains the remaining variance (§5).** Runs with near-identical training loss differ noticeably on dev. Training to near-zero loss (10⁻⁵) does not hurt dev accuracy (Fig. 8).
6. **Recipe (§6).** Use a small learning rate with bias correction and train much longer (20 epochs on small datasets, 10 % linear warm-up, then linear decay). Across 25 seeds this gives a significantly smaller standard deviation (Levene's test p < 0.001) and higher mean performance than the default recipe and Mixout (Table 1, Fig. 1).

## Relevance to GroundOne
- **Same signature as the collapsed GroundOne seed.** In `g1-05b-s2` (seed 4321) the class-weighted training loss rose after step 100 to about 1.03–1.07 and stayed there. That is close to ln 3 ≈ 1.10, the loss of a model with no information over three classes, the three-class analogue of Mosbach's −ln(1/2). By step 300 the model predicted "supported" for every dev sentence.
- **GroundOne's optimiser is in the configuration Mosbach flag.** `train.py` builds `optim.AdamW(learning_rate=sched, weight_decay=0.0)`, and MLX's `AdamW` defaults to `bias_correction=False`. The schedule has a short linear warm-up: 3 % of 801 steps, so the peak LR of 1e-4 is reached around step 24. This combination (no bias correction, short warm-up, LR at the high end for LoRA on a 0.5B) is the one Mosbach identify as prone to early optimisation failure. *Verified from the code and the MLX signature; not yet tested as a cause.*
- **The project notes blame the missing gradient clipping.** Mosbach's evidence points to a different mechanism (vanishing, not exploding gradients), and BERT failed despite clipping. The two hypotheses can be told apart only by logging per-step gradient norms, which `train_log.jsonl` does not record (it records loss and LR). See [[Fine-tuning Instability and Seeds]] and [[Pascanu 2013 - On the difficulty of training RNNs (gradient clipping)]].
- **Candidate fixes, each a declared recipe change to test on new seeds:**
  1. `bias_correction=True`;
  2. a longer warm-up (e.g. 10 %);
  3. a lower peak LR;
  4. gradient-norm clipping (`mlx.optimizers.clip_grad_norm`);
  5. logging gradient norms to diagnose the cause.

  Mosbach's results favour (1)–(3) for a collapse to a constant predictor. The heavy class weights (contradicted 7.49, not mentioned 4.41, supported 0.38) make individual steps larger, which fits both hypotheses.
- **Positive note.** Mosbach's generalisation finding (same loss, different dev score) matches GroundOne's two converged runs: aggregates agree, while per-class recall differs by about ±0.04.

## Links
- Concepts: [[Fine-tuning Instability and Seeds]], [[LoRA]], [[Statistical Significance and Bootstrap]]
- Related sources: [[Dodge 2020 - Fine-Tuning Pretrained LMs (weight init, data order, early stopping)]], [[Pascanu 2013 - On the difficulty of training RNNs (gradient clipping)]], [[Hu 2022 - LoRA]]
- Thesis context: [[GroundOne]], [[Qwen2.5]]
