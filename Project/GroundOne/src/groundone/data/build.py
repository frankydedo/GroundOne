"""Phase 1: build GroundOne's training, dev and test sets (deterministic, versioned).

Follows the EDA recommendations (Project/EDA/report/eda_report.md §3) and plan §5:
  train  = MiniCheck synthetic (binary) + ANLI train (premises not in ANLI dev/test; three-way) + RAGTruth train
           (sentence level, quality = good, rebalanced; three-way), one question per row, prompts <= 2,048 tokens
  dev    = ANLI dev (official), RAGTruth dev (10 % of train sources, by source_id), MiniCheck dev (3 % of documents)
  test   = ANLI test (official), RAGTruth test (all sentences, quality = good), LLM-AggreFact test (evaluation only)
Outputs JSONL files + manifest.json + DATACARD.md in Project/data/processed/<version>/.

Usage: groundone data build [--version v1]
"""
import argparse
import hashlib
import json
import random
import sys
import time
from collections import Counter
from pathlib import Path

import pandas as pd

from ..config import PROJECT
from ..prompts import CONTRADICTED, NOT_MENTIONED, QTYPES, SUPPORTED, label_for, render
from ..text import norm, split_sentences

RAW = PROJECT / "data" / "raw"
TOKENIZER = "Qwen/Qwen2.5-0.5B-Instruct"  # same vocabulary and chat template as the 3B
CFG = {
    "seed": 1234,
    "cap_tokens": 2048,
    "anli_train_per_class": 7000,          # 21K total, like MiniCheck's ANLI share (not the identical subset)
    "ragtruth_dev_source_frac": 0.10,
    "ragtruth_train_target": {"contradicted": 2700, "not_mentioned": 2700, "supported": 2600},
    "ragtruth_dev_responses": 300,
    "minicheck_dev_doc_frac": 0.03,
    # one question per training row; lenient is weighted up because it is where the rules differ from the binary question
    "qtype_mix_threeway_sources": {"sup": 0.30, "three": 0.30, "strict": 0.15, "lenient": 0.25},
    "subset_3b_size": 10000,
}
CLS3 = {0: SUPPORTED, 1: NOT_MENTIONED, 2: CONTRADICTED}  # ANLI label ids


def context_of(task, info):
    if task == "QA":
        return f"Question: {info['question']}\n\n{info['passages']}"
    return info if isinstance(info, str) else json.dumps(info, ensure_ascii=False)


def pick_qtype(rng):
    r, acc = rng.random(), 0.0
    for q, w in CFG["qtype_mix_threeway_sources"].items():
        acc += w
        if r < acc:
            return q
    return "sup"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="v1")
    args = ap.parse_args(argv)
    if args.version == "v2":  # v2 has its own builder (D20–D22); v1 stays reproducible byte for byte
        from . import build_v2
        return build_v2.main(argv)
    out = PROJECT / "data" / "processed" / args.version
    out.mkdir(parents=True, exist_ok=True)
    rng = random.Random(CFG["seed"])
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(TOKENIZER)
    log = {"config": CFG, "created": time.strftime("%Y-%m-%d %H:%M:%S"), "notes": []}

    # ------------------------------------------------------------------ ANLI
    anli = {s: pd.concat([pd.read_parquet(RAW / "anli" / f"{s}_{r}.parquet").assign(round=r) for r in ["r1", "r2", "r3"]])
            for s in ["train", "dev", "test"]}
    held = set(anli["dev"]["premise"].map(norm)) | set(anli["test"]["premise"].map(norm))
    pool = anli["train"][~anli["train"]["premise"].map(norm).isin(held)].copy()
    log["anli_train_pool_after_premise_filter"] = len(pool)
    anli_train = pd.concat([g.sample(n=min(CFG["anli_train_per_class"], len(g)), random_state=CFG["seed"])
                            for _, g in pool.groupby("label")])

    def anli_item(r, split):
        return {"id": f"anli-{split}-{r.uid}", "source": "anli", "group": f"anli-p-{hashlib.sha1(norm(r.premise).encode()).hexdigest()[:12]}",
                "doc": r.premise, "sentences": [r.hypothesis], "idx": 0, "cls": CLS3[int(r.label)], "meta": {"round": r.round}}

    # ------------------------------------------------------------------ RAGTruth
    resp = [json.loads(l) for l in open(RAW / "ragtruth" / "response.jsonl")]
    src = {d["source_id"]: d for d in (json.loads(l) for l in open(RAW / "ragtruth" / "source_info.jsonl"))}
    resp = [r for r in resp if r["quality"] == "good"]
    train_sources = sorted({r["source_id"] for r in resp if r["split"] == "train"})
    rng_src = random.Random(CFG["seed"])
    rng_src.shuffle(train_sources)
    n_dev = int(len(train_sources) * CFG["ragtruth_dev_source_frac"])
    dev_sources = set(train_sources[:n_dev])

    def rt_sentences(r):
        s = src[r["source_id"]]
        sents = split_sentences(r["response"])
        texts = [t for _, _, t in sents]
        rows = []
        for i, (a, b, t) in enumerate(sents):
            types = [x["label_type"] for x in r["labels"] if a < x["end"] and x["start"] < b]
            cls = CONTRADICTED if any("Conflict" in x for x in types) else (NOT_MENTIONED if types else SUPPORTED)
            rows.append({"id": f"rt-{r['id']}-{i}", "source": "ragtruth", "group": f"rt-src-{r['source_id']}",
                         "doc": context_of(s["task_type"], s["source_info"]), "sentences": texts, "idx": i, "cls": cls,
                         "meta": {"task": s["task_type"], "model": r["model"], "response_id": r["id"],
                                  "implicit_true": any(x.get("implicit_true") for x in r["labels"] if a < x["end"] and x["start"] < b)}})
        return rows

    rt = {"train": [], "dev": [], "test": []}
    for r in resp:
        part = "test" if r["split"] == "test" else ("dev" if r["source_id"] in dev_sources else "train")
        rt[part] += rt_sentences(r)
    # rebalance RAGTruth train: all-class targets, sampled at the sentence level
    by_cls = {c: [x for x in rt["train"] if x["cls"] == c] for c in (SUPPORTED, CONTRADICTED, NOT_MENTIONED)}
    rt_train = []
    for c, n in CFG["ragtruth_train_target"].items():
        items = by_cls[c][:]
        rng.shuffle(items)
        rt_train += items[:n]
    log["ragtruth_train_available_by_class"] = {c: len(v) for c, v in by_cls.items()}
    # dev: sample whole responses (keeps K sentences together for the batched engine)
    dev_resp = sorted({x["meta"]["response_id"] for x in rt["dev"]})
    rng.shuffle(dev_resp)
    keep = set(dev_resp[:CFG["ragtruth_dev_responses"]])
    rt_dev = [x for x in rt["dev"] if x["meta"]["response_id"] in keep]

    # ------------------------------------------------------------------ MiniCheck synthetic
    mc = pd.concat([pd.read_parquet(RAW / "minicheck_synth" / f"{n}.parquet").assign(subset=n) for n in ["c2d", "d2c"]]).reset_index(drop=True)
    docs = sorted(mc["doc"].map(norm).unique())
    random.Random(CFG["seed"]).shuffle(docs)
    mc_dev_docs = set(docs[:int(len(docs) * CFG["minicheck_dev_doc_frac"])])

    def mc_item(i, r):
        return {"id": f"mc-{r.subset}-{i}", "source": "minicheck", "group": f"mc-d-{hashlib.sha1(norm(r.doc).encode()).hexdigest()[:12]}",
                "doc": r.doc, "sentences": [r.claim], "idx": 0, "cls": None, "binary": int(r.label), "meta": {"subset": r.subset}}

    mc_items = [mc_item(i, r) for i, r in enumerate(mc.itertuples())]
    mc_train = [x for x, d in zip(mc_items, mc["doc"].map(norm)) if d not in mc_dev_docs]
    mc_dev = [x for x, d in zip(mc_items, mc["doc"].map(norm)) if d in mc_dev_docs]

    # ------------------------------------------------------------------ LLM-AggreFact test (evaluation only, D18)
    ag = pd.read_parquet(RAW / "llm_aggrefact" / "test.parquet")
    ag_items = [{"id": f"agg-{i}", "source": "aggrefact", "group": f"agg-{r.dataset}", "doc": r.doc, "sentences": [r.claim], "idx": 0,
                 "cls": None, "binary": int(r.label), "meta": {"dataset": r.dataset}} for i, r in enumerate(ag.itertuples())]

    # ------------------------------------------------------------------ cross-dataset exclusions (found by check_leakage.py)
    agg_docs = {norm(x["doc"]) for x in ag_items}
    def not_in_agg(items, name):
        kept = [x for x in items if norm(x["doc"]) not in agg_docs]
        if len(kept) < len(items):
            log["notes"].append(f"{name}: removed {len(items) - len(kept)} items whose document is in LLM-AggreFact test")
        return kept
    rt_train, rt_dev, mc_train, mc_dev = (not_in_agg(rt_train, "ragtruth train"), not_in_agg(rt_dev, "ragtruth dev"),
                                          not_in_agg(mc_train, "minicheck train"), not_in_agg(mc_dev, "minicheck dev"))
    # ANLI's official dev and test share premises by design; dev is used for calibration, so drop dev premises seen in test
    test_premises = set(anli["test"]["premise"].map(norm))
    anli_dev = anli["dev"][~anli["dev"]["premise"].map(norm).isin(test_premises)]
    log["notes"].append(f"anli dev: removed {len(anli['dev']) - len(anli_dev)} pairs whose premise is also in ANLI test")

    # ------------------------------------------------------------------ training rows (one question each) + token cap
    train_items = [anli_item(r, "train") for r in anli_train.itertuples()] + rt_train + mc_train
    rows, dropped = [], Counter()
    for it in train_items:
        q = "sup" if it["cls"] is None else pick_qtype(rng)
        row = {**it, "qtype": q, "label": label_for(q, it["cls"], it.get("binary"))}
        row["n_tokens"] = len(tok.encode(render(tok, it["doc"], it["sentences"], it["idx"], q), add_special_tokens=False))
        if row["n_tokens"] > CFG["cap_tokens"]:
            dropped[it["source"]] += 1
            continue
        rows.append(row)
    rng.shuffle(rows)
    log["train_dropped_over_cap"] = dict(dropped)

    # 3B subset: stratified by (source, qtype)
    df = pd.DataFrame([{"k": f"{r['source']}|{r['qtype']}", "i": i} for i, r in enumerate(rows)])
    frac = CFG["subset_3b_size"] / len(rows)
    sub_idx = set(df.groupby("k", group_keys=False).apply(lambda g: g.sample(frac=frac, random_state=CFG["seed"]))["i"])
    rows_3b = [r for i, r in enumerate(rows) if i in sub_idx]

    # ------------------------------------------------------------------ write
    def write(name, items):
        with open(out / f"{name}.jsonl", "w") as f:
            for x in items:
                f.write(json.dumps(x, ensure_ascii=False) + "\n")
        return hashlib.sha256((out / f"{name}.jsonl").read_bytes()).hexdigest()

    files = {
        "train_05b": rows, "train_3b": rows_3b,
        "dev_anli": [anli_item(r, "dev") for r in anli_dev.itertuples()],
        "dev_ragtruth": rt_dev, "dev_minicheck": mc_dev,
        "test_anli": [anli_item(r, "test") for r in anli["test"].itertuples()],
        "test_ragtruth": rt["test"], "test_aggrefact": ag_items,
    }
    man = {"version": args.version, **log, "files": {}}
    for name, items in files.items():
        d = pd.DataFrame(items)
        info = {"rows": len(items), "sha256": write(name, items), "by_source": d["source"].value_counts().to_dict()}
        if "qtype" in d:
            info["by_qtype"] = d["qtype"].value_counts().to_dict()
            info["by_label"] = d["label"].value_counts().to_dict()
            info["tokens"] = {"mean": round(float(d["n_tokens"].mean()), 1), "p50": float(d["n_tokens"].median()),
                              "p90": float(d["n_tokens"].quantile(.9)), "total_M": round(d["n_tokens"].sum() / 1e6, 2)}
        if "cls" in d and d["cls"].notna().any():
            info["by_cls"] = d["cls"].value_counts().to_dict()
        if "binary" in d and d["binary"].notna().any():
            info["binary_supported_rate"] = round(float(d["binary"].mean()), 3)
        man["files"][name] = info
        print(f"{name:16s} {len(items):7d} rows")
    (out / "manifest.json").write_text(json.dumps(man, indent=2, default=str))
    print("manifest written to", out)


if __name__ == "__main__":
    main()
