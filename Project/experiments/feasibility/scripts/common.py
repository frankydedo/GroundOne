"""Shared helpers for the Phase 0 feasibility scripts."""
import json
import os
import re
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESULTS = ROOT / "results"
SEED = 1234

MODELS = {
    "qwen0.5b": "lmstudio-community/Qwen2.5-0.5B-Instruct-MLX-8bit",
    "qwen3b": "lmstudio-community/Qwen2.5-3B-Instruct-MLX-8bit",
    "qwen7b": "mlx-community/Qwen2.5-7B-Instruct-8bit",
}

SYSTEM = (
    "You are a faithfulness verifier. Decide whether the CLAIM is fully supported by the DOCUMENT. "
    "Reply with one letter: A = supported, B = not supported."
)


def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=2, default=str)


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


_SENT_RE = re.compile(r"[^.!?\n]+(?:[.!?]+|$)", re.M)


def split_sentences(text):
    """Return (start, end, sentence) with character offsets. Simple rule-based splitter."""
    out = []
    for m in _SENT_RE.finditer(text):
        s = m.group(0)
        if len(s.strip()) < 3:
            continue
        lead = len(s) - len(s.lstrip())
        start = m.start() + lead
        end = m.end() - (len(s) - len(s.rstrip()))
        out.append((start, end, text[start:end]))
    return out


def balanced_accuracy(y, p, thr=0.5):
    import numpy as np
    y = np.asarray(y).astype(int)
    pred = (np.asarray(p) >= thr).astype(int)
    tpr = ((pred == 1) & (y == 1)).sum() / max((y == 1).sum(), 1)
    tnr = ((pred == 0) & (y == 0)).sum() / max((y == 0).sum(), 1)
    return float((tpr + tnr) / 2)


def ece(y, p, bins=15):
    """ECE of the positive-class probability (binary reliability)."""
    import numpy as np
    y = np.asarray(y).astype(float)
    p = np.asarray(p).astype(float)
    edges = np.linspace(0, 1, bins + 1)
    total = 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (p >= lo) & (p < hi) if hi < 1 else (p >= lo) & (p <= hi)
        if m.sum():
            total += m.sum() / len(p) * abs(p[m].mean() - y[m].mean())
    return float(total)


def metrics(y, p):
    import numpy as np
    from sklearn.metrics import roc_auc_score, brier_score_loss
    y = np.asarray(y).astype(int)
    p = np.clip(np.asarray(p, dtype=float), 1e-6, 1 - 1e-6)
    out = {"n": int(len(y)), "pos_rate": float(y.mean()), "bacc@0.5": balanced_accuracy(y, p)}
    try:
        out["auroc"] = float(roc_auc_score(y, p))
    except ValueError:
        out["auroc"] = None
    out["ece15"] = ece(y, p)
    out["brier"] = float(brier_score_loss(y, p))
    out["nll"] = float(-(y * np.log(p) + (1 - y) * np.log(1 - p)).mean())
    return out
