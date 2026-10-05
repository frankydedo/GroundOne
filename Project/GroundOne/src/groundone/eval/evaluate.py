"""Evaluation suites and calibration fitting, all through the same Engine the server uses.

Suites (test files from data/processed/<version>/):
  aggrefact  LLM-AggreFact test, `sup` question; per sub-dataset balanced accuracy at 0.5, 11-way macro average and the
             RAG-subset average (plan §8.1). Documents longer than the cap are chunked; a claim's P(supported) is the
             maximum over chunks (as MiniCheck does); the number of chunked items is reported.
  ragtruth   RAGTruth test sentences, scored per answer with the shared prefix; questions configurable (default all 4)
  anli       ANLI test: three-way question and the strict / lenient rules (+ sup)
Calibration (`groundone calibrate`): predicts the dev sets with all question types, fits one temperature per question
type, writes calibration.json next to the adapter. Fitted on dev only (never on LLM-AggreFact, D18).
Outputs are create-only: results/<name>/<suite>/{predictions.parquet, metrics.json}.
"""
import argparse
import json
import random
import sys
import time

import numpy as np
import pandas as pd

from ..config import DATA_PROCESSED, RESULTS_DIR
from ..prompts import ANSWER_NAMES, QTYPES, label_for
from .metrics import binary, multiclass

RAG_SUBSET = ("RAGTruth", "Lfqa", "ClaimVerify", "ExpertQA")
CHUNK_TOKENS = 1500


def load_jsonl(path):
    return [json.loads(l) for l in open(path)]


def subsample(items, limit, key, seed=1234):
    if not limit or len(items) <= limit:
        return items
    rng = random.Random(seed)
    by = {}
    for it in items:
        by.setdefault(key(it), []).append(it)
    out = []
    for k in sorted(by):
        g = by[k][:]
        rng.shuffle(g)
        out += g[:max(1, round(limit * len(g) / len(items)))]
    return out


def chunk_doc(tok, doc, n):
    ids = tok.encode(doc, add_special_tokens=False)
    if len(ids) <= n:
        return [doc]
    step = n - 200
    return [tok.decode(ids[i:i + n]) for i in range(0, len(ids) - 200, step)]


def progress_printer(name):
    t0 = time.time()

    def p(done, total):
        el = time.time() - t0
        print(f"  [{name}] {done}/{total}  {el / 60:.1f} min, eta {el / max(done, 1) * (total - done) / 60:.1f} min", flush=True)
    return p


# ---------------------------------------------------------------------------------------------------- suites
def run_aggrefact(engine, items, limit):
    items = subsample(items, limit, lambda x: x["meta"]["dataset"])
    tok = engine.backend.tokenizer
    flat, owner, chunked = [], [], 0
    for n, it in enumerate(items):
        chunks = chunk_doc(tok, it["doc"], CHUNK_TOKENS)
        chunked += len(chunks) > 1
        for c in chunks:
            flat.append({"doc": c, "sentences": it["sentences"], "idx": 0, "qtype": "sup"})
            owner.append(n)
    preds = engine.predict(flat, progress=progress_printer("aggrefact"))
    p = np.zeros(len(items))
    for o, (_, ps) in zip(owner, preds):
        p[o] = max(p[o], ps[0])
    df = pd.DataFrame({"id": [x["id"] for x in items], "dataset": [x["meta"]["dataset"] for x in items],
                       "label": [x["binary"] for x in items], "p_supported": p})
    per = {d: binary(g["label"], g["p_supported"]) for d, g in df.groupby("dataset")}
    m = {"per_dataset": per, "macro_bacc": float(np.mean([v["bacc"] for v in per.values()])),
         "rag_subset_bacc": float(np.mean([per[d]["bacc"] for d in RAG_SUBSET if d in per])),
         "pooled": binary(df["label"], df["p_supported"]), "chunked_items": chunked, "n": len(items)}
    return df, m


def run_ragtruth(engine, items, limit, questions):
    if limit:
        resp = sorted({x["meta"]["response_id"] for x in items})
        random.Random(1234).shuffle(resp)
        keep = set(resp[:limit])
        items = [x for x in items if x["meta"]["response_id"] in keep]
    flat = [{**it, "qtype": q} for it in items for q in questions]
    preds = engine.predict(flat, progress=progress_printer("ragtruth"))
    rows = [{"id": f["id"], "task": f["meta"]["task"], "qtype": f["qtype"], "cls": f["cls"], "probs": ps}
            for f, (_, ps) in zip(flat, preds)]
    df = pd.DataFrame(rows)
    return df, {"n_sentences": len(items), "n_answers": len({x["meta"]["response_id"] for x in items}),
                "questions": questions, **qtype_metrics(df, by="task")}


def run_anli(engine, items, limit, questions):
    items = subsample(items, limit, lambda x: x["cls"])
    flat = [{**it, "qtype": q} for it in items for q in questions]
    preds = engine.predict(flat, progress=progress_printer("anli"))
    df = pd.DataFrame([{"id": f["id"], "qtype": f["qtype"], "cls": f["cls"], "probs": ps} for f, (_, ps) in zip(flat, preds)])
    return df, {"n": len(items), "questions": questions, **qtype_metrics(df)}


def qtype_metrics(df, by=None):
    """Metrics per question type against gold labels derived from the three-way class."""
    out = {}
    for q, g in df.groupby("qtype"):
        names = ANSWER_NAMES[q]
        gold = [("ABC".index(label_for(q, c))) for c in g["cls"]]
        probs = np.array(g["probs"].tolist())
        if q == "three":
            res = {"all": multiclass(gold, probs, names)}
            if by:
                res.update({k: multiclass([gold[i] for i in np.where(g[by].values == k)[0]], probs[g[by].values == k], names)
                            for k in sorted(g[by].unique())})
        else:
            y = 1 - np.array(gold)  # A (supported / acceptable) = 1
            res = {"all": binary(y, probs[:, 0])}
            if by:
                res.update({k: binary(y[g[by].values == k], probs[g[by].values == k, 0]) for k in sorted(g[by].unique())})
        out[q] = res
    return {"by_question": out}


# ---------------------------------------------------------------------------------------------------- entry points
def main(argv=None):
    from ..engine import Engine
    ap = argparse.ArgumentParser(prog="groundone eval")
    ap.add_argument("--suite", choices=["aggrefact", "ragtruth", "anli", "all"], default="all")
    ap.add_argument("--size")
    ap.add_argument("--adapter", help="run name under models/ or a directory; omit for the untrained base model")
    ap.add_argument("--calibration", help="calibration.json (default: <adapter>/calibration.json if present)")
    ap.add_argument("--data", default="v1")
    ap.add_argument("--limit", type=int, default=0, help="subsample (items; answers for ragtruth)")
    ap.add_argument("--questions", default=",".join(QTYPES))
    ap.add_argument("--name", required=True, help="results/<name>/ (create-only)")
    a = ap.parse_args(argv)
    out = RESULTS_DIR / a.name
    cal = a.calibration
    if cal is None and a.adapter:
        from ..config import resolve_model
        cand = __import__("pathlib").Path(resolve_model(a.size, a.adapter)[1]) / "calibration.json"
        cal = str(cand) if cand.exists() else None
    engine = Engine.load(a.size, a.adapter, cal)
    questions = [q for q in a.questions.split(",") if q]
    d = DATA_PROCESSED / a.data
    suites = ["aggrefact", "ragtruth", "anli"] if a.suite == "all" else [a.suite]
    for s in suites:
        sd = out / s
        if sd.exists():
            sys.exit(f"{sd} exists: results are create-only, choose another --name")
        t0 = time.time()
        items = load_jsonl(d / f"test_{s}.jsonl")
        if s == "aggrefact":
            df, m = run_aggrefact(engine, items, a.limit)
        elif s == "ragtruth":
            df, m = run_ragtruth(engine, items, a.limit, questions)
        else:
            df, m = run_anli(engine, items, a.limit, questions)
        sd.mkdir(parents=True)
        df.to_parquet(sd / "predictions.parquet")
        m.update({"model": engine.backend.metadata, "calibrated": engine.calibration is not None, "data": a.data,
                  "limit": a.limit, "wall_minutes": round((time.time() - t0) / 60, 2)})
        (sd / "metrics.json").write_text(json.dumps(m, indent=2, default=str))
        headline = m.get("macro_bacc") or {q: round(v["all"].get("bacc", v["all"].get("macro_recall")), 3) for q, v in m["by_question"].items()}
        print(f"[{s}] done in {m['wall_minutes']} min: {headline}", flush=True)


def calibrate(argv=None):
    from ..calibration import Calibration, fit_temperature, nll
    from ..engine import Engine
    ap = argparse.ArgumentParser(prog="groundone calibrate")
    ap.add_argument("--size")
    ap.add_argument("--adapter", required=True)
    ap.add_argument("--data", default="v1")
    ap.add_argument("--limit", type=int, default=1500, help="dev items per file")
    a = ap.parse_args(argv)
    engine = Engine.load(a.size, a.adapter)
    d = DATA_PROCESSED / a.data
    flat = []
    for name in ("dev_anli", "dev_ragtruth", "dev_minicheck"):
        items = subsample(load_jsonl(d / f"{name}.jsonl"), a.limit, lambda x: x.get("cls") or x.get("binary"))
        for it in items:
            qs = ["sup"] if it.get("cls") is None else list(QTYPES)
            for q in qs:
                lab = ("A" if it["binary"] == 1 else "B") if it.get("cls") is None else label_for(q, it["cls"])
                flat.append({**it, "qtype": q, "gold": "ABC".index(lab)})
    preds = engine.predict(flat, temperature=False, progress=progress_printer("calibrate"))
    temps, report = {}, {}
    for q in QTYPES:
        rows = [(lg, f["gold"]) for f, (lg, _) in zip(flat, preds) if f["qtype"] == q]
        if not rows:
            continue
        temps[q] = fit_temperature(rows)
        report[q] = {"n": len(rows), "temperature": round(temps[q], 4), "nll_before": round(nll(rows, 1.0), 4),
                     "nll_after": round(nll(rows, temps[q]), 4)}
    from ..config import resolve_model
    adir = __import__("pathlib").Path(resolve_model(a.size, a.adapter)[1])
    Calibration(temps, engine.backend.metadata["fingerprint"], {"fitted_on": "dev_anli + dev_ragtruth + dev_minicheck",
                                                                 "data": a.data, "report": report}).save(adir / "calibration.json")
    print(json.dumps(report, indent=2))
    print("written", adir / "calibration.json")
