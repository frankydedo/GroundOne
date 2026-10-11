---
type: concept
tags: [concept, energy, power, inference, prefill, decode, measurement, green-ai, groundone, locality-pillar]
---
# Energy of LLM Inference

Inference, not training, dominates the lifetime energy of deployed models: AWS estimates inference at 80–90% of ML cloud demand, and Google attributed 60% of its ML energy to inference ([[Luccioni 2024 - Power Hungry Processing|Luccioni 2024]] §1). For a local system, energy also means battery life and heat. This page collects how inference energy is measured, what drives it, and what [[GroundOne]] measured.

## Measuring it
| Study | Hardware | Tool | Scope | Unit |
| --- | --- | --- | --- | --- |
| [[Samsi 2023 - From Words to Watts|Samsi 2023]] §III-C | V100 / A100 (sharded LLaMA 7B–65B) | `nvidia-smi` at 100 ms + DCGM energy | GPU only | W, J per output token, J per response |
| [[Luccioni 2024 - Power Hungry Processing|Luccioni 2024]] §3.2 | one A100 on an 8-GPU AWS node, no batching | Code Carbon | GPU + CPU + RAM (idle GPUs included) | kWh and g CO₂eq per 1,000 inferences |
| [[Patel 2024 - Splitwise (prefill vs decode phases)|Splitwise]] §III-F | DGX-H100 / A100 | GPU power normalised to TDP | GPU only | power per phase, Wh per request |
| **GroundOne** (thesis) | Apple M4 16 GB, MLX 8-bit, batch 1 | macOS `powermetrics` Combined Power at 200 ms, minus idle (≈0.2 W) measured 60 s with the model loaded | SoC CPU + GPU + ANE; no DRAM, display or SSD | J per verified answer, J per decision |

Rules that follow from these studies: state the scope (which components are counted), subtract or report idle power, and normalise by the unit the user cares about (response, not token, when outputs differ in length).

## What drives the energy
1. **Output length.** Each generated token is another forward pass. Text generation uses 15× more energy than single-token masked LM, and emissions grow with output length, more steeply for decoder-only models (Luccioni §4.1, §4.2.2).
2. **Task structure and output space.** Classification (a softmax over a few classes) costs about 0.002 kWh per 1,000 inferences against about 0.047 kWh for text generation (Luccioni Table 2); task-specific models are orders of magnitude cheaper than multi-purpose generative ones on the same discriminative task (Luccioni §4.2.1).
3. **Phase power differs.** Prefill is compute-bound and its power rises towards TDP with batch size; decode is memory-bound and its power stays flat (Splitwise Insight VI, Fig. 8). Power-capping barely slows decode but slows prefill a lot (Fig. 9).
4. **Hardware and parallelism.** Faster GPUs draw more power (A100 vs V100, Samsi §IV-A); more shards always raise power and energy per token (Samsi §IV-B–C). Capping A100s from 250 to 175 W cut energy by about 22–24% for 6–7% more time (Samsi Table III).
5. **Power vs energy.** Lower power does not mean lower energy if the run lasts longer: LLM in a flash's sparse model drew less power than the dense one but used more energy in total ([[Alizadeh 2024 - LLM in a flash|Alizadeh 2024]] §5.3).

## GroundOne's measurement (100 latency answers, 25 per K band)
| System | Median s/answer | Net J/answer | Net J/decision | Net power |
| --- | --- | --- | --- | --- |
| **GroundOne 0.5B** | 0.34 | **5.5** | 0.63 | 16.2 W |
| Terse judge 0.5B | 0.65 | 8.9 | 1.01 | 13.5 W |
| Verbose judge 0.5B | 1.74 | 22.5 | 2.56 | 11.6 W |
| **GroundOne 3B** | 2.07 | **33.1** | 3.77 | 16.2 W |
| Terse judge 3B | 3.13 | 43.3 | 4.92 | 14.2 W |
| Verbose judge 3B | 10.01 | 111.7 | 12.71 | 10.9 W |

Source: thesis notes, `results/energy-*/energy/metrics.json`.

- GroundOne uses the least energy at both sizes: **1.6× (0.5B) and 1.3× (3B) less than the terse judge**, 4.1× and 3.4× less than the verbose judge.
- **Caveat: speed ≠ energy.** GroundOne is about 2× faster than the terse judge at K ≥ 14, but its energy advantage is smaller, because its single long prefill keeps the GPU busy (16.2 W) while the judges' autoregressive decoding is memory-bound and draws 11–14 W, for longer. This is the Splitwise power characterisation observed on a laptop SoC ([[Prefill and Decode]]). The thesis must not write "N× faster, hence N× less energy".
- In absolute terms, 5.5 J ≈ 0.0015 Wh and 33 J ≈ 0.009 Wh per verified answer.
- **Context, not comparison.** Samsi reports about 3–4 J per *output token* for sharded LLaMA 65B; Luccioni's BLOOMz-560M uses about 194 J per inference (0.054 kWh per 1,000) on an A100 node including idle GPUs. Hardware, scope, model size and task all differ from GroundOne's SoC-only measurement, so these numbers only show orders of magnitude.

## Links
- Concepts: [[Prefill and Decode]], [[On-Device Inference]], [[Apple Silicon and MLX]], [[System One Models]], [[When System One Beats an LLM]], [[GroundOne Results]], [[LLM-as-a-Judge]]
- Sources: [[Samsi 2023 - From Words to Watts]], [[Luccioni 2024 - Power Hungry Processing]], [[Patel 2024 - Splitwise (prefill vs decode phases)]], [[Alizadeh 2024 - LLM in a flash]], [[Apple 2024 - MacBook Pro 14-inch M4 tech specs]]

## Additional sources (ingest 2026-10-11)
- **Phones**: a 13B INT4 model on a Xiaomi 11 (llama.cpp) uses about 56 J/token, about 700 tokens per 3,000 mAh battery ([[Qu 2024 - Mobile Edge Intelligence for LLMs, A Contemporary Survey (arXiv 2407.18921)|Qu 2024]] §IV). For comparison, GroundOne 3B spends 33 J for a whole answer of ≥ 14 sentences without generating any token ([[GroundOne Results]]); different hardware and task, context only.
- **Reporting protocol**: report Wh per query with meter scope and workload description ([[Wang 2025 - Cognitive Edge Computing, Optimizing Large Models and AI Agents (arXiv 2501.03265)|Wang 2025]] §3.5, §6.7; weak preprint). The thesis already states scope (SoC power via powermetrics) and workload (100 latency answers).
- **Power envelopes**: on-device tier under 10 W (Wang 2025); Strix Halo 55 W chip; DGX Spark 140 W chip; Mac Studio up to 480 W; RTX 5090 575 W ([[Local Inference Hardware]]).
- **Generated tokens dominate time on slow decoders**: 2,200 generated tokens take about 38 s on an RTX 5090 and 234 s on a DGX Spark ([[Presenc 2026 - Local LLM tokens-per-second benchmarks]]); a zero-token verifier avoids this term entirely.

## Phones and rules of thumb (ingest 2026-10-11, second batch)
- MELT: Zephyr-3B 4-bit 0.58–0.76 J per generated token on phones; sustained ≈ 13.8 W, surface up to 47.9 °C ([[Laskaridis 2024 - MELTing point, Mobile Evaluation of Language Transformers (arXiv 2403.12844)|Laskaridis 2024]]). GroundOne 3B's 33 J per long answer ≈ 44–57 phone-generated tokens (different hardware; scale only).
- MobileLLM rule of thumb (from prior work): ≈ 0.1 J per generated token per billion parameters ([[Liu 2024 - MobileLLM, Optimizing Sub-billion Parameter Language Models for On-Device Use Cases (arXiv 2402.14905)|Liu 2024]]).
- NPU prefill uses 1.85–4.32× less energy than the phone GPU (Xu 2025); PowerInfer-2: lowest power is not lowest energy (0.257 vs 0.672 J/token at 5.10 vs 4.07 W).
