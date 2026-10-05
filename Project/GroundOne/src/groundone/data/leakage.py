"""Phase 1: leakage check (plan §5.3). Exits with code 1 if any hard check fails.

Hard checks (FAIL):
  1. Group disjointness: no group (source document) of train/dev appears in any test set.
     (ANLI groups = premise hash; RAGTruth = source_id; MiniCheck = document hash.)
  2. No (document, sentence) pair of train/dev appears in any test set (normalised-text hash).
  3. No training/dev document appears among LLM-AggreFact test documents.
  4. Train and dev are disjoint by group within each source.
Soft checks (WARN, reported): identical claim text shared between train and LLM-AggreFact test with different documents
(short generic sentences can coincide by chance).
Usage: groundone data check [--version v1]
"""
import argparse
import json
import sys
from pathlib import Path

from ..config import PROJECT

from ..text import h, norm


def load(path):
    return [json.loads(l) for l in open(path)]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="v1")
    args = ap.parse_args(argv)
    d = PROJECT / "data" / "processed" / args.version
    sets = {p.stem: load(p) for p in sorted(d.glob("*.jsonl"))}
    train = {k: v for k, v in sets.items() if k.startswith("train")}
    dev = {k: v for k, v in sets.items() if k.startswith("dev")}
    test = {k: v for k, v in sets.items() if k.startswith("test")}
    fails, warns, report = [], [], {}

    def pairs(items):
        return {h(x["doc"], x["sentences"][x["idx"]]) for x in items}

    test_groups = {k: {x["group"] for x in v} for k, v in test.items()}
    test_pairs = {k: pairs(v) for k, v in test.items()}
    agg_docs = {norm(x["doc"]) for x in test["test_aggrefact"]}
    agg_claims = {norm(x["sentences"][0]) for x in test["test_aggrefact"]}

    for name, items in {**train, **dev}.items():
        g = {x["group"] for x in items}
        p = pairs(items)
        for tname in test:
            n_g = len(g & test_groups[tname])
            n_p = len(p & test_pairs[tname])
            report[f"{name} ∩ {tname}"] = {"groups": n_g, "pairs": n_p}
            if n_g:
                fails.append(f"{name}: {n_g} groups also in {tname}")
            if n_p:
                fails.append(f"{name}: {n_p} (document, sentence) pairs also in {tname}")
        n_doc = sum(norm(x["doc"]) in agg_docs for x in items)
        n_claim = sum(norm(x["sentences"][x["idx"]]) in agg_claims for x in items)
        report[f"{name} docs in test_aggrefact"] = n_doc
        report[f"{name} claims equal to an aggrefact test claim"] = n_claim
        if n_doc:
            fails.append(f"{name}: {n_doc} documents also in LLM-AggreFact test")
        if n_claim:
            warns.append(f"{name}: {n_claim} claim strings also appear in LLM-AggreFact test (with different documents)")

    for tname, titems in train.items():
        for dname, ditems in dev.items():
            for src in {x["source"] for x in ditems}:
                tg = {x["group"] for x in titems if x["source"] == src}
                dg = {x["group"] for x in ditems if x["source"] == src}
                n = len(tg & dg)
                report[f"{tname} ∩ {dname} ({src}) groups"] = n
                if n:
                    fails.append(f"{tname} and {dname} share {n} {src} groups")

    out = {"version": args.version, "status": "FAIL" if fails else "PASS", "fails": fails, "warnings": warns, "counts": report}
    (d / "leakage_report.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"leakage check {out['status']}: {len(fails)} failures, {len(warns)} warnings")
    for x in fails + warns:
        print("  -", x)
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
