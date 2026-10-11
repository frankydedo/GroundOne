---
title: "EXO Labs 2025 - NVIDIA DGX Spark and Mac Studio, disaggregated inference"
url: https://blog.exolabs.net/nvidia-dgx-spark/
published: unknown
accessed: 2026-10-11
extracted_with: trafilatura 2.3.1
---

We recently received early access to 2 NVIDIA DGX Spark™ units. NVIDIA calls it the world's smallest AI supercomputer. It has \~100 TFLOPs of FP16 performance with 128GB of CPU-GPU coherent memory at 273 GB/s.

With EXO, we've been [running LLMs on clusters of Apple Mac Studios with M3 Ultra chips](https://x.com/alexocheema/status/1899735281781411907/video/1). The Mac Studio has 512GB of unified memory at 819 GB/s, but the GPU only has \~26 TFLOPs of FP16 performance.

The DGX Spark has 4x the compute, the Mac Studio has 3x the memory bandwidth.

What if we combined them? What if we used DGX Spark for what it does best and Mac Studio for what it does best, in the same inference request?

What you see as a user boils down to two numbers:

- **TTFT** (time‑to‑first‑token): delay from sending a prompt to seeing the first token.
- **TPS** (tokens per second): cadence of tokens after the first one appears.

Everything we do in the system exists to improve those two numbers. The reason they're hard to optimize together is that they're governed by two different phases of the same request: **prefill** and **decode**.

1. You send a prompt.
2. You wait. Nothing appears. This is the **prefill phase**, and it determines TTFT.
3. The first token appears.
4. A stream of tokens follows. This is the **decode phase**, and it determines TPS.

What's happening under the hood in those two phases, and why do they behave so differently?

Prefill processes the prompt and builds a KV cache for each transformer layer. The KV cache consists of a bunch of vectors for each token in the prompt.

These vectors are stored during prefill so we don't need to recompute them during decode.

For large contexts, the amount of compute grows quadratically with the prompt length (Θ(s²)) since every token needs to attend to all the other tokens in the prompt.

With modern techniques like Flash Attention, the data moved can be made to grow linearly with the prompt length (Θ(s)).

So the ratio between the compute and the data moved, i.e. the arithmetic intensity, is linear in the prompt length.

This makes prefill with large contexts compute-bound.

Decode is the auto‑regressive loop after prefill. Each step generates one token by attending against the entire KV cache built so far.

In decode, we are doing vector-matrix multiplications which have lower arithmetic intensity than matrix-matrix multiplications.

This makes decode memory-bound.

Once you separate the phases, the hardware choice is clear.

- **Prefill** → high compute device.
- **Decode** → high memory-bandwidth device.

If you prefill on one device and decode on another, you must send the KV cache across the network. The naive approach is to run prefill, wait for it to finish, transfer the KV cache, then start decode.

This adds a communication cost between the two phases. If the transfer time is too large, you lose the benefit.

The KV cache doesn't have to arrive as one blob at the end. It can arrive layer by layer.

As soon as Layer 1's prefill completes, two things happen simultaneously. Layer 1's KV starts transferring to the M3 Ultra, *and* Layer 2's prefill begins on the DGX Spark. The communication for each layer overlaps with the computation of subsequent layers.

In practice, EXO transfers the KV vectors of a layer *while* the layer is being processed, since the KV vectors are computed before the heavy compute operations. To hide the communication overhead, we just need the layer processing time (t<sub>comp</sub>) to be larger than the KV transfer time (t<sub>send</sub>).

The compute time is t<sub>comp</sub> = F / P, where F is the FLOPs per layer and P is machine FLOPs/s. For large contexts, F scales quadratically: F ∼ c<sub>1</sub>s², where c<sub>1</sub> is a model-dependent constant.

The transfer time is t<sub>send</sub> = D / B, where D is KV data in bits and B is network bandwidth in bits/s. The KV cache has a constant number of vectors per token, so D ∼ q·c<sub>2</sub>·s, where q is quantization (4-bit, 8-bit, etc.) and c<sub>2</sub> is model-dependent.

To fully hide communication, we need the transfer time to be less than the compute time: t<sub>send</sub> \< t<sub>comp</sub>. This means P/B \< F/(q·D) ∼ (c<sub>1</sub>/c<sub>2</sub>)·s/q. With DGX Spark at 100 TFLOPs FP16 and 10 GbE (10 Gbps) link between the DGX Spark and the M3 Ultra, the ratio P/B = 10,000. This means we need s > 10,000q/(c<sub>1</sub>/c<sub>2</sub>).

The constant K = c<sub>1</sub>/c<sub>2</sub> depends on the attention architecture. For older models with multi-head attention (MHA) like Llama-2 7B, K = 2. For models with grouped query attention (GQA), K is larger: Llama-3 8B has K = 8, while Llama-3 70B and Qwen-2.5 72B have K = 16.

With 8-bit KV streaming and K = 16 (Llama-3 70B), the threshold is s > 5k tokens. For K = 8 (Llama-3 8B), it's s > 10k tokens. For K = 2 (Llama-2 7B), it's s > 40k tokens.

Running Llama-3.1 8B (FP16) with an 8,192 token prompt and generating 32 tokens:

| Configuration | Prefill Time | Generation Time | Total Time | Speedup | 
|---|---|---|---|---|
| DGX Spark | 1.47s | 2.87s | 4.34s | 1.9× | 
| M3 Ultra Mac Studio | 5.57s | 0.85s | 6.42s | 1.0× (baseline) | 
| **DGX Spark + M3 Ultra** | **1.47s** | **0.85s** | **2.32s** | **2.8×** | 

The combined setup achieves the best of both worlds: DGX Spark's fast prefill (3.8× faster than M3 Ultra) and M3 Ultra's fast generation (3.4× faster than DGX Spark), delivering 2.8× overall speedup compared to M3 Ultra alone.

Disaggregated prefill and decode, layer-by-layer KV streaming, and hardware-aware phase placement are all automated in EXO.

When you start EXO, it automatically discovers all devices connected in your ad-hoc mesh network and profiles each for compute throughput, memory bandwidth, memory capacity, and network characteristics.

Given a model and your topology, EXO plans which device should handle prefill, which should handle decode, whether to pipeline across layers, when to stream KV, and how to adapt if network conditions change. You don't write the schedule. You don't compute the thresholds. You just run the model, and EXO figures out how to make your heterogeneous cluster fast.

Inference is no longer constrained by what one box can do, but by what your whole cluster can do together.
