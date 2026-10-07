"""Benchmark figures on the frozen test sets: system comparison on T1 and T3, per task, and latency as a function of K.

Reads results/<name>/{t1,t3}/metrics.json (GroundOne, untrained readout, encoders, Rizzo-Flow) and
results/<name>/latency/metrics.json (judges and System One timings). Missing results are skipped, so the figures can be
regenerated as runs complete. Usage: groundone figures benchmarks
"""
import json

import numpy as np

from ..config import PROJECT, RESULTS_DIR
from .style import NEUTRAL, SERIES, SYSTEM_COLORS, Group, bar_labels, plt

SYSTEMS = [  # (label, results name, kind)
    ("Word overlap", None, "overlap"),
    ("HHEM", "hhem-frozen", "binary"),
    ("MiniCheck-RoBERTa", "minicheck-roberta-frozen", "binary"),
    ("Rizzo-Flow 4B", "rizzo-flow-4b-q4-frozen", "three"),
    ("Untrained 0.5B", "base-05b-a", "three"),
    ("Untrained 3B", "base-3b-a", "three"),
    ("GroundOne 0.5B", "g1-05b-b1", "three"),
    ("GroundOne 3B", "g1-3b-b1", "three"),
]
COLORS = {**SYSTEM_COLORS, "Word overlap": "#c4c2bb", "Sentence only": "#8a877f"}
LATENCY = {  # size -> [(label, results name)]
    "0.5B": [("GroundOne (design b)", "lat-g1-05b-b1"), ("System One (design a)", "lat-readout-a-05b"),
             ("Terse judge", "judge-terse-05b"), ("Verbose judge", "judge-verbose-05b")],
    "3B": [("GroundOne (design b)", "lat-g1-3b-b1"), ("System One (design a)", "lat-readout-a-3b"),
           ("Terse judge", "judge-terse-3b"), ("Verbose judge", "judge-verbose-3b")],
}
LAT_COLORS = {"GroundOne (design b)": SERIES[0], "System One (design a)": SERIES[4], "Terse judge": SERIES[7],
              "Verbose judge": SERIES[5]}
BANDS = ["1-4", "5-8", "9-13", ">=14"]


def load(name, suite):
    p = RESULTS_DIR / name / suite / "metrics.json"
    return json.loads(p.read_text()) if p.exists() else None


def binary_block(m):
    return m.get("binary") or m["all"]["binary"]


def comparison(g, suite, title):
    rows = []
    ref = load("g1-05b-b1", suite)
    for label, name, kind in SYSTEMS:
        if kind == "overlap":
            if ref:
                rows.append((label, None, ref["baseline_word_overlap_auroc"], None))
            continue
        m = load(name, suite)
        if not m:
            continue
        b = binary_block(m)
        rows.append((label, b["bacc"], b["auroc"], m["all"]["macro_recall"] if kind == "three" else None))
    if len(rows) < 2:
        return
    shortcut = json.loads((PROJECT / "data/processed/groundone/shortcut_report.json").read_text())
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.6))
    names = [r[0] for r in rows]
    y = np.arange(len(rows))
    au = axes[0].barh(y, [r[2] for r in rows], color=[COLORS.get(n, NEUTRAL) for n in names])
    for b, r in zip(au, rows):
        axes[0].text(b.get_width(), b.get_y() + b.get_height() / 2, f" {r[2]:.3f}", va="center", fontsize=7)
    axes[0].set_yticks(y, names)
    axes[0].set_xlim(0.5, 1.0)
    axes[0].set_xlabel("AUROC, supported vs not supported")
    three = [(r[0], r[3]) for r in rows if r[3] is not None]
    key = {"t1": "test_ragtruth", "t3": "test_vitaminc"}[suite]
    three = [("Sentence only", shortcut[key])] + three
    y2 = np.arange(len(three))
    bars = axes[1].barh(y2, [v for _, v in three], color=[COLORS.get(n, NEUTRAL) for n, _ in three])
    for b, (_, v) in zip(bars, three):
        axes[1].text(b.get_width(), b.get_y() + b.get_height() / 2, f" {v:.3f}", va="center", fontsize=7)
    axes[1].axvline(1 / 3, color=NEUTRAL, ls="--", lw=1)
    axes[1].set_yticks(y2, [n for n, _ in three])
    axes[1].set_xlim(0, 1.0)
    axes[1].set_xlabel("three-way balanced accuracy (dashed: chance)")
    for ax in axes:
        ax.invert_yaxis()
    g.save(fig, f"comparison_{suite}", f"{title}: AUROC of P(supported) for every system, and three-way balanced accuracy for "
           f"systems with a three-way output. Word overlap and the sentence-only classifier never verify the sentence "
           f"against the document. Rizzo-Flow and the untrained 3B are evaluated on subsamples (see metrics files).",
           f"results/*/{suite}/metrics.json")


def by_task(g):
    tasks = ["QA", "Summary", "Data2txt"]
    series = [(label, name) for label, name, kind in SYSTEMS if kind != "overlap" and load(name, "t1")]
    if not series:
        return
    fig, ax = plt.subplots(figsize=(9, 3.4))
    w = 0.8 / len(series)
    for k, (label, name) in enumerate(series):
        m = load(name, "t1")
        vals = [binary_block({"binary": m["by_task"][t]["binary"]} if "binary" in m["by_task"].get(t, {}) else
                             {"binary": m["by_task"][t]})["auroc"] if t in m["by_task"] else np.nan for t in tasks]
        ax.bar(np.arange(3) + (k - (len(series) - 1) / 2) * w, vals, w * 0.95, color=COLORS.get(label, NEUTRAL), label=label)
    ax.set_xticks(range(3), tasks)
    ax.set_ylim(0.5, 1.0)
    ax.set_ylabel("AUROC, supported vs not")
    ax.legend(fontsize=7, ncol=3)
    g.save(fig, "t1_by_task", "T1 (RAGTruth test) AUROC per task for each system.", "results/*/t1/metrics.json")


def latency(g):
    panels = {s: [(l, load(n, "latency")) for l, n in v if load(n, "latency")] for s, v in LATENCY.items()}
    panels = {s: v for s, v in panels.items() if v}
    if not panels:
        return
    fig, axes = plt.subplots(1, len(panels), figsize=(5.5 * len(panels), 3.6), sharey=True)
    for ax, (size, series) in zip(np.atleast_1d(axes), panels.items()):
        for label, m in series:
            xs = [b for b in BANDS if b in m["latency_by_K_band"]]
            ax.plot(xs, [m["latency_by_K_band"][b]["median_s"] for b in xs], marker="o", color=LAT_COLORS[label], label=label)
        ax.set_yscale("log")
        ax.set_title(f"Qwen2.5 {size}")
        ax.set_xlabel("K = sentences checked in the answer")
    np.atleast_1d(axes)[0].set_ylabel("median seconds per answer (log scale)")
    np.atleast_1d(axes)[0].legend(fontsize=7)
    g.save(fig, "latency_vs_K", "Latency per answer as a function of K on the same T1 answers (in-process MLX, one answer at a "
           "time, M4 16 GB). Generative judges write a verdict per sentence; the System One reads all K verdicts without "
           "generating text.", "results/*/latency/metrics.json")
    fig, axes = plt.subplots(1, len(panels), figsize=(5.5 * len(panels), 3.4))
    for ax, (size, series) in zip(np.atleast_1d(axes), panels.items()):
        labels = [l for l, _ in series]
        acc = [m["macro_recall_failures_wrong"] for _, m in series]
        fail = [m["format_failure_rate"] for _, m in series]
        x = np.arange(len(series))
        b1 = ax.bar(x - 0.2, acc, 0.38, color=[LAT_COLORS[l] for l in labels], label="three-way balanced accuracy")
        b2 = ax.bar(x + 0.2, fail, 0.38, color=NEUTRAL, label="format failure rate")
        bar_labels(ax, b1, "{:.2f}")
        bar_labels(ax, b2, "{:.0%}")
        ax.set_xticks(x, [l.replace(" (", "\n(") for l in labels], fontsize=7)
        ax.set_ylim(0, 1.05)
        ax.set_title(f"Qwen2.5 {size}")
    np.atleast_1d(axes)[0].legend(fontsize=7)
    g.save(fig, "judges_quality_failures", "On the latency subset: three-way balanced accuracy (format failures counted as "
           "wrong) and share of sentences whose verdict could not be parsed. System One outputs are always valid.",
           "results/*/latency/metrics.json")


def main():
    g = Group("benchmarks")
    comparison(g, "t1", "T1 RAGTruth test")
    comparison(g, "t3", "T3 VitaminC test")
    by_task(g)
    latency(g)
    g.write_index("Benchmarks on the frozen test sets")
