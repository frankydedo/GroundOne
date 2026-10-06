"""Dataset figures (docs/dataset_plan.md): class balance per split, minority classes per task, K and length distributions,
and where unsupported sentences sit in the answer. Reads Project/data/processed/groundone/*.jsonl.

Usage: groundone figures dataset
"""
import json
from collections import Counter

import numpy as np

from ..config import PROJECT
from .style import INK2, NEUTRAL, SERIES, Group, bar_labels, plt

D = PROJECT / "data" / "processed" / "groundone"
CLASSES = ("supported", "contradicted", "not_mentioned")
CLASS_COLORS = {"supported": SERIES[0], "contradicted": SERIES[1], "not_mentioned": SERIES[6]}
SPLITS = {"train": "train", "dev": "dev", "test_ragtruth": "T1 RAGTruth", "test_vitaminc": "T3 VitaminC"}


def load(name):
    return [json.loads(l) for l in open(D / f"{name}.jsonl")]


def main():
    g = Group("dataset")
    data = {n: load(n) for n in SPLITS}

    # 1. class shares per split
    fig, ax = plt.subplots(figsize=(7, 3.2))
    names = list(SPLITS.values())
    counts = {n: Counter(l for r in data[k] for l in r["labels"] if l is not None) for k, n in SPLITS.items()}
    left = np.zeros(len(names))
    for c in CLASSES:
        tot = np.array([sum(counts[n].values()) for n in names], float)
        v = np.array([counts[n][c] for n in names]) / tot
        ax.barh(names, v, left=left, color=CLASS_COLORS[c], label=c, edgecolor="white", linewidth=1)
        for i, (x, w) in enumerate(zip(left, v)):
            if w > 0.04:
                ax.text(x + w / 2, i, f"{w:.0%}", ha="center", va="center", fontsize=7, color="white")
        left += v
    for i, n in enumerate(names):
        ax.text(1.01, i, f"{sum(counts[n].values()):,}", va="center", fontsize=7, color=INK2)
    ax.set_xlim(0, 1.12)
    ax.invert_yaxis()
    ax.set_xlabel("share of labelled sentences (number of decisions on the right)")
    ax.legend(ncol=3, fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.25))
    g.save(fig, "class_balance_by_split", "Class balance of the labelled sentences in each split. RAGTruth (train, dev, "
           "T1) is about 89 % supported; T3 is sampled to 1,000 pairs per class.", "data/processed/groundone/*.jsonl")

    # 2. minority classes per task in T1 and train
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.2))
    for ax, k in zip(axes, ("train", "test_ragtruth")):
        tasks = ["QA", "Summary", "Data2txt"]
        c = Counter((r["task"], l) for r in data[k] for l in r["labels"] if l is not None)
        x = np.arange(len(tasks))
        for j, cl in enumerate(("contradicted", "not_mentioned")):
            bars = ax.bar(x + (j - 0.5) * 0.38, [c[(t, cl)] for t in tasks], 0.36, color=CLASS_COLORS[cl], label=cl)
            bar_labels(ax, bars, "{:,.0f}")
        ax.set_xticks(x, tasks)
        ax.set_title(SPLITS[k])
        ax.set_ylabel("sentences")
    axes[0].legend(fontsize=7)
    g.save(fig, "minority_classes_by_task", "Contradicted and not-mentioned sentences per RAGTruth task. Contradictions "
           "come mostly from data-to-text; in T1 QA has very few, so its contradicted recall is only indicative.",
           "data/processed/groundone/{train,test_ragtruth}.jsonl")

    # 3. K distribution
    fig, ax = plt.subplots(figsize=(7, 3.2))
    for i, k in enumerate(("train", "test_ragtruth")):
        K = [r["meta"]["K"] for r in data[k]]
        ax.hist(K, bins=np.arange(0.5, 30.5, 1), density=True, alpha=0.55, color=SERIES[i * 2], label=f"{SPLITS[k]} (n = {len(K):,})")
    for b in (4.5, 8.5, 13.5):
        ax.axvline(b, color=NEUTRAL, lw=1, ls="--")
    ax.set_xlabel("K = scored sentences per answer (dashed: K bands 1–4, 5–8, 9–13, ≥ 14)")
    ax.set_ylabel("share of answers")
    ax.legend(fontsize=7)
    g.save(fig, "K_distribution", "Distribution of K (scored sentences per answer) in train and T1, with the K bands used "
           "for the K curves.", "data/processed/groundone/{train,test_ragtruth}.jsonl")

    # 4. prompt length
    fig, ax = plt.subplots(figsize=(7, 3.2))
    for i, k in enumerate(("train", "test_ragtruth")):
        L = [r["meta"]["n_tokens"] for r in data[k]]
        ax.hist(L, bins=60, range=(0, 2100), density=True, alpha=0.55, color=SERIES[i * 2], label=f"{SPLITS[k]} (median {int(np.median(L))})")
    ax.axvline(2048, color=INK2, lw=1, ls="--")
    ax.set_xlabel("tokens of document + answer (Qwen2.5 tokenizer; dashed: 2,048 cap)")
    ax.set_ylabel("share of answers")
    ax.legend(fontsize=7)
    g.save(fig, "prompt_length", "Length of document plus answer in Qwen2.5 tokens; answers over the 2,048-token cap "
           "are excluded (counts in the data card).", "data/processed/groundone/{train,test_ragtruth}.jsonl")

    # 5. unsupported share by sentence position
    fig, ax = plt.subplots(figsize=(7, 3.2))
    for i, k in enumerate(("train", "test_ragtruth")):
        pos = Counter()
        bad = Counter()
        for r in data[k]:
            j = 0
            for l in r["labels"]:
                if l is None:
                    continue
                b = min(j, 12)
                pos[b] += 1
                bad[b] += l != "supported"
                j += 1
        xs = sorted(pos)
        ax.plot(xs, [bad[x] / pos[x] for x in xs], marker="o", color=SERIES[i * 2], label=SPLITS[k])
    ax.set_xticks(range(13), [str(x + 1) for x in range(12)] + ["≥13"])
    ax.set_xlabel("position of the scored sentence in the answer")
    ax.set_ylabel("share contradicted or not mentioned")
    ax.legend(fontsize=7)
    g.save(fig, "unsupported_by_position", "Share of contradicted or not-mentioned sentences by position in the answer: "
           "the first sentence is rarely unsupported (3–7 %), the share peaks at positions 3–5 (12–15 %) and stays at "
           "8–11 % in late positions, so long answers still contain errors to catch at the end.",
           "data/processed/groundone/{train,test_ragtruth}.jsonl")
    g.write_index("Dataset figures")
