# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

MSc thesis workspace. The active project is **GroundOne**: a specialist "System One" (single forward pass, answer-letter logit readout, zero generated tokens) that verifies, sentence by sentence, whether a RAG answer is supported / contradicted / not mentioned by the retrieved document. Fine-tuned Qwen2.5 0.5B and 3B (LoRA, MLX 8-bit) on an Apple Silicon 16 GB laptop. The earlier tool-routing thesis is abandoned (`Project_old/`, gitignored, history only).

Deadlines: new experiments only until **2026-10-30**; experiment and written thesis due **2026-11-10**. The compass is `Project/docs/implementation_plan.md` (decision log in §3, research questions in §2); the dataset is specified in `Project/docs/dataset_plan.md`; status tracker is `Project/docs/tracker.md`. Earlier models/results/figures are archived in `Project/_archive/` (gitignored); the thesis describes only the final dataset. Update the decision log when a decision changes, and do not silently change the experiment.

Language: chat with the user in Italian; code, docs and the thesis are in English. Give objective critique, not validation. Keep claims honest (e.g. the gain over a single-token LLM control is ~0; the gain comes from model size/specialisation, shared-prefix multi-claim scoring, rationale-free judges and calibration).

## Top-level layout

- `Project/GroundOne/` – the software (Python package `groundone`, CLI, HTTP API, tests). Install and CLI usage are documented in its `README.md`.
- `Project/` (the *workspace*, one level above the package; override with `GROUNDONE_WORKSPACE`), map in `Project/README.md`: `data/` (download script, raw + processed datasets), `outputs/` (everything the commands generate: `models/`, `results/`, `figures/`, `logs/`), `experiments/` (one-off studies: `feasibility/` = Phase 0, `eda/`), `jobs/` (guard queues and job scripts), `envs/` (auxiliary venvs: `hhem/`, `feasibility/`; gitignored), `docs/`, `_archive/` (earlier experiments, gitignored).
- `Thesis/` – LaTeX thesis (`toptesi` class, biblatex/biber, glossaries). Chapters in `Thesis/content/chapters/ch*.tex`; build artefacts (`thesis.aux`, `.pdf`, …) are untracked.
- `Vault/` – Obsidian LLM-wiki of papers and notes (`Vault/CLAUDE.md` defines its own workflow; `raw/` sources are immutable). Not code.
- `SystemOne_repos/` (CLM, SemIf, rizzo-flow), `Preprocessing/` – third-party clones / audio transcription, gitignored; related work only. Rizzo-Flow is also used as a running baseline server.

## Commands

Run from `Project/GroundOne` with the venv (`uv venv --python 3.12 .venv` – native arm64 Python required for MLX; `uv pip install --python .venv/bin/python -e ".[test]"`; `.[baselines]` adds torch for encoder baselines).

```bash
pytest -q -m "not model"                     # fast tests, fake backend, no weights
pytest -q -m model                           # real 0.5B model tests (slow)

groundone data build | check | shortcut | freeze   # dataset + checks; leakage check exits 1 on failure; tests are frozen (build refuses changes)
groundone train --config train_0.5b.yaml [--run NAME]     # design (b) by default; configs in Project/GroundOne/configs/
groundone calibrate-b --adapter <run>/best --name <results-name>   # temperature + bias on dev
groundone test --suite t1|t2|t3 --adapter <run>/best --name <results-name>   # frozen tests (T1 RAGTruth, T2 LLM-AggreFact, T3 VitaminC)
groundone baselines frozen|judges ...                    # encoders / Rizzo-Flow on the frozen tests; generative judges + latency vs K
groundone figures all | dataset | benchmarks | training RUN
groundone serve --size 0.5b --adapter <run>              # 127.0.0.1:8019 (HTTP API still uses design a)
groundone guard queue.txt                                # run queued shell commands one at a time under the memory guard
```

There is no linter configured. HHEM baseline needs `transformers < 4.50` and runs from a separate env (`Project/envs/hhem`, `PYTHONPATH=src`). `Project/data/download.py` fetches datasets (LLM-AggreFact is gated: `hf auth login` first).

Thesis build (from `Thesis/`): `latexmk -pdf thesis.tex` (pdflatex + biber; not verified here).

## Architecture (needs several files to see)

- **`prompts.py` is the single source of truth** for the prompt formats: design (b) `encode_marked` (default) and the design (a) question set (`three` is the one used; `sup`/`strict`/`lenient` are legacy). Training, evaluation and inference all render through it so training text == inference text. Changing `SYSTEM`, `QUESTIONS` or the layout requires bumping `PROMPT_VERSION`: calibrations and results are tied to it.
- **Readout design (b), the default (D22).** `prompts.encode_marked` writes the answer with a marker " Verdict:" after every scored sentence; `Backend.score_positions` runs one forward pass per answer and applies the output head only at the markers (`readout.py`), returning A/B/C logits (supported / contradicted / not mentioned). Training (`train.py --design b`) uses a class-weighted loss over all markers. **Design (a)**, the fallback, is a shared prefix plus one question suffix per sentence (`score_shared`, KV cache replicated K times); it is still used by the HTTP API and by the untrained baseline B1.
- **`engine.py`** wraps the backend in a thread-safe service: ALL MLX calls run on one long-lived worker thread (Metal contexts must not hop threads); requests are serialised by a lock, parallelism is inside a request. `api.py` (FastAPI) exposes native `/v1/verify` (`schema.py`) and the TypeSafe/Jev-compatible `/v1/systemone` (`compat.py`, same contract as Rizzo-Flow).
- **Training (`training/train.py`)**: loss is cross-entropy over the allowed answer letters only, at the last prompt token; prompt never supervised. LoRA on all linear layers, token-budget length-bucketed batches. Each run writes `Project/outputs/models/<run>/` (`adapters.safetensors`, `groundone.json` with the base model, `config.yaml`, `train_log.jsonl`, `best/`); run directories are never overwritten. `config.resolve_model` maps a run name to base repo + adapter.
- **Calibration** (`calibration.py`, `eval/calibrate_b.py`): temperature + per-class bias fitted on dev, bound to the model fingerprint (adapter SHA + prompt version). Primary classification metrics use the raw (balanced) decision; calibrated probabilities are used for ECE and thresholds (D24).
- **Data (`data/`)**: `build.py` builds `Project/data/processed/groundone/` from RAGTruth (train/dev/T1), LLM-AggreFact (T2) and VitaminC (T3) following `Project/docs/dataset_plan.md`; `segment.py` (pysbd + checkable-content rule) is shared with inference; the test sets are frozen (`tests_frozen.json`). `leakage.py` must PASS: splits are by group ID (ANLI premise hash, RAGTruth `source_id`, document hash), never by row; run it after every build. Raw data and processed JSONL/parquet are gitignored; manifests and reports are tracked.
- **Eval/baselines**: `eval/tests.py` (frozen tests, metrics by task and K band, word-overlap baseline); `baselines/frozen.py` (B4 encoders MiniCheck/HHEM, B3 Rizzo-Flow); `baselines/judges.py` (B0 terse/verbose generative judges and the latency protocol). All write to `Project/outputs/results/<name>/`. `eval/evaluate.py`, `baselines/encoders.py|rizzo.py` entry points, `outputs/figures/results.py|diagnostics.py` are legacy (earlier datasets).
- `Project/experiments/feasibility/scripts/` and `Project/experiments/eda/scripts/` are numbered one-off experiment scripts (feasibility, EDA) with their own `common.py`; they are history/reference, not the package.

## Operational rules

- **Long jobs (training, evals) must run under `groundone guard`** (kills a job when free memory < 2 GB or swap grows > 3 GB; limits overridable via `Project/outputs/logs/guard/thresholds.json`). The Mac has frozen once without it. Run them with `nohup`/`caffeinate`.
- **No forced time limits on unattended runs**: keep `max_hours: 0` in training configs; a late finish is acceptable, truncated results are not. Queue jobs sequentially and report expected end times instead.
- Models, adapters, runs and data are gitignored; only small JSON summaries and reports are tracked. Ask before downloading large models/datasets.
- `.claude/settings.local.json` denies `git push`, `git reset`, `git checkout` and deletion of `Vault/`, `Thesis/`, `Project_old/`.
