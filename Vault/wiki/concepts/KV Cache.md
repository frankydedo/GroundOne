---
type: concept
tags: [architecture, transformer, inference, kv-cache, memory]
---
# KV Cache (Key-Value Cache)

The **KV Cache** (Key-Value Cache) is an optimization technique used in Transformer models during inference.

As a transformer processes tokens, it computes Key and Value vectors for the attention mechanism. Instead of recomputing these vectors for past tokens at every step, the model stores them in a cache. Only the new token's $k,v$ are computed at each decode step; all earlier ones are read from the cache ([[Kwon 2023 - PagedAttention vLLM|Kwon 2023]] §2.2). Note that a token's cached K/V depend on **all tokens before it**, so a cache entry is valid only for exactly that prefix.

In [[System One Models]] like [[Jev]], the KV Cache enables extreme efficiency: a long, shared "State" is processed once and stored in the cache. Subsequent parallel questions can then attend to this cached state without having to recompute the representations, drastically reducing computational overhead.

## Memory cost
Per token, the cache stores one K and one V vector per layer per **KV head**:
$$\text{bytes/token} = 2\,(\text{K,V}) \times n_{layers} \times n_{kv\_heads} \times d_{head} \times \text{bytes per element}$$
- **OPT-13B** (multi-head, FP16): $2\times40\times5120\times2$ = **800 KB/token**, so a 2048-token request uses **1.6 GB** (Kwon §3).
- **PaLM 540B** (multi-head variant, batch 512, context 2048): the KV cache totals **3 TB, 3× the model weights** ([[Pope 2023 - Efficiently Scaling Transformer Inference|Pope 2023]] §2.1).
- **Grouped-query / multi-query attention** shares K/V heads across query heads and shrinks the cache by $n_{heads}/n_{kv\_heads}$. MQA let PaLM 540B fit 32–64× longer contexts (Pope §3.3, Table 1).
- **[[Qwen2.5]] 0.5B and 3B use GQA with only 2 KV heads.** Derived from the local `config.json` and report Table 1, in FP16:
  - 0.5B: $2\times24\times2\times64\times2$ = **12 KiB/token**, so a 637-token context + answer ≈ 7.5 MiB;
  - 3B: $2\times36\times2\times128\times2$ = **36 KiB/token**, so 637 tokens ≈ 22 MiB.

  Caching hundreds of RAG contexts fits easily in 16 GB unified memory. Weights, not the cache, dominate memory for GroundOne.
- In serving, the cache (not compute) limits batch size. For a 13B model on an A100-40GB, about 30% of memory is KV cache vs. about 65% weights (Kwon Fig. 1). At large batch and long context, **reading the KV cache dominates decode time** (Pope §2).

## Prefix caching and sharing across questions
- **Within one request.** The [[System One Models|System One]] pattern: prefill the shared prefix (context + answer) once, then run $K$ short suffixes (one per sentence or question) that attend to it. The cost goes from about $K\cdot S$ to about $S$ ([[Jevs Architecture Unmasked]]). See [[Prefill and Decode]] for the cost model.
- **Across requests / questions.** If several answers or questions share the same retrieved context or system prompt, the prefix cache can be computed once and **reused**. vLLM supports this as "shared prefix". The provider pre-computes the prefix's KV blocks, and new requests map onto them and only prefill the new tokens. This gave **1.67×** (1-shot prefix) to **3.58×** (5-shot prefix) higher throughput on WMT16 with LLaMA-13B (Kwon §4.4, §6.4, Fig. 16).
- **Requirements for reuse:** an *identical token prefix*, including the chat template and default system prompt. Qwen's template inserts one if none is given ([[Qwen2.5]]). The same positions are also needed, because RoPE is baked into cached keys.

## PagedAttention (vLLM)
[[Kwon 2023 - PagedAttention vLLM|PagedAttention]] stores each sequence's KV cache in **fixed-size blocks** (default 16 tokens), mapped through a block table like OS virtual-memory pages:
- no pre-allocation up to max length, so almost no fragmentation. Earlier systems used only 20.4–38.2% of KV memory for real token states (Fig. 2);
- **reference-counted, copy-on-write blocks**, so parallel samples, beam candidates and requests with a common prefix **share** physical blocks (beam search saves up to 55% memory);
- costs 20–26% higher attention-kernel latency than a contiguous kernel (§7.1), but gives 2–4× end-to-end throughput.

This is a server-side (multi-request, batched) technique. On a single-user M4 with batch 1, fragmentation is not the problem. The *sharing* idea is what GroundOne reuses.

## MLX prompt cache and trimming (how GroundOne does it on-device)
From `mlx_lm/models/cache.py` (mlx-lm 0.31.3, thesis venv):
- `make_prompt_cache(model)` builds one `KVCache` per layer (or a `RotatingKVCache` if `max_kv_size` is set).
- `KVCache.trim(n)` just **moves the offset back by n tokens**. No recomputation and no copy. Later writes overwrite the trimmed slots. `can_trim_prompt_cache` / `trim_prompt_cache(cache, n)` apply this to all layers. A `RotatingKVCache` is only trimmable while it has not wrapped (`offset < max_size`).
- **GroundOne loop (design a):** prefill context + answer once → for each sentence: feed the suffix, read the A/B logits at the last position, then `trim_prompt_cache(cache, len(suffix))` to return to the shared prefix. Cost per sentence ≈ one short forward pass ($t_{suffix}$). *Superseded as the default on 2026-10-10 (decision D22): design (a) is now the fallback, used by the untrained baseline B1 and the Jev-compatible route; the readout has three letters A/B/C (supported / contradicted / not mentioned), not two. See the section on design (b) below.*
- `save_prompt_cache` / `load_prompt_cache` persist a cache to `.safetensors`. This allows **cross-question reuse** of a context's prefix (e.g. when the same retrieved passage is verified against several answers).
- `LRUPromptCache` keeps a trie of cached prompts. It returns the cache whose token prefix best matches a new prompt. If a longer cached prompt shares a prefix, it deep-copies and **trims** it to the common prefix, then only the remaining tokens are prefilled. This is a single-process analogue of vLLM's shared-prefix reuse.
- Caveat: trimming relies on K/V for positions ≤ prefix being unaffected by later tokens, which holds for causal attention. Copy (`copy.deepcopy`) before trimming if the original cache must be kept, e.g. for concurrent branches.

## Design (b): one pass, no per-sentence cache branching (2026-10-10)
GroundOne's default readout writes a marker " Verdict:" after each scored sentence and runs **one forward pass over context + marked answer**; the output head is applied only at the K marker positions. The KV cache is filled once by this single prefill and is never trimmed or replicated, so the cache-sharing tricks above (trim, branch, replicate K times) are not needed. Causal attention guarantees that the verdict at sentence i sees the document and sentences 1..i, but not later sentences. The cost is one compute-bound prefill ([[Prefill and Decode]]); design (b) is 1.4–1.5× faster than design (a) at K ≥ 14.

## KV cache beyond one device
- **Splitwise** moves the KV cache between machines: the prompt machine computes it and sends it layer by layer over InfiniBand to the token machine, overlapping the transfer with prefill (≈8 ms non-overlapped, ≈0.8% of E2E latency) ([[Patel 2024 - Splitwise (prefill vs decode phases)|Patel 2024]] §IV-C). During decode every generated token reads the KV cache of its whole context, which adds to the memory-bound character of the phase (§III-E).
- **Flash offloading.** LLM in a flash keeps attention weights in DRAM and streams sparse FFN weights from flash; the authors note the technique generalises to other transferred data such as activations or the KV cache ([[Alizadeh 2024 - LLM in a flash|Alizadeh 2024]] §3, footnote 1). For GroundOne the cache is small (12–36 KiB/token, see above) and stays in unified memory.
- **On-device GQA.** Apple's AFM-on-device uses grouped-query attention with 8 KV heads explicitly "to reduce the KV-cache memory footprint" ([[Gunter 2024 - Apple Intelligence Foundation Language Models|Gunter 2024]] §2); Qwen2.5 0.5B/3B go further with 2 KV heads.

## Links
- [[Prefill and Decode]], [[System One Models]], [[Jev]], [[Jevs Architecture Unmasked]], [[When System One Beats an LLM]], [[Qwen2.5]], [[GroundOne]]
- Sources: [[Kwon 2023 - PagedAttention vLLM]], [[Pope 2023 - Efficiently Scaling Transformer Inference]], [[Qwen Team 2024 - Qwen2.5 Technical Report]], [[Patel 2024 - Splitwise (prefill vs decode phases)]], [[Alizadeh 2024 - LLM in a flash]], [[Gunter 2024 - Apple Intelligence Foundation Language Models]], [[MLX README (ml-explore)]]
- Also: [[On-Device Inference]], [[Apple Silicon and MLX]]
