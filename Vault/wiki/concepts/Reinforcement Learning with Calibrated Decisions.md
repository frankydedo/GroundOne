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
