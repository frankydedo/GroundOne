# GroundOne: experiment phases

High-level tracker of the experiment and the thesis. Details for each phase are in `implementation_plan.md`.
Update the status column as work progresses.

**Status legend:** ⬜ not started · 🟡 in progress · ✅ done · ⛔ blocked · ✂️ cut

**Key dates:** new experiments until **Thu 2026-10-30** · complete draft to supervisor around **2026-11-05** · submission **Mon 2026-11-10**

| # | Phase | Goal (one line) | Planned | Status | Notes |
| --- | --- | --- | --- | --- | --- |
| 0 | Feasibility | Decide GO/NO-GO: data available, room for improvement, speed gain, fits in 16 GB | Oct 5–7 (overnight run) | ⬜ | Waiting for HF login, permissions and go-ahead |
| 1 | Data | Build train/dev/test sets with no overlap and sentence-level labels | Week 1 (Oct 5–11) | ⬜ | |
| 2 | Engine and benchmark harness | Verifier that reads the context once and scores each sentence, plus scripts that run all systems the same way | Week 1 (Oct 5–11) | ⬜ | |
| 3 | Training 0.5B | Fine-tune the small model and check it beats its untrained version | Week 1–2 | ⬜ | |
| 4 | Training 3B | Fine-tune the larger model overnight | Week 2 (Oct 12–18) | ⬜ | Fallback: 3B untrained only |
| 5 | Baselines | Run the comparison systems: generative LLM judges, untrained models, encoders, Rizzo-Flow | Week 2 | ⬜ | |
| 6 | Main benchmarks | Accuracy and latency of all systems on the test sets | Week 3 (Oct 19–25) | ⬜ | |
| 7 | Calibration and analysis | Calibration, ablations, error analysis | Week 3–4 | ⬜ | |
| 8 | Demo | Local RAG chat (Qwen2.5-3B generator) with sentences coloured by GroundOne | Week 4 (Oct 26–30) | ⬜ | Max 2 days |
| — | **Experiment freeze** | No new experiments after this date | **Oct 30** | ⬜ | |
| 9 | Thesis writing | Chapters in `Thesis/`, in parallel from week 1 | Oct 5 – Nov 8 | ⬜ | See chapter tracker below |
| 10 | Submission | Proofreading, formatting, submit | Nov 9–10 | ⬜ | |

## Thesis chapters

| Chapter | Planned | Status |
| --- | --- | --- |
| 1 Introduction | Week 5 | ⬜ |
| 2 Background and related work | Weeks 1–2 | ⬜ |
| 3 Method (GroundOne) | Week 2 | ⬜ |
| 4 Experimental setup | Week 3 | ⬜ |
| 5 Results (incl. ablations) | Weeks 3–4 | ⬜ |
| 6 Discussion and limitations | Week 4 | ⬜ |
| 7 Conclusion | Week 5 | ⬜ |
| Abstract (final, with numbers) | Week 5 | ⬜ |

## Already done

- ✅ Thesis direction chosen: specialist System One for sentence-level groundedness in local RAG (2026-10-04)
- ✅ Abstract draft (EN/IT) and implementation plan (2026-10-04/05)
- ✅ Literature collected, verified and ingested into the wiki in `Vault/` (2026-10-05)

## Log

Add one line per significant event (date, what happened, impact on the plan).

- 2026-10-05: wiki ingest completed (25 sources). Plan updated: threshold fixed at 0.5 as in the benchmark, success criterion focused on the 0.5B, MiniCheck training data reused.
