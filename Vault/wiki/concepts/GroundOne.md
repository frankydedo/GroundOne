---
type: concept
tags: [thesis, project, system-one, rag, groundedness]
---
# GroundOne (thesis project)

**GroundOne** (working name) is the MSc thesis system: a **specialist [[System One Models|System One]]** that does one thing, which is deciding whether each sentence of a RAG answer is supported by the retrieved context ([[Groundedness Verification]]).

## Design in one paragraph
- **Models and training:** [[Qwen2.5]] 0.5B and 3B, fine-tuned with [[LoRA]] on public human-labelled faithfulness and NLI data ([[Natural Language Inference]], [[RAGTruth]]). The loss is cross-entropy on the restricted logits of two answer letters (`A` = supported, `B` = not supported), with the prompt masked.
- **Inference:** context and answer are prefilled **once** into the [[KV Cache]]. Each sentence is scored by a short suffix. `P(supported)` is read from the logits and temperature-calibrated ([[Calibration]]).
- **Runtime:** MLX on a 16 GB M4 MacBook Pro.
- **Demo:** a local RAG chat with a Qwen2.5-3B generator. GroundOne colours each answer sentence by its probability.

## Why this task (and not tool routing)
A System One saves only the decode phase ([[Prefill and Decode]]). For a single short decision (K = 1), an LLM that emits one letter costs the same. The advantage appears with:
- **many questions over a shared context:** K sentences per answer;
- **judges that would otherwise write a verdict or a rationale;**
- **calibrated probabilities**, usable as thresholds;
- **smaller specialised models.**

Sentence-level groundedness has all four. See [[When System One Beats an LLM]].

## Comparisons
| Family | Systems |
| --- | --- |
| Generative [[LLM-as-a-Judge]] | Qwen2.5 0.5B/3B (terse and rationale), 7B zero-shot |
| Same model, single-token readout | without fine-tuning (ablation A1); single-token generation control (A2) |
| General-purpose System One | [[Rizzo-Flow]] |
| Encoder fact-checkers | [[MiniCheck]], [[HHEM]], [[AlignScore]] |
| Related work only | [[Jev]] (closed), [[CLM]] (CUDA-only), [[SemIf]] |

Benchmarks: [[LLM-AggreFact]], [[RAGTruth]]. Metrics: balanced accuracy, AUROC, [[Expected Calibration Error]], [[Selective Prediction]], latency p50/p90/p99, memory.

## Timeline
New experiments until 2026-10-30; submission 2026-11-10.

## Source of truth
`Project/docs/implementation_plan.md` and `Project/docs/abstract.md`. This page is a summary and may lag behind them.
