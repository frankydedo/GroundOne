---
type: source
author: "Zhenyan Lu, Xiang Li, Dongqi Cai, Rongjie Yi, Fangming Liu, Xiwen Zhang, Nicholas D. Lane, Mengwei Xu (BUPT, Peng Cheng Laboratory, Helixon Research, University of Cambridge)"
date: 2024
venue: "arXiv 2409.15790 (v3, 26 Feb 2025)"
url: "https://arxiv.org/abs/2409.15790"
tags: [source, paper, survey, small-language-models, on-device, prefill, decode, quantization, llama-cpp, memory, kv-cache, qwen]
---
# Lu 2024 – Small Language Models: Survey, Measurements, and Insights

**Raw file**: `raw/local_inference/Lu 2024 - Small Language Models, Survey, Measurements, and Insights (arXiv 2409.15790)_ingested.pdf`

## Overview
A survey and measurement study of **small language models (SLMs)**, defined as **decoder-only transformers with 100M–5B parameters** and open weights (§1–2). It reviews architectures, pre-training datasets and training algorithms (§2). It benchmarks capabilities on commonsense reasoning, problem solving, mathematics, in-context learning and long context (§3). It measures **on-device runtime cost** (prefill and decode latency, memory) with **llama.cpp** on a Jetson Orin NX 16 GB (GPU) and three Android phones (CPU) (§4), surveys on-device optimisations (§4.4), and lists future directions (§5). First author and title confirmed on page 1 (Zhenyan Lu and Xiang Li contributed equally). The upper bound of 5B is justified because, as of September 2024, 7B LLMs were "still mostly deployed in the cloud" (§1 footnote).

## Key Insights
1. **Scope inconsistency.** The abstract says **70** SLMs were surveyed (also §2.1 and Table 1). §1 says **57** were "collected" and fully benchmarked. Runtime cost is measured on **20** models (§4).
2. **Typical SLM architecture as of August 2024 (§2.2 Insights, Fig. 2).** Group-query attention (GQA replacing MHA), gated FFN with SiLU, FFN ratio 2–8, RMSNorm, vocabulary above 50k. The choices are "mostly empirical". Architectural innovations (other than embedding–lm_head sharing, used by Gemma and Qwen) show no strong evidence of superiority.
3. **Qwen2.5 in Table 1.** 0.5B / 1.5B / 3B, released 2024-09, GQA, SiLU, 152k vocabulary, 32k context. Layers 24 / 28 / 36, hidden size 896 / 1536 / 2048, heads 14 / 12 / 16.
4. **Data over size (§2.3 Insights).** Data quality outweighs quantity and architecture. Model-filtered datasets (FineWeb-Edu, DCLM-baseline) closed much of the gap to closed-data models. SLMs are heavily **"over-trained"** relative to Chinchilla (~20 tokens/parameter): typically >1.5T tokens, and Qwen2-0.5B used **12T** tokens vs **7T** for Qwen2-1.5B. The rationale is to spend training compute so that small models deploy well on constrained devices.
5. **Capability trend (§3.2, Fig. 5).** 2022→2024 gains of **10.4%, 13.5%, 13.5%** on commonsense, problem solving and math, vs **7.5%** average for the LLaMA-7B series. Phi-3-mini (3.8B) rivals LLaMA 3.1 8B, which the authors partly attribute to data engineering and possible benchmark overfitting. Open-data SLMs are close on commonsense but behind on math and logic.
6. **In-context learning (§3.3).** 5-shot improves zero-shot SLMs by **2.1%** on average. Larger SLMs benefit more; some small ones get worse (LaMini, more than −2%).
7. **Long context (§3.4, Fig. 7, Needle-in-a-Haystack).** Average accuracy: Qwen1.5-0.5B **22.13%**, Qwen2-0.5B **43.84%**, Llama3.2-3B **57.81%**, **Qwen2.5-3B 91.71%** (near-perfect at all lengths and depths). "Lost in the middle" also appears in small models. Figure titles show these runs used **instruct models via vLLM**, although the paper says it mainly uses base models. Qwen2.5-0.5B is plotted but its score is not stated in the text.
8. **Runtime cost (§4.1, Fig. 8; 4-bit, prompt 50, generate 50, context 2048).**
   - Memory ranges from **275 MB to 2,456 MB** for 0.1B–3B models and is roughly linear in parameters. Large vocabularies inflate the compute buffer (Bloom-560M: 492 MB, 3.5× OpenELM-1.1B).
   - Architecture affects **prefill** latency more than decode: Qwen1.5-0.5B has 25.4% more parameters than Qwen2-0.5B but is 31.9% faster at first-token time on the Jetson. Prefill is more compute-bound, decode memory-bound.
   - Decode latency is close to linear in model size.
   - The authors note that prefill is "often regarded as the dominate phase in end-to-end LLM inference on devices", because on-device tasks involve long context.
9. **Quantisation (§4.2.1, Fig. 9, Phi-1.5).** Decode gains are larger and more consistent (latency reduced by up to 75%, at least 17%) than prefill gains (at least 25% on short prompts, shrinking as prompts grow). **Q4_K_M** is best (about 50% average prefill reduction). Irregular bit-widths (3, 5, 6 bit) can be as slow as or slower than 8-bit.
10. **Hardware (§4.2.2).** The Jetson GPU prefills **10–20×** faster than the Meizu 18 Pro CPU (Bloom-1B1). On phones, latency rises over the first ~10 generated tokens because of thermal throttling (DVFS).
11. **Breakdown (§4.3).** Matrix-vector multiplication dominates (">80%" of time in §4.3.1, ">70%" in the Insights box, another inconsistency). At long contexts the KV cache plus compute buffer take **83–87%** (Qwen2 at 131,072 tokens) to **85–90%** (Qwen1.5 at 32,768) of memory.
12. **Future directions (§5).** Hardware–architecture co-design; synthetic and filtered data; a "deployment-aware Chinchilla law"; on-device personalisation. On that last point, RAG on device "can significantly increase the on-device cost (text embedding generation, longer prompt processing)". Also device–cloud collaboration, fair SLM benchmarking (overfitting to GSM8K), and sparse SLMs (MoE seen as trading memory for compute, a poor fit for memory-constrained devices).

**Quality notes.** Peer-reviewed status not stated (arXiv v3). Measurements use 2021–2023 Android phones and a Jetson, **not Apple Silicon**, and only llama.cpp at 4-bit. Prompts of 50 tokens are far shorter than RAG prompts. The introduction lists "energy consumption" among the measured runtime costs, but §4 reports no energy measurements of its own (energy figures appear only in the related-work summaries of §4.4). Minor internal inconsistencies: 70 vs 57 models; ">80%" vs ">70%"; a quantisation Insights box announced as "two" insights lists three.

## Relevance to GroundOne
- **Defines the class GroundOne belongs to.** Qwen2.5-0.5B and 3B fall within the paper's 100M–5B SLM definition, and both appear in Table 1. Useful as the standard citation for "small language model" in Ch. 1–2 ([[Small Language Models]], [[Qwen2.5]]).
- **Independent support for the prefill/decode argument.** The paper measures that prefill is compute-bound and sensitive to architecture, and decode memory-bound and linear in size. It also states that prefill dominates on-device workloads with long context. This matches GroundOne's design: one long prefill over document + answer, zero decode ([[Prefill and Decode]]). Its numbers come from llama.cpp at 4-bit on Jetson and phones with 50-token prompts, so they cannot be transferred to MLX 8-bit on an M4 with RAG-length prompts.
- **Long context at 3B.** Qwen2.5-3B's 91.71% on Needle-in-a-Haystack (instruct model) is weak but positive evidence that the 3B handles long documents. NIAH is retrieval, not verification, and GroundOne's prompts are well below 32k.
- **Memory is dominated by KV cache at long context.** This supports GroundOne's choice of one pass per answer with the readout only at the markers, rather than KV-cache replication (design a) ([[KV Cache]], [[Letter-Token Readout]]).
- **Quantisation caveat.** On this hardware, 8-bit was not slower than irregular bit-widths and 4-bit was fastest. GroundOne uses 8-bit weights in MLX. The paper measures latency only, not the accuracy cost of 4-bit, so it gives no basis for or against that choice.
- **On-device RAG costs.** §5 explicitly names on-device RAG as costly (embeddings plus longer prompts). GroundOne adds a verifier on top of this. Its single-prefill design is the cheapest way to add verification, but it is still added cost ([[Retrieval-Augmented Generation]], [[On-Device Inference]]).

## Links
- Concepts: [[Prefill and Decode]], [[KV Cache]], [[On-Device Inference]], [[Qwen2.5]], [[Mixture of Experts]], [[Retrieval-Augmented Generation]], [[Letter-Token Readout]], [[Small Language Models]] (proposed), [[Quantization]] (proposed), [[Local Inference Hardware]] (proposed)
- Related sources: [[Qwen Team 2024 - Qwen2.5 Technical Report]], [[llama.cpp README (ggml-org)]], [[Alizadeh 2024 - LLM in a flash]], [[Patel 2024 - Splitwise (prefill vs decode phases)]], [[Stanford HAI 2025 - AI Index Report, Technical performance]], [[Google 2025 - Introducing Gemma 3n]]
