"""EDA part A: LLM-AggreFact test (test T2): sub-datasets, document and claim length, label balance.

Only the test split is analysed: the dev split is not used anywhere (evaluation only, D18)."""
import numpy as np

import pandas as pd

from common import COLORS, NEUTRAL, RAW, describe, n_tokens, plt, save_fig, save_stats

stats, figs = {}, []
ag = pd.read_parquet(RAW / "llm_aggrefact" / "test.parquet")
ag["doc_tok"] = n_tokens(ag["doc"].tolist())
ag["claim_tok"] = n_tokens(ag["claim"].tolist())
per = ag.groupby("dataset").agg(n=("label", "size"), supported=("label", "mean"), docs=("doc", "nunique"),
                                doc_tok_p50=("doc_tok", "median"), doc_tok_p90=("doc_tok", lambda x: x.quantile(.9)),
                                claim_tok_p50=("claim_tok", "median")).round(3)
per["claims_per_doc"] = (per["n"] / per["docs"]).round(2)
stats["per_dataset"] = per.reset_index().to_dict("records")
stats["n"] = len(ag)
stats["supported_rate"] = round(float(ag.label.mean()), 3)
stats["share_docs_over_2048_tokens"] = round(float((ag["doc_tok"] > 2048).mean()), 3)
stats["doc_tokens"] = describe(ag["doc_tok"])

fig, axes = plt.subplots(1, 2, figsize=(10, 3.6))
t = per.sort_values("doc_tok_p50")
axes[0].barh(t.index, t["doc_tok_p50"], color=COLORS[0], label="median")
axes[0].barh(t.index, t["doc_tok_p90"] - t["doc_tok_p50"], left=t["doc_tok_p50"], color=COLORS[0], alpha=.35, label="median to p90")
axes[0].axvline(2048, color=NEUTRAL, ls="--", lw=1)
axes[0].set_xlabel("document length (Qwen2.5 tokens; dashed: 2,048 cap)")
axes[0].legend(fontsize=7)
axes[1].barh(t.index, t["supported"], color=COLORS[2])
axes[1].set_xlim(0, 1)
axes[1].set_xlabel("share of supported claims")
axes[1].set_yticks(range(len(t)), [""] * len(t))
figs.append(save_fig(fig, "aggrefact_datasets", "LLM-AggreFact test (T2): document length and label balance per sub-dataset. "
                     "The macro balanced accuracy weights the 11 sub-datasets equally, although RAGTruth has 56 % of the claims."))
stats["figures"] = figs
save_stats("aggrefact", stats)
print("aggrefact done:", len(ag))
