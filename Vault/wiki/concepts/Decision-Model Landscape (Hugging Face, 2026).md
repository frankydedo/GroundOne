---
type: concept
tags: [hugging-face, decision-models, system-one, ecosystem, survey, evidence-quality, on-device, hallucination-detection, synthesis]
updated: 2026-10-10
---
# Decision-Model Landscape (Hugging Face, 2026)

A survey of the open [[System One Models|decision models]] published on the Hugging Face Hub in September–October 2026, built from the full listing of the `decision-model` tag ([[Hugging Face 2026 - decision-model tag listing (2026-10-10)]]) and from the cards, code and papers ingested on 2026-10-10. It extends [[Hugging Face decision-models Tag]] (the plural tag, ingested earlier the same day) and feeds [[Decision-Model Benchmarks]].

## The tag and its size
- **The big tag is the singular `decision-model`**: 1,529 models from 610 authors on 2026-10-10 (web: `huggingface.co/models?other=decision-model`; API: `api/models?filter=decision-model`). The plural `decision-models` covers mostly datasets and a few models ([[Hugging Face decision-models Tag]]).
- **Almost all of it is five weeks old**: 862 models created in September 2026 and 665 in the first ten days of October, after [[Jev]]'s release. The [[multimodalart 2026 - Jev Decision Index (Hugging Face Space)|Decision Index]] Space, created 2026-09-17, is the de facto leaderboard.
- **Composition** (library field): transformers 392, none declared 344, peft 221 (LoRA adapters), mlx 150, gguf 83, laya 54 (Laya fine-tunes), onnx 42, pytorch 38, jevify 29, coreml 18, transformers.js 16, llama.cpp 15, coreai 14. Pipelines: text-classification 686, image-text-to-text 130, zero-shot-classification 127, text-generation 110.
- **Backbones**: Qwen dominates (460 direct base-model tags; Qwen3.5-4B alone 102), then Laya checkpoints (109), Gemma 4 (68), ModernBERT/mmBERT/Ettin encoders (63), LiquidAI (30).
- **Naming**: 304 model ids contain "jev" and 146 "laya"; Apache-2.0 on 1,186 models.

## Main families
| Family (readout) | How the decision is read | Representative models | Notes |
|---|---|---|---|
| **(a) Decoder + trained joint/pointer head over a shared prefill** | Backbone runs once over state + all questions; a trained head scores option spans or option tokens | Cloudflare **Clef** (joint schema head, all questions jointly); **Kev** (pointer head, state cached, one row per question); Drex DLM (bidirectional state, causal question branches, pointer head; card) | Clef is the first open implementation of the design only inferred for Jev ([[Cloudflare 2026 - Clef model card]], [[Palmer 2026 - Kev-4B model card]]) |
| **(b) Restricted letter readout** (LM head or a head initialised on letter rows) | Options rendered with single-token codes; softmax over their logits at the answer slot | Liquid **d1-3B** (tree-attention shared state); **pplx-decider** (255-row letter head, noncausal attention); Quyet, torchcast, Together **Tev1** (plain LM head, "not a non-autoregressive Jev runtime"); GroundOne | The strongest open family on the leaderboards; GroundOne's family ([[LiquidAI 2026 - d1-3B model card]], [[Perplexity 2026 - pplx-decider-v1.1-27b model card]], [[Letter-Token Readout]]) |
| **(b') Decoder + LoRA + small readout head** | LoRA-adapted decoder, a small head scores options per question | Strands decider (2B), Vela 2.0 decoders, uratori-ja (`<opt>` token head), Bespoke-Nimble-9B-v3 (LoRA; card gives only the Index score) | Closest recipes to GroundOne's scale ([[Strands Agents (Amazon) 2026 - strands-decider-2B-qwen3.5-v1 model card]], [[tokimoa 2026 - uratori-ja-4b model card]]) |
| **(d) Encoder + per-option markers** | Bidirectional encoder; one marker per option, softmax over markers | [[Laya]], Von, Julia-1, d1-omni-600M, Vela 2.0 0.3B, Dev-0.4b, MIMIR-1, GLiNER2.5-Decide (GLiNER2 schema encoder) | Fast and small, weak zero-shot on hard and grounding tasks ([[FluidInference 2026 - d1-omni-600M Core ML model card]]) |
| **Distilled Jev students** | Decoder + LoRA trained on Jev 1.13 output distributions | autotrust JEV-9B / JEV-27B / JEV-27B-VL, GEV-26B-Decide | See red flags |
| **Span outputs** | Word-by-label span head next to the decision head | Vela 2.0 (PII and unsupported-claim spans) | The only family built for hallucination spans ([[KR Labs and vLLM Semantic Router 2026 - Vela 2.0 9B model card]]) |
| Diffusion "Jev mode" | Masked-diffusion LM read as a classifier | DiffusionGemma-based entrants on the Index, Drex DLM (name only) | Covered by family (e) in [[System One Models]] |

## Catalogue of notable models examined
Evidence quality: **A** = code, configs or data manifests released and numbers with intervals or independent reruns; **B** = substantive card with numbers, vendor-measured; **C** = thin card or marketing-heavy. Relevance is to [[GroundOne]].

| Model | Org | Size / backbone | Readout | Decides | Evidence | Relevance |
|---|---|---|---|---|---|---|
| Cloudflare/clef, clef-flash, clef-omni | Cloudflare | 27B Qwen3.8; 9B Qwen3.5; 30B-A3B Qwen3-Omni | joint schema head, one prefill | general typed decisions, multimodal | A (code) / B (numbers vendor-run) | **High**: RAGTruth 79.4 vs Jev 76.5 (vendor run); clef-flash 35.6 |
| LiquidAI/d1-3B, d1-omni-600M | Liquid AI | 3.1B LFM2.5-VL; 587M LFM2.5 encoder | letter readout + tree-shared state; marker encoder | general, vision, audio | A (code) / B | **High**: GroundOne's family at GroundOne's size; M5 Pro latencies |
| perplexity-ai/pplx-decider-v1.1-27b | Perplexity | 27B Qwen3.8, full FT | 255-row letter head, noncausal attention | general, images | A (config + data manifest) | High: v1 tops Index RAGTruth (0.803); trains on VitaminC and WiCE |
| StrandsAgents (= amazon) strands-decider-2B-qwen3.5-v1 | Strands Agents | 2B Qwen3.5-Base + LoRA | small readout head | agent decisions | A (repo, seeds, eval files) | High: seed soup, per-primitive calibration |
| vllm-sr/Vela-2.0 (0.3B–9B) | KR Labs + vLLM Semantic Router | 9B Qwen3.5 hybrid; 0.3B ModernBERT | decision heads + span heads | routing, safety, PII, **unsupported spans** | A− (intervals, selection disclosures) | **High**: RAGTruth example-F1 0.774 (9B) |
| vllm-sr/Decision-2.0 (Eos 0.8B … Vega 27B), d3 | vLLM Semantic Router | 0.6B–29B | "answered together in one forward pass" (2.0); "each from its own forward pass" (d3) | general | C (thin cards, JevArena/Index only) | Low |
| jaredpalmer/kev (0.5B–27B) | individual | 4B Qwen3.5-Base frozen + LoRA | pointer head, cached state | general, long documents | A | High: MLX numbers on an M5; design (a) |
| tokimoa/uratori-ja (0.31B–9B) | individual | 4B Qwen3.5 + LoRA | `<opt>` head | **grounding, RAG faithfulness** (Japanese) | B (self-built eval) | Medium-high: same 3 labels; size ladder |
| fastino/GLiNER2.5-Decide (+ multi, 1B) | Fastino | 340M GLiNER2 encoder | schema encoder | intent, routing, NER | B (paper arXiv 2507.18546 is the 2025 GLiNER2 system) | Low: Index RAGTruth 0.253 |
| togethercomputer/Tev1-4B / 0.8B-experimental | Together AI | Qwen3.5 SFT | generated option letter via LM head | general | B− | Low: Index RAGTruth 0.503 / 0.183 |
| ggml-org/Bespoke-Nimble-9B-v3-GGUF (base bespokelabs/Bespoke-Nimble-9B-v3) | Bespoke Labs (makers of Bespoke-MiniCheck) | 9B Qwen3.5 + LoRA | not described | general | C (one-line card; Index 56.88) | Low: no groundedness numbers despite the MiniCheck lineage; CC BY-NC |
| nace-ai/drex-v1.5, drex-dlm | Nace.AI | 9B Qwen3.5 | pointer head; DLM: bidirectional state + causal branches | general | B (card) | Medium: one-pass multi-question variant; tested on Apple M5 |
| Mapika/decider (0.8B–35B-A3B) | individual | Qwen3.5-Base | one pass, CE then calibration-aware RL | general, agents | B | Low (Index Decider 2B 28.97; RAGTruth 0.284) |
| openjev/openjev, interfaze-ai/lev, wfzyx/von, SupersonicLabs/Julia-1 | various | 4B decoders / 144–395M encoders | first-position option scores / LoRA readout / option markers | general | B | Low: Index RAGTruth lev 0.083, Julia 1 0.520 |
| autotrust JEV-9B, JEV-27B(-VL), GEV-26B-Decide | AutoTrust | 9B–27B Qwen / Gemma + LoRA | distilled from Jev 1.13 distributions | general | C (marketing; teacher-relative metrics) | Low; see red flags |
| lighteternal/biodecision-tev1-4b, cortex-agent-llc/kodiak, ricardocs99/attributed-decision-decider, hiepho/viya-base | individuals | 0.4–4B | various | biomedical judging; guardrails; quote-then-decide contracts; Vietnamese fact-checking | B− (cards) | Low-medium: tagged hallucination-detection or fact-checking, no RAGTruth/LLM-AggreFact numbers |

## Groundedness and hallucination models
- **Only 11 models carry the `hallucination-detection` tag** (Vela 2.0 sizes, Kodiak versions, BioDecision); a few more are tagged `fact-verification` or `rag` (uratori-ja, viya, decide-0.5b, attributed-decision-decider).
- **Substantive ones**: Vela 2.0 (span-level unsupported claims; RAGTruth example-F1 0.774 for 9B, 0.706 for 0.3B; still below the 2B generative LettuceDetect, 0.817) and uratori-ja (Japanese supported / contradicted / insufficient; 0.686 → 0.897 from 0.31B to 9B on its own set).
- **The Decision Index measures RAGTruth at response level for 70 entrants**: no entrant under 1B exceeds 0.553 F1 (chance 0.518); 31 of 70 are at or below chance; all 16 entrants of 15B or more exceed 0.6 ([[multimodalart 2026 - Jev Decision Index (Hugging Face Space)]]).
- **General decision models are not grounding checkers.** Kev 4B 0.330, GLiNER2.5-Decide 0.253, Laya 0.488 and Clef-flash 35.6 on RAGTruth, despite good intent and tool scores.
- No model in the tag reports sentence-level, three-way groundedness on RAGTruth, LLM-AggreFact or VitaminC, the setting of GroundOne.

## On-device ports
- **MLX**: 163 models tagged `mlx`. mlx-community converts Clef (4/8-bit and OptiQ mixed precision); clef-flash-4bit runs on a 16 GB Mac with a 7.0–8.6 GB peak and loses about 1 Index point vs bf16 ([[mlx-community 2026 - clef-flash-4bit model card]]). Kev serves through MLX on Apple Silicon automatically ([[Palmer 2026 - Kev-4B model card]]). Other MLX ports: laya-mlx (63/63 argmax parity with PyTorch on an M3 Max, card), Manchego-MLX, uratori-ja MLX.
- **Core ML / Neural Engine**: FluidInference ports (Laya, GLiNER2.5-Decide, d1-omni, Clef-flash text-only, Verdict); d1-omni runs 99.1 % of ops on the ANE, about 4.6 ms per short question on an M5 Pro ([[FluidInference 2026 - d1-omni-600M Core ML model card]]). mlboydaisuke's Core AI bundles are covered in [[mlboydaisuke 2026 - Decision models on Core AI (JevBench public231) dataset card]].
- **GGUF / llama.cpp**: llama.cpp merged a native `/v1/systemone` server on 2026-10-02 (Laya, Julia-1, lev, OpenJev, Kev; shared prompt prefix for causal models) ([[ggml-org 2026 - llama.cpp PR 29818 systemone API]]); ggml-org, bartowski and mradermacher publish GGUFs (322 models tagged `gguf`).
- **Browser**: onnx-community transformers.js/WebGPU exports (36 models tagged `webgpu`).
- **Edge latency claims from established vendors**: d1-3B 30 ms per question on an Apple M5 Pro, 640 ms for a 3.4k-token state ([[LiquidAI 2026 - d1-3B model card]]).

## What the landscape changes in the definition of "System One / decision model"
1. **"One forward pass" now has at least four implementations**: one prefill over state + all questions with a joint head (Clef); a shared trunk with one branch per question in a single tree-masked pass (d1-3B); a cached state plus one row per question (Kev, GroundOne design a); one sequence per question (Laya, pplx-decider, Tev1). GroundOne's design (b), K verdicts at K markers in one linear sequence, is a fifth, task-specific variant ([[System One Models]]).
2. **"No generation" is not universal.** Together's Tev1 and unlimitedpipe's decide-0.5b keep the LM head and read the first generated token. llama.cpp's maintainers describe decision models as "embedding models plus a head".
3. **Calibration is trained or fitted, never intrinsic.** Clef adds a Brier loss; Strands fits one temperature per primitive and warns to re-measure on one's own traffic; Kev fits one temperature and shows ECE varying from 0.017 to 0.101 across suites; Jev itself is calibrated pooled but not per benchmark ([[Guo 2026 - Just Ask Jev (arXiv 2609.29429)]]); RLCD gives no advantage over cross-entropy once temperature-scaled ([[Deka 2026 - From Retrieval to Typed Decisions SBERT2S1 (arXiv 2610.02486)]]).
4. **Established organisations entered within three weeks of Jev**: Cloudflare, Liquid AI, Perplexity, Strands Agents (Amazon), Together AI, Fastino, vLLM Semantic Router with KR Labs, Bespoke Labs. Their open weights make the "closed vs open" contrast of [[Jev]] obsolete for general decisions; the open question is task specialisation.

## Red flags
- **Inflated popularity.** The top three models hold 54 % of all likes (7,980 of 14,912) and the top three by downloads, all from one uploader (autotrust), 60 % of all downloads (2.79M of 4.68M), all three uploaded between 2026-09-23 and 2026-10-02; the median model has zero likes. Popularity says nothing about quality.
- **Trademark-adjacent names and distillation.** autotrust's "JEV" models are trained on Jev 1.13 output distributions (the JEV-9B card counts 25,376 of 29,955 test targets as Jev distributions) and report agreement with the teacher (KL ≈ 0.019) and an ECE of 0.0007, both from the card's "agreement with the TypeSafe Jev 1.13 teacher" evaluation on its own distillation test set; the cards disclaim affiliation with TypeSafe. Treat such numbers as fidelity to Jev, not accuracy.
- **Self-built, LLM-written evaluation sets** (uratori-ja-eval, Kev's suites, many "typed-decisions" claims) and train/test overlap with public benchmarks (pplx-decider and Strands train on VitaminC; Vela's 0.3B used test results in release selection, disclosed).
- **Vendor-run leaderboard numbers.** Clef's and d1's Decision Index figures are internal runs with the official kit, not board entries; Cloudflare's results table is also its blog's marketing table.
- **Thin cards from known names.** Bespoke-Nimble-9B-v3 gives one number; Decision 2.0 cards give JevArena and the Index only.
- **Re-uploads and quantisations inflate the count**: mradermacher alone has 63 quantisation repositories; 322 models are tagged `gguf`.

## Links
- Sources: [[Hugging Face 2026 - decision-model tag listing (2026-10-10)]], [[Cloudflare 2026 - Clef model card]], [[LiquidAI 2026 - d1-3B model card]], [[Perplexity 2026 - pplx-decider-v1.1-27b model card]], [[KR Labs and vLLM Semantic Router 2026 - Vela 2.0 9B model card]], [[Strands Agents (Amazon) 2026 - strands-decider-2B-qwen3.5-v1 model card]], [[Palmer 2026 - Kev-4B model card]], [[tokimoa 2026 - uratori-ja-4b model card]], [[multimodalart 2026 - Jev Decision Index (Hugging Face Space)]], [[ggml-org 2026 - llama.cpp PR 29818 systemone API]], [[mlx-community 2026 - clef-flash-4bit model card]], [[FluidInference 2026 - d1-omni-600M Core ML model card]], [[Li 2026 - JEV-as-a-Judge (arXiv 2609.26550)]], [[Guo 2026 - Just Ask Jev (arXiv 2609.29429)]], [[Deka 2026 - From Retrieval to Typed Decisions SBERT2S1 (arXiv 2610.02486)]]
- Concepts: [[Hugging Face decision-models Tag]], [[System One Models]], [[Decision-Model Benchmarks]], [[Laya]], [[Jev]], [[Hallucination Detection]], [[Groundedness Verification]], [[On-Device Inference]], [[Apple Silicon and MLX]], [[GroundOne]]
