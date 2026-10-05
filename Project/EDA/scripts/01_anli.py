"""EDA of ANLI (Adversarial NLI): splits, labels, lengths, lexical shortcuts, premise reuse."""
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import COLORS, RAW, describe, n_tokens, norm, save_fig, save_stats

LAB = {0: "entailment\n(supported)", 1: "neutral\n(not mentioned)", 2: "contradiction\n(contradicted)"}
LAB_SHORT = {0: "supported", 1: "not_mentioned", 2: "contradicted"}
frames = []
for split in ["train", "dev", "test"]:
    for r in ["r1", "r2", "r3"]:
        d = pd.read_parquet(RAW / "anli" / f"{split}_{r}.parquet")
        d["split"], d["round"] = split, r
        frames.append(d)
df = pd.concat(frames, ignore_index=True)
df["cls"] = df["label"].map(LAB_SHORT)
stats, figs = {}, []

# sizes and labels
tab = df.groupby(["split", "round", "cls"]).size().unstack(fill_value=0)
stats["sizes"] = df.groupby(["split", "round"]).size().unstack().to_dict()
stats["label_share_by_split_round"] = (tab.div(tab.sum(1), axis=0).round(3)).reset_index().to_dict("records")
fig, axes = plt.subplots(1, 3, figsize=(10, 3), sharey=True)
for ax, split in zip(axes, ["train", "dev", "test"]):
    t = tab.loc[split]
    share = t.div(t.sum(1), axis=0)
    bottom = np.zeros(len(share))
    for i, c in enumerate(["supported", "not_mentioned", "contradicted"]):
        ax.bar(share.index, share[c], bottom=bottom, color=COLORS[i], label=c)
        bottom += share[c].values
    ax.set_title(f"{split} (n = {int(t.values.sum()):,})")
axes[0].set_ylabel("share of pairs")
axes[2].legend(frameon=False, fontsize=8, loc="lower right")
figs.append(save_fig(fig, "anli_labels", "ANLI label shares per split and round. Train is imbalanced (neutral-heavy in R2/R3); dev and test are balanced."))

# lengths
df["premise_tok"] = n_tokens(df["premise"].tolist())
df["hyp_tok"] = n_tokens(df["hypothesis"].tolist())
stats["premise_tokens"] = describe(df["premise_tok"])
stats["hypothesis_tokens"] = describe(df["hyp_tok"])
stats["premise_tokens_by_round"] = {r: describe(g) for r, g in df.groupby("round")["premise_tok"]}
fig, axes = plt.subplots(1, 2, figsize=(10, 3))
for i, r in enumerate(["r1", "r2", "r3"]):
    g = df[df["round"] == r]
    axes[0].hist(g["premise_tok"], bins=60, range=(0, 300), alpha=.55, color=COLORS[i], label=r)
    axes[1].hist(g["hyp_tok"], bins=40, range=(0, 60), alpha=.55, color=COLORS[i], label=r)
axes[0].set_title("premise (document) length, tokens"); axes[1].set_title("hypothesis (claim) length, tokens")
axes[0].legend(frameon=False)
figs.append(save_fig(fig, "anli_lengths", "ANLI premise and hypothesis lengths (Qwen2.5 tokens). Premises are single paragraphs; far shorter than RAG contexts."))

# lexical overlap and negation cues (possible shortcuts)
def words(t):
    return set(re.findall(r"[a-z0-9']+", t.lower()))

df["overlap"] = [len(words(h) & words(p)) / max(len(words(h)), 1) for p, h in zip(df["premise"], df["hypothesis"])]
NEG = re.compile(r"\b(not|no|never|nobody|none|nothing|n't|cannot|neither|nor)\b|n't", re.I)
df["neg"] = df["hypothesis"].str.contains(NEG)
stats["overlap_mean_by_label"] = df.groupby("cls")["overlap"].mean().round(3).to_dict()
stats["negation_rate_by_label"] = df.groupby("cls")["neg"].mean().round(3).to_dict()
stats["negation_rate_by_label_train"] = df[df.split == "train"].groupby("cls")["neg"].mean().round(3).to_dict()
fig, axes = plt.subplots(1, 2, figsize=(10, 3))
order = ["supported", "not_mentioned", "contradicted"]
axes[0].boxplot([df.loc[df.cls == c, "overlap"] for c in order], tick_labels=order, showfliers=False)
axes[0].set_title("share of claim words that appear in the document")
nr = df.groupby(["split", "cls"])["neg"].mean().unstack()[order]
x = np.arange(3)
for i, s in enumerate(["train", "dev", "test"]):
    axes[1].bar(x + (i - 1) * .27, nr.loc[s], width=.27, color=COLORS[i], label=s)
axes[1].set_xticks(x, order); axes[1].set_title("claims containing a negation word"); axes[1].legend(frameon=False)
figs.append(save_fig(fig, "anli_shortcuts", "Possible shortcuts in ANLI: word overlap and negation words differ by label. A model could partly learn the label from the claim alone."))

# premise reuse across splits (several hypotheses share a premise)
prem = df.assign(p=df["premise"].map(norm))
train_p = set(prem.loc[prem.split == "train", "p"])
stats["premises_unique"] = int(prem["p"].nunique())
stats["hypotheses_per_premise_mean"] = round(len(prem) / prem["p"].nunique(), 2)
stats["dev_test_premises_also_in_train"] = {s: round(float(prem.loc[prem.split == s, "p"].isin(train_p).mean()), 4) for s in ["dev", "test"]}
stats["reason_field_nonempty"] = round(float((df["reason"].str.len() > 0).mean()), 3)
stats["examples"] = {c: df[(df.split == "dev") & (df.cls == c)].iloc[0][["premise", "hypothesis"]].to_dict() for c in order}
stats["figures"] = figs
save_stats("anli", stats)
print("anli done:", stats["sizes"])
