Source: https://huggingface.co/alrobles/sciev (revision c47ddebf92cb9550e976dca9c927b5f3f2528a06) — retrieved 2026-10-10

---
license: apache-2.0
tags:
- decision-models
- masked-diffusion
- scientific-ml
- calibration
---

# Sciev — Open System-One Scientific Decision Models

Typed decision heads on a frozen **LLaDA-8B-Instruct** masked-diffusion
backbone. Unstructured `state` + typed questions (`choice` / `noul` /
`score`) → structured decisions with probabilities in **one forward pass
per decision**. No text generation, no output parsing.

- Code: <https://github.com/alrobles/sciev> (`pip install sciev`)
- Site: <https://sciev.org>
- Manuscript: <https://sciev.org/static/sciev-paper.pdf> (in preparation
  for arXiv submission)
- Release: <https://github.com/alrobles/sciev/releases/tag/v0.2.3>

## Contents

| file | role | sha256 (prefix) |
|---|---|---|
| `release/fr_choice.pt` | frozen `choice` head — AttnPoolHead, 67.2M | `67efbc59` |
| `release/fr_noul.pt` | frozen `noul` head — MLP, 16.8M | `317bfa5d` |
| `release/fr_score.pt` | frozen `score` head — MLP + ordinal aux loss, 16.8M | `28dea8d4` |
| `experimental/da_*.pt` | experimental adapted-arm heads (see caveats) | see `evidence.json` |
| `evidence.json` | compact ledger of the 60-report matched study | `8d86aadd` |

Weights are byte-identical to the GitHub v0.2.2/v0.2.3 release assets.
The backbone (`GSAI-ML/LLaDA-8B-Instruct`) is downloaded separately and
keeps its own license.

## Usage

```python
from huggingface_hub import hf_hub_download
ckpt = hf_hub_download("alrobles/sciev", "release/fr_choice.pt")
```

```bash
python -m sciev.eval \
    --ckpt "$ckpt" --decision-type choice \
    --r2-mode spanpool --r2-layers=-1,-9,-17,-25 --canonical-order \
    --r2-temp-fit-decisions decisions_dev.jsonl \
    --decisions-eval decisions_eval.jsonl \
    --device cuda --out eval.json
```

## Key results (matched study, `systemone-v2`, 3 head seeds)

| eval | fr (release) | da (experimental) |
|---|---:|---:|
| sci battery choice, n=448 | 0.970 ± 0.017 | 0.961 ± 0.011 |
| sci battery noul, n=1200 | 0.925 ± 0.006 | 0.913 ± 0.007 |
| sci battery score, n=1218 | 0.859 ± 0.075 | 0.779 ± 0.109 |
| GPQA main, n=441 | 0.295 ± 0.014 | 0.288 ± 0.018 |
| SciFact noul, n=332 | 0.483 ± 0.023 | **0.709 ± 0.020** |

## Scope and caveats

- Internal battery uses constructed distractors and synthetic score
  labels; high accuracy is not a measure of general scientific
  correctness. With the passage removed the frozen choice head still
  agrees with the reference on **87.5%** of items — see the evidence
  controls in `evidence.json` and the paper.
- The `da_*` heads pair the same recipe with **one** archival LoRA
  adapter whose loss is not the native per-token LLaDA estimator;
  results are task-dependent observations, not a causal DAPT estimate.
- External evaluations informed candidate selection — they are
  exploratory estimates, not an untouched final test.
- Calibration temperatures must be fitted on held-out dev data for your
  distribution; confidence is not a correctness guarantee.

## License

Apache-2.0 for code and head weights. Backbone and source datasets keep
their own licenses.
