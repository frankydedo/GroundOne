---
type: concept
tags: [concept, demo, application, swift, swiftui, mlx-swift, rag, groundone, architecture, locality-pillar]
---
# Demo Application

The GroundOne demo: a native macOS app in which retrieval, generation and GroundOne verification run in one process on the 16 GB laptop, and the verifier decides what the user sees. Decided on 2026-10-18 (D28); specification in `Project/docs/demo_architecture.md` (v0.1 draft, open questions in its §12). App name not decided yet (candidates: Ancora, G1RAG, GroundOne Studio, Vaglio, Riscontro).

## What it shows
- Every answer sentence coloured by its verdict, calibrated probabilities on hover (served rule D27).
- Flagged sentences rewritten from the document and re-verified, up to a policy limit ([[Verify-and-Revise Loops]]).
- A timing and memory panel (generation vs verification time, rounds, peak memory): the co-residence measurement of the locality pillar.
- Optional comparison with a terse generative judge on the same answer ([[LLM-as-a-Judge]]).

## Architecture
- **UI** (SwiftUI): chat, document library, policy editor, measurement panel.
- **Core** (pure Swift, no ML imports): orchestrator, verify-and-revise loop, policy engine, audit log; testable with fake engines.
- **Protocols** `Retriever`, `Generator`, `Verifier`; **engines** behind them: SQLite FTS5 and optional embeddings ([[Local RAG Retrieval]]), Qwen2.5-3B-Instruct generator and the GroundOne verifier on MLX Swift ([[MLX Ecosystem]]). A llama.cpp engine could replace MLX later without touching Core.
- **One inference actor** for all MLX calls, as the single MLX worker thread in the Python engine.

## Porting GroundOne
- Reused unchanged: the 8-bit base weights, `adapters.safetensors` + `adapter_config.json` (mlx-lm format, loaded by `LoRAContainer`), `calibration.json` ([[ml-explore 2026 - mlx-swift-lm LoRA adapters reference]]).
- Ported: the marked prompt (with its piecewise tokenisation), the segmentation rule (pysbd per line + checkable-content rule; no Swift pysbd), and the readout (hidden states from the public `Qwen2Model.model`, head applied only at the markers) ([[ml-explore 2026 - mlx-swift-lm Qwen2 model source]], [[Letter-Token Readout]]).
- **Conformance test** (the gate): Python exports fixtures from frozen T1 answers; Swift must reproduce token ids and marker positions exactly, calibrated probabilities within 0.01 and the served labels. If it passes, the thesis results hold for the app with no retraining or recalibration.

## Memory (16 GB)
GroundOne 3B 3.28 GB + adapter 0.12 GB; a 4-bit 3B generator ≈ 1.8 GB (estimate); KV caches ≈ 36 KB per token for the 3B. Alternative: one shared 8-bit base for generator and verifier, switching the adapter with `load`/`unload` (saves ≈ 1.8 GB, decodes at the 8-bit floor) ([[Local Inference Hardware]], [[KV Cache]]).

## Honest limits
- Apple-only UI ([[Demo Runtime Choice]]).
- The loop is driven by GroundOne, so it inherits its errors; the demo measures cost and behaviour, not a faithfulness gain, unless an independent check is added.
- A small generator may fail to repair (Self-Refine's Vicuna result).

## Links
- [[GroundOne]], [[Demo Runtime Choice]], [[MLX Ecosystem]], [[Local RAG Retrieval]], [[Verify-and-Revise Loops]], [[Guardrails and Policies]], [[On-Device Inference]], [[Privacy and Data Sovereignty]]
