---
type: concept
tags: [training, reinforcement-learning, machine-learning]
---
# Reinforcement Learning for Calibrated Decisions (RLCD)

A training technique applied to AI models to ensure that the output probabilities reflect true confidence or certainty, rather than just statistical overconfidence.

## Problem with Traditional RLHF
Traditional RLHF can make models overconfident, assigning extreme probabilities (e.g., 99%) to answers even when the model is uncertain or incorrect.

## Calibrated Rewards
By using calibrated rewards during the reinforcement learning phase, models (such as [[Jev]]) are trained so that their probability distribution acts as a reliable certainty metric. 
- If a model outputs a 90% probability for an answer, it should truly be correct 90% of the time.
- This allows developers to use **confidence thresholds** (e.g., if confidence < 50%, route to a human operator; if > 90%, automate the action).

## Independent evidence on RLCD (ingest 2026-10-10)
- **The open RLCD recipe trails plain cross-entropy.** In a matched grid of heads and objectives, the RLCD recipe released with [[Laya]] is 2.5–3.0 points below cross-entropy, with a fourfold larger seed SD; its reward normalisation inflates the score-function term 3.6–15×, and a leave-one-out baseline recovers most of the gap. After temperature scaling, no objective is clearly better calibrated than cross-entropy ([[Deka 2026 - From Retrieval to Typed Decisions SBERT2S1 (arXiv 2610.02486)]]).
- **Jev's calibration is pooled, not local.** Over alignment benchmarks Jev's pooled ECE is 0.047 but its median per-benchmark ECE is 0.168, a base-rate mismatch ([[Guo 2026 - Just Ask Jev (arXiv 2609.29429)]]). The "90 % means right 90 % of the time" claim above holds only on the training-like mix; thresholds must be fitted per workload ([[Li 2026 - JEV-as-a-Judge (arXiv 2609.26550)]]).
- **The name is used loosely.** Cloudflare calls its secondary RL objective for Clef "Reinforcement Learning for Calibrated Decisions (RLCD)" too, with partial credit for adjacent ordinal choices and a reference penalty, on top of label-smoothed cross-entropy plus a Brier loss ([[Cloudflare 2026 - Clef model card]]). Most open decision models (Kev, Strands, uratori, pplx-decider) use cross-entropy plus temperature, not RL.
- **For GroundOne**: its class-weighted cross-entropy plus dev-fitted temperature and bias is in line with this evidence ([[Calibration]]).

