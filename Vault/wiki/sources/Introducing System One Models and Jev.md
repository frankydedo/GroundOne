---
type: source
author: Diogo Almeida
date: 2026-09-23
tags: [jev, typesafe-ai, system-one-models]
---
# Introducing System One Models & Jev (TypeSafe AI Blog)

**Raw file**: `raw/Introducing System One Models & Jev - TypeSafe AI Blog_ingested.md`

## Summary
The official launch announcement of Jev by Diogo Almeida, founder of TypeSafe AI. It introduces System One Models as a new class of frontier models designed to make fast, structured decisions for automation.

## Key Insights
- **Parallel Sampling**: Jev evaluates all questions in parallel, generating outputs in a single query rather than autoregressively token-by-token.
- **Reinforcement Learning for Calibrated Decisions (RLCD)**: The training algorithm used to ensure Jev's output probabilities are epistemically honest and reflect true confidence.
- **Naming**: "System One" is inspired by Kahneman's "Thinking, Fast and Slow". "Jev" is named after William Stanley Jevons (Jevons paradox - increased efficiency leads to increased demand).
- **Demos**: 
  - *Doom*: Real-time intelligence at 10 queries per second.
  - *Wikiracing*: Navigating Wikipedia links with high-cardinality choices (up to 255 choices).
- **No Type Errors**: Due to its architecture, schema matching is mathematically guaranteed.
