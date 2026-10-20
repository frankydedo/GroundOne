"""Method-chapter figures (Ch. 4): analytic cost model of one verification, System One vs generative judges.

Uses only measured constants: prefill and decode time per token on the M4 (Phase 0) and the mean number of tokens a
judge generates per verdict on the latency subset (generated tokens per answer / mean K). Usage: groundone figures method
"""
import json

import numpy as np

from ..config import RESULTS_DIR
from .style import INK2, NEUTRAL, SERIES, Group, plt

T_PRE = {"0.5B": 0.37e-3, "3B": 2.2e-3}   # s per prompt token (prefill), Phase 0
T_DEC = {"0.5B": 5.9e-3, "3B": 31.8e-3}   # s per generated token (decode), Phase 0
MARKER = 3                                 # tokens of " Verdict:"
S = 800                                    # document + answer tokens (median prompt length is about 770)
GEN_TOKENS = {("0.5B", "terse"): 57, ("0.5B", "verbose"): 252, ("3B", "terse"): 36, ("3B", "verbose"): 248}  # per answer, latency subset


def cost_model(g):
    lat = json.loads((RESULTS_DIR / "g1-05b-b1" / "latency" / "metrics.json").read_text())
    mean_k = lat["decisions"] / lat["answers"]
    K = np.arange(1, 31)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6), sharey=False)
    for ax, size in zip(axes, ("0.5B", "3B")):
        s1 = (S + MARKER * K) * T_PRE[size]
        ax.plot(K, s1, color=SERIES[0], label="System One: prefill of S + 3K tokens")
        for kind, col in (("terse", SERIES[7]), ("verbose", SERIES[5])):
            n = GEN_TOKENS[(size, kind)] / mean_k
            ax.plot(K, S * T_PRE[size] + K * n * T_DEC[size], color=col,
                    label=f"{kind} judge: prefill of S + K × {n:.1f} generated tokens")
        ax.set_ylim(bottom=0)
        ax.set_title(f"Qwen2.5 {size}")
        ax.set_xlabel("K = decisions per answer")
        ax.legend(fontsize=7, loc="upper left")
    axes[0].set_ylabel("seconds per answer (model)")
    g.save(fig, "cost_model", f"Analytic cost of verifying one answer of S = {S} tokens as a function of K, from measured "
           f"constants only: prefill and decode time per token on the M4 and the mean number of tokens each judge "
           f"generates per verdict on the latency subset (mean K = {mean_k:.1f}). Not a measurement; the measured "
           f"latencies are in Ch. 7.", "Phase 0 timings + results/*/latency/metrics.json")


def roc_explainer(g):
    """Schematic (synthetic scores): how the ROC curve and the AUROC arise from the scores of two classes."""
    from scipy.stats import norm
    rng = np.random.default_rng(0)
    pos = 1 / (1 + np.exp(-rng.normal(1.6, 1.1, 4000)))   # supported sentences: high P(supported)
    neg = 1 / (1 + np.exp(-rng.normal(-0.6, 1.1, 1500)))  # not supported: lower, overlapping
    thr = 0.6
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.7))
    ax = axes[0]
    bins = np.linspace(0, 1, 41)
    ax.hist(pos, bins, density=True, alpha=0.6, color=SERIES[0], label="supported")
    ax.hist(neg, bins, density=True, alpha=0.6, color=SERIES[1], label="not supported")
    ax.axvline(thr, color="black", lw=1.2, ls="--")
    ax.text(thr + 0.01, ax.get_ylim()[1] * 0.92, f"threshold {thr}", fontsize=8)
    ax.set_xlabel("score P(supported)")
    ax.set_ylabel("density")
    ax.set_title("(a) scores of the two classes")
    ax.legend(fontsize=8, loc="upper left")
    ax = axes[1]
    ts = np.linspace(1, 0, 201)
    tpr = np.array([(pos >= t).mean() for t in ts])
    fpr = np.array([(neg >= t).mean() for t in ts])
    auc = np.trapezoid(tpr, fpr)
    ax.fill_between(fpr, tpr, color=SERIES[0], alpha=0.15)
    ax.plot(fpr, tpr, color=SERIES[0], lw=2)
    ax.plot([0, 1], [0, 1], color=NEUTRAL, ls="--", lw=1)
    ax.text(0.62, 0.42, "random scores\n(AUROC 0.5)", fontsize=8, color=INK2)
    px, py = (neg >= thr).mean(), (pos >= thr).mean()
    ax.plot(px, py, "o", color="black", ms=6)
    ax.annotate(f"threshold {thr}", (px, py), xytext=(px + 0.08, py - 0.12), fontsize=8, arrowprops=dict(arrowstyle="-", lw=0.8))
    ax.text(0.45, 0.18, f"area = AUROC = {auc:.2f}", fontsize=9, color=SERIES[0])
    ax.set_xlabel("false positive rate (not supported accepted)")
    ax.set_ylabel("true positive rate (supported accepted)")
    ax.set_title("(b) ROC curve: every threshold at once")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.02)
    g.save(fig, "roc_explainer", "Schematic with synthetic scores. (a) Distribution of P(supported) for supported and not "
           "supported sentences, with one threshold. (b) Moving the threshold from 1 to 0 traces the ROC curve; the dot is "
           "the threshold of panel (a); the area under the curve is the AUROC.", "synthetic data")


def main():
    g = Group("method")
    cost_model(g)
    roc_explainer(g)
    g.write_index("Method (Ch. 4)")
