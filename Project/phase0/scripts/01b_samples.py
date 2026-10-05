"""Phase 0, step 1b: balanced evaluation samples (LLM-AggreFact is gated until the author accepts its terms).

Builds three samples, each a table of (uid, set, doc, claim, label, group, K):
  - rt_resp : RAGTruth test, response-level (claim = whole response), QA + Summary, ~50 % hallucinated
  - rt_sent : RAGTruth test, sentence-level from responses half hallucinated / half clean (K sentences share a doc)
  - anli    : ANLI dev r1-r3, entailment -> supported, else not supported
"""
import json
import random

import pandas as pd

from common import DATA, RESULTS, SEED, log, split_sentences, write_json

rng = random.Random(SEED)
resp = [json.loads(l) for l in open(DATA / "ragtruth_response.jsonl")]
src = {d["source_id"]: d for d in (json.loads(l) for l in open(DATA / "ragtruth_source_info.jsonl"))}


def context_of(s):
    info = s["source_info"]
    if s["task_type"] == "QA":
        return f"Question: {info['question']}\n\n{info['passages']}"
    return info if isinstance(info, str) else json.dumps(info, ensure_ascii=False)


pool = []
for r in resp:
    s = src[r["source_id"]]
    if r.get("split") != "test" or s["task_type"] not in ("QA", "Summary"):
        continue
    ctx = context_of(s)
    if len(ctx) > 8000:
        continue
    pool.append((r, s, ctx))
rng.shuffle(pool)
hal = [p for p in pool if p[0]["labels"]]
clean = [p for p in pool if not p[0]["labels"]]
log(f"RAGTruth test QA+Summary pool: {len(hal)} hallucinated, {len(clean)} clean")

# response-level: 150 + 150, disjoint from the sentence-level responses
resp_rows = []
for r, s, ctx in hal[:150] + clean[:150]:
    resp_rows.append({"uid": f"rr{r['id']}", "set": "rt_resp", "doc": ctx, "claim": r["response"],
                      "label": int(not r["labels"]), "group": s["task_type"], "K": 1})
# sentence-level: next 50 + 50 responses, all their sentences
sent_rows = []
for r, s, ctx in hal[150:200] + clean[150:200]:
    spans = [(l["start"], l["end"]) for l in r["labels"]]
    sents = split_sentences(r["response"])
    for i, (a, b, t) in enumerate(sents):
        unsup = any(a < e and s0 < b for s0, e in spans)
        sent_rows.append({"uid": f"rs{r['id']}_{i}", "set": "rt_sent", "doc": ctx, "claim": t, "label": int(not unsup),
                          "group": s["task_type"], "K": len(sents), "response_id": r["id"], "response": r["response"],
                          "sent_idx": i})

from datasets import load_dataset  # noqa: E402
anli = load_dataset("facebook/anli")
anli_rows = []
for rnd in ["dev_r1", "dev_r2", "dev_r3"]:
    d = anli[rnd].shuffle(seed=SEED).select(range(100))
    for ex in d:
        anli_rows.append({"uid": f"an{ex['uid']}", "set": "anli", "doc": ex["premise"], "claim": ex["hypothesis"],
                          "label": int(ex["label"] == 0), "group": rnd, "K": 1})

agg_rows = []
if (DATA / "sample_aggrefact.parquet").exists():
    agg = pd.read_parquet(DATA / "sample_aggrefact.parquet")
    for r in agg.itertuples():
        agg_rows.append({"uid": r.uid, "set": "aggrefact", "doc": r.doc, "claim": r.claim, "label": int(r.label),
                         "group": r.dataset, "K": 1})
    log(f"LLM-AggreFact sample: {len(agg_rows)}")
df = pd.concat([pd.DataFrame(x) for x in (resp_rows, sent_rows, anli_rows, agg_rows) if x], ignore_index=True)
df.to_parquet(DATA / "eval_samples.parquet")
summary = df.groupby("set")["label"].agg(["count", "mean"]).round(3).to_dict("index")
summary["rt_sent_responses"] = int(df[df.set == "rt_sent"]["response_id"].nunique())
summary["rt_sent_mean_K"] = float(df[df.set == "rt_sent"].groupby("response_id")["K"].first().mean())
write_json(RESULTS / "01b_samples.json", summary)
log(json.dumps(summary))
