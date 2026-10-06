"""Leakage check for the GroundOne dataset (dataset plan R6). Exits with code 1 if any hard check fails.

Hard checks (FAIL):
  1. No group (RAGTruth source, LLM-AggreFact document, VitaminC page) of dev/train appears in a test set.
  2. No document of dev/train appears (normalised text) in any test set.
  3. No (document, sentence) pair of dev/train appears in any test set.
  4. dev and train share no group.
Soft check (WARN): sentence strings of dev/train equal to a test sentence with a different document (short generic
sentences can coincide by chance).
Usage: groundone data check
"""
import json
import sys

from ..text import h, norm
from .build import OUT, TEST_FILES


def load(name):
    return [json.loads(l) for l in open(OUT / f"{name}.jsonl")]


def main(argv=None):
    tests = {n: load(n) for n in TEST_FILES}
    fit = {n: load(n) for n in ("dev", "train")}
    fails, warns, counts = [], [], {}
    t_groups = {n: {r["group"] for r in v} for n, v in tests.items()}
    t_docs = {n: {norm(r["doc"]) for r in v} for n, v in tests.items()}
    t_pairs = {n: {h(r["doc"], s) for r in v for s in r["sentences"]} for n, v in tests.items()}
    t_sents = {norm(s) for v in tests.values() for r in v for s, l in zip(r["sentences"], r["labels"]) if l is not None}
    for name, recs in fit.items():
        groups = {r["group"] for r in recs}
        docs = {norm(r["doc"]) for r in recs}
        pairs = {h(r["doc"], s) for r in recs for s in r["sentences"]}
        for t in tests:
            c = {"groups": len(groups & t_groups[t]), "docs": len(docs & t_docs[t]), "pairs": len(pairs & t_pairs[t])}
            counts[f"{name} vs {t}"] = c
            fails += [f"{name}: {v} {k} shared with {t}" for k, v in c.items() if v]
        same = sum(norm(s) in t_sents for r in recs for s, l in zip(r["sentences"], r["labels"]) if l is not None)
        counts[f"{name} sentences equal to a test sentence"] = same
        if same:
            warns.append(f"{name}: {same} sentence strings also occur in a test set (different documents)")
    shared = {r["group"] for r in fit["dev"]} & {r["group"] for r in fit["train"]}
    counts["dev vs train groups"] = len(shared)
    if shared:
        fails.append(f"dev and train share {len(shared)} groups")
    out = {"status": "FAIL" if fails else "PASS", "fails": fails, "warnings": warns, "counts": counts}
    (OUT / "leakage_report.json").write_text(json.dumps(out, indent=2))
    print(f"leakage check {out['status']}: {len(fails)} failures, {len(warns)} warnings")
    for x in fails + warns:
        print("  -", x)
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
