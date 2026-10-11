---
type: source
author: "NVIDIA Corporation"
date: 2026-09-10
venue: "NVIDIA DGX Spark User Guide, Hardware Overview (documentation page, revision dated 2026-09-10; retrieved 2026-10-11)"
url: "https://docs.nvidia.com/dgx/dgx-spark/hardware.html"
tags: [source, vendor-spec, hardware, nvidia, dgx-spark, grace-blackwell, unified-memory, bandwidth, local-inference]
---
# NVIDIA – DGX Spark Hardware Overview

**Raw file**: `raw/local_inference/NVIDIA - DGX Spark hardware overview_ingested.md`

## Overview
NVIDIA's official hardware documentation for the **DGX Spark**, a small-form-factor desktop built on the GB10 Grace Blackwell system-on-chip (integrated Arm CPU and Blackwell GPU sharing one LPDDR5x memory pool). It is the citable vendor source for the Spark's memory, bandwidth, compute and power figures. The page contains specifications only: no benchmarks, and **no price**.

## Key Insights (vendor specifications)
| Item | Specification (as stated by NVIDIA) |
| --- | --- |
| Architecture | Grace Blackwell, integrated GPU and CPU (GB10 SoC) |
| CPU | 20-core Arm: 10 Cortex-X925 + 10 Cortex-A725 |
| GPU | Blackwell, 5th-gen Tensor Cores (FP4 support), 4th-gen RT Cores, **6,144 CUDA cores** |
| **Memory** | **128 GB LPDDR5x unified system memory**, 256-bit interface, 16 channels, LPDDR5X-8533 (listed as "4266 MHz" clock) |
| **Memory bandwidth** | **273 GB/s** |
| **AI compute** | "Up to 1,000 TOPS" inference and "up to 1 PFLOP at FP4 precision **with sparsity**" |
| Storage | 1 TB or 4 TB NVMe M.2, self-encrypting |
| Network | 10 GbE RJ-45, ConnectX-7 Smart NIC (2x QSFP), Wi-Fi 7, Bluetooth 5.4 |
| **Power** | 240 W external supply; **GB10 SoC TDP 140 W**, 100 W for the rest of the system |
| Size / weight | 150 x 150 x 50.5 mm, 1.2 kg |
| Model support (vendor claim) | "AI models up to 200 billion parameters" (405B with two Sparks) |
| Software listed | PyTorch, TRT-LLM, "other AI frameworks" |

- **Internal consistency check (arithmetic):** 256 bit x 8533 MT/s / 8 = 273 GB/s, so the bandwidth matches the memory configuration; "4266 MHz" is the clock of the double-data-rate memory, not a second, conflicting speed.
- The **1 PFLOP figure is a peak at FP4 with structured sparsity**, the most favourable possible precision. No dense FP16/BF16 or INT8 figure is given on this page. [[EXO Labs 2025 - NVIDIA DGX Spark and Mac Studio, disaggregated inference|EXO Labs]] quotes "~100 TFLOPs of FP16", which is a third-party figure, not from this page.
- The "200B parameters" claim does not state the precision. 128 GB can only hold 200B parameters at about 4 bits per weight or less (arithmetic: 200B x 0.5 byte = 100 GB), so it implicitly assumes FP4-class quantisation.

## Relevance to GroundOne
- **Bandwidth bound on decode.** At 273 GB/s the Spark has about 2.3x the bandwidth of the thesis M4 (120 GB/s, [[Apple 2024 - MacBook Pro 14-inch M4 tech specs]]). For a 3B model in 8-bit (about 3.3 GB), the decode lower bound would be about 12 ms/token instead of about 27 ms (arithmetic). Its bandwidth is still well below the Mac Studio M3 Ultra's 819 GB/s ([[Apple 2025 - Mac Studio (2025) tech specs]]).
- **Compute-rich, bandwidth-moderate.** The Spark is the archetype of a device whose advantage is in **prefill** (compute), which is exactly the phase a System One uses. EXO Labs' measurement (Spark prefill 3.8x faster than an M3 Ultra, decode 3.4x slower) illustrates this ([[Prefill and Decode]]).
- **Power envelope.** 140 W SoC TDP is far above the about 16 W of SoC power GroundOne draws on the M4 during verification. A comparison of joules per verification would need measurement on the device, not TDP ([[Energy of LLM Inference]]).
- **Does not apply directly.** GroundOne is implemented in MLX for Apple Silicon. The page lists PyTorch and TRT-LLM, so running GroundOne here would need a port. A 128 GB machine is also far more than GroundOne needs: the 3B model peaked at 5.9 GB in training. The Spark belongs in the thesis as context ("dedicated local inference machines"), not as a target platform.
- **No price on the page.** Any price must come from another dated source.

## Links
- Concepts: [[On-Device Inference]], [[Prefill and Decode]], [[Energy of LLM Inference]], [[Local Inference Hardware]] (proposed), [[Local Inference Hardware|Unified Memory Architecture]] (proposed), [[Prefill and Decode|Memory Bandwidth Bound]] (proposed), [[Quantization]] (proposed)
- Related sources: [[EXO Labs 2025 - NVIDIA DGX Spark and Mac Studio, disaggregated inference]], [[Apple 2025 - Mac Studio (2025) tech specs]], [[Apple 2024 - MacBook Pro 14-inch M4 tech specs]], [[Hardware Corner 2025 - How fast is the AI Max+ 395 for LLM inference]], [[Patel 2024 - Splitwise (prefill vs decode phases)]]
