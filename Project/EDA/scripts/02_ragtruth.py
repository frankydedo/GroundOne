"""EDA of RAGTruth: tasks, generators, hallucination rates, span types, sentence-level labels, K, lengths."""
import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import COLORS, RAW, describe, n_tokens, save_fig, save_stats, split_sentences

resp = pd.DataFrame([json.loads(l) for l in open(RAW / "ragtruth" / "response.jsonl")])
src = pd.DataFrame([json.loads(l) for l in open(RAW / "ragtruth" / "source_info.jsonl")])
df = resp.merge(src[["source_id", "task_type", "source", "source_info"]], on="source_id")
df["hallucinated"] = df["labels"].map(bool)
stats, figs = {}, []
TASKS = ["QA", "Summary", "Data2txt"]

# ---------------- responses ----------------
stats["responses_by_split_task"] = df.groupby(["split", "task_type"]).size().unstack().to_dict()
stats["sources_by_task_origin"] = src.groupby(["task_type", "source"]).size().to_dict()
stats["sources_shared_between_splits"] = int((df.groupby("source_id")["split"].nunique() > 1).sum())
stats["quality"] = df["quality"].value_counts().to_dict()
stats["hallucinated_rate_by_task_split"] = df.groupby(["task_type", "split"])["hallucinated"].mean().round(3).unstack().to_dict()
stats["hallucinated_rate_by_model"] = df.groupby("model")["hallucinated"].mean().round(3).sort_values().to_dict()
fig, axes = plt.subplots(1, 2, figsize=(10, 3.2))
hr = df.groupby(["task_type", "split"])["hallucinated"].mean().unstack().loc[TASKS]
x = np.arange(3)
for i, s in enumerate(["train", "test"]):
    axes[0].bar(x + (i - .5) * .38, hr[s], width=.38, color=COLORS[i], label=s)
axes[0].set_xticks(x, TASKS); axes[0].set_title("share of responses with ≥ 1 hallucination"); axes[0].legend(frameon=False)
hm = df.groupby("model")["hallucinated"].mean().sort_values()
axes[1].barh(hm.index, hm.values, color=COLORS[1]); axes[1].set_title("by generator model")
figs.append(save_fig(fig, "ragtruth_responses", "RAGTruth responses with at least one annotated hallucination, by task and by the LLM that wrote them."))

# ---------------- spans ----------------
spans = df[["id", "task_type", "split", "response", "labels"]].explode("labels").dropna(subset=["labels"])
sp = pd.json_normalize(spans["labels"]).assign(task_type=spans["task_type"].values, split=spans["split"].values, rid=spans["id"].values)
sp["len"] = sp["end"] - sp["start"]
sp["kind"] = np.where(sp["label_type"].str.contains("Conflict"), "Conflict (contradicted)", "Baseless (not mentioned)")
sp["evident"] = sp["label_type"].str.startswith("Evident")
stats["spans_total"] = len(sp)
stats["span_types"] = sp["label_type"].value_counts().to_dict()
stats["span_kind_by_task"] = sp.groupby(["task_type", "kind"]).size().unstack(fill_value=0).to_dict()
stats["span_flags"] = {"implicit_true": int(sp.get("implicit_true", pd.Series(dtype=bool)).fillna(False).sum()),
                       "due_to_null": int(sp.get("due_to_null", pd.Series(dtype=bool)).fillna(False).sum())}
stats["span_length_chars"] = describe(sp["len"])
fig, axes = plt.subplots(1, 2, figsize=(10, 3.2))
kt = sp.groupby(["task_type", "label_type"]).size().unstack(fill_value=0).loc[TASKS]
bottom = np.zeros(3)
for i, c in enumerate(["Evident Conflict", "Subtle Conflict", "Evident Baseless Info", "Subtle Baseless Info"]):
    if c in kt:
        axes[0].bar(TASKS, kt[c], bottom=bottom, color=COLORS[i], label=c); bottom += kt[c].values
axes[0].set_title("annotated spans by type"); axes[0].legend(frameon=False, fontsize=7)
axes[1].hist(sp["len"].clip(upper=600), bins=60, color=COLORS[0]); axes[1].set_title("span length (characters, clipped at 600)")
figs.append(save_fig(fig, "ragtruth_spans", "RAGTruth hallucination spans: Baseless Info (content not in the context) dominates; Conflict (contradiction) is rarer, and Subtle Conflict is very rare."))

# ---------------- sentence-level labels ----------------
rows, crossing, uncovered = [], 0, 0
for r in df.itertuples():
    sents = split_sentences(r.response)
    spans_r = r.labels
    for s in spans_r:
        hit = [i for i, (a, b, _) in enumerate(sents) if a < s["end"] and s["start"] < b]
        crossing += len(hit) > 1
        uncovered += len(hit) == 0
    for i, (a, b, t) in enumerate(sents):
        types = [s["label_type"] for s in spans_r if a < s["end"] and s["start"] < b]
        flags_it = any(s.get("implicit_true") for s in spans_r if a < s["end"] and s["start"] < b)
        cls = "contradicted" if any("Conflict" in x for x in types) else ("not_mentioned" if types else "supported")
        rows.append({"rid": r.id, "task": r.task_type, "split": r.split, "K": len(sents), "cls": cls,
                     "n_spans": len(types), "implicit_true": flags_it, "chars": b - a})
sent = pd.DataFrame(rows)
stats["sentences_total"] = len(sent)
stats["spans_crossing_sentence_boundary"] = {"n": crossing, "share": round(crossing / len(sp), 3)}
stats["spans_not_covered_by_any_sentence"] = uncovered
stats["sentence_class_share_by_task_split"] = sent.groupby(["task", "split"])["cls"].value_counts(normalize=True).round(3).unstack().to_dict("index")
stats["sentence_class_counts_train"] = sent[sent.split == "train"]["cls"].value_counts().to_dict()
stats["sentence_class_counts_test"] = sent[sent.split == "test"]["cls"].value_counts().to_dict()
stats["sentences_with_implicit_true"] = int(sent["implicit_true"].sum())
k = sent.groupby("rid").agg(K=("K", "first"), task=("task", "first"))
stats["K_by_task"] = {t: describe(g["K"]) for t, g in k.groupby("task")}
stats["responses_with_K_ge_8_share"] = round(float((k["K"] >= 8).mean()), 3)
fig, axes = plt.subplots(1, 2, figsize=(10, 3.2))
for i, t in enumerate(TASKS):
    axes[0].hist(k.loc[k.task == t, "K"], bins=np.arange(0.5, 30.5, 1), alpha=.55, color=COLORS[i], label=t)
axes[0].set_title("sentences per response (K)"); axes[0].legend(frameon=False)
cs = sent.groupby("task")["cls"].value_counts(normalize=True).unstack().loc[TASKS][["supported", "not_mentioned", "contradicted"]]
bottom = np.zeros(3)
for i, c in enumerate(cs.columns):
    axes[1].bar(TASKS, cs[c], bottom=bottom, color=COLORS[i], label=c); bottom += cs[c].values
axes[1].set_title("sentence-level classes (all splits)"); axes[1].legend(frameon=False, fontsize=8, loc="lower right")
figs.append(save_fig(fig, "ragtruth_sentences", "RAGTruth at sentence level (labels derived from spans): K per response and the share of supported / not mentioned / contradicted sentences."))

# ---------------- context lengths ----------------
def context_of(task, info):
    if task == "QA":
        return f"Question: {info['question']}\n\n{info['passages']}"
    return info if isinstance(info, str) else json.dumps(info, ensure_ascii=False)

src["context"] = [context_of(t, i) for t, i in zip(src["task_type"], src["source_info"])]
src["ctx_tok"] = n_tokens(src["context"].tolist())
resp_tok = n_tokens(df["response"].tolist())
df["resp_tok"] = resp_tok
stats["context_tokens_by_task"] = {t: describe(g) for t, g in src.groupby("task_type")["ctx_tok"]}
stats["response_tokens_by_task"] = {t: describe(g) for t, g in df.groupby("task_type")["resp_tok"]}
src_tok = src.set_index("source_id")["ctx_tok"]
df["prompt_tok_est"] = df["source_id"].map(src_tok) + df["resp_tok"] + 60
stats["share_prompts_over_1024_tokens"] = round(float((df["prompt_tok_est"] > 1024).mean()), 3)
stats["share_prompts_over_2048_tokens"] = round(float((df["prompt_tok_est"] > 2048).mean()), 3)
fig, ax = plt.subplots(figsize=(10, 3))
for i, t in enumerate(TASKS):
    ax.hist(src.loc[src.task_type == t, "ctx_tok"], bins=60, range=(0, 2500), alpha=.55, color=COLORS[i], label=t)
for v in (1024, 2048):
    ax.axvline(v, color="k", ls="--", lw=.8)
ax.set_title("context length (tokens); dashed lines = 1,024 / 2,048 training caps"); ax.legend(frameon=False)
figs.append(save_fig(fig, "ragtruth_context_lengths", "RAGTruth context lengths by task. Data2txt contexts are JSON business records; QA contexts are 3 retrieved passages."))

stats["example_data2txt_context"] = src[src.task_type == "Data2txt"]["context"].iloc[0][:400]
stats["figures"] = figs
save_stats("ragtruth", stats)
(RAW.parent / "processed").mkdir(exist_ok=True)
sent.to_parquet(RAW.parent / "processed" / "ragtruth_sentences_eda.parquet")
print("ragtruth done:", stats["sentences_total"], "sentences")
