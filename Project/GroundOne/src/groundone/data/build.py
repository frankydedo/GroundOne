"""Build the GroundOne dataset (docs/dataset_plan.md v2): one training source, three test sets.

  test_ragtruth   T1  RAGTruth official test split, one record per answer, three-way label per checkable sentence
  test_aggrefact  T2  LLM-AggreFact test (evaluation only, D18), one record per (document, claim), binary label
  test_vitaminc   T3  VitaminC test, real revisions only, 1,000 pairs per class, three-way label
  dev             RAGTruth train split, 10 % of sources (by source_id)
  train           RAGTruth train split, remaining sources
Record: {id, source, group, split, task, doc, sentences, labels, meta}; labels[i] is supported / contradicted /
not_mentioned (T2: supported / unsupported) or null for a sentence without checkable content (segment.py).
Writes Project/data/processed/groundone/: *.jsonl (gitignored), manifest.json, build_report.json, DATACARD.md.
If tests_frozen.json exists, the rebuilt test files must hash to the frozen values (otherwise the build fails).

Usage: groundone data build
"""
import hashlib
import json
import random
import re
import sys
import time
from collections import Counter, defaultdict

import pandas as pd

from ..config import PROJECT
from ..prompts import CONTRADICTED, NOT_MENTIONED, SUPPORTED
from ..text import norm
from .segment import segment

RAW = PROJECT / "data" / "raw"
OUT = PROJECT / "data" / "processed" / "groundone"
TOKENIZER = "Qwen/Qwen2.5-0.5B-Instruct"  # same vocabulary as the 3B
CFG = {"seed": 1234, "cap_tokens": 2048, "prompt_overhead_tokens": 80, "dev_source_frac": 0.10,
       "vitaminc_per_class": 1000, "k_bands": [[1, 4], [5, 8], [9, 13], [14, 999]]}
TEST_FILES = ("test_ragtruth", "test_aggrefact", "test_vitaminc")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def k_band(k):
    for lo, hi in CFG["k_bands"]:
        if lo <= k <= hi:
            return f"{lo}-{hi}" if hi < 999 else f">={lo}"
    return "0"


def context_of(task, info):
    if task == "QA":
        return f"Question: {info['question']}\n\n{info['passages']}"
    return info if isinstance(info, str) else json.dumps(info, ensure_ascii=False)


# ---------------------------------------------------------------------------------------------------- sources
def ragtruth(tok, report):
    resp = [json.loads(l) for l in open(RAW / "ragtruth" / "response.jsonl")]
    src = {d["source_id"]: d for d in (json.loads(l) for l in open(RAW / "ragtruth" / "source_info.jsonl"))}
    train_sources = sorted({r["source_id"] for r in resp if r["split"] == "train"})
    random.Random(CFG["seed"]).shuffle(train_sources)
    dev_sources = set(train_sources[:int(len(train_sources) * CFG["dev_source_frac"])])
    out = {"test": [], "dev": [], "train": []}
    drop = Counter()
    # R6: no training/dev document may appear in LLM-AggreFact test (one CNN article does)
    agg_docs = set(pd.read_parquet(RAW / "llm_aggrefact" / "test.parquet").doc.map(norm))
    lost_spans = 0
    for r in resp:
        part = "test" if r["split"] == "test" else ("dev" if r["source_id"] in dev_sources else "train")
        if r["quality"] != "good":
            drop[f"{part}: quality {r['quality']}"] += 1
            continue
        s = src[r["source_id"]]
        doc = context_of(s["task_type"], s["source_info"])
        if part != "test" and norm(doc) in agg_docs:
            drop[f"{part}: document in LLM-AggreFact test"] += 1
            continue
        sents = segment(r["response"])
        labels = []
        for x in sents:
            types = [l["label_type"] for l in r["labels"] if x.start < l["end"] and l["start"] < x.end]
            if not x.checkable:
                labels.append(None)
                continue
            labels.append(CONTRADICTED if any("Conflict" in t for t in types) else (NOT_MENTIONED if types else SUPPORTED))
        lost_spans += sum(not any(x.checkable and x.start < l["end"] and l["start"] < x.end for x in sents) for l in r["labels"])
        k = sum(l is not None for l in labels)
        if k == 0:
            drop[f"{part}: no checkable sentence"] += 1
            continue
        n_tok = len(tok.encode(doc)) + len(tok.encode(" ".join(x.text for x in sents))) + CFG["prompt_overhead_tokens"]
        if n_tok > CFG["cap_tokens"]:
            drop[f"{part}: over {CFG['cap_tokens']} tokens"] += 1
            continue
        out[part].append({"id": f"rt-{r['id']}", "source": "ragtruth", "group": f"rt-src-{r['source_id']}", "split": part,
                          "task": s["task_type"], "doc": doc, "sentences": [x.text for x in sents], "labels": labels,
                          "meta": {"K": k, "n_sentences": len(sents), "n_tokens": n_tok, "model": r["model"],
                                   "response_id": r["id"], "source_id": r["source_id"]}})
    report["ragtruth_dropped"] = dict(drop)
    report["ragtruth_spans_touching_no_checkable_sentence"] = lost_spans
    return out


def aggrefact():
    ag = pd.read_parquet(RAW / "llm_aggrefact" / "test.parquet")
    return [{"id": f"agg-{i}", "source": "aggrefact", "group": f"agg-{r.dataset}-{hashlib.sha1(norm(r.doc).encode()).hexdigest()[:12]}",
             "split": "test", "task": r.dataset, "doc": r.doc, "sentences": [r.claim],
             "labels": [SUPPORTED if int(r.label) == 1 else "unsupported"], "meta": {"K": 1}} for i, r in enumerate(ag.itertuples())]


def detok(t):
    """VitaminC text is tokenised ("UK ." / "( BPI )"); undo the spacing around punctuation only."""
    t = re.sub(r"\s+([.,;:!?%)\]])", r"\1", t)
    t = re.sub(r"([(\[$])\s+", r"\1", t)
    return re.sub(r"\s+'s\b", "'s", t).strip()


def vitaminc(report):
    d = pd.read_json(RAW / "vitaminc" / "test.jsonl", lines=True)
    real = d[d.revision_type == "real"]
    report["vitaminc_real_test_by_label"] = real.label.value_counts().to_dict()
    lab = {"SUPPORTS": SUPPORTED, "REFUTES": CONTRADICTED, "NOT ENOUGH INFO": NOT_MENTIONED}
    pick = pd.concat([g.sample(n=CFG["vitaminc_per_class"], random_state=CFG["seed"]) for _, g in real.groupby("label")])
    pick = pick.sort_values("unique_id")
    return [{"id": f"vitc-{r.unique_id}", "source": "vitaminc", "group": f"vitc-page-{r.page}", "split": "test",
             "task": "VitaminC", "doc": detok(r.evidence), "sentences": [detok(r.claim)], "labels": [lab[r.label]],
             "meta": {"K": 1, "case_id": r.case_id, "page": r.page}} for r in pick.itertuples()]


# ---------------------------------------------------------------------------------------------------- checks
def check_c2_c3(t1, report):
    """C2: segmentation vs LLM-AggreFact's RAGTruth claims; C3: our binary label vs LLM-AggreFact's label (reported)."""
    ag = pd.read_parquet(RAW / "llm_aggrefact" / "test.parquet")
    ag = ag[ag.dataset == "RAGTruth"]
    agl = defaultdict(set)
    for c, l in zip(ag.claim.map(norm), ag.label):
        agl[c].add(int(l))
    ours = {}
    for rec in t1:
        for s, l in zip(rec["sentences"], rec["labels"]):
            if l is not None:
                ours.setdefault(norm(s), set()).add(int(l == SUPPORTED))
    matched = set(agl) & set(ours)
    c2a = len(matched) / len(agl)
    c2b = sum(1 for c in ours if c not in agl) / len(ours)
    usable = [c for c in matched if len(agl[c]) == 1 and len(ours[c]) == 1]
    agree = sum(agl[c] == ours[c] for c in usable)
    dis = Counter(f"ours {'S' if next(iter(ours[c])) else 'notS'} / aggrefact {'S' if next(iter(agl[c])) else 'notS'}"
                  for c in usable if agl[c] != ours[c])
    report["C2"] = {"aggrefact_claims_found": round(c2a, 4), "our_sentences_absent": round(c2b, 4),
                    "pass": c2a >= 0.90 and c2b <= 0.10}
    report["C3"] = {"matched_unique_sentences": len(usable), "binary_agreement": round(agree / len(usable), 4),
                    "disagreements": dict(dis), "pass": agree / len(usable) >= 0.97}


def coverage(records):
    """C4: counts per task x K band x class (checkable sentences), and answers per K band."""
    cls, ans = Counter(), Counter()
    for r in records:
        b = k_band(r["meta"]["K"])
        ans[f"{r['task']}|{b}"] += 1
        for l in r["labels"]:
            if l is not None:
                cls[f"{r['task']}|{b}|{l}"] += 1
    flagged = sorted(k for k, v in cls.items() if v < 30 and k.split("|")[2] != SUPPORTED)
    return {"answers": dict(sorted(ans.items())), "sentences": dict(sorted(cls.items())), "cells_below_30": flagged}


def summary(records):
    labels = Counter(l for r in records for l in r["labels"] if l is not None)
    k = [r["meta"]["K"] for r in records]
    out = {"records": len(records), "labels": dict(labels), "decisions": sum(labels.values()),
           "null_sentences": sum(l is None for r in records for l in r["labels"]),
           "by_task": dict(Counter(r["task"] for r in records)),
           "K": {"mean": round(sum(k) / len(k), 2), "max": max(k), "answers_K_ge_14": sum(x >= 14 for x in k)}}
    if "n_tokens" in records[0]["meta"]:
        out["tokens_M"] = round(sum(r["meta"]["n_tokens"] for r in records) / 1e6, 2)
    return out


def trivial_baselines(records):
    """C5 (part): majority-class and uniform-random macro recall (balanced accuracy) of the three-way decision."""
    labels = [l for r in records for l in r["labels"] if l is not None]
    classes = sorted(set(labels))
    return {"majority_class": Counter(labels).most_common(1)[0][0], "majority_balanced_accuracy": round(1 / len(classes), 4),
            "random_balanced_accuracy": round(1 / len(classes), 4)}


# ---------------------------------------------------------------------------------------------------- main
def main(argv=None):
    from transformers import AutoTokenizer
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    tok = AutoTokenizer.from_pretrained(TOKENIZER)
    report = {"config": CFG, "created": time.strftime("%Y-%m-%d %H:%M:%S")}
    rt = ragtruth(tok, report)
    files = {"test_ragtruth": rt["test"], "test_aggrefact": aggrefact(), "test_vitaminc": vitaminc(report),
             "dev": rt["dev"], "train": rt["train"]}
    check_c2_c3(rt["test"], report)
    report["C4"] = {"test_ragtruth": coverage(rt["test"])}
    report["C5_trivial"] = {n: trivial_baselines(files[n]) for n in ("test_ragtruth", "test_vitaminc")}
    report["C5_reference"] = ("MiniCheck-RoBERTa on the unchanged LLM-AggreFact test: see results/minicheck-roberta/aggrefact "
                              "(measured 74.0 vs published 73.5)")
    report["summary"] = {n: summary(v) for n, v in files.items()}

    frozen_path = OUT / "tests_frozen.json"
    frozen = json.loads(frozen_path.read_text()) if frozen_path.exists() else None
    man = {"created": report["created"], "files": {}}
    for name, recs in files.items():
        p = OUT / f"{name}.jsonl"
        tmp = OUT / f".{name}.jsonl.tmp"
        with open(tmp, "w") as f:
            for r in recs:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        h = sha(tmp)
        if frozen and name in frozen["files"] and frozen["files"][name]["sha256"] != h:
            tmp.unlink()
            sys.exit(f"{name}: rebuilt file differs from the frozen test set (tests_frozen.json); refusing to overwrite")
        tmp.replace(p)
        man["files"][name] = {"records": len(recs), "sha256": h}
        print(f"{name:15s} {len(recs):6d} records  {report['summary'][name]['decisions']:7d} decisions")
    (OUT / "manifest.json").write_text(json.dumps(man, indent=2))
    (OUT / "build_report.json").write_text(json.dumps(report, indent=2, default=str))
    print("C2", report["C2"], "\nC3", report["C3"])
    print(f"written to {OUT} in {time.time() - t0:.0f} s")


def freeze(argv=None):
    """C6: record the SHA-256 of the test files; later builds must reproduce them exactly."""
    man = json.loads((OUT / "manifest.json").read_text())
    for n in TEST_FILES:
        if sha(OUT / f"{n}.jsonl") != man["files"][n]["sha256"]:
            sys.exit(f"{n}.jsonl does not match manifest.json; rebuild first")
    p = OUT / "tests_frozen.json"
    if p.exists():
        sys.exit("tests_frozen.json already exists: the test sets are frozen (changes need a decision-log entry)")
    p.write_text(json.dumps({"frozen": time.strftime("%Y-%m-%d %H:%M:%S"),
                             "files": {n: man["files"][n] for n in TEST_FILES}}, indent=2))
    print("test sets frozen:", p)


if __name__ == "__main__":
    main()
