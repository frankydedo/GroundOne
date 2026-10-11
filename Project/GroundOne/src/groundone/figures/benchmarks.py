"""Benchmark figures on the frozen test sets: system comparison on T1 and T3, per task, and latency as a function of K.

Reads results/<name>/{t1,t3}/metrics.json (GroundOne, untrained readout, encoders, Rizzo-Flow) and
results/<name>/latency/metrics.json (judges and System One timings). Missing results are skipped, so the figures can be
regenerated as runs complete. Usage: groundone figures benchmarks
"""
import json

import numpy as np

from ..config import DATA_PROCESSED, RESULTS_DIR
from .style import NEUTRAL, SERIES, SYSTEM_COLORS, Group, bar_labels, plt

SYSTEMS = [  # (label, results name, kind)
    ("Word overlap", None, "overlap"),
    ("HHEM", "hhem", "binary"),
    ("MiniCheck-RoBERTa", "minicheck-roberta", "binary"),
    ("Rizzo-Flow 4B", "rizzo-flow-4b-q4", "three"),
    ("d1-3B (Liquid AI)", "d1-3b", "three"),
    ("Untrained 0.5B", "untrained-05b", "three"),
    ("Untrained 3B", "untrained-3b", "three"),
    ("GroundOne 0.5B", "g1-05b-b1", "three"),
    ("GroundOne 3B", "g1-3b-b1", "three"),
]
COLORS = {**SYSTEM_COLORS, "Word overlap": "#c4c2bb", "Sentence only": "#8a877f", "d1-3B (Liquid AI)": "#e87ba4"}
LATENCY = {  # size -> [(label, results name)]
    "0.5B": [("GroundOne (design b)", "g1-05b-b1"), ("System One (design a)", "untrained-05b"),
             ("Terse judge", "judge-terse-05b"), ("Verbose judge", "judge-verbose-05b")],
    "3B": [("GroundOne (design b)", "g1-3b-b1"), ("System One (design a)", "untrained-3b"),
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
    shortcut = json.loads((DATA_PROCESSED / "groundone/shortcut_report.json").read_text())
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


def energy(g):
    """Joules per verified answer (powermetrics, SoC, net of idle) and the speed-up vs energy ratio, per model size."""
    rows = {"0.5B": [("GroundOne", "energy-g1-05b"), ("Terse judge", "energy-terse-05b"), ("Verbose judge", "energy-verbose-05b")],
            "3B": [("GroundOne", "energy-g1-3b"), ("Terse judge", "energy-terse-3b"), ("Verbose judge", "energy-verbose-3b")]}
    col = {"GroundOne": SERIES[0], "Terse judge": SERIES[7], "Verbose judge": SERIES[5]}
    data = {s: [(l, load(n, "energy")) for l, n in v if load(n, "energy")] for s, v in rows.items()}
    data = {s: v for s, v in data.items() if v}
    if not data:
        return
    fig, axes = plt.subplots(1, len(data), figsize=(5.2 * len(data), 3.4))
    for ax, (size, series) in zip(np.atleast_1d(axes), data.items()):
        labels = [l for l, _ in series]
        j = [m["energy"]["net_joules_per_answer"] for _, m in series]
        w = [m["energy"]["net_watts"] for _, m in series]
        bars = ax.bar(range(len(series)), j, color=[col[l] for l in labels])
        for b, jj, ww in zip(bars, j, w):
            ax.annotate(f"{jj:.1f} J\n{ww:.0f} W", (b.get_x() + b.get_width() / 2, jj), xytext=(0, 2),
                        textcoords="offset points", ha="center", va="bottom", fontsize=7)
        ax.set_xticks(range(len(series)), labels, fontsize=8)
        ax.set_ylim(0, max(j) * 1.25)
        ax.set_title(f"Qwen2.5 {size}")
    np.atleast_1d(axes)[0].set_ylabel("joules per answer (net of idle)")
    g.save(fig, "energy_per_answer", "Energy per verified answer on 100 latency answers (powermetrics, CPU + GPU + Neural "
           "Engine, net of idle power), with the mean net power during the run. GroundOne uses the least energy, but its "
           "single long prefill draws more power than autoregressive decoding, so the energy advantage is smaller than the "
           "speed advantage.", "results/energy-*/energy/metrics.json")


def equal_output(g):
    """Equal-output judges (B0d): ranking quality (AUROC) and calibrated risk-coverage (AURC) vs GroundOne."""
    sys = [("GroundOne", "g1-{t}-b1", SERIES[0]), ("Judge, logits", "judge-tlogit-{t}", "#8a877f"),
           ("Judge, verbalised", "judge-json-{t}", "#c4c2bb")]
    vals = {}
    for size, t in (("0.5B", "05b"), ("3B", "3b")):
        for label, name, _ in sys:
            p = RESULTS_DIR / name.format(t=t) / "latency" / "calibration.json"
            c = json.loads(p.read_text())["t1"] if p.exists() else None
            if c:
                vals[(size, label)] = (c["raw"]["binary"]["auroc"], c["affine"]["aurc"])
    if not vals:
        return
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.4))
    x = np.arange(2)
    for k, (label, _, colr) in enumerate(sys):
        for ax, i, fmt in ((axes[0], 0, "{:.2f}"), (axes[1], 1, "{:.3f}")):
            ys = [vals.get((s, label), (np.nan, np.nan))[i] for s in ("0.5B", "3B")]
            bars = ax.bar(x + (k - 1) * 0.27, ys, 0.25, color=colr, label=label)
            bar_labels(ax, bars, fmt)
    for ax, t in ((axes[0], "AUROC of P(supported), higher is better"), (axes[1], "AURC after calibration, lower is better")):
        ax.set_xticks(x, ["Qwen2.5 0.5B", "Qwen2.5 3B"])
        ax.set_title(t)
    axes[0].axhline(0.5, color=NEUTRAL, ls="--", lw=1)
    axes[0].set_ylim(0, 1.22)
    axes[0].legend(fontsize=7, loc="upper center", ncol=3, frameon=True, facecolor="white", edgecolor="#e4e3df")
    g.save(fig, "equal_output_judges", "Equal-output comparison on the 200 latency answers: generative judges of the same size "
           "asked for GroundOne's output (a label and three probabilities per sentence), with probabilities read from the "
           "logits of the generated letter or written in JSON; all systems calibrated on dev with the same map. Sentences "
           "with a valid verdict only.", "results/{g1-*,judge-tlogit-*,judge-json-*}/latency/calibration.json")


def readout_vs_generation(g):
    """Control B2: restricted three-letter readout vs the token greedy generation would emit, same weights and pass."""
    rows = [(s, load(f"b2-{t}", "t1")) for s, t in (("0.5B", "05b"), ("3B", "3b"))]
    rows = [(s, m) for s, m in rows if m]
    if not rows:
        return
    fig, axes = plt.subplots(1, len(rows), figsize=(5.2 * len(rows), 3.4), sharey=True)
    for ax, (size, m) in zip(np.atleast_1d(axes), rows):
        groups = ["all T1", "K ≥ 14"]
        ro = [m["macro_recall_readout"], m["by_K_band"][">=14"]["readout"]]
        ge = [m["macro_recall_generate_failures_wrong"], m["by_K_band"][">=14"]["generate"]]
        x = np.arange(2)
        b1 = ax.bar(x - 0.2, ro, 0.38, color=SERIES[0] if size == "0.5B" else SERIES[6], label="restricted readout (GroundOne)")
        b2 = ax.bar(x + 0.2, ge, 0.38, color=NEUTRAL, label="generated token (B2)")
        bar_labels(ax, b1, "{:.3f}")
        bar_labels(ax, b2, "{:.3f}")
        ax.set_xticks(x, groups)
        ax.set_ylim(0, 1.0)
        ax.set_title(f"Qwen2.5 {size} (format failures of B2: {m['format_failure_rate']:.1%})")
    np.atleast_1d(axes)[0].set_ylabel("T1 three-way balanced accuracy")
    np.atleast_1d(axes)[0].legend(fontsize=7, loc="lower left")
    g.save(fig, "readout_vs_generation", "Control B2 on the full T1: with the same fine-tuned weights and the same forward pass, "
           "the verdict is either read from the three answer letters (GroundOne) or taken as the token that greedy "
           "generation would emit at the marker (failures counted as errors).", "results/b2-*/t1/metrics.json")


def seed_runs(g):
    """Dev three-way balanced accuracy during training for the 0.5B runs (two completed seeds, one stopped after collapse)."""
    from ..config import MODELS_DIR
    runs = [("seed 1234 (run 1)", "g1-05b-b1", SERIES[0], "-"), ("seed 777 (run 2)", "g1-05b-s3", SERIES[2], "-"),
            ("seed 4321 (stopped)", "g1-05b-s2", SERIES[7], "--")]
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    drawn = False
    for label, run, colr, ls in runs:
        p = MODELS_DIR / run / "train_log.jsonl"
        if not p.exists():
            continue
        ev = [json.loads(l) for l in open(p) if '"event": "eval"' in l]
        if not ev:
            continue
        ax.plot([e["step"] for e in ev], [e["dev_macro_recall_all"] for e in ev], marker="o", color=colr, ls=ls, label=label)
        drawn = True
    if not drawn:
        plt.close(fig)
        return
    ax.axhline(1 / 3, color=NEUTRAL, ls=":", lw=1)
    ax.annotate("chance / constant predictor", (480, 1 / 3 - 0.025), fontsize=7, color=NEUTRAL)
    ax.set_xlabel("optimiser step")
    ax.set_ylabel("dev three-way balanced accuracy")
    ax.set_ylim(0.25, 0.8)
    ax.legend(fontsize=7, loc="center right")
    g.save(fig, "seed_runs_05b", "Development three-way balanced accuracy during training of the 0.5B with the same recipe and "
           "three seeds. Two runs converge to the same level; the third collapsed to a constant predictor after step 150 and "
           "was stopped at step ≈ 470.", "models/g1-05b-{b1,s3,s2}/train_log.jsonl")


def main():
    g = Group("benchmarks")
    seed_runs(g)
    energy(g)
    equal_output(g)
    readout_vs_generation(g)
    comparison(g, "t1", "T1 RAGTruth test")
    comparison(g, "t3", "T3 VitaminC test")
    by_task(g)
    latency(g)
    g.write_index("Benchmarks on the frozen test sets")
