---
type: source
author: "Woosuk Kwon, Zhuohan Li, Siyuan Zhuang, Ying Sheng, Lianmin Zheng, Cody Hao Yu, Joseph E. Gonzalez, Hao Zhang, Ion Stoica"
date: 2023
venue: "SOSP 2023 (arXiv 2309.06180)"
url: "https://arxiv.org/abs/2309.06180"
tags: [source, paper, kv-cache, pagedattention, vllm, serving, prefix-sharing]
---
# Kwon 2023 – Efficient Memory Management for LLM Serving with PagedAttention (vLLM)

**Raw file**: `raw/Kwon 2023 - PagedAttention vLLM_ingested.pdf`

## Overview
Introduces **PagedAttention**, an attention kernel that works on a KV cache stored in **non-contiguous fixed-size blocks**, like virtual-memory pages in an operating system. On top of it the authors build **vLLM**, a serving engine with almost no KV-cache waste that can **share KV blocks within and across requests**. Throughput improves **2–4×** over FasterTransformer and Orca at the same latency, with larger gains for longer sequences, larger models and more complex decoding (abstract, §1).

## Key Insights
1. **The KV cache is the serving bottleneck (§1, Fig. 1).** For a 13B model on an A100-40GB, about 65% of memory holds weights and about 30% the KV cache. KV-cache management therefore determines the maximum batch size, and with it throughput.
2. **Size of the KV cache (§3).** For OPT-13B, one token takes $2\,(\text{K,V})\times 5120\,(\text{hidden})\times 40\,(\text{layers})\times 2\,(\text{bytes, FP16}) = 800$ KB. A 2048-token request can take **1.6 GB**.
3. **Waste in earlier systems (§3.1, Figs. 2–3).** Contiguous pre-allocation up to the maximum length causes reserved slots, internal fragmentation and external fragmentation. Only **20.4%–38.2%** of KV memory held actual token states. vLLM reaches **96.3%**.
4. **Paging (§4).**
   - A block table maps logical blocks to physical blocks, and blocks are allocated on demand.
   - Physical blocks carry **reference counts** and use **copy-on-write**, so parallel samples and beam candidates share prompt blocks (§4.4). Beam search saves up to 55% memory.
   - Default block size is **16 tokens** (§7.2).
   - When memory runs out, eviction is all-or-nothing per sequence, either swapped to CPU or recomputed.
5. **Shared prefix (§4.4, §6.4).** A provider can **pre-compute the KV cache of a common prefix** (system prompt, few-shot examples). New requests map their first logical blocks onto these cached physical blocks, and **prefill only runs on the new part**. On WMT16 translation with LLaMA-13B, throughput is **1.67× higher** than Orca (Oracle) with a 1-shot shared prefix and **3.58×** with a 5-shot prefix (Fig. 16).
6. **Background on the two phases (§2.2).** The prompt phase is parallel matrix–matrix work. The generation phase is sequential matrix–vector work, "memory-bound", and "responsible for most portion of the latency of a single request." Cost: the PagedAttention kernel itself is 20–26% slower than FasterTransformer's attention kernel because of block-table indirection (§7.1). End-to-end throughput is still much higher.

## Relevance to GroundOne
- GroundOne's inference pattern is **one shared prefix (context + answer) followed by K short suffixes**, one per sentence. That is exactly the **shared-prefix / copy-on-write** case vLLM optimises. A generative judge doing the same work would keep generating into separate sequences, each with its own growing KV cache.
- **Prefix caching across questions.** When several answers, or several regenerated answers, share the same retrieved context, the context KV blocks can be computed once and reused. This is the [[KV Cache]] reuse argument behind [[System One Models]] such as [[Jev]].
- On a single M4 with batch 1, fragmentation is irrelevant. The thesis uses MLX's prompt cache with **trimming** (roll back to the prefix after each suffix) instead of paging. See [[KV Cache]]. vLLM is still the right reference for how the same idea scales on servers.
- Memory per token is far smaller for Qwen2.5-0.5B/3B than for OPT-13B, thanks to GQA with 2 KV heads: about 12 KiB/token for 0.5B and 36 KiB/token for 3B in FP16, derived in [[KV Cache]]. So many cached contexts fit in 16 GB.

## Links
- Concepts: [[KV Cache]], [[Prefill and Decode]], [[Qwen2.5]]
- Related sources: [[Pope 2023 - Efficiently Scaling Transformer Inference]]
- Thesis context: [[System One Models]], [[Jev]], [[When System One Beats an LLM]]
