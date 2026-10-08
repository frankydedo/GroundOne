"""Phase 0b, N5: accuracy and format reliability of the generative judges (terse and verbose).

On the 100 RAGTruth test responses of the rt_sent sample (630 sentences): one prompt per response listing its
numbered sentences; greedy generation; parse a yes/no verdict per sentence. Unparseable or missing verdicts are
counted as format failures (and scored as 'supported', the majority class, for accuracy).
Usage: python 08_gen_judges.py qwen0.5b|qwen3b
"""
import json
import re
import sys
import time

import mlx.core as mx
import numpy as np
import pandas as pd
from mlx_lm import load, stream_generate

from common import DATA, MODELS, RESULTS, balanced_accuracy, log, write_json

key = sys.argv[1]
mx.set_memory_limit(int(7e9))
mx.set_cache_limit(int(1e9))
model, tok = load(MODELS[key])
SYS = "You are a faithfulness verifier for retrieval-augmented answers."
df = pd.read_parquet(DATA / "eval_samples.parquet")
rs = df[df.set == "rt_sent"]


def prompt(doc, sents, verbose):
    listing = "\n".join(f"[{i+1}] {s}" for i, s in enumerate(sents))
    if verbose:
        fmt = ("For each sentence write exactly one line: '<number>: <one short sentence of reasoning> Verdict: yes' if it is "
               "fully supported by the DOCUMENT, or '... Verdict: no' otherwise.")
    else:
        fmt = "For each sentence write exactly one line: '<number>: yes' if it is fully supported by the DOCUMENT, '<number>: no' otherwise. Nothing else."
    return tok.apply_chat_template([{"role": "system", "content": SYS},
                                    {"role": "user", "content": f"DOCUMENT:\n{doc}\n\nANSWER (numbered sentences):\n{listing}\n\n{fmt}"}],
                                   tokenize=False, add_generation_prompt=True)


def parse(text, n, verbose):
    got = {}
    for line in text.splitlines():
        m = re.match(r"\s*\[?(\d+)\]?\s*[:.)-]", line)
        if not m:
            continue
        v = re.findall(r"verdict:\s*(yes|no)", line, re.I) if verbose else re.findall(r"\b(yes|no)\b", line, re.I)
        if v:
            got[int(m.group(1))] = v[-1].lower() == "yes"
    return [got.get(i + 1) for i in range(n)]


rows, t0 = [], time.time()
for j, (rid, g) in enumerate(rs.groupby("response_id")):
    g = g.sort_values("sent_idx")
    sents, doc = g["claim"].tolist(), g["doc"].iloc[0]
    for verbose in (False, True):
        t = time.perf_counter()
        text, last = "", None
        for last in stream_generate(model, tok, prompt(doc, sents, verbose), max_tokens=(70 if verbose else 8) * len(sents) + 20):
            text += last.text
        ms = (time.perf_counter() - t) * 1000
        verdicts = parse(text, len(sents), verbose)
        for (_, r), v in zip(g.iterrows(), verdicts):
            rows.append({"uid": r.uid, "label": r.label, "judge": "verbose" if verbose else "terse", "verdict": v,
                         "response_ms": ms, "gen_tokens": last.generation_tokens, "K": len(sents)})
    if j % 20 == 0:
        log(f"{key} {j}/100")
res = pd.DataFrame(rows)
res.to_parquet(RESULTS / f"08_gen_judges_{key}.parquet")
out = {"model": MODELS[key], "wall_min": (time.time() - t0) / 60}
for jname, g in res.groupby("judge"):
    fail = g["verdict"].isna()
    pred = g["verdict"].fillna(True).astype(float)
    per_resp = g.groupby("uid").first()
    out[jname] = {"n_sentences": int(len(g)), "format_failure_rate": float(fail.mean()),
                  "bacc": balanced_accuracy(g["label"], pred),
                  "response_ms_p50": float(np.percentile(g.drop_duplicates("response_ms")["response_ms"], 50)),
                  "gen_tokens_per_sentence_mean": float((g.drop_duplicates("response_ms")["gen_tokens"] / g.drop_duplicates("response_ms")["K"]).mean())}
write_json(RESULTS / f"08_gen_judges_{key}.json", out)
log("done " + key + " " + json.dumps(out))
