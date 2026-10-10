---
type: source
author: "Siddharth Samsi, Dan Zhao, Joseph McDonald, Baolin Li, Adam Michaleas, Michael Jones, William Bergeron, Jeremy Kepner, Devesh Tiwari, Vijay Gadepally"
date: 2023
venue: "IEEE HPEC 2023 (arXiv 2310.03003)"
url: "https://arxiv.org/abs/2310.03003"
tags: [source, paper, energy, inference, gpu, llama, power-capping, green-ai]
---
# Samsi 2023 – From Words to Watts: Benchmarking the Energy Costs of LLM Inference

**Raw file**: `raw/Samsi 2023 - From Words to Watts_ingested.pdf`

## Overview
An early empirical study (MIT, NYU, Northeastern) of the **energy cost of LLM inference**, as opposed to training. It runs LLaMA 7B, 13B and 65B on NVIDIA V100 (32 GB) and A100 (80 GB) GPUs of the MIT Supercloud, on 4,096 prompts each from Alpaca and GSM8K, with model sharding up to 32 GPUs (§III). The authors call it a "preliminary analysis": output quality, quantisation and continuous batching are explicitly out of scope (§III-C).

## Key Insights
1. **Measurement method (§III-C).** GPU power from `nvidia-smi` sampled every 100 ms and aggregate GPU energy in joules from NVIDIA DCGM on the rank-0 node, multiplied by the number of nodes. Derived metrics are **energy per second (W)**, **energy per decoded output token** and **energy per response** = total energy divided by tokens or responses. Only GPU energy is counted (no CPU, DRAM or cooling).
2. **Faster is not free (§IV-A, Fig. 2–3).** The A100 gives up to 2× (7B) and 1.25× (13B) higher throughput than the V100, but at a considerably higher energy per second, especially for the 7B. For the 65B the throughput gain is small and it is unclear whether the extra power is worth it.
3. **Per-token energy of a 65B model (§IV-C, Fig. 6–7).** About **3–4 J per output token**, nearly unchanged between maximum generation lengths of 512 and 1,024. More shards always raise power (300 W to about 1 kW for 8 to 32 GPUs, §IV-B) and energy per token.
4. **Power capping (§IV-E, Table III).** On 4× A100 with LLaMA 65B, capping from 250 W to 175 W raises inference time by about 6–7% while cutting total energy by about 22–24%. A 150 W cap costs 15–22% more time.
5. **Utilisation (§IV-F, Table IV).** Streaming-multiprocessor utilisation stays at 94–99%, while memory utilisation on 80 GB A100s is only 23–27%, suggesting co-location of several models.

## Relevance to GroundOne
- **Method template.** GroundOne measures joules per verified answer with macOS `powermetrics` (SoC CPU + GPU + ANE, 200 ms sampling, net of about 0.2 W idle). This is the Apple-silicon counterpart of Samsi's nvidia-smi/DCGM protocol, and like Samsi it counts accelerator energy only (no DRAM, display or SSD). The thesis should state this scope explicitly, as Samsi does. See [[Energy of LLM Inference]].
- **Energy per response is the right unit.** Samsi normalises by responses as well as tokens. For GroundOne the natural unit is **energy per verified answer** (5.5 J for the 0.5B, 33 J for the 3B), because a System One produces no output tokens to normalise by.
- **"Faster ≠ proportionally less energy".** Samsi's A100 vs V100 result (higher throughput, higher power) is the same pattern as GroundOne vs generative judges: GroundOne is about 2× faster than a terse judge but uses only 1.3–1.6× less energy, because its compute-bound prefill draws more power ([[Patel 2024 - Splitwise (prefill vs decode phases)|Splitwise]]).
- **Order-of-magnitude contrast.** 3–4 J per *token* for a sharded 65B model in a datacenter, against about 5.5 J per *whole verified answer* (about 9 decisions per answer on average in the energy subset: 5.5 J / 0.63 J per decision) for GroundOne 0.5B on a laptop. The setups differ completely (model size, hardware, batching), so this is context for the locality argument, not a like-for-like comparison.

## Links
- Concepts: [[Energy of LLM Inference]], [[Prefill and Decode]], [[On-Device Inference]]
- Related sources: [[Luccioni 2024 - Power Hungry Processing]], [[Patel 2024 - Splitwise (prefill vs decode phases)]], [[Alizadeh 2024 - LLM in a flash]]
