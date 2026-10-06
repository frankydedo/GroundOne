"""Shared helpers for the GroundOne EDA.

Part A (01–03) describes the source datasets in Project/data/raw/; part B (04) describes the dataset built by
`groundone data build` (Project/data/processed/groundone/). Each script writes figures to EDA/report/figures/ and numbers
to EDA/report/stats/<name>.json; make_report.py assembles EDA/report/eda_report.md (conclusions.md is hand-written).
Token counts use the Qwen2.5 tokenizer (same vocabulary for 0.5B and 3B). Run with the GroundOne venv.
"""
import json
import re
from pathlib import Path

import pandas as pd

from groundone.figures.style import NEUTRAL, SERIES, plt  # noqa: F401  (shared thesis style)

PROJECT = Path(__file__).resolve().parents[2]
RAW = PROJECT / "data" / "raw"
DATASET = PROJECT / "data" / "processed" / "groundone"
REPORT = PROJECT / "EDA" / "report"
FIG = REPORT / "figures"
STATS = REPORT / "stats"
FIG.mkdir(parents=True, exist_ok=True)
STATS.mkdir(parents=True, exist_ok=True)
COLORS = SERIES
TASKS = ["QA", "Summary", "Data2txt"]
CLASS_COLORS = {"supported": SERIES[0], "contradicted": SERIES[1], "not_mentioned": SERIES[6]}

_tok = None


def tokenizer():
    global _tok
    if _tok is None:
        from transformers import AutoTokenizer
        _tok = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")
    return _tok


def n_tokens(texts, batch=2048):
    tok = tokenizer()
    out = []
    texts = [t if isinstance(t, str) else str(t) for t in texts]
    for i in range(0, len(texts), batch):
        out += [len(x) for x in tok(texts[i:i + batch], add_special_tokens=False)["input_ids"]]
    return out


def norm(text):
    return re.sub(r"\s+", " ", str(text).strip().lower())


def save_fig(fig, name, caption):
    fig.tight_layout()
    fig.savefig(FIG / f"{name}.png", bbox_inches="tight")
    plt.close(fig)
    return {"file": f"figures/{name}.png", "caption": caption}


def _clean(o):
    if isinstance(o, dict):
        return {(" | ".join(map(str, k)) if isinstance(k, tuple) else str(k)): _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    return o


def save_stats(name, obj):
    (STATS / f"{name}.json").write_text(json.dumps(_clean(obj), indent=2, default=str))


def describe(values):
    s = pd.Series(values)
    return {k: round(float(v), 1) for k, v in s.describe(percentiles=[.5, .9, .99]).items()}


def load_split(name):
    return [json.loads(l) for l in open(DATASET / f"{name}.jsonl")]
