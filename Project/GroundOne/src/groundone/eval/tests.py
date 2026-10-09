"""Evaluation on the frozen GroundOne test sets (dataset plan §4), single three-way question (D20).

  t1  RAGTruth test: every scored sentence of every answer, shared prefix per answer. Three-way balanced accuracy
      (macro recall), per-class recall, predicted shares, binary balanced accuracy at 0.5 and AUROC of P(supported),
      strict / lenient policies, all by task and by K band; plus the word-overlap baseline on the same sentences.
  t3  VitaminC test: same metrics (K = 1).
  t2  LLM-AggreFact test: P(supported) at 0.5, per sub-dataset, 11-way macro and RAG subset; documents longer than
      the cap are chunked and the maximum over chunks is kept.
  --decision generate (t1/t3, design b; control B2): same forward pass, but the verdict is the full-vocabulary argmax
      token at each marker, i.e. what greedy single-token generation would emit. "A"/"B"/"C" with or without a leading
      space map to the three classes; any other token is a format failure (counted as wrong). Also reports the
      agreement with the 3-letter readout.
Outputs are create-only: results/<name>/<suite>/{predictions.parquet, metrics.json}.
Usage: groundone test --suite t1|t2|t3 [--adapter RUN] --name NAME [--design b|a] [--decision readout|generate] [--limit N]
"""
import argparse
import json
import random
import re
import sys
import time

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

from ..config import RESULTS_DIR
from ..data.build import OUT, k_band
from .evaluate import CHUNK_TOKENS, RAG_SUBSET, chunk_doc, progress_printer
from .metrics import binary

CLASSES = ("supported", "contradicted", "not_mentioned")
STOP = set("a an the of in on at to for and or is are was were be been by with as that this it its from has have had".split())


def load(name):
    return [json.loads(l) for l in open(OUT / f"{name}.jsonl")]


def overlap(c, e):
    cw = {w for w in re.findall(r"[a-z0-9]+", c.lower()) if w not in STOP}
    return len(cw & set(re.findall(r"[a-z0-9]+", e.lower()))) / max(len(cw), 1)


def three_way(df):
    """df: columns cls, p (3 probabilities in letter order A/B/C = supported/contradicted/not_mentioned)."""
    P = np.array(df["p"].tolist())
    y = np.array([CLASSES.index(c) for c in df["cls"]])
    pred = P.argmax(1)
    rec = {c: float((pred[y == k] == k).mean()) for k, c in enumerate(CLASSES) if (y == k).any()}
    out = {"n": int(len(y)), "macro_recall": float(np.mean(list(rec.values()))), "recall": rec,
           "predicted_share": {c: round(float((pred == k).mean()), 4) for k, c in enumerate(CLASSES)}}
    sup = (y == 0).astype(int)
    out["binary"] = binary(sup, P[:, 0])                                  # supported vs not, threshold 0.5
    if 0 < (y == 1).sum() < len(y):
        out["lenient_auroc"] = float(roc_auc_score((y != 1).astype(int), 1 - P[:, 1]))  # not contradicted vs contradicted
        out["lenient_bacc"] = float(np.mean([((P[:, 1] <= 0.5)[y != 1]).mean(), ((P[:, 1] > 0.5)[y == 1]).mean()]))
    return out


def by(df, col):
    return {str(k): three_way(g) for k, g in df.groupby(col) if len(g) >= 10}


def answer_items(recs):
    flat = []
    for r in recs:
        for i, y in enumerate(r["labels"]):
            if y is not None:
                flat.append({"id": f"{r['id']}-{i}", "doc": r["doc"], "sentences": r["sentences"], "idx": i, "qtype": "three",
                             "cls": y, "task": r["task"], "K": r["meta"]["K"], "kband": k_band(r["meta"]["K"])})
    return flat


def score_b(engine, recs, raw=False):
    """Design (b): one pass per record, logits at the markers. Returns one probability triple per scored sentence
    (calibrated if the engine has a calibration), or the raw logits with raw=True."""
    from ..calibration import softmax
    from ..prompts import encode_marked
    tok = engine.backend.tokenizer
    enc = [encode_marked(tok, r["doc"], r["sentences"], [l is not None for l in r["labels"]]) for r in recs]
    out = []
    for start in range(0, len(enc), 200):
        chunk = enc[start:start + 200]
        lg = engine._run(engine.backend.score_positions, [e[0] for e in chunk], [e[1] for e in chunk])
        cal = engine.calibration
        out += [x if raw else (cal.probs("three", x) if cal else softmax(x)) for per in lg for x in per]
        print(f"  [{start + len(chunk)}/{len(enc)}]", flush=True)
    return out


def run_generate(engine, recs):
    """Control B2: verdict = full-vocabulary argmax at each marker (one pass per answer, same as the readout)."""
    from ..prompts import encode_marked
    be, tok = engine.backend, engine.backend.tokenizer
    to_cls = {}
    for k, L in enumerate("ABC"):
        to_cls[be.letter_ids[L]] = k
        to_cls[tok.encode(" " + L, add_special_tokens=False)[0]] = k
    enc = [encode_marked(tok, r["doc"], r["sentences"], [l is not None for l in r["labels"]]) for r in recs]
    lg, am = [], []
    for start in range(0, len(enc), 200):
        chunk = enc[start:start + 200]
        l, a = engine._run(lambda: be.score_positions([e[0] for e in chunk], [e[1] for e in chunk], with_argmax=True))
        lg += [x for per in l for x in per]
        am += [x for per in a for x in per]
        print(f"  [{start + len(chunk)}/{len(enc)}]", flush=True)
    flat = answer_items(recs)
    df = pd.DataFrame([{k: f[k] for k in ("id", "cls", "task", "K", "kband")} for f in flat])
    df["token"] = [tok.decode([t]) for t in am]
    df["pred_generate"] = [to_cls.get(t, -1) for t in am]
    df["pred_readout"] = [int(np.argmax(x)) for x in lg]
    y = np.array([CLASSES.index(c) for c in df["cls"]])

    def macro(pred, mask=None):
        mask = np.ones(len(y), bool) if mask is None else mask
        return float(np.mean([(pred[mask & (y == k)] == k).mean() for k in range(3) if (mask & (y == k)).any()]))
    pg, pr = df["pred_generate"].to_numpy(), df["pred_readout"].to_numpy()
    m = {"decision": "generate (full-vocabulary argmax at the markers; B2)", "n": int(len(df)), "n_answers": len(recs),
         "macro_recall_generate_failures_wrong": macro(pg), "macro_recall_readout": macro(pr),
         "format_failure_rate": float((pg == -1).mean()), "agreement_with_readout": float((pg == pr).mean()),
         "spaced_letter_rate": float(np.mean([t.startswith(" ") and t.strip() in "ABC" and t.strip() != "" for t in df["token"]])),
         "top_tokens": df["token"].value_counts().head(8).to_dict(),
         "by_task": {t: {"generate": macro(pg, (df["task"] == t).to_numpy()), "readout": macro(pr, (df["task"] == t).to_numpy())}
                     for t in sorted(df["task"].unique())},
         "by_K_band": {b: {"generate": macro(pg, (df["kband"] == b).to_numpy()), "readout": macro(pr, (df["kband"] == b).to_numpy())}
                       for b in sorted(df["kband"].unique())}}
    return df, m


def run_threeway(engine, recs, name, design="b"):
    flat = answer_items(recs)
    if design == "b":
        preds = [(None, p) for p in score_b(engine, recs)]
    else:
        preds = engine.predict(flat, progress=progress_printer(name))
    df = pd.DataFrame([{k: f[k] for k in ("id", "cls", "task", "K", "kband")} | {"p": list(map(float, p))}
                       for f, (_, p) in zip(flat, preds)])
    ov = np.array([overlap(f["sentences"][f["idx"]], f["doc"]) for f in flat])
    m = {"all": three_way(df), "by_task": by(df, "task"), "by_K_band": by(df, "kband"),
         "baseline_word_overlap_auroc": float(roc_auc_score(df["cls"] == "supported", ov)),
         "n_answers": len(recs)}
    return df, m


def run_aggrefact(engine, recs, design="b"):
    tok = engine.backend.tokenizer
    flat, owner, chunked = [], [], 0
    for n, r in enumerate(recs):
        chunks = chunk_doc(tok, r["doc"], CHUNK_TOKENS)
        chunked += len(chunks) > 1
        for c in chunks:
            flat.append({"doc": c, "sentences": r["sentences"], "idx": 0, "qtype": "three"})
            owner.append(n)
    if design == "b":
        preds = [(None, x) for x in score_b(engine, [{"doc": f["doc"], "sentences": f["sentences"], "labels": ["x"]} for f in flat])]
    else:
        preds = engine.predict(flat, progress=progress_printer("t2"))
    p = np.zeros(len(recs))
    p3 = [[0.0, 0.0, 0.0] for _ in recs]
    for o, (_, ps) in zip(owner, preds):
        if ps[0] >= p[o]:
            p[o], p3[o] = ps[0], list(map(float, ps))
    df = pd.DataFrame({"id": [r["id"] for r in recs], "dataset": [r["task"] for r in recs],
                       "label": [int(r["labels"][0] == "supported") for r in recs], "p_supported": p, "p": p3})
    per = {d: binary(g["label"], g["p_supported"]) for d, g in df.groupby("dataset")}
    return df, {"per_dataset": per, "macro_bacc": float(np.mean([v["bacc"] for v in per.values()])),
                "rag_subset_bacc": float(np.mean([per[d]["bacc"] for d in RAG_SUBSET if d in per])),
                "pooled": binary(df["label"], df["p_supported"]), "chunked_items": chunked, "n": len(recs)}


def main(argv=None):
    from ..engine import Engine
    ap = argparse.ArgumentParser(prog="groundone test")
    ap.add_argument("--suite", choices=["t1", "t2", "t3"], required=True)
    ap.add_argument("--size")
    ap.add_argument("--adapter")
    ap.add_argument("--calibration")
    ap.add_argument("--name", required=True)
    ap.add_argument("--limit", type=int, default=0, help="debug: random N records only")
    ap.add_argument("--design", choices=["a", "b"], default="b", help="readout design the adapter was trained for")
    ap.add_argument("--decision", choices=["readout", "generate"], default="readout",
                    help="generate = control B2 (t1/t3, design b): full-vocabulary argmax at the markers")
    a = ap.parse_args(argv)
    sd = RESULTS_DIR / a.name / a.suite
    if sd.exists():
        sys.exit(f"{sd} exists: results are create-only")
    engine = Engine.load(a.size, a.adapter, a.calibration)
    file = {"t1": "test_ragtruth", "t2": "test_aggrefact", "t3": "test_vitaminc"}[a.suite]
    recs = load(file)
    if a.limit:
        recs = random.Random(0).sample(recs, min(a.limit, len(recs)))
    t0 = time.time()
    if a.decision == "generate":
        if a.suite == "t2" or a.design != "b":
            sys.exit("--decision generate needs --suite t1|t3 and design b")
        df, m = run_generate(engine, recs)
    else:
        df, m = run_aggrefact(engine, recs, a.design) if a.suite == "t2" else run_threeway(engine, recs, a.suite, a.design)
    sd.mkdir(parents=True)
    df.to_parquet(sd / "predictions.parquet")
    m.update({"design": a.design, "model": engine.backend.metadata, "calibrated": engine.calibration is not None, "test_file": file,
              "limit": a.limit, "wall_minutes": round((time.time() - t0) / 60, 2)})
    (sd / "metrics.json").write_text(json.dumps(m, indent=2, default=str))
    head = m.get("macro_bacc") or ({k: m[k] for k in ("macro_recall_generate_failures_wrong", "macro_recall_readout",
                                                       "format_failure_rate", "agreement_with_readout")}
                                   if a.decision == "generate" else None) or {"macro_recall": round(m["all"]["macro_recall"], 4), "auroc": m["all"]["binary"]["auroc"],
                                   "predicted_share": m["all"]["predicted_share"]}
    print(f"[{a.suite}] done in {m['wall_minutes']} min: {head}", flush=True)


if __name__ == "__main__":
    main()
