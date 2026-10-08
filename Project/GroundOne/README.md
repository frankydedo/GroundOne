# GroundOne

**A specialist System One for sentence-level groundedness verification in local RAG.**
Given a retrieved document and a generated answer, GroundOne decides for every sentence whether it is supported, contradicted or not mentioned by the document. It never generates text. A marker follows every sentence of the answer, and the verdicts for all K sentences are read from the logits of three answer letters in one forward pass (readout design b). A binary score and strict / lenient policies are derived from the three probabilities.

It runs fully on-device on Apple Silicon (MLX) with fine-tuned Qwen2.5 0.5B or 3B models. MSc thesis project; design, decisions and results are in [`../docs/`](../docs/).

| | |
| --- | --- |
| Models | Qwen2.5-0.5B-Instruct, Qwen2.5-3B-Instruct (MLX 8-bit) + GroundOne LoRA adapters |
| Decision | one per sentence: A supported · B contradicted · C not mentioned (training and evaluation: design b; the HTTP API still uses the earlier per-question format, design a) |
| APIs | native `POST /v1/verify`; TypeSafe/Jev-compatible `POST /v1/systemone` (same contract as Rizzo-Flow) |
| Output | three probabilities per sentence, 0 generated tokens, optional calibration (temperature + bias) |

## Install

```bash
cd Project/GroundOne
uv venv --python 3.12 .venv            # a native arm64 Python is required for MLX
uv pip install --python .venv/bin/python -e ".[test]"
source .venv/bin/activate              # or prefix commands with .venv/bin/
```

## Command-line interface

```bash
# serving (HTTP API, still design a)
groundone serve --size 0.5b --adapter <run>      # HTTP API on 127.0.0.1:8019 (+ /playground)
groundone verify request.json --adapter <run>    # one request, no server
groundone systemone request.json                 # one Jev-compatible request, no server
groundone schema [--response | --compat]         # JSON Schema of the API
groundone models                                 # base models and trained runs

# dataset (Project/docs/dataset_plan.md)
groundone data build                             # build Project/data/processed/groundone/ + checks (C2-C5); refuses to change frozen tests
groundone data check | shortcut                  # leakage check (exit 1 on failure), sentence-only shortcut baseline
groundone data freeze                            # record the SHA-256 of the test sets (done 2026-10-07)
groundone data rows                              # design (a) training rows (fallback design only)

# training, calibration, evaluation (design b)
groundone train --config train_0.5b.yaml [--run <run>]   # hyper-parameters in configs/*.yaml; flags override
groundone calibrate-b --adapter <run>/best --name <results-name>   # temperature + bias on dev; reliability figures
groundone test --suite t1|t2|t3 --adapter <run>/best --name <results-name> [--limit N] [--design a]
groundone guard queue.txt                        # run long jobs one at a time under a memory guard
groundone figures all | dataset | benchmarks | training <run>   # thesis figures -> Project/outputs/figures/<group>/

# baselines on the frozen tests, same metrics as `groundone test`
groundone test --suite t1 --size 0.5b --design a --name <name>               # B1 untrained readout (no adapter)
groundone baselines frozen --system encoder --model minicheck-roberta|hhem --suite t1 --name <name>   # B4
groundone baselines frozen --system rizzo --url http://127.0.0.1:8017 --suite t1 --limit 300 --name <name>   # B3
groundone baselines judges --system terse|verbose|groundone|readout-a --size 0.5b [--adapter <run>/best] --name <name>   # B0 + latency
```

- `baselines frozen --system rizzo` queries a running Rizzo-Flow server (B3, general-purpose System One) through the Jev-compatible API.
- The encoders (B4) need PyTorch: `uv pip install -e ".[baselines]"`. HHEM needs `transformers` < 4.50 and runs from a separate environment: `env PYTHONPATH=GroundOne/src <hhem-env>/bin/python -m groundone.cli baselines frozen --system encoder --model hhem ...`.
- Legacy entry points for the earlier datasets (`groundone eval`, `groundone calibrate`, `baselines encoder|rizzo`) are kept for reference only.
- Without `--adapter` the untrained base model is used. Experiment data and outputs live in the workspace one level up (`Project/data`, `Project/outputs/models`, `Project/outputs/results`, `Project/outputs/figures`, `Project/outputs/logs`).
- Trained runs live in `Project/outputs/models/<run>/`: `adapters.safetensors`, `adapter_config.json`, `config.yaml`, `groundone.json`, `train_log.jsonl`, and `best/` with `calibration.json`.

## HTTP API

**Native: `POST /v1/verify`**

```bash
curl -s localhost:8019/v1/verify -H 'Content-Type: application/json' -d '{
  "document": "The Eiffel Tower is in Paris. It was completed in 1889 and is 330 metres tall.",
  "answer": "The Eiffel Tower is in Paris. It was finished in 1889. It is 500 metres tall.",
  "questions": ["sup", "three"],
  "threshold": 0.5
}'
```

The answer is split into sentences (or pass `sentences: [...]`). For each sentence the response gives `p_supported`, `flagged` (`p_supported < threshold`), the probabilities of every answer per question, the most likely labels, and `n_decisions`, `usage` (input tokens, 0 output tokens) and `timing`.

**Compatible: `POST /v1/systemone`, `GET /v1/models`.** These follow the public TypeSafe/Jev API, the contract Rizzo-Flow also serves (`noul`, `choice` and `score` questions over a shared `state`). A client written for them works by changing the base URL. The response `model` always names the local GroundOne model. Generic questions are answered by the same engine, but GroundOne is trained only for groundedness questions. Bearer auth is enforced on these routes when `GROUNDONE_API_KEY` is set.

Other routes: `GET /health` (model, adapter hash, prompt version, fingerprint), `GET /playground` (web UI), `GET /docs` (OpenAPI).

## Layout

```
Project/GroundOne/              the software (this folder)
configs/          training hyper-parameters (train_0.5b.yaml, train_3b.yaml)
src/groundone/
  prompts.py      single source of truth for the prompt format and question set (training = inference)
  backend.py      MLX model + adapter; shared-prefix batched scoring and length-batched scoring
  engine.py       thread-safe service (one MLX thread, request lock); verify / systemone / predict
  schema.py       strict native API contract          compat.py   TypeSafe/Jev-compatible contract
  api.py          FastAPI app                         cli.py      command-line interface
  calibration.py  temperature scaling bound to the model fingerprint
  data/           dataset build, leakage check, shortcut baseline
  training/       LoRA training loop with the restricted answer-letter loss
  eval/           evaluation suites and metrics
  baselines/      Rizzo-Flow client (B3) and encoder fact-checkers (B4)
  figures/        thesis figures from every phase (fixed colour per system)
  tools/          memory guard for unattended runs
tests/            fast tests with a fake backend; `pytest -m model` runs the real-model tests

Project/                        the experiment workspace (one level up)
  data/  models/  results/  runs/  EDA/  phase0/  docs/
```

## Tests

```bash
pytest -q -m "not model"    # API, schema, compatible wire format, label mapping (no weights)
pytest -q -m model          # real 0.5B: batched scoring == one pass per question; end-to-end verify
```
