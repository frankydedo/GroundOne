# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

MSc thesis workspace. The active project is **GroundOne**: a specialist "System One" (single forward pass, answer-letter logit readout, zero generated tokens) that verifies, sentence by sentence, whether a RAG answer is supported / contradicted / not mentioned by the retrieved document. Fine-tuned Qwen2.5 0.5B and 3B (LoRA, MLX 8-bit) on an Apple Silicon 16 GB laptop. The earlier tool-routing thesis is abandoned (`Project_old/`, gitignored, history only).

Deadlines: new experiments only until **2026-10-30**; experiment and written thesis due **2026-11-10**. The compass is `Project/docs/implementation_plan.md` (decision log in §3, research questions in §2); the dataset is specified in `Project/docs/dataset_plan.md`; status tracker is `Project/docs/Phases&ToDos.md`. Earlier models/results/figures are archived in `Project/_archive/` (gitignored); the thesis describes only the final dataset. Update the decision log when a decision changes, and do not silently change the experiment.

Language: chat with the user in Italian; code, docs and the thesis are in English. Give objective critique, not validation. Keep claims honest (e.g. the gain over a single-token LLM control is ~0; the gain comes from model size/specialisation, shared-prefix multi-claim scoring, rationale-free judges and calibration).

## Top-level layout

- `Project/GroundOne/` – the software (Python package `groundone`, CLI, HTTP API, tests). Install and CLI usage are documented in its `README.md`.
- `Project/` (the *workspace*, one level above the package; override with `GROUNDONE_WORKSPACE`) – experiment data and outputs: `data/` (raw + processed datasets), `models/` (trained adapters), `runs/` (logs, guard output), `results/` (eval JSON), `EDA/`, `phase0/` (feasibility scripts, own venvs), `docs/`.
- `Thesis/` – LaTeX thesis (`toptesi` class, biblatex/biber, glossaries). Chapters in `Thesis/content/chapters/ch*.tex`; build artefacts (`thesis.aux`, `.pdf`, …) are untracked.
- `Vault/` – Obsidian LLM-wiki of papers and notes (`Vault/CLAUDE.md` defines its own workflow; `raw/` sources are immutable). Not code.
- `SystemOne_repos/` (CLM, SemIf, rizzo-flow), `Preprocessing/` – third-party clones / audio transcription, gitignored; related work only. Rizzo-Flow is also used as a running baseline server.

## Commands

Run from `Project/GroundOne` with the venv (`uv venv --python 3.12 .venv` – native arm64 Python required for MLX; `uv pip install --python .venv/bin/python -e ".[test]"`; `.[baselines]` adds torch for encoder baselines).

```bash
pytest -q -m "not model"                     # fast tests, fake backend, no weights
pytest -q -m model                           # real 0.5B model tests (slow)
pytest -q tests/test_api.py::test_name       # single test

groundone data check | shortcut                          # leakage check (exit 1 on fail), shortcut baseline (dataset builder: being rewritten, see docs/dataset_plan.md)
groundone train --config train_0.5b.yaml [--run NAME]    # configs in Project/GroundOne/configs/; flags override YAML
groundone calibrate --adapter <run>
groundone eval --suite aggrefact|ragtruth|anli|all --adapter <run> --name <results-name> [--limit N]
groundone serve --size 0.5b --adapter <run>              # 127.0.0.1:8019, /playground, /docs
groundone baselines rizzo|encoder ...                    # comparison systems, same test files and metrics
groundone guard queue.txt                                # run queued shell commands one at a time under the memory guard
```

There is no linter configured. HHEM baseline needs `transformers < 4.50` and runs from a separate env (`Project/phase0/.venv-hhem`, `PYTHONPATH=src`). `Project/data/download.py` fetches datasets (LLM-AggreFact is gated: `hf auth login` first).

Thesis build (from `Thesis/`): `latexmk -pdf thesis.tex` (pdflatex + biber; not verified here).

## Architecture (needs several files to see)

- **`prompts.py` is the single source of truth** for the prompt layout and question set (currently `sup`, `three`, `strict`, `lenient`; to be reduced to the single three-way decision of D20). Training, evaluation and inference all render through it so training text == inference text. Changing `SYSTEM`, `QUESTIONS` or the layout requires bumping `PROMPT_VERSION`: calibrations and results are tied to it.
- **Prompt = shared prefix + short suffix.** The prefix (document + numbered answer sentences) is identical for all K questions; the suffix asks one question about sentence `[i]`. `backend.py` prefills the common prefix once, replicates the KV cache along the batch axis and runs suffixes as right-padded batches (`score_shared`, exact vs scoring each prompt alone); `score_many` handles unrelated pair-dataset prompts. Output is the raw logits of the allowed letters (A/B or A/B/C), no generation.
- **`engine.py`** wraps the backend in a thread-safe service: ALL MLX calls run on one long-lived worker thread (Metal contexts must not hop threads); requests are serialised by a lock, parallelism is inside a request. `api.py` (FastAPI) exposes native `/v1/verify` (`schema.py`) and the TypeSafe/Jev-compatible `/v1/systemone` (`compat.py`, same contract as Rizzo-Flow).
- **Training (`training/train.py`)**: loss is cross-entropy over the allowed answer letters only, at the last prompt token; prompt never supervised. LoRA on all linear layers, token-budget length-bucketed batches. Each run writes `Project/models/<run>/` (`adapters.safetensors`, `groundone.json` with the base model, `config.yaml`, `train_log.jsonl`, `best/`); run directories are never overwritten. `config.resolve_model` maps a run name to base repo + adapter.
- **Calibration** (`calibration.py`): temperature per question type, bound to the model fingerprint (adapter SHA + prompt version); a mismatched fingerprint is rejected.
- **Data (`data/`)**: the dataset is being rebuilt from scratch following `Project/docs/dataset_plan.md` (task D20: one three-way decision per answer sentence, K = number of sentences; test set frozen first). `leakage.py` must PASS: splits are by group ID (ANLI premise hash, RAGTruth `source_id`, document hash), never by row; run it after every build. Raw data and processed JSONL/parquet are gitignored; manifests and reports are tracked.
- **Eval/baselines**: B1 untrained base (omit `--adapter`), B3 Rizzo-Flow via HTTP, B4 encoders (MiniCheck, HHEM; documents chunked ~400 words, max over chunks). All write to `Project/results/<name>/`.
- `Project/phase0/scripts/` and `Project/EDA/scripts/` are numbered one-off experiment scripts (feasibility, EDA) with their own `common.py`; they are history/reference, not the package.

## Operational rules

- **Long jobs (training, evals) must run under `groundone guard`** (kills a job when free memory < 2 GB or swap grows > 3 GB; limits overridable via `Project/runs/guard/thresholds.json`). The Mac has frozen once without it. Run them with `nohup`/`caffeinate`.
- **No forced time limits on unattended runs**: keep `max_hours: 0` in training configs; a late finish is acceptable, truncated results are not. Queue jobs sequentially and report expected end times instead.
- Models, adapters, runs and data are gitignored; only small JSON summaries and reports are tracked. Ask before downloading large models/datasets.
- `.claude/settings.local.json` denies `git push`, `git reset`, `git checkout` and deletion of `Vault/`, `Thesis/`, `Project_old/`.
