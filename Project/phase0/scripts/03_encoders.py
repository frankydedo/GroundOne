"""Phase 0, step 3: encoder baselines (B4) on the same evaluation samples.

MiniCheck (RoBERTa-L, DeBERTa-v3-L, Flan-T5-L) and HHEM-2.1-open, run with PyTorch on MPS.
Long documents are chunked (~400 words, as in MiniCheck) and the max P(supported) over chunks is kept.
Usage: python 03_encoders.py minicheck-roberta|minicheck-deberta|minicheck-ft5|hhem [max_items]
"""
import sys
import time

import numpy as np
import pandas as pd
import torch

from common import DATA, RESULTS, log, metrics, write_json

name = sys.argv[1]
max_items = int(sys.argv[2]) if len(sys.argv) > 2 else None
dev = "mps" if torch.backends.mps.is_available() else "cpu"
REPOS = {"minicheck-roberta": "lytang/MiniCheck-RoBERTa-Large", "minicheck-deberta": "lytang/MiniCheck-DeBERTa-v3-Large",
         "minicheck-ft5": "lytang/MiniCheck-Flan-T5-Large", "hhem": "vectara/hallucination_evaluation_model"}
repo = REPOS[name]


def chunks(doc, words=400):
    w = doc.split()
    if len(w) <= words:
        return [doc]
    step = words - 50
    return [" ".join(w[i:i + words]) for i in range(0, max(len(w) - 50, 1), step)]


if name == "hhem":
    from transformers import AutoModelForSequenceClassification
    model = AutoModelForSequenceClassification.from_pretrained(repo, trust_remote_code=True).to(dev).eval()

    def score(doc, claim):
        with torch.no_grad():
            return max(float(s) for s in model.predict([(c, claim) for c in chunks(doc)]))
elif name == "minicheck-ft5":
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(repo)
    model = AutoModelForSeq2SeqLM.from_pretrained(repo).to(dev).eval()
    id0, id1 = tok("0").input_ids[0], tok("1").input_ids[0]

    def score(doc, claim):
        best = 0.0
        for c in chunks(doc):
            enc = tok(f"premise: {c} hypothesis: {claim}", return_tensors="pt", truncation=True, max_length=2048).to(dev)
            dec = torch.full((1, 1), model.config.decoder_start_token_id, device=dev)
            with torch.no_grad():
                lg = model(**enc, decoder_input_ids=dec).logits[0, -1]
            best = max(best, float(torch.softmax(lg[[id0, id1]], -1)[1]))
        return best
else:
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(repo)
    model = AutoModelForSequenceClassification.from_pretrained(repo).to(dev).eval()

    def score(doc, claim):
        best = 0.0
        for c in chunks(doc):
            enc = tok(c, claim, return_tensors="pt", truncation="only_first", max_length=512).to(dev)
            with torch.no_grad():
                best = max(best, float(torch.softmax(model(**enc).logits[0], -1)[-1]))
        return best

df = pd.read_parquet(DATA / "eval_samples.parquet")
if max_items:
    df = df.groupby("set", group_keys=False).sample(frac=1, random_state=1234).groupby("set").head(max_items)
for _ in range(2):
    score("The sky is blue.", "The sky is blue.")
rows, t0 = [], time.time()
for i, r in enumerate(df.itertuples()):
    t = time.perf_counter()
    p = score(r.doc, r.claim)
    if dev == "mps":
        torch.mps.synchronize()
    rows.append({"uid": r.uid, "set": r.set, "label": r.label, "p_supported": p, "ms": (time.perf_counter() - t) * 1000})
    if i % 200 == 0:
        log(f"{name} {i}/{len(df)}")
pred = pd.DataFrame(rows)
sfx = f"_n{max_items}" if max_items else ""
pred.to_parquet(RESULTS / f"preds_{name}{sfx}.parquet")
out = {"model": repo, "device": dev, "wall_min": (time.time() - t0) / 60}
for s, g in pred.groupby("set"):
    m = metrics(g["label"], g["p_supported"])
    m["ms_p50"], m["ms_p90"] = float(np.percentile(g["ms"], 50)), float(np.percentile(g["ms"], 90))
    out[s] = m
write_json(RESULTS / f"03_{name}{sfx}.json", out)
log(f"done {name}: " + ", ".join(f"{s} bacc={out[s]['bacc@0.5']:.3f}" for s in pred["set"].unique()))
