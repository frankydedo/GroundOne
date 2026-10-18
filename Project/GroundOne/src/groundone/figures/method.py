"""Method-chapter figures (Ch. 4): analytic cost model of one verification, System One vs generative judges.

Uses only measured constants: prefill and decode time per token on the M4 (Phase 0) and the mean number of tokens a
judge generates per verdict on the latency subset (generated tokens per answer / mean K). Usage: groundone figures method
"""
import json

import numpy as np

from ..config import RESULTS_DIR
from .style import SERIES, Group, plt

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


def main():
    g = Group("method")
    cost_model(g)
    g.write_index("Method (Ch. 4)")
