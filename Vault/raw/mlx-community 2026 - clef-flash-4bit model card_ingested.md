Source: https://huggingface.co/mlx-community/clef-flash-4bit (revision b5adbe2c3a95200d4bf04a0727c8ec457157d5e1) — retrieved 2026-10-10

---
license: apache-2.0
library_name: mlx
base_model: Cloudflare/clef-flash
base_model_relation: quantized
pipeline_tag: zero-shot-classification
tags:
- mlx
- clef
- cloudflare
- systemone
- structured-output
- classification
- multimodal
- custom-code
- decision-model
---

# mlx-community/clef-flash-4bit

[Cloudflare/clef-flash](https://huggingface.co/Cloudflare/clef-flash) converted to MLX (4-bit) for Apple Silicon.

Clef turns a state (text, JSON, images, or video) plus a schema of typed questions into a
probability for every allowed option, in a single forward pass. **It is not a chat model** —
`mlx_vlm.generate`, `mlx_lm.generate`, and LM Studio will load the backbone but produce
meaningless text. Use the bundled `clef_mlx.py` loader, which runs the backbone and the
joint schema head.

## Which variant fits your Mac?

| Variant | Base | Download | Peak memory (1k / 4k / 16k tokens) | Latency (1k / 16k tokens) | Minimum Mac RAM |
|---|---|---|---|---|---|
| **clef-flash-4bit (this repo)** | 9B | 6.2 GB | 7.0 / 7.2 / 8.6 GB | 0.31 s / 7.0 s | 16 GB |
| [clef-flash-8bit](https://huggingface.co/mlx-community/clef-flash-8bit) | 9B | 10.7 GB | 11.4 / 11.6 / 13.0 GB | 0.34 s / 7.7 s | 24 GB (16 GB for short prompts) |
| [clef-4bit](https://huggingface.co/mlx-community/clef-4bit) | 27B | 16.3 GB | 17.1 / 17.5 / 19.6 GB | 1.4 s / 26.0 s | 32 GB |
| [clef-8bit](https://huggingface.co/mlx-community/clef-8bit) | 27B | 29.8 GB | 30.5 / 30.8 / 33.0 GB | 1.5 s / 32.0 s | 48 GB |

Measured on an M5 Max with text input. macOS lets the GPU use only about 70–75% of RAM by default, so the minimum RAM is higher than the peak. The 9B variants are much faster; the 27B variants score higher (see the quality check below).

## Usage

```bash
pip install "mlx-vlm>=0.7.4,<0.8" huggingface_hub   # no torch needed
```

Tested with mlx 0.32.3, mlx-lm 0.32.0 and mlx-vlm 0.7.4. `clef_mlx.py` uses mlx-vlm internals, so it
warns if you load it with an untested mlx-vlm minor version.

```python
import sys
from huggingface_hub import snapshot_download

path = snapshot_download("mlx-community/clef-flash-4bit")
sys.path.insert(0, path)
import clef_mlx

model = clef_mlx.load(path)
response = model.systemone({
    "model": "clef-flash",
    "state": "Our checkout started returning errors and orders are blocked.",
    "questions": {
        "department": {
            "type": "choice",
            "instructions": "Which team should handle the message?",
            "criteria": {"billing": "Payments or invoices", "technical": "Bugs or outages"},
        },
        "urgency": {"type": "score", "criteria": ["Can wait", "This week", "Today"]},
        "outage": {"type": "noul", "instructions": "Is a service down?"},
    },
})
print(response["answers"])
```

Images (PIL) and videos (frame arrays) go in `images` / `videos`, as in the original:

```python
from PIL import Image
model.predict({
    "state": {"task": "Review the attached receipt."},
    "images": [Image.open("receipt.jpg")],
    "questions": {"legible": {"type": "noul", "instructions": "Is the receipt total legible?"}},
})
```

See the [original model card](https://huggingface.co/Cloudflare/clef-flash) for the input format, question types, and benchmarks.

## Try it from the command line

`clef_mlx.py` runs on its own. From the downloaded repo it uses that repo by default; elsewhere pass
`--model mlx-community/clef-flash-4bit`.

```bash
cd "$(hf download mlx-community/clef-flash-4bit --quiet)"
python clef_mlx.py predict \
  --state "Checkout has been failing for every customer for the last hour." \
  --questions '{"urgent": {"type": "noul", "instructions": "Is this urgent?"},
               "team": {"type": "choice", "criteria": {"billing": "Payments", "technical": "Outages and errors"}}}'
```

`--questions` takes JSON, a `.json` file, or `-` for stdin; `--request` takes a whole request body instead;
`--image photo.jpg` attaches an image (repeatable). The output is the SystemOne response as JSON.

## Run a local SystemOne server

```bash
python clef_mlx.py serve --port 8000          # http://127.0.0.1:8000, local only by default
curl http://127.0.0.1:8000/v1/systemone -H "Content-Type: application/json" -d '{
  "model": "clef-flash",
  "state": "Checkout has been failing for every customer for the last hour.",
  "questions": {"urgent": {"type": "noul", "instructions": "Is this urgent?"}}
}'
```

- `POST /v1/systemone` takes the same request body as the Jev/SystemOne API and returns the same response
  (plus `usage.latency_ms`), so existing SystemOne clients can point at your laptop. `GET /health` and
  `GET /v1/models` are also available.
- Images go in `images` as data URLs, base64, or http(s) URLs. Videos aren't supported over HTTP.
- Errors return JSON: `400` for invalid requests, `413` with "maximum context length" for inputs that don't fit.
  Add `"truncate": false` to a request (or start with `--no-truncate`) to get the `413` instead of truncation.
- Requests run one at a time on the GPU. There is no authentication: keep the default `127.0.0.1` binding
  unless you put your own proxy in front.
- For the [Decision Index](https://github.com/apolinario/decision-index), start with `--no-truncate` and use
  its `http` engine: `python -m decision_index run --engine http --option base_url=http://127.0.0.1:8000`.

## Limitations

- **Not a chat model.** Text generation tools (`mlx_lm.generate`, `mlx_vlm.generate`, LM Studio, Ollama) load
  the backbone but give meaningless output. Only `clef_mlx.py` runs the decision head.
- **Long inputs are truncated by default**, exactly like the reference implementation: the state is cut so
  the whole prompt fits in 16,384 tokens. Pass `truncate=False` to `predict()`/`systemone()` to get a
  `clef_mlx.ContextTooLong` error instead, or raise `max_length` (the head was trained at 16k).
- **One record per call.** There is no batching; requests run one after another.
- **Images or videos, not both in one record.** Several images, or several videos, are fine.
- **Speed depends heavily on the chip.** Latencies above are from an M5 Max; long prompts on base
  M-series chips will be several times slower.
- **Custom code.** Like the original release, this repo ships Python (`clef_mlx.py`) that you import and run.
  Read it before use if that matters in your environment.

## Conversion

- Backbone: `mlx_vlm.convert -q --q-bits 4 --q-group-size 64` (vision tower kept in bf16).
- Joint schema head: `joint_head.safetensors` copied unchanged (bf16) and run by `clef_mlx.py`.
- `processor_config.json` is the original from Cloudflare/clef-flash; prompt/token layout matches the reference
  `joint_schema_model.py` exactly (images and video).

## Parity vs. official PyTorch implementation (bf16)

| Inputs | Top answer agrees | Max abs Δprob |
|---|---|---|
| Text (4 records, 10 questions) | 10/10 | 0.029 |
| Images + video (5 records, 9 questions) | 9/9 | 0.119 |

Measured on an M5 Max (128 GB). Small spot-check, not a full benchmark run.

## Quality check: Decision Index (sampled)

| | Decision Index (sample) | Same top answer as bf16 | Mean max abs Δp | Median latency |
|---|---|---|---|---|
| **This model (4-bit)** | **54.65** | 96.4% (15,915 answers) | 0.040 | 311 ms |
| MLX bf16, same rows | 55.63 | — | — | 339 ms |
| Cloudflare published (full suite) | 57.07 | | | |

4-bit costs about **1 index point** vs bf16 on identical rows. Most of the remaining gap to the published score is
already present in bf16 (sample noise and harness differences), not quantization. Agreement is lowest on
low-chance many-option tasks (POP909, GPQA, CLINC150).

Method: [Decision Index](https://github.com/apolinario/decision-index) 0.2.1 kit (suite rebuilt byte-identical), stratified
2,000-request sample across all 44 benchmarks (`suite sample --n 2000`), engine = `clef_mlx.py` with
`max_length=16384` and **no truncation** (over-length requests are refused and count as wrong; 15 of 2,000,
mostly BRIGHT). The index is computed from each benchmark's native metric on the sampled rows with the kit's
chance correction and weights; HLE and iSarcasmEval are set to 0 to match how Cloudflare's published run is
scored. With ~40 rows per benchmark, per-benchmark numbers are noisy (±10+ pts) — only the index is meaningful.

## License

Apache-2.0, following [Cloudflare/clef-flash](https://huggingface.co/Cloudflare/clef-flash).

