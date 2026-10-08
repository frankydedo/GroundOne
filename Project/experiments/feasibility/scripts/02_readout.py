"""Phase 0, step 2: zero-shot single-token logit readout (baseline B1).

P(supported) = softmax([logit_A, logit_B])[0] at the last prompt position, no generation.
Usage: python 02_readout.py qwen0.5b [max_items]
"""
import sys
import time

import mlx.core as mx
import numpy as np
import pandas as pd
from mlx_lm import load

from common import DATA, MODELS, RESULTS, SYSTEM, log, metrics, write_json

key = sys.argv[1]
max_items = int(sys.argv[2]) if len(sys.argv) > 2 else None
mx.set_memory_limit(int(float(__import__("os").environ.get("MLX_MEM_GB", 7)) * 1e9))
mx.set_cache_limit(int(1e9))
model, tok = load(MODELS[key])

ids_A = tok.encode("A", add_special_tokens=False)
ids_B = tok.encode("B", add_special_tokens=False)
assert len(ids_A) == 1 and len(ids_B) == 1, (ids_A, ids_B)
A, B = ids_A[0], ids_B[0]


def prompt(doc, claim):
    msgs = [{"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"DOCUMENT:\n{doc}\n\nCLAIM:\n{claim}\n\nIs the CLAIM fully supported by the DOCUMENT? Answer A (supported) or B (not supported)."}]
    return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)


df = pd.read_parquet(DATA / "eval_samples.parquet")
if max_items:
    df = df.groupby("set").head(max_items)

# warm-up
for _ in range(3):
    x = mx.array([tok.encode(prompt("The sky is blue.", "The sky is blue."), add_special_tokens=False)])
    mx.eval(model(x)[0, -1])
mx.reset_peak_memory()

rows = []
t0 = time.time()
for i, r in enumerate(df.itertuples()):
    ids = tok.encode(prompt(r.doc, r.claim), add_special_tokens=False)
    t = time.perf_counter()
    logits = model(mx.array([ids]))[0, -1].astype(mx.float32)
    two = mx.softmax(mx.stack([logits[A], logits[B]]))
    top = int(mx.argmax(logits).item())
    mx.eval(two)
    ms = (time.perf_counter() - t) * 1000
    p = float(two[0].item())
    rows.append({"uid": r.uid, "set": r.set, "label": r.label, "p_supported": p, "ms": ms, "n_tokens": len(ids),
                 "top_token_is_AB": top in (A, B)})
    if i % 100 == 0:
        log(f"{key} {i}/{len(df)} {ms:.0f} ms, {len(ids)} tok")
pred = pd.DataFrame(rows)
pred.to_parquet(RESULTS / f"preds_readout_{key}{'_test' if max_items else ''}.parquet")

out = {"model": MODELS[key], "peak_mem_gb": mx.get_peak_memory() / 1e9, "wall_min": (time.time() - t0) / 60}
for s, g in pred.groupby("set"):
    m = metrics(g["label"], g["p_supported"])
    m["top_token_is_AB_rate"] = float(g["top_token_is_AB"].mean())
    m["ms_p50"] = float(np.percentile(g["ms"], 50))
    m["ms_p90"] = float(np.percentile(g["ms"], 90))
    m["tokens_p50"] = float(np.percentile(g["n_tokens"], 50))
    out[s] = m
write_json(RESULTS / f"02_readout_{key}{'_test' if max_items else ''}.json", out)
log(f"done {key}: " + ", ".join(f"{s} bacc={out[s]['bacc@0.5']:.3f} auroc={out[s]['auroc']:.3f}" for s in pred['set'].unique()))
