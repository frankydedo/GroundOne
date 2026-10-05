"""Shared helpers for the GroundOne EDA (Phase 1a).

Every analysis script loads raw data from Project/data/raw/, writes figures to EDA/report/figures/ and
numbers to EDA/report/stats/<name>.json. make_report.py assembles everything into EDA/report/eda_report.md.
Token counts use the Qwen2.5 tokenizer (same vocabulary for 0.5B and 3B).
"""
import json
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

PROJECT = Path(__file__).resolve().parents[2]
RAW = PROJECT / "data" / "raw"
REPORT = PROJECT / "EDA" / "report"
FIG = REPORT / "figures"
STATS = REPORT / "stats"
FIG.mkdir(parents=True, exist_ok=True)
STATS.mkdir(parents=True, exist_ok=True)

# The experiments the data must serve (see implementation_plan.md §2, §6.5, §7).
EXPERIMENTS = {
    "X1": "Binary groundedness: training data (specialisation, RQ1)",
    "X2": "Binary groundedness: evaluation comparable with published results (RQ1, RQ5 plain task)",
    "X3": "K decisions over one shared context: latency and parallel scoring (RQ2)",
    "X4": "Three-way question: supported / contradicted / not mentioned (RQ5)",
    "X5": "Rules in the prompt: strict vs lenient definition of an error (RQ5)",
    "X6": "Calibration: dev split for temperature, test split for ECE / selective prediction (RQ3)",
    "X7": "Demo realism: RAG answers to user questions over retrieved passages",
}

COLORS = ["#2b6cb0", "#c05621", "#2f855a", "#9b2c2c", "#6b46c1", "#b7791f", "#4a5568", "#00838f"]
plt.rcParams.update({"figure.dpi": 130, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.alpha": 0.25, "font.size": 9})

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


_SENT_RE = re.compile(r"[^.!?\n]+(?:[.!?]+|$)", re.M)


def split_sentences(text):
    """Rule-based splitter used in Phase 0 (kept identical so EDA numbers match the experiments)."""
    out = []
    for m in _SENT_RE.finditer(text):
        s = m.group(0)
        if len(s.strip()) < 3:
            continue
        start = m.start() + (len(s) - len(s.lstrip()))
        end = m.end() - (len(s) - len(s.rstrip()))
        out.append((start, end, text[start:end]))
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
