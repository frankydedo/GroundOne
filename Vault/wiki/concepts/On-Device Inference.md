---
type: concept
tags: [concept, on-device, local-inference, privacy, runtimes, llama-cpp, mlx, apple-silicon, groundone, locality-pillar]
---
# On-Device Inference

**On-device (local) inference** runs a model on the user's own hardware, as opposed to **remote (hosted) inference**, where inputs are sent to a provider's API and processed in a datacenter. Full locality is one of the pillars of the thesis: [[GroundOne]] is trained, calibrated, evaluated and served on one consumer laptop (Apple M4, 16 GB), with no call to any external service; the network is used only once, to download public datasets and open weights.

## Local vs remote: the trade-off
| Axis | Local (on-device) | Remote (hosted API) |
| --- | --- | --- |
| Privacy, data sovereignty | documents never leave the device (GDPR, confidential corpora) | inputs sent to a third party |
| Availability | works offline | needs network and provider uptime |
| Latency | no network round trip, but limited compute and memory bandwidth | network round trip, fast datacenter accelerators, possible queueing |
| Cost | one-off hardware plus energy | per-token pricing; rate limits |
| Control, reproducibility | fixed weights and versions | silent model updates and deprecations |
| Capability | small models (memory-bound) | frontier models |
| Logit access | full (needed for a [[System One Models|System One]] readout and calibration) | often none: closed APIs expose no or limited token log-probs ([[Es 2024 - RAGAS|RAGAS]] §1–2; Tian et al. had to estimate "label probabilities" from samples, [[Tian 2023 - Just Ask for Calibration]]) |

**Hybrid set-ups** exist: Apple pairs a ~3B on-device model with a larger server model on Private Cloud Compute ([[Gunter 2024 - Apple Intelligence Foundation Language Models|Gunter 2024]] §1). The thesis takes the strict position: the whole verification pipeline stays local.

## The binding constraints on a laptop
1. **Memory capacity decides which model fits.** A 7B model needs over 14 GB in half precision, beyond most personal devices ([[Alizadeh 2024 - LLM in a flash|Alizadeh 2024]] §1). Options: quantise (8-bit, 4-bit, ~3.7 bpw in Apple's on-device model), pick smaller models, or stream weights from flash (LLM in a flash runs models up to 2× DRAM, at a large per-token cost).
2. **Memory bandwidth decides decode speed.** At batch 1 every generated token reads all weights; on the 120 GB/s M4 this bounds decode at about 4 ms/token (0.5B, 8-bit) and 27 ms/token (3B) ([[Apple Silicon and MLX]], [[Prefill and Decode]]).
3. **Compute decides prefill speed**, which is high on GPUs even in laptops: the M4 prefills about 2.8–3k tokens/s on the 0.5B.
4. **Co-residence.** A local RAG assistant must hold generator, verifier, retriever, KV caches and the OS in the same unified memory ([[Retrieval-Augmented Generation]]).
5. **Energy and battery** ([[Energy of LLM Inference]]).

## Evolution of local runtimes and models
- **llama.cpp / ggml** ([[llama.cpp README (ggml-org)]]): dependency-free C/C++ inference, 1.5–8-bit integer quantisation (GGUF), Metal, CUDA, Vulkan and many other backends, CPU+GPU hybrid offload, an OpenAI-compatible server. Distribution layers such as Ollama and LM Studio build on this ecosystem (not ingested as sources).
- **MLX** ([[MLX README (ml-explore)]], Hannun et al. 2023): Apple's array framework for Apple silicon with a unified memory model, lazy evaluation and NumPy/PyTorch-like APIs; `mlx-lm` adds LLM generation, quantisation and LoRA fine-tuning. GroundOne's runtime.
- **Platform vendors' on-device models**: Apple Intelligence's AFM-on-device (~3B, GQA with 8 KV heads, <4 bpw palettisation on the Neural Engine, runtime-swappable rank-16 LoRA adapters; [[Gunter 2024 - Apple Intelligence Foundation Language Models|Gunter 2024]] §2, §5).
- **Memory-limited inference research**: flash offloading with windowing and row-column bundling ([[Alizadeh 2024 - LLM in a flash]]).
- **Small open models**: [[Qwen2.5]] 0.5B–7B and similar families make specialised local models practical; [[LoRA]] / [[Dettmers 2023 - QLoRA|QLoRA]] make fine-tuning them feasible on consumer hardware.

## Why locality and System One fit together (the thesis argument)
- Local hardware is weakest exactly at **autoregressive decoding** (bandwidth-bound) and comparatively strong at **prefill** (compute-bound). A System One avoids decoding entirely, so its advantage is largest where inference is local. This turns locality from a constraint into the reason the design matters ([[Prefill and Decode]], [[When System One Beats an LLM]]).
- Measured on the M4 (MLX, in-process): at K ≥ 14 sentences GroundOne needs **0.41 s (0.5B) / 2.57 s (3B)** per answer, about **2× faster than a terse** and **6× faster than a verbose** generative judge of the same size; energy per verified answer is **5.5 J / 33 J**, 1.3–1.6× less than the terse judge ([[GroundOne Results]], [[Energy of LLM Inference]]).
- The recipe matches the industrial pattern for on-device language features: a small quantised base model plus a task-specific LoRA adapter on all linear layers (Apple: ~3B, rank 16; GroundOne: Qwen2.5 0.5B/3B, 8-bit, r16) ([[Gunter 2024 - Apple Intelligence Foundation Language Models]]).
- A local System One also keeps **full logit access**, which a hosted judge usually does not offer; GroundOne's calibration and served threshold depend on it ([[Calibration]]).

## Open items for the locality pillar (from the thesis plan)
- Offline proof: rerun an evaluation with `HF_HUB_OFFLINE=1` and the network off.
- Memory when co-resident with a generator (training peaks so far: 2.6 GB for 0.5B, 5.9 GB for 3B).
- Licence table and cost comparison against a hosted judge.
- Cross-runtime comparisons are not claimed: [[Rizzo-Flow]] runs on llama.cpp (Q4, 4B, over HTTP), GroundOne in MLX in-process.

## Sources
[[Gunter 2024 - Apple Intelligence Foundation Language Models]], [[Alizadeh 2024 - LLM in a flash]], [[MLX README (ml-explore)]], [[llama.cpp README (ggml-org)]], [[Apple 2024 - MacBook Pro 14-inch M4 tech specs]], [[Patel 2024 - Splitwise (prefill vs decode phases)]], [[Luccioni 2024 - Power Hungry Processing]], [[Samsi 2023 - From Words to Watts]]. Related concepts: [[Apple Silicon and MLX]], [[Energy of LLM Inference]], [[Prefill and Decode]], [[KV Cache]], [[Retrieval-Augmented Generation]], [[GroundOne]].
