# Implementation Plan: GroundOne (working title)

A specialist System One for local RAG: single-pass, calibrated groundedness verification with compact Qwen2.5 models on a 16 GB Apple Silicon laptop.

> **Status:** draft v0.2 (2026-10-04), for the author's review. Nothing here has been run yet except where marked *(measured)*.
> **Hard constraint: the experiment *and* the written thesis (`Thesis/`) must be done by the submission date, 2026-11-10. New experiments only until 2026-10-30.** The schedule (§9) and the scope cuts (§1.5) follow from this.
> Every number marked *(estimate)* or *(provisional)* is a planning figure to be replaced by a measurement.
> Companion document: `abstract.md`.

---

## 0. How to use this document

- It is the compass for the whole experiment: if a task is not traceable to a research question (§2), it is out of scope.
- Decisions that the author must confirm are tagged **[DECIDE]**. Open questions are collected in §14.
- Go/no-go gates are in §9. **Phase 0 (feasibility) decides whether we commit to this use case at all.**
- Update this file whenever a decision changes. Never silently change the experiment: add a line to the decision log (§3).

---

## 1. Goal and scope

### 1.1 Thesis statement
A compact language model, fine-tuned to do **one thing** (decide whether a sentence is supported by a given context) and used as a **System One** (one forward pass, logit readout, no text generation), can approach the accuracy of much larger generative judges, at a fraction of the latency and memory, on a laptop. Its probabilities can be calibrated well enough to be used as thresholds.

This is a hypothesis. The thesis is valid whether it is confirmed or not, provided the comparison is controlled and honest.

### 1.2 The task (one decision, done well)
**Groundedness verification for RAG.** Input: a retrieved context `C`, a generated answer `A` split into sentences `s_1..s_K`. Output: for each `s_i`, `P(supported | C, A, s_i)`.

- Core task is binary (supported / not supported). The probability is the product; there is no separate "abstain" class. Uncertainty is expressed by the probability and handled with thresholds (selective prediction).
- This is the **narrowing of use case B** discussed with the author: from "relevance + support + groundedness" to the single decision *support*. Reason: it is the only variant where a shared long context and several short questions occur naturally (the shared-prefix advantage, §4.3). Per-chunk relevance grading does not have this structure.

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
- Qwen2.5-7B fine-tuning (7B is used only as a zero-shot inference baseline).
- Training a new RLCD-style reinforcement learning stage. Calibration is done by supervised loss plus post-hoc temperature scaling.
- A hand-labelled local evaluation set (cut for time, decision D10).

### 1.5 Scope cuts imposed by the one-month deadline (D11)
| Item | Original plan | One-month plan |
| --- | --- | --- |
| Hand-labelled local set | 150–300 sentences | **Cut.** The demo is evaluated qualitatively plus latency/memory only |
| Seeds | 0.5B ×3, 3B ×1–2 | 0.5B ×2 if time allows (else ×1), 3B ×1 |
| Hyper-parameter sweep | small sweep on 0.5B | at most 2–3 configurations, chosen on dev |
| Ablations | A1–A5 | **A1, A2 required** (they come for free from baselines B1, B2); A3–A5 in week 4 only if the main matrix is complete |
| Extensions | E1, E2 | **Cut** unless everything else is done; RQ5 then answered only on the plain task |
| Slow baselines (B0b rationale judge, B0c 7B) | full test sets | **stratified subsample** (e.g. 300–500 items), stated in the thesis |
| Training sources | 3–4 sources | **1–2 sources** (decided in Phase 0) |
| Context cap | 1,024 then 2,048 | 1,024 (2,048 only if free) |
| Demo | streaming, policy actions | static answer + coloured sentences + threshold slider + timings |
| Phase 0 | ~1 week | **2 days** |

---

## 2. Research questions and hypotheses

| ID | Research question | Hypothesis (falsifiable) |
| --- | --- | --- |
| RQ1 | **Specialisation.** Can a fine-tuned 0.5B/3B System One match larger zero-shot generative judges? | H1: fine-tuned 3B reaches at least the balanced accuracy of the zero-shot 7B generative judge on the held-out benchmarks; fine-tuned 0.5B is within a *(provisional)* 5 points of it. |
| RQ2 | **Readout vs generation.** How much does the logit readout alone buy, at the same model size? | H2a: against a same-model single-token-generation control the latency difference is negligible (this is the expected honest result). H2b: against a generative judge that emits a structured verdict per claim, the speed-up grows with K (claims per answer) and is largest for judges that emit a rationale. |
| RQ3 | **Calibration.** Are the probabilities usable as confidence? | H3: after fine-tuning plus temperature scaling, ECE is lower than for zero-shot logits of the same model and than for verbalised confidence of generative judges; selective prediction at a chosen coverage improves accuracy monotonically. |
| RQ4 | **Reliability and cost on-device.** Does the full stack fit and stay interactive on 16 GB? | H4: the verifier adds *(provisional)* < 1 s p95 to a typical 5-sentence answer with the 3B and < 0.3 s with the 0.5B; peak memory of generator + verifier + retriever stays under ~11 GB; the System One has 0 % format failures while small generative judges show measurable ones. |
| RQ5 | **Against the strongest cheap alternative.** Does an LLM-based System One add anything over a specialised encoder (MiniCheck, HHEM)? | H5 (exploratory): the encoder wins or ties on accuracy and speed for the plain task; the System One's value, if any, appears in instruction/policy conditioning (stretch experiment E2, §6.5). **A negative result here is acceptable and must be reported.** |

Success levels (to be fixed after Phase 0):
- **Minimum viable thesis:** controlled comparison completed, honest decomposition of gains, working demo, even if the encoder baseline dominates.
- **Target:** H1, H2b, H3 and H4 confirmed.
- **Stretch:** policy-conditioning experiment, streaming verification in the demo, 7B fine-tuning.

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

Record future changes below (date, decision, reason).

- 2026-10-04: D1 confirmed by the author (single task: sentence-level groundedness). D10, D11 added.
- 2026-10-05: submission date 2026-11-10; experiment freeze 2026-10-30. Encoder baselines (B4) approved. CLM = related work only (not a baseline). Demo generator = Qwen2.5-3B-Instruct (D12). Phase 0 to run autonomously overnight once the author gives the go-ahead.

---

## 4. System design

### 4.1 Prompt format
Chat template of Qwen2.5 (ChatML). The prompt is split into a **shared prefix** and a **per-claim suffix** so that the prefix is encoded once.

```
<|im_start|>system
You are a faithfulness verifier. Decide whether the FOCUS sentence is fully supported by the CONTEXT.
Reply with one letter: A = supported, B = not supported.<|im_end|>
<|im_start|>user
CONTEXT:
{retrieved passages}

ANSWER:
{full generated answer}
                                  <- shared prefix ends here (at a newline boundary)
FOCUS:
{sentence i}<|im_end|>
<|im_start|>assistant
                                  <- read logits of the tokens "A" and "B" here
```

- The full answer is part of the prefix so that pronouns and references in sentence *i* can be resolved; the suffix only names the focus sentence.
- For pair-style benchmarks (LLM-AggreFact: `document`, `claim`) the answer *is* the claim and K = 1. The shared-prefix saving only appears on RAGTruth-style responses and in the demo.
- **Boundary check (mandatory unit test):** `tokens(prefix + suffix) == tokens(prefix) + tokens(suffix)` for every example. Split only at a newline boundary; otherwise BPE merges across the boundary change the tokens.

### 4.2 Engine (MLX)
```
engine.verify(context, answer_sentences) -> [P(supported)_i]
 1. build prefix, tokenise, prefill once into a KV cache            (cost ~ prefill(S))
 2. for each sentence i:
      run suffix tokens through the model with the cache,
      read logits at the last position for {"A","B"} -> softmax(2) / T
      trim the cache back to the prefix length                       (mlx_lm trim_prompt_cache)
 3. return probabilities (+ timings: prefill_ms, per_claim_ms)
```
- Restricted softmax over the two answer tokens, divided by a calibrated temperature `T`.
- Phase 3 first version evaluates suffixes sequentially (trim after each). Batched suffixes with a replicated cache are a possible optimisation if sequential is too slow.
- MLX Metal context must stay on one dedicated worker thread (lesson from LightningRoute).
- Keep the engine free of HTTP so that it can be benchmarked in-process; the API layer is a thin wrapper (FastAPI: `POST /v1/verify`, `GET /health`).

### 4.3 Cost model (the claim we have to test, not assume)
Let `S` = prefix tokens, `K` = claims, `n` = tokens a generative judge emits per claim, `t_dec` = per-token decode time.

- Generative judge: `T_gen ≈ prefill(S) + K · n · t_dec`
- System One: `T_s1 ≈ prefill(S) + K · t_suffix`

Preliminary measurement on this machine *(measured, single run, 15 prompts per bucket, MLX 8-bit, old routing prompts)*:

| Model | Prompt tokens | Prefill | Decode per token |
| --- | --- | --- | --- |
| Qwen2.5-0.5B | 242 / 441 / 637 | 86 / 152 / 211 ms | 6.8 / 7.2 / 7.0 ms |
| Qwen2.5-3B | 242 / 441 / 637 | 544 / 941 / 1362 ms | 36.8 / 39.8 / 42.0 ms |

Consequences to keep in mind:
- **Prefill dominates.** Roughly 2 ms/token on the 3B. The fixed cost of reading the context is the same for System One and generative judges.
- Against a *terse* generative judge (about 7 tokens per verdict), K = 8 adds about `8·7·40 ms ≈ 2.2 s` of decoding on the 3B, against well under a second of suffixes for the System One. With a 1000-token context the end-to-end gain is only on the order of 1.5–2× *(estimate)*.
- Against a judge that **writes a rationale** (50–150 tokens per claim) the gain is an order of magnitude or more.
- Against a **single-token generative control** the gain is about zero. This is the honest result for H2a.
- The largest lever is therefore **model size**: a 0.5B specialist has roughly 6× cheaper prefill than the 3B. If it keeps the accuracy, that is the main speed-up, and it comes from specialisation, not from the readout.

The thesis must report all three comparisons and not only the favourable one.

### 4.4 Calibration
1. Train with cross-entropy on the restricted 2-way logits (§6).
2. Fit a temperature `T` on a dev split that is disjoint from both train and test, by minimising NLL.
3. Report ECE (15 bins and adaptive bins), Brier, NLL, reliability diagrams, before/after `T`.
4. Optional: Platt scaling on the logit difference if `T` alone is insufficient.
5. Selective prediction: accuracy vs coverage curve, AURC. This is what makes the probability useful (e.g. flag a sentence only if `P(supported) < τ`).

---

## 5. Data

All sources are public with human labels. Facts below come from the ingested sources (`Vault/wiki/concepts/LLM-AggreFact.md`, `RAGTruth.md`, `MiniCheck.md`, `Natural Language Inference.md`, 2026-10-05); download access and licences are confirmed in Phase 0.

### 5.1 Evaluation sets (never used for training or threshold tuning)
| Set | What it is | Use |
| --- | --- | --- |
| **LLM-AggreFact** | Human-labelled (document, claim) pairs from 10 datasets in the paper (11 on the leaderboard, incl. RAGTruth); about 15.1K dev / 12.9K test; partial support counts as unsupported; HF access is gated (login + terms) | Main out-of-distribution benchmark. Its **dev** split may be used for threshold/temperature checks only, never for training (the authors describe it as largely test-only) |
| **RAGTruth (test split)** | 2,965 instances / 17,790 responses (43.1 % hallucinated) from 6 LLMs, QA / summarisation / data-to-text; character-span annotations of 4 types; test = 450 instances (2,700 responses); **no dev split**; licence not stated in the paper | Main in-domain RAG benchmark. Sentence labels derived from spans (rule: *unsupported* if the sentence overlaps any span). Spans flagged `implicit_true` and `due_to_null` are handled by an explicit, documented rule (default: keep them as unsupported, report a variant without them). Document the version used (Lynx reports a different test size) |

(A hand-labelled local set was planned and cut for time, D10.)

LLM-AggreFact contains RAGTruth data: the RAGTruth **train** split may be used for training only if no RAGTruth test item reaches the training set, and results on the LLM-AggreFact RAGTruth subset must be reported separately.

### 5.2 Training sources *(to verify availability and licences)*
| Source | Role | Mapping to labels |
| --- | --- | --- |
| **MiniCheck training recipe (default)**: 7,076 C2D + 7,319 D2C synthetic examples + a 21K hard ANLI subset (≈35K) | Multi-sentence documents with claims; same data as the strongest small baseline, so the comparison with MiniCheck is data-matched | as released; ANLI neutral/contradiction → not supported |
| ANLI (full) / MNLI | Only if needed; MiniCheck found more ANLI did not help and AlignScore found NLI-heavy data can hurt | entailment → supported; else not supported |
| RAGTruth train split | In-domain RAG responses; dev carved out of it **grouped by instance** | sentence-level derived labels |
| Optionally VitaminC / FEVER-style data | Extra fact-verification pairs | as released |

Target size: ≈35K (MiniCheck recipe) plus a RAGTruth-train share to be decided in Phase 0, class-balanced, with a length cap that keeps the full prompt within the memory budget (§6.3).

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
- Base: `Qwen2.5-0.5B-Instruct` and `Qwen2.5-3B-Instruct` (MLX; 8-bit for 0.5B, 4-bit/8-bit for 3B to be decided by memory).
- Method: LoRA on **all linear layers of all blocks** (QLoRA found adapter coverage matters more than rank; the old configs adapted only 8 blocks; `mlx_lm` defaults to the last 16 blocks), rank 8–16. Avoid a 4-bit base if memory allows: Rizzo-Flow measured a 14-point weaker starting point with an NF4 base.
- **Licence note:** Qwen2.5-3B is under the *Qwen Research* licence (not Apache-2.0, unlike 0.5B/1.5B/7B). Fine for thesis research; check its terms before publishing 3B adapters. Qwen2.5-1.5B is the nearest Apache-2.0 alternative.
- Training hardware: the M4 / 16 GB machine. Use gradient checkpointing, batch size 1 with gradient accumulation.

### 6.2 Loss
- Position: last prompt token. Logits restricted to the two answer tokens `A`, `B`. Loss = cross-entropy of the 2-way softmax against the gold label.
- All prompt tokens are masked: the label is the only supervised signal.
- Optional variants (ablation A3): soft labels where annotator agreement exists; full-vocabulary cross-entropy on the label token instead of the restricted softmax.
- v1 may use `mlx_lm.lora` with the prompt/completion format and `mask_prompt: true` to get a first result quickly; the custom loop follows if needed for the restricted loss.

### 6.3 Memory and length
The risk is long contexts. Rules of thumb *(to measure)*:
- Cap training prompts at 1,024 tokens first, then try 2,048. RAG use in the demo is top-3 chunks of 300–500 tokens plus the answer.
- Measure peak memory with the MLX peak-memory API at a few lengths before launching a long run.
- If the 3B does not train at the target length, fall back to 4-bit base (QLoRA-style), shorter cap, or smaller rank, and document it.
- Training time is unknown: do a 100-step timing run first and extrapolate *(estimate required)*.

### 6.4 Procedure
1. Sanity run: 0.5B on a small subset; loss must decrease; the engine's output must equal the training-time computation (same prompt, same logits within tolerance).
2. Hyper-parameter sweep (small): learning rate, rank, epochs, on the 0.5B only; selection on dev only.
3. Final runs: 0.5B (2 seeds if time allows, else 1), 3B (1 seed, launched overnight). Report mean ± std where seeds exist and state the single-seed limitation otherwise.
4. Save adapters, configs, loss curves, dataset hash, git commit for every run.

### 6.5 Ablations and extensions
**A1 and A2 are required.** A3–A5 run in week 4 only if the main experiment matrix is complete (§1.5, §9). E1 and E2 are future work. Results go in thesis §5.4.

| ID | Experiment | Purpose |
| --- | --- | --- |
| A1 | Base vs fine-tuned, same readout | Isolates the effect of fine-tuning |
| A2 | Readout vs single-token generation, same fine-tuned weights | Confirms equivalence (H2a) |
| A3 | Restricted-softmax vs full-vocab loss; hard vs soft labels | Effect of the loss on calibration |
| A4 | Training-set size curve (e.g. 5k / 10k / 20k / all) | Data efficiency |
| A5 | Prefix with and without the full answer | Value of context for resolving references |
| E1 (stretch) | Sentence-level vs claim-decomposed verification | Granularity |
| E2 (stretch) | **Policy conditioning**: change the definition of "supported" in the prompt (strict vs lenient), evaluate on matching relabelled data, compare with encoders that cannot take a policy | The one place where an LLM-based System One could beat an encoder (RQ5) |

---

## 7. Baselines (a ladder that isolates each effect)

| ID | System | What it isolates |
| --- | --- | --- |
| B0a | Qwen2.5 0.5B / 3B zero-shot, **generative judge** emitting a structured verdict per claim (JSON-like), greedy | Typical practice at the same size |
| B0b | Same, with a short rationale before the verdict | The "reasoning judge" case; largest latency gap expected |
| B0c | Qwen2.5-7B-Instruct 4-bit zero-shot generative judge | Larger generalist; the model H1 compares against |
| B1 | Same base models, **single-token readout, no fine-tuning** | Readout alone, without specialisation |
| B2 | Fine-tuned model used with `generate(max_tokens=1)` | **Honest control**: should equal GroundOne in accuracy and latency |
| B3 | **Rizzo-Flow** (general-purpose System One) via its `/v1/systemone` or `/v1/decisions` API, boolean question per claim, shared state = context | General-purpose System One. Sizes available are Spark-X2.5 4B and 1.7B; whether a Qwen2.5 GGUF can be loaded with `--model` is **untested** and is checked in Phase 0. Report which weights (`flow` default fine-tune or `base`) |
| B4 | **Encoders:** MiniCheck (smallest public variants), HHEM-2.1-open, AlignScore, run on the same machine (PyTorch MPS/CPU) | Strongest cheap specialised alternative (RQ5) |
| B5 | Published numbers of larger systems on LLM-AggreFact (not re-run) | Context only |
| (B6) | **CLM** (Contrastive Language Models, Kwok et al., 2026, blog + Apache-2.0 code in `SystemOne_repos/CLM`): bi-encoder System One on frozen Qwen3-8B + small heads | **Related work only** (author's decision, 2026-10-05). It needs vLLM on CUDA and ~16 GB for the 8B encoder, so it does not run on the M4 as shipped. Its soft-label cross-entropy over options is borrowed for ablation A3 |

Rules: same prompt content, same truncation, same machine, same decoding settings (greedy) wherever applicable; prompts of the baselines are fixed **before** looking at test results and frozen in the repo.

Experiment matrix: {B0a, B1, B2, GroundOne} × {0.5B, 3B} on the full test sets; {B0b, B0c} on a stratified subsample; {B3, B4} once each (B4 pending the author's go-ahead); on {LLM-AggreFact, RAGTruth}.

---

## 8. Metrics and protocol

### 8.1 Quality
- **Balanced accuracy** (the LLM-AggreFact convention), **AUROC**, F1 on the unsupported class, per sub-dataset and macro-average.
- Threshold: **primary = fixed 0.5** (the LLM-AggreFact leaderboard protocol, so numbers are comparable with published ones); secondary = one global threshold chosen on our dev split; plus threshold-free AUROC. Never tune thresholds per test set.
- Published reference points (LLM-AggreFact leaderboard, avg BAcc, not re-run): Bespoke-MiniCheck-7B 77.4; MiniCheck-Flan-T5-L 75.0; Qwen2.5-7B-Instruct zero-shot 72.8; HHEM-2.1-open 71.8; AlignScore 70.5; Qwen2.5-0.5B-Instruct zero-shot 64.2 (51.6 on RAGTruth). Qwen2.5-3B is not listed.
- Confidence intervals via bootstrap; paired bootstrap for system differences.

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

---

## 9. Phases, gates and deliverables

Experiment and thesis together. The machine trains or benchmarks **at night**; daytime goes to code and writing. **Submission: 2026-11-10. Last day for new experiments: 2026-10-30.**

| Week | Dates | Experiment | Writing (`Thesis/`) | Gate at end of week |
| --- | --- | --- | --- | --- |
| **1** | Oct 5–11 | **Phase 0** (2 days, §10, waiting for the author's go) → data pipeline + leakage check + boundary tests → engine (prefix cache) + harness; first 0.5B training run overnight | Thesis skeleton (chapters, bib); wiki lint + ingest of the new sources (§15); Ch. 2 Background & related work | **GO/NO-GO (day 2 of Phase 0)**; datasets frozen; engine logits == training logits |
| **2** | Oct 12–18 | 0.5B final run(s); 3B training overnight; baselines B0a, B1, B2 on full test sets; B0b/B0c on subsample; B4 encoders; B3 Rizzo-Flow | Ch. 3 Method (task, prompt, engine, loss, calibration) | 0.5B beats B1 on dev; 3B adapter exists |
| **3** | Oct 19–25 | GroundOne 3B eval; latency protocol (§8.3); calibration (temperature, reliability, risk-coverage); ablations A1/A2; error analysis | Ch. 4 Experimental setup; start Ch. 5 Results as numbers arrive | All main tables and figures generated from `results/` |
| **4** | Oct 26–Nov 1 | Stretch ablations (A3–A5) if the main matrix is complete; minimal demo (2 days max); **feature freeze Fri Oct 30** | Ch. 5 Results, Ch. 6 Discussion | Experiments closed |
| **5** | Nov 2–8 | Fixes and re-runs of already-defined experiments only; reproducibility package | Ch. 1 Introduction, Ch. 7 Conclusion, final abstract with numbers; complete draft to supervisor by ~Nov 5; revisions | Complete thesis |
| **buffer** | Nov 9–10 | – | Formatting, proofreading | **Submission Nov 10** |

Rules:
- **No new experiment after Oct 30.** Anything that misses the freeze goes to "future work".
- If a step slips by more than 2 days, cut from the bottom of the priority list: demo polish → B3 Rizzo-Flow → B0b rationale judge → 3B fine-tuning (fall back to 0.5B fine-tuned + 3B zero-shot).
- Figures and tables are produced by scripts from `results/`, never by hand, so that late re-runs do not cost writing time.

Thesis chapter outline (to fill in `Thesis/content/chapters/`):
1. Introduction (motivation: trustworthy local RAG; System One vs LLM; RQs; contributions)
2. Background and related work (LLM inference: prefill vs decode, KV cache; System One models; hallucination detection and RAG verification; calibration and selective prediction; parameter-efficient fine-tuning)
3. GroundOne: method and implementation
4. Experimental setup (data, baselines, metrics, protocol, hardware)
5. Results
   - 5.1 Accuracy vs baselines (RQ1, RQ5)
   - 5.2 Latency, throughput and memory: readout vs generation, effect of K and context length (RQ2, RQ4)
   - 5.3 Calibration and selective prediction (RQ3)
   - 5.4 **Ablation studies** (§6.5): A1 fine-tuned vs base with the same readout; A2 logit readout vs single-token generation with the same weights; A3–A5 only if run before the freeze
   - 5.5 Error analysis
6. Discussion, limitations and threats to validity
7. Conclusion and future work (policy conditioning, streaming verification, larger models)

---

## 10. Phase 0: feasibility test (to run only after the author approves this plan)

Goal: decide in **two days**, at low cost and with **no training**, whether the use case has room for a fine-tuned specialist and whether the machine can do the work.

### 10.1 Checks and measurements
1. **Data:** confirm LLM-AggreFact and RAGTruth are downloadable, check licences, sizes, fields, split definitions, how sentence-level labels can be derived from RAGTruth spans. Confirm availability of ANLI and the MiniCheck training data.
2. **Zero-shot headroom:** on a stratified sample of about 300–500 examples, run Qwen2.5-0.5B and 3B **base, single-token readout** (B1) and the 7B-4bit generative judge (B0c). Record balanced accuracy and AUROC.
3. **Encoder reference:** run the smallest public MiniCheck and HHEM on the same sample (B4). Confirm they run on this Mac.
4. **Rizzo-Flow check:** can it start on the M4 (llama.cpp Metal), and can `--model` load a Qwen2.5 GGUF? If not, record that B3 will use Spark-X2.5 1.7B/4B and be presented as an external reference.
5. **Shared-prefix speed:** implement a minimal prefix-cache evaluation and measure, on the 0.5B and 3B, `T_gen` (terse structured verdicts) vs `T_s1` for K = 1, 3, 8 and context lengths of about 500, 1000 and 2000 tokens.
6. **Memory:** measure peak memory for inference at those lengths, and a short LoRA training probe (a few dozen steps) at 1,024 and 2,048 tokens on the 3B.

### 10.2 Go/no-go criteria *(provisional; the author may adjust)*
| # | Criterion | Why |
| --- | --- | --- |
| G1 | Datasets usable with human labels and permissive enough licences | Without data there is no experiment |
| G2 | Zero-shot 3B readout is clearly above chance (balanced accuracy ≥ ~0.60) | The task is within reach of the model |
| G3 | There is headroom **for the 0.5B**: the best small encoder (MiniCheck-FT5, published 75.0) is clearly better than zero-shot 0.5B (published 64.2) — re-measured on our sample. For the 3B, headroom is reported, not required | The leaderboard already shows the 7B zero-shot at 72.8, so the 3B gap may be small; the specialisation claim rests mainly on the 0.5B |
| G4 | Shared-prefix evaluation is at least ~1.5× faster than the terse generative judge at K = 8 | Otherwise the System One advantage rests only on model size |
| G5 | 0.5B LoRA training probe fits; 3B fits at ≥ 1,024 tokens | Feasibility on 16 GB |

If G1 or G5 fail: choose another use case. If G2 fails: the task is too hard for these sizes, so rescope to an easier decision. If G3 fails: the benchmark is a poor discriminator, so look for harder data. If G4 fails: the thesis shifts to "model size and specialisation", and the plan is revised accordingly (still valid, but the abstract changes).

With one month, a NO-GO cannot cost more than these two days: if G2 or G3 fail, prefer **rescoping the same task** (easier subset, e.g. RAGTruth QA only, or shorter contexts) over switching use case.

### 10.3 Fallback use cases (if Phase 0 says NO-GO)
A privacy gate before cloud LLM calls (multi-label, K ≈ 10 categories); prompt-injection scanning for local agents (K = 1, latency/threshold story); chunk relevance grading (against cross-encoder rerankers).

---

## 11. Demo specification

**Local RAG chat with a live groundedness verifier**, fully on-device.

| Component | Choice *(to confirm)* |
| --- | --- |
| Ingestion | Markdown/PDF/text files → chunks of ~300–500 tokens |
| Embeddings and retrieval | small local embedding model, cosine search in memory (no external vector DB) |
| Generator | Qwen2.5-3B-Instruct (or 7B 4-bit if memory allows), MLX, streaming |
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
| Encoders (MiniCheck/HHEM) beat the System One on accuracy and speed | High | Medium | Expected; framed as RQ5. Keep E2 (policy conditioning) and the local-demo/on-device angle; report honestly |
| Shared-prefix gain is small against a terse generative judge (prefill dominates) | Medium | Medium | Measured in Phase 0 (G4); report decomposition; emphasise model-size effect and rationale-generating judges |
| 3B does not fine-tune at long contexts within 16 GB | Medium | Medium | Length cap, 4-bit base, smaller rank, shorter K; or ship 0.5B-only plus 3B zero-shot |
| Label noise / derived sentence labels in RAGTruth | Medium | Medium | Document the derivation rule, report on LLM-AggreFact pairs where labels are native, use the hand-labelled set as a check |
| Training/test leakage | Medium | High | Hard-coded leakage check in the dataset build; split by source ID |
| Qwen2.5 pre-training contamination of public benchmarks | Unknown | Low–Medium | State as a limitation; include the local hand-labelled set (private documents) |
| Timing noise (thermal throttling, background processes) | High | Medium | Protocol in §8.3; repeated runs; report spread |
| Rizzo-Flow cannot run on the Mac or with Qwen | Medium | Low | Present as external reference with its own model; check in Phase 0 |
| Fixed-size answer slots irrelevant here (binary) but position bias still possible | Low | Low | Fixed mapping + fine-tuning; test by swapping letter order on a dev subset |
| Scope creep (demo, extra datasets, 7B fine-tune) | High | High | Anything not tied to RQ1–RQ5 or the demo is a stretch item; revisit at each gate |
| **Schedule: one month for experiment and thesis** | High | High | Night-time runs, feature freeze Oct 23, cut list in §9, writing in parallel from week 1, scripted figures |
| 3B training too slow to finish overnight | Medium | Medium | Measure in Phase 0 probe; reduce data/steps; fall back to 0.5B fine-tuned + 3B zero-shot |

Threats to validity to discuss in the thesis: benchmark representativeness for *local* RAG, single hardware platform, few seeds for the 3B, prompt sensitivity of the baselines (mitigated by freezing prompts before testing), possible pre-training contamination.

---

## 13. Repository layout and reproducibility

Proposed structure under `Project/`:

```
Project/
  docs/                    # abstract, this plan, phase reports, decision log updates
  groundone/               # installable package
    engine/                # prefix-cache verifier, tokenisation + boundary checks
    api/                   # thin FastAPI wrapper
    calibration/           # temperature scaling, metrics
  training/                # data builders, leakage check, training loop, configs
  baselines/               # runners for B0–B4, frozen prompts
  benchmarks/              # latency/quality harness, result schemas
  demo/                    # local RAG app
  data/                    # gitignored; manifests and hashes tracked
  results/                 # create-only run outputs (config, commit, hash, hardware)
  tests/                   # unit tests: boundary, engine==training logits, leakage
```

Reproducibility rules: one config file per run; fixed seeds; dataset and prompt hashes stored with results; results never overwritten; one git tag per reported experiment; `uv` for environments.

**What carries over from `Project_old/`:** the single-thread MLX worker pattern, letter-token mapping, FastAPI skeleton and LoRA/plot scripts (as references). **What does not:** the BFCL datasets, v1–v3 results, the routing benchmark numbers. **Lessons applied:** no train/test overlap (§5.3), prompt masking in training (D5), in-process timing (§8.3), a same-size single-token control (B2), and no flat-latency claim without measurement (§4.3).

---

## 14. Open questions for the author

Answered: D1 confirmed; no hand-labelled set (D10); submission 2026-11-10, experiments until 2026-10-30; encoder baselines (B4) yes; CLM related work only.

Still open:
1. **Phase 0 go-ahead** (downloads of datasets and baseline models, a few GB).
2. **Generator for the demo** (the local LLM that writes the RAG answers that GroundOne then checks): Qwen2.5-3B (safe on memory) or 7B 4-bit (better answers, risky on 16 GB)?
3. Supervisor requirements (length/format, mandatory comparisons), if any.

---

## 15. References (verified 2026-10-05, copies in `Vault/raw/`)

Authors, years and venues were checked against arXiv, the ACL Anthology and AAAI. The PDFs and page copies are in `Vault/raw/` (not yet ingested into the wiki). Cite the **publication** year, not the arXiv year.

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

**Inference background**
- Pope et al. (2023). Efficiently Scaling Transformer Inference. MLSys 2023.
- Kwon et al. (2023). Efficient Memory Management for Large Language Model Serving with PagedAttention. SOSP 2023.
