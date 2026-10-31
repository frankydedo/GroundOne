"""Figures of the local-inference chapter (Ch. 2): hardware landscape, bandwidth bounds, memory fit, open/closed gap.

Hardware numbers are the vendors' published specifications (sources in HARDWARE); every derived quantity is arithmetic
on them (stated in the captions). Own measurements come from Phase 0 (prefill/decode on the M4) and from the latency
protocol of the generative judges.
"""
import re
from datetime import date

import numpy as np
import pandas as pd

from ..config import EXPERIMENTS, PROJECT, RESULTS_DIR
from .style import INK2, NEUTRAL, SERIES, SURFACE, Group, load_json, plt

RAW = PROJECT.parent / "Vault" / "raw" / "local_inference"
PHASE0 = EXPERIMENTS / "feasibility" / "results"

# name: (max memory GB, bandwidth GB/s, kind, source). Bandwidth is the vendor's figure for the configuration with the
# listed maximum memory; kind = unified memory (CPU and GPU share it) or discrete GPU memory.
HARDWARE = {
    "MacBook Pro M4\n(thesis machine, 16 GB)": (16, 120, "unified", "Apple, MacBook Pro 14-inch M4 tech specs", 16),
    "MacBook Pro / Mac mini M5": (32, 153, "unified", "Apple, MacBook Pro and Mac mini tech specs (2026)", 16),
    "Mac mini M5 Pro": (64, 307, "unified", "Apple, Mac mini tech specs (2026)", 24),
    "MacBook Pro M5 Max": (128, 614, "unified", "Apple, MacBook Pro tech specs (2026)", 48),
    "Mac Studio M4 Max": (128, 546, "unified", "Apple, Mac Studio (2025) tech specs", 48),
    "Mac Studio M3 Ultra": (256, 819, "unified", "Apple, Mac Studio (2025) tech specs", 96),
    "NVIDIA DGX Spark": (128, 273, "unified", "NVIDIA, DGX Spark hardware overview", 128),
    "RTX 5090": (32, 1792, "discrete", "NVIDIA, GeForce compare specs (2026)", 32),
    "RTX 5080": (16, 960, "discrete", "NVIDIA, GeForce compare specs (2026)", 16),
    "RTX 5060 Ti": (16, 448, "discrete", "NVIDIA, GeForce compare specs (2026)", 16),
}
# name: (max memory GB, bandwidth GB/s, kind, source, min memory GB of the configurations with that bandwidth). The thesis
# machine is plotted at its actual 16 GB.
KIND_COLOR = {"unified": SERIES[0], "discrete": SERIES[1]}
THESIS = "MacBook Pro M4\n(thesis machine, 16 GB)"

# Italian labels for the Italian thesis (figures/locality_it); any string not listed stays as it is.
IT = {
    "MacBook Pro M4\n(thesis machine, 16 GB)": "MacBook Pro M4\n(macchina della tesi, 16 GB)",
    "reading a prompt token (prefill)": "lettura di un token del prompt (prefill)",
    "writing an output token (decode)": "scrittura di un token di output (decoding)",
    "× per token": "× per token",
    "milliseconds per token (log scale)": "millisecondi per token (scala log.)",
    "memory available to the model (GB, log scale)  →  which models fit": "memoria disponibile per il modello (GB, scala log.)  →  quali modelli entrano",
    "memory bandwidth (GB/s, log scale)\n→  how fast tokens are generated": "banda di memoria (GB/s, scala log.)\n→  velocità di generazione dei token",
    "unified memory (shared by CPU and GPU)": "memoria unificata (condivisa da CPU e GPU)",
    "discrete GPU memory (VRAM)": "memoria dedicata della GPU (VRAM)",
    "1,600": "1600",
    "measured on the M4 (Phase 0)": "misurato sull'M4 (Fase 0)",
    "minimum milliseconds per generated token (log scale)": "millisecondi minimi per token generato (scala log.)",
    "minimum seconds spent writing the verdicts of one answer (log scale)": "secondi minimi per scrivere i verdetti di una risposta (scala log.)",
    "(a) any model that generates: time per token": "(a) qualunque modello che genera: tempo per token",
    "(b) 3B LLM judge: time to write the verdicts (answers with ≥ 14 sentences)": "(b) giudice LLM da 3B: tempo per scrivere i verdetti (risposte con ≥ 14 frasi)",
    "terse LLM judge": "giudice LLM sintetico", "verbose LLM judge": "giudice LLM verboso",
    "generated tokens": "token generati",
    "of weights": "di pesi",
    "16-bit (training format)": "16 bit (formato di addestramento)",
    "8-bit (MLX, as in GroundOne)": "8 bit (MLX, come in GroundOne)",
    "4-bit (typical local deployment)": "4 bit (tipico dell'uso locale)",
    "7–8B generator": "generatore da 7–8B", "70B model": "modello da 70B",
    "parameters (billions, log scale)": "parametri (miliardi, scala log.)",
    "memory for the weights alone (GB, log scale)": "memoria per i soli pesi (GB, scala log.)",
    "best closed model (API)": "miglior modello chiuso (API)",
    "best open-weight model": "miglior modello open-weight",
    "bandwidth roof: 120 GB/s × intensity": "tetto della banda: 120 GB/s × intensità",
    "compute reached in prefill": "calcolo raggiunto nel prefill",
    "(lower bound of the peak)": "(limite inferiore del picco)",
    "decode, 1 token\n(both models)": "decoding, 1 token\n(entrambi i modelli)",
    "prefill, 500 tokens\n(0.5B, FFN layer)": "prefill, 500 token\n(0.5B, strato FFN)",
    "prefill, 1,000 tokens\n(3B, FFN layer)": "prefill, 1000 token\n(3B, strato FFN)",
    "ridge": "ridge point",
    "arithmetic intensity (FLOPs per byte read from memory, log scale)": "intensità aritmetica (FLOP per byte letto dalla memoria, scala log.)",
    "attainable throughput (TFLOP/s, log scale)": "throughput raggiungibile (TFLOP/s, scala log.)",
    "gap between the best closed and the best open-weight model:": "divario tra il miglior modello chiuso e il miglior open-weight:",
    "closed": "chiuso", "open-weight": "open-weight", "open-weight, small class": "open-weight, classe piccola",
}
LANG = "en"


def tr(text):
    return IT.get(text, text) if LANG == "it" else text


# weight bytes of the two GroundOne bases in MLX 8-bit (group size 64: 8 bits + 0.5 bits of scale and bias per weight)
PARAMS = {"Qwen2.5-0.5B": 0.494e9, "Qwen2.5-3B": 3.09e9}
BITS_MLX8 = 8.5


def _weight_gb(params, bits):
    return params * bits / 8 / 1e9


def prefill_vs_decode(g):
    """Own Phase 0 measurement: time per prompt token (prefill) vs per generated token (decode) on the M4."""
    rows = []
    for key, lab in [("qwen0.5b", "Qwen2.5-0.5B"), ("qwen3b", "Qwen2.5-3B")]:
        d = load_json(PHASE0 / f"04_speed_{key}.json")
        if not d:
            return
        per_tok = np.median([d["table"][f"L{L}_K1"]["s1_prefill_ms"] / L for L in (500, 1000, 2000)])
        rows.append((lab, per_tok, d["decode_ms_per_token_median"]))
    fig, ax = plt.subplots(figsize=(6.2, 3.2))
    x = np.arange(len(rows))
    w = 0.36
    ax.bar(x - w / 2, [r[1] for r in rows], w, color=SERIES[0], label=tr("reading a prompt token (prefill)"))
    ax.bar(x + w / 2, [r[2] for r in rows], w, color=SERIES[7], label=tr("writing an output token (decode)"))
    for i, (lab, p, dcd) in enumerate(rows):
        ax.text(i - w / 2, p * 1.08, f"{p:.2f}", ha="center", va="bottom", fontsize=8, color=INK2)
        ax.text(i + w / 2, dcd * 1.08, f"{dcd:.1f}", ha="center", va="bottom", fontsize=8, color=INK2)
        ax.text(i, dcd * 2.3, f"{dcd / p:.0f}" + tr("× per token"), ha="center", fontsize=9, fontweight="bold")
    ax.set_yscale("log")
    ax.set_ylim(0.1, 200)
    ax.set_xticks(x, [r[0] for r in rows])
    ax.set_ylabel(tr("milliseconds per token (log scale)"))
    ax.legend(loc="upper left")
    g.save(fig, "prefill_vs_decode_m4", "Time per token when the model reads its input (prefill) and when it writes its "
           "output (decode), measured on the thesis machine (Apple M4, 16 GB, MLX 8-bit, batch 1). Prefill time is the "
           "median over 500-, 1,000- and 2,000-token contexts divided by the context length; decode time is the median "
           "per generated token. Writing a token costs about fifteen times more than reading one.",
           "experiments/feasibility/results/04_speed_*.json (Phase 0)")


def hardware_landscape(g):
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    for name, (mem, bw, kind, _, mem_min) in HARDWARE.items():
        if mem_min < mem:
            ax.plot([mem_min, mem], [bw, bw], color=KIND_COLOR[kind], lw=3, alpha=0.35, solid_capstyle="round", zorder=2)
        ax.scatter(mem, bw, s=70 if name != THESIS else 110, color=KIND_COLOR[kind], edgecolor="white", linewidth=1.5,
                   zorder=3, marker="o" if kind == "unified" else "s")
        dx, dy, ha = (1.12, 1.02, "left")
        if name in ("Mac Studio M3 Ultra",):
            dx, dy, ha = (1.0, 1.13, "right")
        ax.annotate(tr(name).replace("\n", " "), (mem, bw), xytext=(mem * dx, bw * dy), fontsize=7.5, ha=ha, va="center",
                    color="#0b0b0b" if name == THESIS else INK2, fontweight="bold" if name == THESIS else "normal")
    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    ax.set_xticks([16, 32, 64, 128, 256], ["16", "32", "64", "128", "256"])
    ax.set_yticks([100, 200, 400, 800, 1600], ["100", "200", "400", "800", tr("1,600")])
    ax.set_xlim(11, 400)
    ax.set_ylim(90, 2600)
    ax.set_xlabel(tr("memory available to the model (GB, log scale)  →  which models fit"))
    ax.set_ylabel(tr("memory bandwidth (GB/s, log scale)\n→  how fast tokens are generated"))
    for kind, lab in [("unified", "unified memory (shared by CPU and GPU)"), ("discrete", "discrete GPU memory (VRAM)")]:
        ax.scatter([], [], color=KIND_COLOR[kind], marker="o" if kind == "unified" else "s", label=tr(lab))
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, fontsize=8)
    g.save(fig, "hardware_landscape", "Local inference hardware on the two axes that decide what can run: memory capacity "
           "(which models fit) and memory bandwidth (how fast tokens can be generated). Discrete GPUs have the highest "
           "bandwidth but at most 32 GB; unified-memory machines trade bandwidth for capacity. Values are the vendors' "
           "published specifications (Apple, NVIDIA spec pages, accessed 2026-10-11): the marker is the largest memory "
           "configuration at that bandwidth, the shaded bar the range of memory sizes offered; the thesis machine is "
           "shown at its actual 16 GB.", "figures/locality.py HARDWARE (vendor spec pages in Vault/raw/local_inference)")


def decode_cost_by_hardware(g):
    """Two panels: (a) lower bound per generated token for both bases; (b) lower bound on a 3B judge's decoding per long
    answer (median generated tokens of the latency protocol). Both = weight bytes / bandwidth (batch 1)."""
    toks = {}
    for j in ("terse", "verbose"):
        p = RESULTS_DIR / f"judge-{j}-3b" / "latency" / "predictions.parquet"
        if not p.exists():
            return
        x = pd.read_parquet(p).drop_duplicates("rid")
        toks[j] = float(x[x.K >= 14].generated_tokens.median())
    meas = {"Qwen2.5-0.5B": load_json(PHASE0 / "04_speed_qwen0.5b.json"), "Qwen2.5-3B": load_json(PHASE0 / "04_speed_qwen3b.json")}
    names = sorted(HARDWARE, key=lambda n: HARDWARE[n][1])
    labels = [tr(n).replace("\n", " ") for n in names]
    y = np.arange(len(names))
    h = 0.38
    i = names.index(THESIS)
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.0, 7.6))
    for k, (model, params) in enumerate(PARAMS.items()):
        gb = _weight_gb(params, BITS_MLX8)
        vals = [gb / HARDWARE[n][1] * 1000 for n in names]
        a1.barh(y + (k - 0.5) * h, vals, h, color=[SERIES[0], SERIES[6]][k], label=f"{model}, 8-bit ({gb:.2f} GB {tr('of weights')})")
        for q, (yi, v) in enumerate(zip(y + (k - 0.5) * h, vals)):
            txt = f"{v:.1f}" if v >= 1 else f"{v:.2f}"
            if q == i and meas[model]:  # thesis machine: bound inside the bar end, measured value next to the diamond
                a1.text(v / 1.06, yi, txt, va="center", ha="right", fontsize=7, color="white")
            else:
                a1.text(v * 1.05, yi, txt, va="center", fontsize=7, color=INK2)
    for k, (model, d) in enumerate(meas.items()):
        if d:
            a1.scatter(d["decode_ms_per_token_median"], i + (k - 0.5) * h, marker="D", color="#0b0b0b", s=22, zorder=4,
                       label=tr("measured on the M4 (Phase 0)") if k == 0 else None)
            a1.text(d["decode_ms_per_token_median"] * 1.12, i + (k - 0.5) * h, f"{d['decode_ms_per_token_median']:.1f}",
                    va="center", fontsize=7, color="#0b0b0b", fontweight="bold")
    a1.set_xscale("log")
    a1.set_xlim(right=250)
    a1.set_xlabel(tr("minimum milliseconds per generated token (log scale)"))
    a1.set_title(tr("(a) any model that generates: time per token"), loc="left", fontsize=9)
    a1.legend(loc="upper right", fontsize=7)
    gb3 = _weight_gb(PARAMS["Qwen2.5-3B"], BITS_MLX8)
    colors = {"terse": SERIES[7], "verbose": SERIES[5]}
    for k, j in enumerate(("terse", "verbose")):
        vals = [toks[j] * gb3 / HARDWARE[n][1] for n in names]
        a2.barh(y + (k - 0.5) * h, vals, h, color=colors[j], label=f"{tr(j + ' LLM judge')} ({toks[j]:.0f} {tr('generated tokens')})")
        for yi, v in zip(y + (k - 0.5) * h, vals):
            a2.text(v * 1.05, yi, f"{v:.2f} s", va="center", fontsize=7, color=INK2)
    a2.set_xscale("log")
    a2.set_xlim(right=40)
    a2.set_xlabel(tr("minimum seconds spent writing the verdicts of one answer (log scale)"))
    a2.set_title(tr("(b) 3B LLM judge: time to write the verdicts (answers with ≥ 14 sentences)"), loc="left", fontsize=9)
    a2.legend(loc="upper right", fontsize=7)
    for ax in (a1, a2):
        ax.set_yticks(y, labels, fontsize=8)
    g.save(fig, "decode_cost_by_hardware", "Lower bounds on the cost of generating text on each class of local hardware, "
           "computed as weight bytes divided by the vendor's memory bandwidth (batch 1, KV cache ignored). (a) Time per "
           "generated token for the two GroundOne base models in 8-bit; diamonds: decode time measured on the thesis "
           "machine, about 75–85 % of the bound. (b) Minimum time a 3B LLM judge spends only on writing its "
           "verdicts for an answer of 14 or more sentences (median generated tokens of the latency protocol). A System "
           "One generates no token, so both costs are zero for it on every machine.",
           "figures/locality.py (arithmetic on vendor specs) + Phase 0 + results/judge-{terse,verbose}-3b/latency")


def memory_fit(g):
    sizes = np.logspace(np.log10(0.3e9), np.log10(800e9), 200)
    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    for bits, col, lab in [(16, NEUTRAL, tr("16-bit (training format)")), (8.5, SERIES[0], tr("8-bit (MLX, as in GroundOne)")),
                           (4.5, SERIES[2], tr("4-bit (typical local deployment)"))]:
        ax.plot(sizes / 1e9, sizes * bits / 8 / 1e9, color=col, label=lab)
    for mem in (16, 32, 64, 128, 256):
        ax.axhline(mem, color="#c8c6bf", lw=0.8, ls="--", zorder=1)
        ax.text(1.15, mem * 1.06, f"{mem} GB", fontsize=7, color=INK2)
    for name, p in [("GroundOne 0.5B", 0.494e9), ("GroundOne 3B", 3.09e9), ("7–8B generator", 7.6e9), ("70B model", 70e9)]:
        ax.axvline(p / 1e9, color="#e4e3df", lw=1, zorder=0)
        ax.text(p / 1e9 * 1.05, 1300, tr(name), rotation=90, fontsize=7, color=INK2, va="top",
                bbox=dict(facecolor=SURFACE, edgecolor="none", pad=1.0), zorder=5)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_ylim(0.1, 1600)
    ax.set_xlim(0.3, 800)
    ax.set_xlabel(tr("parameters (billions, log scale)"))
    ax.set_ylabel(tr("memory for the weights alone (GB, log scale)"))
    ax.legend(loc="lower right", fontsize=7.5)
    g.save(fig, "memory_fit", "Memory needed for the weights of a model as a function of its size and precision "
           "(parameters × bits per weight; the 8- and 4-bit lines include half a bit of per-group scales). Dashed lines "
           "mark common memory sizes of local hardware. The KV cache, activations, the operating system and any other "
           "model running at the same time come on top, so a 16 GB laptop holds a 7–8B generator in 4 bits and a small "
           "verifier, but not much more.", "figures/locality.py (arithmetic)")


def open_closed_gap(g):
    path = RAW / "Epoch AI - Open vs closed capability gap (ECI)_ingested.md"
    if not path.exists():
        return
    recs = []
    for line in path.read_text().splitlines():
        if not line.startswith("| ") or line.startswith("| Model |"):
            continue
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) < 16 or not re.match(r"\d{4}-\d{2}-\d{2}", c[5]) or not re.match(r"[\d.]+$", c[15]):
            continue
        acc = c[6]
        kind = "open" if acc.startswith("Open weights") else "closed" if acc in ("API access", "Hosted access (no API)") else None
        if kind:
            recs.append((date.fromisoformat(c[5]), kind, float(c[15])))
    if not recs:
        return
    df = pd.DataFrame(recs, columns=["date", "kind", "eci"]).sort_values("date")
    fig, ax = plt.subplots(figsize=(7.0, 3.6))
    for kind, col, lab in [("closed", SERIES[1], tr("best closed model (API)")), ("open", SERIES[0], tr("best open-weight model"))]:
        d = df[df.kind == kind].copy()
        d["best"] = d.eci.cummax()
        ax.scatter(d.date, d.eci, s=8, color=col, alpha=0.25, linewidth=0)
        ax.step(d.date, d.best, where="post", color=col, label=lab)
    ax.set_ylabel("Epoch Capabilities Index")
    ax.legend(loc="upper left")
    g.save(fig, "open_closed_gap", "Capability of the best closed and the best open-weight model over time, on Epoch AI's "
           "aggregate Epoch Capabilities Index (dots: individual models; lines: best so far). Open-weight models trail "
           "the closed frontier by a few months (about four on average in January–May 2026, according to Epoch AI).",
           "Epoch AI, open vs closed capability gap (data table, accessed 2026-10-11)")


def roofline_m4(g):
    """Roofline of the thesis machine: bandwidth roof from Apple's spec, compute level from the measured prefill."""
    d05, d3 = load_json(PHASE0 / "04_speed_qwen0.5b.json"), load_json(PHASE0 / "04_speed_qwen3b.json")
    if not (d05 and d3):
        return
    bw = 120e9
    achieved = {}
    for lab, d, n in [("0.5B", d05, PARAMS["Qwen2.5-0.5B"]), ("3B", d3, PARAMS["Qwen2.5-3B"])]:
        ms = np.median([d["table"][f"L{L}_K1"]["s1_prefill_ms"] / L for L in (500, 1000, 2000)])
        achieved[lab] = 2 * n / (ms / 1000)
    peak = max(achieved.values())

    def intensity(n, din, dout, wbytes=1.0, abytes=2.0):  # FLOPs per byte of one linear layer, n tokens at once
        return 2 * n * din * dout / (wbytes * din * dout + abytes * n * (din + dout))

    x = np.logspace(-0.3, 3.3, 300)
    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    ax.plot(x, np.minimum(bw * x, peak) / 1e12, color="#0b0b0b", lw=2)
    ax.text(0.7, bw * 0.7 / 1e12 * 2.6, tr("bandwidth roof: 120 GB/s × intensity"), rotation=33, fontsize=7.5, color=INK2)
    ax.text(150, peak / 1e12 * 1.12, f"{tr('compute reached in prefill')} ≈ {peak / 1e12:.1f} TFLOP/s {tr('(lower bound of the peak)')}",
            fontsize=7.5, color=INK2, ha="center")
    pts = [(tr("decode, 1 token\n(both models)"), intensity(1, 2048, 11008), SERIES[7], (1.3, 0.45), "left"),
           (tr("prefill, 500 tokens\n(0.5B, FFN layer)"), intensity(500, 896, 4864), SERIES[0], (0.8, 0.4), "right"),
           (tr("prefill, 1,000 tokens\n(3B, FFN layer)"), intensity(1000, 2048, 11008), SERIES[6], (1.0, 0.2), "center")]
    for lab, i, col, (fx, fy), ha in pts:
        y = min(bw * i, peak) / 1e12
        ax.scatter(i, y, s=60, color=col, zorder=4, edgecolor="white", linewidth=1.2)
        ax.annotate(lab, (i, y), xytext=(i * fx, y * fy), fontsize=7.5, color=INK2, ha=ha,
                    arrowprops=dict(arrowstyle="-", color="#c8c6bf", lw=0.8))
    ax.axvline(peak / bw, color="#c8c6bf", ls="--", lw=1)
    ax.text(peak / bw * 1.08, 0.012, f"{tr('ridge')} ≈ {peak / bw:.0f} FLOP/byte", fontsize=7, color=INK2)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_ylim(0.01, 8)
    ax.set_xlabel(tr("arithmetic intensity (FLOPs per byte read from memory, log scale)"))
    ax.set_ylabel(tr("attainable throughput (TFLOP/s, log scale)"))
    g.save(fig, "roofline_m4", "Roofline model of the thesis machine. The sloped roof is Apple's memory bandwidth (120 "
           "GB/s); Apple publishes no peak compute figure, so the flat roof is the throughput actually reached during "
           "prefill (2 FLOPs per parameter per token divided by the measured time per token), a lower bound of the "
           "peak. Generating one token reads every weight for about 2 FLOPs per byte and sits deep on the bandwidth "
           "roof; reading hundreds of tokens at once reuses each weight and reaches the compute roof. Intensities are "
           "computed for one feed-forward layer of Qwen2.5 with 8-bit weights and 16-bit activations; attention is "
           "ignored.", "Williams et al. 2009 (model) + Phase 0 timings + Qwen2.5 layer shapes")


def aa_snapshot(g):
    """Snapshot of the Artificial Analysis Intelligence Index (2026-10-20): open-weight vs closed models."""
    path = RAW / "Artificial Analysis 2026 - Intelligence Index snapshot (2026-10-20)_ingested.md"
    if not path.exists():
        path = RAW / "Artificial Analysis 2026 - Intelligence Index snapshot (2026-10-20).md"
    if not path.exists():
        return
    rows = []
    for line in path.read_text().splitlines():
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) == 6 and re.match(r"[\d.]+$", c[2]):
            rows.append((c[0], float(c[1]), c[3] == "yes", c[4]))  # chart value, as published
    rows.sort(key=lambda r: r[1])
    fig, ax = plt.subplots(figsize=(7.2, 6.6))
    y = np.arange(len(rows))
    cols = [SERIES[0] if r[2] else SERIES[1] for r in rows]
    bars = ax.barh(y, [r[1] for r in rows], color=cols, height=0.72)
    for b, r in zip(bars, rows):
        ax.text(b.get_width() + 0.4, b.get_y() + b.get_height() / 2, f"{r[1]:.0f}", va="center", fontsize=7, color=INK2)
        if r[3] == "small":
            b.set_hatch("////")
            b.set_edgecolor("white")
    ax.set_yticks(y, [r[0] for r in rows], fontsize=7)
    best_c = max(r[1] for r in rows if not r[2])
    best_o = max(r[1] for r in rows if r[2])
    top = len(rows) - 0.3
    for v in (best_c, best_o):
        ax.plot([v, v], [top, top + 0.9], color=INK2, lw=0.8)
    ax.annotate("", xy=(best_c, top + 0.6), xytext=(best_o, top + 0.6),
                arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.8), annotation_clip=False)
    ax.text(best_o - 0.8, top + 0.6, tr("gap between the best closed and the best open-weight model:")
            + f" {best_c - best_o:.0f}", ha="right", va="center", fontsize=7, color=INK2)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=SERIES[1], label=tr("closed")), Patch(color=SERIES[0], label=tr("open-weight")),
                       Patch(facecolor=SERIES[0], hatch="////", edgecolor="white", label=tr("open-weight, small class"))],
              loc="lower right", fontsize=7)
    ax.set_xlim(0, 66)
    ax.set_ylim(-0.7, len(rows) + 0.9)
    ax.set_xlabel(tr("Artificial Analysis Intelligence Index v4.3.2"))
    ax.grid(axis="y", visible=False)
    g.save(fig, "aa_intelligence_snapshot", f"Artificial Analysis Intelligence Index on 2026-10-20 (v4.3.2, 10 evaluations), "
           f"redrawn from the published chart; open-weight status from the leaderboard data. Best closed model "
           f"{best_c:.0f}, best open-weight model {best_o:.0f}.", "Artificial Analysis leaderboard, accessed 2026-10-20")


def main():
    global LANG
    for lang, group, title in (("en", "locality", "Local inference (Ch. 2)"), ("it", "locality_it", "Inferenza locale (Cap. 2)")):
        LANG = lang
        g = Group(group)
        for f in (prefill_vs_decode, roofline_m4, hardware_landscape, decode_cost_by_hardware, memory_fit, open_closed_gap,
                  aa_snapshot):
            f(g)
        g.write_index(title)
    LANG = "en"
