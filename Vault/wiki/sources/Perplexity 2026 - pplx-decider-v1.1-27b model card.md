---
type: source
author: "Perplexity AI"
date: 2026
venue: "Hugging Face model card perplexity-ai/pplx-decider-v1.1-27b, revision 6195aa5 (retrieved 2026-10-10), with decision_config.json, training/config.json and training/data-manifest.json"
url: "https://huggingface.co/perplexity-ai/pplx-decider-v1.1-27b"
tags: [source, model-card, system-one, decision-models, established-org, letter-readout, noncausal-attention, tasksource, contamination, pplx-decider]
---
# Perplexity 2026 – pplx-decider-v1.1-27b model card

**Raw file**: `raw/Perplexity 2026 - pplx-decider-v1.1-27b model card_ingested.md`
**Supplementary raw files** (unchanged JSON from the same revision): `raw/Perplexity 2026 - pplx-decider-v1.1-27b decision_config_ingested.json`, `raw/Perplexity 2026 - pplx-decider-v1.1-27b training config_ingested.json`, `raw/Perplexity 2026 - pplx-decider-v1.1-27b training data-manifest_ingested.json`

## Overview
Perplexity's open-weight (Apache-2.0) decision model, an update of `pplx-decider-v1-27b` on the same Qwen3.8-27B backbone. The card is short; the repository ships the training code (`autojev`), the training config, a data manifest with per-source row counts, a release manifest and the evaluation JSON, which makes it one of the best-documented large entrants.

## Key Insights
1. **Readout.** A `Qwen3_5Model` backbone plus `readout.safetensors`, a BF16 `[255, 5120]` decision head. `decision_config.json` maps the 255 rows to the token ids of option codes A..Z, AA, AB, … ("This artifact has a separate readout, not a full-vocabulary `lm_head`"; a serving export must map readout row *i* into vocabulary row `token_ids[i]`). Pooling is the **last** token; a calibration temperature (1.0087) is applied once by `DecisionModel.predict`, and logits must be normalised over the valid candidates of each decision. This is a **restricted letter readout** (family b) whose rows are trained separately from the LM head ([[Letter-Token Readout]]).
2. **Lifting the causal mask.** The card attributes most of the gain over v1 to "the lifting of the causal mask and training on more data". The config sets `attention_mode: noncausal_full_attention`: the full-attention layers run bidirectionally while the linear-attention layers keep their native behaviour, and "default causal inference does not reproduce this checkpoint's evaluated setup".
3. **One decision per row.** The usage example passes `{"state", "question"}` rows; inputs above 8,192 tokens (text plus images) are rejected, not truncated.
4. **Training (verified in the JSON).** Full fine-tune (no LoRA), one epoch, learning rate 2e-6, effective batch 256, 2,446 steps, `brier_weight` 0.0 (plain soft cross-entropy in `loss.py`). 626,033 training rows: 95,930 "original" rows plus **530,103 tasksource rows** (84.7 %) after an LLM-based filter (path name `tasksource-glm-filter`), from 349 sources. The card's acknowledgment credits "a large part of the gains" to [[Sileo 2026 - tasksource-jev-typed-decisions dataset card|tasksource]] data.
5. **Training sources overlap GroundOne's tests.** The manifest lists `vitaminc` (3,945 rows) and `wice` (3,881 rows), plus `doc-nli`, `fever-evidence-related`, `health_fact` and many NLI sets. VitaminC is GroundOne's T3 source and WiCE is one of the [[LLM-AggreFact Sub-datasets]] of T2, so any run of this model on GroundOne's tests would be contaminated on those parts (row-level overlap not checked).
6. **Decision Index 0.2.1 (vendor table).** Overall 61.56 for v1.1 vs 56.4 for v1 and 57.9 for Jev; v1.1 leads Language (69.45), Retrieval (61.26) and Arts (44.66), Jev leads Knowledge (51.4). `evaluation/decision-index.json` gives a raw index of 70.68. On the community board snapshot of 2026-09-28, the earlier **v1** had the highest RAGTruth F1 of all 70 entrants (0.803; [[multimodalart 2026 - Jev Decision Index (Hugging Face Space)]]).

## Relevance to GroundOne
- **Same readout family, opposite scale.** A 27B full fine-tune with a restricted letter head is at the top of the board; GroundOne applies the same readout idea at 0.5B/3B with LoRA and a task-specific marker layout. It supports the thesis claim that the restricted readout is a sound interface and that accuracy comes from capacity and training data.
- **Bidirectional attention over the state** is a design option GroundOne does not use (its causal markers must not see later sentences, which matters for one-pass multi-sentence scoring). Perplexity's choice works because each row holds one question.
- **Contamination warning** for any comparison on VitaminC or LLM-AggreFact ([[Datasets for GroundOne]]).

## Links
- Concepts: [[System One Models]], [[Letter-Token Readout]], [[Decision-Model Landscape (Hugging Face, 2026)]], [[Decision-Model Benchmarks]], [[VitaminC]], [[LLM-AggreFact]]
- Related sources: [[multimodalart 2026 - Jev Decision Index (Hugging Face Space)]], [[Sileo 2026 - tasksource-jev-typed-decisions dataset card]]
