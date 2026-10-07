"""Baselines on the frozen GroundOne test sets (T1 RAGTruth, T3 VitaminC), same metrics as `groundone test`.

  encoder  B4: MiniCheck-RoBERTa / -DeBERTa / HHEM. One P(supported) per (document, sentence), documents chunked as in
           encoders.py, maximum over chunks. Binary metrics only (an encoder has no three-way output), by task and K band.
  rizzo    B3: Rizzo-Flow through its /v1/systemone API. State = document + numbered answer; one three-way `choice`
           question per scored sentence (K questions on one shared state). Three-way and binary metrics.
Outputs are create-only: results/<name>/<suite>/{predictions.parquet, metrics.json}.
Usage: groundone baselines frozen --system encoder --model minicheck-roberta --suite t1 --name minicheck-roberta [--limit N]
       groundone baselines frozen --system rizzo --url http://127.0.0.1:8017 --suite t1 --name rizzo-flow-4b-q4 --limit 300
"""
import argparse
import json
import random
import sys
import time

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

from ..config import RESULTS_DIR
from ..data.build import k_band
from ..eval.metrics import binary
from ..eval.tests import CLASSES, by, load, overlap, three_way

FILES = {"t1": "test_ragtruth", "t3": "test_vitaminc"}


def stratified(recs, n, seed=1234):
    """n records, proportional per task (T1) or per class (T3), fixed seed."""
    if not n or n >= len(recs):
        return recs
    key = (lambda r: r["task"]) if recs[0]["source"] == "ragtruth" else (lambda r: r["labels"][0])
    groups = {}
    for r in recs:
        groups.setdefault(key(r), []).append(r)
    rng = random.Random(seed)
    out = []
    for k in sorted(groups):
        g = groups[k][:]
        rng.shuffle(g)
        out += g[:round(n * len(g) / len(recs))]
    return out


def binary_by(df, col):
    return {str(k): binary((g["cls"] == "supported").astype(int), g["p_supported"]) for k, g in df.groupby(col) if len(g) >= 10}


def run_encoder(model, recs):
    from .encoders import make_scorer
    score, dev = make_scorer(model)
    rows, n = [], 0
    t0 = time.time()
    for r in recs:
        for i, y in enumerate(r["labels"]):
            if y is None:
                continue
            t = time.perf_counter()
            p = score(r["doc"], r["sentences"][i])
            rows.append({"id": f"{r['id']}-{i}", "cls": y, "task": r["task"], "K": r["meta"]["K"], "kband": k_band(r["meta"]["K"]),
                         "p_supported": p, "seconds": time.perf_counter() - t, "ov": overlap(r["sentences"][i], r["doc"])})
            n += 1
            if dev == "mps" and n % 50 == 0:
                import torch
                torch.mps.empty_cache()
            if n % 1000 == 0:
                el = time.time() - t0
                print(f"  [{model}] {n} sentences, {el / 60:.1f} min", flush=True)
    df = pd.DataFrame(rows)
    m = {"binary": binary((df["cls"] == "supported").astype(int), df["p_supported"]),
         "by_task": binary_by(df, "task"), "by_K_band": binary_by(df, "kband"),
         "baseline_word_overlap_auroc": float(roc_auc_score(df["cls"] == "supported", df["ov"])),
         "device": dev, "latency_per_sentence_p50_s": float(df["seconds"].median())}
    return df.drop(columns=["ov"]), m


def run_rizzo(url, recs):
    from .rizzo import post
    crit = {"supported": "supported by the document", "contradicted": "contradicted by the document",
            "not_mentioned": "neither supported nor contradicted (not mentioned)"}
    rows, skipped = [], 0
    for n, r in enumerate(recs):
        numbered = "\n".join(f"[{k + 1}] {s}" for k, s in enumerate(r["sentences"]))
        state = f"DOCUMENT:\n{r['doc']}\n\nANSWER (numbered sentences):\n{numbered}"
        idx = [i for i, y in enumerate(r["labels"]) if y is not None]
        qs = {f"s{i}": {"type": "choice", "instructions": f"Compared with the DOCUMENT, sentence [{i + 1}] is:", "criteria": crit}
              for i in idx}
        try:
            out, sec = post(url, {"model": "rizzo-latest", "state": state, "questions": qs})
        except Exception as e:  # noqa: BLE001  (e.g. over Rizzo's context limit)
            skipped += 1
            print("  skip", r["id"], str(e)[:80], flush=True)
            continue
        for i in idx:
            pr = out["answers"][f"s{i}"]["probabilities"]
            rows.append({"id": f"{r['id']}-{i}", "cls": r["labels"][i], "task": r["task"], "K": r["meta"]["K"],
                         "kband": k_band(r["meta"]["K"]), "p": [float(pr[c]) for c in CLASSES], "answer_seconds": sec,
                         "ov": overlap(r["sentences"][i], r["doc"])})
        if n % 25 == 0:
            print(f"  [rizzo] {n}/{len(recs)} records", flush=True)
    df = pd.DataFrame(rows)
    lat = df.drop_duplicates(["answer_seconds"])
    m = {"all": three_way(df), "by_task": by(df, "task"), "by_K_band": by(df, "kband"),
         "baseline_word_overlap_auroc": float(roc_auc_score(df["cls"] == "supported", df["ov"])),
         "skipped_records": skipped, "latency_per_answer_p50_s": float(lat["answer_seconds"].median())}
    return df.drop(columns=["ov"]), m


def main(argv=None):
    ap = argparse.ArgumentParser(prog="groundone baselines frozen")
    ap.add_argument("--system", choices=["encoder", "rizzo"], required=True)
    ap.add_argument("--model", default="minicheck-roberta", help="encoder: minicheck-roberta | minicheck-deberta | hhem")
    ap.add_argument("--url", default="http://127.0.0.1:8017")
    ap.add_argument("--suite", choices=list(FILES), required=True)
    ap.add_argument("--limit", type=int, default=0, help="stratified subsample of records (0 = all)")
    ap.add_argument("--name", required=True)
    a = ap.parse_args(argv)
    sd = RESULTS_DIR / a.name / a.suite
    if sd.exists():
        sys.exit(f"{sd} exists: results are create-only")
    recs = stratified(load(FILES[a.suite]), a.limit)
    t0 = time.time()
    df, m = run_encoder(a.model, recs) if a.system == "encoder" else run_rizzo(a.url, recs)
    sd.mkdir(parents=True)
    df.to_parquet(sd / "predictions.parquet")
    m.update({"system": a.system, "model": a.model if a.system == "encoder" else "rizzo-flow (server)", "test_file": FILES[a.suite],
              "records": len(recs), "limit": a.limit, "wall_minutes": round((time.time() - t0) / 60, 2)})
    (sd / "metrics.json").write_text(json.dumps(m, indent=2, default=str))
    head = m.get("binary", m.get("all", {}).get("binary", {}))
    print(f"[{a.system} {a.suite}] done in {m['wall_minutes']} min: bacc {head.get('bacc')}, auroc {head.get('auroc')}", flush=True)


if __name__ == "__main__":
    main()
