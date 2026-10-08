"""Phase 0b, N6: flexibility probe vs MiniCheck, with existing labels only.

Three classes per (document, sentence): supported / contradicted / not mentioned.
  ANLI dev:            entailment / contradiction / neutral
  RAGTruth sentences:  no span / a 'Conflict' span / a 'Baseless Info' span (conflict wins if both)
Tasks (zero-shot, System One readout, one pass per item):
  threeway : A = supported, B = contradicted, C = not mentioned
  strict   : rule "anything not stated in the document is an error"       -> gold OK = supported
  lenient  : rule "only statements contradicting the document are errors"  -> gold OK = supported or not mentioned
MiniCheck-RoBERTa (fixed supported/unsupported score, from step 3) is scored against both rule labels.
Usage: python 07_flex.py qwen0.5b|qwen3b
"""
import json
import sys
import time

import mlx.core as mx
import numpy as np
import pandas as pd
from mlx_lm import load

from common import DATA, MODELS, RESULTS, balanced_accuracy, log, split_sentences, write_json
from s1engine import Engine

key = sys.argv[1]
mx.set_memory_limit(int(7e9))
mx.set_cache_limit(int(1e9))
model, tok = load(MODELS[key])
eng = Engine(model, tok)

# ---------- three-way gold labels ----------
df = pd.read_parquet(DATA / "eval_samples.parquet")
items = df[df.set.isin(["anli", "rt_sent"])].copy()
from datasets import load_dataset  # noqa: E402
anli = load_dataset("facebook/anli")
lab = {}
for rnd in ["dev_r1", "dev_r2", "dev_r3"]:
    for ex in anli[rnd]:
        lab[f"an{ex['uid']}"] = {0: "supported", 1: "not_mentioned", 2: "contradicted"}[ex["label"]]
resp = {json.loads(l)["id"]: json.loads(l) for l in open(DATA / "ragtruth_response.jsonl")}
for rid in items[items.set == "rt_sent"]["response_id"].unique():
    r = resp[rid]
    for i, (a, b, _) in enumerate(split_sentences(r["response"])):
        types = [s["label_type"] for s in r["labels"] if a < s["end"] and s["start"] < b]
        cls = "contradicted" if any("Conflict" in t for t in types) else ("not_mentioned" if types else "supported")
        lab[f"rs{rid}_{i}"] = cls
items["cls"] = items["uid"].map(lab)
assert items["cls"].notna().all(), items[items.cls.isna()].uid.head()
log("class counts: " + str(items.groupby(["set", "cls"]).size().to_dict()))

# ---------- prompts ----------
SYS = "You are a faithfulness verifier. Answer with a single letter."
TASKS = {
    "threeway": ("Compare the SENTENCE with the DOCUMENT. A = the sentence is supported by the document. "
                 "B = the sentence is contradicted by the document. C = the document does not mention it "
                 "(neither supports nor contradicts it).", ("A", "B", "C")),
    "strict": ("Rule: anything in the SENTENCE that is not stated in the DOCUMENT is an error, even if it might be true. "
               "A = acceptable under this rule, B = error under this rule.", ("A", "B")),
    "lenient": ("Rule: only statements that CONTRADICT the DOCUMENT are errors; information that the document simply "
                "does not mention is acceptable. A = acceptable under this rule, B = error under this rule.", ("A", "B")),
}


def prompt(doc, claim, instr):
    msgs = [{"role": "system", "content": SYS},
            {"role": "user", "content": f"DOCUMENT:\n{doc}\n\nSENTENCE:\n{claim}\n\n{instr}"}]
    return tok.encode(tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True), add_special_tokens=False)


t0 = time.time()
preds = {t: [] for t in TASKS}
for i, r in enumerate(items.itertuples()):
    for t, (instr, letters) in TASKS.items():
        preds[t].append(eng.score_fresh([prompt(r.doc, r.claim, instr)], letters)[0])
    if i % 200 == 0:
        log(f"{key} {i}/{len(items)}")
for t in TASKS:
    items[f"p_{t}"] = preds[t]

mc = pd.read_parquet(RESULTS / "preds_minicheck-roberta.parquet").set_index("uid")["p_supported"]
items["p_minicheck"] = items["uid"].map(mc)
items["gold_strict"] = (items.cls == "supported").astype(int)
items["gold_lenient"] = (items.cls != "contradicted").astype(int)
items.drop(columns=["doc"]).to_parquet(RESULTS / f"07_flex_{key}.parquet")

CLS = ["supported", "contradicted", "not_mentioned"]
out = {"model": MODELS[key], "wall_min": (time.time() - t0) / 60}
for s, g in items.groupby("set"):
    y = g["cls"].map({c: i for i, c in enumerate(CLS)}).to_numpy()
    p3 = np.array(g["p_threeway"].tolist())
    pred3 = p3.argmax(1)
    recalls = {c: float((pred3[y == i] == i).mean()) for i, c in enumerate(CLS) if (y == i).any()}
    p_strict = np.array([p[0] for p in g["p_strict"]])
    p_len = np.array([p[0] for p in g["p_lenient"]])
    nm = (g["cls"] == "not_mentioned").to_numpy()
    out[s] = {
        "n": int(len(g)), "class_counts": g["cls"].value_counts().to_dict(),
        "threeway_macro_recall": float(np.mean(list(recalls.values()))), "threeway_recall": recalls,
        "strict_rule": {"qwen_bacc": balanced_accuracy(g.gold_strict, p_strict),
                        "minicheck_bacc": balanced_accuracy(g.gold_strict, g.p_minicheck)},
        "lenient_rule": {"qwen_bacc": balanced_accuracy(g.gold_lenient, p_len),
                         "qwen_strict_prompt_on_lenient_labels": balanced_accuracy(g.gold_lenient, p_strict),
                         "minicheck_bacc": balanced_accuracy(g.gold_lenient, g.p_minicheck)},
        "rule_sensitivity_on_not_mentioned": {  # P(acceptable) should rise from strict to lenient
            "mean_p_ok_strict": float(p_strict[nm].mean()) if nm.any() else None,
            "mean_p_ok_lenient": float(p_len[nm].mean()) if nm.any() else None},
    }
write_json(RESULTS / f"07_flex_{key}.json", out)
log(f"done {key}: " + json.dumps({s: (round(v['threeway_macro_recall'], 3), round(v['lenient_rule']['qwen_bacc'], 3),
                                       round(v['lenient_rule']['minicheck_bacc'], 3)) for s, v in out.items() if isinstance(v, dict)}))
