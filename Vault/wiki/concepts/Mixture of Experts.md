---
type: concept
tags: [architecture, machine-learning]
---
# Mixture of Experts (MoE)

**Mixture of Experts (MoE)** is a machine learning technique, specifically used in transformer architectures, that utilizes sparse capacity.

Instead of activating all parameters in a dense network for every input token, a router network directs each token to a small subset of specialized feed-forward networks (the "experts"). This allows the model to have a massively scaled total parameter count (high capacity/knowledge) while only using a fraction of compute per token (low active parameters).

In the context of [[System One Models]] like [[Jev]], MoE is highly advantageous because it avoids the typical MoE memory bandwidth bottlenecks that occur during autoregressive token-by-token decoding.
