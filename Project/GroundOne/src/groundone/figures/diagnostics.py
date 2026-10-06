"""Diagnostic figures for a trained run: format effect, sentence position / K, probability spread, three-way confusion.

Usage: groundone figures diagnostics g1-05b-v1   (needs results/<run>/{ragtruth,aggrefact,anli}/predictions.parquet)
"""
import json

import numpy as np
import pandas as pd

from ..config import DATA_PROCESSED, RESULTS_DIR
from ..eval.metrics import binary
from ..text import norm
from .style import INK2, NEUTRAL, SERIES, Group, bar_labels, plt


def load(name):
    return {x["id"]: x for x in (json.loads(l) for l in open(DATA_PROCESSED / "v1" / f"{name}.jsonl"))}


def main(run):
    g = Group(f"diagnostics-{run}")
    rt, ag = load("test_ragtruth"), load("test_aggrefact")
    P = pd.read_parquet(RESULTS_DIR / run / "ragtruth" / "predictions.parquet")
    P["p"] = P.probs.map(lambda v: v[0])
    S = P[P.qtype == "sup"].copy()
    S["claim"] = S.id.map(lambda i: norm(rt[i]["sentences"][rt[i]["idx"]]))
    S["pos"] = S.id.map(lambda i: rt[i]["idx"])
    S["K"] = S.id.map(lambda i: len(rt[i]["sentences"]))
    S["y"] = (S.cls == "supported").astype(int)

    # 1. same sentences, two formats
    A = pd.read_parquet(RESULTS_DIR / run / "aggrefact" / "predictions.parquet")
    A = A[A.dataset == "RAGTruth"].copy()
    A["claim"] = A.id.map(lambda i: norm(ag[i]["sentences"][0]))
    M = S.merge(A[["claim", "p_supported", "label"]].drop_duplicates("claim"), on="claim")
    fig, ax = plt.subplots(figsize=(5, 3.2))
    vals = [binary(M.label, M.p_supported)["bacc"], binary(M.label, M.p)["bacc"]]
    bars = ax.bar(["document + one sentence\n(pair format)", "document + whole answer,\nquestion on sentence i"], vals,
                  0.5, color=[SERIES[0], SERIES[1]])
    bar_labels(ax, bars, "{:.3f}")
    ax.set_ylim(0.45, 0.8)
    ax.axhline(0.5, color=NEUTRAL, lw=1, ls="--")
    ax.set_ylabel("balanced accuracy (supported?)")
    g.save(fig, "format_effect_same_sentences", f"The same {len(M):,} RAGTruth test sentences scored in the two prompt "
           f"formats (LLM-AggreFact labels), run {run}. The multi-sentence System One format loses accuracy.",
           f"results/{run}/ragtruth, results/{run}/aggrefact")

    # 2. by position and by K
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.2), sharey=True)
    for ax, col, bins, lab in [(axes[0], "pos", [(0, 0), (1, 2), (3, 5), (6, 99)], "sentence position (0 = first)"),
                               (axes[1], "K", [(1, 4), (5, 8), (9, 13), (14, 99)], "sentences in the answer (K)")]:
        names, vals, ns = [], [], []
        for lo, hi in bins:
            d = S[(S[col] >= lo) & (S[col] <= hi)]
            names.append(f"{lo}" if lo == hi else (f"{lo}–{hi}" if hi < 99 else f"≥{lo}"))
            vals.append(binary(d.y, d.p)["bacc"])
            ns.append(len(d))
        bars = ax.bar(names, vals, 0.6, color=SERIES[1])
        bar_labels(ax, bars, "{:.2f}")
        ax.axhline(0.5, color=NEUTRAL, lw=1, ls="--")
        ax.set_xlabel(lab)
    axes[0].set_ylabel("balanced accuracy (supported?)")
    axes[0].set_ylim(0.4, 0.75)
    g.save(fig, "accuracy_by_position_and_K", f"RAGTruth test, multi-sentence format: accuracy falls for long answers "
           f"(K ≥ 14 is below chance) and for late sentences (run {run}).", f"results/{run}/ragtruth")

    # 3. probability spread per task
    fig, ax = plt.subplots(figsize=(7, 3.2))
    for i, t in enumerate(["QA", "Summary", "Data2txt"]):
        d = S[S.task == t]
        ax.hist(d.p, bins=60, range=(0.35, 0.65), alpha=0.6, color=SERIES[i], label=f"{t} (mean {d.p.mean():.3f}, sd {d.p.std():.3f})")
    ax.axvline(0.5, color=INK2, lw=1, ls="--")
    ax.set_xlabel("P(supported) after temperature scaling")
    ax.set_ylabel("sentences")
    ax.legend(fontsize=7)
    g.save(fig, "probability_spread_by_task", f"In the multi-sentence format the probabilities are squeezed around 0.5 "
           f"(sd ≈ 0.02–0.03) and shifted per task, so a fixed threshold of 0.5 flips on a tiny bias (run {run}).",
           f"results/{run}/ragtruth")

    # 4. question behaviour: share of each predicted answer
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.2))
    for ax, src, title in [(axes[0], P, "RAGTruth test"),
                           (axes[1], pd.read_parquet(RESULTS_DIR / run / "anli" / "predictions.parquet"), "ANLI test")]:
        rows = []
        for q in ("sup", "strict", "lenient", "three"):
            d = src[src.qtype == q]
            if len(d):
                pr = np.array(d.probs.tolist())
                share = np.bincount(pr.argmax(1), minlength=pr.shape[1]) / len(pr)
                rows.append((q, share))
        bottom = np.zeros(len(rows))
        for k, lab in enumerate(["A (supported / acceptable)", "B (not supported / contradicted / error)", "C (not mentioned)"]):
            v = np.array([s[k] if k < len(s) else 0 for _, s in rows])
            ax.bar([q for q, _ in rows], v, 0.6, bottom=bottom, color=SERIES[k], label=lab)
            bottom += v
        ax.set_title(title)
        ax.set_ylabel("share of predicted answers")
    axes[0].legend(fontsize=7, loc="lower left")
    g.save(fig, "predicted_answer_shares", f"Share of each predicted answer per question (run {run}). The lenient rule "
           f"almost always answers 'acceptable' and the three-way question almost never answers 'not mentioned': these "
           f"questions were not learned.", f"results/{run}/ragtruth, results/{run}/anli")
    g.write_index(f"Diagnostics: {run}")
