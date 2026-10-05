# GroundOne

**A specialist System One for sentence-level groundedness verification in local RAG.**
Given a retrieved document and a generated answer, GroundOne decides for every sentence whether it is supported, contradicted or not mentioned by the document. It also applies verification rules given in the request. It never generates text: the document and the answer are read once, all K questions about all sentences are scored in one batched forward pass, and the probability of each answer is read from the logits of single answer letters.

It runs fully on-device on Apple Silicon (MLX) with fine-tuned Qwen2.5 0.5B or 3B models. MSc thesis project; design, decisions and results are in [`docs/`](docs/).

| | |
| --- | --- |
| Models | Qwen2.5-0.5B-Instruct, Qwen2.5-3B-Instruct (MLX 8-bit) + GroundOne LoRA adapters |
| Questions | `sup` supported? · `three` supported / contradicted / not mentioned · `strict` and `lenient` verification rules |
| APIs | native `POST /v1/verify`; TypeSafe/Jev-compatible `POST /v1/systemone` (same contract as Rizzo-Flow) |
| Output | probabilities per sentence and question, 0 generated tokens, optional temperature calibration |

## Install

```bash
cd Project/GroundOne
uv venv --python 3.12 .venv            # a native arm64 Python is required for MLX
uv pip install --python .venv/bin/python -e ".[test]"
source .venv/bin/activate              # or prefix commands with .venv/bin/
```

## Command-line interface

```bash
groundone serve --size 0.5b --adapter <run>      # HTTP API on 127.0.0.1:8019 (+ /playground)
groundone verify request.json --adapter <run>    # one request, no server
groundone systemone request.json                 # one Jev-compatible request, no server
groundone schema [--response | --compat]         # JSON Schema of the API
groundone models                                 # base models and trained runs

groundone data build | check | shortcut          # datasets (data/processed/<version>), leakage check, shortcut baseline
groundone train --config train_0.5b.yaml [--run <run>]   # hyper-parameters in configs/*.yaml
groundone calibrate --adapter <run>              # one temperature per question type, fitted on dev
groundone eval --suite aggrefact|ragtruth|anli|all --adapter <run> --name <results-name> [--limit N]
groundone guard queue.txt                        # run long jobs one at a time under a memory guard

# comparison systems (baselines), same test files and metrics as `groundone eval`
groundone baselines rizzo --url http://127.0.0.1:8017 --suite all --limit 1000 --name rizzo-flow-4b
groundone baselines encoder --model minicheck-roberta|minicheck-deberta|hhem --suite all --name <results-name>
```

`baselines rizzo` queries a running Rizzo-Flow server (B3, general-purpose System One) through the Jev-compatible API
that GroundOne also serves. `baselines encoder` runs the encoder fact-checkers (B4) with PyTorch: install the extra
with `uv pip install -e ".[baselines]"`; HHEM needs `transformers` < 4.50 and runs from a separate environment
(`PYTHONPATH=src <hhem-env>/bin/python -m groundone.baselines.encoders --model hhem ...`).

Without `--adapter` the untrained base model is served (baseline B1). Experiment data and outputs live in the workspace one level up (`Project/data`, `Project/models`, `Project/results`, `Project/runs`). Trained runs live in `Project/models/<run>/`
(`adapters.safetensors`, `adapter_config.json`, `config.yaml`, `groundone.json`, `calibration.json`, `train_log.jsonl`).

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
