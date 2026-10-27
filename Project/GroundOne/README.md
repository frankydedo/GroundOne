# GroundOne

**A specialist System One for sentence-level groundedness verification in local RAG.**
Given a retrieved document and a generated answer, GroundOne decides for every sentence whether it is supported, contradicted or not mentioned by the document. It never generates text. A marker follows every sentence of the answer, and the verdicts for all K sentences are read from the logits of three answer letters in one forward pass (readout design b). A binary score and strict / lenient policies are derived from the three probabilities.

It runs fully on-device on Apple Silicon (MLX) with fine-tuned Qwen2.5 0.5B or 3B models. MSc thesis project; design, decisions and results are in [`../docs/`](../docs/).

| | |
| --- | --- |
| Models | Qwen2.5-0.5B-Instruct, Qwen2.5-3B-Instruct (MLX 8-bit) + GroundOne LoRA adapters |
| Decision | one per sentence: A supported · B contradicted · C not mentioned (design b in training, evaluation and the HTTP API; design a only for base models and the compatible API) |
| APIs | native `POST /v1/verify` and `POST /v1/prefetch`; TypeSafe/Jev-compatible `POST /v1/systemone` (same contract as Rizzo-Flow) |
| Output | per sentence: label, three calibrated probabilities, strict / lenient flags (one coherent rule, D27); 0 generated tokens |

## Install

```bash
cd Project/GroundOne
uv venv --python 3.12 .venv            # a native arm64 Python is required for MLX
uv pip install --python .venv/bin/python -e ".[test]"
source .venv/bin/activate              # or prefix commands with .venv/bin/
```

## Command-line interface

```bash
# serving (HTTP API, design b with a design-(b) adapter)
groundone serve --adapter <run>/best             # HTTP API on 127.0.0.1:8019 (+ /playground); uses <run>/best/calibration.json
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
groundone calibrate-b --adapter <run>/best --name <results-name>   # temperature + bias + served threshold on dev; reliability figures
groundone test --suite t1|t2|t3 --adapter <run>/best --name <results-name> [--limit N] [--design a]
groundone guard queue.txt                        # run long jobs one at a time under a memory guard
groundone figures all | dataset | benchmarks | training <run>   # thesis figures -> Project/outputs/figures/<group>/

# baselines on the frozen tests, same metrics as `groundone test`
groundone test --suite t1 --size 0.5b --design a --name <name>               # B1 untrained readout (no adapter)
groundone baselines frozen --system encoder --model minicheck-roberta|hhem --suite t1 --name <name>   # B4
groundone baselines frozen --system rizzo --url http://127.0.0.1:8017 --suite t1 --limit 300 --name <name>   # B3
groundone baselines judges --system terse|verbose|json|terse-logits|groundone|readout-a --size 0.5b [--adapter <run>/best] [--split dev] [--energy] --name <name>   # B0, B0d + latency / energy
groundone baselines judges-calibrate --name <name> [--calibration FILE]   # calibrate a judge on its dev run (D25)
groundone baselines decompose --system groundone|terse|verbose --size 0.5b [--adapter <run>/best] [--cache none|fixed|doc|rewrite] --name <name>   # latency split: reading (prefill) vs deciding; prefix caching; rewrite = answer-prefix reuse (D32)
groundone baselines decompose-report --name <name>                         # medians, overall and decision-only speed-ups
groundone test --suite t1 --adapter <run>/best --decision generate --name <name>   # control B2: verdict = generated token
groundone bootstrap                              # CIs and paired tests from saved predictions
groundone matrix                                 # results matrix -> Project/docs/tracker.md
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
  "answer": "Sure! The Eiffel Tower is in Paris. It was finished in 1889. It is 500 metres tall."
}'
```

With a design (b) adapter (served since D27):
- **Segmentation.** The answer is segmented with the rule used for training (`data/segment.py`), or you can pass `sentences: [...]`. Sentences without checkable content ("Sure!") come back with `scored: false` and no verdict.
- **One pass.** All verdicts are read in one forward pass at the markers.
- **Prefix cache (D32).** The fixed instructions are read once per process, and the last four documents stay in the KV cache, so another answer on a cached document (a rewritten answer, a second question on the same sources) costs only the answer's tokens. It is exact under causal attention (`tests/test_model.py`). The last answer verified on each document is kept as well, so after a rewrite the pass starts at the first changed token and the verdicts of the sentences before it are reused. The response field `prefix_cache` says what was reused (`answer prefix`, `document`, `instructions`); `GROUNDONE_PREFIX_CACHE=0` turns it off.
- **Prefetch: `POST /v1/prefetch` `{"document": ...}`.** Reads the document into the prefix cache before the answer exists (while the generator writes it, or while the user reads it), so that the first `/v1/verify` on it already reads only the answer. Returns `cached` (`read`, `already`, `disabled`), `head_tokens` and `seconds`.
- **Per scored sentence:** `labels.three` (supported / contradicted / not_mentioned), the three probabilities in `answers.three`, `p_supported`, and the flags `flag_strict` (= `flagged`, not supported) and `flag_lenient` (contradicted). `questions` (`sup`, `strict`, `lenient`) adds derived views of the same three probabilities.
- **One coherent rule.** Labels, flags and the probabilities shown come from a single rule. The probabilities are calibrated (`<run>/best/calibration.json`), and the label is "supported" iff `p_supported >= threshold`, otherwise the more probable of the other two. The threshold is the one fitted on dev by `calibrate-b`, or the request's `threshold`. With no threshold at all, the label is the argmax of the raw class-balanced logits, the decision used in the evaluation.
- **Response metadata:** `design`, `decision_rule`, `threshold`, `n_decisions`, `usage` (input tokens, 0 output tokens) and `timing`.

Base models and design (a) adapters use the earlier per-question format: one question per sentence over a shared prefix, `flagged` iff P(supported) < threshold (default 0.5).

**Compatible: `POST /v1/systemone`, `GET /v1/models`.** These follow the public TypeSafe/Jev API, the contract Rizzo-Flow also serves (`noul`, `choice` and `score` questions over a shared `state`). A client written for them works by changing the base URL. The response `model` always names the local GroundOne model. Generic questions are answered by the same engine, but GroundOne is trained only for groundedness questions. Bearer auth is enforced on these routes when `GROUNDONE_API_KEY` is set.

The compatible API answers generic questions with the per-question format (design a).

Other routes: `GET /health` (model, adapter hash, prompt version, fingerprint, design, served threshold), `GET /playground` (web UI: labels follow the threshold slider with the same rule as the server), `GET /docs` (OpenAPI).

## Layout

```
Project/GroundOne/              the software (this folder)
configs/          training hyper-parameters (train_0.5b.yaml, train_3b.yaml)
src/groundone/
  prompts.py      single source of truth for the prompt formats (design b markers, design a questions; training = inference)
  readout.py      logits at the marker positions only (design b)
  backend.py      MLX model + adapter; shared-prefix batched scoring, length-batched scoring, design-(b) pass with a cached prefix
  engine.py       thread-safe service (one MLX thread, request lock); verify / systemone / predict
  schema.py       strict native API contract          compat.py   TypeSafe/Jev-compatible contract
  api.py          FastAPI app + playground.html       cli.py      command-line interface
  calibration.py  temperature + bias and the served threshold, bound to the model fingerprint
  data/           dataset build, segmentation (segment.py, shared with inference), leakage check, shortcut baseline
  training/       LoRA training loop with the restricted answer-letter loss
  eval/           frozen tests (tests.py, incl. B2), calibrate_b.py, bootstrap.py, metrics
  baselines/      encoders (B4), Rizzo-Flow (B3), LLM judges incl. equal-output (B0, B0d), latency / energy, latency split (decompose)
  figures/        thesis figures from every phase (fixed colour per system)
  tools/          memory guard, results matrix, powermetrics meter
tests/            fast tests with a fake backend; `pytest -m model` runs the real-model tests

Project/                        the experiment workspace (one level up)
  data/  outputs/{models,results,figures,logs}/  experiments/  jobs/  envs/  docs/
```

## Tests

```bash
pytest -q -m "not model"    # API, schema, compatible wire format, label mapping (no weights)
pytest -q -m model          # real 0.5B: batched scoring == one pass per question; end-to-end verify
```
