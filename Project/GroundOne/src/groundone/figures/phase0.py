"""Figures of the feasibility study (Phase 0 / 0b), from Project/phase0/results/."""
import numpy as np
import pandas as pd

from ..config import PROJECT
from .style import NEUTRAL, SYSTEM_COLORS as C, Group, bar_labels, load_json, plt

R = PROJECT / "phase0" / "results"
MODELS = {"qwen0.5b": "0.5B", "qwen3b": "3B"}


def speed_vs_k(g):
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.4), sharey=False)
    for ax, (k, lab) in zip(axes, MODELS.items()):
        d = load_json(R / f"06_speed_batched_{k}.json")
        if not d:
            continue
        t = d["table"]
        ks = [1, 3, 8, 24]
        rows = [t[f"L1000_K{x}"] for x in ks]
        for key, name in [("s1_batched_ms", "System One (batched)"), ("terse_ms", "Terse judge"), ("verbose_ms", "Verbose judge")]:
            ax.plot(ks, [r[key] / 1000 for r in rows], marker="o", color=C[name], label=name)
        ax.set_xscale("log", base=2)
        ax.set_xticks(ks, [str(x) for x in ks])
        ax.set_title(f"Qwen2.5-{lab}, 1,000-token context")
        ax.set_xlabel("decisions per context (K)")
        ax.set_ylabel("time per answer (s)")
    axes[0].legend()
    g.save(fig, "p0b_latency_vs_K", "Time to verify one answer as the number of decisions K over the same 1,000-token "
           "context grows (untrained models, M4 16 GB, MLX 8-bit). The System One scores all K questions in one batched "
           "pass after a single prefill; generative judges decode their verdicts token by token.",
           "phase0/results/06_speed_batched_*.json")


def gain_vs_k(g):
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.4), sharey=True)
    shades = {500: "#9ec5f0", 1000: "#2a78d6", 2000: "#16447a"}
    for ax, (k, lab) in zip(axes, MODELS.items()):
        d = load_json(R / f"06_speed_batched_{k}.json")
        if not d:
            continue
        for L in (500, 1000, 2000):
            ks = [1, 3, 8, 24]
            ax.plot(ks, [d["table"][f"L{L}_K{x}"]["gain_vs_terse"] for x in ks], marker="o", color=shades[L], label=f"{L} tokens")
        ax.axhline(1, color=NEUTRAL, lw=1, ls="--")
        ax.set_xscale("log", base=2)
        ax.set_xticks([1, 3, 8, 24], ["1", "3", "8", "24"])
        ax.set_title(f"Qwen2.5-{lab}")
        ax.set_xlabel("decisions per context (K)")
    axes[0].set_ylabel("speed-up vs terse judge (×)")
    axes[0].legend(title="context length")
    g.save(fig, "p0b_speedup_vs_K_by_context", "Speed-up of the batched System One over a terse generative judge as a "
           "function of K, for three context lengths. The gain grows with K and shrinks with context length, because "
           "prefill is paid by both methods. Dashed line: no gain.", "phase0/results/06_speed_batched_*.json")


def batching_matters(g):
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.4))
    for ax, (k, lab) in zip(axes, MODELS.items()):
        a, b = load_json(R / f"04_speed_{k}.json"), load_json(R / f"06_speed_batched_{k}.json")
        if not (a and b):
            continue
        ks = [1, 3, 8]
        ax.plot(ks, [a["table"][f"L1000_K{x}"]["s1_fresh_ms"] / 1000 for x in ks], marker="o", color=NEUTRAL, label="one full pass per question")
        ax.plot(ks, [a["table"][f"L1000_K{x}"]["s1_shared_ms"] / 1000 for x in ks], marker="o", color=C["System One (sequential)"], label="shared prefix, sequential suffixes")
        ax.plot(ks, [b["table"][f"L1000_K{x}"]["s1_batched_ms"] / 1000 for x in ks], marker="o", color=C["System One (batched)"], label="shared prefix, batched suffixes")
        ax.set_title(f"Qwen2.5-{lab}, 1,000-token context")
        ax.set_xlabel("decisions per context (K)")
        ax.set_ylabel("time per answer (s)")
        ax.set_xticks(ks)
    axes[0].legend()
    g.save(fig, "p0_system_one_variants", "Three ways of computing K System One decisions over one context. Reusing the "
           "prefix is essential; batching the short suffixes removes most of the remaining cost (Phase 0 vs Phase 0b).",
           "phase0/results/04_speed_*.json, 06_speed_batched_*.json")


def zero_shot_accuracy(g):
    sets = [("aggrefact", "LLM-AggreFact"), ("rt_sent", "RAGTruth sentences"), ("anli", "ANLI dev")]
    systems = [("Untrained 0.5B", R / "02_readout_qwen0.5b.json"), ("Untrained 3B", R / "02_readout_qwen3b.json"),
               ("MiniCheck-RoBERTa", R / "03_minicheck-roberta.json")]
    data = {n: load_json(p) for n, p in systems}
    for metric, stem, ylab, cap in [
        ("bacc@0.5", "p0_zero_shot_bacc", "balanced accuracy", "Zero-shot balanced accuracy (threshold 0.5) of the untrained "
         "Qwen2.5 System One readout and of MiniCheck-RoBERTa on the same 1,780 evaluation items (Phase 0 sample)."),
        ("ece15", "p0_zero_shot_ece", "ECE (lower is better)", "Expected calibration error (15 bins) on the same items: the "
         "untrained Qwen probabilities are poorly calibrated.")]:
        fig, ax = plt.subplots(figsize=(7, 3.2))
        x = np.arange(len(sets))
        w = 0.26
        for i, (n, _) in enumerate(systems):
            if not data[n]:
                continue
            bars = ax.bar(x + (i - 1) * w, [data[n][s][metric] for s, _ in sets], w - 0.02, color=C[n], label=n)
            bar_labels(ax, bars)
        ax.set_xticks(x, [l for _, l in sets])
        ax.set_ylabel(ylab)
        if metric.startswith("bacc"):
            ax.axhline(0.5, color=NEUTRAL, lw=1, ls="--")
            ax.set_ylim(0.4, 0.9)
        ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.18))
        g.save(fig, stem, cap, "phase0/results/02_readout_*.json, 03_minicheck-roberta.json")


def generative_judges(g):
    rows = []
    for k, lab in MODELS.items():
        d = load_json(R / f"08_gen_judges_{k}.json")
        r = load_json(R / f"02_readout_{k}.json")
        if d:
            rows += [(lab, "Terse judge", d["terse"]["bacc"], d["terse"]["format_failure_rate"]),
                     (lab, "Verbose judge", d["verbose"]["bacc"], d["verbose"]["format_failure_rate"])]
        if r:
            rows.append((lab, "System One (batched)", r["rt_sent"]["bacc@0.5"], 0.0))
    if not rows:
        return
    df = pd.DataFrame(rows, columns=["model", "system", "bacc", "fail"])
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.2))
    for ax, col, ylab in [(axes[0], "fail", "format failure rate"), (axes[1], "bacc", "balanced accuracy")]:
        x = np.arange(2)
        for i, s in enumerate(["System One (batched)", "Terse judge", "Verbose judge"]):
            vals = [df[(df.model == m) & (df.system == s)][col].mean() for m in ("0.5B", "3B")]
            bars = ax.bar(x + (i - 1) * 0.26, vals, 0.24, color=C[s], label=s.replace(" (batched)", " readout"))
            bar_labels(ax, bars)
        ax.set_xticks(x, ["Qwen2.5-0.5B", "Qwen2.5-3B"])
        ax.set_ylabel(ylab)
    axes[1].set_ylim(0.4, 0.8)
    axes[0].legend()
    g.save(fig, "p0b_generative_judges", "Generative judges vs System One readout on 630 RAGTruth sentences (untrained "
           "models). Left: share of verdicts that could not be parsed. Right: balanced accuracy. The System One returns a "
           "valid answer by construction.", "phase0/results/08_gen_judges_*.json, 02_readout_*.json")


def flexibility(g):
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.2))
    for ax, s, title in [(axes[0], "anli", "ANLI dev"), (axes[1], "rt_sent", "RAGTruth sentences")]:
        groups = ["three-way\n(macro recall)", "strict rule", "lenient rule"]
        x = np.arange(3)
        for i, (k, lab, name) in enumerate([("qwen0.5b", "0.5B", "Untrained 0.5B"), ("qwen3b", "3B", "Untrained 3B")]):
            d = load_json(R / f"07_flex_{k}.json")
            if not d:
                continue
            v = [d[s]["threeway_macro_recall"], d[s]["strict_rule"]["qwen_bacc"], d[s]["lenient_rule"]["qwen_bacc"]]
            bars = ax.bar(x + (i - 1) * 0.26, v, 0.24, color=C[name], label=name)
            bar_labels(ax, bars)
        d = load_json(R / "07_flex_qwen3b.json")
        if d:
            bars = ax.bar(x[1:] + 0.26, [d[s]["strict_rule"]["minicheck_bacc"], d[s]["lenient_rule"]["minicheck_bacc"]], 0.24,
                          color=C["MiniCheck-RoBERTa"], label="MiniCheck-RoBERTa (one fixed score)")
            bar_labels(ax, bars)
        ax.set_xticks(x, groups)
        ax.set_title(title)
        ax.set_ylim(0.2, 0.85)
    axes[0].set_ylabel("balanced accuracy / macro recall")
    axes[0].legend(fontsize=7)
    g.save(fig, "p0b_flexibility_zero_shot", "Zero-shot flexibility probe: three-way question and verification rules "
           "written in the prompt. Untrained models do not follow the rules (≈ 0.5); MiniCheck cannot receive a rule, so "
           "its single score is evaluated against each rule's labels. Chance: 0.33 (three-way), 0.5 (rules).",
           "phase0/results/07_flex_*.json")


def training_probe(g):
    rows = []
    for k, lab in MODELS.items():
        for n in (1024, 2048):
            d = load_json(R / f"05_train_probe_{k}_{n}.json")
            if d and d.get("peak_mem_gb"):
                rows.append((lab, n, d["peak_mem_gb"], d["sec_per_step_median"]))
    if not rows:
        return
    df = pd.DataFrame(rows, columns=["model", "tokens", "mem", "sec"])
    fig, axes = plt.subplots(1, 2, figsize=(8, 3))
    for ax, col, ylab in [(axes[0], "mem", "peak memory (GB)"), (axes[1], "sec", "seconds per step (batch 1)")]:
        x = np.arange(2)
        for i, (m, name) in enumerate([("0.5B", "Untrained 0.5B"), ("3B", "Untrained 3B")]):
            bars = ax.bar(x + (i - 0.5) * 0.36, [df[(df.model == m) & (df.tokens == n)][col].mean() for n in (1024, 2048)],
                          0.34, color=[C["GroundOne 0.5B"], C["GroundOne 3B"]][i], label=f"Qwen2.5-{m}")
            bar_labels(ax, bars, "{:.1f}")
        ax.set_xticks(x, ["1,024 tokens", "2,048 tokens"])
        ax.set_ylabel(ylab)
    axes[0].legend()
    g.save(fig, "p0_training_probe", "LoRA training probe on the M4 16 GB (all linear layers, gradient checkpointing, "
           "restricted answer-letter loss): peak memory and time per step at two example lengths.",
           "phase0/results/05_train_probe_*.json")


def main():
    g = Group("phase0")
    for f in (speed_vs_k, gain_vs_k, batching_matters, zero_shot_accuracy, generative_judges, flexibility, training_probe):
        f(g)
    g.write_index("Phase 0 / 0b figures (feasibility)")
