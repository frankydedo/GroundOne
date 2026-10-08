"""LEGACY entry point (earlier test files). `make_scorer` and `chunks` are reused by baselines/frozen.py, which runs the encoders on the frozen tests.

Baseline B4: encoder fact-checkers (MiniCheck-RoBERTa/-DeBERTa, HHEM-2.1-open) on the processed test sets.

They output one P(supported) per (document, claim). Documents are chunked (~400 words, MiniCheck's recipe) and the
maximum over chunks is kept. Evaluation:
  aggrefact  per sub-dataset balanced accuracy at 0.5, macro and RAG-subset averages
  ragtruth   binary (supported vs not) on our sentence labels, per task
  anli       the single score is compared with the `sup`, `strict` and `lenient` gold labels: an encoder cannot change
             its behaviour with the rule, which is exactly what RQ5 measures
Needs PyTorch (`uv pip install -e ".[baselines]"`). HHEM needs transformers < 4.50: run it from the separate
environment (Project/envs/hhem) with PYTHONPATH=GroundOne/src.
Usage: groundone baselines encoder --model minicheck-roberta --suite all --name minicheck-roberta [--limit N]
"""
import argparse
import json
import time

import numpy as np
import pandas as pd

from ..config import DATA_PROCESSED, RESULTS_DIR
from ..eval.evaluate import RAG_SUBSET, load_jsonl, subsample
from ..eval.metrics import binary
from ..prompts import label_for

REPOS = {"minicheck-roberta": "lytang/MiniCheck-RoBERTa-Large", "minicheck-deberta": "lytang/MiniCheck-DeBERTa-v3-Large",
         "hhem": "vectara/hallucination_evaluation_model"}


def chunks(doc, words=400):
    w = doc.split()
    if len(w) <= words:
        return [doc]
    return [" ".join(w[i:i + words]) for i in range(0, max(len(w) - 50, 1), words - 50)]


def make_scorer(name):
    import torch
    dev = "mps" if torch.backends.mps.is_available() else "cpu"
    if name == "hhem":
        from transformers import AutoModelForSequenceClassification
        model = AutoModelForSequenceClassification.from_pretrained(REPOS[name], trust_remote_code=True).to(dev).eval()

        def score(doc, claim):
            with torch.no_grad():
                return max(float(s) for s in model.predict([(c, claim) for c in chunks(doc)]))
    else:
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
        tok = AutoTokenizer.from_pretrained(REPOS[name])
        model = AutoModelForSequenceClassification.from_pretrained(REPOS[name]).to(dev).eval()

        def score(doc, claim):
            best = 0.0
            for c in chunks(doc):
                # fixed shape (pad to 512): MPS caches one kernel set per input shape, so variable lengths made memory grow
                enc = tok(c, claim, return_tensors="pt", truncation="only_first", max_length=512, padding="max_length").to(dev)
                with torch.no_grad():
                    best = max(best, float(torch.softmax(model(**enc).logits[0], -1)[-1]))
            return best
    return score, dev


def main(argv=None):
    ap = argparse.ArgumentParser(prog="groundone baselines encoder")
    ap.add_argument("--model", choices=list(REPOS), required=True)
    ap.add_argument("--suite", choices=["aggrefact", "ragtruth", "anli", "all"], default="all")
    ap.add_argument("--limit", type=int, default=0, help="subsample size per suite (0 = full test set)")
    ap.add_argument("--data", default="v1")
    ap.add_argument("--name", required=True)
    a = ap.parse_args(argv)
    score, dev = make_scorer(a.model)
    d = DATA_PROCESSED / a.data
    for s in (["anli", "ragtruth", "aggrefact"] if a.suite == "all" else [a.suite]):
        sd = RESULTS_DIR / a.name / s
        if sd.exists():
            raise SystemExit(f"{sd} exists (create-only)")
        items = load_jsonl(d / f"test_{s}.jsonl")
        key = {"aggrefact": lambda x: x["meta"]["dataset"], "ragtruth": lambda x: x["meta"]["task"], "anli": lambda x: x["cls"]}[s]
        items = subsample(items, a.limit, key)
        t0 = time.time()
        ps, secs = [], []
        for n, it in enumerate(items):
            t = time.perf_counter()
            ps.append(score(it["doc"], it["sentences"][it["idx"]]))
            secs.append(time.perf_counter() - t)
            if dev == "mps" and n % 50 == 49:
                # the MPS allocator keeps buffers for every input length it has seen: release them regularly
                # (otherwise the process grew to ~10 GB on RAGTruth and pushed the system into swap)
                import torch
                torch.mps.empty_cache()
            if n % 500 == 0:
                el = time.time() - t0
                print(f"  [{a.model} {s}] {n}/{len(items)}  {el / 60:.1f} min, eta {el / max(n, 1) * (len(items) - n) / 60:.1f} min", flush=True)
        df = pd.DataFrame({"id": [x["id"] for x in items], "p_supported": ps, "seconds": secs})
        if s == "aggrefact":
            df["dataset"] = [x["meta"]["dataset"] for x in items]
            df["label"] = [x["binary"] for x in items]
            per = {k: binary(g["label"], g["p_supported"]) for k, g in df.groupby("dataset")}
            m = {"per_dataset": per, "macro_bacc": float(np.mean([v["bacc"] for v in per.values()])),
                 "rag_subset_bacc": float(np.mean([per[k]["bacc"] for k in RAG_SUBSET if k in per]))}
        else:
            df["cls"] = [x["cls"] for x in items]
            if s == "ragtruth":
                df["task"] = [x["meta"]["task"] for x in items]
                y = (df["cls"] == "supported").astype(int)
                m = {"sup": {"all": binary(y, df["p_supported"]),
                             **{t: binary(y[df.task == t], df.loc[df.task == t, "p_supported"]) for t in sorted(df.task.unique())}}}
            else:
                m = {"by_question": {q: binary(np.array([1 if label_for(q, c) == "A" else 0 for c in df["cls"]]), df["p_supported"])
                                     for q in ("sup", "strict", "lenient")},
                     "note": "one fixed score evaluated against each rule's labels (encoders cannot take a rule)"}
        m.update({"system": a.model, "repo": REPOS[a.model], "device": dev, "n": len(items), "limit": a.limit,
                  "latency_p50_s": float(np.median(secs)), "wall_minutes": round((time.time() - t0) / 60, 2)})
        sd.mkdir(parents=True)
        df.to_parquet(sd / "predictions.parquet")
        (sd / "metrics.json").write_text(json.dumps(m, indent=2, default=str))
        print(f"[{a.model} {s}] done in {m['wall_minutes']} min", flush=True)


if __name__ == "__main__":
    main()
