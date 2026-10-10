---
type: source
author: "Keivan Alizadeh, Iman Mirzadeh, Dmitry Belenko, S. Karen Khatamifard, Minsik Cho, Carlo C. Del Mundo, Mohammad Rastegari, Mehrdad Farajtabar (Apple)"
date: 2024
venue: "ACL 2024 (arXiv 2312.11514)"
url: "https://arxiv.org/abs/2312.11514"
tags: [source, paper, on-device, flash-memory, dram, sparsity, apple-silicon, inference]
---
# Alizadeh 2024 – LLM in a flash: Efficient LLM Inference with Limited Memory

**Raw file**: `raw/Alizadeh 2024 - LLM in a flash_ingested.pdf`

## Overview
An Apple paper on running LLMs **larger than the available DRAM** by keeping the weights in **flash storage** and loading only the needed parts on demand. Guided by a cost model of flash reads, it introduces **windowing** (reuse neurons activated by recent tokens) and **row-column bundling** (store matching up-projection columns and down-projection rows together to read bigger contiguous chunks). Together with a low-rank predictor of ReLU activation sparsity, this runs models **up to 2× the DRAM size**, with up to **4×, 7× and 20×** faster inference than naive loading on CPU, Metal and NVIDIA GPU, respectively (abstract, §1).

## Key Insights
1. **Memory hierarchy (§2.1, Fig. 2a).** In a unified-memory device, flash offers about 100 GB of capacity at about 1 GB/s of random-read bandwidth, DRAM about 10 GB at about 100 GB/s. A 7B model needs over 14 GB in half precision, beyond most personal devices (§1).
2. **Flash favours large reads (§2.2, Fig. 2b).** An M1 Max with 1 TB SSD exceeds 6 GiB/s on a 1 GiB sequential read, but small random reads are much slower due to latency to first byte. 32 KiB or larger reads across 32 threads make sparse loading viable.
3. **Sparsity (§3.1).** OPT 6.7B has 97% sparsity in its FFN layer; ReLU-fied Falcon 7B 95%; FATReLU Llama 2 about 90%. Attention weights and embeddings (about one third of the model) stay in DRAM; only the predicted-active FFN neurons are loaded.
4. **Results (Tables 2–3).** For OPT 6.7B (16-bit) on an M1 Max with half the model in memory, I/O latency per token falls from 2,196 ms (naive) to 87 ms with predictor, windowing and bundling. End-to-end per-token latency on Metal M1 falls from 2,389 ms to 565 ms (I/O 2,196 → 92 ms, while compute rises from 193 to 438 ms), and on the RTX 4090 from 2,218 ms to 84 ms.
5. **Energy note (§5.3).** The sparse model draws less **power**, but takes longer per token, so its total **energy** is higher than the dense model's. The authors leave a systematic power study to future work.
6. **Limitations (§8).** Single-batch generation only; prompt processing (prefill) and multi-batch inference are not studied; memory is assumed to be half the model size.

## Relevance to GroundOne
- **Memory, not compute, limits on-device LLMs.** The paper frames the constraint GroundOne faces on the 16 GB M4: weights must fit in unified memory alongside the generator and the retriever. GroundOne avoids flash offloading entirely by choosing small models (0.5B and 3B, 8-bit, peak memory 2.6–5.9 GB in training) rather than larger models streamed from SSD. See [[On-Device Inference]] and [[Apple Silicon and MLX]].
- **Decode is the target of these optimisations.** The paper optimises per-token generation (weights reloaded for every token). A System One generates no tokens, so its cost is one prefill, which the paper explicitly does not study (§8). This is another sign that prefill-only workloads are a different regime from the one most on-device work targets ([[Prefill and Decode]]).
- **Power vs energy.** §5.3 is an independent example of the pattern GroundOne measured: lower power does not imply lower energy when the run lasts longer. GroundOne draws more power than a decoding judge but finishes sooner ([[Energy of LLM Inference]]).
- **Apple's on-device direction.** Together with [[Gunter 2024 - Apple Intelligence Foundation Language Models|Apple Intelligence]], it documents the platform vendor's own work on running LLMs locally on Apple silicon.

## Links
- Concepts: [[On-Device Inference]], [[Apple Silicon and MLX]], [[Prefill and Decode]], [[KV Cache]], [[Energy of LLM Inference]]
- Related sources: [[Gunter 2024 - Apple Intelligence Foundation Language Models]], [[MLX README (ml-explore)]], [[Patel 2024 - Splitwise (prefill vs decode phases)]]
