---
type: concept
tags: [thesis, project, system-one, rag, groundedness]
updated: 2026-10-10
---
# GroundOne (thesis project)

**GroundOne** is the MSc thesis system: a **specialist [[System One Models|System One]]** that does one thing. For each sentence of a RAG answer it decides whether the retrieved document *supports* it, *contradicts* it or *does not mention* it ([[Groundedness Verification]]). It runs fully on the user's laptop ([[On-Device Inference]]). Results are in [[GroundOne Results]].

## Design (current, 2026-10-10)
- **Task.** One three-way decision per answer sentence. K is the number of sentences, i.e. of decisions per answer. A binary score and strict / lenient error policies are derived from the three probabilities. Sentences without checkable content get no verdict (pysbd segmentation plus a content rule, shared by training and inference).
- **Readout (design b).** A marker " Verdict:" follows every scored sentence. All K verdicts are read in **one forward pass** from the logits of the letters A/B/C, restricted to those three, with the output head applied only at the markers ([[Letter-Token Readout]], [[Prefill and Decode]]). Design (a) is a shared prefix plus one question per sentence ([[KV Cache]]). It remains the fallback, the format of the untrained baseline, and the format of the Jev-compatible API route.
- **Models and training.** [[Qwen2.5]] 0.5B and 3B Instruct, MLX 8-bit, fine-tuned with [[LoRA]] (r16 on all linear layers) on **RAGTruth only** (13,203 answers, 90,795 decisions). The loss is a class-weighted cross-entropy restricted to the three letters, with the prompt never supervised. Data: [[Datasets for GroundOne]].
- **Calibration.** Temperature plus per-class bias fitted on dev ([[Calibration]]). The served label uses one rule: "supported" iff calibrated P(supported) ≥ τ, where τ is fitted on dev (0.90–0.94) ([[Selective Prediction]]).
- **Runtime.** MLX on a 16 GB M4 MacBook Pro ([[Apple Silicon and MLX]]). There is a Python package with a CLI and a local HTTP API: native `/v1/verify` on design (b), and a TypeSafe/[[Jev]]-compatible `/v1/systemone` route, the same contract as [[Rizzo-Flow]].
- **Demo (open).** A local RAG chat with a Qwen2.5-3B generator, where GroundOne colours each sentence.

## Why this task
A System One saves the decode phase ([[Prefill and Decode]]). The advantage grows with:
- the number of decisions over a shared context (K sentences per answer);
- judges that would otherwise write verdicts or rationales;
- the need for calibrated probabilities usable as thresholds;
- small specialised models.

Sentence-level groundedness has all four. See [[When System One Beats an LLM]].

## Comparisons (as run)
| Family | Systems |
| --- | --- |
| Cues that never verify against the document | word overlap; sentence-only classifier |
| Same models, untrained (B1) | Qwen2.5 0.5B / 3B, design (a) readout |
| Generative [[LLM-as-a-Judge]] (same size) | terse (B0a), verbose with rationale (B0b), equal-output judge with verbalised or logit probabilities (B0d) |
| Readout vs generation (B2) | fine-tuned model, verdict = generated token at the markers |
| General-purpose System One (B3) | [[Rizzo-Flow]] 4B Q4 (llama.cpp, HTTP) |
| Encoder fact-checkers (B4) | [[MiniCheck]]-RoBERTa, [[HHEM]]-2.1-open |
| Published only | Qwen2.5-7B zero-shot on [[LLM-AggreFact]] (72.8) |
| Related work only | [[Jev]] (closed), [[CLM]] (CUDA-only), [[SemIf]], [[AlignScore]] |

- **Tests**, built and frozen before training:
  - T1: [[RAGTruth]] test, three-way;
  - T2: [[LLM-AggreFact]], binary, evaluation only;
  - T3: [[VitaminC]], three-way, a different domain.
- **Metrics:**
  - three-way balanced accuracy, binary AUROC;
  - [[Expected Calibration Error]], Brier, AURC;
  - latency vs K, energy per answer;
  - [[Statistical Significance and Bootstrap|cluster-bootstrap intervals]].

## Timeline
New experiments until 2026-10-30; submission 2026-11-10.

## Source of truth
`Project/docs/checkpoint_2026-10-10.md` (current summary), `Project/docs/implementation_plan.md` (decision log D1–D27) and `Project/docs/thesis_notes.md`. This page is a summary and may lag behind them.
