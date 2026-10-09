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
| 2 | Engine and benchmark harness | Verifier that reads the context once and scores each sentence, plus scripts that run all systems the same way | Oct 5 | ✅ | `Project/GroundOne` package: CLI, server (native + Jev-compatible API), YAML training configs, calibration, eval; tests pass |
| 3 | Training 0.5B | Fine-tune the small model and check it beats its untrained version | Oct 7 | ✅ | g1-05b-b1 (design b, all answers, 5.4 h): T1 three-way 0.769, AUROC 0.905 |
| 4 | Training 3B | Fine-tune the larger model overnight | Oct 7–9 | ✅ | g1-3b-b1 (6,500 answers, 12.25 h): T1 0.832, AUROC 0.940; T2 macro 74.8 |
| 5 | Baselines | Run the comparison systems: terse and verbose generative judges, untrained models, encoders, Rizzo-Flow | Oct 7–8 | ✅ | All on the frozen tests (subsamples for Rizzo-Flow, untrained 3B on T1, judges); B2 open (§14 of the plan) |
| 6 | Main benchmarks | Accuracy and latency of all systems on the test sets | Oct 7–9 | 🟡 | All accuracy runs and latency vs K done; missing: bootstrap CIs, energy (powermetrics), optional second seed |
| 7 | Calibration and analysis | Calibration, ablations, error analysis | Oct 7–8 | 🟡 | Calibration (both models) and error analysis by word overlap done; ablations to decide |
| 8 | Demo | Local RAG chat (Qwen2.5-3B generator) with sentences coloured by GroundOne | Week 4 (Oct 26–30) | ⬜ | Max 2 days |
| — | **Experiment freeze** | No new experiments after this date | **Oct 30** | ⬜ | |
| 9 | Thesis writing | Chapters in `Thesis/`, in parallel from week 1 | Oct 5 – Nov 8 | 🟡 | First drafts of Ch. 3, 4, 5, 6 and summary; Ch. 1, 2, 7, 8 to write |
| 10 | Submission | Proofreading, formatting, submit | Nov 9–10 | ⬜ | |

## Thesis chapters

| Chapter | Planned | Status |
| --- | --- | --- |
| 1 Introduction | Week 5 | ⬜ |
| 2 Background and related work | Weeks 1–2 | ⬜ |
| 3 Method (GroundOne) | Week 2 | ⬜ |
| 4 Data and exploratory analysis | after Phase 1 | ⬜ skeleton |
| 5 Experimental setup | Week 3 | ⬜ |
| 6 Results (incl. ablations) | Weeks 3–4 | ⬜ |
| 7 Discussion and limitations | Week 4 | ⬜ |
| 8 Conclusion | Week 5 | ⬜ |
| Abstract (final, with numbers) | Week 5 | ⬜ |

## Results matrix

<!-- results-matrix:start -->

| System | T1 three-way | T1 binary bacc | T1 AUROC | T2 macro | T2 RAG subset | T3 three-way | T3 AUROC | s/answer K≥14 | T1 ECE (cal.) | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GroundOne 0.5B | 0.769 | 0.815 | 0.905 | 70.1 | 74.4 | 0.442 | 0.722 | **0.41** | **0.019** |  |
| GroundOne 3B | **0.832** | **0.874** | **0.940** | **74.8** | **76.9** | 0.527 | 0.817 | 2.57 | **0.019** |  |
| Untrained 0.5B (design a) | 0.372 | 0.500 | 0.502 | – | – | 0.334 | 0.503 | 0.59 | – |  |
| Untrained 3B (design a) | 0.437 | 0.630 | 0.726 | – | – | 0.531 | 0.821 | 3.83 | – | T1 on 600 answers |
| MiniCheck-RoBERTa | – | 0.762 | 0.814 | 74.0 | 74.6 | – | **0.968** | – | – | binary only; T2 from the earlier run on the same test; T3 in its training lineage |
| HHEM-2.1-open | – | 0.731 | 0.821 | – | – | – | 0.795 | – | – | binary only |
| Rizzo-Flow 4B Q4 | 0.603 | 0.769 | 0.894 | 61.5 | 58.2 | **0.712** | 0.909 | – | – | T1 300 answers, T3 600 pairs; T2 earlier run on 1,100 items |
| Word overlap (no model) | – | – | 0.737 | – | – | – | 0.698 | – | – | never reads the document as a whole |
| Sentence only (n-grams) | 0.570 | – | – | – | – | 0.331 | – | – | – | ignores the document |
| *Published (leaderboard)* | – | – | – | Qwen2.5-0.5B 64.2 · Qwen2.5-7B 72.8 · MiniCheck-FT5 75.0 | – | – | – | – | – | not re-run |

| Judge (latency subset: 200 T1 answers) | Three-way (failures wrong) | Format failures | s/answer K≥14 | s/answer overall | Generated tokens/answer |
| --- | --- | --- | --- | --- | --- |
| Terse judge 0.5B | 0.233 | 23.3% | **0.80** | **0.64** | 57 |
| Verbose judge 0.5B | 0.017 | 97.0% | 2.51 | 1.81 | 252 |
| Terse judge 3B | 0.390 | **0.1%** | 4.44 | 3.16 | **36** |
| Verbose judge 3B | **0.402** | 7.6% | 15.86 | 10.23 | 248 |

*Generated by `groundone matrix` from `outputs/results/*/metrics.json`; do not edit by hand. **Bold** = best value in its column among the listed systems (lowest for latency, ECE, failures and tokens). Check the notes before reading a bold cell: some values come from subsamples or from a system whose training data include that test's source.*

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

**Standing rules:** every phase leaves figures (`groundone figures all` → `Project/outputs/figures/`); every result or insight goes into `docs/thesis_notes.md`.

**Later**
- [ ] Bootstrap confidence intervals and paired tests (CPU, from saved predictions)
- [ ] Second seed of the 0.5B (≈ 6 h with evaluations) to measure run-to-run variance
- [ ] HTTP API on readout design (b), then demo; the served output must be coherent (labels and strict/lenient flags from one rule, e.g. calibrated probabilities with dev-tuned thresholds; see thesis notes 2026-10-09)
- [ ] Decide on the B2 control (plan §14)
- [ ] **Pillar "full locality"** (all items approved by the author, 2026-10-08):
   - [ ] overview of local inference for Ch. 1–2: local vs remote, evolution of runtimes, hardware comparison with cited vendor specs
   - [ ] proof of independence: full evaluation with the network disabled (`HF_HUB_OFFLINE=1`, Wi-Fi off); report that it completes
   - [ ] energy per verification with `powermetrics` (GPU/CPU/ANE power while verifying the latency answers, joules per answer for GroundOne vs the judges). `sudo -n powermetrics` enabled without password (sudoers rule + Claude Code allow rule, 2026-10-08; tested)
   - [ ] co-residence: peak memory of generator (3B) + GroundOne verifier + retriever running together, against the 16 GB budget
   - [ ] licences as part of independence: one table (models, datasets, baselines) with licence and allowed use
   - [ ] cost comparison with a hosted LLM judge for N answers (provider prices on a stated date, cited)
   - [ ] state in Ch. 5 that every baseline also ran on the same laptop
- [x] ~~Second night of 3B training~~: not needed, the dev score plateaued (0.705 at step 320, 0.700 at the end)
- [ ] Optional extension (week 4): grounded ingestion loop for an LLM wiki, evaluated with injected errors (`thesis_notes.md`, Ch. 8)
- [ ] Ch. 2 (background), Ch. 1, 7, 8; supervisors + degree programme in `Thesis/common/thesis_info.tex`

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
- 2026-10-07: validation run g1-05b-b1 (0.5B, design b, all 13,203 training answers, 802 steps, 5.4 h; best dev checkpoint step 600: three-way balanced accuracy 0.633 mean over tasks, 0.731 overall). **T1 (RAGTruth test): three-way macro recall 0.769** (QA 0.589, Summary 0.544, Data2txt 0.812), binary balanced accuracy 0.815, **AUROC 0.905 vs 0.737 for word overlap**, K >= 14: 0.723 (no collapse). Weak spots: contradicted recall in QA 0.03 / Summary 0.13 (few examples, contradictions concentrated in Data2txt); probabilities uncalibrated (ECE 0.30). **T3 (VitaminC): 0.442**, mostly 'not mentioned' predicted, AUROC 0.722 vs 0.698 overlap: weak transfer outside RAG. Dataset validation criteria on T1 all pass. T2 running.
- 2026-10-07: g1-05b-b1 on T2 (LLM-AggreFact, 144 min): macro balanced accuracy 70.1 (earlier v1 model 72.0, MiniCheck-RoBERTa 74.0, zero-shot 0.5B 64.2, 7B 72.8); **RAG subset 74.4 (RoBERTa 74.6, v1 71.0); RAGTruth column 82.1 (RoBERTa 76.5)**. Lower on non-RAG columns (AggreFact-CNN/XSum, FactCheck-GPT, Reveal), as expected without pair-format training data. Night queue finished 09:00 without interruptions.
- 2026-10-07: error analysis of g1-05b-b1 by word overlap. **T3:** supported recall 0.02 when overlap <= 0.4 vs 0.64 when > 0.7; contradicted recall 0 on claims without digits. The model falls back on lexical overlap for paraphrased support and small numeric edits. **T1:** robust at low/mid overlap (macro 0.77), but contradicted 0.24 and not-mentioned 0.43 recall when overlap > 0.7, i.e. hallucinations hidden in sentences that copy the source. Same weakness on both tests; the gap on T3 is that most VitaminC claims are of this kind.
- 2026-10-08: day/night queue finished at 10:20 without interruptions: all baselines on the frozen tests, generative judges and latency (0.5B, 3B), GroundOne 3B (6,500 answers, 12.25 h; T1 0.832 / AUROC 0.940, T3 0.527), 3B calibration (T1 ECE 0.18 → 0.019). Results in `thesis_notes.md`.
- 2026-10-08: Project/ restructured (author's approval): generated artefacts in `outputs/` (models, results, figures, logs); one-off studies in `experiments/` (feasibility = former phase0, eda); `jobs/` (queues, job scripts); `envs/` (hhem, feasibility venvs); results renamed consistently (`untrained-*`, latency inside each system folder); legacy results, queues and logs moved to `_archive/`; `Phases&ToDos.md` renamed `tracker.md`; new `Project/README.md` and `docs/README.md`. Verified: tests, dataset rebuild reproduces the frozen hashes, leakage check, all figures, model evaluation, calibrated engine, HHEM env, guard, EDA scripts.
- 2026-10-09: full T2 for the 3B done (14.8 h, one 25-min pause): LLM-AggreFact macro 74.8 (0.5B 70.1, MiniCheck-RoBERTa 74.0, zero-shot 7B 72.8), RAG subset 76.9. Queue 4 (subsample + second seed) cancelled in favour of the full run.
