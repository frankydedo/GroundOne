"""Datasets v2 (decisions D20–D22, Project/docs/analysis_2026-10-06.md).

What changes from v1 (diagnosis of run g1-05b-v1: rules learned as label priors, multi-sentence format weak):
  D20  every item with a three-way class is trained with ALL FOUR questions (sup, three, strict, lenient) as separate
       rows, so the same (document, sentence) appears with answers that differ only because the question differs.
  D21  more multi-sentence training: synthetic ANLI answers (3–12 hypotheses of one premise, numbered, each with its own
       human label; up to 3 target sentences per answer) and RAGTruth sentences sampled class-balanced from full
       answers, with long answers (K >= 14) weighted x2. MiniCheck stays pair format, `sup` only.
  D22  fixed dev file `dev_mix` (every item with all four questions, four blocks: ANLI pairs, ANLI multi-sentence,
       RAGTruth, MiniCheck) used for checkpoint selection on mean balanced accuracy; `dev_anli_multi` is also used by
       calibration so that it sees the multi-sentence format.
Test sets are copied byte-for-byte from v1 (results stay comparable); dev_anli / dev_ragtruth / dev_minicheck too.
ANLI multi-sentence dev premises are reserved from the ANLI train pool (disjoint from dev/test by construction).

Usage: groundone data build --version v2
"""
import argparse
import hashlib
import json
import random
import shutil
import time
from collections import Counter

import pandas as pd

from ..config import PROJECT
from ..prompts import CONTRADICTED, NOT_MENTIONED, QTYPES, SUPPORTED, label_for, render
from ..text import norm, split_sentences
from .build import CLS3, TOKENIZER, context_of

RAW = PROJECT / "data" / "raw"
CFG = {
    "seed": 4321,
    "cap_tokens": 2048,
    "anli_multi_targets": 3500,         # target hypotheses inside synthetic multi-sentence answers
    "anli_multi_k": (3, 12),            # sentences per synthetic answer
    "anli_multi_targets_per_answer": 3,
    "anli_pair_targets": 2000,          # target hypotheses in pair format (K = 1)
    "anli_dev_premise_frac": 0.02,      # train-pool premises reserved for the multi-sentence dev
    "ragtruth_targets_per_class": 700,
    "ragtruth_long_k": 14,
    "ragtruth_long_weight": 2.0,
    "minicheck_rows": 10000,
    "dev_mix_per_block": 120,           # items per block (x4 questions, except MiniCheck)
}
CLASSES = (SUPPORTED, CONTRADICTED, NOT_MENTIONED)


def weighted_sample(items, n, weight, rng):
    """n items without replacement, P proportional to weight (Efraimidis–Spirakis keys)."""
    return sorted(items, key=lambda x: -rng.random() ** (1.0 / weight(x)))[:n]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="v2")
    args = ap.parse_args(argv)
    v1 = PROJECT / "data" / "processed" / "v1"
    out = PROJECT / "data" / "processed" / args.version
    out.mkdir(parents=True, exist_ok=True)
    rng = random.Random(CFG["seed"])
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(TOKENIZER)
    log = {"config": CFG, "created": time.strftime("%Y-%m-%d %H:%M:%S"), "notes": []}

    def n_tokens(it, q):
        return len(tok.encode(render(tok, it["doc"], it["sentences"], it["idx"], q), add_special_tokens=False))

    def four(it):
        return [{**it, "qtype": q, "label": label_for(q, it["cls"])} for q in QTYPES]

    # ------------------------------------------------------------------ ANLI: premise groups
    anli = {s: pd.concat([pd.read_parquet(RAW / "anli" / f"{s}_{r}.parquet").assign(round=r) for r in ["r1", "r2", "r3"]])
            for s in ["train", "dev", "test"]}
    held = set(anli["dev"]["premise"].map(norm)) | set(anli["test"]["premise"].map(norm))
    pool = anli["train"][~anli["train"]["premise"].map(norm).isin(held)].copy()
    pool["pkey"] = pool["premise"].map(norm)
    premises = sorted(pool["pkey"].unique())
    rng.shuffle(premises)
    n_dev = int(len(premises) * CFG["anli_dev_premise_frac"])
    dev_prem, train_prem = premises[:n_dev], premises[n_dev:]
    by_prem = {k: g for k, g in pool.groupby("pkey")}

    def group_of(p):
        return f"anli-p-{hashlib.sha1(p.encode()).hexdigest()[:12]}"

    def balanced_hyps(g, k):
        """Up to k hypotheses of one premise, round-robin over labels (keeps classes mixed inside an answer)."""
        lists = [list(x.sample(frac=1, random_state=rng.randrange(2**31)).itertuples()) for _, x in g.groupby("label")]
        rng.shuffle(lists)
        picked = []
        while len(picked) < k and any(lists):
            for l in lists:
                if l and len(picked) < k:
                    picked.append(l.pop())
        rng.shuffle(picked)
        return picked

    def anli_multi(p, split, n_targets):
        g = by_prem[p]
        lo, hi = CFG["anli_multi_k"]
        hyps = balanced_hyps(g, rng.randint(lo, hi))
        if len(hyps) < 2:
            return []
        sents = [r.hypothesis for r in hyps]
        idxs = rng.sample(range(len(hyps)), min(n_targets, len(hyps)))
        return [{"id": f"anlim-{split}-{hyps[i].uid}", "source": "anli", "group": group_of(p), "doc": hyps[i].premise,
                 "sentences": sents, "idx": i, "cls": CLS3[int(hyps[i].label)],
                 "meta": {"round": hyps[i].round, "format": "multi", "K": len(sents)}} for i in idxs]

    def anli_pair(r, split):
        return {"id": f"anli-{split}-{r.uid}", "source": "anli", "group": group_of(norm(r.premise)), "doc": r.premise,
                "sentences": [r.hypothesis], "idx": 0, "cls": CLS3[int(r.label)], "meta": {"round": r.round, "format": "pair"}}

    # multi-sentence answers from the first train premises, pairs from the remaining ones (no premise in both)
    anli_m, used = [], 0
    for p in train_prem:
        if len(anli_m) >= CFG["anli_multi_targets"]:
            break
        anli_m += anli_multi(p, "train", CFG["anli_multi_targets_per_answer"])
        used += 1
    rest = pool[pool["pkey"].isin(set(train_prem[used:]))]
    per_cls = CFG["anli_pair_targets"] // 3
    anli_p = [anli_pair(r, "train") for _, g in rest.groupby("label")
              for r in g.sample(n=min(per_cls, len(g)), random_state=CFG["seed"]).itertuples()]
    log["anli"] = {"pool": len(pool), "premises": len(premises), "dev_premises": n_dev, "multi_premises": used,
                   "multi_targets": len(anli_m), "pair_targets": len(anli_p)}

    anli_dev_multi = []
    for p in dev_prem:
        anli_dev_multi += anli_multi(p, "dev", 1)

    # ------------------------------------------------------------------ RAGTruth: class-balanced targets in full answers
    resp = [json.loads(l) for l in open(RAW / "ragtruth" / "response.jsonl")]
    src = {d["source_id"]: d for d in (json.loads(l) for l in open(RAW / "ragtruth" / "source_info.jsonl"))}
    resp = [r for r in resp if r["quality"] == "good"]
    # same dev sources as v1 (seed 1234 in build.py), so dev_ragtruth stays disjoint from training
    train_sources = sorted({r["source_id"] for r in resp if r["split"] == "train"})
    random.Random(1234).shuffle(train_sources)
    dev_sources = set(train_sources[:int(len(train_sources) * 0.10)])
    agg_docs = {norm(json.loads(l)["doc"]) for l in open(v1 / "test_aggrefact.jsonl")}
    rt = []
    for r in resp:
        if r["split"] == "test" or r["source_id"] in dev_sources:
            continue
        s = src[r["source_id"]]
        doc = context_of(s["task_type"], s["source_info"])
        if norm(doc) in agg_docs:
            continue
        sents = split_sentences(r["response"])
        texts = [t for _, _, t in sents]
        for i, (a, b, t) in enumerate(sents):
            types = [x["label_type"] for x in r["labels"] if a < x["end"] and x["start"] < b]
            cls = CONTRADICTED if any("Conflict" in x for x in types) else (NOT_MENTIONED if types else SUPPORTED)
            rt.append({"id": f"rt-{r['id']}-{i}", "source": "ragtruth", "group": f"rt-src-{r['source_id']}", "doc": doc,
                       "sentences": texts, "idx": i, "cls": cls,
                       "meta": {"task": s["task_type"], "model": r["model"], "response_id": r["id"], "format": "multi",
                                "K": len(texts)}})
    w = lambda x: CFG["ragtruth_long_weight"] if x["meta"]["K"] >= CFG["ragtruth_long_k"] else 1.0
    rt_train = []
    for c in CLASSES:
        cand = [x for x in rt if x["cls"] == c]
        rt_train += weighted_sample(cand, CFG["ragtruth_targets_per_class"] * 2, w, rng)  # x2: margin for the token cap
    log["ragtruth_available_by_class"] = dict(Counter(x["cls"] for x in rt))

    # ------------------------------------------------------------------ MiniCheck (pair, sup only): reuse v1 rows
    mc_v1 = [json.loads(l) for l in open(v1 / "train_05b.jsonl")]
    mc_v1 = [x for x in mc_v1 if x["source"] == "minicheck"]
    rng.shuffle(mc_v1)
    mc_train = [{**x, "meta": {**x["meta"], "format": "pair"}} for x in mc_v1[:CFG["minicheck_rows"]]]

    # ------------------------------------------------------------------ training rows + token cap
    rows, dropped = [], Counter()
    rt_kept = Counter()
    for it in anli_m + anli_p + rt_train:
        if it["source"] == "ragtruth" and rt_kept[it["cls"]] >= CFG["ragtruth_targets_per_class"]:
            continue
        rs = four(it)
        lens = [n_tokens(it, r["qtype"]) for r in rs]
        if max(lens) > CFG["cap_tokens"]:
            dropped[it["source"]] += 1
            continue
        if it["source"] == "ragtruth":
            rt_kept[it["cls"]] += 1
        rows += [{**r, "n_tokens": n} for r, n in zip(rs, lens)]
    for x in mc_train:
        rows.append(x)  # already has qtype, label, n_tokens (same prompt version)
    rng.shuffle(rows)
    log["train_dropped_over_cap_items"] = dict(dropped)

    # ------------------------------------------------------------------ dev_mix (D22): fixed, all four questions
    k = CFG["dev_mix_per_block"]

    def balanced(items, n):
        out_ = []
        for c in CLASSES:
            cand = [x for x in items if x["cls"] == c]
            rng.shuffle(cand)
            out_ += cand[:n // 3]
        return out_

    dev_anli_v1 = [json.loads(l) for l in open(v1 / "dev_anli.jsonl")]
    dev_rt_v1 = [json.loads(l) for l in open(v1 / "dev_ragtruth.jsonl")]
    dev_mc_v1 = [json.loads(l) for l in open(v1 / "dev_minicheck.jsonl")]
    blocks = {"anli_pair": balanced(dev_anli_v1, k), "anli_multi": balanced(anli_dev_multi, k),
              "ragtruth": balanced(dev_rt_v1, k)}
    dev_mix = [{**r, "block": b} for b, items in blocks.items() for it in items for r in four(it)]
    rng.shuffle(dev_mc_v1)
    dev_mix += [{**x, "qtype": "sup", "label": "A" if x["binary"] == 1 else "B", "block": "minicheck"} for x in dev_mc_v1[:k]]

    # ------------------------------------------------------------------ write
    def write(name, items):
        with open(out / f"{name}.jsonl", "w") as f:
            for x in items:
                f.write(json.dumps(x, ensure_ascii=False) + "\n")
        return hashlib.sha256((out / f"{name}.jsonl").read_bytes()).hexdigest()

    for name in ("test_anli", "test_ragtruth", "test_aggrefact", "dev_anli", "dev_ragtruth", "dev_minicheck"):
        shutil.copy2(v1 / f"{name}.jsonl", out / f"{name}.jsonl")
    files = {"train_05b": rows, "dev_mix": dev_mix, "dev_anli_multi": anli_dev_multi}
    man = {"version": args.version, **log, "copied_from_v1": ["test_*", "dev_anli", "dev_ragtruth", "dev_minicheck"], "files": {}}
    for name, items in files.items():
        d = pd.DataFrame(items)
        fmt = d["sentences"].map(lambda s: "multi" if len(s) > 1 else "pair")
        info = {"rows": len(items), "sha256": write(name, items), "by_source": d["source"].value_counts().to_dict(),
                "by_format": fmt.value_counts().to_dict()}
        if "qtype" in d:
            info["by_qtype"] = d["qtype"].value_counts().to_dict()
            info["by_source_qtype_label"] = {"|".join(k): int(v) for k, v in d.groupby(["source", "qtype", "label"]).size().items()}
        if "n_tokens" in d:
            info["tokens"] = {"mean": round(float(d["n_tokens"].mean()), 1), "p50": float(d["n_tokens"].median()),
                              "p90": float(d["n_tokens"].quantile(.9)), "total_M": round(d["n_tokens"].sum() / 1e6, 2)}
            info["tokens_by_source_M"] = (d.groupby("source")["n_tokens"].sum() / 1e6).round(2).to_dict()
        if "block" in d:
            info["by_block"] = d["block"].value_counts().to_dict()
        K = d["sentences"].map(len)
        info["K"] = {"mean": round(float(K.mean()), 2), "share_K_ge_14": round(float((K >= 14).mean()), 3)}
        man["files"][name] = info
        print(f"{name:16s} {len(items):7d} rows  {info.get('tokens', '')}")
    (out / "manifest.json").write_text(json.dumps(man, indent=2, default=str))
    print("manifest written to", out)


if __name__ == "__main__":
    main()
