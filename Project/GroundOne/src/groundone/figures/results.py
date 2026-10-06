"""Results figures: all systems evaluated so far (results/<name>/<suite>/metrics.json), compared per test set."""
import json

import numpy as np

from ..config import RESULTS_DIR
from .style import NEUTRAL, SYSTEM_COLORS as C, Group, bar_labels, plt

# results folder -> display name (entity colour from style.SYSTEM_COLORS); add new systems here
NAMES = {"base-05b": "Untrained 0.5B", "base-3b": "Untrained 3B", "g1-05b-v1": "GroundOne 0.5B", "g1-3b-v1": "GroundOne 3B",
         "minicheck-roberta": "MiniCheck-RoBERTa", "minicheck-deberta": "MiniCheck-DeBERTa", "hhem": "HHEM",
         "rizzo-flow-4b-q4": "Rizzo-Flow 4B"}


def collect(suite):
    out = {}
    for folder, name in NAMES.items():
        p = RESULTS_DIR / folder / suite / "metrics.json"
        if p.exists():
            out[name] = json.loads(p.read_text())
    return out


def anli_rules(g):
    data = collect("anli")
    if not data:
        return
    qs = [("sup", "supported?"), ("strict", "strict rule"), ("lenient", "lenient rule"), ("three", "three-way\n(macro recall)")]
    fig, ax = plt.subplots(figsize=(9, 3.4))
    x = np.arange(len(qs))
    w = 0.8 / len(data)
    for i, (name, m) in enumerate(data.items()):
        bq = m["by_question"]
        vals = []
        for q, _ in qs:
            v = bq.get(q)
            if v is None:
                vals.append(np.nan)
            else:
                v = v.get("all", v)
                vals.append(v.get("bacc", v.get("macro_recall", np.nan)))
        bars = ax.bar(x - 0.4 + w * (i + 0.5), vals, w * 0.92, color=C.get(name, NEUTRAL), label=name)
        bar_labels(ax, bars)
    ax.set_xticks(x, [l for _, l in qs])
    ax.set_ylabel("balanced accuracy / macro recall")
    ax.set_ylim(0.2, 0.95)
    ax.legend(ncol=3, fontsize=7, loc="upper center", bbox_to_anchor=(0.5, 1.22))
    g.save(fig, "anli_questions_and_rules", "ANLI test: the binary question, the two verification rules and the three-way "
           "question. Encoders produce one fixed score, evaluated against each rule's labels (no bar for three-way). "
           "Rizzo-Flow is measured on a 600-item subsample.", "results/*/anli/metrics.json")


def ragtruth_binary(g):
    data = collect("ragtruth")
    if not data:
        return
    tasks = ["all", "QA", "Summary", "Data2txt"]
    fig, ax = plt.subplots(figsize=(9, 3.4))
    x = np.arange(len(tasks))
    w = 0.8 / len(data)
    for i, (name, m) in enumerate(data.items()):
        sup = m.get("sup") or m.get("by_question", {}).get("sup", {})
        vals = [sup.get(t, {}).get("bacc", np.nan) for t in tasks]
        bars = ax.bar(x - 0.4 + w * (i + 0.5), vals, w * 0.92, color=C.get(name, NEUTRAL), label=name)
        bar_labels(ax, bars)
    ax.set_xticks(x, ["all tasks", "QA", "Summary", "Data-to-text"])
    ax.set_ylabel("balanced accuracy (supported?)")
    ax.set_ylim(0.3, 1.0)
    ax.axhline(0.5, color=NEUTRAL, lw=1, ls="--")
    ax.legend(ncol=3, fontsize=7, loc="upper center", bbox_to_anchor=(0.5, 1.22))
    g.save(fig, "ragtruth_supported_by_task", "RAGTruth test, sentence level, binary question, by task (our span-derived "
           "labels, all sentences). Rizzo-Flow on a 200-answer subsample.", "results/*/ragtruth/metrics.json")


def aggrefact(g):
    data = collect("aggrefact")
    if not data:
        return
    dsets = sorted({d for m in data.values() for d in m["per_dataset"]})
    fig, ax = plt.subplots(figsize=(10, 3.6))
    x = np.arange(len(dsets) + 2)
    w = 0.8 / len(data)
    for i, (name, m) in enumerate(data.items()):
        vals = [m["per_dataset"].get(d, {}).get("bacc", np.nan) for d in dsets] + [m["macro_bacc"], m["rag_subset_bacc"]]
        ax.bar(x - 0.4 + w * (i + 0.5), vals, w * 0.92, color=C.get(name, NEUTRAL), label=name)
    ax.set_xticks(x, dsets + ["macro\naverage", "RAG\nsubset"], rotation=45, ha="right")
    ax.set_ylabel("balanced accuracy")
    ax.set_ylim(0.3, 1.0)
    ax.axhline(0.5, color=NEUTRAL, lw=1, ls="--")
    ax.legend(ncol=4, fontsize=7, loc="upper center", bbox_to_anchor=(0.5, 1.2))
    g.save(fig, "aggrefact_per_dataset", "LLM-AggreFact test: balanced accuracy per sub-dataset at threshold 0.5, the "
           "11-way macro average and the RAG-subset average (RAGTruth, LFQA, ClaimVerify, ExpertQA).",
           "results/*/aggrefact/metrics.json")


def main():
    g = Group("results")
    for f in (anli_rules, ragtruth_binary, aggrefact):
        f(g)
    g.write_index("Results figures (all systems evaluated so far)")
