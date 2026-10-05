"""Cross-dataset EDA: side-by-side comparison and overlap / leakage checks."""
import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import COLORS, RAW, n_tokens, norm, save_fig, save_stats, split_sentences

stats, figs = {}, []
resp = pd.DataFrame([json.loads(l) for l in open(RAW / "ragtruth" / "response.jsonl")])
src = pd.DataFrame([json.loads(l) for l in open(RAW / "ragtruth" / "source_info.jsonl")])
ag = pd.concat([pd.read_parquet(RAW / "llm_aggrefact" / f"{s}.parquet").assign(split=s) for s in ["dev", "test"]])
mc = pd.concat([pd.read_parquet(RAW / "minicheck_synth" / f"{n}.parquet") for n in ["c2d", "d2c"]])
anli = pd.concat([pd.read_parquet(RAW / "anli" / f"{s}_{r}.parquet").assign(split=s) for s in ["train", "dev", "test"] for r in ["r1", "r2", "r3"]])

# ---- overlap: LLM-AggreFact's RAGTruth subset vs RAGTruth train/test ----
ag_rt = ag[ag.dataset == "RAGTruth"]
resp["norm"] = resp["response"].map(norm)
sent_norm = {}
for r in resp.itertuples():
    for _, _, t in split_sentences(r.response):
        sent_norm.setdefault(norm(t), set()).add(r.split)
resp_split = dict(zip(resp["norm"], resp["split"]))
claims = ag_rt["claim"].map(norm)
match_resp = claims.map(resp_split)
match_sent = claims.map(lambda c: "/".join(sorted(sent_norm.get(c, set()))) or None)
stats["aggrefact_ragtruth_subset"] = {
    "n": len(ag_rt), "by_split": ag_rt["split"].value_counts().to_dict(),
    "claims_equal_to_a_full_ragtruth_response": match_resp.value_counts(dropna=False).to_dict(),
    "claims_equal_to_a_ragtruth_sentence": match_sent.value_counts(dropna=False).to_dict(),
}
src_ctx = set(norm(s["source_info"]["passages"]) if s["task_type"] == "QA" else norm(s["source_info"] if isinstance(s["source_info"], str) else json.dumps(s["source_info"]))
              for s in src.to_dict("records"))
stats["aggrefact_ragtruth_docs_found_in_ragtruth_sources"] = round(float(ag_rt["doc"].map(norm).isin(src_ctx).mean()), 3)

# ---- overlap: MiniCheck synthetic vs LLM-AggreFact, ANLI vs LLM-AggreFact ----
ag_docs = set(ag["doc"].map(norm))
ag_claims = set(ag["claim"].map(norm))
stats["minicheck_docs_in_aggrefact"] = int(mc["doc"].map(norm).isin(ag_docs).sum())
stats["minicheck_claims_in_aggrefact"] = int(mc["claim"].map(norm).isin(ag_claims).sum())
stats["anli_premises_in_aggrefact"] = int(anli["premise"].map(norm).isin(ag_docs).sum())

# ---- side-by-side profile ----
def sample_tokens(texts, n=3000, seed=0):
    s = pd.Series(texts).sample(min(n, len(texts)), random_state=seed)
    return n_tokens(s.tolist())

profiles = {
    "ANLI": (anli["premise"], anli["hypothesis"]),
    "RAGTruth (QA)": (src[src.task_type == "QA"]["source_info"].map(lambda i: f"Question: {i['question']}\n\n{i['passages']}"), None),
    "RAGTruth (Summary)": (src[src.task_type == "Summary"]["source_info"].map(str), None),
    "MiniCheck synth": (mc["doc"], mc["claim"]),
    "LLM-AggreFact test": (ag[ag.split == "test"]["doc"], ag[ag.split == "test"]["claim"]),
}
doc_tok = {k: sample_tokens(v[0]) for k, v in profiles.items()}
stats["doc_tokens_median"] = {k: float(np.median(v)) for k, v in doc_tok.items()}
fig, ax = plt.subplots(figsize=(10, 3.4))
ax.boxplot(list(doc_tok.values()), tick_labels=list(doc_tok.keys()), showfliers=False, vert=False)
ax.axvline(1024, color="k", ls="--", lw=.8); ax.axvline(2048, color="k", ls=":", lw=.8)
ax.set_title("document / context length (tokens, sample of ≤ 3,000 per set); lines = 1,024 and 2,048")
figs.append(save_fig(fig, "cross_doc_lengths", "Document length across all datasets. ANLI premises are an order of magnitude shorter than RAG contexts."))

stats["label_schemes"] = {
    "ANLI": "3 classes from humans: entailment / neutral / contradiction",
    "RAGTruth": "character spans of 4 types on LLM answers; sentence classes derived (supported / not mentioned / contradicted)",
    "MiniCheck synth": "binary supported / unsupported (synthetic, LLM-generated)",
    "LLM-AggreFact": "binary supported / unsupported (human); partial support = unsupported",
}
stats["figures"] = figs
save_stats("cross", stats)
print("cross done:", json.dumps(stats["aggrefact_ragtruth_subset"], default=str))

# ---- agreement: our span-derived sentence labels vs LLM-AggreFact's labels for the same RAGTruth sentences ----
ours = {}
for r in resp.itertuples():
    for a, b, t in split_sentences(r.response):
        unsup = any(a < s["end"] and s["start"] < b for s in r.labels)
        ours.setdefault(norm(t), set()).add(int(not unsup))
agree_rows = []
for s in ["dev", "test"]:
    a = ag_rt[ag_rt.split == s]
    for c, l in zip(a["claim"].map(norm), a["label"]):
        o = ours.get(c)
        if o and len(o) == 1:
            agree_rows.append({"split": s, "ours": next(iter(o)), "aggrefact": int(l)})
ag_df = pd.DataFrame(agree_rows)
ct = pd.crosstab(ag_df["ours"], ag_df["aggrefact"])
stats["label_agreement_ours_vs_aggrefact"] = {
    "matched_sentences": len(ag_df), "agreement": round(float((ag_df.ours == ag_df.aggrefact).mean()), 4),
    "crosstab_rows_ours_cols_aggrefact": {str(k): {str(c): int(v) for c, v in r.items()} for k, r in ct.to_dict("index").items()},
    "aggrefact_dev_ragtruth_comes_from": "RAGTruth train split", "aggrefact_test_ragtruth_comes_from": "RAGTruth test split",
}
save_stats("cross", stats)
print("agreement:", stats["label_agreement_ours_vs_aggrefact"]["agreement"], stats["label_agreement_ours_vs_aggrefact"]["crosstab_rows_ours_cols_aggrefact"])
