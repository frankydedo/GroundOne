---
type: source
author: "Pratyush Patel, Esha Choukse, Chaojie Zhang, Aashaka Shah, Íñigo Goiri, Saeed Maleki, Ricardo Bianchini"
date: 2024
venue: "ISCA 2024 (arXiv 2311.18677)"
url: "https://arxiv.org/abs/2311.18677"
tags: [source, paper, inference, prefill, decode, power, energy, gpu, serving]
---
# Patel 2024 – Splitwise: Efficient Generative LLM Inference Using Phase Splitting

**Raw file**: `raw/Patel 2024 - Splitwise (prefill vs decode phases)_ingested.pdf`

## Overview
Splitwise (University of Washington and Microsoft) characterises generative LLM inference on production traces from two Azure services (coding and conversation) and shows that each request has two phases with different resource profiles: a **compute-intensive prompt phase** (prefill) and a **memory-intensive token-generation phase** (decode). It then proposes running the two phases on **separate machines**, transferring the KV cache over InfiniBand. Splitwise clusters reach **1.4× higher throughput at 20% lower cost**, or **2.35× more throughput under the same power and cost budget** (abstract). The models are Llama2-70B and BLOOM-176B on vLLM, 8× H100 or A100 per machine (§III, Table III).

## Key Insights
The paper's value for this wiki is its characterisation (§III), stated as seven "insights":
1. **Two phases** (§II-B, Fig. 1). The prompt phase processes all input tokens in parallel in one iteration and fills the [[KV Cache]]. Each later token uses only the last token plus the cache, which makes decode "more memory bandwidth and capacity intensive than the computationally heavy prompt phase".
2. **Decode dominates end-to-end time** (Insight III, §III-C). Most of the E2E time is spent in the token phase, even for coding requests with long prompts (median 1,500 tokens) and few outputs (median 13 tokens). For BLOOM-176B, **a 1,500-token prompt phase takes as long as generating 6 output tokens**.
3. **TTFT grows almost linearly with prompt size** because the prompt phase is compute-bound with high GPU utilisation (Fig. 5a). TBT barely changes with batch size: 2× at batch 64 (Fig. 5b).
4. **Batching** (Insights II, IV, V). Prompt-phase throughput drops beyond about 2,048 batched tokens; decode throughput keeps rising with batch size until memory runs out. "Batching during the prompt phase is compute-bound, whereas the token phase is limited by memory capacity."
5. **Power** (Insight VI, §III-F, Fig. 8–9). Prompt-phase **power draw rises with batch size** and approaches TDP; **token-phase power draw stays flat** because decode is memory-bound. Power-capping H100s from 700 W to 350 W barely slows decode but substantially slows prefill.
6. **Hardware** (Insight VII, Table IV). Decode does not need the newest GPUs: on Llama-70B, A100 versus H100 shows the same energy per request for conversation (1.37 Wh) and lower cost.
7. **Phase splitting**. Layer-wise KV-cache transfer overlaps with prefill; the non-overlapped transfer is about 8 ms and adds about 0.8% to E2E latency (§IV-C, §VI).

## Relevance to GroundOne
- **Theoretical support for the energy result.** GroundOne reads all K verdicts from a single prefill, while generative judges spend most of their time decoding. Splitwise shows that prefill draws more power than decode (Fig. 8). This explains why GroundOne's energy advantage over a terse judge (1.3–1.6×) is smaller than its speed advantage (≈2×): its single long prefill runs at about 16 W on the M4, against 11–14 W for the judges' memory-bound decoding. See [[Energy of LLM Inference]] and [[Prefill and Decode]].
- **Prefill vs decode cost ratio.** Splitwise's "1,500 prompt tokens ≈ 6 output tokens" (BLOOM-176B, H100) has the same shape as the thesis' own M4 measurement, where one decode step costs about as much as prefilling 14–21 tokens. The ratios differ (≈250 vs 14–21 prompt tokens per generated token) and should not be compared directly, but both say that one generated token costs as much as many prompt tokens.
- **Caveat on transfer.** The characterisation is for 70B–176B models on H100/A100 servers with batching; on a single-user M4 at batch 1 the qualitative split (compute-bound prefill, bandwidth-bound decode) holds, but the absolute numbers do not transfer. See [[Apple Silicon and MLX]].
- TTFT/TBT/E2E (Table II) are useful vocabulary for the latency chapter: a System One has only a TTFT-like cost and no TBT.

## Links
- Concepts: [[Prefill and Decode]], [[KV Cache]], [[Energy of LLM Inference]], [[On-Device Inference]], [[System One Models]]
- Related sources: [[Pope 2023 - Efficiently Scaling Transformer Inference]], [[Kwon 2023 - PagedAttention vLLM]], [[Samsi 2023 - From Words to Watts]], [[Luccioni 2024 - Power Hungry Processing]]
