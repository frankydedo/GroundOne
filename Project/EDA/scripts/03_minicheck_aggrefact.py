"""EDA (lighter) of the MiniCheck synthetic training data and of the LLM-AggreFact benchmark."""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import COLORS, RAW, describe, n_tokens, save_fig, save_stats

stats, figs = {}, []

# ---------------- MiniCheck synthetic ----------------
mc = pd.concat([pd.read_parquet(RAW / "minicheck_synth" / f"{n}.parquet").assign(subset=n) for n in ["c2d", "d2c"]])
mc["doc_tok"] = n_tokens(mc["doc"].tolist())
mc["claim_tok"] = n_tokens(mc["claim"].tolist())
stats["minicheck"] = {
    "sizes": mc["subset"].value_counts().to_dict(),
    "supported_rate": mc.groupby("subset")["label"].mean().round(3).to_dict(),
    "doc_tokens": describe(mc["doc_tok"]), "claim_tokens": describe(mc["claim_tok"]),
    "unique_docs": int(mc["doc"].nunique()), "claims_per_doc_mean": round(len(mc) / mc["doc"].nunique(), 2),
}

# ---------------- LLM-AggreFact ----------------
ag = pd.concat([pd.read_parquet(RAW / "llm_aggrefact" / f"{s}.parquet").assign(split=s) for s in ["dev", "test"]])
ag["doc_tok"] = n_tokens(ag["doc"].tolist())
ag["claim_tok"] = n_tokens(ag["claim"].tolist())
per = ag.groupby(["dataset", "split"]).agg(n=("label", "size"), supported=("label", "mean"),
                                           doc_tok_p50=("doc_tok", "median"), doc_tok_p90=("doc_tok", lambda x: x.quantile(.9)),
                                           claim_tok_p50=("claim_tok", "median")).round(3)
stats["aggrefact"] = {"per_dataset": per.reset_index().to_dict("records"),
                      "share_docs_over_2048_tokens_test": round(float((ag[ag.split == "test"]["doc_tok"] > 2048).mean()), 3),
                      "contamination_identifier_example": str(ag["contamination_identifier"].dropna().iloc[0])[:120]}

fig, axes = plt.subplots(1, 2, figsize=(11, 3.6))
t = per.xs("test", level="split").sort_values("doc_tok_p50")
axes[0].barh(t.index, t["doc_tok_p50"], color=COLORS[0], label="median")
axes[0].barh(t.index, t["doc_tok_p90"] - t["doc_tok_p50"], left=t["doc_tok_p50"], color=COLORS[0], alpha=.35, label="to p90")
axes[0].axvline(2048, color="k", ls="--", lw=.8); axes[0].set_title("document length (tokens), test"); axes[0].legend(frameon=False, fontsize=7)
axes[1].barh(t.index, t["supported"], color=COLORS[2]); axes[1].set_xlim(0, 1); axes[1].set_title("share of supported claims, test")
figs.append(save_fig(fig, "aggrefact_datasets", "LLM-AggreFact sub-datasets: document length and label balance vary widely; balanced accuracy averages them with equal weight."))

fig, ax = plt.subplots(figsize=(10, 3))
ax.hist(mc["doc_tok"], bins=60, range=(0, 1500), alpha=.6, color=COLORS[1], label="MiniCheck synthetic (doc)")
ax.hist(ag.loc[ag.split == "test", "doc_tok"], bins=60, range=(0, 1500), alpha=.4, color=COLORS[0], label="LLM-AggreFact test (doc)")
ax.set_title("document length (tokens)"); ax.legend(frameon=False)
figs.append(save_fig(fig, "minicheck_vs_aggrefact_lengths", "MiniCheck training documents are short (median ≈ 190 tokens; ≈ 290 with claim and prompt) compared with many LLM-AggreFact documents."))
stats["figures"] = figs
save_stats("minicheck_aggrefact", stats)
print("minicheck/aggrefact done")
