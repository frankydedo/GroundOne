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

## Third-party on-device measurements of decision models (ingest 2026-10-10)
- **Core AI on an Apple M4 Max (128 GB), int8** ([[mlboydaisuke 2026 - Decision models on Core AI (JevBench public231) dataset card]]). Eight models (six decision models, two chat models) ran fully locally behind a Jev-compatible server on JevBench's 231 public items, one question per request.
  - The Qwen3.5-family decision models prefill one token at a time (S = 1) and **re-prefill the whole state for every question**: a 3k-token state costs **40–220 s per question**. p95 latency over 231 requests: 29 s (decider-0.8b), 93 s (qwen3.5-2b-decision), 142 s (apus-decision-v1-4b, on a GPU shared with two other servers).
  - The fast encoder (laya-multilingual, p50 0.02 s) reads only 256 input tokens, which cut 95 of 111 hard items.
  - Latency was measured on a contended GPU (solo runs about 2× faster); answers were bit-identical solo vs concurrent.
  - Hard-tier accuracy stays below the hosted Jev row (0.559 best local vs 0.730).
- **Laya on Apple MPS** (M5 Max): p50 19.2 ms per decision ([[Nandakishore 2026 - Laya as a Typed Probabilistic Assessor (arXiv 2609.33843)|Nandakishore 2026]]); 42.9 ms in morrenhale's serial probe. The multilingual checkpoint needs about 1.7 s for a 4,000-token input on an Apple GPU (vendor card).
- **What this shows for the thesis.** On-device decision models are feasible, but the dominant cost on long documents is **prefill repeated per question**. GroundOne's design (b) prefills the document once per answer and reads K verdicts at markers in the same pass: 0.41 s (0.5B) / 2.57 s (3B) per answer at K ≥ 14 on a 16 GB M4 ([[GroundOne Results]]). This is evidence for one-pass multi-question scoring, not a benchmark claim: hardware, runtime, documents and models all differ. The alternative of reading a short window of the state, as truncating encoders do, is not acceptable for grounded verification.

## Decision-model ports and runtimes for local use (ingest 2026-10-10, `decision-model` tag)
- **llama.cpp serves decision models natively** since 2026-10-02 (`/v1/systemone` in `llama-server`; Laya, Julia-1, lev, OpenJev, Kev; shared prompt prefix for causal models), with worst-case probability differences of 1.8e-4 to 2.2e-2 against the reference implementations on one test request ([[ggml-org 2026 - llama.cpp PR 29818 systemone API]]).
- **A 9B decision model fits a 16 GB Mac**: Clef-flash in MLX 4-bit peaks at 7.0–8.6 GB (1k–16k tokens) and answers in 0.31 s at 1k tokens and 7.0 s at 16k on an M5 Max, losing about one Decision Index point against bf16 ([[mlx-community 2026 - clef-flash-4bit model card]]). Its RAGTruth score is poor, though (35.6 F1, vendor run).
- **Prefill dominates on device**: Kev-4B on an M5 (MLX) answers three questions about an 8k-token state in 6.6 s when the state is new and 354 ms when it is cached ([[Palmer 2026 - Kev-4B model card]]). Liquid's d1-3B needs 30 ms for one question but 640 ms for a 3.4k-token state on an M5 Pro ([[LiquidAI 2026 - d1-3B model card]]).
- **Neural Engine**: a Core ML port of d1-omni-600M runs 99.1 % of ops on the ANE at about 4.6 ms per short question (M5 Pro), but only up to 256 tokens ([[FluidInference 2026 - d1-omni-600M Core ML model card]]).
- **For the thesis.** The locality pillar is now shared by industry (Liquid's "edge decision models", MLX and Core ML ports within days of release). What remains specific to GroundOne is the long-context, many-decisions case: GroundOne pays one prefill per answer for K sentence verdicts, the regime where these measurements show cost concentrates. Cross-chip numbers (M4 vs M5) are context, not comparisons.

## Open items for the locality pillar (from the thesis plan)
- Offline proof: rerun an evaluation with `HF_HUB_OFFLINE=1` and the network off.
- Memory when co-resident with a generator (training peaks so far: 2.6 GB for 0.5B, 5.9 GB for 3B).
- Licence table and cost comparison against a hosted judge.
- Cross-runtime comparisons are not claimed: [[Rizzo-Flow]] runs on llama.cpp (Q4, 4B, over HTTP), GroundOne in MLX in-process.

## Sources
[[Gunter 2024 - Apple Intelligence Foundation Language Models]], [[Alizadeh 2024 - LLM in a flash]], [[MLX README (ml-explore)]], [[llama.cpp README (ggml-org)]], [[ggml-org 2026 - llama.cpp PR 29818 systemone API]], [[mlx-community 2026 - clef-flash-4bit model card]], [[Palmer 2026 - Kev-4B model card]], [[FluidInference 2026 - d1-omni-600M Core ML model card]], [[Apple 2024 - MacBook Pro 14-inch M4 tech specs]], [[Patel 2024 - Splitwise (prefill vs decode phases)]], [[Luccioni 2024 - Power Hungry Processing]], [[Samsi 2023 - From Words to Watts]]. Related concepts: [[Apple Silicon and MLX]], [[Energy of LLM Inference]], [[Prefill and Decode]], [[KV Cache]], [[Retrieval-Augmented Generation]], [[GroundOne]].

## Local inference landscape (ingest 2026-10-11, local inference sources)
- **Why now.** Open models that fit one consumer GPU reach frontier performance after 6–12 months, and the open/closed gap has narrowed to a few months ([[Open-Weight Models]], [[Epoch AI 2025 - Frontier AI performance becomes accessible on consumer hardware within a year]], [[Stanford HAI 2025 - AI Index Report, Technical performance]]).
- **Hardware.** A comparison of laptops, Mac Studio, DGX Spark, Strix Halo and consumer GPUs on capacity, bandwidth, compute, power and price is in [[Local Inference Hardware]]. The prefill/decode asymmetry appears on every class (EXO: Spark 3.8× faster prefill, M3 Ultra 3.4× faster decode; Apple M5 vs M4: TTFT 3.3–4.1× faster, generation 1.19–1.27×).
- **Privacy** has its own page, with the 2026 Navier–Stokes case as a concrete example of the unverifiability of cloud data handling ([[Privacy and Data Sovereignty]], [[Navier-Stokes Credit Dispute (2026)]]).
- **Small models, quantisation, hybrids**: [[Small Language Models]], [[Quantization]], [[Edge-Cloud Collaborative Inference]] (Qu 2024 argues pure on-device is too limited and favours edge servers: a counter-position to acknowledge).
- **Ecosystem**: llama.cpp → GGUF → Ollama / LM Studio / Jan / GPT4All is the mainstream consumer stack ([[Presenc 2026 - State of the llama.cpp ecosystem]], unsourced adoption numbers). Runtime choice changes decode throughput by up to an order of magnitude on the same Mac ([[Rajesh 2025 - Local LLM inference on Apple Silicon, MLX vs MLC vs Ollama vs llama.cpp (arXiv 2511.05502)|Rajesh 2025]], indicative only).
- **Energy on phones**: a 13B INT4 model in llama.cpp on a Xiaomi 11 uses about 56 J/token, about 700 tokens per 3,000 mAh charge ([[Qu 2024 - Mobile Edge Intelligence for LLMs, A Contemporary Survey (arXiv 2407.18921)|Qu 2024]] §IV); see [[Energy of LLM Inference]].
