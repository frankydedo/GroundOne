# Implementation Plan: GroundOne (working title)

A specialist System One for local RAG: single-pass, calibrated groundedness verification with compact Qwen2.5 models on a 16 GB Apple Silicon laptop.

> **Status:** v0.8 (2026-10-18; D28 demo as a native Swift app). Done: feasibility (Phase 0/0b), EDA, the GroundOne package, the dataset (built, validated, test sets frozen 2026-10-07, `dataset_plan.md`), GroundOne 0.5B (two completed runs) and 3B (readout design b), calibration and served threshold, all baselines on the frozen tests (incl. the same-size general decision model d1-3B), the latency protocol, the 3B on the full LLM-AggreFact test, the equal-output judge, bootstrap CIs, control B2, energy per verification. Thesis: full drafts of all nine chapters (2026-10-10/11), new Ch. 2 on local inference; Ch. 1–2 and the summary revised by the author in Italian and aligned in English (2026-10-13); abstract v0.4. Pending: the demo (`demo_architecture.md`), the other locality items, the author's review of Ch. 3–9. All findings: `thesis_notes.md`; summary: `checkpoint_2026-10-10.md`.
> **Hard constraint: the experiment *and* the written thesis (`Thesis/`) must be done by the submission date, 2026-11-10. New experiments only until 2026-10-30.** The schedule (§9) and the scope cuts (§1.5) follow from this.
> Every number marked *(estimate)* or *(provisional)* is a planning figure to be replaced by a measurement.
> Companion document: `abstract.md`.

---

## 0. How to use this document

- It is the compass for the whole experiment: if a task is not traceable to a research question (§2), it is out of scope.
- Decisions that the author must confirm are tagged **[DECIDE]**. Open questions are collected in §14.
- Phases and gates are in §9 and §10. Phase 0/0b (feasibility) said **GO** on 2026-10-05. A one-page tracker is in `tracker.md`.
- Update this file whenever a decision changes. Never silently change the experiment: add a line to the decision log (§3).

---

## 1. Goal and scope

### 1.1 Thesis statement
A compact language model, fine-tuned to do **one thing** (verify the sentences of a RAG answer against the retrieved context) and used as a **System One** (one forward pass, logit readout, no text generation), can (i) answer **many questions over one shared context in parallel**, faster than a generative judge and always in a valid format, (ii) approach the accuracy of larger models after specialisation, (iii) tell *contradicted* from *not mentioned* sentences, so that the user can choose a strict or lenient notion of error without retraining, and (iv) give probabilities calibrated well enough to be used as thresholds, all on a laptop.

This is a hypothesis. The thesis is valid whether it is confirmed or not, provided the comparison is controlled and honest.

**Pillar: full locality and independence** (author, 2026-10-08). The whole solution (training, calibration, evaluation, inference) runs on one consumer laptop with no external API or service. This is a central argument, not a constraint: the System One avoids autoregressive decoding, which is the slowest operation on local hardware. Ch. 1–2 include an overview of local inference (local vs remote, evolution, hardware); outline in `thesis_notes.md`.

### 1.2 The task (one decision, done well)
**Groundedness verification for RAG** (redefined 2026-10-06, D20). Input: a retrieved context `C` and a generated answer `A` split into sentences `s_1..s_K`. Output: for each `s_i`, one decision with three classes and their probabilities `P(supported)`, `P(contradicted)`, `P(not_mentioned)` (sum 1).

- **supported**: everything the sentence states is said or directly implied by `C`; **contradicted**: some part conflicts with `C`; **not_mentioned**: it adds information `C` neither contains nor contradicts. A sentence with both a conflicting and an unverifiable part is *contradicted*.
- **K = the number of sentences of the answer**: one decision per sentence, no artificial extra questions. K is the variable on which the System One advantage is measured (accuracy and latency as a function of K).
- Everything else is derived from the three probabilities, without asking the model again: binary groundedness = `P(supported)`; strict rule (anything not stated is an error) flags `P(supported) < τ`; lenient rule (only contradictions are errors) flags `P(contradicted) > τ`. There is no abstain class; uncertainty is handled with thresholds (selective prediction).
- This is the **narrowing of use case B** discussed with the author: one task (groundedness of answer sentences), not chunk relevance. Reason: a shared long context with several short questions occurs naturally (the shared-prefix advantage, §4.3). Per-chunk relevance grading does not have this structure.

### 1.2b Where each advantage comes from (spine of the method chapter)
GroundOne is a Qwen2.5 model used in System One mode **plus** task-specific training. The two parts bring different gains, and the thesis must keep them apart:

| Advantage | Source | Already present in the untrained model (B1)? |
| --- | --- | --- |
| Speed vs a generative judge; K questions scored in parallel over one shared context | The **System One mechanism** (single pass, logit readout, shared prefix, batched suffixes) | Yes: it only has to be implemented well (Phase 0b) |
| Accuracy | **Training** (GroundOne) | No: the 0.5B is ~16 points below the encoders zero-shot |
| Reliable probabilities (calibration) | Training + temperature scaling | No: zero-shot ECE 0.22–0.32 |
| Three-way answers (contradicted vs not mentioned), hence strict/lenient rules chosen by the user | Training on three-way labels | Partly (Phase 0b) |
| Speed vs a **larger** model of equal quality | Training: a 0.5B that matches the 3B is ~6× cheaper per decision | Only if training works |

Fine-tuning does **not** change latency: after LoRA merging, GroundOne runs exactly the same computation as B1.

### 1.2c What makes GroundOne a specialist (vs general-purpose System Ones such as Rizzo-Flow, SemIf, Jev)
1. **Data:** trained only on sentence-vs-document verification (sources in `dataset_plan.md`), not on generic typed decisions.
2. **Decision space:** one fixed three-way decision per sentence (supported / contradicted / not mentioned), instead of arbitrary questions and primitives.
3. **Objective:** the loss is computed on the answer letters only, at the exact position and with the exact prompt used at inference.
4. **Engine and calibration:** the engine is built for RAG (context and answer prefilled once, answer split into sentences, sentences scored by index in parallel), and the temperature is fitted on groundedness data.

The test of specialisation is the head-to-head with Rizzo-Flow on our benchmarks. A relevant prior: Rizzo-Flow's generic fine-tune got **worse** on missing evidence (0.750 → 0.583), which is our task. The price, stated in the thesis: GroundOne is not meant to answer anything outside this task.

### 1.3 In scope
- Fine-tuning Qwen2.5-0.5B-Instruct and Qwen2.5-3B-Instruct with LoRA (MLX).
- A custom inference engine with shared-prefix evaluation.
- Baselines in a ladder that isolates each source of gain (§7).
- Evaluation on public human-labelled benchmarks (§5, §8).
- A minimal local RAG demo with live verification (§11).

### 1.4 Out of scope (explicit)
- Tool routing and everything in `Project_old/` (kept as development history; not part of the thesis claims).
- Argument/JSON generation, free-text explanations, multi-step reasoning.
- Multi-lingual use: **English only**.
- Qwen2.5-7B in any form: it is not run; its published zero-shot LLM-AggreFact score (72.8) is used as the larger-model reference (D13).
- Training a new RLCD-style reinforcement learning stage. Calibration is done by supervised loss plus post-hoc temperature scaling.
- A hand-labelled local evaluation set (cut for time, decision D10).

### 1.5 Scope cuts imposed by the one-month deadline (D11)
| Item | Original plan | One-month plan |
| --- | --- | --- |
| Hand-labelled local set | 150–300 sentences | **Cut.** The demo is evaluated qualitatively plus latency/memory only |
| Seeds | 0.5B ×3, 3B ×1–2 | 0.5B ×2 if time allows (else ×1), 3B ×1 |
| Hyper-parameter sweep | small sweep on 0.5B | at most 2–3 configurations, chosen on dev |
| Ablations | A1–A5 | **A1, A2 required** (they come for free from baselines B1, B2); A3–A5 in week 4 only if the main matrix is complete |
| Extensions | E1, E2 | E1 cut. E2 (rules in the prompt) replaced by rules derived from the three-way output (D20) |
| Slow baselines (B0b verbose judge) | full test sets | **stratified subsample** (e.g. 300–500 items), stated in the thesis. B0c (7B) not run (D13) |
| Training sources | 3–4 sources | see `dataset_plan.md` |
| Context cap | 1,024 then 2,048 | 1,024 (2,048 only if free) |
| Demo | streaming, policy actions | static answer + coloured sentences + threshold slider + timings |
| Phase 0 | ~1 week | **2 days** |

---

## 2. Research questions and hypotheses

| ID | Research question | Hypothesis (falsifiable) |
| --- | --- | --- |
| RQ1 | **Specialisation.** Can a fine-tuned 0.5B/3B System One match larger zero-shot models and the encoders? | H1: the fine-tuned 0.5B closes most of its gap to MiniCheck-RoBERTa (zero-shot gap ≈ 16 points on our LLM-AggreFact sample) and reaches the zero-shot 3B; the fine-tuned 3B reaches at least the published zero-shot 7B (72.8 on the full LLM-AggreFact). |
| RQ2 | **Readout vs generation.** How much does the System One mechanism buy, at the same model size? | H2a: against a same-model single-token-generation control the latency difference is negligible. H2b: against terse and verbose generative judges the speed-up grows with K (decisions per context). **Phase 0b (untrained models): ≈2× vs terse and ≈6× vs verbose at K = 24**; to be confirmed on GroundOne with the full protocol. H2c: the System One always returns K valid answers, while small generative judges break the format (Phase 0b: up to 97 % failures for the 0.5B verbose judge). |
| RQ3 | **Calibration.** Are the probabilities usable as confidence? | H3: after fine-tuning plus temperature scaling, ECE is lower than for zero-shot logits of the same model and than for verbalised confidence of generative judges; selective prediction at a chosen coverage improves accuracy monotonically. |
| RQ4 | **Reliability and cost on-device.** Does the full stack fit and stay interactive on 16 GB? | H4: the verifier adds *(provisional)* < 1 s p95 to a typical 5-sentence answer with the 3B and < 0.3 s with the 0.5B; peak memory of generator + verifier + retriever stays under ~11 GB; the System One has 0 % format failures while small generative judges show measurable ones. |
| RQ5 | **Beyond a binary score.** What does the System One give that a binary encoder (MiniCheck, HHEM) does not? | H5: on the plain binary task the encoder ties or wins (expected, and reported). GroundOne separates contradicted from not mentioned sentences (three-way macro-F1 above chance on RAGTruth test), so strict and lenient rules can be applied at inference, and it uses the whole answer as context (pronouns, references) while encoders score sentences in isolation. |

Success levels:
- **Minimum viable thesis:** controlled comparison completed, honest decomposition of gains (H2b/H2c are already supported by Phase 0b), working demo, even if the encoder wins on the plain task.
- **Target:** H1 (0.5B), H2b, H2c, H3 and H5 confirmed.
- **Stretch:** streaming verification in the demo; implicit-truth rule (RAGTruth `implicit_true`).

### 2.1 Status of the hypotheses after the first full round (2026-10-08)

Numbers are from `thesis_notes.md`; T1 = RAGTruth test, T2 = LLM-AggreFact, T3 = VitaminC.

| ID | Evidence so far | Status |
| --- | --- | --- |
| H1 specialisation | LLM-AggreFact macro: 3B **74.8** (on par with MiniCheck-RoBERTa 74.0: +0.8, 95 % CI −0.5 to +2.1; above the published zero-shot 7B 72.8), 0.5B 70.1 (zero-shot 64.2); RAG subset 76.9 (3B, +2.4 over RoBERTa, CI +1.4 to +3.3) / 74.4 (0.5B, on par) vs RoBERTa 74.6. T1 AUROC 0.905 (0.5B) and 0.940 (3B) vs 0.81–0.82 for the encoders. On T1 the 0.5B beats Rizzo-Flow 4B (three-way 0.80 vs 0.60 on the same answers) | **Supported in the RAG domain.** Weaker outside it (T3; non-RAG T2 columns) |
| H2a readout vs single-token generation | Checked on 200 dev answers (2026-10-09): at the markers the full-vocabulary argmax is the *spaced* letter (" A") in 75 % (0.5B) / 99 % (3B) of cases, never the unspaced letter that the readout reads; mapped to a verdict, it agrees with the readout in 75 % / 92 %. The trained letters carry only 4–5 % of the probability mass: the restricted loss shapes their relative logits, not their absolute mass. Same forward pass, so same latency. **B2 on full T1 (2026-10-10):** generated token 0.521 vs readout 0.769 (0.5B; 24.7 % format failures), 0.761 vs 0.832 (3B); +0.248 [+0.228, +0.269] and +0.071 [+0.059, +0.083] | **The restricted readout adds accuracy** at equal weights, pass and latency; more for the smaller model |
| H2b speed vs generative judges | At K ≥ 14: 0.5B 0.41 s vs 0.80 s (terse) and 2.51 s (verbose); 3B 2.57 s vs 4.44 s and 15.86 s. The gain grows with K | **Supported** |
| H2c format reliability | 0.5B judges: 23 % (terse) and 97 % (verbose) unparsable verdicts; 3B: 0.1 % and 7.6 %. System One: 0 % | **Supported** |
| H3 calibration | Temperature + bias on dev: T1 binary ECE 0.30 → 0.019 (0.5B), 0.18 → 0.019 (3B); AURC 0.015 / 0.010. Does not transfer to T3 | **Supported in domain** |
| H4 on-device cost | Training peak 2.6 GB (0.5B) and 5.9 GB (3B); verification 0.33 s / 1.99 s median per answer (3B at K 5–8: 1.93 s, above the provisional < 1 s); energy 5.5 J / 33 J per answer. Co-resident memory with a generator not yet measured | **Partly supported** (0.5B yes; 3B slower than the target; co-residence pending) |
| H5 beyond a binary score | Three-way 0.769 / 0.832 on T1; contradicted recall low outside data-to-text (QA and Summary 0.03 → 0.30 with the 3B) | **Partly supported** |

---

## 3. Key design decisions (decision log)

| # | Decision | Rationale | Alternatives considered |
| --- | --- | --- | --- |
| D1 | Task = groundedness (support) verification, binary | Natural shared context + K short questions; public human-labelled data; real local-RAG need | Chunk relevance (no shared-state structure; strong cross-encoder rivals); prompt-injection detection (K = 1, noisier labels); privacy filter (mostly synthetic labels) |
| D2 | Models: Qwen2.5 0.5B and 3B Instruct (fine-tuned); 7B zero-shot baseline only | Fits 16 GB; matches author's size plan | 7B fine-tuning (memory with long contexts) |
| D3 | Fixed answer letters (now `A` supported / `B` contradicted / `C` not mentioned, D20), fixed mapping | Single-token readout; fine-tuning removes most position bias | Random option order (adds noise for a 2-way task); `Yes/No` words (tokenisation variants) |
| D4 | Custom MLX engine with prefix KV cache and per-claim suffix evaluation | Needed to realise the shared-context advantage; the old LightningRoute engine had none | Using Rizzo-Flow as the engine (not our contribution) |
| D5 | Custom training loop: cross-entropy over the restricted answer logits, prompt masked | `mlx_lm` rejects prompt masking for the `text` format; previous runs trained on every prompt token (label < 1 % of the loss) | `mlx_lm.lora` with completion format + `mask_prompt` as a first version |
| D6 | Calibration = temperature scaling fitted on a held-out dev set | One parameter, no leakage risk if dev is separate from test | RLCD (out of scope), isotonic (needs more data) |
| D7 | English only | Author's decision | Italian |
| D8 | Demo = local RAG chat app with coloured sentences and a threshold slider *(UI and scope refined by D28)* | Author's decision | CLI only |
| D9 | Always include the two "honest controls": same-size single-token LLM, and a specialised encoder | They are the comparisons a reviewer will ask for | – |
| D10 | No hand-labelled local set | Author's decision (2026-10-04): no time | Small manual set |
| D11 | One-month scope cuts (§1.5) | Deadline: experiment + thesis in one month | Full plan |
| D12 | Demo generator = Qwen2.5-3B-Instruct | Memory: 3B generator + verifier fits 16 GB | 7B 4-bit (too tight) |
| D13 | 7B not run; published leaderboard number used as reference | Memory and time; the number exists | Run 7B 4-bit zero-shot |
| D14 | Engine scores the K questions in one **batched** pass (prefix KV cache replicated K times, short index-based suffixes) | Phase 0: sequential suffixes erased the System One advantage; Phase 0b: batched is exact (|Δp| = 0) and 2–6× faster than generative judges at K = 24 | Sequential suffixes with cache trimming |
| D15 | *(Superseded by D20)* Three-way question and strict/lenient rules become part of GroundOne's question set and of its **training data** | Phase 0b: zero-shot models do not follow rules; this is the flexibility claim vs encoders | Drop flexibility; keep it zero-shot only |
| D16 | Phase 1a: exploratory data analysis of ANLI and RAGTruth before building the training mix | Decide which dataset serves which question, length caps, label rules | Build the mix directly |
| D17 | Fine-tune **both** 0.5B and 3B; compare at the end | Author's decision: let the results pick the better trade-off | 0.5B main + 3B zero-shot reference |
| D18 | LLM-AggreFact is used only to evaluate: no training, and no fitting of temperature, threshold or model selection on any of its splits | Its HF gating condition forbids using it for pretraining or fine-tuning; fitting on it would also make our numbers incomparable with the leaderboard | Fit temperature on its dev |
| D19 | GroundOne is an installable package with CLI and HTTP API (native `/v1/verify` + TypeSafe/Jev-compatible `/v1/systemone`, the contract Rizzo-Flow serves) | Author's requirement; evaluation, demo and server share one engine; drop-in replacement for Rizzo-Flow/Jev clients | Loose scripts |
| D20 | **Task redefined**: one three-way decision per answer sentence (supported / contradicted / not mentioned); K = number of sentences; binary score and strict/lenient rules derived from the three probabilities. Supersedes D15 and the four-question format | The four questions were deterministic functions of the three-way class (strict = binary, lenient = not contradicted): they inflated K artificially and gave conflicting targets for the same sentence. K must come from the task (sentences of the answer) | Keep four questions in the prompt |
| D21 | **Dataset rebuilt from scratch** following `dataset_plan.md`, reduced to the strict minimum: RAGTruth is the only training source (plus dev and test T1); LLM-AggreFact (T2) and VitaminC (T3) are test-only. Test sets defined, validated and frozen **before** any training. Only the final dataset is described in the thesis | Author's decision (2026-10-06): without a reliable test set every later result is useless | Iterate on the previous dataset |
| D22 | **Readout design (b) is the default**: one forward pass per answer, a marker " Verdict:" after every scored sentence, A/B/C logits read at the markers, output head applied only there; class-weighted loss (classes contribute equally). Design (a), with one question suffix per sentence, is kept as a fallback | Uses every labelled sentence of an answer in one training row (≈ 8× more supervision for the same cost) and one pass at inference. Validated on 2026-10-07: T1 three-way 0.769 (0.5B) | Design (a) as default |
| D23 | **Validation run and 3B configuration**: 0.5B on all training answers (accumulation 4); 3B on 6,500 random answers (option A, one night; same LR 1e-4; ≈ 16 answers per step; dev on 200 answers) | Author's decisions 2026-10-06/07; one night per model on the M4 | 3B on the full set over two nights |
| D24 | **Calibration per adapter = temperature + per-class bias on dev** (`groundone calibrate-b`). Primary classification metrics use the raw (balanced) decision; calibrated probabilities are used for ECE, thresholds and selective prediction | The bias restores base rates and moves the argmax towards "supported" (three-way 0.77 → 0.63 for the 0.5B) | Temperature only |
| D25 | **Equal-output judge B0d** (2026-10-09): a zero-shot generative judge of the same size that must return the same content as GroundOne, i.e. per scored sentence a label and P(A), P(B), P(C). Two variants: **B0d-verbal** writes the probabilities in a JSON object (the stated label is the decision); **B0d-logit** is the terse judge with the three probabilities read from the logits at the generated letter. Both are calibrated with the same temperature + bias as GroundOne, fitted on 200 K-stratified dev answers (`judges-calibrate`); GroundOne is re-evaluated on the same latency subset with its own calibration. JSON prompt with placeholders, no numeric example (an example was copied verbatim by both sizes; chosen on 12 dev answers on format validity only). Lenient parsing (per-entry regex; a missing label is taken as the argmax of p) | Author's request: B0a/B0b give less information than GroundOne (no probabilities, so no ECE, thresholds or strict/lenient policy), so the comparison was not at equal output. B0d-logit is the strongest generative opponent and also answers the open B2 question at the judge level | Compare only with B0a/B0b; constrained (grammar) decoding, noted as a limitation |
| D26 | **Seed runs of the 0.5B** (2026-10-09): seed 4321 (`g1-05b-s2`) collapsed (dev macro 0.369 → 0.333 → 0.444 at steps 150/300/450) and was stopped at step ≈ 470; replaced by seed 777 (`g1-05b-s3`), presented in the thesis as the second run. The stopped run is disclosed in one sentence (thesis notes), and its logs are kept | Incomplete runs cannot be compared with complete ones, but omitting them would be selective reporting; the collapse is evidence on the robustness of the recipe (no gradient clipping) | Let seed 4321 finish (≈ 3.5 h of training plus ≈ 3 h of tests on a collapsed model); hide the stopped run |
| D27 | **HTTP API on design (b) with one coherent output rule** (2026-10-10): `/v1/verify` follows the adapter's design; with design (b) it segments with the training rule, runs one pass, and derives labels, strict/lenient flags and the shown probabilities from the calibrated probabilities: "supported" iff P(supported) ≥ τ, else the more probable of contradicted / not mentioned. τ is fitted on dev by `calibrate-b` (maximising three-way macro recall) and stored in `calibration.json`; a request may override it; without τ the label is the raw class-balanced argmax (D24). `/v1/systemone` stays on design (a) | The served output showed raw-argmax labels next to calibrated probabilities that contradicted them (thesis notes 2026-10-09); a single rule on calibrated probabilities with a dev threshold keeps labels, flags and probabilities consistent while approximating the evaluated balanced decision | Raw-argmax labels next to calibrated probabilities; argmax of calibrated probabilities (three-way 0.77 → 0.63, D24) |
| D28 | **Demo = native macOS app in Swift/SwiftUI with MLX Swift** (2026-10-18): retrieval, generator and GroundOne verifier in one process; GroundOne ported to Swift (prompt, segmentation, marker readout, calibration) and gated by a conformance test against the Python probabilities (\|Δp\| < 0.01); a verify-and-revise loop that rewrites only flagged sentences; policies (strict/lenient, τ, attempts, on-failure action) and an audit log; measurement mode for the co-residence and overhead figures. Engines behind protocols, so a llama.cpp backend can replace MLX later. Spec: `demo_architecture.md` | Locality as a product property (one signed app, no interpreter, no server); reuses the trained MLX adapters and calibration unchanged (no retraining, no recalibration); native PDF, sentence and SQLite APIs | Python app around the existing server (B); Rust with Tauri + mlx-rs or candle (C); llama.cpp/GGUF (D: requantisation and recalibration) |

Record future changes below (date, decision, reason).

- 2026-10-04: D1 confirmed by the author (single task: sentence-level groundedness). D10, D11 added.
- 2026-10-05: submission date 2026-11-10; experiment freeze 2026-10-30. Encoder baselines (B4) approved. CLM = related work only (not a baseline). D12–D16 added after Phase 0/0b.
- 2026-10-05: **D17**: both the 0.5B and the 3B are fine-tuned and evaluated in parallel; the thesis reports which one is the better trade-off. The 3B is trained on a ~10K subset to fit one night.
- 2026-10-06: **D20** (task redefined: three-way per sentence, K = sentences) and **D21** (dataset rebuilt from scratch, `dataset_plan.md`) decided with the author. The earlier datasets, models trained on them and their analysis were archived outside the repository.
- 2026-10-07: **D22** (readout design b default), **D23** (validation run; 3B option A), test sets frozen. 2026-10-08: **D24** (calibration temperature + bias; decisions on raw output). First full round of results in `thesis_notes.md`.
- 2026-10-09: full T2 for the 3B (macro 74.8, RAG subset 76.9); the subsample + second-seed queue was cancelled in favour of it (author). No decision changed.
- 2026-10-09: **D25** (equal-output judge B0d), bootstrap CIs (T2 claim vs MiniCheck tempered to "on par").
- 2026-10-09/10: **D26** (seed 4321 collapsed and stopped; seed 777 completed, presented as run 2); control B2 and energy measured.
- 2026-10-10: **D27** (HTTP API on design b, one coherent output rule; served threshold fitted on dev).
- 2026-10-11: new thesis chapter on local inference (Ch. 2, author's decision; chapters renumbered 1–9). No experiment changed.
- 2026-10-18: **D28** (demo as a native Swift/SwiftUI app with MLX Swift; §11 replaced by `demo_architecture.md`). Open details listed there (§12) and in §14.

---

## 4. System design

### 4.1 Prompt format

> **Current default: readout design (b)** (D22, `prompts.encode_marked`). The prompt is: system message, user turn with an instruction, `DOCUMENT:` and `ANSWER:`. Every sentence is written as `[k] sentence`, and every scored sentence is followed by the marker " Verdict:" (3 tokens). The A/B/C logits are read at the marker's last token, all K in one forward pass, and the sequence ends after the last marker. The format below (design a) is the fallback, and is also used by the untrained baseline B1 and by the compatible `/v1/systemone` route; the native `/v1/verify` serves design (b) since D27.

Chat template of Qwen2.5 (ChatML). The prompt is split into a **shared prefix** and a **per-claim suffix** so that the prefix is encoded once.

```
<|im_start|>system
You are a faithfulness verifier for retrieval-augmented answers.<|im_end|>
<|im_start|>user
DOCUMENT:
{retrieved passages}

ANSWER (numbered sentences):
[1] ...
[2] ...
                                  <- shared prefix ends here
Question about sentence [i]: {question q}  Answer A for yes, B for no.   (three-way: A/B/C)<|im_end|>
<|im_start|>assistant
                                  <- read the logits of the allowed letters here
```

- The full numbered answer is part of the prefix, so pronouns in sentence *i* can be resolved; the suffix only names the sentence index and the question (~10–25 tokens). This is the Phase 0b format (`experiments/feasibility/scripts/s1engine.py`, `06_speed_batched.py`); the exact wording is frozen in Phase 2.
- For pair-style benchmarks (LLM-AggreFact: `document`, `claim`) the answer *is* the claim and K = 1. The shared-prefix saving only appears on RAGTruth-style responses and in the demo.
- **Boundary rule:** the engine tokenises each full prompt and takes the **longest common token prefix** as the shared part, so BPE merges at the boundary cannot cause mismatches. Unit test: batched probabilities equal one-pass-per-question probabilities (Phase 0b: max |Δp| = 0.00000).

### 4.2 Engine (MLX)

> Design (b): `Backend.score_positions` runs one padded batch of whole answers, gathers the hidden states at the marker positions and applies the output head only there (`readout.py`). The description below is design (a).

```
engine.verify(context, answer_sentences, questions) -> [P(answer)_k for k in 1..K]
 1. build the K prompts, take the common token prefix, prefill it once   (cost ~ prefill(S))
 2. replicate the prefix KV cache K times along the batch axis
 3. run the K short suffixes as ONE right-padded batch
 4. at each suffix's last real token read the logits of the allowed letters -> softmax / T
 5. return probabilities (+ timings: prefill_ms, batch_ms)
```
- Restricted softmax over the two answer tokens, divided by a calibrated temperature `T`.
- Batched by design (D14). Implementation: `GroundOne/src/groundone/backend.py` (prototype: `experiments/feasibility/scripts/s1engine.py`). Memory: the replicated cache costs K × prefix × ~36 KiB/token on the 3B (≈ 1.7 GB at K = 24, 2,000 tokens).
- MLX Metal context must stay on one dedicated worker thread (lesson from LightningRoute).
- Keep the engine free of HTTP so that it can be benchmarked in-process; the API layer is a thin wrapper (FastAPI: `POST /v1/verify`, `GET /health`).

### 4.3 Cost model (the claim we have to test, not assume)
Let `S` = prefix tokens, `K` = claims, `n` = tokens a generative judge emits per claim, `t_dec` = per-token decode time.

- Generative judge: `T_gen ≈ prefill(S) + K · n · t_dec`
- System One: `T_s1 ≈ prefill(S) + K · t_suffix`

Measured in Phase 0/0b *(MLX 8-bit, M4 16 GB)*: prefill ≈ 0.37 ms/token (0.5B) and ≈ 2.2 ms/token (3B); decode ≈ 5.9 ms/token (0.5B) and ≈ 31.8 ms/token (3B). Generative judges wrote ≈ 4–5 tokens per decision (terse) and ≈ 20–31 (verbose). End-to-end results by K and context length: `phase0_report.md` §B1.

Consequences to keep in mind:
- **Prefill dominates.** Roughly 2 ms/token on the 3B. The fixed cost of reading the context is the same for System One and generative judges.
- Against a *terse* generative judge the gain grows with K: ≈1.0× at K = 1, ≈1.4× at K = 8, ≈1.9× at K = 24 (3B, 1,000 tokens, measured with untrained models).
- Against a **verbose** judge: ≈3.3× at K = 8 and ≈5.8× at K = 24 (same setting).
- The gain shrinks with context length (prefill is shared by all methods); for the 0.5B at 2,000 tokens it disappears.
- Against a **single-token generative control** the gain is about zero. This is the honest result for H2a.
- A second lever is **model size**: a 0.5B specialist has roughly 6× cheaper prefill than the 3B. If it keeps the accuracy, that speed-up comes from specialisation, not from the readout.

The thesis must report all three comparisons and not only the favourable one.

### 4.4 Calibration
1. Train with cross-entropy on the restricted logits (§6; design b: A/B/C at every marker, class-weighted).
2. Fit a temperature `T` and a per-class bias on a dev split that is disjoint from both train and test, by minimising NLL (D24); fit the served threshold τ on dev (D27).
3. Report ECE (15 bins and adaptive bins), Brier, NLL, reliability diagrams, before/after `T`.
4. Optional: Platt scaling on the logit difference if `T` alone is insufficient.
5. Selective prediction: accuracy vs coverage curve, AURC. This is what makes the probability useful (e.g. flag a sentence only if `P(supported) < τ`).

---

## 5. Data

The dataset (sources, label mapping, splits, leakage rules, reliability checks, sizes) is specified in **`dataset_plan.md`** and is built from scratch (D21). Constraints that stay fixed:
- LLM-AggreFact is **evaluation only** (D18): no training, and no fitting of temperature, threshold or model selection on any of its splits.
- Splits are by group (source document / instance), never by row; a leakage check fails the build on any overlap with a test set.
- The test set is defined, validated and frozen before any training run.
- Contamination of Qwen2.5's own pre-training data cannot be excluded; stated as a limitation.

---

## 6. Training plan

### 6.1 Setup
- Base: `Qwen2.5-0.5B-Instruct` and `Qwen2.5-3B-Instruct`, MLX 8-bit for both (the Phase 0 probe fit the 3B at 2,048 tokens in 5.9 GB).
- Method: LoRA on **all linear layers of all blocks** (QLoRA found adapter coverage matters more than rank; the old configs adapted only 8 blocks; `mlx_lm` defaults to the last 16 blocks), rank 8–16. Avoid a 4-bit base if memory allows: Rizzo-Flow measured a 14-point weaker starting point with an NF4 base.
- **Licence note:** Qwen2.5-3B is under the *Qwen Research* licence (not Apache-2.0, unlike 0.5B/1.5B/7B). Fine for thesis research; check its terms before publishing 3B adapters. Qwen2.5-1.5B is the nearest Apache-2.0 alternative.
- Training hardware: the M4 / 16 GB machine. Use gradient checkpointing, batch size 1 with gradient accumulation.

### 6.2 Loss
- Position: design (b), the default: the marker after every scored sentence, A/B/C logits, class-weighted cross-entropy over all markers (D22). Design (a): the last prompt token. In both, logits are restricted to the allowed answer letters and the loss is the cross-entropy of that restricted softmax against the gold label.
- All prompt tokens are masked: the label is the only supervised signal.
- Optional variants (ablation A3): soft labels where annotator agreement exists; full-vocabulary cross-entropy on the label token instead of the restricted softmax.
- Implemented as a custom MLX loop (`groundone train --config train_0.5b.yaml`, `GroundOne/src/groundone/training/train.py`; hyper-parameters in `GroundOne/configs/*.yaml`, copied into each run): `mlx_lm.lora`'s data pipeline is incompatible with the installed `transformers` 5.x. Length-bucketed batches under a token budget, gradient accumulation, warm-up + cosine LR, dev evaluation every `eval_every` steps (150 for the 0.5B, 80 for the 3B), best checkpoint kept, adapters saved in MLX format.

### 6.3 Memory and length
The risk is long contexts. Rules of thumb *(to measure)*:
- Cap training prompts at 1,024 tokens first, then try 2,048. RAG use in the demo is top-3 chunks of 300–500 tokens plus the answer.
- Measure peak memory with the MLX peak-memory API at a few lengths before launching a long run.
- If the 3B does not train at the target length, fall back to 4-bit base (QLoRA-style), shorter cap, or smaller rank, and document it.
- Training time (Phase 0 probe, measured per token): one epoch of ≈35K MiniCheck-length examples ≈ 3–4 h on the 0.5B and ≈ 17 h on the 3B. The 3B must be trained on a subset (~10K examples ≈ one night).

### 6.4 Procedure

> **As run (2026-10-07/08).** One epoch, AdamW lr 1e-4 (no weight decay), cosine decay, LoRA r16 / α32 / dropout 0.05 on all linear layers.
> - 0.5B: all 13,203 training answers, 802 steps, warm-up 3 %, accumulation 4, dev every 150 steps on the full dev set, 5.4 h.
> - 3B: 6,500 answers, 403 steps, warm-up 5 %, ≈ 2 answers per micro-batch × accumulation 8, dev on 200 answers every 80 steps, 12.25 h.
> - Best checkpoint on dev three-way balanced accuracy (mean over tasks).
> - Configs: `GroundOne/configs/train_0.5b.yaml`, `train_3b.yaml`. 0.5B: two completed runs (seeds 1234 and 777) plus one collapsed and stopped run (D26); 3B: one run.

1. Sanity run: 0.5B on a small subset; loss must decrease; the engine's output must equal the training-time computation (same prompt, same logits within tolerance).
2. Hyper-parameter sweep (small): learning rate, rank, epochs, on the 0.5B only; selection on dev only.
3. Final runs: 0.5B (2 seeds if time allows, else 1), 3B (1 seed, launched overnight). Report mean ± std where seeds exist and state the single-seed limitation otherwise.
4. Save adapters, configs, loss curves, dataset hash, git commit for every run.

### 6.5 Ablations and extensions
**A1 and A2 are required.** A3–A5 run in week 4 only if the main experiment matrix is complete (§1.5, §9). E1 is future work; E2 is evaluated from the three-way output (D20). Results go in thesis §6.4.

| ID | Experiment | Purpose |
| --- | --- | --- |
| A1 | Base vs fine-tuned, same readout | Isolates the effect of fine-tuning |
| A2 | Readout vs single-token generation, same fine-tuned weights | Confirms equivalence (H2a) |
| A3 | Restricted-softmax vs full-vocab loss; hard vs soft labels | Effect of the loss on calibration |
| A4 | Training-set size curve (e.g. 5k / 10k / 20k / all) | Data efficiency |
| A5 | Prefix with and without the full answer | Value of context for resolving references |
| E1 (stretch) | Sentence-level vs claim-decomposed verification | Granularity |
| E2 (superseded by D20) | Rules applied at inference from the three-way probabilities (strict: `P(supported) < τ`; lenient: `P(contradicted) > τ`), evaluated against gold rule labels derived from the three-way test labels | RQ5 |

---

## 7. Baselines (a ladder that isolates each effect)

| ID | System | What it isolates |
| --- | --- | --- |
| B0a | Qwen2.5 0.5B / 3B zero-shot, **terse generative judge**: one line '<id>: yes/no' per decision, greedy | Typical practice at the same size |
| B0b | **Verbose generative judge**: one sentence of reasoning, then 'Verdict: yes/no', per decision | The common LLM-as-a-judge practice (RAGAS, Lynx); largest latency gap |
| B0d | **Equal-output judge** (D25): same content as GroundOne (label + three probabilities per sentence), either verbalised in JSON (B0d-verbal) or read from the logits at the generated letter (B0d-logit); calibrated on dev like GroundOne | Output parity: what a generative judge costs to give the same information, and how good its probabilities are |
| B0c | Qwen2.5-7B-Instruct zero-shot, **published number only** (72.8 on LLM-AggreFact), not run (D13) | Larger-model reference for H1 |
| B1 | Same base models, **single-token readout, no fine-tuning** | Readout alone, without specialisation |
| B2 | Fine-tuned model, verdict = the token greedy generation would emit at each marker (same pass; `groundone test --decision generate`) | Readout vs generation at equal weights and latency; run 2026-10-10: the readout is +0.25 (0.5B) / +0.07 (3B) better |
| B3 | **Rizzo-Flow** (general-purpose System One) via its `/v1/systemone` or `/v1/decisions` API, boolean question per claim, shared state = context | General-purpose System One. Sizes available are Spark-X2.5 4B and 1.7B; whether a Qwen2.5 GGUF can be loaded with `--model` is **untested** and is checked in Phase 0. Report which weights (`flow` default fine-tune or `base`) |
| B4 | **Encoders:** MiniCheck-RoBERTa and -DeBERTa, HHEM-2.1-open (separate env, `transformers` 4.46), run on the same machine (PyTorch MPS). MiniCheck-Flan-T5 does not fit the memory guard (published number used); AlignScore optional | Strongest cheap specialised alternative (RQ1, RQ5) |
| B5 | Published numbers of larger systems on LLM-AggreFact (not re-run) | Context only |
| (B6) | **CLM** (Contrastive Language Models, Kwok et al., 2026, blog + Apache-2.0 code in `SystemOne_repos/CLM`): bi-encoder System One on frozen Qwen3-8B + small heads | **Related work only** (author's decision, 2026-10-05). It needs vLLM on CUDA and ~16 GB for the 8B encoder, so it does not run on the M4 as shipped. Its soft-label cross-entropy over options is borrowed for ablation A3 |

Rules: same prompt content, same truncation, same machine, same decoding settings (greedy) wherever applicable; prompts of the baselines are fixed **before** looking at test results and frozen in the repo.

Experiment matrix as run on the frozen tests (2026-10-07/08):
- **Full T1 and T3**: GroundOne 0.5B / 3B; B4 MiniCheck-RoBERTa and HHEM; B1 untrained 0.5B (format a).
- **T2**: GroundOne 0.5B and 3B (full test); RoBERTa (published protocol).
- **Subsamples**: B1 untrained 3B on 600 T1 answers; B3 Rizzo-Flow 4B Q4 on 300 T1 answers and 600 T3 pairs; B0a / B0b terse and verbose judges (0.5B, 3B) on the 200 latency answers (50 per K band).
- **Baselines that do not verify the sentence against the document**: word overlap (AUROC) and the sentence-only n-gram classifier.
- **B2** on full T1, both sizes (2026-10-10). **B0d** equal-output judges on the latency subset (D25). Energy (powermetrics) on 100 latency answers. Second 0.5B run on T1, T2, T3 (D26).
- Commands: `groundone test`, `groundone baselines frozen|judges`.

---

## 8. Metrics and protocol

### 8.1 Quality
- **Balanced accuracy** (the LLM-AggreFact convention), **AUROC**, F1 on the unsupported class, per sub-dataset and macro-average.
- Threshold: **primary = fixed 0.5** (the LLM-AggreFact leaderboard protocol, so numbers are comparable with published ones); secondary = one global threshold chosen on our dev split; plus threshold-free AUROC. Never tune thresholds per test set.
- Published reference points (LLM-AggreFact leaderboard, avg BAcc, not re-run): Bespoke-MiniCheck-7B 77.4; MiniCheck-Flan-T5-L 75.0; Qwen2.5-7B-Instruct zero-shot 72.8; HHEM-2.1-open 71.8; AlignScore 70.5; Qwen2.5-0.5B-Instruct zero-shot 64.2 (51.6 on RAGTruth). Qwen2.5-3B is not listed.
- Confidence intervals via bootstrap; paired bootstrap for system differences.
- **LLM-AggreFact reporting rules** (from the sub-dataset papers, wiki page `LLM-AggreFact Sub-datasets`):
  - Report the 11-way macro average **and** a "RAG subset" average (RAGTruth, Lfqa, ClaimVerify, ExpertQA), the sub-datasets closest to local RAG.
  - Documents over the 2,048-token cap (2.4 % of test, mostly ClaimVerify and WiCE): **chunk and take the maximum P(supported) over chunks** (a claim is supported if any chunk supports it), as MiniCheck does, and report how many items needed it. No silent truncation.
  - Training data is ~90 % supported in RAGTruth while Reveal / FactCheck-GPT / WiCE are 23–31 % supported: rebalance training classes and keep the single 0.5 threshold.
  - Known noisy or ceiling-limited columns: ExpertQA (experts used world knowledge; all published models ≈ 50–61), TofuEval (κ 0.34–0.42), AggreFact-CNN (≈ 57 negatives). Differences there need a paired bootstrap before being called a win.

### 8.2 Calibration
ECE (fixed and adaptive bins), Brier, NLL, reliability diagrams, risk-coverage curves and AURC (AURC is defined in later work by Geifman et al., not the 2017 paper; cite accordingly). ECE is never reported alone (a constant predictor can have perfect ECE). For generative judges: ECE of verbalised confidence if elicited, and of the token probability of the verdict if available.

### 8.3 Latency and throughput
- Per answer (K claims) end-to-end in-process, and per claim; p50 / p90 / p99. Report prefill and per-claim suffix time separately.
- Throughput in claims/s.
- At least 200 answers per configuration, 5 warm-up runs discarded, fixed order and seed, models run one at a time, Mac plugged in, no other heavy processes, ambient state noted. Repeat each latency configuration at least 3 times and report the spread. (Latency runs are short; quality runs are done once.)
- In-process timings are primary; HTTP timings secondary (the previous benchmark mixed them).
- Latency stratified by context length and by K.

### 8.4 Resources and reliability
- Peak memory per configuration (MLX peak memory; process RSS for PyTorch baselines).
- Output-format failure rate for generative baselines (unparseable verdicts), reported as a percentage.
- Energy per verification via `powermetrics` (in scope since 2026-10-08, part of the locality pillar): joules per answer, GroundOne vs generative judges. Needs root.

### 8.5 Reporting rules
- Report all baselines, including those where we lose.
- Results files are create-only (never overwritten); each run stores config, git commit, dataset hash and hardware notes.
- **Every phase leaves figures** (author's rule, 2026-10-05): `groundone figures all` writes 300-dpi PNGs with draft captions to `Project/outputs/figures/<group>/` (phase0, eda, sweep, training-<run>, results, …). A new kind of result gets its plotting function in `GroundOne/src/groundone/figures/` in the same change; overnight queues end with `groundone figures all`. Colours are fixed per system across all figures.

---

## 9. Phases, gates and deliverables

Experiment and thesis together. The machine trains or benchmarks **at night**; daytime goes to code and writing. **Submission: 2026-11-10. Last day for new experiments: 2026-10-30.**

| Week | Dates | Experiment | Writing (`Thesis/`) | Gate at end of week |
| --- | --- | --- | --- | --- |
| **1** ✅ (ahead) | Oct 5–11 | Phase 0 + 0b ✅ (Oct 5) → **Phase 1a EDA** of ANLI and RAGTruth (`Project/experiments/eda/`) → Phase 1 data pipeline + leakage check → engine + harness; first 0.5B training run overnight | Thesis skeleton (chapters, bib); Ch. 2 Background & related work (wiki ingest ✅); Ch. 4 Data and EDA (material ready) | Datasets frozen ✅ (Oct 7); 0.5B and 3B trained, baselines and latency done (Oct 8), i.e. most of weeks 2–3 |
| **2** ✅ (done by Oct 10) | Oct 12–18 | 0.5B final run(s); 3B training overnight; baselines B0a, B1, B2 on full test sets; B0b/B0c on subsample; B4 encoders; B3 Rizzo-Flow | Ch. 3 Method (task, prompt, engine, loss, calibration) | 0.5B beats B1 on dev; 3B adapter exists |
| **3** ✅ (done by Oct 10; A3–A5 not run) | Oct 19–25 | GroundOne 3B eval; latency protocol (§8.3); calibration (temperature, reliability, risk-coverage); ablations A1/A2; error analysis | Ch. 5 Experimental setup; start Ch. 6 Results as numbers arrive | All main tables and figures generated from `outputs/results/` |
| **4** | Oct 26–Nov 1 | Stretch ablations (A3–A5) if the main matrix is complete; minimal demo (2 days max); **feature freeze Fri Oct 30** | Ch. 6 Results, Ch. 7 Discussion | Experiments closed |
| **5** | Nov 2–8 | Fixes and re-runs of already-defined experiments only; reproducibility package | Ch. 1 Introduction, Ch. 8 Conclusion, final abstract with numbers; complete draft to supervisor by ~Nov 5; revisions | Complete thesis |
| **buffer** | Nov 9–10 | – | Formatting, proofreading | **Submission Nov 10** |

Rules:
- **No new experiment after Oct 30.** Anything that misses the freeze goes to "future work".
- If a step slips by more than 2 days, cut from the bottom of the priority list: demo polish → B3 Rizzo-Flow → B0b verbose judge on the full matrix (keep the Phase 0b numbers) → 3B fine-tuning (fall back to 0.5B fine-tuned + 3B zero-shot).
- Figures and tables are produced by scripts from `outputs/results/`, never by hand, so that late re-runs do not cost writing time.

Thesis chapter outline (`Thesis/content/chapters/`, English; Italian reference version in `Thesis_ita/`; renumbered 2026-10-11):
1. Introduction (`ch1_introduction.tex`): motivation, System One vs autoregressive LLM, open problems, RQ1–RQ5, contributions
2. Local inference of language models (`ch2_local_inference.tex`): hosted vs local, open-weight and small models, cost model (prefill vs decode, roofline), hardware, runtimes and specialised engines, quantisation, energy, consequences for GroundOne
3. Background and related work (`ch3_background.tex`)
4. GroundOne: method and implementation (`ch4_method.tex`)
5. Data (`ch5_data.tex`)
6. Experimental setup (`ch6_setup.tex`)
7. Results (`ch7_results.tex`)
8. Discussion, limitations and threats to validity (`ch8_discussion.tex`)
9. Conclusion and future work (`ch9_conclusion.tex`)
Appendix: output examples. The demo (D28) goes into its own chapter or into Ch. 7/8: to decide (`demo_architecture.md` §12).

---

## 10. Phase 0: feasibility test

**Status: Phase 0 and Phase 0b done (2026-10-05).** Phase 0b: speed gain grows with K (≈2× vs terse, ≈6× vs verbose judge at K = 24); generative judges break format; zero-shot rule-following fails, so flexibility becomes a training target. Full results: `phase0_report.md`. Code and raw outputs: `Project/experiments/feasibility/`.

### 10.1 What Phase 0 ran

**Which System One was evaluated.** GroundOne does not exist yet (it is the fine-tuned model of Phases 3–4). In Phase 0 the "System One" is the **untrained baseline B1**: the stock instruction models `Qwen2.5-0.5B-Instruct` and `Qwen2.5-3B-Instruct` (MLX 8-bit conversions `lmstudio-community/Qwen2.5-*-Instruct-MLX-8bit`), used in System One mode. That means a chat prompt with the document and the claim, **one forward pass**, the logits of the two answer tokens `A` (supported) and `B` (not supported) read at the last position, and a softmax over those two only. There is no generation, no fine-tuning and no calibration. Rizzo-Flow (the general-purpose System One, B3) was not run. Phase 0 therefore measures the **starting point** of GroundOne and the cost of the System One mechanism, not GroundOne itself. The script is `Project/experiments/feasibility/scripts/02_readout.py` (accuracy), and `04_speed.py` adds the shared-prefix variant used for the speed test.

1. **Data:** LLM-AggreFact, RAGTruth, MiniCheck synthetic data and ANLI downloaded and checked. Evaluation sample of 1,780 items (§5 of the report).
2. **Zero-shot headroom:** Qwen2.5-0.5B and 3B, single-token readout (B1), on all items. The 7B was **not** run; the published leaderboard number (72.8) is used instead.
3. **Encoders (B4):** MiniCheck-RoBERTa on all items; HHEM and MiniCheck-DeBERTa on a random 150-per-set subsample. MiniCheck-Flan-T5 was stopped by the memory guard and not evaluated.
4. **Rizzo-Flow:** postponed to a daytime session (memory).
5. **Speed:** System One with and without a shared prefix vs a terse generative judge; K = 1, 3, 8; contexts of 500/1,000/2,000 tokens; 0.5B and 3B.
6. **Training probe:** 30 LoRA steps with the restricted A/B loss, at 1,024 and 2,048 tokens, 0.5B and 3B.

### 10.2 Go/no-go criteria and outcome
| # | Criterion | Outcome |
| --- | --- | --- |
| G1 | Datasets usable with human labels and acceptable licences | ✅ (RAGTruth MIT, MiniCheck data MIT, ANLI CC-BY-NC, LLM-AggreFact CC-BY-ND: fine for a thesis) |
| G2 | Zero-shot 3B readout above chance (BAcc ≥ ~0.60) | ✅ 0.760 LLM-AggreFact, 0.713 RAGTruth sentences |
| G3 | Headroom for the 0.5B against the best small encoder | ✅ MiniCheck-RoBERTa 0.759 vs 0.5B 0.595 (+16 points). The 3B zero-shot already ties the encoder on LLM-AggreFact |
| G4 | Shared-prefix System One ≥ ~1.5× faster than a terse generative judge at K = 8 | ❌ 0.9–1.1× on both sizes. **Not conclusive**: see 10.3 |
| G5 | LoRA training fits in 16 GB | ✅ peak 5.9 GB (3B, 2,048 tokens). Time is the constraint: one epoch of the MiniCheck recipe ≈ 3–4 h on the 0.5B and ≈ 17 h on the 3B (estimates) |

**Decision: GO on the task.** G4 is re-tested in Phase 0b before the thesis framing is fixed.

### 10.3 Why G4 failed, and why the test was not a fair test of the architecture
The Phase 0 speed test under-used the System One:
1. **Sequential suffixes.** The K sentences were scored one after another. The point of a System One with high K is to score all K questions **in parallel** in one batched forward pass over the shared prefix (as Rizzo-Flow and SemIf do). A generative judge cannot do that: it must emit its tokens one at a time.
2. **Long suffixes.** Each question repeated the full sentence (~40 tokens), although the answer was already in the shared prefix. A suffix of ~10 tokens ("Is sentence 3 supported?") is enough.
3. **A strong generative baseline.** The terse judge read the context once and answered all K sentences in one output of ~4–5 tokens each. Its extra cost was only ~0.2 s (0.5B) to ~1.1 s (3B). This baseline stays, but it is not the only realistic one: LLM judges in practice (RAGAS, Lynx) write a rationale before each verdict.

Unchanged by these fixes: **prefill dominates** (≈ 2.2 ms/token on the 3B, 0.37 ms/token on the 0.5B), and every method pays it. So the gain against a terse judge is bounded by its decoding time and will stay moderate on long contexts. This must be reported as it is.

### 10.4 Phase 0b: re-test centred on the System One's strengths (done 2026-10-05; results in `phase0_report.md` §B1–B3)
New aspects compared with Phase 0:

| # | What changes | Why |
| --- | --- | --- |
| N1 | **Batched suffix scoring**: the prefix KV cache is replicated across a batch of K short suffixes (padded), one forward pass, logits read at each suffix's last real token | Realises the parallelism a generative judge cannot have |
| N2 | **Short suffixes** referring to the sentence by index; the answer lives in the shared prefix | Cuts the per-question cost ~4× |
| N3 | **Higher K by construction**: several questions per sentence (supported / contradicted / relevant), K = sentences × criteria, up to 8 × 3 = 24 | High K is the natural regime of a System One; one context, many decisions |
| N4 | **Verbose generative judge** (short rationale, then verdict, per sentence) next to the terse one | It is the common LLM-as-a-judge practice; both are reported |
| N5 | Generative outputs saved and parsed: **format-failure rate** and **accuracy** of both generative judges on a subsample | Phase 0 measured only their speed |
| N6 | **Flexibility probe vs MiniCheck**, using **only existing labels** (no hand-built data): (a) **three-way question** supported / contradicted / not mentioned. On ANLI: entailment / contradiction / neutral. On RAGTruth sentences: no span / a *Conflict* span (5,525 spans) / a *Baseless Info* span (8,764 spans). (b) **Rule change in the prompt**, with gold labels derived from the same three-way labels: *strict rule* ("anything not stated in the document is unsupported": only supported = OK) vs *lenient rule* ("flag only statements that contradict the document": supported or not mentioned = OK). On RAGTruth, an optional third rule uses the `implicit_true` flag (1,928 spans): "true world knowledge is acceptable" | Shows what an encoder cannot do without retraining: MiniCheck outputs one supported/unsupported score and has no way to receive a rule |

Expected results *(estimates made before Phase 0b; measured values in the report — the verbose judge was shorter than assumed, so the measured gains vs verbose are ≈3–6×, not 7–20×)*:

| Setting | Terse judge | Verbose judge (~60 tokens/sentence) | System One, batched + short suffixes | Expected gain |
| --- | --- | --- | --- | --- |
| 3B, 1,000-token context, K = 8 | ~3.5 s (measured) | ~17 s | ~2.4–2.6 s | ~1.4× vs terse, ~7× vs verbose |
| 3B, 1,000-token context, K = 24 | ~5.7 s | ~48 s | ~2.7 s | ~2× vs terse, ~15× vs verbose |
| 0.5B, 1,000-token context, K = 8 | ~0.59 s (measured) | ~3.2 s | ~0.42 s | ~1.4× vs terse, ~7× vs verbose |
| 0.5B, 1,000-token context, K = 24 | ~1.0 s | ~9 s | ~0.45 s | ~2× vs terse, ~20× vs verbose |

General expectation: the gain **grows with K** and **shrinks with context length** (prefill is shared by all methods). Against verbose judges it is large at any K. Flexibility probe: the zero-shot 3B should follow a three-way question and a rule change above chance. MiniCheck can only be compared on the strict rule (its native task); under the lenient rule its fixed output is scored against the lenient labels, which shows the cost of not being able to change the rule.

Phase 0b criteria *(provisional)*:
| # | Criterion |
| --- | --- |
| G4b | Batched System One ≥ 1.5× faster than the terse judge at K = 24, and ≥ 3× faster than the verbose judge at K = 8 (1,000-token context, both sizes) |
| G4c | The gain increases monotonically with K |
| G6 | Zero-shot 3B three-way BAcc clearly above chance (≥ ~0.45 for 3 classes), and under the lenient rule it beats MiniCheck's fixed score on the lenient labels (i.e. it actually follows the rule) |

If G4b fails even with batching: the speed argument is limited to rationale-writing judges and the thesis says so; the core claims become specialisation, flexibility and calibration. If G6 fails zero-shot: flexibility becomes a training target (multi-question data) rather than a zero-shot property, or is dropped.

### 10.5 Fallback use cases (not needed: Phase 0 said GO)
A privacy gate before cloud LLM calls (multi-label, K ≈ 10 categories); prompt-injection scanning for local agents (K = 1, latency/threshold story); chunk relevance grading (against cross-encoder rerankers).

---

## 11. Demo specification

**Superseded by `demo_architecture.md` (D28, 2026-10-18).** In short: a native macOS app (Swift, SwiftUI, MLX Swift) running retrieval (SQLite FTS5, optional embeddings), the Qwen2.5-3B-Instruct generator (D12) and GroundOne in one process; every answer sentence coloured by the served rule (D27); flagged sentences rewritten from the document and re-verified up to a policy limit; strict/lenient policies, audit log, a measurement mode (generation vs verification time, revision rounds, peak memory) and a comparison mode with a terse generative judge. The GroundOne port is gated by a conformance test against the Python probabilities; if it fails by 2026-10-24, the app calls the existing `groundone serve` on localhost instead.

Changes with respect to the first spec (2026-10-04): native app instead of a web page; regeneration of flagged sentences moved from future work into the demo; time budget about six working days instead of two (to confirm, `demo_architecture.md` §12).

---

## 12. Risks, threats to validity and mitigations

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Encoders (MiniCheck/HHEM) beat the System One on accuracy and speed on the plain task | High | Medium | Expected; reported. The comparison that matters is RQ5 (three-way question and rules), which encoders cannot express |
| Gain over a terse judge is small at low K and long contexts (prefill dominates) | Certain | Medium | Measured in Phase 0b: report the full curve over K and context length, including where the gain vanishes |
| Training on rules does not transfer (model memorises label mapping) | Medium | Medium | Hold out rule × dataset combinations; evaluate rules on ANLI dev, which is not used for training |
| 3B does not fine-tune at long contexts within 16 GB | Medium | Medium | Length cap, 4-bit base, smaller rank, shorter K; or ship 0.5B-only plus 3B zero-shot |
| Label noise / derived sentence labels in RAGTruth | Medium | Medium | Document the derivation rule (EDA, Phase 1a), report on LLM-AggreFact pairs where labels are native |
| Training/test leakage | Medium | High | Hard-coded leakage check in the dataset build; split by source ID |
| Qwen2.5 pre-training contamination of public benchmarks | Unknown | Low–Medium | State as a limitation |
| Timing noise (thermal throttling, background processes) | High | Medium | Protocol in §8.3; repeated runs; report spread |
| Rizzo-Flow cannot run on the Mac or with Qwen | Medium | Low | Present as external reference with its own model; checked in a daytime session (not done in Phase 0) |
| Fixed-size answer slots irrelevant here (binary) but position bias still possible | Low | Low | Fixed mapping + fine-tuning; test by swapping letter order on a dev subset |
| Demo port to Swift takes longer than planned (D28) | Medium | Medium | Conformance test as a gate (M1); fallback to the existing local HTTP server; demo polish first on the cut list |
| Scope creep (demo, extra datasets, 7B fine-tune) | High | High | Anything not tied to RQ1–RQ5 or the demo is a stretch item; revisit at each gate |
| **Schedule: one month for experiment and thesis** | High | High | Night-time runs, experiment freeze Oct 30, cut list in §9, writing in parallel from week 1, scripted figures |
| 3B training too slow to finish overnight | High (≈17 h per full epoch, measured) | Medium | Train the 3B on a ~10K subset; fall back to 0.5B fine-tuned + 3B zero-shot |
| The Mac freezes during unattended runs | Low (since the guard) | High | Every long job runs under `groundone guard` (`tools/watchdog.py`: kills a job when free memory or swap growth crosses the limits in `outputs/logs/guard/thresholds.json`) |

Threats to validity to discuss in the thesis: benchmark representativeness for *local* RAG, single hardware platform, few seeds for the 3B, prompt sensitivity of the baselines (mitigated by freezing prompts before testing), possible pre-training contamination.

---

## 13. Repository layout and reproducibility

Implemented structure (2026-10-05, D19), modelled on Rizzo-Flow: an installable package with a CLI and an HTTP API. Usage: `Project/GroundOne/README.md`.

```
Project/                     # experiment workspace (restructured 2026-10-08; map in Project/README.md)
  GroundOne/                 # the software (installable package, own .venv)
    pyproject.toml, README.md
    configs/                 # train_0.5b.yaml, train_3b.yaml (copied into each run)
    src/groundone/
      prompts.py             # prompts: design (a) questions, design (b) encode_marked (training = inference)
      readout.py             # design (b): output head applied at marker positions only
      backend.py             # MLX model + adapter: score_positions (b), score_shared / score_many (a)
      engine.py, api.py, schema.py, compat.py, cli.py, playground.html   # service, HTTP API (design b, D27), CLI, UI
      calibration.py         # temperature + bias per key, bound to the model fingerprint
      data/                  # build.py (dataset + checks), segment.py (pysbd + content rule), leakage.py, shortcut.py, rows.py (design a)
      training/train.py      # LoRA loop, design (b) default
      eval/                  # tests.py (frozen T1/T2/T3, B2), calibrate_b.py, bootstrap.py, metrics.py; evaluate.py = legacy (v1 data)
      baselines/             # frozen.py (encoders, Rizzo-Flow), judges.py (generative judges + latency); encoders.py / rizzo.py legacy entry points
      figures/               # dataset, benchmarks, training, phase0 (+ legacy results, diagnostics)
      tools/                 # watchdog.py (memory guard), matrix.py (results matrix), power.py (powermetrics)
    tests/
  data/                      # download.py + manifests; raw/ and processed/groundone/ (jsonl gitignored; manifest, reports, DATACARD tracked)
  outputs/                   # generated by the groundone commands
    models/                  # trained adapters (gitignored): g1-05b-b1, g1-05b-s3 (run 2), g1-05b-s2 (stopped, D26), g1-3b-b1
    results/                 # metrics.json tracked, predictions gitignored; one folder per system (latency/ inside)
    figures/                 # thesis figures (PNG + captions)
    logs/                    # memory-guard logs (gitignored)
  experiments/               # one-off studies: feasibility/ (Phase 0/0b scripts, data, results), eda/ (scripts, report)
  jobs/                      # guard queues and job scripts (records of the runs)
  envs/                      # auxiliary venvs (gitignored): hhem/ (transformers < 4.50), feasibility/
  docs/  _archive/ (earlier experiments, gitignored)
```

Reproducibility rules: one config file per run; fixed seeds; dataset and prompt hashes stored with results; results never overwritten; one git tag per reported experiment; `uv` for environments.

**What carries over from `Project_old/`:** the single-thread MLX worker pattern, letter-token mapping, FastAPI skeleton and LoRA/plot scripts (as references). **What does not:** the BFCL datasets, v1–v3 results, the routing benchmark numbers. **Lessons applied:** no train/test overlap (§5, `dataset_plan.md`), prompt masking in training (D5), in-process timing (§8.3), a same-size single-token control (B2), and no flat-latency claim without measurement (§4.3).

---

## 14. Open questions for the author

Answered: D1 confirmed; no hand-labelled set (D10); submission 2026-11-10, experiments until 2026-10-30; encoder baselines (B4) yes; CLM related work only.

Also answered: Phase 0/0b run (GO); demo generator = 3B (D12); 7B not run (D13).


Still open (updated 2026-10-18):
1. ~~B2 control~~: done 2026-10-10 on full T1 (readout +0.25 / +0.07 over the generated token; §2 H2a).
2. ~~T2 for the 3B~~: done 2026-10-09 (macro 74.8).
3. ~~Bootstrap confidence intervals~~: done 2026-10-09 (`groundone bootstrap`, `results/bootstrap/`). Every claimed difference is significant except: T2 macro 3B vs MiniCheck-RoBERTa (+0.8, CI −0.5 to +2.1), T2 RAG subset 0.5B vs RoBERTa, T1 AUROC 0.5B vs Rizzo-Flow on its subsample.
4. ~~HTTP API on design (b)~~: done 2026-10-10 (D27). Optional extension (grounded ingestion loop for an LLM wiki, `thesis_notes.md` Ch. 8) still open.
5. ~~Supervisor requirements~~: none specific (author, 2026-10-11); target 120–150 pages.
6. **Demo (D28)**: name, generator (separate 4-bit or shared base), retriever, repository location, thesis placement, evaluation of the revise loop, segmentation port, time budget. Listed in `demo_architecture.md` §12 (2026-10-18).

---

## 15. References (verified 2026-10-05, copies in `Vault/raw/`)

Authors, years and venues were checked against arXiv, the ACL Anthology and AAAI. The PDFs and page copies are in `Vault/raw/` and are ingested into the wiki (`Vault/wiki/`). Cite the **publication** year, not the arXiv year.

**System One (grey literature: blogs and repositories, cite as such)**
- TypeSafe, *Introducing System One models and Jev* (blog, 2026). Other Jev sources are already in the wiki.
- SemIf (github.com/TheoLeeCJ/SemIf): `SemIf README.md`, `SemIf RESULTS.md`.
- Rizzo-Flow (github.com/Rizzo-AI-Academy/rizzo-flow): `Rizzo-Flow README.md`, `Rizzo-Flow training.md`.
- Kwok, Kang, Suresh, Saad-Falcon, Pavone, Ré, Mirhoseini (2026). *Contrastive Language Models: A System One Model for Fast and Generalizable Decision-Making*. Notion blog (contrastive-lm.notion.site), Stanford / NVIDIA Research. The Notion subtitle says "Approach" where the README says "Model". Not peer-reviewed.

**RAG, verification, judges**
- Lewis et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. NeurIPS 2020.
- Niu et al. (2024). RAGTruth: A Hallucination Corpus for Developing Trustworthy Retrieval-Augmented Language Models. ACL 2024.
- Tang, Laban, Durrett (2024). MiniCheck: Efficient Fact-Checking of LLMs on Grounding Documents. EMNLP 2024. Introduces LLM-AggreFact. The leaderboard (llm-aggrefact.github.io, saved 2026-10-05) lists MiniCheck-FT5-L 75.0, HHEM-2.1-open 71.8 and AlignScore 70.5 balanced accuracy.
- Zha, Yang, Li, Hu (2023). AlignScore: Evaluating Factual Consistency with a Unified Alignment Function. ACL 2023.
- Vectara (2024). HHEM-2.1-Open, model card (HF `vectara/hallucination_evaluation_model`, flan-t5-base).
- Es, James, Espinosa-Anke, Schockaert (2024). RAGAs: Automated Evaluation of Retrieval Augmented Generation. EACL 2024 System Demonstrations.
- Saad-Falcon, Khattab, Potts, Zaharia (2024). ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems. NAACL 2024.
- Ravi et al. (2024). Lynx: An Open Source Hallucination Evaluation Model. arXiv preprint.
- Zheng et al. (2023). Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. NeurIPS 2023 Datasets and Benchmarks.
- Asai et al. (2024). Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection. ICLR 2024.
- Nie et al. (2020). Adversarial NLI. ACL 2020. Williams, Nangia, Bowman (2018). A Broad-Coverage Challenge Corpus for Sentence Understanding through Inference. NAACL 2018.

**Models and fine-tuning**
- Hu et al. (2022). LoRA: Low-Rank Adaptation of Large Language Models. ICLR 2022.
- Dettmers et al. (2023). QLoRA: Efficient Finetuning of Quantized LLMs. NeurIPS 2023.
- Qwen Team (2024). Qwen2.5 Technical Report. arXiv:2412.15115.
- Apple, MLX and `mlx-lm` (software; cite the repositories).

**Calibration and selective prediction**
- Naeini, Cooper, Hauskrecht (2015). Obtaining Well Calibrated Probabilities Using Bayesian Binning. AAAI 2015. This is where ECE comes from.
- Guo, Pleiss, Sun, Weinberger (2017). On Calibration of Modern Neural Networks. ICML 2017.
- Kadavath et al. (2022). Language Models (Mostly) Know What They Know. arXiv preprint.
- Tian et al. (2023). Just Ask for Calibration: Strategies for Eliciting Calibrated Confidence Scores from Language Models Fine-Tuned with Human Feedback. EMNLP 2023.
- Geifman, El-Yaniv (2017). Selective Classification for Deep Neural Networks. NeurIPS 2017.

**Datasets and their sources** (dataset cards and papers in `Vault/raw/`, verified 2026-10-05)
- Dataset cards: `facebook/anli` (CC BY-NC 4.0), `lytang/LLM-AggreFact` (CC BY-ND 4.0, gated, evaluation only), `lytang/C2D-and-D2C-MiniCheck` (MIT), RAGTruth GitHub README (MIT).
- RAGTruth sources: Nguyen et al. (2016). MS MARCO: A Human Generated MAchine Reading COmprehension Dataset. arXiv:1611.09268 (CoCo@NIPS 2016) [QA]. See, Liu, Manning (2017). Get To The Point: Summarization with Pointer-Generator Networks. ACL 2017 [CNN/DailyMail as cited by RAGTruth]; Hermann et al. (2015). Teaching Machines to Read and Comprehend. NeurIPS 2015 [original CNN/DailyMail]. Yelp Open Dataset (web page, no paper) [Data2txt].
- LLM-AggreFact sub-datasets: Tang et al. (2023). Understanding Factual Errors in Summarization: Errors, Summarizers, Datasets, Error Detectors. ACL 2023 [AggreFact-CNN/XSum]. Tang et al. (2024). TofuEval: Evaluating Hallucinations of LLMs on Topic-Focused Dialogue Summarization. NAACL 2024 [TofuEval-MediaSum/MeetingBank]. Kamoi et al. (2023). WiCE: Real-World Entailment for Claims in Wikipedia. EMNLP 2023. Jacovi et al. (2024). A Chain-of-Thought Is as Strong as Its Weakest Link: A Benchmark for Verifiers of Reasoning Chains. ACL 2024 [REVEAL]. Liu, Zhang, Liang (2023). Evaluating Verifiability in Generative Search Engines. Findings of EMNLP 2023 [ClaimVerify]. Wang et al. (2024). Factcheck-Bench: Fine-Grained Evaluation Benchmark for Automatic Fact-checkers. Findings of EMNLP 2024 [FactCheck-GPT]. Malaviya et al. (2024). ExpertQA: Expert-Curated Questions and Attributed Answers. NAACL 2024. Chen, Xu, Arora, Choi (2024). Understanding Retrieval Augmentation for Long-Form Question Answering. COLM 2024 [LFQA].

**Inference background**
- Pope et al. (2023). Efficiently Scaling Transformer Inference. MLSys 2023.
- Kwon et al. (2023). Efficient Memory Management for Large Language Model Serving with PagedAttention. SOSP 2023.
