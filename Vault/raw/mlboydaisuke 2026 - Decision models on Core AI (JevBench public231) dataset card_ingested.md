Source: https://huggingface.co/datasets/mlboydaisuke/coreai-decision-models-public231 (revision b7a859ca9cbd9c365479e38e651ad034aee4f212) — retrieved 2026-10-10

---
license: mit
pretty_name: Decision models on Core AI, 231 public items
tags:
- benchmark
- decision-models
- core-ai
- apple-silicon
viewer: false
---

# Decision models on Core AI, 231 public items

Eight models from the coreai-kit catalog answered the 231 public items of [JevBench](https://github.com/fstandhartinger/jevbench) (easy 48, standard 72, hard 111) with Core AI on a Mac: Apple M4 Max, int8 bundles, except the laya-multilingual encoder in fp16. Six are decision models; two are chat models asked zero-shot. JevBench's own harness at commit `2fa63fa` (v1.4.0) sent each item through its stock `typesafe` adapter to `decide-cli serve` from [coreai-kit](https://github.com/john-rocky/coreai-kit) at commit `adbc755`, one question per request. JevBench's own code scored the answers. Every per-item result is here, so the accuracy, calibration and latency figures can be recomputed from this dataset.

This is an independent run, not an official JevBench result.

## Results

| model (kit catalog id, Mac int8, contended) | easy 48 | standard 72 | hard 111 | ECE hard | p50 s (231) | p95 s (231) | hard max s | bundle | note |
|---|---|---|---|---|---|---|---|---|---|
| apus-decision-v1-4b | 1.000 | 0.986 | 0.559 | 0.347 | 5.94 | 142.09 | 217.6 | 5.4G | three model servers on one GPU (30-item solo re-check: identical probabilities) |
| decider-0.8b | 1.000 | 0.833 | 0.414 | 0.320 | 1.69 | 29.10 | 90.6 | 1.2G | server alone |
| laya-multilingual | 0.896 | 0.403 | 0.342 | 0.273 | 0.02 | 0.20 | 0.3 | 649M | encoder s256: hard 95/111 rows truncated at 256 tokens |
| minicpm5-2b | 0.979 | 0.708 | 0.459 | 0.241 | 0.14 | 1.19 | 1.8 | 2.5G | zero-shot chat, catalog temperature 2.93 |
| openthai-systemone | 1.000 | 0.819 | 0.324 | 0.449 | 0.62 | 25.93 | 39.0 | 1.0G | server alone (three short model loads overlapped; 5-item solo re-check identical) |
| qwen3.5-2b | 1.000 | 0.750 | 0.441 | 0.245 | 2.74 | 50.22 | 62.3 | 2.8G | zero-shot chat, no calibration (temperature 1), server alone (kit gate runs overlapped 08:29–09:02) |
| qwen3.5-2b-decision | 1.000 | 0.778 | 0.405 | 0.235 | 3.24 | 92.89 | 138.5 | 2.8G | three model servers on one GPU (30-item solo re-check: identical probabilities) |
| system-one-scorer-4b | 1.000 | 0.861 | 0.505 | 0.164 | 8.96 | 61.61 | 72.0 | 4.7G | author max_len 384/row: hard 70/111 rows state cut; three model servers on one GPU (30-item solo re-check: identical probabilities) |

| published system (same 231 public items, their own serving stack) | easy | standard | hard | p50 s easy/std/hard |
|---|---|---|---|---|
| Jev 1.13.0 (TypeSafe AI) | 1.000 | 0.986 | 0.730 | 0.665/0.653/0.672 |
| Winnow-12B Q8 | 1.000 | 0.958 | 0.730 | 0.203/0.209/0.291 |
| classifier.dev (fast tier) | 1.000 | 0.986 | 0.703 | 0.378/0.387/0.374 |
| decider-35b-a3b (Mapika) | 1.000 | 0.972 | 0.667 | 0.283/0.283/0.312 |
| SemIf, formerly OpenJev (Qwen3.5-4B, TheoLeeCJ) | 1.000 | 0.986 | 0.613 | 0.188/0.188/0.223 |
| reflex 4B (kshetrajna12) | 1.000 | 0.944 | 0.604 | 0.33/1.128/1.879 |
| open-alternative-jev (Qwen3.5-4B, IkerMoel) | 1.000 | 0.833 | 0.568 | 0.191/0.192/0.247 |
| decider-2b (Mapika) | 1.000 | 0.847 | 0.495 | 0.26/0.259/0.268 |
| system-one-open (Gemma 4 E2B LoRA on an L4) | 1.000 | 0.931 | 0.486 | 0.516/0.649/0.682 |
| kev 0.6B (research preview) | 1.000 | 0.806 | 0.432 | 0.421/0.589/0.608 |
| Laya (Convai Innovations, ModernBERT-large 421M) | 0.958 | 0.694 | 0.351 | 0.368/0.382/1.922 |

Footnotes
- laya-multilingual: encoder bundle wfp16-s256 → hard 95/111 rows truncated at 256 input tokens (states up to 3,677 tokens); easy/original untruncated (max 107).
- system-one-scorer-4b: author's encode cuts the state from its end so each row (state + question + option) fits max_len 384 → hard 70/111 rows at the cap.
- minicpm5-2b: kind chat, zero-shot under the kit's JSON decision prompt, catalog calibration temperature 2.93 (fit on SemIf perturbations108).
- decider-0.8b / openthai-systemone / qwen3.5-2b-decision: Qwen3.5-family hybrids, S=1 prefill; a 3k-token hard state costs 40–220 s per question, re-prefilled for every question at this kit commit.
- apus-decision-v1-4b hard p50: 44.0 s over the 55 rows answered while three serves ran, 8.4 s over the 56 rows answered alone.
- Solo subset p50 (recheck30, easy / original / hard): qwen3.5-2b-decision 1.07 / 1.18 / 22.0 s; apus 2.60 / 2.62 / 41.9 s; scorer 2.51 / 2.73 / 20.1 s.
- Published rows: recomputed from jevbench results/v1.2/jevbench-v1.2-per-task.json (per-item outcomes for the same 231 public ids); their runs used the entrants' own serving stacks (bf16 GPU etc.), so same items, not same conditions. JevBench's headline Intelligence/score is chance-corrected over 534 items incl. sealed ones and is not comparable to these accuracies.
- qwen3.5-2b stands in for qwen3.5-4b, which is not in the kit catalog: kind chat, zero-shot under the kit's JSON decision prompt, no calibration entry (temperature 1).
- Solo re-check (30 rows per model of the three-server run + 5 overlapped openthai rows): returned probabilities bit-identical to the concurrent runs (max |Δp| 0.0, argmax 30/30), latency ~2× lower alone.

In the qwen3.5-2b note, the kit gate runs were another session's `decide-cli` and `swift build` runs on the same Mac. They overlapped 73 and 42 of its rows; its last 67 hard rows ran with neither.

## Method

- Machine: Mac, Apple M4 Max, 128 GB, macOS 27.0 (26A428), Xcode 27.0 RC. Runs on 2026-09-24, JST (the manifests use UTC).
- Server: `decide-cli serve --model <catalog id>` from coreai-kit `adbc755` (`Examples/Decide`, release build) on 127.0.0.1. It answers the `/v1/systemone` requests that JevBench's `typesafe` adapter sends. Each model loads the bundle that the kit catalog pins at that commit (table below).
- Client: JevBench `2fa63fa` with the stock `typesafe` adapter and no API key. decider-0.8b ran through the JevBench CLI. The other seven ran through `run_tier.py`, which calls the same JevBench runner and summarizer with a 900 s HTTP timeout instead of the adapter's 120 s.
- Per model: a 3-item contract probe, JevBench's `conformance/check.py`, then the easy, original (= standard) and hard tiers.
- Scoring is JevBench's own: the predicted label is the argmax of the returned probabilities. All 8 × 231 requests returned HTTP 200, and every row was strict-valid.
- `verify.py` recomputes accuracy, ECE (top label, 10 bins) and latency from the rows. Accuracy and the hard-tier ECE equal JevBench's `summary-<tier>.json`. `table.py` rebuilds both tables.
- Latency is the client's wall clock per request. p50 and p95 are over all 231 requests of a model.
- Published rows: `published-public231.json`, recomputed from JevBench's per-item outcomes (`results/v1.2/jevbench-v1.2-per-task.json`) for the same 231 item ids.
- Solo re-check: `recheck_select.py` picked 30 items (`recheck30.jsonl`). The three models that had run as concurrent serves re-ran them alone, and so did the 5 openthai-systemone rows that overlapped other models' loads. `recheck_compare.py` wrote `<model>/recheck/compare.json`.
- Cascade: `cascade/` scores a device-to-hosted cascade from these rows and JevBench's published per-item outcomes. No new inference ran for it.

| catalog id | Hugging Face repo | revision | bundle variant |
|---|---|---|---|
| apus-decision-v1-4b | [mlboydaisuke/APUS-Decision-v1-4B-CoreAI](https://huggingface.co/mlboydaisuke/APUS-Decision-v1-4B-CoreAI) | `3e946e1c4fafd9c909492bb81e8f400439560aee` | `gpu-pipelined-b2/apus_decision_v1_4b_decode_int8hu_block32_sym` |
| decider-0.8b | [mlboydaisuke/decider-0.8b-CoreAI](https://huggingface.co/mlboydaisuke/decider-0.8b-CoreAI) | `ff60ccf563556efbf83442e891e57d68a1840728` | `gpu-pipelined/decider_0_8b_decode_int8hu_block32_sym` |
| laya-multilingual | [mlboydaisuke/Laya-Multilingual-CoreAI](https://huggingface.co/mlboydaisuke/Laya-Multilingual-CoreAI) | `1175a4e6231fdfe8946e6566276f8d71eb8f02ef` | `macos/wfp16-s256` |
| minicpm5-2b | [mlboydaisuke/MiniCPM5-2B-CoreAI](https://huggingface.co/mlboydaisuke/MiniCPM5-2B-CoreAI) | `f306590f991d66cad23af06bf72464519b65ba9f` | `int8` |
| openthai-systemone | [mlboydaisuke/OpenThai-SystemOne-CoreAI](https://huggingface.co/mlboydaisuke/OpenThai-SystemOne-CoreAI) | `e48583dab6c527fb87f47e074a5724a701c05600` | `gpu-pipelined/openthai_systemone_decode_int8lin` |
| qwen3.5-2b | [mlboydaisuke/qwen3.5-2B-CoreAI](https://huggingface.co/mlboydaisuke/qwen3.5-2B-CoreAI) | `3aa6c97d9545b9f7de6307b953a81db38cb660af` | `gpu-pipelined/qwen3_5_2b_decode_int8hu_block32_sym` |
| qwen3.5-2b-decision | [mlboydaisuke/Qwen3.5-2B-Decision-CoreAI](https://huggingface.co/mlboydaisuke/Qwen3.5-2B-Decision-CoreAI) | `3b79912057db40be51697dfdaa433d6cb436b409` | `gpu-pipelined/qwen3_5_2b_decision_decode_int8hu_block32_sym` |
| system-one-scorer-4b | [mlboydaisuke/system-one-qwen3.5-4b-scorer-CoreAI](https://huggingface.co/mlboydaisuke/system-one-qwen3.5-4b-scorer-CoreAI) | `f27dcd3124cb3aa53e46b6707d3edb976f55c5f3` | `gpu-pipelined/system_one_qwen3_5_4b_scorer_decode_int8lin` |

## Caveats

- Latency is contended and is reference only. The GPU was not reserved for these runs. qwen3.5-2b-decision, apus-decision-v1-4b and system-one-scorer-4b ran as three concurrent serves, and other jobs overlapped some rows of openthai-systemone and qwen3.5-2b (`run.md` lists them).
- Concurrency changed latency, not answers. The solo re-check returned bit-identical probabilities: max |Δp| 0.0, argmax 30/30 for each of the three concurrent models and 5/5 for openthai-systemone. For the three concurrent models, the median solo/concurrent latency ratio was 0.43–0.52.
- Truncation: the laya-multilingual bundle reads 256 input tokens, so 95 of 111 hard rows were cut. system-one-scorer-4b follows its author's 384-token rows, which cut the state on 70 of 111 hard rows.
- qwen3.5-2b and minicpm5-2b are general chat models, asked zero-shot through the kit's JSON decision prompt.
- Public items only. JevBench's official score combines four axes and includes sealed items, so it is not comparable with these accuracies. The published rows used each entrant's own serving stack: same items, different conditions.
- The cascade chose and scored its thresholds on the same 231 items, so its accuracies are optimistic.
- The numbers are for coreai-kit `adbc755`. The later 0.7.0 release was not re-run.

## Layout

| path | content |
|---|---|
| `RESULTS.md` | the two tables and the footnotes above |
| `published-public231.json` | per-tier accuracy and p50 of 52 published systems on the same 231 items |
| `recheck30.jsonl` | the 30 JevBench public items of the solo re-check, copied verbatim |
| `verify.py`, `table.py` | recompute one model's figures from its rows; rebuild the tables |
| `run_tier.py` | runs one tier through JevBench's runner and summarizer |
| `recheck_select.py`, `recheck_compare.py` | pick the re-check items; compare solo and concurrent rows |
| `cascade/` | `cascade.py`, `summary.json` and `README.md` of the cascade analysis |
| `LICENSE-jevbench` | JevBench's MIT licence, which covers the copied items |
| `<model>/results-{easy,original,hard}.jsonl` | one row per item, as JevBench's runner wrote it |
| `<model>/summary-{easy,original,hard}.json` | JevBench's summarize output per tier |
| `<model>/manifest-{easy,original,hard}.json` | adapter, endpoint, dataset hash, UTC start and end |
| `<model>/run.md` | versions, load, probe, conformance, timings and overlaps of the run |
| `<model>/serve.log` | one line per answered request: state tokens and milliseconds |
| `<model>/probe/results-probe.jsonl` | the 3-item contract probe (decider-0.8b: `probe/results.jsonl`) |
| `<model>/recheck/` | `results-recheck.jsonl` and `compare.json` of the solo re-check (4 models) |

A result row holds the item id, family, the probability returned for each label, the predicted label, correctness, validity flags, HTTP status, latency and token usage. It holds no state or question text: `grep -lE '"(state|question|instructions|criteria|expected|labels)":' */results-*.jsonl */probe/results*.jsonl */recheck/results-recheck.jsonl` prints nothing. The item text lives in JevBench's `datasets/public/`; `recheck30.jsonl` is the only file here that copies it.

The scripts read a JevBench checkout at `~/code/jevbench`. `table.py` also reads a coreai-kit checkout and the kit's local model store for its bundle column. Edit those paths to rerun them; `verify.py` needs only a model directory.

`run.md` also names local files that are not published: raw request and response bodies, other logs, process snapshots and ledgers. In this copy, the manifests' `driver` path is relative to the dataset root, and `run.md` omits local paths and the names of unrelated processes.

## Attribution and license

The items, the harness and the published per-item outcomes come from JevBench by Florian Standhartinger and contributors, under the MIT licence (`LICENSE-jevbench`). `published-public231.json` is recomputed from JevBench's `results/v1.2/jevbench-v1.2-per-task.json` (file revision v1.3.0, at commit `2fa63fa`). Each item copied into `recheck30.jsonl` carries the licence MIT in its own provenance field.

This dataset is MIT, like JevBench. It holds results and scripts, no model weights. Each model keeps the licence on its model card; system-one-scorer-4b, for example, is CC-BY-NC-4.0.

## Links

- coreai-kit 0.7.0, the release after the measured commit: https://github.com/john-rocky/coreai-kit/releases/tag/0.7.0
- coreai-kit commit `adbc755`: https://github.com/john-rocky/coreai-kit/commit/adbc755b4fa8b5789fa86f33cb8efcf7d7deaa7d
- JevBench: https://github.com/fstandhartinger/jevbench
- Model cards, each with a section on this run: the eight repos in the table under Method.
