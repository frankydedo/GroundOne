"""EDA part B: the built GroundOne dataset (Project/data/processed/groundone/), beyond the counts in DATACARD.md.

  1. segmentation: regex splitter (earlier experiments) vs pysbd + checkable-content rule, on all good RAGTruth answers
  2. train vs T1: task, generator and class shares (distribution shift)
  3. where the classes come from: RAGTruth span types behind contradicted / not_mentioned sentences
  4. claim-document word overlap by class (train, T1, T3): a surface cue a model could exploit
  5. sentence-only cues: the most predictive n-grams of the shortcut classifier, per class
  6. unsupported share by generator in train and T1
"""
import json
import re
from collections import Counter, defaultdict

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression

from common import CLASS_COLORS, COLORS, NEUTRAL, RAW, TASKS, load_split, plt, save_fig, save_stats
from groundone.data import segment as seg

STOP = set("a an the of in on at to for and or is are was were be been by with as that this it its from has have had".split())
REGEX = re.compile(r"[^.!?\n]+(?:[.!?]+|$)", re.M)  # splitter used before the dataset rebuild
stats, figs = {}, []
data = {n: load_split(n) for n in ("train", "dev", "test_ragtruth", "test_vitaminc")}
resp = {r["id"]: r for r in (json.loads(l) for l in open(RAW / "ragtruth" / "response.jsonl"))}

# 1. segmentation -----------------------------------------------------------------------------------------------
good = [r for r in resp.values() if r["quality"] == "good"]
n_regex = sum(len([m for m in REGEX.finditer(r["response"]) if len(m.group(0).strip()) >= 3]) for r in good)
cats = Counter()
n_pysbd = 0
for r in good:
    for x in seg.segment(r["response"]):
        n_pysbd += 1
        if x.checkable:
            continue
        t = x.text.strip().strip("*#-•> \t").strip()
        cats["fewer than 2 words" if len(seg._WORD.findall(t)) < 2 else "heading ending with ':'" if t.endswith(":")
             else "citation only" if seg._CITATION.match(t) else "conversational / refusal formula"] += 1
stats["segmentation"] = {"answers": len(good), "regex_sentences": n_regex,
                         "pysbd_sentences": n_pysbd, "non_checkable_by_reason": dict(cats),
                         "non_checkable_share": round(sum(cats.values()) / n_pysbd, 4)}
fig, ax = plt.subplots(figsize=(7, 2.8))
k, v = zip(*cats.most_common())
bars = ax.barh(k, v, color=NEUTRAL)
for b in bars:
    ax.text(b.get_width(), b.get_y() + b.get_height() / 2, f" {int(b.get_width()):,}", va="center", fontsize=7)
ax.invert_yaxis()
ax.set_xlabel(f"sentences without checkable content (of {n_pysbd:,} RAGTruth sentences)")
figs.append(save_fig(fig, "non_checkable_reasons", "Sentences kept as context but not scored (label null), by the rule that "
                     "excluded them, over all good RAGTruth answers."))

# 2. train vs T1 shift --------------------------------------------------------------------------------------------
def frame(recs, split):
    rows = []
    for r in recs:
        for i, l in enumerate(r["labels"]):
            if l is not None:
                rows.append({"split": split, "task": r["task"], "model": r["meta"].get("model"), "cls": l,
                             "sent": r["sentences"][i], "doc": r["doc"]})
    return pd.DataFrame(rows)


S = pd.concat([frame(data["train"], "train"), frame(data["test_ragtruth"], "T1")])
stats["class_share_by_split_task"] = S.groupby(["split", "task"])["cls"].value_counts(normalize=True).round(3).unstack().to_dict("index")
stats["unsupported_share_by_split_model"] = (S.assign(u=S.cls != "supported").groupby(["model", "split"])["u"].mean().round(3).unstack().to_dict("index"))
fig, axes = plt.subplots(1, 2, figsize=(10, 3.4))
for ax, sp in zip(axes, ("train", "T1")):
    cs = S[S.split == sp].groupby("task")["cls"].value_counts(normalize=True).unstack().loc[TASKS]
    left = np.zeros(3)
    for c in ("contradicted", "not_mentioned"):
        bars = ax.bar(np.arange(3) + (0 if c == "contradicted" else 0.38) - 0.19, cs[c], 0.36, color=CLASS_COLORS[c], label=c)
        for b in bars:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height(), f"{b.get_height():.1%}", ha="center", va="bottom", fontsize=7)
    ax.set_xticks(range(3), TASKS)
    ax.set_title(sp)
    ax.set_ylabel("share of scored sentences")
axes[0].legend(fontsize=7)
figs.append(save_fig(fig, "minority_share_train_vs_T1", "Share of contradicted and not-mentioned sentences per task in train and "
                     "T1. T1 has fewer hallucinations than train in every task (RAGTruth test answers are cleaner)."))
um = pd.DataFrame(stats["unsupported_share_by_split_model"]).T.sort_values("train")
fig, ax = plt.subplots(figsize=(7, 3.2))
y = np.arange(len(um))
ax.barh(y - 0.19, um["train"], 0.36, color=COLORS[0], label="train")
ax.barh(y + 0.19, um["T1"], 0.36, color=COLORS[2], label="T1")
ax.set_yticks(y, um.index)
ax.set_xlabel("share of scored sentences contradicted or not mentioned")
ax.legend(fontsize=7)
figs.append(save_fig(fig, "unsupported_by_generator", "Unsupported sentences by the LLM that wrote the answer: GPT-3.5/4 "
                     "answers are mostly supported, Llama-2 and Mistral answers carry most hallucinations."))

# 3. span types behind the classes ------------------------------------------------------------------------------
types = defaultdict(Counter)
for name in ("train", "test_ragtruth"):
    for r in data[name]:
        raw = resp[r["meta"]["response_id"]]
        sents = [x for x in seg.segment(raw["response"])]
        for x, l in zip(sents, r["labels"]):
            if l in ("contradicted", "not_mentioned"):
                t = sorted({s["label_type"] for s in raw["labels"] if x.start < s["end"] and s["start"] < x.end})
                types[f"{name}|{l}"][" + ".join(t)] += 1
stats["span_types_behind_classes"] = {k: dict(v.most_common(6)) for k, v in types.items()}

# 4. word overlap by class ----------------------------------------------------------------------------------------
def overlap(c, e):
    cw = {w for w in re.findall(r"[a-z0-9]+", c.lower()) if w not in STOP}
    ew = set(re.findall(r"[a-z0-9]+", e.lower()))
    return len(cw & ew) / max(len(cw), 1)


V = frame(data["test_vitaminc"], "T3")
O = pd.concat([S, V])
O["overlap"] = [overlap(a, b) for a, b in zip(O["sent"], O["doc"])]
stats["overlap_mean_by_split_class"] = O.groupby(["split", "cls"])["overlap"].mean().round(3).unstack().to_dict("index")
from sklearn.metrics import roc_auc_score  # noqa: E402
stats["overlap_auroc_supported_vs_not"] = {sp: round(float(roc_auc_score(g.cls == "supported", g.overlap)), 3) for sp, g in O.groupby("split")}
fig, axes = plt.subplots(1, 3, figsize=(11, 3.2), sharey=True)
for ax, sp in zip(axes, ("train", "T1", "T3")):
    g = O[O.split == sp]
    for c in ("supported", "contradicted", "not_mentioned"):
        x = g[g.cls == c]["overlap"]
        ax.hist(x, bins=20, range=(0, 1), density=True, alpha=.5, color=CLASS_COLORS[c], label=f"{c} ({x.mean():.2f})")
    ax.set_title(sp)
    ax.set_xlabel("share of sentence content words in the document")
    ax.legend(fontsize=6)
axes[0].set_ylabel("density")
figs.append(save_fig(fig, "overlap_by_class", "Word overlap between a sentence and its document, by class (mean in brackets). "
                     "The same ordering holds in all three sets (supported > contradicted > not mentioned), VitaminC included: "
                     "word overlap is a natural, partial cue, so a verifier must be compared with an overlap-only baseline."))

# 5. sentence-only cues -------------------------------------------------------------------------------------------
tr = S[S.split == "train"]
vec = CountVectorizer(ngram_range=(1, 2), min_df=20, stop_words="english")
X = vec.fit_transform(tr["sent"])
clf = LogisticRegression(max_iter=3000, class_weight="balanced").fit(X, tr["cls"])
names = np.array(vec.get_feature_names_out())
stats["sentence_only_top_ngrams"] = {c: names[np.argsort(-clf.coef_[i])[:15]].tolist() for i, c in enumerate(clf.classes_)}
stats["figures"] = figs
save_stats("dataset", stats)
print("dataset done")
