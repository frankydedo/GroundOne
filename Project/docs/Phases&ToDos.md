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

**Now (afternoon of Oct 5, GPU free until 22:00)**
- [ ] Commit the work so far (blocked by the safety rule on `git commit`: the author commits, or allows it)
- [x] Rizzo-Flow reinstalled natively (arm64 + Metal; the old install was x86/CPU-only); model already on disk
- [ ] B3 Rizzo-Flow: measured on a subsample of our test sets (queued: `runs/rizzo_job.sh`)
- [x] `groundone baselines rizzo|encoder` added to the package
- [ ] B4 MiniCheck-RoBERTa on the full test sets (queued); HHEM on ANLI + RAGTruth if time; DeBERTa and HHEM on LLM-AggreFact later
- [ ] B1 untrained 0.5B on ANLI + RAGTruth (running); LLM-AggreFact full (~2 h) moved to a later night
- [x] Thesis skeleton in `Thesis/`: English, title, 8 chapters with TODO notes, summary draft, verified bibliography (`bibliography.bib`, template kept as `bibliography_template.bib`). TODO: supervisor names and degree programme in `common/thesis_info.tex`; LaTeX is not installed locally (compile on Overleaf or install MacTeX)
- [x] Ch. 4 first draft (data and EDA, with 6 figures)

**Tonight (start by 22:00)**
- [ ] Night 1 queue (`runs/queue_night1.txt`): 0.5B full training → calibrate → eval ANLI + LLM-AggreFact. Start only after the afternoon queue has finished (one model at a time)

**Next**
- [ ] Read the night-1 results; decide on ANLI negation rebalancing (v2) and on any config change
- [ ] 0.5B eval on RAGTruth (all questions, shared prefix) and latency protocol (§8.3)
- [ ] 3B training (night 2, `configs/train_3b.yaml`)
- [ ] Generative judges B0a/B0b on the full matrix (subsample for B0b)
- [ ] Ch. 2 (background and related work), Ch. 3 (method)

## Already done

- ✅ Thesis direction chosen: specialist System One for sentence-level groundedness in local RAG (2026-10-04)
- ✅ Abstract draft (EN/IT) and implementation plan (2026-10-04/05)
- ✅ Literature collected, verified and ingested into the wiki in `Vault/` (2026-10-05), incl. dataset sources
- ✅ Phase 0/0b feasibility, Phase 1a EDA, Phase 1 datasets v1, Phase 2 GroundOne package (2026-10-05)
- ✅ LR/batch sweep on the 0.5B: lr 1e-4 with ~20 examples per step is best of 4 (2026-10-05)

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
