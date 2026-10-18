# GroundOne: phases and to-dos

High-level tracker of the experiment and the thesis, plus the running to-do list. Details for each phase are in `implementation_plan.md`.
Update the status column and the to-do list as work progresses.

**Status legend:** ⬜ not started · 🟡 in progress · ✅ done · ⛔ blocked · ✂️ cut

**Key dates:** new experiments until **Thu 2026-10-30** · complete draft to supervisor around **2026-11-05** · submission **Mon 2026-11-10**

| # | Phase | Goal (one line) | Planned | Status | Notes |
| --- | --- | --- | --- | --- | --- |
| 0 | Feasibility | Decide GO/NO-GO: data available, room for improvement, speed gain, fits in 16 GB | Oct 5 (overnight run) | ✅ | GO on the task; speed criterion failed vs terse judges → framing to decide. See `phase0_report.md` |
| 0b | Feasibility re-test | Batched System One vs terse and verbose LLM judges at high K; flexibility probe vs MiniCheck | Oct 5 | ✅ | G4b/G4c pass (gain grows with K); G6 fails zero-shot → flexibility trained. See report |
| 1a | EDA | Analyse the source datasets (labels, lengths, K, span types, overlap) | Oct 5 | ✅ | Report `Project/experiments/eda/report/eda_report.md`; data in `Project/data/raw/` |
| 1 | Dataset | Task-driven train/dev/test sets for the three-way per-sentence task (D20, D21); test set validated and frozen first | Oct 6–7 | ✅ | Built and validated; tests frozen Oct 7. `dataset_plan.md`, `data/processed/groundone/DATACARD.md` |
| 2 | Engine and benchmark harness | Verifier that reads the context once and scores each sentence, plus scripts that run all systems the same way | Oct 5 | ✅ | `Project/GroundOne` package: CLI, server on design (b) since Oct 10 (native + Jev-compatible API), YAML training configs, calibration, eval; tests pass |
| 3 | Training 0.5B | Fine-tune the small model and check it beats its untrained version | Oct 7 | ✅ | g1-05b-b1 (design b, all answers, 5.5 h wall clock): T1 three-way 0.769, AUROC 0.905. Run 2 g1-05b-s3 (seed 777): 0.767 / 0.907; seed 4321 collapsed and was stopped (D26) |
| 4 | Training 3B | Fine-tune the larger model overnight | Oct 7–9 | ✅ | g1-3b-b1 (6,500 answers, 12.25 h): T1 0.832, AUROC 0.940; T2 macro 74.8 |
| 5 | Baselines | Run the comparison systems: terse and verbose generative judges, untrained models, encoders, Rizzo-Flow | Oct 7–10 | ✅ | All on the frozen tests (subsamples for Rizzo-Flow, untrained 3B on T1, judges); equal-output judge B0d (D25); control B2 on full T1 |
| 6 | Main benchmarks | Accuracy and latency of all systems on the test sets | Oct 7–10 | ✅ | Accuracy, latency vs K, bootstrap CIs and paired tests, energy (powermetrics), second 0.5B run |
| 7 | Calibration and analysis | Calibration, ablations, error analysis | Oct 7–10 | ✅ | Calibration (all runs) + served threshold τ (D27); error analysis by word overlap; A1 = B1 and A2 = B2 done, A3–A5 not run |
| 8 | Demo | Native macOS app (Swift, SwiftUI, MLX Swift): local RAG with the Qwen2.5-3B generator, GroundOne in-process, verify-and-revise loop, policies, measurement mode (D28) | Oct 19–30 | 🟡 | Runtime chosen and spec drafted (`demo_architecture.md`, 2026-10-18); open questions there (§12); conformance test is the gate (M1), fallback to the local HTTP server |
| — | **Experiment freeze** | No new experiments after this date | **Oct 30** | ⬜ | |
| 9 | Thesis writing | Chapters in `Thesis/` (EN) and `Thesis_ita/` (IT, author's reference), in parallel from week 1 | Oct 5 – Nov 8 | 🟡 | Full drafts of all nine chapters; summary, Ch. 1 and Ch. 2 revised by the author (IT) and aligned (EN) on 2026-10-13; Ch. 3–9 to review; demo chapter/section to write |
| 10 | Submission | Proofreading, formatting, submit | Nov 9–10 | ⬜ | |

## Thesis chapters

Chapters renumbered on 2026-10-11 after the new Ch. 2. Italian version (`Thesis_ita/`) is the one the author reviews; English is aligned after each review.

| Chapter | Status |
| --- | --- |
| Summary | ✅ revised by the author (IT), aligned (EN) 2026-10-13; locality paragraph added |
| 1 Introduction | ✅ revised by the author (IT), aligned (EN) 2026-10-11/13: System One vs LLM TikZ figure, RQs rewritten, footnotes |
| 2 Local inference of language models (new) | ✅ revised by the author (IT), aligned (EN) 2026-10-13: 13+ figures and tables (cost model, roofline, hardware photos, memory architectures, SSD streaming, engines ds4/colibri) |
| 3 Background and related work | 🟡 draft; author review pending |
| 4 Method (GroundOne) | 🟡 draft; author review pending |
| 5 Data and exploratory analysis | 🟡 draft; author review pending |
| 6 Experimental setup | 🟡 draft; author review pending; add "every baseline ran on the same laptop" |
| 7 Results | 🟡 draft with all results; author review pending; demo case study if placed here |
| 8 Discussion and limitations | 🟡 draft; author review pending |
| 9 Conclusion | 🟡 draft; llama.cpp port as future work |
| Appendix: output examples | ✅ 2026-10-10 |
| Draft for the supervisor (summary + Ch. 1–2, EN PDF) | ✅ 2026-10-13, repository root (not committed) |

## Results matrix

<!-- results-matrix:start -->

| System | T1 three-way | T1 binary bacc | T1 AUROC | T2 macro | T2 RAG subset | T3 three-way | T3 AUROC | s/answer K≥14 | T1 ECE (cal.) | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GroundOne 0.5B | 0.769 | 0.815 | 0.905 | 70.1 | 74.4 | 0.442 | 0.722 | **0.41** | **0.019** |  |
| GroundOne 0.5B, run 2 | 0.767 | 0.832 | 0.907 | 71.5 | 74.3 | 0.434 | 0.747 | – | 0.020 | second completed seed (777); a further run was stopped after collapsing (D26) |
| GroundOne 3B | **0.832** | **0.874** | **0.940** | 74.8 | **76.9** | 0.527 | 0.817 | 2.57 | **0.019** |  |
| Untrained 0.5B (design a) | 0.372 | 0.500 | 0.502 | – | – | 0.334 | 0.503 | 0.59 | – |  |
| Untrained 3B (design a) | 0.437 | 0.630 | 0.726 | – | – | 0.531 | 0.821 | 3.83 | – | T1 on 600 answers |
| MiniCheck-RoBERTa | – | 0.762 | 0.814 | 74.0 | 74.6 | – | **0.968** | – | – | binary only; T2 from the earlier run on the same test; T3 in its training lineage |
| HHEM-2.1-open | – | 0.731 | 0.821 | – | – | – | 0.795 | – | – | binary only |
| Rizzo-Flow 4B Q4 | 0.603 | 0.769 | 0.894 | 61.5 | 58.2 | 0.712 | 0.909 | – | – | T1 300 answers, T3 600 pairs; T2 earlier run on 1,100 items |
| Liquid AI d1-3B (zero-shot) | 0.657 | 0.792 | 0.863 | **75.7** | 76.5 | **0.724** | 0.913 | – | – | general-purpose open decision model, GroundOne's size; PyTorch MPS; T2 on a 4,000-item random subsample |
| Word overlap (no model) | – | – | 0.737 | – | – | – | 0.698 | – | – | never reads the document as a whole |
| Sentence only (n-grams) | 0.570 | – | – | – | – | 0.331 | – | – | – | ignores the document |
| B2: fine-tuned 0.5B, generated token | 0.521 | – | – | – | – | – | – | – | – | same pass as GroundOne; 24.7% format failures |
| B2: fine-tuned 3B, generated token | 0.761 | – | – | – | – | – | – | – | – | same pass as GroundOne; 1.2% format failures |
| *Published (leaderboard)* | – | – | – | Qwen2.5-0.5B 64.2 · Qwen2.5-7B 72.8 · MiniCheck-FT5 75.0 | – | – | – | – | – | not re-run |

| System (latency subset: 200 T1 answers) | Three-way (failures wrong) | Format failures | s/answer K≥14 | s/answer overall | Generated tokens/answer | Binary ECE raw | Binary ECE cal. |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GroundOne 0.5B | **0.835** | **0.0%** | **0.41** | **0.33** | **0** | **0.298** | **0.034** |
| Terse judge 0.5B | 0.233 | 23.3% | 0.80 | 0.64 | 57 | – | – |
| Verbose judge 0.5B | 0.017 | 97.0% | 2.51 | 1.81 | 252 | – | – |
| Equal-output judge, verbalised 0.5B | 0.234 | 30.9% | 2.47 | 1.37 | 213 | 0.526 | 0.051 |
| Equal-output judge, logits 0.5B | 0.234 | 23.5% | 0.81 | 0.66 | 58 | 0.350 | 0.039 |
| GroundOne 3B | **0.900** | **0.0%** | **2.57** | **1.99** | **0** | **0.181** | **0.030** |
| Terse judge 3B | 0.390 | 0.1% | 4.44 | 3.16 | 36 | – | – |
| Verbose judge 3B | 0.402 | 7.6% | 15.86 | 10.23 | 248 | – | – |
| Equal-output judge, verbalised 3B | 0.410 | **0.0%** | 17.00 | 10.56 | 248 | 0.367 | 0.044 |
| Equal-output judge, logits 3B | 0.390 | 0.1% | 4.38 | 3.08 | 37 | **0.181** | 0.041 |

| Energy (100 latency answers, powermetrics, net of idle) | Three-way | Median s/answer | J/answer | J/decision | Net power (W) |
| --- | --- | --- | --- | --- | --- |
| GroundOne 0.5B | **0.823** | **0.34** | **5.5** | **0.63** | 16.2 |
| Terse judge 0.5B | 0.231 | 0.65 | 8.9 | 1.01 | 13.5 |
| Verbose judge 0.5B | 0.009 | 1.74 | 22.5 | 2.56 | 11.6 |
| GroundOne 3B | **0.894** | **2.07** | **33.1** | **3.77** | 16.2 |
| Terse judge 3B | 0.355 | 3.13 | 43.3 | 4.92 | 14.2 |
| Verbose judge 3B | 0.381 | 10.01 | 111.7 | 12.71 | 10.9 |

*Generated by `groundone matrix` from `outputs/results/*/metrics.json`; do not edit by hand. **Bold** = best value in its column among the listed systems (lowest for latency, ECE, failures and tokens; in the judge table, within each model size). ECE in the judge table: sentences with a valid verdict, calibration fitted on 200 dev answers (`judges-calibrate`); terse and verbose judges give no probabilities. Check the notes before reading a bold cell: some values come from subsamples or from a system whose training data include that test's source.*

<!-- results-matrix:end -->

## To-dos

**Now (from Oct 7), in priority order** (author's decisions: freeze approved; 3B option A, one night on a subset, a second night only if the dev is still improving)
1. [x] Freeze the test sets (`groundone data freeze`, 2026-10-07 13:49; a rebuild reproduces the hashes)
2. [x] Calibrate the 0.5B (g1-05b-b1) on dev (T1 binary ECE 0.30 → 0.02; does not transfer to T3; `thesis_notes.md`): temperature + bias; ECE / Brier / NLL before and after on T1, T2, T3; reliability diagrams
3. [x] Train the 3B (design b) on 6,500 random answers (g1-3b-b1, 12.25 h; T1 0.832 three-way / AUROC 0.940; T3 0.527); T2 full test done 2026-10-09 (14.8 h): macro 74.8, RAG subset 76.9
4. [x] Baselines on the frozen tests (daytime, GPU free):
   - [x] encoders MiniCheck-RoBERTa and HHEM on T1 and T3 (T2: RoBERTa done, 74.0)
   - [x] untrained readout B1 (format a) on T1 and T3 (3B: T1 on 600 answers)
   - [x] generative judges B0a (terse) and B0b (verbose), 200 answers stratified by K
   - [x] Rizzo-Flow (B3) on T1 (300 answers) and T3 (600 pairs)
   - [x] latency protocol as a function of K (central figure `outputs/figures/benchmarks/latency_vs_K.png`)
5. [x] First draft of the new thesis chapters from `thesis_notes.md` (Ch. 3 method, Ch. 5 setup, Ch. 6 results)

**Remaining experiment items before the freeze (2026-10-30)**, in priority order (2026-10-18; GPU runs only with the author's go-ahead, under the guard):
1. [ ] 🟡 running (queue_day8, started 21:05) **Co-residence (RQ4, H4 still "partly supported")**: one Python process with the 3B 4-bit generator + GroundOne 3B (and 0.5B); RAG-style queries from T1 (question + document → answer → verification); peak memory, generation vs verification time. No demo needed; gives the demo chapter its reference numbers. ≈ 1 h GPU
2. [ ] **Offline proof** (locality pillar): a subset evaluation with `HF_HUB_OFFLINE=1` and Wi-Fi off; report that it completes with identical predictions. ≈ 30 min
3. [ ] **8-bit vs bf16** (Ch. 2 quantisation section, measured instead of cited): 0.5B with the bf16 base (cached) and the same adapter: probability differences and T1 metrics. The 3B needs a ≈ 6 GB bf16 download (ask). ≈ 1–2 h
4. [x] ~~Seed 4321 re-run~~: not done (author, 2026-10-18)
5. [x] ~~A3–A5~~: cut, not mentioned in the thesis (D29, 2026-10-18)
6. [ ] Desk items (no GPU): licence table; hosted-judge cost comparison; Ch. 6 sentence that every baseline ran on the laptop; Italian figure labels for Ch. 3–9; git tag per reported experiment and reproducibility notes at the freeze
7. [ ] Then the demo (M0–M5 above)

**Standing rules:** every phase leaves figures (`groundone figures all` → `Project/outputs/figures/`); every result or insight goes into `docs/thesis_notes.md`.

**Later**
- [x] HTTP API on design (b) with one coherent output rule (D27, 2026-10-10)
- [x] Served threshold τ fitted on dev (2026-10-10): 0.935 / 0.895 / 0.925 (0.5B run 1, run 2, 3B); served rule = raw decision within 0.01 on T1
- [ ] **Demo (D28, `demo_architecture.md`)**, milestones:
   - [x] open questions answered (2026-10-18; segmentation approach to confirm)
   - [ ] M0 Xcode project; MLX Swift streams an answer from Qwen2.5-3B
   - [ ] M1 GroundOne in Swift + fixture export in Python + conformance test (gate, by 2026-10-24)
   - [ ] M2 library + SQLite FTS5 retrieval + coloured chat
   - [ ] M3 policy engine, verify-and-revise loop, audit log
   - [ ] M4 measurement and comparison modes, export, figures (before the freeze, 2026-10-30)
   - [ ] M5 polish, screenshots, README
- [x] B2 control on full T1 (2026-10-10): generated token 0.521 / 0.761 vs readout 0.769 / 0.832 (0.5B / 3B)
- [x] Thesis: show one real output example per system (GroundOne JSON, terse and verbose judge text, encoders, Rizzo-Flow) on the same answer (author request, 2026-10-09)
- [ ] **Pillar "full locality"** (all items approved by the author, 2026-10-08):
   - [x] overview of local inference: became the whole Ch. 2 (2026-10-11), revised 2026-10-12/13
   - [ ] proof of independence: full evaluation with the network disabled (`HF_HUB_OFFLINE=1`, Wi-Fi off); report that it completes
   - [x] energy per verification with `powermetrics` (2026-10-10): GroundOne 5.5 J / 33 J per answer vs terse 8.9 / 43 and verbose 22.5 / 112
   - [ ] co-residence: peak memory of generator (3B) + GroundOne verifier + retriever running together, against the 16 GB budget (measured in the demo's measurement mode, D28)
   - [ ] licences as part of independence: one table (models, datasets, baselines) with licence and allowed use
   - [ ] cost comparison with a hosted LLM judge for N answers (provider prices on a stated date, cited)
   - [ ] state in Ch. 6 (setup) that every baseline also ran on the same laptop
- [x] ~~Second night of 3B training~~: not needed, the dev score plateaued (0.705 at step 320, 0.700 at the end)
- [ ] Optional extension (week 4): grounded ingestion loop for an LLM wiki, evaluated with injected errors (`thesis_notes.md`, Ch. 8)
- [x] Ch. 1, 2 (local inference), 3, 8, 9 written (2026-10-10/11)
- [ ] Author's review of Ch. 3–9 (Italian first), then alignment of the English version

## Already done

- ✅ Thesis direction chosen: specialist System One for sentence-level groundedness in local RAG (2026-10-04)
- ✅ Abstract draft (EN/IT) and implementation plan (2026-10-04/05)
- ✅ Literature collected, verified and ingested into the wiki in `Vault/` (2026-10-05), incl. dataset sources
- ✅ Phase 0/0b feasibility, Phase 1a EDA, Phase 2 GroundOne package (2026-10-05)
- ✅ Baseline harness: MiniCheck-RoBERTa, HHEM, Rizzo-Flow reproduce published numbers (2026-10-05)

## Log

Add one line per significant event (date, what happened, impact on the plan).

- 2026-10-05: wiki ingest completed (25 sources). Plan updated: threshold fixed at 0.5 as in the benchmark, success criterion focused on the 0.5B, MiniCheck training data reused.
- 2026-10-05: Phase 0 done overnight. G1, G2, G3 (0.5B), G5 pass; G4 (speed vs terse generative judge) fails. 3B full training ≈ 17 h → subset needed. Framing decision pending (report §7).
- 2026-10-05: Phase 0b done. Batched System One ≈2× faster than terse and ≈6× than verbose judges at K = 24; small generative judges break format (0.5B verbose 97 % failures); zero-shot rule-following fails → train on three-way + rule-conditioned data.
- 2026-10-05: Phase 1a EDA done. ANLI = three-way + rules; RAGTruth = K-decisions + in-domain training; LLM-AggreFact test = main benchmark. LLM-AggreFact-RAGTruth dev = RAGTruth train (do not use for calibration); our RAGTruth sentence labels agree 98.6 % with LLM-AggreFact; 2,048-token cap; ANLI premises shared across splits → filter.
- 2026-10-05: Phase 2 done. GroundOne is an installable package (`Project/GroundOne`, README): CLI, FastAPI server with /v1/verify and Jev/Rizzo-compatible /v1/systemone, training loop, calibration, evaluation suites, memory guard. 10 fast tests + 2 real-model tests pass; end-to-end smoke run (train 10 steps → calibrate → eval → serve adapter) OK.
- 2026-10-05: Package moved to `Project/GroundOne` (software) vs `Project/` (experiment workspace); training hyper-parameters in YAML (`GroundOne/configs/`). Measured 0.5B training speed: ≈ 11 s/step → a full epoch ≈ 7 h.
- 2026-10-05: Baselines B1 (untrained 0.5B: ≈ chance), B3 Rizzo-Flow 4B Q4 (ANLI sup 0.761, three-way 0.606; RAGTruth 0.805; LLM-AggreFact macro 0.615 on 1,100), B4 MiniCheck-RoBERTa / HHEM on ANLI + RAGTruth. Sanity check vs the LLM-AggreFact leaderboard on the 14,952 RAGTruth sentences shared with it, with its labels: RoBERTa 76.4 (published 77.2), HHEM 73.0 (published 69.9) → implementations correct. On all 19,902 RAGTruth test sentences scores are ~2 points lower (≈ 5k sentences not in LLM-AggreFact are harder, likely splitter fragments): report RAGTruth on the LLM-AggreFact-matched sentences with its labels as the primary number.
- 2026-10-05: `groundone figures` added (300-dpi PNGs + captions in `Project/outputs/figures/`). Night queues end with `groundone figures all`.
- 2026-10-06: first training runs showed that the dataset did not teach the task (format and question design). Task redefined (D20: one three-way decision per sentence, K = sentences) and dataset rebuilt from scratch (D21, `dataset_plan.md`). Earlier processed data deleted; earlier models, results and figures moved to `Project/_archive/` (not versioned).
- 2026-10-06: dataset built in one evening following `dataset_plan.md` v2 (RAGTruth only for training; tests RAGTruth, LLM-AggreFact, VitaminC). pysbd segmentation + checkable-content rule; C2 96.3 %, C3 98.75 %, leakage PASS. The sentence-only baseline reaches 0.66 on Data2txt (template sentences) and chance on QA/Summary. VitaminC ingested in the wiki.
- 2026-10-06: EDA redone for the final dataset (`experiments/eda/report/eda_report.md`, part A sources, part B built dataset). ANLI/MiniCheck parts removed. Key findings: word overlap alone gives AUROC 0.74 on T1; the sentence-only cue is limited to Data2txt; T1 is cleaner than train; contradicted ≈ evident contradictions. Wiki updated.
- 2026-10-07: readout design (b) adopted as default (author): one pass per answer, verdict at a marker after each scored sentence, class-weighted loss. Implemented and smoke-tested; validation run of the 0.5B (9,000 answers) started at 00:36 (`jobs/queue_night3.txt`).
- 2026-10-07: validation run g1-05b-b1 (0.5B, design b, all 13,203 training answers, 802 steps, 5.5 h wall clock; best dev checkpoint step 600: three-way balanced accuracy 0.633 mean over tasks, 0.731 overall). **T1 (RAGTruth test): three-way macro recall 0.769** (QA 0.589, Summary 0.544, Data2txt 0.812), binary balanced accuracy 0.815, **AUROC 0.905 vs 0.737 for word overlap**, K >= 14: 0.723 (no collapse). Weak spots: contradicted recall in QA 0.03 / Summary 0.13 (few examples, contradictions concentrated in Data2txt); probabilities uncalibrated (ECE 0.30). **T3 (VitaminC): 0.442**, mostly 'not mentioned' predicted, AUROC 0.722 vs 0.698 overlap: weak transfer outside RAG. Dataset validation criteria on T1 all pass. T2 running.
- 2026-10-07: g1-05b-b1 on T2 (LLM-AggreFact, 144 min): macro balanced accuracy 70.1 (earlier v1 model 72.0, MiniCheck-RoBERTa 74.0, zero-shot 0.5B 64.2, 7B 72.8); **RAG subset 74.4 (RoBERTa 74.6, v1 71.0); RAGTruth column 82.1 (RoBERTa 76.5)**. Lower on non-RAG columns (AggreFact-CNN/XSum, FactCheck-GPT, Reveal), as expected without pair-format training data. Night queue finished 09:00 without interruptions.
- 2026-10-07: error analysis of g1-05b-b1 by word overlap. **T3:** supported recall 0.02 when overlap <= 0.4 vs 0.64 when > 0.7; contradicted recall 0 on claims without digits. The model falls back on lexical overlap for paraphrased support and small numeric edits. **T1:** robust at low/mid overlap (macro 0.77), but contradicted 0.24 and not-mentioned 0.43 recall when overlap > 0.7, i.e. hallucinations hidden in sentences that copy the source. Same weakness on both tests; the gap on T3 is that most VitaminC claims are of this kind.
- 2026-10-08: day/night queue finished at 10:20 without interruptions: all baselines on the frozen tests, generative judges and latency (0.5B, 3B), GroundOne 3B (6,500 answers, 12.25 h; T1 0.832 / AUROC 0.940, T3 0.527), 3B calibration (T1 ECE 0.18 → 0.019). Results in `thesis_notes.md`.
- 2026-10-08: Project/ restructured (author's approval): generated artefacts in `outputs/` (models, results, figures, logs); one-off studies in `experiments/` (feasibility = former phase0, eda); `jobs/` (queues, job scripts); `envs/` (hhem, feasibility venvs); results renamed consistently (`untrained-*`, latency inside each system folder); legacy results, queues and logs moved to `_archive/`; `Phases&ToDos.md` renamed `tracker.md`; new `Project/README.md` and `docs/README.md`. Verified: tests, dataset rebuild reproduces the frozen hashes, leakage check, all figures, model evaluation, calibrated engine, HHEM env, guard, EDA scripts.
- 2026-10-09: full T2 for the 3B done (14.8 h, one 25-min pause): LLM-AggreFact macro 74.8 (0.5B 70.1, MiniCheck-RoBERTa 74.0, zero-shot 7B 72.8), RAG subset 76.9. Queue 4 (subsample + second seed) cancelled in favour of the full run.
- 2026-10-09 15:12: equal-output judge B0d (D25) done, both variants, 0.5B + 3B (queue_day5, 1 h 48 min, no guard intervention). GroundOne wins at equal output: three-way 0.835 / 0.900 vs ≤ 0.41; AURC 0.009 / 0.005 vs 0.048–0.063. Judge table of the results matrix updated; details in thesis notes
- 2026-10-09 16:30: bootstrap CIs and paired tests (`groundone bootstrap`, B = 2000, cluster by leakage group). All claimed differences significant except T2 macro 3B vs MiniCheck-RoBERTa (+0.8, CI −0.5 to +2.1): claim tempered in abstract, plan and Ch. 6. B2 check on dev: generation emits the spaced letter, agrees with the readout in 75 % / 92 %
- 2026-10-10 08:37: night-6 queue done. Second completed 0.5B run (seed 777; seed 4321 stopped after collapse, D26): T1 0.767 vs 0.769, T2 71.5 vs 70.1. B2 on full T1: generated token 0.521 / 0.761 vs readout 0.769 / 0.832 (0.5B / 3B). Energy per answer: GroundOne 5.5 J / 33 J vs terse 8.9 / 43 and verbose 22 / 112. Matrix extended (run 2, B2, energy)
- 2026-10-10: HTTP API on design (b) (D27): training segmentation, one pass, labels/flags/probabilities from one rule (calibrated P(supported) ≥ dev threshold τ); `calibrate-b` now fits τ and keeps the dev logits; playground updated; 3 new API tests (13 fast tests pass); real check on the 0.5B: 0.10 s, 0 output tokens
- 2026-10-10 13:12: served threshold τ fitted on dev for all runs (queue_day6): 0.935 / 0.895 / 0.925; the served rule matches the evaluated raw decision within 0.01 on T1
- 2026-10-10: general audit (docs, thesis, code): stale statements fixed in docs and code (bootstrap now drops items skipped by Rizzo-Flow on T2: macro 61.5; run-2 and B2 pairs added); thesis chapter updates listed in the chapter table
- 2026-10-10: wiki lint + 22 + 12 sources ingested (incl. the Hugging Face decision-models tag); whole thesis revised chapter by chapter: Ch. 1, 2, 7, 8 written, Ch. 3–6 revised, summary with results, output-examples appendix, 5 new figures, 26 new bibliography entries; compiles cleanly (68 pages)
- 2026-10-11 07:39: night-7 queues done. Liquid AI d1-3B (same-size general decision model, zero-shot) on T1/T3/T2-subsample: GroundOne wins in domain (T1 +0.11 / +0.18), on par on T2 (3B), loses on VitaminC (−0.20). First d1 queue lost T1 to an MPS memory issue (fixed with restartable workers). CPU experiments: response-level F1 (Decision Index protocol) 0.73–0.78; LCB threshold not needed in domain
- 2026-10-11: thesis updated with the same-size general decision model (d1-3B, B3b) in Ch. 1, 5, 6, 7, 8 and the summary; decision-model ecosystem (Clef, d1, pplx-decider, Decision Index, Jev studies) in Ch. 2; response-level comparison with the Decision Index in Ch. 6; comparison figures regenerated with d1-3B; compiles cleanly (72 pages)
- 2026-10-11: new Ch. 2 "Local inference of language models" (author's decision: locality is the backbone; thesis target 120–150 pages); about 50 local-inference sources in `Vault/raw/local_inference/` ingested; chapters renumbered 1–9 in both languages; figures `groundone figures locality` (EN and IT)
- 2026-10-11/12: author's review of the Italian summary and Ch. 1 (System One vs LLM TikZ figure, RQs rewritten, footnotes, dataset contribution stated as derived, baselines named); Ch. 2 clarity pass, hardware photos from the author's images, Table 2.1 formatted
- 2026-10-13: Ch. 2 additions: specialised engines (ds4, colibri), discrete vs unified memory and SSD streaming diagrams, reading-vs-writing claim made precise; author's review of Ch. 2 done; English summary, Ch. 1 and Ch. 2 aligned; abstract v0.4; draft PDF (summary + Ch. 1–2) prepared for the supervisor
- 2026-10-18: demo decided (D28): native macOS app in Swift/SwiftUI with MLX Swift, GroundOne in-process with a conformance test, verify-and-revise loop and policies; spec in `demo_architecture.md`; 31 demo sources saved in `Vault/raw/demo/` and ingested (MLX Swift ecosystem, alternatives, app components, verify-and-revise and guardrails papers)
- 2026-10-18: demo details decided by the author (GroundOne Studio provisional, 3B 4-bit generator, hybrid retrieval, own thesis chapter); remaining experiment items listed and prioritised (co-residence, offline proof, 8-bit vs bf16; optional seed re-run; A3–A5 to decide)
- 2026-10-18: Ch. 3–9 of the Italian thesis revised (clarity, footnotes, 12 TikZ diagrams, 6 more plots, Italian figure labels; 127 pages). D29: A3–A5 cut and not cited; seed re-run and 3B bf16 dropped. queue_day8 started 21:05 (offline proof in a network-denying sandbox, 8-bit vs bf16 on the 0.5B, co-residence)
