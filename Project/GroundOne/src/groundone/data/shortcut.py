"""Claim-only shortcut baseline (dataset plan §6): a bag-of-words logistic regression that sees ONLY the sentence, never
the document. Trained on train, evaluated on dev and on the three-way test sets. If it scores far above chance, labels
can partly be guessed from surface cues, which a fine-tuned model may learn instead of checking the document.
Usage: groundone data shortcut
"""
import json

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score

from .build import OUT


def pairs(name):
    out = []
    for l in open(OUT / f"{name}.jsonl"):
        r = json.loads(l)
        out += [(s, y, r["task"]) for s, y in zip(r["sentences"], r["labels"]) if y is not None]
    return out


def main(argv=None):
    tr = pairs("train")
    vec = CountVectorizer(ngram_range=(1, 2), min_df=3)
    clf = LogisticRegression(max_iter=3000, class_weight="balanced").fit(vec.fit_transform([s for s, _, _ in tr]), [y for _, y, _ in tr])
    out = {"train_sentences": len(tr), "chance_balanced_accuracy": round(1 / 3, 4)}
    for name in ("dev", "test_ragtruth", "test_vitaminc"):
        p = pairs(name)
        pred = clf.predict(vec.transform([s for s, _, _ in p]))
        out[name] = round(balanced_accuracy_score([y for _, y, _ in p], pred), 4)
        if name == "test_ragtruth":
            for t in sorted({t for _, _, t in p}):
                idx = [i for i, x in enumerate(p) if x[2] == t]
                out[f"{name}|{t}"] = round(balanced_accuracy_score([p[i][1] for i in idx], [pred[i] for i in idx]), 4)
    (OUT / "shortcut_report.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
