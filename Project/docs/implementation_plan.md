# Implementation Plan: GroundOne (working title)

A specialist System One for local RAG: single-pass, calibrated groundedness verification with compact Qwen2.5 models on a 16 GB Apple Silicon laptop.

> **Status:** v0.5 (2026-10-05). Phase 0, 0b, 1a (EDA) and 1 (datasets v1) are done (`phase0_report.md`, `Project/EDA/report/eda_report.md`, `phase1_report.md`). Next: Phase 2 (engine + evaluation harness) and the first 0.5B training run.
> **Hard constraint: the experiment *and* the written thesis (`Thesis/`) must be done by the submission date, 2026-11-10. New experiments only until 2026-10-30.** The schedule (§9) and the scope cuts (§1.5) follow from this.
> Every number marked *(estimate)* or *(provisional)* is a planning figure to be replaced by a measurement.
> Companion document: `abstract.md`.

---

## 0. How to use this document

- It is the compass for the whole experiment: if a task is not traceable to a research question (§2), it is out of scope.
- Decisions that the author must confirm are tagged **[DECIDE]**. Open questions are collected in §14.
- Phases and gates are in §9 and §10. Phase 0/0b (feasibility) said **GO** on 2026-10-05. A one-page tracker is in `Phases&ToDos.md`.
- Update this file whenever a decision changes. Never silently change the experiment: add a line to the decision log (§3).

---

## 1. Goal and scope

### 1.1 Thesis statement
A compact language model, fine-tuned to do **one thing** (verify the sentences of a RAG answer against the retrieved context) and used as a **System One** (one forward pass, logit readout, no text generation), can (i) answer **many questions over one shared context in parallel**, faster than a generative judge and always in a valid format, (ii) approach the accuracy of larger models after specialisation, (iii) follow a small set of verification rules given in the prompt, which a fixed encoder cannot, and (iv) give probabilities calibrated well enough to be used as thresholds, all on a laptop.

This is a hypothesis. The thesis is valid whether it is confirmed or not, provided the comparison is controlled and honest.

### 1.2 The task (one decision, done well)
**Groundedness verification for RAG.** Input: a retrieved context `C`, a generated answer `A` split into sentences `s_1..s_K`. Output: for each `s_i`, `P(supported | C, A, s_i)`.

- **Core question** (binary): supported / not supported. **Additional questions on the same sentence** (decided after Phase 0b): a three-way question (supported / contradicted / not mentioned) and two verification rules written in the prompt (strict: anything not stated is an error; lenient: only contradictions are errors). They raise K naturally (sentences × questions) and are where an LLM-based System One can do what an encoder cannot. Zero-shot the models do not follow them, so they are **trained**. The probability is the product; there is no abstain class; uncertainty is handled with thresholds (selective prediction).
- This is the **narrowing of use case B** discussed with the author: one task (groundedness of answer sentences), not chunk relevance. Reason: a shared long context with several short questions occurs naturally (the shared-prefix advantage, §4.3). Per-chunk relevance grading does not have this structure.

### 1.2b Where each advantage comes from (spine of the method chapter)
GroundOne is a Qwen2.5 model used in System One mode **plus** task-specific training. The two parts bring different gains, and the thesis must keep them apart:

| Advantage | Source | Already present in the untrained model (B1)? |
| --- | --- | --- |
| Speed vs a generative judge; K questions scored in parallel over one shared context | The **System One mechanism** (single pass, logit readout, shared prefix, batched suffixes) | Yes: it only has to be implemented well (Phase 0b) |
| Accuracy | **Training** (GroundOne) | No: the 0.5B is ~16 points below the encoders zero-shot |
| Reliable probabilities (calibration) | Training + temperature scaling | No: zero-shot ECE 0.22–0.32 |
| Three-way answers and rule changes in the prompt | Training on the three-way format (zero-shot ability measured in Phase 0b) | Partly |
| Speed vs a **larger** model of equal quality | Training: a 0.5B that matches the 3B is ~6× cheaper per decision | Only if training works |

Fine-tuning does **not** change latency: after LoRA merging, GroundOne runs exactly the same computation as B1.

### 1.2c What makes GroundOne a specialist (vs general-purpose System Ones such as Rizzo-Flow, SemIf, Jev)
1. **Data:** trained only on claim-vs-document verification (MiniCheck data, ANLI, RAGTruth train), not on generic typed decisions.
2. **Question space:** a fixed, narrow set of questions (supported / contradicted / not mentioned, plus the strict and lenient rules), instead of arbitrary questions and primitives.
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
| Extensions | E1, E2 | E1 cut. **E2 (rules in the prompt) promoted to the core experiment** after Phase 0b (D15) |
| Slow baselines (B0b verbose judge) | full test sets | **stratified subsample** (e.g. 300–500 items), stated in the thesis. B0c (7B) not run (D13) |
| Training sources | 3–4 sources | MiniCheck recipe (C2D + D2C + hard ANLI) + RAGTruth train; three-way and rule labels from ANLI and RAGTruth (final mix after the EDA, Phase 1a) |
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
| RQ5 | **Flexibility vs the strongest cheap alternative.** What can a System One do that a specialised encoder (MiniCheck, HHEM) cannot? | H5: on the plain binary task the encoder ties or wins (expected, and reported). After training, GroundOne answers the three-way question and follows the strict/lenient rules (gold labels from ANLI and RAGTruth), which MiniCheck's single fixed score cannot express; zero-shot it does not (Phase 0b). |

Success levels:
- **Minimum viable thesis:** controlled comparison completed, honest decomposition of gains (H2b/H2c are already supported by Phase 0b), working demo, even if the encoder wins on the plain task.
- **Target:** H1 (0.5B), H2b, H2c, H3 and H5 confirmed.
- **Stretch:** streaming verification in the demo; implicit-truth rule (RAGTruth `implicit_true`).

---

## 3. Key design decisions (decision log)

| # | Decision | Rationale | Alternatives considered |
| --- | --- | --- | --- |
| D1 | Task = groundedness (support) verification, binary | Natural shared context + K short questions; public human-labelled data; real local-RAG need | Chunk relevance (no shared-state structure; strong cross-encoder rivals); prompt-injection detection (K = 1, noisier labels); privacy filter (mostly synthetic labels) |
| D2 | Models: Qwen2.5 0.5B and 3B Instruct (fine-tuned); 7B zero-shot baseline only | Fits 16 GB; matches author's size plan | 7B fine-tuning (memory with long contexts) |
| D3 | Two answer tokens (`A` supported / `B` not supported), fixed mapping | Single-token readout; fine-tuning removes most position bias | Random option order (adds noise for a 2-way task); `Yes/No` words (tokenisation variants) |
| D4 | Custom MLX engine with prefix KV cache and per-claim suffix evaluation | Needed to realise the shared-context advantage; the old LightningRoute engine had none | Using Rizzo-Flow as the engine (not our contribution) |
| D5 | Custom training loop: cross-entropy over the restricted answer logits, prompt masked | `mlx_lm` rejects prompt masking for the `text` format; previous runs trained on every prompt token (label < 1 % of the loss) | `mlx_lm.lora` with completion format + `mask_prompt` as a first version |
| D6 | Calibration = temperature scaling fitted on a held-out dev set | One parameter, no leakage risk if dev is separate from test | RLCD (out of scope), isotonic (needs more data) |
| D7 | English only | Author's decision | Italian |
| D8 | Demo = local RAG chat app with coloured sentences and a threshold slider | Author's decision | CLI only |
| D9 | Always include the two "honest controls": same-size single-token LLM, and a specialised encoder | They are the comparisons a reviewer will ask for | – |
| D10 | No hand-labelled local set | Author's decision (2026-10-04): no time | Small manual set |
| D11 | One-month scope cuts (§1.5) | Deadline: experiment + thesis in one month | Full plan |
| D12 | Demo generator = Qwen2.5-3B-Instruct | Memory: 3B generator + verifier fits 16 GB | 7B 4-bit (too tight) |
| D13 | 7B not run; published leaderboard number used as reference | Memory and time; the number exists | Run 7B 4-bit zero-shot |
| D14 | Engine scores the K questions in one **batched** pass (prefix KV cache replicated K times, short index-based suffixes) | Phase 0: sequential suffixes erased the System One advantage; Phase 0b: batched is exact (|Δp| = 0) and 2–6× faster than generative judges at K = 24 | Sequential suffixes with cache trimming |
| D15 | Three-way question and strict/lenient rules become part of GroundOne's question set and of its **training data** | Phase 0b: zero-shot models do not follow rules; this is the flexibility claim vs encoders | Drop flexibility; keep it zero-shot only |
| D17 | Fine-tune **both** 0.5B and 3B; compare at the end | Author's decision: let the results pick the better trade-off | 0.5B main + 3B zero-shot reference |
| D18 | LLM-AggreFact is used only to evaluate: no training, and no fitting of temperature, threshold or model selection on any of its splits | Its HF gating condition forbids using it for pretraining or fine-tuning; fitting on it would also make our numbers incomparable with the leaderboard | Fit temperature on its dev |
| D19 | GroundOne is an installable package with CLI and HTTP API (native `/v1/verify` + TypeSafe/Jev-compatible `/v1/systemone`, the contract Rizzo-Flow serves) | Author's requirement; evaluation, demo and server share one engine; drop-in replacement for Rizzo-Flow/Jev clients | Loose scripts |
| D16 | Phase 1a: exploratory data analysis of ANLI and RAGTruth before building the training mix | Decide which dataset serves which question, length caps, label rules | Build the mix directly |
| D20 | Data v2: every training item with a three-way class appears with **all four questions** (sup, three, strict, lenient) | v1 (one random question per row) taught the rules as label priors: lenient ≈ always "acceptable", "not mentioned" never predicted (analysis_2026-10-06 §3.2) | Reweight question types only |
| D21 | Data v2: ~55 % of rows in the multi-sentence format: synthetic ANLI answers (3–12 hypotheses of one premise, up to 3 targets each) + class-balanced RAGTruth sentences with long answers (K ≥ 14) weighted ×2; MiniCheck kept as pairs | v1: −6 points in the multi-sentence format on the same sentences, K ≥ 14 below chance | RAGTruth only (labels noisier, fewer items) |
| D22 | Fixed dev `dev_mix` (all four questions, blocks ANLI pair / ANLI multi / RAGTruth / MiniCheck); best checkpoint = highest mean balanced accuracy over (block, question) | v1 dev (one random question, plain accuracy, loss selection) was noisy and hid the unlearned lenient rule | Dev loss |
| D23 | Calibration: temperature **and bias** per question type and per prompt format (pair / multi), fitted on dev; report balanced accuracy at the fixed 0.5 threshold | v1 probabilities squeezed around 0.5 and shifted: temperature alone cannot move the decision boundary | Temperature only; per-task thresholds (task unknown at inference) |
| D24 | (Optional, not in v2) negation balancing of ANLI rows | Claim-only baseline 0.56 on ANLI train but 0.36–0.39 on dev/test: cue does not transfer, low priority | – |
| D25 | Run order: 0.5B on v2 first (same hyper-parameters as v1, so v1 vs v2 is an ablation), the 3B on v2 only if the 0.5B v2 improves | Cheapest test of D20–D23 before spending a night on the 3B | 3B on v1 data |

Record future changes below (date, decision, reason).

- 2026-10-04: D1 confirmed by the author (single task: sentence-level groundedness). D10, D11 added.
- 2026-10-05: submission date 2026-11-10; experiment freeze 2026-10-30. Encoder baselines (B4) approved. CLM = related work only (not a baseline). D12–D16 added after Phase 0/0b.
- 2026-10-05: **D17**: both the 0.5B and the 3B are fine-tuned and evaluated in parallel; the thesis reports which one is the better trade-off. The 3B is trained on a ~10K subset to fit one night.

---

## 4. System design

### 4.1 Prompt format
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

- The full numbered answer is part of the prefix, so pronouns in sentence *i* can be resolved; the suffix only names the sentence index and the question (~10–25 tokens). This is the Phase 0b format (`phase0/scripts/s1engine.py`, `06_speed_batched.py`); the exact wording is frozen in Phase 2.
- For pair-style benchmarks (LLM-AggreFact: `document`, `claim`) the answer *is* the claim and K = 1. The shared-prefix saving only appears on RAGTruth-style responses and in the demo.
- **Boundary rule:** the engine tokenises each full prompt and takes the **longest common token prefix** as the shared part, so BPE merges at the boundary cannot cause mismatches. Unit test: batched probabilities equal one-pass-per-question probabilities (Phase 0b: max |Δp| = 0.00000).

### 4.2 Engine (MLX)
```
engine.verify(context, answer_sentences, questions) -> [P(answer)_k for k in 1..K]
 1. build the K prompts, take the common token prefix, prefill it once   (cost ~ prefill(S))
 2. replicate the prefix KV cache K times along the batch axis
 3. run the K short suffixes as ONE right-padded batch
 4. at each suffix's last real token read the logits of the allowed letters -> softmax / T
 5. return probabilities (+ timings: prefill_ms, batch_ms)
```
- Restricted softmax over the two answer tokens, divided by a calibrated temperature `T`.
- Batched by design (D14). Implementation: `GroundOne/src/groundone/backend.py` (prototype: `phase0/scripts/s1engine.py`). Memory: the replicated cache costs K × prefix × ~36 KiB/token on the 3B (≈ 1.7 GB at K = 24, 2,000 tokens).
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
1. Train with cross-entropy on the restricted 2-way logits (§6).
2. Fit a temperature `T` on a dev split that is disjoint from both train and test, by minimising NLL.
3. Report ECE (15 bins and adaptive bins), Brier, NLL, reliability diagrams, before/after `T`.
4. Optional: Platt scaling on the logit difference if `T` alone is insufficient.
5. Selective prediction: accuracy vs coverage curve, AURC. This is what makes the probability useful (e.g. flag a sentence only if `P(supported) < τ`).

---

## 5. Data

All sources are public with human labels. Access, sizes and licences were confirmed in Phase 0 (2026-10-05). **The EDA of Phase 1a is done** (`Project/EDA/report/eda_report.md`, usability table in its §2); its recommendations are the starting point of Phase 1. Key constraints from it: LLM-AggreFact is **evaluation-only** by licence (no training, no fitting of temperature/threshold on it); the LLM-AggreFact-RAGTruth **dev** part is RAGTruth **train**; RAGTruth test = LLM-AggreFact-RAGTruth test (report once); training cap 2,048 tokens; ANLI training pairs whose premise appears in ANLI dev/test are excluded.

### 5.1 Evaluation sets (never used for training or threshold tuning)
| Set | What it is | Use |
| --- | --- | --- |
| **LLM-AggreFact** | Human-labelled (document, claim) pairs from 11 datasets (leaderboard version on HF, incl. RAGTruth); **30,420 dev / 29,320 test**; partial support counts as unsupported; HF access gated (granted); licence CC-BY-ND 4.0 | Main out-of-distribution benchmark. **Licence/gating condition: evaluation only — it may not be used for pretraining or fine-tuning any model.** Therefore nothing is fitted on it either (no temperature, threshold or model selection on its dev split); dev is at most a sanity check, and never its RAGTruth part |
| **RAGTruth (test split)** | 2,965 instances / 17,790 responses (43.1 % hallucinated) from 6 LLMs, QA / summarisation / data-to-text; character-span annotations of 4 types (Evident/Subtle × Conflict/Baseless Info); train 15,090 / test 2,700 responses; **no dev split**; licence MIT (GitHub repo) | Main in-domain RAG benchmark. Sentence labels derived from spans (rule: *unsupported* if the sentence overlaps any span). Spans flagged `implicit_true` and `due_to_null` are handled by an explicit, documented rule (default: keep them as unsupported, report a variant without them). Document the version used (Lynx reports a different test size) |

(A hand-labelled local set was planned and cut for time, D10.)

LLM-AggreFact contains RAGTruth data: the RAGTruth **train** split may be used for training only if no RAGTruth test item reaches the training set, and results on the LLM-AggreFact RAGTruth subset must be reported separately.

### 5.2 Training sources *(availability and licences verified in Phase 0; final mix after the EDA)*
| Source | Role | Mapping to labels |
| --- | --- | --- |
| **MiniCheck training recipe (default)**: 7,076 C2D + 7,319 D2C synthetic examples + a 21K hard ANLI subset (≈35K) | Multi-sentence documents with claims; same data as the strongest small baseline, so the comparison with MiniCheck is data-matched | as released; ANLI neutral/contradiction → not supported |
| ANLI (full) / MNLI | Only if needed; MiniCheck found more ANLI did not help and AlignScore found NLI-heavy data can hurt | entailment → supported; else not supported |
| RAGTruth train split | In-domain RAG responses; dev carved out of it **grouped by instance** | sentence-level derived labels |
| ANLI (three-way) and RAGTruth spans | Three-way question and strict/lenient rules (D15) | entailment / contradiction / neutral; RAGTruth: no span / Conflict / Baseless Info |

Target size: ≈35K (MiniCheck recipe) plus a RAGTruth-train share and the three-way/rule examples, decided after the EDA, class-balanced, with a length cap that keeps the full prompt within the memory budget (§6.3).

### 5.3 Splitting and leakage rules (hard requirements)
The previous experiment's test set shared 880 of 1000 queries with the training set. This must not happen again.

1. Split by **source document/example ID** before any augmentation, oversampling or duplication.
2. A `check_leakage.py` script runs on every dataset build and **fails** if any evaluation example (by ID, and by normalised-text hash of context+claim) appears in training or dev. It must be part of the build, not a manual step.
3. Fixed random seeds; dataset builds are deterministic and hashed; the hash is stored with every result.
4. Dev (for temperature and threshold) is carved out of the training sources, never from the test benchmarks.
5. Contamination of Qwen2.5's own pre-training data cannot be excluded; state this as a limitation.

---

## 6. Training plan

### 6.1 Setup
- Base: `Qwen2.5-0.5B-Instruct` and `Qwen2.5-3B-Instruct`, MLX 8-bit for both (the Phase 0 probe fit the 3B at 2,048 tokens in 5.9 GB).
- Method: LoRA on **all linear layers of all blocks** (QLoRA found adapter coverage matters more than rank; the old configs adapted only 8 blocks; `mlx_lm` defaults to the last 16 blocks), rank 8–16. Avoid a 4-bit base if memory allows: Rizzo-Flow measured a 14-point weaker starting point with an NF4 base.
- **Licence note:** Qwen2.5-3B is under the *Qwen Research* licence (not Apache-2.0, unlike 0.5B/1.5B/7B). Fine for thesis research; check its terms before publishing 3B adapters. Qwen2.5-1.5B is the nearest Apache-2.0 alternative.
- Training hardware: the M4 / 16 GB machine. Use gradient checkpointing, batch size 1 with gradient accumulation.

### 6.2 Loss
- Position: last prompt token. Logits restricted to the allowed answer letters (`A`/`B`, or `A`/`B`/`C` for the three-way question). Loss = cross-entropy of that restricted softmax against the gold label.
- All prompt tokens are masked: the label is the only supervised signal.
- Optional variants (ablation A3): soft labels where annotator agreement exists; full-vocabulary cross-entropy on the label token instead of the restricted softmax.
- Implemented as a custom MLX loop (`groundone train --config train_0.5b.yaml`, `GroundOne/src/groundone/training/train.py`; hyper-parameters in `GroundOne/configs/*.yaml`, copied into each run): `mlx_lm.lora`'s data pipeline is incompatible with the installed `transformers` 5.x. Length-bucketed batches under a token budget, gradient accumulation, warm-up + cosine LR, dev evaluation every 250 steps, best checkpoint kept, adapters saved in MLX format.

### 6.3 Memory and length
The risk is long contexts. Rules of thumb *(to measure)*:
- Cap training prompts at 1,024 tokens first, then try 2,048. RAG use in the demo is top-3 chunks of 300–500 tokens plus the answer.
- Measure peak memory with the MLX peak-memory API at a few lengths before launching a long run.
- If the 3B does not train at the target length, fall back to 4-bit base (QLoRA-style), shorter cap, or smaller rank, and document it.
- Training time (Phase 0 probe, measured per token): one epoch of ≈35K MiniCheck-length examples ≈ 3–4 h on the 0.5B and ≈ 17 h on the 3B. The 3B must be trained on a subset (~10K examples ≈ one night).

### 6.4 Procedure
1. Sanity run: 0.5B on a small subset; loss must decrease; the engine's output must equal the training-time computation (same prompt, same logits within tolerance).
2. Hyper-parameter sweep (small): learning rate, rank, epochs, on the 0.5B only; selection on dev only.
3. Final runs: 0.5B (2 seeds if time allows, else 1), 3B (1 seed, launched overnight). Report mean ± std where seeds exist and state the single-seed limitation otherwise.
4. Save adapters, configs, loss curves, dataset hash, git commit for every run.

### 6.5 Ablations and extensions
**A1 and A2 are required.** A3–A5 run in week 4 only if the main experiment matrix is complete (§1.5, §9). E1 is future work; E2 is now part of the main experiment (D15). Results go in thesis §6.4.

| ID | Experiment | Purpose |
| --- | --- | --- |
| A1 | Base vs fine-tuned, same readout | Isolates the effect of fine-tuning |
| A2 | Readout vs single-token generation, same fine-tuned weights | Confirms equivalence (H2a) |
| A3 | Restricted-softmax vs full-vocab loss; hard vs soft labels | Effect of the loss on calibration |
| A4 | Training-set size curve (e.g. 5k / 10k / 20k / all) | Data efficiency |
| A5 | Prefix with and without the full answer | Value of context for resolving references |
| E1 (stretch) | Sentence-level vs claim-decomposed verification | Granularity |
| E2 (**core**, D15) | **Rules in the prompt**: strict vs lenient definition of an error, gold labels derived from ANLI / RAGTruth three-way labels; compare with encoders that cannot take a rule | RQ5 |

---

## 7. Baselines (a ladder that isolates each effect)

| ID | System | What it isolates |
| --- | --- | --- |
| B0a | Qwen2.5 0.5B / 3B zero-shot, **terse generative judge**: one line '<id>: yes/no' per decision, greedy | Typical practice at the same size |
| B0b | **Verbose generative judge**: one sentence of reasoning, then 'Verdict: yes/no', per decision | The common LLM-as-a-judge practice (RAGAS, Lynx); largest latency gap |
| B0c | Qwen2.5-7B-Instruct zero-shot, **published number only** (72.8 on LLM-AggreFact), not run (D13) | Larger-model reference for H1 |
| B1 | Same base models, **single-token readout, no fine-tuning** | Readout alone, without specialisation |
| B2 | Fine-tuned model used with `generate(max_tokens=1)` | **Honest control**: should equal GroundOne in accuracy and latency |
| B3 | **Rizzo-Flow** (general-purpose System One) via its `/v1/systemone` or `/v1/decisions` API, boolean question per claim, shared state = context | General-purpose System One. Sizes available are Spark-X2.5 4B and 1.7B; whether a Qwen2.5 GGUF can be loaded with `--model` is **untested** and is checked in Phase 0. Report which weights (`flow` default fine-tune or `base`) |
| B4 | **Encoders:** MiniCheck-RoBERTa and -DeBERTa, HHEM-2.1-open (separate env, `transformers` 4.46), run on the same machine (PyTorch MPS). MiniCheck-Flan-T5 does not fit the memory guard (published number used); AlignScore optional | Strongest cheap specialised alternative (RQ1, RQ5) |
| B5 | Published numbers of larger systems on LLM-AggreFact (not re-run) | Context only |
| (B6) | **CLM** (Contrastive Language Models, Kwok et al., 2026, blog + Apache-2.0 code in `SystemOne_repos/CLM`): bi-encoder System One on frozen Qwen3-8B + small heads | **Related work only** (author's decision, 2026-10-05). It needs vLLM on CUDA and ~16 GB for the 8B encoder, so it does not run on the M4 as shipped. Its soft-label cross-entropy over options is borrowed for ablation A3 |

Rules: same prompt content, same truncation, same machine, same decoding settings (greedy) wherever applicable; prompts of the baselines are fixed **before** looking at test results and frozen in the repo.

Experiment matrix: {B0a, B1, B2, GroundOne} × {0.5B, 3B} on the full test sets; B0b on a stratified subsample; {B3, B4} once each; on {LLM-AggreFact, RAGTruth, ANLI dev (three-way and rules)}.

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
- Optional: energy via `powermetrics` (stretch).

### 8.5 Reporting rules
- Report all baselines, including those where we lose.
- Results files are create-only (never overwritten); each run stores config, git commit, dataset hash and hardware notes.
- **Every phase leaves figures** (author's rule, 2026-10-05): `groundone figures all` writes 300-dpi PNGs with draft captions to `Project/figures/<group>/` (phase0, eda, sweep, training-<run>, results, …). A new kind of result gets its plotting function in `GroundOne/src/groundone/figures/` in the same change; overnight queues end with `groundone figures all`. Colours are fixed per system across all figures.

---

## 9. Phases, gates and deliverables

Experiment and thesis together. The machine trains or benchmarks **at night**; daytime goes to code and writing. **Submission: 2026-11-10. Last day for new experiments: 2026-10-30.**

| Week | Dates | Experiment | Writing (`Thesis/`) | Gate at end of week |
| --- | --- | --- | --- | --- |
| **1** | Oct 5–11 | Phase 0 + 0b ✅ (Oct 5) → **Phase 1a EDA** of ANLI and RAGTruth (`Project/EDA/`) → Phase 1 data pipeline + leakage check → engine + harness; first 0.5B training run overnight | Thesis skeleton (chapters, bib); Ch. 2 Background & related work (wiki ingest ✅); Ch. 4 Data and EDA (material ready) | Datasets frozen; engine probabilities == training-time probabilities |
| **2** | Oct 12–18 | 0.5B final run(s); 3B training overnight; baselines B0a, B1, B2 on full test sets; B0b/B0c on subsample; B4 encoders; B3 Rizzo-Flow | Ch. 3 Method (task, prompt, engine, loss, calibration) | 0.5B beats B1 on dev; 3B adapter exists |
| **3** | Oct 19–25 | GroundOne 3B eval; latency protocol (§8.3); calibration (temperature, reliability, risk-coverage); ablations A1/A2; error analysis | Ch. 5 Experimental setup; start Ch. 6 Results as numbers arrive | All main tables and figures generated from `results/` |
| **4** | Oct 26–Nov 1 | Stretch ablations (A3–A5) if the main matrix is complete; minimal demo (2 days max); **feature freeze Fri Oct 30** | Ch. 6 Results, Ch. 7 Discussion | Experiments closed |
| **5** | Nov 2–8 | Fixes and re-runs of already-defined experiments only; reproducibility package | Ch. 1 Introduction, Ch. 8 Conclusion, final abstract with numbers; complete draft to supervisor by ~Nov 5; revisions | Complete thesis |
| **buffer** | Nov 9–10 | – | Formatting, proofreading | **Submission Nov 10** |

Rules:
- **No new experiment after Oct 30.** Anything that misses the freeze goes to "future work".
- If a step slips by more than 2 days, cut from the bottom of the priority list: demo polish → B3 Rizzo-Flow → B0b verbose judge on the full matrix (keep the Phase 0b numbers) → 3B fine-tuning (fall back to 0.5B fine-tuned + 3B zero-shot).
- Figures and tables are produced by scripts from `results/`, never by hand, so that late re-runs do not cost writing time.

Thesis chapter outline (to fill in `Thesis/content/chapters/`):
1. Introduction (motivation: trustworthy local RAG; System One vs LLM; RQs; contributions)
2. Background and related work (LLM inference: prefill vs decode, KV cache; System One models; hallucination detection and RAG verification; calibration and selective prediction; parameter-efficient fine-tuning)
3. GroundOne: method and implementation
4. Data and exploratory analysis (from Phase 1a, `Project/EDA/report/eda_report.md`)
   - 4.1 The datasets and where they come from: ANLI, RAGTruth, MiniCheck synthetic data, LLM-AggreFact and its 11 sub-datasets
   - 4.2 Exploratory analysis: label schemes and balance, lengths, sentences per answer (K), span types, shortcuts (ANLI negation cue), label agreement (98.6 % with LLM-AggreFact)
   - 4.3 Overlaps and leakage: LLM-AggreFact-RAGTruth = RAGTruth (dev = train, test = test), ANLI premise reuse; the rules derived from them
   - 4.4 Usability of each dataset per experiment and the resulting training mix and splits
5. Experimental setup (baselines, metrics, protocol, hardware)
6. Results
   - 6.1 Accuracy vs baselines (RQ1, RQ5)
   - 6.2 Latency, throughput and memory: readout vs generation, effect of K and context length (RQ2, RQ4)
   - 6.3 Calibration and selective prediction (RQ3)
   - 6.4 **Ablation studies** (§6.5): A1 fine-tuned vs base with the same readout; A2 logit readout vs single-token generation with the same weights; A3–A5 only if run before the freeze
   - 6.5 Error analysis
7. Discussion, limitations and threats to validity
8. Conclusion and future work (streaming verification, larger models, more rules)

---

## 10. Phase 0: feasibility test

**Status: Phase 0 and Phase 0b done (2026-10-05).** Phase 0b: speed gain grows with K (≈2× vs terse, ≈6× vs verbose judge at K = 24); generative judges break format; zero-shot rule-following fails, so flexibility becomes a training target. Full results: `phase0_report.md`. Code and raw outputs: `Project/phase0/`.

### 10.1 What Phase 0 ran

**Which System One was evaluated.** GroundOne does not exist yet (it is the fine-tuned model of Phases 3–4). In Phase 0 the "System One" is the **untrained baseline B1**: the stock instruction models `Qwen2.5-0.5B-Instruct` and `Qwen2.5-3B-Instruct` (MLX 8-bit conversions `lmstudio-community/Qwen2.5-*-Instruct-MLX-8bit`), used in System One mode. That means a chat prompt with the document and the claim, **one forward pass**, the logits of the two answer tokens `A` (supported) and `B` (not supported) read at the last position, and a softmax over those two only. There is no generation, no fine-tuning and no calibration. Rizzo-Flow (the general-purpose System One, B3) was not run. Phase 0 therefore measures the **starting point** of GroundOne and the cost of the System One mechanism, not GroundOne itself. The script is `Project/phase0/scripts/02_readout.py` (accuracy), and `04_speed.py` adds the shared-prefix variant used for the speed test.

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

**Local RAG chat with a live groundedness verifier**, fully on-device.

| Component | Choice *(to confirm)* |
| --- | --- |
| Ingestion | Markdown/PDF/text files → chunks of ~300–500 tokens |
| Embeddings and retrieval | small local embedding model, cosine search in memory (no external vector DB) |
| Generator | Qwen2.5-3B-Instruct (D12), MLX |
| Verifier | GroundOne 0.5B or 3B, in-process or via the local API |
| UI | single local web page: answer text with each sentence coloured by `P(supported)`, a threshold slider, per-sentence probability on hover, a panel with timings |
| Policy actions | flag only (one-month plan); "regenerate flagged sentences" is future work |
| Time budget | **2 days, week 4.** If it runs late, a CLI demo with coloured terminal output is acceptable |

Demo metrics: generation time vs verification time per answer, verifier overhead relative to generation, memory in use, and the generative-judge alternative's overhead for comparison. Memory budget to check: macOS + generator + verifier + embeddings + KV caches within 16 GB (the 7B 4-bit generator plus 3B verifier is likely too tight; prefer 3B generator with 0.5B/3B verifier).

Stretch: verify each sentence while the generator is still producing the next one (both models share the GPU, so measure the contention honestly).

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
| Scope creep (demo, extra datasets, 7B fine-tune) | High | High | Anything not tied to RQ1–RQ5 or the demo is a stretch item; revisit at each gate |
| **Schedule: one month for experiment and thesis** | High | High | Night-time runs, experiment freeze Oct 30, cut list in §9, writing in parallel from week 1, scripted figures |
| 3B training too slow to finish overnight | High (≈17 h per full epoch, measured) | Medium | Train the 3B on a ~10K subset; fall back to 0.5B fine-tuned + 3B zero-shot |
| The Mac freezes during unattended runs | Low (since the guard) | High | Every long job runs under `phase0/scripts/watchdog.py` (kills a job when free memory < 2 GB) |

Threats to validity to discuss in the thesis: benchmark representativeness for *local* RAG, single hardware platform, few seeds for the 3B, prompt sensitivity of the baselines (mitigated by freezing prompts before testing), possible pre-training contamination.

---

## 13. Repository layout and reproducibility

Implemented structure (2026-10-05, D19), modelled on Rizzo-Flow: an installable package with a CLI and an HTTP API. Usage: `Project/GroundOne/README.md`.

```
Project/                     # experiment workspace
  GroundOne/                 # the software (installable package, own .venv)
    pyproject.toml, README.md
    configs/                 # training hyper-parameters: train_0.5b.yaml, train_3b.yaml (copied into each run)
    src/groundone/
      prompts.py             # single source of truth for prompts and questions (training = inference)
      backend.py             # MLX model + adapter; shared-prefix batched scoring (D14), length-batched scoring
      engine.py              # thread-safe service (one MLX thread + lock): verify / systemone / predict
      schema.py, compat.py   # native contract (/v1/verify) and TypeSafe/Jev-compatible contract (/v1/systemone)
      api.py, cli.py         # FastAPI app; `groundone serve|verify|systemone|schema|models|data|train|calibrate|eval|guard`
      calibration.py         # temperature per question type, bound to the model fingerprint
      data/ training/ eval/ tools/   # dataset build + leakage check; LoRA loop; evaluation suites; memory guard
      playground.html        # web UI (base of the demo)
    tests/                   # fake-backend tests (API, schema, compat) + `-m model` real-model tests
  data/                      # download.py + manifests tracked; raw/ and processed data gitignored
  models/                    # trained adapters (gitignored)
  results/                   # evaluation outputs (JSON tracked, predictions gitignored)
  runs/                      # logs and job queues (gitignored)
  EDA/  phase0/  docs/
```

Reproducibility rules: one config file per run; fixed seeds; dataset and prompt hashes stored with results; results never overwritten; one git tag per reported experiment; `uv` for environments.

**What carries over from `Project_old/`:** the single-thread MLX worker pattern, letter-token mapping, FastAPI skeleton and LoRA/plot scripts (as references). **What does not:** the BFCL datasets, v1–v3 results, the routing benchmark numbers. **Lessons applied:** no train/test overlap (§5.3), prompt masking in training (D5), in-process timing (§8.3), a same-size single-token control (B2), and no flat-latency claim without measurement (§4.3).

---

## 14. Open questions for the author

Answered: D1 confirmed; no hand-labelled set (D10); submission 2026-11-10, experiments until 2026-10-30; encoder baselines (B4) yes; CLM related work only.

Also answered: Phase 0/0b run (GO); demo generator = 3B (D12); 7B not run (D13).

Also answered: training mix v1 (`phase1_report.md`).

Still open:
1. Whether to rebalance ANLI negation cues (v2) — decide after the first training run.
2. Supervisor requirements (length/format, mandatory comparisons), if any.

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
- 2026-10-06: after the night-1 results (docs/analysis_2026-10-06.md), the author approved **D20–D25**: datasets v2, fixed dev with balanced-accuracy selection, temperature + bias calibration per format, 0.5B v2 before the 3B.
