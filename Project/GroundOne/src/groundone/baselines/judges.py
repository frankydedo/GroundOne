"""Generative judges (B0a terse, B0b verbose) and the latency protocol as a function of K (plan §7, §8.3).

All systems run on the same subset of T1 answers, stratified by K band (default 50 answers per band), in-process
on MLX, one answer at a time (the deployment setting), greedy decoding for the judges.
  terse      zero-shot LLM writes one line "<n>: <letter>" per scored sentence            (B0a)
  verbose    zero-shot LLM writes "<n>: <one short reason> Verdict: <letter>" per sentence (B0b)
  groundone  System One, design (b): one forward pass per answer, letters read at the markers (adapter)
  readout-a  System One, design (a): prefix once + K question suffixes in one batch (base weights; latency only, the
             computation does not depend on the weights)
Letters: A supported, B contradicted, C not mentioned. A sentence whose verdict cannot be parsed is a format failure
(counted as wrong in the accuracy, reported separately). Latency: wall-clock of the model call per answer; the first
3 answers are warm-up and excluded; System One systems are timed over 3 repetitions (median kept).
Outputs: results/<name>/latency/{predictions.parquet, metrics.json}.
Usage: groundone baselines judges --system terse|verbose|groundone|readout-a --size 0.5b [--adapter RUN] --name NAME
"""
import argparse
import json
import random
import re
import sys
import time

import numpy as np
import pandas as pd

from ..config import RESULTS_DIR
from ..data.build import k_band
from ..eval.tests import CLASSES, load, three_way
from ..prompts import SYSTEM, encode_marked, render

INSTR = {
    "terse": ("Check each listed sentence of the ANSWER against the DOCUMENT. For each sentence number write exactly one "
              "line '<number>: <letter>', where A = supported by the DOCUMENT, B = contradicted by the DOCUMENT, "
              "C = not mentioned in the DOCUMENT. Write nothing else."),
    "verbose": ("Check each listed sentence of the ANSWER against the DOCUMENT. For each sentence number write exactly one "
                "line '<number>: <one short sentence of reasoning> Verdict: <letter>', where A = supported by the DOCUMENT, "
                "B = contradicted by the DOCUMENT, C = not mentioned in the DOCUMENT."),
}
TOKENS_PER_SENTENCE = {"terse": 8, "verbose": 70}


def k_stratified(recs, per_band, seed=1234):
    rng = random.Random(seed)
    bands = {}
    for r in recs:
        bands.setdefault(k_band(r["meta"]["K"]), []).append(r)
    out = []
    for b in sorted(bands):
        g = bands[b][:]
        rng.shuffle(g)
        out += g[:per_band]
    return out


def judge_prompt(tok, r, style):
    numbered = "\n".join(f"[{k + 1}] {s}" for k, s in enumerate(r["sentences"]))
    todo = ", ".join(str(i + 1) for i, y in enumerate(r["labels"]) if y is not None)
    user = f"{INSTR[style]}\n\nDOCUMENT:\n{r['doc']}\n\nANSWER (numbered sentences):\n{numbered}\n\nSentences to check: {todo}"
    return tok.apply_chat_template([{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}],
                                   tokenize=False, add_generation_prompt=True)


def parse(text, wanted, style):
    got = {}
    for line in text.splitlines():
        m = re.match(r"^\s*\[?(\d+)\]?\s*[:.)\-]\s*(.*)$", line)
        if not m:
            continue
        n, rest = int(m.group(1)), m.group(2)
        v = re.search(r"verdict\s*[:\-]?\s*\(?([ABC])\b", rest, re.I) if style == "verbose" else None
        if v is None:
            letters = re.findall(r"\b([ABC])\b", rest)
            v = letters[-1] if letters else None
        else:
            v = v.group(1).upper()
        if v and n not in got:
            got[n] = v
    return {i: got.get(i + 1) for i in wanted}


def main(argv=None):
    from ..calibration import softmax
    from ..engine import Engine
    ap = argparse.ArgumentParser(prog="groundone baselines judges")
    ap.add_argument("--system", choices=["terse", "verbose", "groundone", "readout-a"], required=True)
    ap.add_argument("--size", default="0.5b")
    ap.add_argument("--adapter")
    ap.add_argument("--per-band", type=int, default=50)
    ap.add_argument("--name", required=True)
    a = ap.parse_args(argv)
    sd = RESULTS_DIR / a.name / "latency"
    if sd.exists():
        sys.exit(f"{sd} exists: results are create-only")
    recs = k_stratified(load("test_ragtruth"), a.per_band)
    engine = Engine.load(a.size, a.adapter)
    be, tok = engine.backend, engine.backend.tokenizer
    warm = recs[:3]
    rows = []

    def timed(fn, reps):
        ts, out = [], None
        for _ in range(reps):
            t = time.perf_counter()
            out = engine._run(fn)
            ts.append(time.perf_counter() - t)
        return out, float(np.median(ts))

    for n, r in enumerate(warm + recs):
        idx = [i for i, y in enumerate(r["labels"]) if y is not None]
        if a.system in ("terse", "verbose"):
            from mlx_lm import generate
            prompt = judge_prompt(tok, r, a.system)
            n_in = len(tok.encode(prompt, add_special_tokens=False))
            text, sec = timed(lambda: generate(be.model, tok, prompt, max_tokens=TOKENS_PER_SENTENCE[a.system] * len(idx) + 40,
                                               verbose=False), 1)
            n_out = len(tok.encode(text, add_special_tokens=False))
            verdicts = parse(text, idx, a.system)
            probs = {i: ([1.0, 0.0, 0.0] if v == "A" else [0.0, 1.0, 0.0] if v == "B" else [0.0, 0.0, 1.0] if v == "C" else None)
                     for i, v in verdicts.items()}
        elif a.system == "groundone":
            ids, pos = encode_marked(tok, r["doc"], r["sentences"], [y is not None for y in r["labels"]])
            n_in, n_out, text = len(ids), 0, ""
            lg, sec = timed(lambda: be.score_positions([ids], [pos]), 3)
            probs = {i: softmax(x) for i, x in zip(idx, lg[0])}
        else:
            prompts = [be.encode(render(tok, r["doc"], r["sentences"], i, "three")) for i in idx]
            n_in, n_out, text = len(prompts[0]), 0, ""
            (lg, _), sec = timed(lambda: be.score_shared(prompts, [("A", "B", "C")] * len(idx)), 3)
            probs = {i: softmax(x) for i, x in zip(idx, lg)}
        if n < len(warm):
            continue
        for i in idx:
            rows.append({"id": f"{r['id']}-{i}", "rid": r["id"], "cls": r["labels"][i], "task": r["task"], "K": len(idx),
                         "kband": k_band(len(idx)), "p": probs[i], "answer_seconds": sec, "prompt_tokens": n_in,
                         "generated_tokens": n_out})
        if (n - len(warm)) % 25 == 0:
            print(f"  [{a.system} {a.size}] {n - len(warm)}/{len(recs)} answers, last {sec:.2f} s (K={len(idx)})", flush=True)
    df = pd.DataFrame(rows)
    df["format_failure"] = df["p"].isna()
    parsed = df[~df["format_failure"]]
    y = np.array([CLASSES.index(c) for c in df["cls"]])
    pred = np.array([int(np.argmax(p)) if p is not None else -1 for p in df["p"]])  # -1 = failure, always wrong
    rec = {c: float((pred[y == k] == k).mean()) for k, c in enumerate(CLASSES) if (y == k).any()}
    ans = df.drop_duplicates("rid")
    lat = {b: {"answers": int(len(g)), "median_s": float(g["answer_seconds"].median()),
               "p90_s": float(g["answer_seconds"].quantile(.9)), "median_s_per_decision": float((g["answer_seconds"] / g["K"]).median())}
           for b, g in ans.groupby("kband")}
    m = {"system": a.system, "size": a.size, "adapter": a.adapter, "answers": int(len(ans)), "decisions": int(len(df)),
         "format_failure_rate": float(df["format_failure"].mean()),
         "macro_recall_failures_wrong": float(np.mean(list(rec.values()))), "recall_failures_wrong": rec,
         "parsed_only": three_way(parsed) if len(parsed) else None, "latency_by_K_band": lat,
         "latency_all": {"median_s": float(ans["answer_seconds"].median()), "p90_s": float(ans["answer_seconds"].quantile(.9)),
                         "p99_s": float(ans["answer_seconds"].quantile(.99)),
                         "mean_generated_tokens": float(ans["generated_tokens"].mean()), "mean_K": float(ans["K"].mean())},
         "protocol": "in-process MLX, one answer at a time, 3 warm-up answers excluded; System One median of 3 repetitions"}
    sd.mkdir(parents=True)
    df.assign(p=[json.dumps(p) for p in df["p"]]).to_parquet(sd / "predictions.parquet")
    (sd / "metrics.json").write_text(json.dumps(m, indent=2, default=float))
    print(f"[{a.system} {a.size}] macro {m['macro_recall_failures_wrong']:.3f}, failures "
          f"{m['format_failure_rate']:.1%}, median {m['latency_all']['median_s']:.2f} s/answer", flush=True)


if __name__ == "__main__":
    main()
