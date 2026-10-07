"""Calibration for readout design (b) (plan D23, docs/dataset_plan.md §8).

1. Score the dev set (answer-level records) and keep the raw A/B/C logits at every marker.
2. Fit, by minimising dev NLL, (i) a temperature and (ii) a temperature + per-class bias (affine).
3. Save calibration.json next to the adapter (key "three"; the affine map is the one used).
4. Re-apply both maps to the saved test predictions (log-probabilities are logits up to a constant, which neither map
   changes), so no test set is scored again. T2 is reported uncalibrated if its predictions hold only P(supported).
5. Report, before and after: three-way macro recall and accuracy, top-label ECE, NLL, Brier; binary P(supported)
   balanced accuracy, AUROC, ECE, Brier; risk-coverage (AURC) of the binary decision. Figures: reliability diagrams and
   risk-coverage curves in figures/calibration-<run>/.
Usage: groundone calibrate-b --adapter RUN [--name RESULTS_NAME]
"""
import argparse
import json

import numpy as np
import pandas as pd

from ..calibration import Calibration, fit_affine, fit_temperature
from ..config import RESULTS_DIR
from ..data.build import OUT
from .metrics import binary, ece

CLASSES = ("supported", "contradicted", "not_mentioned")


def apply(logits, t, bias):
    z = np.asarray(logits, float) / t + np.asarray(bias, float)
    z -= z.max(1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(1, keepdims=True)


def three_metrics(P, y):
    pred = P.argmax(1)
    rec = [float((pred[y == k] == k).mean()) for k in range(3) if (y == k).any()]
    onehot = np.eye(3)[y]
    return {"macro_recall": float(np.mean(rec)), "accuracy": float((pred == y).mean()),
            "ece_top_label": ece((pred == y).astype(float), P.max(1)),
            "nll": float(-np.mean(np.log(np.clip(P[np.arange(len(y)), y], 1e-9, 1)))),
            "brier": float(np.mean(((P - onehot) ** 2).sum(1))),
            "predicted_share": [round(float((pred == k).mean()), 4) for k in range(3)]}


def risk_coverage(y_bin, p_sup):
    """Selective prediction for the binary decision: sort by confidence max(p, 1-p), accuracy of the kept fraction."""
    conf = np.maximum(p_sup, 1 - p_sup)
    correct = ((p_sup >= 0.5).astype(int) == y_bin).astype(float)
    order = np.argsort(-conf)
    risk = 1 - np.cumsum(correct[order]) / np.arange(1, len(order) + 1)
    cov = np.arange(1, len(order) + 1) / len(order)
    return cov, risk, float(risk.mean())


def evaluate_split(L, y, maps):
    out = {}
    for name, (t, b) in maps.items():
        P = apply(L, t, b)
        ys = (y == 0).astype(int)
        _, _, aurc = risk_coverage(ys, P[:, 0])
        out[name] = {"three_way": three_metrics(P, y), "binary": binary(ys, P[:, 0]), "aurc": aurc}
    return out


def main(argv=None):
    from ..config import resolve_model
    from ..engine import Engine
    from ..figures.style import INK2, NEUTRAL, SERIES, Group, plt
    from .tests import score_b
    ap = argparse.ArgumentParser(prog="groundone calibrate-b")
    ap.add_argument("--size")
    ap.add_argument("--adapter", required=True)
    ap.add_argument("--name", help="results/<name>/ holding t1, t2, t3 predictions (default: run name)")
    a = ap.parse_args(argv)
    run = a.name or a.adapter.split("/")[0]
    engine = Engine.load(a.size, a.adapter)
    dev = [json.loads(l) for l in open(OUT / "dev.jsonl")]
    L = np.array(score_b(engine, dev, raw=True))
    y = np.array([CLASSES.index(l) for r in dev for l in r["labels"] if l is not None])
    rows = [(list(map(float, l)), int(g)) for l, g in zip(L, y)]
    t_only = fit_temperature(rows)
    t_aff, b_aff = fit_affine(rows)
    maps = {"raw": (1.0, [0.0, 0.0, 0.0]), "temperature": (t_only, [0.0, 0.0, 0.0]), "affine": (t_aff, b_aff)}
    adir = __import__("pathlib").Path(resolve_model(a.size, a.adapter)[1])
    Calibration({"three": t_aff}, engine.backend.metadata["fingerprint"],
                {"fitted_on": "dev (answer-level, design b)", "design": "b", "temperature_only": t_only},
                {"three": b_aff}).save(adir / "calibration.json")
    report = {"maps": {k: {"temperature": round(t, 4), "bias": [round(x, 4) for x in b]} for k, (t, b) in maps.items()},
              "dev": evaluate_split(L, y, maps)}
    curves = {"dev": (L, y)}
    for suite in ("t1", "t3"):
        p = RESULTS_DIR / run / suite / "predictions.parquet"
        if p.exists():
            df = pd.read_parquet(p)
            Lt = np.log(np.clip(np.array(df["p"].tolist()), 1e-12, 1))
            yt = np.array([CLASSES.index(c) for c in df["cls"]])
            report[suite] = evaluate_split(Lt, yt, maps)
            curves[suite] = (Lt, yt)
    p2 = RESULTS_DIR / run / "t2" / "metrics.json"
    if p2.exists():
        report["t2_uncalibrated_pooled"] = json.loads(p2.read_text())["pooled"]
    out = RESULTS_DIR / run / "calibration"
    out.mkdir(parents=True, exist_ok=True)
    (out / "metrics.json").write_text(json.dumps(report, indent=2, default=float))

    g = Group(f"calibration-{run}")
    labels = {"dev": "dev", "t1": "T1 RAGTruth", "t3": "T3 VitaminC"}
    fig, axes = plt.subplots(1, len(curves), figsize=(4 * len(curves), 3.6), sharey=True)
    edges = np.linspace(0, 1, 11)
    for ax, (split, (Ls, ys)) in zip(np.atleast_1d(axes), curves.items()):
        ax.plot([0, 1], [0, 1], color=NEUTRAL, ls="--", lw=1)
        for k, (name, col) in enumerate((("raw", SERIES[1]), ("affine", SERIES[0]))):
            P = apply(Ls, *maps[name])[:, 0]
            yb = (ys == 0).astype(float)
            xs, fs = [], []
            for lo, hi in zip(edges[:-1], edges[1:]):
                m = (P >= lo) & ((P < hi) if hi < 1 else (P <= hi))
                if m.sum() >= 20:
                    xs.append(P[m].mean())
                    fs.append(yb[m].mean())
            ax.plot(xs, fs, marker="o", color=col, label=f"{name} (ECE {ece(yb, P):.3f})")
        ax.set_title(labels[split])
        ax.set_xlabel("predicted P(supported)")
        ax.legend(fontsize=7, loc="upper left")
    np.atleast_1d(axes)[0].set_ylabel("observed share supported")
    g.save(fig, "reliability_binary", f"Reliability of P(supported) before (raw) and after temperature + bias calibration "
           f"fitted on dev (run {run}); bins with at least 20 sentences.", f"results/{run}/calibration/metrics.json")
    fig, ax = plt.subplots(figsize=(6, 3.4))
    for k, (split, (Ls, ys)) in enumerate(curves.items()):
        cov, risk, aurc = risk_coverage((ys == 0).astype(int), apply(Ls, *maps["affine"])[:, 0])
        ax.plot(cov, risk, color=SERIES[[0, 2, 6][k]], label=f"{labels[split]} (AURC {aurc:.3f})")
    ax.set_xlabel("coverage (share of sentences decided, most confident first)")
    ax.set_ylabel("error rate of the binary decision")
    ax.legend(fontsize=7)
    g.save(fig, "risk_coverage", f"Selective prediction: error rate of the supported / unsupported decision as the least "
           f"confident sentences are deferred (calibrated probabilities, run {run}).", f"results/{run}/calibration/metrics.json")
    g.write_index(f"Calibration: {run}")
    short = {s: {m: {"macro": round(v[m]["three_way"]["macro_recall"], 4), "ece_bin": round(v[m]["binary"]["ece15"], 4),
                     "ece_top": round(v[m]["three_way"]["ece_top_label"], 4), "nll": round(v[m]["three_way"]["nll"], 4)}
                 for m in maps} for s, v in report.items() if s in ("dev", "t1", "t3")}
    print(json.dumps({"maps": report["maps"], "summary": short}, indent=1))


if __name__ == "__main__":
    main()
