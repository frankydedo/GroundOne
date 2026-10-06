"""EDA part A: VitaminC test split (source of test T3): real vs synthetic, label balance, lengths, contrastive structure,
numerical claims, and claim-evidence word overlap by label (the bias VitaminC's annotators were told to avoid)."""
import re

import numpy as np
import pandas as pd

from common import CLASS_COLORS, COLORS, RAW, describe, n_tokens, plt, save_fig, save_stats

STOP = set("a an the of in on at to for and or is are was were be been by with as that this it its from has have had".split())
NUM = re.compile(r"\d")
stats, figs = {}, []
d = pd.read_json(RAW / "vitaminc" / "test.jsonl", lines=True)
stats["test_by_type_label"] = d.groupby(["revision_type", "label"]).size().to_dict()
r = d[d.revision_type == "real"].copy()
r["claim_tok"] = n_tokens(r["claim"].tolist())
r["evidence_tok"] = n_tokens(r["evidence"].tolist())
r["numeric"] = r["claim"].map(lambda s: bool(NUM.search(s)))


def overlap(c, e):
    cw = {w for w in re.findall(r"[a-z0-9]+", c.lower()) if w not in STOP}
    ew = set(re.findall(r"[a-z0-9]+", e.lower()))
    return len(cw & ew) / max(len(cw), 1)


r["overlap"] = [overlap(c, e) for c, e in zip(r["claim"], r["evidence"])]
stats["real"] = {"n": len(r), "pages": int(r["page"].nunique()), "cases": int(r["case_id"].nunique()),
                 "pairs_per_case_mean": round(len(r) / r["case_id"].nunique(), 2),
                 "claims_with_several_evidences": int((r.groupby("claim").evidence.nunique() > 1).sum()),
                 "claim_tokens": describe(r["claim_tok"]), "evidence_tokens": describe(r["evidence_tok"]),
                 "numeric_claim_share_by_label": r.groupby("label")["numeric"].mean().round(3).to_dict(),
                 "overlap_mean_by_label": r.groupby("label")["overlap"].mean().round(3).to_dict()}

lab = {"SUPPORTS": "supported", "REFUTES": "contradicted", "NOT ENOUGH INFO": "not_mentioned"}
fig, axes = plt.subplots(1, 2, figsize=(10, 3.2))
for i, (l, g) in enumerate(r.groupby("label")):
    axes[0].hist(g["overlap"], bins=20, range=(0, 1), alpha=.55, color=CLASS_COLORS[lab[l]], label=f"{lab[l]} (mean {g['overlap'].mean():.2f})")
axes[0].set_xlabel("share of claim content words found in the evidence")
axes[0].set_ylabel("pairs")
axes[0].legend(fontsize=7)
c = r.groupby("label").size()
axes[1].bar([lab[x] for x in c.index], c.values, color=[CLASS_COLORS[lab[x]] for x in c.index])
axes[1].set_ylabel("real test pairs")
figs.append(save_fig(fig, "vitaminc_overlap_labels", "VitaminC real test split (source of T3): claim-evidence word overlap by label "
                     "and label counts. Supported claims share more words with the evidence than refuted and NEI claims "
                     "(0.58 / 0.46 / 0.36) despite the annotators' instructions; T3 samples 1,000 pairs per class."))
stats["figures"] = figs
save_stats("vitaminc", stats)
print("vitaminc done:", len(r))
