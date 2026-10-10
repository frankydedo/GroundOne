---
type: concept
tags: [fine-tuning, stability, random-seeds, optimization, gradient-clipping, adam, reproducibility, lora, groundone]
---
# Fine-tuning Instability and Seeds

## The phenomenon
Fine-tuning a pretrained model several times with **identical data and hyperparameters, changing only the random seed**, can give very different results. Most runs land near the same score; some **diverge** to a trivial predictor (majority class or a constant label). On small GLUE tasks the distribution of results is **bimodal** ([[Dodge 2020 - Fine-Tuning Pretrained LMs (weight init, data order, early stopping)|Dodge 2020]] Figs. 2–3).

**In plain words:** the same recipe can produce a good model or a useless one depending on the dice roll. A single run tells you little about the recipe, and best-of-N results overstate it.

## What causes it
| Source | Finding |
| --- | --- |
| [[Dodge 2020 - Fine-Tuning Pretrained LMs (weight init, data order, early stopping)\|Dodge 2020]] | 2,100 BERT runs. Weight initialisation of the new head and data order contribute **comparably** to the variance (Table 3). Some seeds are reliably better (ANOVA, Table 4). Diverged runs sit near the majority baseline. Divergence is visible after 20–30 % of training, so start many runs and stop the bad ones early (§5). Seeds alone gave about 7 points over published RTE/CoLA results. |
| [[Mosbach 2021 - On the Stability of Fine-tuning BERT\|Mosbach 2021]] | Failures are **not** catastrophic forgetting or small data per se. They are an early **optimisation** failure with **vanishing gradients** in the lower layers and a training loss stuck at the trivial value (−ln ½ for binary tasks). Adam **without bias correction** (the BERT default) plus a high LR is a key culprit; the default recipe already used gradient clipping. Fix: small LR, bias correction, warm-up, many more iterations. |
| [[Pascanu 2013 - On the difficulty of training RNNs (gradient clipping)\|Pascanu 2013]] | **Exploding** gradients create steep walls in the loss surface; one large step can throw the parameters far away. Fix: rescale the gradient when its norm exceeds a threshold (Algorithm 1), with the threshold set from typical gradient norms. It fixes optimisation and is not a regulariser. |

Exploding and vanishing gradients are different mechanisms with different remedies. **Logged gradient norms** tell them apart: a spike before the collapse points to exploding, persistently tiny lower-layer norms point to vanishing.

## Reporting practice
- Report **several seeds**, or at least disclose failed runs. Do not select seeds silently: best-of-N is optimistic (Dodge §3.1).
- Fix the seed policy in advance, and say which randomness each seed controls (initialisation, data order, dropout).
- Separate **seed variance** from **test-set variance**. A test-set bootstrap treats each trained model as fixed and does not include re-training noise ([[Statistical Significance and Bootstrap]]).
- Evaluate on dev frequently: it raises expected performance and catches divergence early (Dodge §3.1, §5).

## GroundOne
- **Recipe** (`configs/train_0.5b.yaml`, `training/train.py`):
  - LoRA r = 16 (alpha 32) on all linear layers of Qwen2.5-0.5B-Instruct (MLX 8-bit);
  - class-weighted cross-entropy over the A/B/C logits at the markers (weights: supported 0.38, contradicted 7.49, not mentioned 4.41);
  - `optim.AdamW(learning_rate=sched, weight_decay=0.0)`, peak LR 1e-4, linear warm-up over 3 % of 801 steps (≈ 24 steps), then cosine decay;
  - one epoch; dev evaluation every 150 steps, best checkpoint by balanced accuracy;
  - **no gradient clipping, no non-finite check, no gradient-norm logging**.
  - One `seed` controls both the LoRA initialisation (`mx.random.seed`) and the batch order.
  - **MLX `AdamW` defaults to `bias_correction=False`** and the code does not override it. This is the configuration Mosbach identify as unstable. *Verified in the code; not tested as a cause.*
- **What happened (D26):**

| Run | Seed | Outcome |
| --- | --- | --- |
| `g1-05b-b1` (run 1) | 1234 | Converged. T1 three-way 0.769, AUROC 0.905, T2 macro 70.1 |
| `g1-05b-s2` | 4321 | **Collapsed.** Loss rose after step 100 to ≈ 1.03–1.07, close to ln 3 ≈ 1.10 (no information over 3 classes). Dev macro recall 0.369 at step 150, 0.333 at step 300 with 100 % "supported", 0.444 at step 450. Stopped at ≈ step 470 and disclosed, not hidden. |
| `g1-05b-s3` (run 2) | 777 | Converged. T1 three-way 0.767, AUROC 0.907, T2 macro 71.5 |

- **Reading.**
  - When training converges, it converges to the same place. Aggregates differ by about 0.002 on T1; the differences sit in per-class recall (±0.04) and small slices (K ≥ 14 ±0.023, T3 AUROC ±0.025, single T2 datasets up to 10 points). That is Mosbach's "generalisation" component.
  - The risk is an **early collapse**, Dodge's diverged mode, with Mosbach's signature (loss stuck at the trivial value).
  - The 3B was trained with one seed only.
- **Diagnosis status.** The project notes attribute the collapse to the missing gradient clipping: one large update, amplified by the 7.5× class weight, at LR 1e-4. That is Pascanu's exploding scenario. Mosbach's evidence suggests an equally plausible vanishing / optimisation scenario, made worse by Adam without bias correction and a short warm-up. Without gradient-norm logs the two cannot be separated.
- **Fix options, each a declared recipe change to be checked on new seeds (not run, "possible, not planned"):**
  1. log the global and per-layer gradient norm every step (diagnostic, no recipe change);
  2. `bias_correction=True` in AdamW;
  3. a longer warm-up (≈ 10 % of steps);
  4. a lower peak LR (e.g. 5e-5, the code default);
  5. gradient-norm clipping (`mlx.optimizers.clip_grad_norm`), threshold from a high percentile of norms in a converged run;
  6. an automatic early-stop-and-restart rule when dev macro recall is still ≤ 0.40 at step 300 (Dodge §5).
- **For the thesis.** State that one of three 0.5B seeds collapsed, that the recipe has no clipping and uses Adam without bias correction, and that the collapse rate is not estimable from three runs. Present run 1 and run 2 side by side. Treat their spread as a floor for meaningful differences on T2 and T3.

## Links
- Sources: [[Dodge 2020 - Fine-Tuning Pretrained LMs (weight init, data order, early stopping)]], [[Mosbach 2021 - On the Stability of Fine-tuning BERT]], [[Pascanu 2013 - On the difficulty of training RNNs (gradient clipping)]], [[Berg-Kirkpatrick 2012 - An Empirical Investigation of Statistical Significance in NLP]], [[Hu 2022 - LoRA]]
- Concepts: [[Statistical Significance and Bootstrap]], [[LoRA]], [[Qwen2.5]], [[Calibration]]
- Thesis context: [[GroundOne]]
