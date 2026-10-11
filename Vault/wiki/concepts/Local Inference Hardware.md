---
type: concept
tags: [concept, hardware, local-inference, apple-silicon, dgx-spark, strix-halo, consumer-gpu, memory-bandwidth, unified-memory, locality-pillar]
---
# Local Inference Hardware

The hardware on which language models can run outside a datacenter, compared on the three axes that decide what is feasible ([[On-Device Inference]]): **memory capacity** (which model fits), **memory bandwidth** (decode speed, since every generated token reads all the weights) and **compute** (prefill speed). Power and price complete the picture. Ingested 2026-10-11 for the Ch. 1–2 overview.

## The rule that organises everything
- **Decode is bandwidth-bound**: at batch 1, time per generated token ≥ weight bytes / bandwidth. Measured decode reaches about 65 % (DGX Spark) and 73 % (M3 Ultra) of the theoretical bandwidth in EXO's test ([[EXO Labs 2025 - NVIDIA DGX Spark and Mac Studio, disaggregated inference|EXO Labs 2025]]).
- **Prefill is compute-bound.** The cleanest evidence comes from two head-to-heads:
  - Spark vs M3 Ultra (Llama-3.1 8B FP16, 8k prompt): the Spark prefills **3.8×** faster, the M3 Ultra decodes **3.4×** faster (EXO).
  - M5 vs M4 with MLX: time to first token **3.3–4.1×** faster thanks to the GPU neural accelerators, generation only **1.19–1.27×** faster, in line with a 1.28× bandwidth increase (120 → 153 GB/s); Apple itself states that TTFT is compute-bound and generation bandwidth-bound ([[Apple ML Research 2025 - Exploring LLMs with MLX and the neural accelerators in the M5 GPU|Apple ML Research 2025]]).
  - Same pattern on edge devices: across 18 matched pairs, slowdowns accumulate in decode while prompt evaluation moves by at most +16 % ([[Das 2026 - Large Models for Small Devices, Edge AI Deployment (arXiv 2608.15693)|Das 2026]] §6.3).
- **Unified memory** (Apple silicon, DGX Spark, Strix Halo) lets the GPU address most of system RAM: it raises capacity, not bandwidth.

## Comparison (figures only as stated in the ingested sources; prices tied to date and market)
| System | Memory | Bandwidth | Compute | Power | Price |
| --- | --- | --- | --- | --- | --- |
| MacBook Pro M4 (thesis machine) | 16–32 GB | 120 GB/s | — | 70 W adapter | — |
| MacBook Pro M5 | 24 GB tested | 153 GB/s | GPU neural accelerators | — | — |
| Mac Studio M4 Max | 36 / 48–128 GB | 410 / 546 GB/s | — | 480 W max | — |
| Mac Studio M3 Ultra | 96–256 GB | 819 GB/s | ~26 TFLOPS FP16 (EXO) | 480 W max | — |
| NVIDIA DGX Spark (GB10) | 128 GB | 273 GB/s | 1 PFLOP FP4 sparse; ~100 TFLOPS FP16 (EXO) | 140 W chip, 240 W PSU | ~$4,699 (search snippet, not on the vendor page) |
| AMD Strix Halo (Framework Desktop) | 32–128 GB, up to 96 GB as VRAM (110 GB on Linux) | — (~215 GB/s measured, per search snippet) | NPU 50 TOPS | 55 W chip | $1,099–1,999 (Aug 2025, US), later raised by the RAM shortage |
| Mac mini M4 Pro 64 GB | 64 GB | — | — | — | ~€2,500 (Mar 2026) |
| RTX 5090 / 4090 / used 3090 | 32 / 24 / 24 GB | — | — | 575 / 450 / 350 W | $1,999+ / $1,500–1,800 / $650–800 (SEO source) |
| Intel Arc Pro B60 | 24 GB | "450 GB/s" (forum, unverified) | — | — | ~€640 |

Sources: [[NVIDIA - DGX Spark hardware overview]], [[Apple 2025 - Mac Studio (2025) tech specs]], [[Apple 2024 - MacBook Pro 14-inch M4 tech specs]], [[EXO Labs 2025 - NVIDIA DGX Spark and Mac Studio, disaggregated inference]], [[Hardware Corner 2025 - How fast is the AI Max+ 395 for LLM inference]], [[PCWorld - Framework Desktop review]], [[Corelab - Best GPU for local LLMs, VRAM tier list]], [[Level1Techs - ASRock Intel Arc Pro B60 24 GB for local AI]], [[Davies Meyer - Mac mini M4 Pro for local AI inference]].

## Classes and what they are for
- **Laptops (16–32 GB, 100–150 GB/s)**: small models (≤ 8B quantised); the thesis machine. Everything in GroundOne fits here.
- **Desktop unified-memory machines under $3k** (Strix Halo 128 GB, Mac mini M4 Pro 64 GB): large or MoE models at modest decode speed; a 70B Q8 runs at about 3 tok/s on Strix Halo vs 5.5–6.3 on an M4 Max 128 GB (Hardware Corner).
- **Dedicated AI boxes above $3k** (Mac Studio M3 Ultra, DGX Spark): Spark for prefill-heavy and CUDA work, Mac Studio for decode-heavy chat; EXO combines both by disaggregating prefill and decode ([[EXO Labs 2025 - NVIDIA DGX Spark and Mac Studio, disaggregated inference|EXO]]; cf. Splitwise in [[Prefill and Decode]]).
- **Discrete consumer GPUs**: very high bandwidth and compute but VRAM capped at 12–32 GB; the model must fit in VRAM.
- **Mobile SoCs**: 50–60 GB/s, 6–16 GB RAM, < 10 W ([[Wang 2025 - Cognitive Edge Computing, Optimizing Large Models and AI Agents (arXiv 2501.03265)|Wang 2025]], [[Li 2025 - Collaborative Inference between Edge SLMs and Cloud LLMs, A Survey (arXiv 2507.16731)|Li 2025]]).

## Runtimes matter as much as chips
On an M2 Ultra, decode throughput ranges from about 230 tok/s (MLX) to 150 (llama.cpp), 20–40 (Ollama) and 7–9 (PyTorch MPS) ([[Rajesh 2025 - Local LLM inference on Apple Silicon, MLX vs MLC vs Ollama vs llama.cpp (arXiv 2511.05502)|Rajesh 2025]], internally inconsistent; use as indicative only). On the same Mac, MLX decodes about 15 % faster than GGUF (Hardware Corner). Intel's software stack is fragmented (Level1Techs). See [[Apple Silicon and MLX]], [[Quantization]].

## Relevance to GroundOne
- **The prefill/decode asymmetry is visible across every class of hardware**, and vendors themselves (Apple, EXO) now describe it. This is independent support for the thesis argument that a System One, which never decodes, gains most where decoding is slow ([[When System One Beats an LLM]]).
- **Prefill-oriented hardware is the trend** (M5 neural accelerators, DGX Spark): GroundOne's single prefill per answer would benefit directly, while a generative judge's decode would benefit far less. This is an extrapolation from the vendors' 1.7B–30B, 4k-token measurements, not a GroundOne measurement.
- **The thesis machine is the low end** (16 GB, 120 GB/s): if GroundOne fits and is fast there, it fits everywhere above. DGX Spark and Strix Halo would need a non-MLX port.

## Quality notes
- Vendor pages (Apple, NVIDIA) give no price and few compute figures; EXO measures its own software. Corelab and Davies Meyer are SEO/marketing with impossible products or numbers; Level1Techs is anecdotal. Apple's page lists 256 GB maximum for the M3 Ultra, while EXO and Hardware Corner describe 512 GB.

## Links
- Concepts: [[On-Device Inference]], [[Apple Silicon and MLX]], [[Prefill and Decode]], [[Energy of LLM Inference]], [[Mixture of Experts]], [[Quantization]], [[Small Language Models]]

## Additions (ingest 2026-10-11, second batch; thesis Ch. 2)
- Current Apple lineup from vendor pages: MacBook Pro / Mac mini M5 153 GB/s (16–32 GB), M5 Pro 307 GB/s (24–64 GB), M5 Max 460–614 GB/s (up to 128 GB) ([[Apple 2026 - MacBook Pro tech specs (M5 family)]], [[Apple 2026 - Mac mini tech specs]]); NVIDIA RTX 50 bandwidths ([[NVIDIA 2026 - GeForce graphics cards compare specs]]).
- Phone NPUs: fast INT8 prefill (7B INT4 at 770 tok/s), decode limited to 44–60 GB/s shared bandwidth ([[Xue 2024 - PowerInfer-2, Fast Large Language Model Inference on a Smartphone (arXiv 2406.06282)|Xue 2024]], [[Xu 2025 - Fast On-device LLM Inference with NPUs (arXiv 2407.05858)|Xu 2025]]).
- Thesis figures (`groundone figures locality`): `hardware_landscape` (thesis machine at its actual 16 GB, bars over memory ranges), `decode_floor_by_hardware`, `judge_decode_overhead_by_hardware` (3B judge, K ≥ 14: ≥ 1.78 s terse / 10.6 s verbose on the M4, 0.12 / 0.71 s on an RTX 5090), `roofline_m4`, `memory_fit`, `open_closed_gap`, `prefill_vs_decode_m4`.
