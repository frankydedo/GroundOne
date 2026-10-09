# GroundOne workspace

Experiment workspace of the MSc thesis *A Specialist System One for Local RAG* (GroundOne): a compact language model,
fine-tuned with LoRA, that verifies every sentence of a RAG answer against the retrieved document in one forward pass.
The thesis itself is in `../Thesis/`, the literature wiki in `../Vault/`.

## Map

| Folder | What it holds | Versioned |
| --- | --- | --- |
| `GroundOne/` | The software: installable Python package `groundone` (CLI, HTTP API, dataset builder, training, evaluation, baselines, figures), configs, tests. Usage: `GroundOne/README.md` | yes |
| `docs/` | Plans, tracker, findings for the thesis (index: `docs/README.md`) | yes |
| `data/` | `download.py` and `manifest.json`; `raw/` (downloaded datasets); `processed/groundone/` (the dataset: train, dev, frozen tests T1–T3, data card, check reports) | scripts, manifests, reports, data card |
| `outputs/models/` | Trained adapters (`g1-05b-b1`, `g1-3b-b1`), each with `config.yaml`, `train_log.jsonl`, `best/` and `calibration.json` | no |
| `outputs/results/` | One folder per system: `t1/`, `t2/`, `t3/` (test sets), `latency/`, `calibration/`; `metrics.json` + `predictions.parquet` | `metrics.json` only |
| `outputs/figures/` | Thesis figures (300-dpi PNG) with draft captions in each `index.md` | yes |
| `outputs/logs/` | Memory-guard logs and job output (`guard/thresholds.json` sets the limits) | no |
| `experiments/feasibility/` | Phase 0/0b feasibility study (numbered scripts, data, results, logs); report: `docs/phase0_report.md` | scripts, results JSON |
| `experiments/eda/` | Exploratory analysis of the sources and of the built dataset (scripts, `report/eda_report.md`) | yes |
| `jobs/` | Queues run under the memory guard and job scripts: records of what ran | yes |
| `envs/` | Auxiliary Python environments: `hhem/` (HHEM needs `transformers` < 4.50), `feasibility/` | no |
| `_archive/` | Earlier experiments (first datasets, their models, results and figures) | no |

## Reproduce

All commands run from this folder with the package environment (`GroundOne/.venv`, see `GroundOne/README.md`).

```bash
python data/download.py                                   # datasets into data/raw/ (LLM-AggreFact is gated: hf auth login)
GroundOne/.venv/bin/groundone data build                  # dataset + checks; the frozen test sets must be reproduced exactly
GroundOne/.venv/bin/groundone data check                  # leakage check
GroundOne/.venv/bin/groundone guard jobs/queue_night3.txt # 0.5B: train, evaluate (one job at a time, memory guard)
GroundOne/.venv/bin/groundone guard jobs/queue_day4.txt   # baselines, judges + latency, 3B
GroundOne/.venv/bin/groundone guard jobs/queue_day5.txt   # equal-output judge B0d (D25)
GroundOne/.venv/bin/groundone figures all                 # all figures -> outputs/figures/
GroundOne/.venv/bin/python experiments/eda/scripts/01_ragtruth.py   # EDA (then 02, 03, 04, make_report.py)
```

The HHEM baseline runs from its own environment:
`env PYTHONPATH=GroundOne/src envs/hhem/bin/python -m groundone.cli baselines frozen --system encoder --model hhem --suite t1 --name hhem`.
