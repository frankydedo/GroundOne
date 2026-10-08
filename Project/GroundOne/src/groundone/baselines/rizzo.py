"""LEGACY entry point (earlier test files). `post` is reused by baselines/frozen.py, which runs Rizzo-Flow on the frozen tests.

Baseline B3: Rizzo-Flow (general-purpose System One) through its TypeSafe/Jev-compatible API.

Rizzo-Flow must be running (e.g. `rizzo serve --port 8017` from SystemOne_repos/rizzo-flow). Every request uses the
same contract GroundOne also serves (`POST /v1/systemone`), so the comparison is on equal footing:
  aggrefact  state = document, one noul question with the claim ("fully supported?")
  ragtruth   state = document + numbered answer, one noul question per sentence (Rizzo shares the state's KV cache
             across questions: its native strength)
  anli       state = premise; noul `sup`, choice `three` (supported / contradicted / not_mentioned), noul strict / lenient
Per request we record wall-clock latency. Results: results/<name>/<suite>/{predictions.parquet, metrics.json}.
Usage: groundone baselines rizzo --url http://127.0.0.1:8017 --suite all --limit 1000 --name rizzo-flow-4b
"""
import argparse
import json
import random
import time
import urllib.request

import numpy as np
import pandas as pd

from ..config import DATA_PROCESSED, RESULTS_DIR
from ..eval.evaluate import RAG_SUBSET, load_jsonl, subsample
from ..eval.metrics import binary, multiclass
from ..prompts import label_for

RULES = {
    "strict": "Rule: anything in the sentence that is not stated in the document is an error, even if it might be true. "
              "Is the sentence acceptable under this rule?",
    "lenient": "Rule: only statements that contradict the document are errors; information the document does not mention "
               "is acceptable. Is the sentence acceptable under this rule?",
}


def post(url, body, timeout=600):
    req = urllib.request.Request(f"{url}/v1/systemone", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    t = time.perf_counter()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        out = json.loads(r.read())
    return out, time.perf_counter() - t


def run_aggrefact(url, items):
    rows = []
    for n, it in enumerate(items):
        body = {"model": "rizzo-latest", "state": it["doc"], "questions": {
            "sup": {"type": "noul", "instructions": f"Is the following claim fully supported by the document? Claim: {it['sentences'][0]}"}}}
        try:
            out, sec = post(url, body)
            p = out["answers"]["sup"]["noul"]
        except Exception as e:  # noqa: BLE001  (e.g. a document over Rizzo's context limit)
            p, sec = np.nan, np.nan
            print("  skip", it["id"], str(e)[:80], flush=True)
        rows.append({"id": it["id"], "dataset": it["meta"]["dataset"], "label": it["binary"], "p_supported": p, "seconds": sec})
        if n % 100 == 0:
            print(f"  [rizzo aggrefact] {n}/{len(items)}", flush=True)
    df = pd.DataFrame(rows)
    ok = df.dropna(subset=["p_supported"])
    per = {d: binary(g["label"], g["p_supported"]) for d, g in ok.groupby("dataset")}
    return df, {"per_dataset": per, "macro_bacc": float(np.mean([v["bacc"] for v in per.values()])),
                "rag_subset_bacc": float(np.mean([per[d]["bacc"] for d in RAG_SUBSET if d in per])),
                "skipped": int(df["p_supported"].isna().sum()), "latency_p50_s": float(ok["seconds"].median())}


def run_ragtruth(url, items):
    by = {}
    for it in items:
        by.setdefault(it["meta"]["response_id"], []).append(it)
    rows = []
    for n, (rid, sents) in enumerate(by.items()):
        sents.sort(key=lambda x: x["idx"])
        numbered = "\n".join(f"[{k + 1}] {s}" for k, s in enumerate(sents[0]["sentences"]))
        state = f"DOCUMENT:\n{sents[0]['doc']}\n\nANSWER (numbered sentences):\n{numbered}"
        qs = {f"s{x['idx']}": {"type": "noul", "instructions": f"Is sentence [{x['idx'] + 1}] fully supported by the DOCUMENT?"}
              for x in sents}
        try:
            out, sec = post(url, {"model": "rizzo-latest", "state": state, "questions": qs})
        except Exception as e:  # noqa: BLE001
            print("  skip", rid, str(e)[:80], flush=True)
            continue
        for x in sents:
            rows.append({"id": x["id"], "task": x["meta"]["task"], "cls": x["cls"], "K": len(sents),
                         "p_supported": out["answers"][f"s{x['idx']}"]["noul"], "answer_seconds": sec})
        if n % 25 == 0:
            print(f"  [rizzo ragtruth] {n}/{len(by)} answers", flush=True)
    df = pd.DataFrame(rows)
    y = (df["cls"] == "supported").astype(int)
    lat = df.drop_duplicates("answer_seconds")
    return df, {"sup": {"all": binary(y, df["p_supported"]),
                        **{t: binary(y[df.task == t], df.loc[df.task == t, "p_supported"]) for t in sorted(df.task.unique())}},
                "answers": int(len(lat)), "latency_per_answer_p50_s": float(lat["answer_seconds"].median()),
                "mean_K": float(lat["K"].mean())}


def run_anli(url, items):
    rows = []
    for n, it in enumerate(items):
        claim = it["sentences"][0]
        qs = {"sup": {"type": "noul", "instructions": f"Sentence: {claim}\nIs the sentence fully supported by the document?"},
              "three": {"type": "choice", "instructions": f"Sentence: {claim}\nCompared with the document, the sentence is:",
                        "criteria": {"supported": "supported by the document", "contradicted": "contradicted by the document",
                                     "not_mentioned": "neither supported nor contradicted (not mentioned)"}},
              **{r: {"type": "noul", "instructions": f"Sentence: {claim}\n{t}"} for r, t in RULES.items()}}
        out, sec = post(url, {"model": "rizzo-latest", "state": it["doc"], "questions": qs})
        a = out["answers"]
        rows.append({"id": it["id"], "cls": it["cls"], "sup": a["sup"]["noul"], "strict": a["strict"]["noul"],
                     "lenient": a["lenient"]["noul"], "three": [a["three"]["probabilities"][k] for k in ("supported", "contradicted", "not_mentioned")],
                     "seconds": sec})
        if n % 100 == 0:
            print(f"  [rizzo anli] {n}/{len(items)}", flush=True)
    df = pd.DataFrame(rows)
    m = {}
    for q in ("sup", "strict", "lenient"):
        y = np.array([1 if label_for(q, c) == "A" else 0 for c in df["cls"]])
        m[q] = binary(y, df[q])
    m["three"] = multiclass(["ABC".index(label_for("three", c)) for c in df["cls"]], np.array(df["three"].tolist()),
                            ("supported", "contradicted", "not_mentioned"))
    return df, {"by_question": m, "latency_p50_s": float(df["seconds"].median())}


def main(argv=None):
    ap = argparse.ArgumentParser(prog="groundone baselines rizzo")
    ap.add_argument("--url", default="http://127.0.0.1:8017")
    ap.add_argument("--suite", choices=["aggrefact", "ragtruth", "anli", "all"], default="all")
    ap.add_argument("--limit", type=int, default=1000, help="items (answers for ragtruth)")
    ap.add_argument("--data", default="v1")
    ap.add_argument("--name", required=True)
    a = ap.parse_args(argv)
    d = DATA_PROCESSED / a.data
    info = json.loads(urllib.request.urlopen(f"{a.url}/health").read())
    for s in (["aggrefact", "ragtruth", "anli"] if a.suite == "all" else [a.suite]):
        sd = RESULTS_DIR / a.name / s
        if sd.exists():
            raise SystemExit(f"{sd} exists (create-only)")
        items = load_jsonl(d / f"test_{s}.jsonl")
        t0 = time.time()
        if s == "aggrefact":
            df, m = run_aggrefact(a.url, subsample(items, a.limit, lambda x: x["meta"]["dataset"]))
        elif s == "ragtruth":
            resp = sorted({x["meta"]["response_id"] for x in items})
            random.Random(1234).shuffle(resp)
            keep = set(resp[:a.limit])
            df, m = run_ragtruth(a.url, [x for x in items if x["meta"]["response_id"] in keep])
        else:
            df, m = run_anli(a.url, subsample(items, a.limit, lambda x: x["cls"]))
        sd.mkdir(parents=True)
        df.to_parquet(sd / "predictions.parquet")
        m.update({"system": "rizzo-flow", "server_health": info, "limit": a.limit, "wall_minutes": round((time.time() - t0) / 60, 2)})
        (sd / "metrics.json").write_text(json.dumps(m, indent=2, default=str))
        print(f"[rizzo {s}] done in {m['wall_minutes']} min", flush=True)


if __name__ == "__main__":
    main()
