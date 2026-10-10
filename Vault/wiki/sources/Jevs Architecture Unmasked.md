---
type: source
author: "Archer Hume"
date: 2026-09-22
tags: [source, article, architecture, jev]
---
# Jev’s Architecture Unmasked

**Raw file**: `raw/Jev’s Architecture Unmasked_ingested.md`

**Source URL**: https://archerhume.com/posts/jevs-architecture-unmasked/

This article by Archer Hume provides a deep dive into the inferred architecture of [[Jev]] based on 10,000 API probing calls. It debunks common misconceptions (e.g., that Jev is just a JSON classifier generating text under the hood) and provides evidence for how System One Models operate.

## Key Insights
1. **Direct Probability Readout**: Jev does not generate text token-by-token (autoregressive decoding). It ends the prefill phase with a readout head that maps hidden states directly to answer probabilities.
2. **Shared State and Isolated Questions**: The shared context (State) is processed once and stored in the **[[KV Cache]]**. Multiple question branches then run in parallel, attending to this shared state but isolated from one another. This changes computation cost from $QS$ to $S$ (for $Q$ questions and $S$ state tokens).
3. **Listwise Option Processing**: The model evaluates options together as a list before making a decision. Adding options changes the context, proving that choices interact and are not merely independently scored logits normalized post-hoc.
4. **Calibration via Scoring Rules**: TypeSafe uses proper scoring rules (like log loss or Brier loss) during its RLCD training to ensure the probability distribution is epistemically honest.
5. **Sparse Backbone**: Hume infers that Jev likely uses a sparse **[[Mixture of Experts]]** (MoE) transformer to maintain high capacity while remaining extremely fast and memory-efficient, bypassing the usual MoE overheads seen in token-by-token generation.
