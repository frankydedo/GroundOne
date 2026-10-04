---
type: source
author: "Reiner Pope, Sholto Douglas, Aakanksha Chowdhery, Jacob Devlin, James Bradbury, Anselm Levskaya, Jonathan Heek, Kefan Xiao, Shivani Agrawal, Jeff Dean (Google)"
date: 2023
venue: "MLSys 2023 (arXiv 2211.05102)"
url: "https://arxiv.org/abs/2211.05102"
tags: [source, paper, inference, prefill, decode, kv-cache, multiquery-attention, latency]
---
# Pope 2023 – Efficiently Scaling Transformer Inference

**Raw file**: `raw/Pope 2023 - Efficiently Scaling Transformer Inference_ingested.pdf`

## Overview
A Google paper on serving very large decoder models (PaLM 8B/62B/540B on TPU v4). It builds a simple **analytical cost model** (memory time, compute time, communication time) and uses it to choose multi-dimensional partitioning layouts. Results: **29 ms/token decode** for PaLM 540B with int8 weights, and **76% MFU** on large-batch prefill, at 2048-token context (abstract). For this wiki the value is less the TPU partitioning and more the clear **separation of prefill and decode** and the memory analysis of the KV cache.

## Key Insights
1. **Prefill vs. decode are different regimes (§2, §2.2).** Latency = time to process the input tokens ("prefill") + time to generate output tokens autoregressively ("decode"). Prefill runs over all $B\times L_{input}$ tokens **in parallel in one forward pass**. Decode is a **sequential loop of $L_{gen}$ forward passes**, one token each, so "the two phases have different performance characteristics."
2. **Cost model (§2).**
   - Compute: about **2N matmul FLOPs per token** for an N-parameter decoder, with attention FLOPs relatively small.
   - Memory: weights and KV cache must be loaded from HBM **once per forward pass**. At small batch and short context, **weight loading dominates**. At large batch and long context (e.g. 2048+ tokens, batch 512+), **KV cache loading dominates**.
   - Decode at low batch size is therefore bound by memory bandwidth: the cores sit idle while weights stream in.
3. **The KV cache can be bigger than the model (§2.1).** For a 500B+ multi-head model at batch 512 and context 2048, the KV cache is **3 TB, three times the parameters**.
4. **Multiquery attention (§3.3, §4.2, Table 1).** One shared K/V head shrinks the KV cache by a factor of $n_{heads}$. With the right partitioning (shard the KV cache over batch), PaLM 540B fits **32–64× longer contexts** (e.g. 43,000 vs. 1,320 tokens at batch 128). Prefill latency is similar for MQA and MHA because prefill attention is compute-limited. Decode is faster with MQA, especially at long context.
5. **Concrete numbers (Table 2, PaLM 540B, 64 chips).** Low-latency **prefill of 2048 tokens: 0.29 s at 43% MFU** (batch 1, int8). Low-latency **decode of 64 tokens: 1.82 s at 14% MFU** (batch 64, int8). Generating only 64 tokens takes about 6× longer than reading 2048 tokens, and uses the hardware 3× less efficiently. The paper's chatbot example: 64 user tokens + 1920 cached history + 64 generated tokens = **1.9 s total**, nearly all of it decode (§1).
6. **int8 weights help decode latency (§4.4).** 28.5 ms/token vs. 36.9 ms/token for bf16 at batch 64, because low-batch decode is dominated by weight-loading time. At large batch the effect is neutral.

## Relevance to GroundOne
- This is the **main citation** for the argument that a System One verifier saves **decode, not prefill**. Prefill of context + answer is unavoidable for both a generative judge and GroundOne. What GroundOne removes is the sequential, memory-bound loop of $n$ generated tokens per verdict, and decode is the least efficient phase per token (Table 2: 14% vs. 43% MFU). See [[Prefill and Decode]].
- The thesis's own preliminary M4 numbers show the same asymmetry at small scale. 0.5B prefill costs about 0.33–0.36 ms per token at 242–637 tokens, while one decode step costs about 7 ms, so **one generated token costs about as much as prefilling about 20 tokens**. 3B: about 2.1–2.2 ms/token prefill vs. 37–42 ms/token decode. Same order of magnitude as Pope's ratio, on very different hardware.
- §4.4 explains why **8-bit weights** make sense on the M4: batch-1 decode is weight-bandwidth-bound, so smaller weights mean faster tokens. Scoring suffixes is also a small-token-count forward pass and is therefore bound by weight loading too.
- §3.3 / Table 1 explain why Qwen2.5's **GQA (2 KV heads)** makes caching a shared prefix cheap. See [[KV Cache]] and [[Qwen2.5]].

## Links
- Concepts: [[Prefill and Decode]], [[KV Cache]], [[Qwen2.5]]
- Related sources: [[Kwon 2023 - PagedAttention vLLM]]
- Thesis context: [[System One Models]], [[When System One Beats an LLM]], [[Jev]]
