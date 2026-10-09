"""Generative judges (B0a terse, B0b verbose, B0d equal-output) and the latency protocol as a function of K (plan §7, §8.3).

All systems run on the same subset of T1 answers, stratified by K band (default 50 answers per band), in-process
on MLX, one answer at a time (the deployment setting), greedy decoding for the judges.
  terse      zero-shot LLM writes one line "<n>: <letter>" per scored sentence            (B0a)
  verbose    zero-shot LLM writes "<n>: <one short reason> Verdict: <letter>" per sentence (B0b)
  json       zero-shot LLM returns GroundOne's content as JSON: a label and verbalised probabilities for A, B, C per
             sentence (B0d-verbal, D25); the stated label is the decision, the probabilities feed calibration
  terse-logits  the terse judge, with P(A), P(B), P(C) read from the logits at the generated letter (B0d-logit, D25)
  groundone  System One, design (b): one forward pass per answer, letters read at the markers (adapter)
  readout-a  System One, design (a): prefix once + K question suffixes in one batch (base weights; latency only, the
             computation does not depend on the weights)
Letters: A supported, B contradicted, C not mentioned. A sentence whose verdict cannot be parsed is a format failure
(counted as wrong in the accuracy, reported separately); for json, also when the three probabilities are missing. Latency: wall-clock of the model call per answer; the first
3 answers are warm-up and excluded; System One systems are timed over 3 repetitions (median kept).
Outputs: results/<name>/latency/{predictions.parquet, metrics.json}; with --split dev, results/<name>/dev/ (the same
K-stratified protocol on dev answers, used to calibrate the judge: `judges-calibrate`).
Usage: groundone baselines judges --system terse|verbose|json|terse-logits|groundone|readout-a --size 0.5b
       [--adapter RUN] [--split test|dev] --name NAME
       groundone baselines judges-calibrate --name NAME [--calibration PATH]
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
    # placeholders, no numeric example: an example with numbers was copied verbatim (chosen on 12 dev answers, D25)
    "json": ("Check each listed sentence of the ANSWER against the DOCUMENT. Return only a JSON object with one entry "
             "per sentence number to check, in this form: {\"<number>\": {\"label\": \"<A, B or C>\", \"p\": "
             "[<probability of A>, <probability of B>, <probability of C>]}, ...}, where A = supported by the DOCUMENT, "
             "B = contradicted by the DOCUMENT, C = not mentioned in the DOCUMENT, \"label\" is the most likely letter and "
             "\"p\" are your own probabilities for A, B and C, as decimals that sum to 1. Write nothing else."),
}
INSTR["terse-logits"] = INSTR["terse"]
TOKENS_PER_SENTENCE = {"terse": 8, "terse-logits": 8, "verbose": 70, "json": 45}
LINE_HEAD = re.compile(r"^\s*\[?(\d+)\]?\s*[:.)\-]\s*$")
JSON_ENTRY = re.compile(r'"?(\d+)"?\s*:\s*\{\s*(?:"label"\s*:\s*"([ABC])"\s*,\s*)?"p"\s*:\s*\[\s*([0-9.eE+-]+)\s*,'
                        r'\s*([0-9.eE+-]+)\s*,\s*([0-9.eE+-]+)\s*\]')


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


def parse_json(text, wanted):
    """Lenient: one regex per entry, so a truncated or slightly malformed object still yields its complete entries.
    A missing label is taken as the argmax of p (same content, lenient in the judge's favour). Returns {index: (label
    index, normalised probabilities)}; None if valid probabilities are missing."""
    got = {}
    for n, lab, *ps in JSON_ENTRY.findall(text):
        try:
            p = np.array([float(x) for x in ps])
        except ValueError:
            continue
        if int(n) not in got and np.all(p >= 0) and p.sum() > 0:
            got[int(n)] = ("ABC".index(lab) if lab else int(np.argmax(p)), (p / p.sum()).tolist())
    return {i: got.get(i + 1) for i in wanted}


def generate_with_letter_probs(model, tok, prompt, max_tokens):
    """Greedy generation (same sampler as `generate`) that also keeps, at every generated token, the log-probabilities
    of the letters A, B, C in both spellings (with and without a leading space). Only 6 values per step are copied."""
    from mlx_lm import stream_generate
    trip = [[tok.encode(p + c, add_special_tokens=False)[0] for c in "ABC"] for p in (" ", "")]
    flat = trip[0] + trip[1]
    toks, lps = [], []
    for r in stream_generate(model, tok, prompt, max_tokens=max_tokens):
        toks.append(int(r.token))
        lps.append(r.logprobs[flat].tolist())
    return toks, lps, trip


def parse_letter_probs(tok, toks, lps, trip, wanted):
    """P(A), P(B), P(C) at the letter that follows '<n>:' on a line, renormalised over the three letters."""
    from ..calibration import softmax
    got = {}
    for j, t in enumerate(toks):
        for k, tr in enumerate(trip):
            if t in tr:
                m = LINE_HEAD.match(tok.decode(toks[:j]).split("\n")[-1])
                if m and int(m.group(1)) not in got:
                    got[int(m.group(1))] = softmax(lps[j][3 * k:3 * k + 3])
    return {i: got.get(i + 1) for i in wanted}


def main(argv=None):
    from ..calibration import softmax
    from ..engine import Engine
    ap = argparse.ArgumentParser(prog="groundone baselines judges")
    ap.add_argument("--system", choices=["terse", "verbose", "json", "terse-logits", "groundone", "readout-a"], required=True)
    ap.add_argument("--split", choices=["test", "dev"], default="test", help="dev: answers for calibrating the judge")
    ap.add_argument("--size", default="0.5b")
    ap.add_argument("--adapter")
    ap.add_argument("--per-band", type=int, default=50)
    ap.add_argument("--name", required=True)
    a = ap.parse_args(argv)
    sd = RESULTS_DIR / a.name / ("latency" if a.split == "test" else "dev")
    if sd.exists():
        sys.exit(f"{sd} exists: results are create-only")
    recs = k_stratified(load("test_ragtruth" if a.split == "test" else "dev"), a.per_band)
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
        labels = None
        if a.system == "terse-logits":
            prompt = judge_prompt(tok, r, "terse")
            n_in = len(tok.encode(prompt, add_special_tokens=False))
            (toks, lps, trip), sec = timed(lambda: generate_with_letter_probs(
                be.model, tok, prompt, TOKENS_PER_SENTENCE["terse"] * len(idx) + 40), 1)
            text, n_out = tok.decode(toks), len(toks)
            probs = parse_letter_probs(tok, toks, lps, trip, idx)
        elif a.system == "json":
            from mlx_lm import generate
            prompt = judge_prompt(tok, r, "json")
            n_in = len(tok.encode(prompt, add_special_tokens=False))
            text, sec = timed(lambda: generate(be.model, tok, prompt, max_tokens=TOKENS_PER_SENTENCE["json"] * len(idx) + 60,
                                               verbose=False), 1)
            n_out = len(tok.encode(text, add_special_tokens=False))
            parsed_json = parse_json(text, idx)
            probs = {i: (v[1] if v else None) for i, v in parsed_json.items()}
            labels = {i: (v[0] if v else None) for i, v in parsed_json.items()}
        elif a.system in ("terse", "verbose"):
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
                         "generated_tokens": n_out,
                         "label": (labels[i] if labels else None) if probs[i] is not None else None,
                         "text": text if i == idx[0] else None})
        if (n - len(warm)) % 25 == 0:
            print(f"  [{a.system} {a.size}] {n - len(warm)}/{len(recs)} answers, last {sec:.2f} s (K={len(idx)})", flush=True)
    df = pd.DataFrame(rows)
    df["format_failure"] = df["p"].isna()
    parsed = df[~df["format_failure"]]
    y = np.array([CLASSES.index(c) for c in df["cls"]])
    # decision: the stated label (json) or the most probable letter; -1 = failure, always wrong
    pred = np.array([(int(l) if l is not None and not pd.isna(l) else int(np.argmax(p))) if p is not None else -1
                     for p, l in zip(df["p"], df["label"])])
    rec = {c: float((pred[y == k] == k).mean()) for k, c in enumerate(CLASSES) if (y == k).any()}
    ans = df.drop_duplicates("rid")
    lat = {b: {"answers": int(len(g)), "median_s": float(g["answer_seconds"].median()),
               "p90_s": float(g["answer_seconds"].quantile(.9)), "median_s_per_decision": float((g["answer_seconds"] / g["K"]).median())}
           for b, g in ans.groupby("kband")}
    has_label = df["label"].notna()
    m = {"system": a.system, "size": a.size, "adapter": a.adapter, "split": a.split, "answers": int(len(ans)),
         "decisions": int(len(df)),
         "label_disagrees_with_argmax_p": (float(np.mean([int(l) != int(np.argmax(p)) for p, l in
                                                          zip(df["p"][has_label], df["label"][has_label])]))
                                           if has_label.any() else None),
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


def calibrate(argv=None):
    """Post-hoc calibration of a judge on the latency subset, with the same affine map used for GroundOne (D24, D25).

    Without --calibration: fit temperature + bias on results/<name>/dev (log-probabilities used as logits; verbalised
    probabilities clipped at 1e-3 so that a stated 0 stays finite; logit-based ones at 1e-12). With --calibration PATH (a GroundOne
    calibration.json): apply that map, so GroundOne is evaluated on the same latency subset in the same way.
    Format failures are excluded (their count is reported). Writes results/<name>/latency/calibration.json with the
    same metric blocks as `calibrate-b` (raw and affine)."""
    from ..calibration import fit_affine
    from ..eval.calibrate_b import evaluate_split
    ap = argparse.ArgumentParser(prog="groundone baselines judges-calibrate")
    ap.add_argument("--name", required=True)
    ap.add_argument("--calibration", help="apply this calibration.json (key 'three') instead of fitting on dev")
    a = ap.parse_args(argv)

    def read(split):
        df = pd.read_parquet(RESULTS_DIR / a.name / split / "predictions.parquet")
        p = [json.loads(x) for x in df["p"]]
        ok = np.array([x is not None for x in p])
        eps = 1e-3 if json.loads((RESULTS_DIR / a.name / split / "metrics.json").read_text())["system"] == "json" else 1e-12
        L = np.log(np.clip(np.array([x for x in p if x is not None], float), eps, 1))
        y = np.array([CLASSES.index(c) for c in df["cls"][ok]])
        return L, y, int((~ok).sum()), len(df)

    path = RESULTS_DIR / a.name / "latency" / "calibration.json"
    L, y, fails, n = read("latency")
    if not a.calibration:
        Ld, yd, _, _ = read("dev")
        if min(len(yd), len(y)) < 30:  # e.g. a judge that almost never returns valid probabilities
            path.write_text(json.dumps({"fitted_on": None, "t1": None, "sentences": n, "format_failures_excluded": fails,
                                        "note": f"not calibrated: {len(yd)} valid dev and {len(y)} valid test sentences"}, indent=2))
            print(f"[{a.name}] not calibrated: too few valid sentences ({len(yd)} dev, {len(y)} test)")
            return
    if a.calibration:
        c = json.loads(open(a.calibration).read())
        t, b, fitted = float(c["temperatures"]["three"]), list(c["biases"]["three"]), a.calibration
    else:
        t, b = fit_affine([(list(map(float, l)), int(g)) for l, g in zip(Ld, yd)])
        fitted = f"results/{a.name}/dev ({len(yd)} sentences)"
    maps = {"raw": (1.0, [0.0, 0.0, 0.0]), "affine": (t, b)}
    out = {"fitted_on": fitted, "map": {"temperature": round(t, 4), "bias": [round(x, 4) for x in b]},
           "sentences": n, "format_failures_excluded": fails, "t1": evaluate_split(L, y, maps)}
    path.write_text(json.dumps(out, indent=2, default=float))
    r = out["t1"]
    print(f"[{a.name}] binary ECE {r['raw']['binary']['ece15']:.3f} -> {r['affine']['binary']['ece15']:.3f}, "
          f"AURC {r['raw']['aurc']:.3f} -> {r['affine']['aurc']:.3f} ({fails} failures excluded) -> {path}")


if __name__ == "__main__":
    main()
