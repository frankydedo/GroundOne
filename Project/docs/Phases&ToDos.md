# GroundOne: phases and to-dos

High-level tracker of the experiment and the thesis, plus the running to-do list. Details for each phase are in `implementation_plan.md`.
Update the status column and the to-do list as work progresses.

**Status legend:** ⬜ not started · 🟡 in progress · ✅ done · ⛔ blocked · ✂️ cut

**Key dates:** new experiments until **Thu 2026-10-30** · complete draft to supervisor around **2026-11-05** · submission **Mon 2026-11-10**

| # | Phase | Goal (one line) | Planned | Status | Notes |
| --- | --- | --- | --- | --- | --- |
| 0 | Feasibility | Decide GO/NO-GO: data available, room for improvement, speed gain, fits in 16 GB | Oct 5 (overnight run) | ✅ | GO on the task; speed criterion failed vs terse judges → framing to decide. See `phase0_report.md` |
| 0b | Feasibility re-test | Batched System One vs terse and verbose LLM judges at high K; flexibility probe vs MiniCheck | Oct 5 | ✅ | G4b/G4c pass (gain grows with K); G6 fails zero-shot → flexibility trained. See report |
| 1a | EDA | Analyse the source datasets (labels, lengths, K, span types, overlap) | Oct 5 | ✅ | Report `Project/EDA/report/eda_report.md`; data in `Project/data/raw/` |
| 1 | Dataset | Task-driven train/dev/test sets for the three-way per-sentence task (D20, D21); test set validated and frozen first | Oct 6–9 | 🟡 | Plan: `dataset_plan.md` |
| 2 | Engine and benchmark harness | Verifier that reads the context once and scores each sentence, plus scripts that run all systems the same way | Oct 5 | ✅ | `Project/GroundOne` package: CLI, server (native + Jev-compatible API), YAML training configs, calibration, eval; tests pass |
| 3 | Training 0.5B | Fine-tune the small model and check it beats its untrained version | after Phase 1 | ⬜ | Starts only on the frozen dataset |
| 4 | Training 3B | Fine-tune the larger model overnight | Week 2 (Oct 12–18) | ⬜ | |
| 5 | Baselines | Run the comparison systems: terse and verbose generative judges, untrained models, encoders, Rizzo-Flow | Oct 5 – week 2 | 🟡 | Harness works (encoders, HHEM, Rizzo-Flow run on the earlier test files); rerun on the frozen test set |
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
| 4 Data and exploratory analysis | after Phase 1 | ⬜ skeleton |
| 5 Experimental setup | Week 3 | ⬜ |
| 6 Results (incl. ablations) | Weeks 3–4 | ⬜ |
| 7 Discussion and limitations | Week 4 | ⬜ |
| 8 Conclusion | Week 5 | ⬜ |
| Abstract (final, with numbers) | Week 5 | ⬜ |

## To-dos

**Now (Oct 6–9): dataset, following `dataset_plan.md`**
- [x] Dataset built (`groundone data build`): T1 RAGTruth 2,647 answers, T2 LLM-AggreFact 29,320, T3 VitaminC 3,000, dev 1,468 and train 13,203 answers; checks C2, C3, leakage pass; data card `data/processed/groundone/DATACARD.md`; figures `figures/dataset/`
- [ ] Author approves freezing the test sets (`groundone data freeze`)

**Standing rule:** every phase leaves figures (`groundone figures all` → `Project/figures/`).

**Next**
- [ ] Training code for the three-way task and readout design decision (dataset plan §8)
- [ ] 0.5B and 3B training on the frozen dataset
- [ ] Baselines on the frozen test set (encoders, HHEM, Rizzo-Flow; generative judges B0a/B0b; latency protocol §8.3)
- [ ] Ch. 2 (background and related work), Ch. 3 (method); supervisors + degree programme in `Thesis/common/thesis_info.tex`

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
- 2026-10-05: `groundone figures` added (300-dpi PNGs + captions in `Project/figures/`). Night queues end with `groundone figures all`.
- 2026-10-06: first training runs showed that the dataset did not teach the task (format and question design). Task redefined (D20: one three-way decision per sentence, K = sentences) and dataset rebuilt from scratch (D21, `dataset_plan.md`). Earlier processed data deleted; earlier models, results and figures moved to `Project/_archive/` (not versioned).
- 2026-10-06: dataset built in one evening following `dataset_plan.md` v2 (RAGTruth only for training; tests RAGTruth, LLM-AggreFact, VitaminC). pysbd segmentation + checkable-content rule; C2 96.3 %, C3 98.75 %, leakage PASS. The sentence-only baseline reaches 0.66 on Data2txt (template sentences) and chance on QA/Summary. VitaminC ingested in the wiki.
- 2026-10-06: EDA redone for the final dataset (`EDA/report/eda_report.md`, part A sources, part B built dataset). ANLI/MiniCheck parts removed. Key findings: word overlap alone gives AUROC 0.74 on T1; the sentence-only cue is limited to Data2txt; T1 is cleaner than train; contradicted ≈ evident contradictions. Wiki updated.
- 2026-10-07: readout design (b) adopted as default (author): one pass per answer, verdict at a marker after each scored sentence, class-weighted loss. Implemented and smoke-tested; validation run of the 0.5B (9,000 answers) started at 00:36 (`runs/queue_night3.txt`).
- 2026-10-07: validation run g1-05b-b1 (0.5B, design b, all 13,203 training answers, 802 steps, 5.4 h; best dev checkpoint step 600: three-way balanced accuracy 0.633 mean over tasks, 0.731 overall). **T1 (RAGTruth test): three-way macro recall 0.769** (QA 0.589, Summary 0.544, Data2txt 0.812), binary balanced accuracy 0.815, **AUROC 0.905 vs 0.737 for word overlap**, K >= 14: 0.723 (no collapse). Weak spots: contradicted recall in QA 0.03 / Summary 0.13 (few examples, contradictions concentrated in Data2txt); probabilities uncalibrated (ECE 0.30). **T3 (VitaminC): 0.442**, mostly 'not mentioned' predicted, AUROC 0.722 vs 0.698 overlap: weak transfer outside RAG. Dataset validation criteria on T1 all pass. T2 running.
