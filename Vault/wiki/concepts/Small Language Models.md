---
type: concept
tags: [concept, small-language-models, slm, on-device, specialisation, lora, qwen]
---
# Small Language Models

Language models small enough to run on personal devices. Definitions disagree: the main measurement survey defines SLMs as decoder-only models of **100M–5B parameters** ([[Lu 2024 - Small Language Models, Survey, Measurements, and Insights (arXiv 2409.15790)|Lu 2024]]); other surveys use different bounds ([[Li 2025 - Collaborative Inference between Edge SLMs and Cloud LLMs, A Survey (arXiv 2507.16731)|Li 2025]] is internally inconsistent). Wang 2025 places on-device models at 1–3B and under 10 W. GroundOne's Qwen2.5 0.5B and 3B sit inside every definition.

## Key facts
- **Over-trained by design**: small models are trained far past the Chinchilla optimum (e.g. Qwen2-0.5B on 12T tokens) (Lu 2024).
- **Capability per parameter keeps rising**: smallest model above 60 % MMLU went from 540B to 3.8B parameters in two years ([[Stanford HAI 2025 - AI Index Report, Technical performance]]); see [[Open-Weight Models]].
- **On-device cost** (Lu 2024, llama.cpp 4-bit on Jetson and phones): prefill is compute-bound and sensitive to architecture; decode is memory-bound and grows linearly with size; memory 275–2,456 MB for 0.1B–3B models; at long context the KV cache and compute buffer take 83–90 % of memory ([[Prefill and Decode]], [[KV Cache]]).
- **Specialisation**: SLMs fine-tuned with LoRA "can approximate LLM outputs in narrow domains while maintaining low latency and data locality" (Li 2025 §1.3.2). Apple's on-device model is the industrial example (~3B with per-feature LoRA adapters; [[Gunter 2024 - Apple Intelligence Foundation Language Models]]).
- **Prior collapse on skewed tasks**: on BoolQ a small model keeps 71 % accuracy with only 52.6 % balanced accuracy because it answers "yes" on 97 of 100 items ([[Das 2026 - Large Models for Small Devices, Edge AI Deployment (arXiv 2608.15693)|Das 2026]] §6.2). This supports reporting balanced decisions, as GroundOne does ([[GroundOne Results]]).
- **Vendor on-device models**: Gemma 3n, 5B/8B raw parameters with a claimed 2/3 GB "dynamic footprint" ([[Google 2025 - Introducing Gemma 3n]], vendor claim).

## Relevance to GroundOne
- GroundOne is the thesis's answer to "what can an SLM do if it is specialised in one decision": the untrained 0.5B/3B score 0.37/0.44 three-way balanced accuracy on RAGTruth, the fine-tuned ones 0.769/0.832 ([[GroundOne Results]]).
- Small general-purpose decision models (< 1B) barely beat chance on response-level RAGTruth in the Decision Index ([[Decision-Model Landscape (Hugging Face, 2026)]]), which is the gap specialisation fills.
- Caution: the surveys' "System 1 / System 2" vocabulary (FS-GEN in Li 2025: small model = System 1, LLM = System 2) is a different use of the term from [[System One Models]].

## Links
- Concepts: [[Qwen2.5]], [[LoRA]], [[On-Device Inference]], [[Open-Weight Models]], [[Quantization]], [[Edge-Cloud Collaborative Inference]], [[Local Inference Hardware]]

## MobileLLM (ingest 2026-10-11, second batch)
- Phone guidance: an app should use ≤ 10 % of DRAM; a 350M model designed for depth (SwiGLU, embedding sharing, GQA) matches LLaMA-2 7B on API-calling exact match ([[Liu 2024 - MobileLLM, Optimizing Sub-billion Parameter Language Models for On-Device Use Cases (arXiv 2402.14905)|Liu 2024]]). Qwen2.5-0.5B already follows that recipe. The 10 % rule applied to a 16 GB laptop (1.6 GB: the 0.5B fits, the 3B does not) is an extrapolation.

## As repairers (ingest 2026-10-18)
- In Self-Refine, Vicuna-13B could not refine its output even with oracle feedback ([[Madaan 2023 - Self-Refine, Iterative Refinement with Self-Feedback (arXiv 2303.17651)]]): a risk for the 3B generator in the demo's repair loop ([[Demo Application]]). Conversely, CRAG's 0.77B evaluator judges retrieval better than ChatGPT, a further case of a small specialist beating a generalist.
