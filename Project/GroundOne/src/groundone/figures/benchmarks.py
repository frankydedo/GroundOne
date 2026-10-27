"""Benchmark figures on the frozen test sets: system comparison on T1 and T3, per task, and latency as a function of K.

Reads results/<name>/{t1,t3}/metrics.json (GroundOne, untrained readout, encoders, Rizzo-Flow) and
results/<name>/latency/metrics.json (LLM judges and System One timings). Missing results are skipped, so the figures can be
regenerated as runs complete. Usage: groundone figures benchmarks
"""
import json

import numpy as np

from ..config import DATA_PROCESSED, RESULTS_DIR
from .style import GRID, INK2, LANG, NEUTRAL, SERIES, SYSTEM_COLORS, Group, _tr_text, bar_labels, plt

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
    "0.5B": [("GroundOne (design b)", "g1-05b-b1"), ("Decision model (design a)", "untrained-05b"),
             ("Terse LLM judge", "judge-terse-05b"), ("Verbose LLM judge", "judge-verbose-05b")],
    "3B": [("GroundOne (design b)", "g1-3b-b1"), ("Decision model (design a)", "untrained-3b"),
           ("Terse LLM judge", "judge-terse-3b"), ("Verbose LLM judge", "judge-verbose-3b")],
}
LAT_COLORS = {"GroundOne (design b)": SERIES[0], "Decision model (design a)": SERIES[4], "Terse LLM judge": SERIES[7],
              "Verbose LLM judge": SERIES[5]}
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
           "time, M4 16 GB). LLM judges write a verdict per sentence; the System One reads all K verdicts without "
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
    rows = {"0.5B": [("GroundOne", "energy-g1-05b"), ("Terse LLM judge", "energy-terse-05b"), ("Verbose LLM judge", "energy-verbose-05b")],
            "3B": [("GroundOne", "energy-g1-3b"), ("Terse LLM judge", "energy-terse-3b"), ("Verbose LLM judge", "energy-verbose-3b")]}
    col = {"GroundOne": SERIES[0], "Terse LLM judge": SERIES[7], "Verbose LLM judge": SERIES[5]}
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
    """Equal-output LLM judges (B0d): ranking quality (AUROC) and calibrated risk-coverage (AURC) vs GroundOne."""
    sys = [("GroundOne", "g1-{t}-b1", SERIES[0]), ("LLM judge, logits", "judge-tlogit-{t}", "#8a877f"),
           ("LLM judge, verbalised", "judge-json-{t}", "#c4c2bb")]
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
    g.save(fig, "equal_output_judges", "Equal-output comparison on the 200 latency answers: LLM judges of the same size "
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


def gain_decomposition(g):
    """T1 three-way balanced accuracy: untrained readout -> fine-tuned with generated token (B2) -> restricted readout."""
    rows = []
    for size, unt, b2, g1 in (("0.5B", "untrained-05b", "b2-05b", "g1-05b-b1"), ("3B", "untrained-3b", "b2-3b", "g1-3b-b1")):
        mu, mb, mg = load(unt, "t1"), load(b2, "t1"), load(g1, "t1")
        if not (mu and mb and mg):
            return
        rows.append((size, mu["all"]["macro_recall"], mb["macro_recall_generate_failures_wrong"], mg["all"]["macro_recall"]))
    labels = ["untrained (readout)", "fine-tuned, generated token (B2)", "fine-tuned, restricted readout (GroundOne)"]
    cols = [NEUTRAL, SERIES[3], SERIES[0]]
    fig, ax = plt.subplots(figsize=(7.5, 3.4))
    w = 0.26
    for k, (lab, col) in enumerate(zip(labels, cols)):
        xs = np.arange(len(rows)) + (k - 1) * w
        vals = [r[k + 1] for r in rows]
        bars = ax.bar(xs, vals, w * 0.92, color=col, label=lab)
        for b, r, v in zip(bars, rows, vals):
            txt = f"{v:.3f}" if k == 0 else f"{v:.3f}\n(+{v - r[k]:.2f})"
            ax.text(b.get_x() + b.get_width() / 2, v + 0.01, txt, ha="center", va="bottom", fontsize=7)
    ax.axhline(1 / 3, color=NEUTRAL, ls="--", lw=1)
    ax.set_xticks(range(len(rows)), [f"Qwen2.5 {r[0]}" for r in rows])
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("T1 three-way balanced accuracy")
    ax.legend(fontsize=7, loc="upper left")
    g.save(fig, "gain_decomposition", "Where GroundOne's accuracy on T1 comes from: the same base model untrained (readout, design "
           "a), fine-tuned but deciding with the token it would generate (control B2, format failures counted as wrong), and "
           "fine-tuned with the restricted readout. In brackets, the gain over the previous step. The untrained 3B "
           "is evaluated on 600 answers. Dashed: chance.", "results/{untrained,b2,g1}-*/t1/metrics.json")


def latency_split(g):
    """Time per answer split into reading the text (prefill, shared) and deciding, per K band and model size."""
    runs = {"0.5B": "decompose-05b", "3B": "decompose-3b"}
    data = {s: json.loads(p.read_text()) for s, n in runs.items()
            if (p := RESULTS_DIR / n / "decompose" / "metrics.json").exists()}
    if not data:
        return
    systems = [("groundone", "GroundOne", SERIES[0]), ("terse", "Terse LLM judge", SERIES[7]),
               ("verbose", "Verbose LLM judge", SERIES[5])]
    fig, axes = plt.subplots(1, len(data), figsize=(5.6 * len(data), 3.8))
    w = 0.26
    for ax, (size, m) in zip(np.atleast_1d(axes), data.items()):
        for k, (key, label, color) in enumerate(systems):
            if key not in m["systems"]:
                continue
            bands = m["systems"][key]["by_K_band"]
            x = np.arange(len(BANDS)) + (k - 1) * w
            read = [bands[b]["read_s"] if b in bands else np.nan for b in BANDS]
            decide = [max(bands[b]["decide_s"], 0) if b in bands else np.nan for b in BANDS]
            ax.bar(x, read, w * 0.92, color="#d9d7d0", edgecolor="white", linewidth=0.5,
                   label="reading the text (prefill)" if k == 0 else None)
            ax.bar(x, decide, w * 0.92, bottom=read, color=color, edgecolor="white", linewidth=0.5,
                   label="GroundOne: deciding (markers + readout)" if key == "groundone" else f"{label}: writing the verdicts")
            if key != "groundone" and ">=14" in m["speedup"].get(key, {}):
                sp = m["speedup"][key][">=14"]["decide"]["ratio"]
                ax.annotate(f"×{sp:.0f}", (x[-1], read[-1] + decide[-1]), xytext=(0, 2), textcoords="offset points",
                            ha="center", va="bottom", fontsize=7)
        ax.set_xticks(range(len(BANDS)), BANDS)
        ax.set_xlabel("K = sentences checked in the answer")
        ax.set_title(f"Qwen2.5 {size}")
    np.atleast_1d(axes)[0].set_ylabel("median seconds per answer")
    np.atleast_1d(axes)[0].legend(fontsize=7, loc="upper left")
    g.save(fig, "latency_split", "Time to verify one answer split into reading the document and the answer (the prefill, "
           "which every approach pays) and deciding: for GroundOne the marker tokens and the readout, for the LLM judges "
           "the decoding of the verdicts. Same 200 T1 answers as the latency runs, in-process MLX, medians per K band. "
           "The labels give, for K >= 14, how many times longer the LLM judge takes to decide than GroundOne.",
           "results/decompose-*/decompose/metrics.json")


def prefill_composition(g):
    """What the prompt is made of and what each part costs: (a) GroundOne's prompt tokens by part, (b) measured time per
    part (cache levels none / instructions / document) for GroundOne and the terse LLM judge, 3B."""
    import pandas as pd
    d = RESULTS_DIR / "decompose-3b" / "decompose"
    runs = {f"{s}{c}": d / f"{s}{c}.parquet" for s in ("groundone", "terse") for c in ("", "-fixed", "-doc")}
    if not all(p.exists() for p in runs.values()):
        return
    r = {k: pd.read_parquet(p) for k, p in runs.items()}
    parts = [("instructions (fixed: cached)", "#1d4f91"), ("document (fixed for the same sources: cached)", SERIES[0]),
             ("answer (changes: read from the first changed token)", SERIES[3]),
             ("deciding (GroundOne: markers + readout; judge: writing the verdicts)", SERIES[7])]
    fig, (a, b) = plt.subplots(1, 2, figsize=(11.2, 4.0), gridspec_kw={"width_ratios": [1, 1.25]})
    # (a) tokens: instructions = cached with "fixed", document = cached with "doc" minus that, markers = 3 per sentence
    m = r["groundone"].merge(r["groundone-doc"][["rid", "cached_tokens"]], on="rid").merge(
        r["groundone-fixed"][["rid", "cached_tokens"]].rename(columns={"cached_tokens": "fx"}), on="rid")
    tok = pd.DataFrame({"kband": m.kband, "i": m.fx, "d": m.cached_tokens - m.fx, "a": m.read_tokens - m.cached_tokens,
                        "k": m.prompt_tokens - m.read_tokens}).groupby("kband").mean().reindex(BANDS)
    x = np.arange(len(BANDS))
    bottom = np.zeros(len(BANDS))
    for col, (_, color) in zip("idak", parts):
        a.bar(x, tok[col], 0.6, bottom=bottom, color=color, edgecolor="white", linewidth=1)
        bottom += tok[col].to_numpy()
    for i, band in enumerate(BANDS):
        t = tok.loc[band]
        a.text(i, t.i + t.d / 2, f"{t.d / t.sum():.0%}", ha="center", va="center", fontsize=7, color="white")
        a.text(i, t.i + t.d + (t.a + t.k) / 2, f"{(t.a + t.k) / t.sum():.0%}", ha="center", va="center", fontsize=7)
    a.set_xticks(x, BANDS)
    a.set_xlabel("K = sentences checked in the answer")
    a.set_ylabel("mean prompt tokens per answer")
    a.set_title("(a) GroundOne's prompt, by part")
    # (b) time: differences of band medians between cache levels, so the stack adds up to the median without cache
    med = {k: v.groupby("kband").total_s.median().reindex(BANDS) for k, v in r.items()}
    w = 0.36
    for j, (sys, label, hatch) in enumerate([("groundone", "GroundOne", None), ("terse", "Terse LLM judge", "///")]):
        doc = r[f"{sys}-doc"].groupby("kband")
        read = doc.read_s.median().reindex(BANDS)
        seg = [med[sys] - med[f"{sys}-fixed"], med[f"{sys}-fixed"] - med[f"{sys}-doc"], read, med[f"{sys}-doc"] - read]
        xs = x + (j - 0.5) * w
        bottom = np.zeros(len(BANDS))
        for s, (_, color) in zip(seg, parts):
            v = np.clip(s.to_numpy(), 0, None)
            b.bar(xs, v, w * 0.92, bottom=bottom, color=color, edgecolor="white", linewidth=0.8, hatch=hatch)
            bottom += v
        for xi, top in zip(xs, bottom):
            b.text(xi, top, "G1" if sys == "groundone" else "J", ha="center", va="bottom", fontsize=7)
    b.set_xticks(x, BANDS)
    b.set_xlabel("K = sentences checked in the answer")
    b.set_ylabel("median seconds per answer (3B)")
    b.set_title("(b) Time per part: GroundOne (G1) and terse LLM judge (J)")
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for _, c in parts]
    fig.legend(handles, [p for p, _ in parts], loc="upper center", ncol=2, fontsize=7.5, frameon=False,
               bbox_to_anchor=(0.5, -0.01))   # below the axes: tight_layout ignores figure legends
    g.save(fig, "prefill_composition",
           "Composition of the prefill. (a) GroundOne's prompt on the 200 T1 latency answers, mean tokens by part per K "
           "band: the fixed instructions, the document, the answer and its markers (labels: share of the document and "
           "of answer + markers). (b) Measured time per part with the 3B, from the runs with nothing, the instructions or "
           "the instructions and the document in the KV cache (differences of the band medians, so each stack adds up to "
           "the median time without cache). The parts that stay the same across verifications of the same sources "
           "(blue) are the ones worth caching; the answer changes with every version.",
           "results/decompose-3b/decompose/*.parquet")


def speedup_summary(g):
    """GroundOne's speed-up over the LLM judges in each situation, at equal conditions (same answers, machine, cache):
    no cache, sources cached (read ahead or verified before), after a rewrite, and the deciding part alone."""
    runs = {"0.5B": "decompose-05b", "3B": "decompose-3b"}
    data = {s: json.loads(p.read_text()) for s, n in runs.items()
            if (p := RESULTS_DIR / n / "decompose" / "metrics.json").exists()}
    if len(data) < 2 or any("cache" not in m or "rewrite" not in m for m in data.values()):
        return
    situations = [  # (label, getter(metrics, judge) -> {"ratio", "ci95"} or None, hatched)
        ("no cache\nall answers", lambda m, j: m["speedup"][j]["all"]["total"], False),
        ("no cache\nK ≥ 14", lambda m, j: m["speedup"][j][">=14"]["total"], False),
        ("sources\ncached\nall answers", lambda m, j: m["cache"]["doc"]["speedup"][j]["all"]["total"], False),
        ("sources\ncached\nK ≥ 14", lambda m, j: m["cache"]["doc"]["speedup"][j][">=14"]["total"], False),
        ("after a\nrewrite\nall answers", lambda m, j: m["rewrite"]["terse_over_groundone"]["prefix"] if j == "terse" else None, False),
        ("deciding\nonly (net\nof reading)", lambda m, j: m["speedup"][j]["all"]["decide"], True),
    ]
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.0), sharey=True)
    x = np.arange(len(situations))
    w = 0.38
    for ax, (judge, title) in zip(axes, [("terse", "(a) Terse LLM judge"), ("verbose", "(b) Verbose LLM judge")]):
        for k, size in enumerate(["0.5B", "3B"]):
            color = SYSTEM_COLORS[f"GroundOne {size}"]
            for i, (_, get, hatched) in enumerate(situations):
                r = get(data[size], judge)
                xi = x[i] + (k - 0.5) * w
                if r is None:
                    ax.text(xi, 1.15, "n.m.", ha="center", va="bottom", fontsize=7, color=NEUTRAL)
                    continue
                lo, hi = r["ci95"]
                ax.bar(xi, r["ratio"], w * 0.9, color=color, edgecolor="white", linewidth=0.8,
                       hatch="///" if hatched else None, alpha=0.75 if hatched else 1.0,
                       label=f"GroundOne {size}" if i == 0 else None)
                ax.errorbar(xi, r["ratio"], yerr=[[r["ratio"] - lo], [hi - r["ratio"]]], fmt="none", ecolor=INK2,
                            elinewidth=0.9, capsize=2)
                ax.text(xi, hi * 1.06, f"{r['ratio']:.1f}" if r["ratio"] < 10 else f"{r['ratio']:.0f}", ha="center",
                        va="bottom", fontsize=7)
        ax.axhline(1, color=INK2, linewidth=0.8, linestyle="--")
        ax.axvline(len(situations) - 1.5, color=GRID, linewidth=1.2)
        ax.set_yscale("log")
        ax.set_yticks([1, 2, 5, 10, 20, 50, 100], ["1", "2", "5", "10", "20", "50", "100"])
        ax.minorticks_off()
        ax.grid(axis="x", visible=False)
        # tick labels are redrawn from the formatter, after `localise`: translate them here
        ax.set_xticks(x, [_tr_text(s) if LANG == "it" else s for s, _, _ in situations], fontsize=7.5)
        ax.set_title(title)
    axes[0].set_ylabel("speed-up of GroundOne (× faster, log scale)")
    axes[0].legend(fontsize=7.5, loc="upper left")
    g.save(fig, "speedup_summary",
           "GroundOne's speed-up over the LLM judges in each situation, on the same 200 T1 answers (ratio of median "
           "times, 95 % bootstrap intervals). In every situation GroundOne and the judge have the same cache: the sources "
           "cached are the state after a read-ahead or an earlier verification; after a rewrite, the beginning of the "
           "answer is cached as well (verbose judge not measured, n.m.). The hatched bars, right of the line, exclude "
           "reading the text: the limit that the overall speed-up approaches as the reading shrinks.",
           "results/decompose-*/decompose/metrics.json")


def main():
    g = Group("benchmarks")
    seed_runs(g)
    energy(g)
    equal_output(g)
    readout_vs_generation(g)
    gain_decomposition(g)
    comparison(g, "t1", "T1 RAGTruth test")
    comparison(g, "t3", "T3 VitaminC test")
    by_task(g)
    latency(g)
    latency_split(g)
    prefill_composition(g)
    speedup_summary(g)
    g.write_index("Benchmarks on the frozen test sets")
