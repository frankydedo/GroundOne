---
type: concept
tags: [architecture, machine-learning]
---
# Mixture of Experts (MoE)

**Mixture of Experts (MoE)** is a machine learning technique, specifically used in transformer architectures, that utilizes sparse capacity.

Instead of activating all parameters in a dense network for every input token, a router network directs each token to a small subset of specialized feed-forward networks (the "experts"). This allows the model to have a massively scaled total parameter count (high capacity/knowledge) while only using a fraction of compute per token (low active parameters).

In the context of [[System One Models]], [[Jevs Architecture Unmasked|Archer Hume infers]] (from black-box probing, not confirmed by TypeSafe) that [[Jev]] uses a sparse MoE backbone. The argument is that a model that only does prefill avoids the memory-bandwidth cost MoE pays during token-by-token decoding (see [[Prefill and Decode]]). None of the open System One implementations ([[SemIf]], [[Rizzo-Flow]], [[CLM]]) uses MoE.

## MoE on local hardware (ingest 2026-10-11)
- Unified-memory machines favour MoE models: only the active experts are read per token, so decode is faster than a dense model of the same total size, while capacity holds all experts. Examples: Llama 4 Scout 12.64 tok/s and gpt-oss-20B 53.9 tok/s on a Strix Halo Framework Desktop (runtime and quantisation not stated; [[PCWorld - Framework Desktop review]]); a 30B MoE at 4-bit takes 17.31 GB in MLX ([[Apple ML Research 2025 - Exploring LLMs with MLX and the neural accelerators in the M5 GPU]]).
- Epoch's consumer-GPU analysis counts only models whose full weights fit, which biases it against MoE ([[Epoch AI 2025 - Frontier AI performance becomes accessible on consumer hardware within a year]]). See [[Local Inference Hardware]].
