---
type: source
author: "Zhenliang Xue, Yixin Song, Zeyu Mi, Xinrui Zheng, Yubin Xia, Haibo Chen (IPADS, Shanghai Jiao Tong University)"
date: 2024
venue: "arXiv preprint 2406.06282 (v3, 12 Dec 2024); no peer-reviewed venue stated in the file"
url: "https://arxiv.org/abs/2406.06282"
tags: [source, paper, preprint, on-device, smartphone, npu, sparsity, flash-offloading, decode, energy]
---
# Xue 2024 – PowerInfer-2: Fast Large Language Model Inference on a Smartphone

**Raw file**: `raw/local_inference/Xue 2024 - PowerInfer-2, Fast Large Language Model Inference on a Smartphone (arXiv 2406.06282)_ingested.pdf`

## Overview
A smartphone inference framework for LLMs **larger than the available memory**. It extends PowerInfer, the earlier PC system, with 12K lines of C++. The core abstraction is the **neuron cluster**: a group of FFN neurons with the same activation pattern, sized at runtime for the target processor. Clusters with dense activations run on the **NPU**, sparse clusters on the **CPU**, and a cluster-level pipeline overlaps computation with flash (UFS) I/O, helped by a segmented neuron cache. Prefill uses an **NPU-centric** workflow; decoding uses a hybrid CPU/NPU workflow that adapts to the batch size. Headline claims: up to **27.8×** faster than state-of-the-art frameworks, and the first **47B** model served on a smartphone (TurboSparse-Mixtral-47B at **11.68 tokens/s**), with negligible accuracy loss (abstract). The file is the arXiv v3 preprint; it states no peer-reviewed venue.

## Key Insights
1. **Two hardware gaps between phones and PCs (§1, §2.3).** (i) **Sparse computing:** mobile NPUs are fast on dense operations but lack sparse support, so PC-style sparse systems (PowerInfer, LLM in a flash) fall back to the CPU and decode about 70% slower for 7B models. (ii) **Storage:** UFS 4.0 offers about half the sequential bandwidth of a PC NVMe SSD (4 vs 7.5 GB/s) and about 1/12 of the random-read IOPS (100K vs 1,200K).
2. **The NPU wins prefill, the CPU wins sparse decode (§2.3, Fig. 3a).** On a OnePlus 12 (Snapdragon 8 Gen 3), a 7B INT4 model reaches **770 tokens/s prefill on the NPU, vs 37 on the GPU and 8 on the CPU**. At batch sizes below 1 (sparse matrix–vector), six CPU cores beat the NPU and the GPU. The share of highly activated neurons rises from **<1% at batch 1 to about 75% at batch 32** (Fig. 2).
3. **Shared memory bandwidth (§2.3).** In unified memory, matrix operations on a 7B model reach **43.9 GB/s CPU-only, 56 GB/s NPU-only and 59.6 GB/s with both**. Using both processors therefore raises the effective bandwidth available to memory-bound decoding.
4. **Mobile GPUs are avoided (§2.3).** The GPU was slower than both NPU and CPU on matrix–vector operations, and only about 50% of its kernel time was compute. Citing "private communications", the authors report that phone manufacturers avoid GPUs for LLM inference because of contention with rendering. This is anecdotal evidence.
5. **Offloading kills existing systems (§2.4, Table 2).** On the OnePlus 12 with Mistral-7B and 50% of FFN weights in flash, decoding falls from **12.4 to 1.4 tokens/s** (PowerInfer, −89%) and from **12.9 to 2.3 tokens/s** (LLMFlash, −82%).
6. **Results (§7, Tables 3–8).** Devices: OnePlus 12 (24 GB, 19 GB available, UFS 4.0) and OnePlus Ace 2 (Snapdragon 8+ Gen 1, 16 GB, 11 GB available, UFS 3.1).
   - **Decoding** with 50% FFN offload on the OnePlus 12: on average **24.6×** (up to 27.8×) over llama.cpp and **3.84×** (up to 4.63×) over LLMFlash.
   - **Prefill** at 512 tokens with offload: **44.23×** over llama.cpp, **48.97×** over LLMFlash and **1.99×** over Qualcomm's QNN.
   - **In memory** (Bamboo-7B): prefill exceeds **700 tokens/s** for both PowerInfer-2 and QNN, about 32× the other frameworks. Decoding is **2.24×** faster than llama.cpp, attributed to CPU+NPU bandwidth (43.9 → 59.6 GB/s) and sparsity.
   - **Memory:** with 7 GB available, Mixtral-47B decodes at 2.13 tokens/s, and at 19 GB at 11.68 tokens/s.
7. **Energy (§7.4, Table 8).** Over 100 lmsys-chat-1m prompts, energy per generated token is **0.257 J (PowerInfer-2) vs 0.373 J (QNN) and 0.672 J (llama.cpp)**, i.e. −31.1% and −61.8%. Peak power is similar: **5.095 W, 5.133 W and 4.065 W**. Llama.cpp draws the lowest peak power but uses the most energy per token, because it runs longer.
8. **Quantization granularity matters (§7.6, Table 7).** QNN's per-channel INT4 hurts accuracy badly. For Qwen2-7B, the average is 56.93 vs 79.25 (llama.cpp, group size 32) and 78.38 (PowerInfer-2, outlier weights in INT8 plus INT4 per channel), and GSM8K drops to **22.26** vs 77.43 (llama.cpp). NPUs do not support group-wise quantization.

## Relevance to GroundOne
- **Independent support for the cost model.** The paper splits the work by phase: dense, compute-bound prefill goes to the NPU, and memory-bound decode is limited by bandwidth (43.9 / 56 / 59.6 GB/s). This is the same split the thesis uses to explain why a prefill-only verifier is cheap ([[Prefill and Decode]]). The 770 vs 37 vs 8 tokens/s prefill comparison (NPU / GPU / CPU) is a strong illustration of why the accelerator matters for prefill, keeping in mind that it comes from a single Fig. 3a measurement on one phone ([[Local Inference Hardware]]).
- **Mostly about decode and oversized models, which GroundOne avoids.** Most of the contribution (sparsity prediction, neuron caches, flash pipelining) serves token generation for models that do not fit in DRAM. GroundOne generates no tokens and uses models that fit comfortably in 16 GB (0.5B and 3B at 8-bit). That puts it outside the regime this paper optimises, much as with [[Alizadeh 2024 - LLM in a flash]].
- **Power vs energy, again.** Table 8 is a third independent instance of the pattern GroundOne measured: the lowest peak power (llama.cpp, 4.07 W) gives the highest energy per token (0.672 J) because the run lasts longer. GroundOne draws more power than a decoding judge but finishes sooner ([[Energy of LLM Inference]]). Note that the paper's metric is J per *generated* token, which is undefined for a System One. Compare energy per verified answer instead.
- **Quantization caution.** The QNN collapse on GSM8K shows that how weights are quantized for a given accelerator can matter more than the bit width. This is relevant if GroundOne were ever moved to an NPU or a coarser scheme ([[Quantization]]).
- **Privacy is the stated motivation.** The introduction lists privacy through local data processing and offline operation as reasons for on-device LLMs ([[Privacy and Data Sovereignty]], [[On-Device Inference]]).

## Links
- Concepts: [[Local Inference Hardware]], [[Prefill and Decode]], [[On-Device Inference]], [[Energy of LLM Inference]], [[Quantization]], [[Mixture of Experts]], [[Small Language Models]]
- Related sources: [[Xu 2025 - Fast On-device LLM Inference with NPUs (arXiv 2407.05858)]], [[Alizadeh 2024 - LLM in a flash]], [[Gunter 2024 - Apple Intelligence Foundation Language Models]]
