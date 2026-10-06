# GroundOne: phases and to-dos

High-level tracker of the experiment and the thesis, plus the running to-do list. Details for each phase are in `implementation_plan.md`.
Update the status column and the to-do list as work progresses.

**Status legend:** ⬜ not started · 🟡 in progress · ✅ done · ⛔ blocked · ✂️ cut

**Key dates:** new experiments until **Thu 2026-10-30** · complete draft to supervisor around **2026-11-05** · submission **Mon 2026-11-10**

| # | Phase | Goal (one line) | Planned | Status | Notes |
| --- | --- | --- | --- | --- | --- |
| 0 | Feasibility | Decide GO/NO-GO: data available, room for improvement, speed gain, fits in 16 GB | Oct 5 (overnight run) | ✅ | GO on the task; speed criterion failed vs terse judges → framing to decide. See `phase0_report.md` |
| 0b | Feasibility re-test | Batched System One vs terse and verbose LLM judges at high K; flexibility probe vs MiniCheck | Oct 5 | ✅ | G4b/G4c pass (gain grows with K); G6 fails zero-shot → flexibility trained. See report |
| 1a | EDA | Analyse ANLI and RAGTruth (labels, lengths, K, span types, overlap) to decide which dataset serves which question | Oct 5 | ✅ | Report `Project/EDA/report/eda_report.md`; data in `Project/data/raw/` |
| 1 | Data | Build train/dev/test sets with no overlap: binary, three-way and rule labels | Oct 5 | ✅ | v1 built, leakage check PASS; see `phase1_report.md` |
| 2 | Engine and benchmark harness | Verifier that reads the context once and scores each sentence, plus scripts that run all systems the same way | Oct 5 | ✅ | `Project/GroundOne` package: CLI, server (native + Jev-compatible API), YAML training configs, calibration, eval; tests pass |
| 3 | Training 0.5B | Fine-tune the small model and check it beats its untrained version | Oct 5–6 | 🟡 | LR/batch sweep done (lr 1e-4, accum 2 kept, `models/sweep-summary.md`); full run tonight (`runs/queue_night1.txt`, ≈ 8.5 h) |
| 4 | Training 3B | Fine-tune the larger model overnight | Week 2 (Oct 12–18) | ⬜ | Fallback: 3B untrained only |
| 5 | Baselines | Run the comparison systems: terse and verbose generative judges, untrained models, encoders, Rizzo-Flow | Oct 5 – week 2 | 🟡 | Afternoon of Oct 5: Rizzo-Flow check, encoders and untrained 0.5B on full test sets |
| 6 | Main benchmarks | Accuracy and latency of all systems on the test sets | Week 3 (Oct 19–25) | ⬜ | |
| 7 | Calibration and analysis | Calibration, ablations, error analysis | Week 3–4 | ⬜ | |
| 8 | Demo | Local RAG chat (Qwen2.5-3B generator) with sentences coloured by GroundOne | Week 4 (Oct 26–30) | ⬜ | Max 2 days |
| — | **Experiment freeze** | No new experiments after this date | **Oct 30** | ⬜ | |
| 9 | Thesis writing | Chapters in `Thesis/`, in parallel from week 1 | Oct 5 – Nov 8 | 🟡 | Skeleton + Ch. 4 draft started Oct 5 |
| 10 | Submission | Proofreading, formatting, submit | Nov 9–10 | ⬜ | |

## Thesis chapters

| Chapter | Planned | Status |
| --- | --- | --- |
| 1 Introduction | Week 5 | ⬜ |
| 2 Background and related work | Weeks 1–2 | ⬜ |
| 3 Method (GroundOne) | Week 2 | ⬜ |
| 4 Data and exploratory analysis | Week 1–2 | 🟡 first draft (Oct 5) |
| 5 Experimental setup | Week 3 | ⬜ |
| 6 Results (incl. ablations) | Weeks 3–4 | ⬜ |
| 7 Discussion and limitations | Week 4 | ⬜ |
| 8 Conclusion | Week 5 | ⬜ |
| Abstract (final, with numbers) | Week 5 | ⬜ |

## To-dos

**Now (Oct 6)** — analysis of v1 results: `docs/analysis_2026-10-06.md`
- [ ] Author approves decisions D20–D25 (analysis §4)
- [ ] Data v2: all four questions per item (D20); ~50 % multi-sentence rows incl. synthetic ANLI answers and full RAGTruth answers up to K ≥ 14 (D21); optional negation balance (D24)
- [ ] Dev v2 with all questions + selection on mean balanced accuracy (D22); calibration with temperature + bias on multi-sentence dev (D23)
- [ ] Quick check (~300 steps, ~1 h) of the 0.5B on v2 before the night

**Tonight**
- [ ] 0.5B full training on v2 → calibrate → eval ANLI, RAGTruth, LLM-AggreFact → `groundone figures all` (D25)

**Standing rule:** every phase leaves figures (`groundone figures all` → `Project/figures/`).

**Next**
- [ ] 3B training on v2 (night 2), only if the 0.5B v2 improves
- [ ] Enlarge Rizzo-Flow subsamples for the final tables
- [ ] Latency protocol (§8.3); B0a/B0b generative judges on the full matrix (subsample for B0b)
- [ ] DeBERTa baseline; HHEM and untrained 0.5B on LLM-AggreFact
- [ ] Ch. 2 (background and related work), Ch. 3 (method); supervisors + degree programme in `Thesis/common/thesis_info.tex`

## Already done

- ✅ Thesis direction chosen: specialist System One for sentence-level groundedness in local RAG (2026-10-04)
- ✅ Abstract draft (EN/IT) and implementation plan (2026-10-04/05)
- ✅ Literature collected, verified and ingested into the wiki in `Vault/` (2026-10-05), incl. dataset sources
- ✅ Phase 0/0b feasibility, Phase 1a EDA, Phase 1 datasets v1, Phase 2 GroundOne package (2026-10-05)
- ✅ LR/batch sweep on the 0.5B: lr 1e-4 with ~20 examples per step is best of 4 (2026-10-05)
- ✅ Baselines B1, B3, B4 (RoBERTa, HHEM) and first GroundOne-0.5B (v1) trained and evaluated (2026-10-05/06)

## Log

Add one line per significant event (date, what happened, impact on the plan).

- 2026-10-05: wiki ingest completed (25 sources). Plan updated: threshold fixed at 0.5 as in the benchmark, success criterion focused on the 0.5B, MiniCheck training data reused.
- 2026-10-05: Phase 0 done overnight. G1, G2, G3 (0.5B), G5 pass; G4 (speed vs terse generative judge) fails. 3B full training ≈ 17 h → subset needed. Framing decision pending (report §7).
- 2026-10-05: Phase 0b done. Batched System One ≈2× faster than terse and ≈6× than verbose judges at K = 24; small generative judges break format (0.5B verbose 97 % failures); zero-shot rule-following fails → train on three-way + rule-conditioned data.
- 2026-10-05: Phase 1a EDA done. ANLI = three-way + rules; RAGTruth = K-decisions + in-domain training; LLM-AggreFact test = main benchmark. LLM-AggreFact-RAGTruth dev = RAGTruth train (do not use for calibration); our RAGTruth sentence labels agree 98.6 % with LLM-AggreFact; 2,048-token cap; ANLI premises shared across splits → filter.
- 2026-10-05: Phase 1 done. Datasets v1: train_05b 42,910 rows (14.5 M tokens), train_3b 10,000; dev/test for ANLI, RAGTruth, MiniCheck, LLM-AggreFact. Leakage check PASS after removing one CNN article shared with LLM-AggreFact test and 711 ANLI dev premises shared with test. Claim-only baseline: 0.56 on ANLI train, 0.36–0.39 on dev/test (cues do not transfer).
- 2026-10-05: Phase 2 done. GroundOne is an installable package (`Project/GroundOne`, README): CLI, FastAPI server with /v1/verify and Jev/Rizzo-compatible /v1/systemone, training loop, calibration, evaluation suites, memory guard. 10 fast tests + 2 real-model tests pass; end-to-end smoke run (train 10 steps → calibrate → eval → serve adapter) OK.
- 2026-10-05: Package moved to `Project/GroundOne` (software) vs `Project/` (experiment workspace); training hyper-parameters in YAML (`GroundOne/configs/`). Measured 0.5B training speed: ≈ 11 s/step → a full epoch ≈ 7 h.
- 2026-10-05: Sweep (4 configs × ~2,200 examples, same order, dev 300): lr 1e-4/accum 2 best (dev loss 1.015 → 0.750, acc 0.38 → 0.52); lr 2e-4 and accum 1 stuck on a constant answer; lr 5e-5 unstable. Config unchanged for night 1.
- 2026-10-05: Baselines B1 (untrained 0.5B: ≈ chance), B3 Rizzo-Flow 4B Q4 (ANLI sup 0.761, three-way 0.606; RAGTruth 0.805; LLM-AggreFact macro 0.615 on 1,100), B4 MiniCheck-RoBERTa / HHEM on ANLI + RAGTruth. Sanity check vs the LLM-AggreFact leaderboard on the 14,952 RAGTruth sentences shared with it, with its labels: RoBERTa 76.4 (published 77.2), HHEM 73.0 (published 69.9) → implementations correct. On all 19,902 RAGTruth test sentences scores are ~2 points lower (≈ 5k sentences not in LLM-AggreFact are harder, likely splitter fragments): report RAGTruth on the LLM-AggreFact-matched sentences with its labels as the primary number.
- 2026-10-05: `groundone figures` added; 15 figures generated (phase0, sweep, training, results) + 10 EDA mirrored in `Project/figures/`. Night queue ends with `groundone figures all`.
- 2026-10-06: Night 1 done without interruptions (0.5B v1, 2,235 steps, 7 h; best dev loss at step 250). LLM-AggreFact: GroundOne-0.5B 72.0 (zero-shot 0.5B 64.2, 7B 72.8; our MiniCheck-RoBERTa 74.0). But: multi-sentence format −6 points on the same sentences, K ≥ 14 below chance, lenient rule always "acceptable", "not mentioned" never predicted, probabilities squeezed around 0.5 and shifted per task. Diagnosis = data (one question per row, 18 % multi-sentence). Proposed data v2 (D20–D25), see `docs/analysis_2026-10-06.md`; diagnostic figures in `figures/diagnostics-g1-05b-v1/`.
