---
type: concept
tags: [system-one, decision-models, encoder, open-weights, calibration, laya, related-work]
---
# Laya

**Laya** (Convai Innovations, `convaiinnovations/laya`, licence **Apache-2.0**) is an open-weight, encoder-based [[System One Models|System One]] with a Jev-compatible interface (state + typed `choice` / `score` / `noul` questions → probabilities, no generated text). It is the most visible open alternative to [[Jev]] under the [[Hugging Face decision-models Tag]]. Its independent results are much weaker than its vendor claims. Main sources: [[Convai Innovations 2026 - Laya model card]] (vendor) and the independent evaluations listed below.

## Architecture
- Three checkpoints: `laya` (English, **ModernBERT-large**, 421M, 512-token context), `laya-multilingual` (mmBERT-base, 322M, 1,024 tokens, up to 8,192), and `laya-typed-decisions` (ModernBERT-large, 421M, fine-tuned on one benchmark). A `Router` picks the checkpoint by script and language.
- The backbone is fully fine-tuned and topped by a **2-layer transformer decision head**, an option-marker scorer and an act/escalate head. **Each option is scored at its own `[MASK]` token, and the scores are softmaxed over that question's options**, so options are defined at request time.
- Options are rendered as `"{label}: {definition}"` ([[Azizi 2026 - Labels Override Definitions in Jev-Style Typed Decision Models (arXiv 2610.02586)|Azizi 2026]]).
- "All questions in one forward pass" means one batched call. Laya builds **one input sequence per question** (Azizi 2026), so the state is re-encoded for every question. Latency grows with the number of questions (39.5 ms for 1, 158.6 ms for 10, 771 ms for 50 on a T4).
- The English checkpoint leaves about 320 tokens for the state (512 minus a 192-token option budget).

## Training
- **RLCD** (the vendor's "Reinforcement Learning for Calibrated Decisions"): the policy reports a distribution; exploration adds zero-mean Gaussian noise to the logits; the reward is a strictly proper scoring rule (log + spherical, plus the ranked probability score for ordinal questions); updates are REINFORCE with a group-mean baseline. Per [[Nandakishore 2026 - Laya as a Typed Probabilistic Assessor (arXiv 2609.33843)|Nandakishore 2026]], the typed-decisions recipe also adds a soft cross-entropy against teacher distributions. Compare [[Reinforcement Learning with Calibrated Decisions]].
- Temperatures are fitted per question type or per option count. For the typed-decisions checkpoint they were fitted on a slice of the training data and then overridden at inference by an inherited per-option-count table (Nandakishore 2026).

## Vendor claims vs independent results
| Claim (vendor card) | Independent measurement | Source |
| --- | --- | --- |
| typed-decisions accuracy 0.766 vs Jev 0.727 | Reproduced (0.767), **but the checkpoint is fine-tuned on that benchmark's own training split**, and the score exceeds the teacher's self-agreement ceiling (0.735). Base checkpoints zero-shot: 0.362 / 0.3615 | Nandakishore 2026; [[morrenhale 2026 - Decision benchmark Jev vs Laya vs Julia-1 dataset card\|morrenhale]] |
| ECE 0.081 vs Jev 0.246 (Jev figure third-party) | Laya's 0.081 is post-temperature. The same card quotes Jev at 0.144 elsewhere. morrenhale measures **Laya 0.222 vs Jev 0.105** over 19,776 decisions; Jev 0.038 on typed-decisions | card; morrenhale |
| Strong zero-shot decision engine (implied by the comparison table) | Accuracy **0.590 vs Jev 0.775** (morrenhale). **59.8 % vs Jev 98.0 %**, pair accuracy 36.5 % ([[Yong 2026 - DecideBench dataset card\|DecideBench]]). JevBench chance-corrected intelligence **1.79** (typed-decisions checkpoint 5.47; Jev 63.6) ([[Benchmark Heaven 2026 - JevBench v1.6.1 dataset card\|JevBench]]) | three independent boards |
| Where Laya wins | AG News 0.927 vs Jev 0.892 (morrenhale): easy, well-represented topic classification | morrenhale |
| p50 32.8 ms, "6–8× faster than Jev" | Local T4 vs a hosted API with network: not like-for-like. Apple MPS: 42.9 ms (morrenhale), 19.2 ms per decision (Nandakishore). JevBench raw p50: 0.825 s | several |
| "Ships over-confident" (base checkpoints: refit ECE 0.466 → 0.081) | The **typed-decisions** checkpoint is uniformly **under-confident** (signed gap −0.214). One temperature **T = 0.469** gives held-out ECE **0.204 → 0.037** | Nandakishore 2026 |
| Claim verification (not claimed) | Out-of-distribution claim-verification probe: **0.617**, entity swaps and one-step inference at chance | Nandakishore 2026 |

## Fragility
- **Option order:** 22.5 % of answers flip when the options are reversed (laya 0.3.5), with reversed order 8.8 points more accurate, a position bias ([[pranaysuyash 2026 - Laya Formatting Fragility dataset card|pranaysuyash]]). On the typed-decisions checkpoint, option permutations flip 6.75 % (Nandakishore).
- **Key renames:** 32.8 % flips (position-based); phrasing: 15.0 % (pranaysuyash). Jev: 2.9–8.3 % on the same suite.
- **Labels override definitions:** deleting all definitions leaves accuracy unchanged; contradicting labels drop it to 0.1357; removing the label from the rendering makes Laya exactly label-invariant (Azizi 2026).
- **Negation:** "Is it false that…" flips 96.6–98.3 % of decisions with the probability unchanged (Azizi 2026).
- **Confidence under corruption:** error AUROC 0.8123 under normal labels, 0.2433 under misleading ones (Azizi 2026).
- **Truncation:** an on-device bundle of laya-multilingual with a 256-token input cut 95 of 111 hard JevBench items ([[mlboydaisuke 2026 - Decision models on Core AI (JevBench public231) dataset card|Core AI run]]).

## Relation to GroundOne
| | Laya | [[GroundOne]] |
| --- | --- | --- |
| Backbone | bidirectional encoder (ModernBERT-large / mmBERT-base) | causal decoder ([[Qwen2.5]] 0.5B / 3B) + [[LoRA]] |
| Readout | one `[MASK]` per option, trained head, softmax over options | logits of letters A/B/C at a " Verdict:" marker after each sentence, restricted to the three letters ([[Letter-Token Readout]]) |
| Multiple decisions on one state | one sequence per question (state re-encoded) | one pass per answer; K verdicts read at K markers in the same context |
| Options | caller-defined at run time, `"{label}: {definition}"` | fixed, trained three-way mapping (A = supported, B = contradicted, C = not mentioned) |
| State length | about 320 tokens (English), up to 8,192 (multilingual, erratic past about 4k) | full document + answer |
| Calibration | RLCD + shipped temperatures (wrong direction on typed-decisions) | temperature + per-class bias fitted on dev, threshold τ fitted on dev (D27) |
| Generality | general typed decisions, weak zero-shot | one task, specialised |

- The encoder `[MASK]` head and the decoder letter readout are two ways of scoring a closed option set in one pass. The difference that matters for groundedness is **sharing the long context across decisions**, which GroundOne's marker design does and Laya's per-question sequences do not.
- Laya's own card states the lesson the thesis also draws: "a fast base to specialise, not a zero-shot decision engine". The capability comes from fine-tuning, as for GroundOne (untrained B1 near chance).
- **As a baseline:** Apache-2.0 and local, but zero-shot weak and with short context. The claim-verification probe (0.617) suggests it would not be a strong groundedness baseline. Not run; low priority.

## Links
- Sources: [[Convai Innovations 2026 - Laya model card]], [[Nandakishore 2026 - Laya as a Typed Probabilistic Assessor (arXiv 2609.33843)]], [[Azizi 2026 - Labels Override Definitions in Jev-Style Typed Decision Models (arXiv 2610.02586)]], [[morrenhale 2026 - Decision benchmark Jev vs Laya vs Julia-1 dataset card]], [[Yong 2026 - DecideBench dataset card]], [[Benchmark Heaven 2026 - JevBench v1.6.1 dataset card]], [[pranaysuyash 2026 - Laya Formatting Fragility dataset card]], [[mlboydaisuke 2026 - Decision models on Core AI (JevBench public231) dataset card]]
- Concepts: [[System One Models]], [[Decision-Model Benchmarks]], [[Hugging Face decision-models Tag]], [[Jev]], [[Calibration]], [[Letter-Token Readout]], [[When System One Beats an LLM]]
