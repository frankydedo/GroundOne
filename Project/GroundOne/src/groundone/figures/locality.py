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
from .style import INK2, NEUTRAL, SERIES, Group, load_json, plt

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
    ax.bar(x - w / 2, [r[1] for r in rows], w, color=SERIES[0], label="reading a prompt token (prefill)")
    ax.bar(x + w / 2, [r[2] for r in rows], w, color=SERIES[7], label="writing an output token (decode)")
    for i, (lab, p, dcd) in enumerate(rows):
        ax.text(i - w / 2, p * 1.08, f"{p:.2f}", ha="center", va="bottom", fontsize=8, color=INK2)
        ax.text(i + w / 2, dcd * 1.08, f"{dcd:.1f}", ha="center", va="bottom", fontsize=8, color=INK2)
        ax.text(i, dcd * 2.3, f"{dcd / p:.0f}× per token", ha="center", fontsize=9, fontweight="bold")
    ax.set_yscale("log")
    ax.set_ylim(0.1, 200)
    ax.set_xticks(x, [r[0] for r in rows])
    ax.set_ylabel("milliseconds per token (log scale)")
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
        ax.annotate(name.replace("\n", " "), (mem, bw), xytext=(mem * dx, bw * dy), fontsize=7.5, ha=ha, va="center",
                    color="#0b0b0b" if name == THESIS else INK2, fontweight="bold" if name == THESIS else "normal")
    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    ax.set_xticks([16, 32, 64, 128, 256], ["16", "32", "64", "128", "256"])
    ax.set_yticks([100, 200, 400, 800, 1600], ["100", "200", "400", "800", "1,600"])
    ax.set_xlim(11, 400)
    ax.set_ylim(90, 2600)
    ax.set_xlabel("memory available to the model (GB, log scale)  →  which models fit")
    ax.set_ylabel("memory bandwidth (GB/s, log scale)\n→  how fast tokens are generated")
    for kind, lab in [("unified", "unified memory (shared by CPU and GPU)"), ("discrete", "discrete GPU memory (VRAM)")]:
        ax.scatter([], [], color=KIND_COLOR[kind], marker="o" if kind == "unified" else "s", label=lab)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, fontsize=8)
    g.save(fig, "hardware_landscape", "Local inference hardware on the two axes that decide what can run: memory capacity "
           "(which models fit) and memory bandwidth (how fast tokens can be generated). Discrete GPUs have the highest "
           "bandwidth but at most 32 GB; unified-memory machines trade bandwidth for capacity. Values are the vendors' "
           "published specifications (Apple, NVIDIA spec pages, accessed 2026-10-11): the marker is the largest memory "
           "configuration at that bandwidth, the shaded bar the range of memory sizes offered; the thesis machine is "
           "shown at its actual 16 GB.", "figures/locality.py HARDWARE (vendor spec pages in Vault/raw/local_inference)")


def decode_floor(g):
    """Lower bound on time per generated token = weight bytes / bandwidth (batch 1)."""
    names = sorted(HARDWARE, key=lambda n: HARDWARE[n][1])
    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    y = np.arange(len(names))
    h = 0.38
    meas = {"Qwen2.5-0.5B": load_json(PHASE0 / "04_speed_qwen0.5b.json"), "Qwen2.5-3B": load_json(PHASE0 / "04_speed_qwen3b.json")}
    i = names.index(THESIS)
    for j, (model, params) in enumerate(PARAMS.items()):
        gb = _weight_gb(params, BITS_MLX8)
        vals = [gb / HARDWARE[n][1] * 1000 for n in names]
        ax.barh(y + (j - 0.5) * h, vals, h, color=[SERIES[0], SERIES[6]][j], label=f"{model}, 8-bit ({gb:.2f} GB of weights)")
        for k, (yi, v) in enumerate(zip(y + (j - 0.5) * h, vals)):
            xl = max(v, meas[model]["decode_ms_per_token_median"] * 1.1) if (k == i and meas[model]) else v
            ax.text(xl * 1.05, yi, f"{v:.1f}" if v >= 1 else f"{v:.2f}", va="center", fontsize=7, color=INK2)
    for j, (model, d) in enumerate(meas.items()):
        if d:
            ax.scatter(d["decode_ms_per_token_median"], i + (j - 0.5) * h, marker="D", color="#0b0b0b", s=22, zorder=4,
                       label="measured on the M4 (Phase 0)" if j == 0 else None)
    ax.set_xscale("log")
    ax.set_xlim(right=60)
    ax.set_yticks(y, [n.replace("\n", " ") for n in names], fontsize=8)
    ax.set_xlabel("minimum milliseconds per generated token (log scale)")
    ax.legend(loc="lower center", bbox_to_anchor=(0.4, 1.0), ncol=2, fontsize=7.5)
    g.save(fig, "decode_floor_by_hardware", "Lower bound on the time to generate one token with the two GroundOne base "
           "models, computed as weight bytes divided by the vendor's memory bandwidth (batch 1, weights read once per "
           "token, KV cache ignored). Diamonds: decode time measured on the thesis machine, which reaches about 75–85 % "
           "of the bound. No hardware removes this cost for a model that generates; a System One does not pay it.",
           "figures/locality.py (arithmetic on vendor specs) + experiments/feasibility/results/04_speed_*.json")


def judge_decode_overhead(g):
    """Seconds a generative judge spends only on decoding a long answer's verdicts, lower bound per hardware."""
    toks = {}
    for j in ("terse", "verbose"):
        p = RESULTS_DIR / f"judge-{j}-3b" / "latency" / "predictions.parquet"
        if not p.exists():
            return
        x = pd.read_parquet(p).drop_duplicates("rid")
        toks[j] = float(x[x.K >= 14].generated_tokens.median())
    gb = _weight_gb(PARAMS["Qwen2.5-3B"], BITS_MLX8)
    names = sorted(HARDWARE, key=lambda n: HARDWARE[n][1])
    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    y = np.arange(len(names))
    h = 0.38
    colors = {"terse": SERIES[7], "verbose": SERIES[5]}
    for k, j in enumerate(("terse", "verbose")):
        vals = [toks[j] * gb / HARDWARE[n][1] for n in names]
        ax.barh(y + (k - 0.5) * h, vals, h, color=colors[j], label=f"{j} judge ({toks[j]:.0f} generated tokens)")
        for yi, v in zip(y + (k - 0.5) * h, vals):
            ax.text(v * 1.05, yi, f"{v:.2f} s", va="center", fontsize=7, color=INK2)
    ax.set_xscale("log")
    ax.set_yticks(y, [n.replace("\n", " ") for n in names], fontsize=8)
    ax.set_xlabel("minimum seconds spent decoding per answer (log scale)")
    ax.legend(loc="lower center", bbox_to_anchor=(0.4, 1.0), ncol=2, fontsize=7.5)
    g.save(fig, "judge_decode_overhead_by_hardware", "Minimum time that a 3B generative judge spends only on writing its "
           "verdicts for one long answer (14 or more sentences), on each class of hardware: median generated tokens "
           "measured in the latency protocol (terse and verbose judges) times weight bytes divided by bandwidth. This is "
           "a floor on top of the prefill, which both the judge and a System One pay; a System One generates no token, "
           "so this term is zero for it on every machine.",
           "results/judge-{terse,verbose}-3b/latency/predictions.parquet + vendor specs")


def memory_fit(g):
    sizes = np.logspace(np.log10(0.3e9), np.log10(800e9), 200)
    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    for bits, col, lab in [(16, NEUTRAL, "16-bit (training format)"), (8.5, SERIES[0], "8-bit (MLX, as in GroundOne)"),
                           (4.5, SERIES[2], "4-bit (typical local deployment)")]:
        ax.plot(sizes / 1e9, sizes * bits / 8 / 1e9, color=col, label=lab)
    for mem in (16, 32, 64, 128, 256):
        ax.axhline(mem, color="#c8c6bf", lw=0.8, ls="--", zorder=1)
        ax.text(1.15, mem * 1.06, f"{mem} GB", fontsize=7, color=INK2)
    for name, p in [("GroundOne 0.5B", 0.494e9), ("GroundOne 3B", 3.09e9), ("7–8B generator", 7.6e9), ("70B model", 70e9)]:
        ax.axvline(p / 1e9, color="#e4e3df", lw=1, zorder=0)
        ax.text(p / 1e9 * 1.05, 1300, name, rotation=90, fontsize=7, color=INK2, va="top")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_ylim(0.1, 1600)
    ax.set_xlim(0.3, 800)
    ax.set_xlabel("parameters (billions, log scale)")
    ax.set_ylabel("memory for the weights alone (GB, log scale)")
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
    for kind, col, lab in [("closed", SERIES[1], "best closed model (API)"), ("open", SERIES[0], "best open-weight model")]:
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
    ax.text(0.7, bw * 0.7 / 1e12 * 2.6, "bandwidth roof: 120 GB/s × intensity", rotation=33, fontsize=7.5, color=INK2)
    ax.text(150, peak / 1e12 * 1.12, f"compute reached in prefill ≈ {peak / 1e12:.1f} TFLOP/s (lower bound of the peak)",
            fontsize=7.5, color=INK2, ha="center")
    pts = [("decode, 1 token\n(both models)", intensity(1, 2048, 11008), SERIES[7], (1.3, 0.45), "left"),
           ("prefill, 500 tokens\n(0.5B, FFN layer)", intensity(500, 896, 4864), SERIES[0], (0.8, 0.4), "right"),
           ("prefill, 1,000 tokens\n(3B, FFN layer)", intensity(1000, 2048, 11008), SERIES[6], (1.0, 0.2), "center")]
    for lab, i, col, (fx, fy), ha in pts:
        y = min(bw * i, peak) / 1e12
        ax.scatter(i, y, s=60, color=col, zorder=4, edgecolor="white", linewidth=1.2)
        ax.annotate(lab, (i, y), xytext=(i * fx, y * fy), fontsize=7.5, color=INK2, ha=ha,
                    arrowprops=dict(arrowstyle="-", color="#c8c6bf", lw=0.8))
    ax.axvline(peak / bw, color="#c8c6bf", ls="--", lw=1)
    ax.text(peak / bw * 1.08, 0.012, f"ridge ≈ {peak / bw:.0f} FLOP/byte", fontsize=7, color=INK2)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_ylim(0.01, 8)
    ax.set_xlabel("arithmetic intensity (FLOPs per byte read from memory, log scale)")
    ax.set_ylabel("attainable throughput (TFLOP/s, log scale)")
    g.save(fig, "roofline_m4", "Roofline model of the thesis machine. The sloped roof is Apple's memory bandwidth (120 "
           "GB/s); Apple publishes no peak compute figure, so the flat roof is the throughput actually reached during "
           "prefill (2 FLOPs per parameter per token divided by the measured time per token), a lower bound of the "
           "peak. Generating one token reads every weight for about 2 FLOPs per byte and sits deep on the bandwidth "
           "roof; reading hundreds of tokens at once reuses each weight and reaches the compute roof. Intensities are "
           "computed for one feed-forward layer of Qwen2.5 with 8-bit weights and 16-bit activations; attention is "
           "ignored.", "Williams et al. 2009 (model) + Phase 0 timings + Qwen2.5 layer shapes")


def main():
    g = Group("locality")
    for f in (prefill_vs_decode, roofline_m4, hardware_landscape, decode_floor, judge_decode_overhead, memory_fit, open_closed_gap):
        f(g)
    g.write_index("Local inference (Ch. 2)")
