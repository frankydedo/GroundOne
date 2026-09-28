---
type: concept
tags: [architecture, transformer]
---
# KV Cache (Key-Value Cache)

The **KV Cache** (Key-Value Cache) is an optimization technique used in Transformer models during inference.

As a transformer processes tokens, it computes Key and Value vectors for the attention mechanism. Instead of recomputing these vectors for past tokens at every step, the model stores them in a cache. 

In [[System One Models]] like [[Jev]], the KV Cache enables extreme efficiency: a long, shared "State" is processed once and stored in the cache. Subsequent parallel questions can then attend to this cached state without having to recompute the representations, drastically reducing computational overhead.
