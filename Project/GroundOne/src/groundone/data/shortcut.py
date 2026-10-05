"""Phase 1 check: claim-only baseline for ANLI (EDA finding: negation cue in train, reversed in dev/test).

A bag-of-words logistic regression sees ONLY the claim (hypothesis), never the document. If it scores far above chance,
the training labels can be partly guessed from surface cues and the fine-tuned model may learn them.
Trained on the ANLI rows of train_05b (three-way class), evaluated on dev_anli and test_anli.
Usage: groundone data shortcut [--version v1]
"""
import argparse
import json
import re
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score

from ..config import PROJECT

NEG = re.compile(r"\b(not|no|never|nobody|none|nothing|cannot|neither|nor)\b|n't", re.I)


def load(d, name):
    return [json.loads(l) for l in open(d / f"{name}.jsonl")]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="v1")
    d = PROJECT / "data" / "processed" / ap.parse_args(argv).version
    tr = [x for x in load(d, "train_05b") if x["source"] == "anli"]
    sets = {"dev_anli": load(d, "dev_anli"), "test_anli": load(d, "test_anli")}
    claim = lambda x: x["sentences"][x["idx"]]  # noqa: E731
    vec = CountVectorizer(ngram_range=(1, 2), min_df=3, lowercase=True)
    Xtr = vec.fit_transform([claim(x) for x in tr])
    ytr = [x["cls"] for x in tr]
    clf = LogisticRegression(max_iter=2000, C=1.0).fit(Xtr, ytr)
    out = {"train_rows": len(tr), "chance": 1 / 3}
    for name, items in sets.items():
        y = [x["cls"] for x in items]
        pred = clf.predict(vec.transform([claim(x) for x in items]))
        neg = np.array([bool(NEG.search(claim(x))) for x in items])
        out[name] = {"claim_only_bacc": round(balanced_accuracy_score(y, pred), 4),
                     "negation_rate_by_class": {c: round(float(neg[np.array(y) == c].mean()), 3) for c in sorted(set(y))}}
    trneg = np.array([bool(NEG.search(claim(x))) for x in tr])
    out["train_negation_rate_by_class"] = {c: round(float(trneg[np.array(ytr) == c].mean()), 3) for c in sorted(set(ytr))}
    # in-distribution reference: 5-fold-like holdout on train
    k = len(tr) // 5
    clf2 = LogisticRegression(max_iter=2000).fit(Xtr[k:], ytr[k:])
    out["train_holdout_claim_only_bacc"] = round(balanced_accuracy_score(ytr[:k], clf2.predict(Xtr[:k])), 4)
    (d / "shortcut_report.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
