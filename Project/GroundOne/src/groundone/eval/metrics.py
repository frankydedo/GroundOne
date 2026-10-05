"""Evaluation metrics (plan §8): balanced accuracy at a fixed threshold, AUROC, calibration (ECE, Brier, NLL)."""
import numpy as np


def bacc(y, p, thr=0.5):
    y = np.asarray(y).astype(int)
    pred = (np.asarray(p) >= thr).astype(int)
    pos, neg = y == 1, y == 0
    tpr = (pred[pos] == 1).mean() if pos.any() else np.nan
    tnr = (pred[neg] == 0).mean() if neg.any() else np.nan
    return float(np.nanmean([tpr, tnr]))


def ece(y, p, bins=15):
    y, p = np.asarray(y, float), np.asarray(p, float)
    edges = np.linspace(0, 1, bins + 1)
    tot = 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (p >= lo) & ((p < hi) if hi < 1 else (p <= hi))
        if m.any():
            tot += m.mean() * abs(p[m].mean() - y[m].mean())
    return float(tot)


def binary(y, p, thr=0.5):
    from sklearn.metrics import roc_auc_score
    y = np.asarray(y).astype(int)
    p = np.clip(np.asarray(p, float), 1e-7, 1 - 1e-7)
    out = {"n": int(len(y)), "pos_rate": round(float(y.mean()), 4), "bacc": bacc(y, p, thr)}
    out["auroc"] = float(roc_auc_score(y, p)) if 0 < y.sum() < len(y) else None
    out["ece15"] = ece(y, p)
    out["brier"] = float(np.mean((p - y) ** 2))
    out["nll"] = float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))
    return out


def multiclass(y, probs, names):
    """y: gold class indices; probs: (n, k). Macro recall (= balanced accuracy), accuracy, per-class recall, ECE of max prob."""
    y = np.asarray(y)
    probs = np.asarray(probs, float)
    pred = probs.argmax(1)
    rec = {names[k]: float((pred[y == k] == k).mean()) for k in range(len(names)) if (y == k).any()}
    conf = probs.max(1)
    return {"n": int(len(y)), "macro_recall": float(np.mean(list(rec.values()))), "accuracy": float((pred == y).mean()),
            "recall": rec, "ece15_maxprob": ece((pred == y).astype(float), conf),
            "nll": float(-np.mean(np.log(np.clip(probs[np.arange(len(y)), y], 1e-7, 1))))}
