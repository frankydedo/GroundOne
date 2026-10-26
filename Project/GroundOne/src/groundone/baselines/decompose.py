"""Latency net of the prefill: how much of the time to verify an answer is reading the text, and how much is deciding;
and what prefix caching saves (D32).

Same K-stratified T1 answers and the same in-process MLX protocol as `baselines judges` (3 warm-up answers excluded,
one answer at a time). Per answer:
  groundone  read = one forward pass over the same text without markers (head applied at the last token only);
             total = the served pass with a marker after every scored sentence; decide = total - read (the marker
             tokens and the head at the markers). The two passes are interleaved `--reps` times, medians kept.
  terse, verbose  the LLM judge through mlx_lm stream_generate: read = time to the first token (prefill of the judge
             prompt), total = until the last token, decide = total - read (decoding the verdicts); 1 repetition,
             as in the latency runs.
--cache selects what is already in the KV cache when the clock starts (prefilled beforehand, not timed):
  none   nothing (cold start: the published latency protocol)
  fixed  the fixed instructions (system prompt + instruction), identical for every request
  doc    the instructions and the document, as when a document is verified again (a rewritten answer, another answer
         on the same sources); only the answer is read
The same prefixes are cached for GroundOne and for the LLM judges, so the comparison stays like for like.
Outputs: results/<name>/decompose/<system>[-<cache>].parquet (create-only); `decompose-report` writes metrics.json
with medians per K band, overall and decision-only speed-ups per cache setting, and bootstrap 95% intervals over
answers.
Usage: groundone baselines decompose --system groundone|terse|verbose --size 0.5b [--adapter RUN] [--cache none|fixed|doc]
           --name NAME [--reps 3]
       groundone baselines decompose-report --name NAME
"""
import argparse
import json
import sys
import time

import numpy as np
import pandas as pd

from ..config import RESULTS_DIR
from ..data.build import k_band
from ..eval.tests import load
from ..prompts import encode_marked, marked_prefix_lengths
from .judges import TOKENS_PER_SENTENCE, judge_prompt, k_stratified

BANDS = ["1-4", "5-8", "9-13", ">=14"]
SYSTEMS = ("groundone", "terse", "verbose")
CACHES = ("none", "fixed", "doc")


def run_file(system, cache):
    return f"{system}.parquet" if cache == "none" else f"{system}-{cache}.parquet"


def common_len(a, b):
    n = 0
    while n < min(len(a), len(b)) and a[n] == b[n]:
        n += 1
    return n


def judge_prefix_lengths(tok, prompt, ids):
    """Token lengths of the judge prompt's fixed instructions and of its head up to the end of the document."""
    enc = lambda t: tok.encode(t, add_special_tokens=False)  # noqa: E731
    return (common_len(enc(prompt[:prompt.index("DOCUMENT:\n")]), ids),
            common_len(enc(prompt[:prompt.index("\n\nANSWER (numbered sentences):")]), ids))


def main(argv=None):
    from ..engine import Engine
    ap = argparse.ArgumentParser(prog="groundone baselines decompose")
    ap.add_argument("--system", choices=SYSTEMS, required=True)
    ap.add_argument("--size", default="0.5b")
    ap.add_argument("--adapter")
    ap.add_argument("--cache", choices=CACHES, default="none")
    ap.add_argument("--per-band", type=int, default=50)
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--name", required=True)
    a = ap.parse_args(argv)
    if a.system == "groundone" and not a.adapter:
        sys.exit("--adapter is required for groundone")
    out = RESULTS_DIR / a.name / "decompose" / run_file(a.system, a.cache)
    if out.exists():
        sys.exit(f"{out} exists: results are create-only")
    recs = k_stratified(load("test_ragtruth"), a.per_band)
    engine = Engine.load(a.size, a.adapter if a.system == "groundone" else None)
    be, tok = engine.backend, engine.backend.tokenizer
    warm = recs[:3]
    rows = []
    fixed_state = None

    def prefix_for(ids, n_fixed, n_head):
        nonlocal fixed_state
        if a.cache == "none":
            return None
        if fixed_state is None or fixed_state["ids"] != tuple(ids[:n_fixed]):
            fixed_state = engine._run(be.prefill, ids[:n_fixed])
        return fixed_state if a.cache == "fixed" else engine._run(be.prefill, ids[:n_head], fixed_state)

    def judge_once(ids, prefix, max_tokens):
        from mlx_lm import stream_generate
        from ..backend import explicit_offset_mask
        cache, n = be._cache_from(prefix, ids)
        t0 = time.perf_counter()
        first, k = None, 0
        with explicit_offset_mask():  # the prompt after a cached prefix: several queries at an offset (MLX 0.29.3 bug)
            for _ in stream_generate(be.model, tok, ids[n:], max_tokens=max_tokens, prompt_cache=cache):
                k += 1
                if first is None:
                    first = time.perf_counter() - t0
        return first, time.perf_counter() - t0, k

    for n, r in enumerate(warm + recs):
        idx = [i for i, y in enumerate(r["labels"]) if y is not None]
        if a.system == "groundone":
            ids, pos = encode_marked(tok, r["doc"], r["sentences"], [y is not None for y in r["labels"]])
            plain, _ = encode_marked(tok, r["doc"], r["sentences"], [False] * len(r["sentences"]))
            prefix = prefix_for(ids, *marked_prefix_lengths(tok, r["doc"]))
            n_pre = len(prefix["ids"]) if prefix else 0
            reads, totals = [], []
            for _ in range(a.reps):  # interleaved, so slow drift affects both passes alike
                t = time.perf_counter()
                if prefix:
                    engine._run(be.score_positions_from, prefix, plain, [len(plain) - 1])
                else:
                    engine._run(be.score_positions, [plain], [[len(plain) - 1]])
                reads.append(time.perf_counter() - t)
                t = time.perf_counter()
                if prefix:
                    engine._run(be.score_positions_from, prefix, ids, pos)
                else:
                    engine._run(be.score_positions, [ids], [pos])
                totals.append(time.perf_counter() - t)
            read, total, n_in, n_read, n_out = (float(np.median(reads)), float(np.median(totals)), len(ids) - n_pre,
                                                len(plain) - n_pre, 0)
        else:
            prompt = judge_prompt(tok, r, a.system)
            ids = tok.encode(prompt, add_special_tokens=False)
            prefix = prefix_for(ids, *judge_prefix_lengths(tok, prompt, ids))
            n_pre = len(prefix["ids"]) if prefix else 0
            n_in = n_read = len(ids) - n_pre
            read, total, n_out = engine._run(judge_once, ids, prefix, TOKENS_PER_SENTENCE[a.system] * len(idx) + 40)
        if n < len(warm):
            continue
        rows.append({"rid": r["id"], "task": r["task"], "K": len(idx), "kband": k_band(len(idx)), "cache": a.cache,
                     "cached_tokens": n_pre, "read_s": read, "total_s": total, "decide_s": total - read,
                     "prompt_tokens": n_in, "read_tokens": n_read, "generated_tokens": n_out})
        if (n - len(warm)) % 25 == 0:
            print(f"  [decompose {a.system} {a.size} cache={a.cache}] {n - len(warm)}/{len(recs)}: read {read:.3f} s, "
                  f"total {total:.3f} s (K={len(idx)}, {n_pre} cached tokens)", flush=True)
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_parquet(out)
    d = pd.DataFrame(rows)
    print(f"[decompose {a.system} {a.size} cache={a.cache}] median read {d['read_s'].median():.3f} s, "
          f"decide {d['decide_s'].median():.4f} s, total {d['total_s'].median():.3f} s", flush=True)


def _ratio_ci(num, den, B=2000, seed=1234):
    """Ratio of medians (num / den) over paired answers, with a bootstrap 95% interval resampling answers."""
    rng = np.random.default_rng(seed)
    num, den = np.asarray(num), np.asarray(den)
    point = float(np.median(num) / np.median(den))
    bs = [np.median(num[i]) / np.median(den[i]) for i in (rng.integers(0, len(num), len(num)) for _ in range(B))]
    return {"ratio": point, "ci95": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]}


def _summary(d):
    keys = ("read_s", "decide_s", "total_s", "read_tokens", "generated_tokens", "cached_tokens")
    med = lambda x: {k: float(x[k].median()) for k in keys if k in x} | {  # noqa: E731
        "read_share": float((x["read_s"] / x["total_s"]).median())}
    return {"answers": int(len(d)), "by_K_band": {b: med(x) for b, x in d.groupby("kband")}, "all": med(d)}


def report(argv=None):
    ap = argparse.ArgumentParser(prog="groundone baselines decompose-report")
    ap.add_argument("--name", required=True)
    a = ap.parse_args(argv)
    sd = RESULTS_DIR / a.name / "decompose"
    runs = {(s, c): pd.read_parquet(sd / run_file(s, c)) for s in SYSTEMS for c in CACHES if (sd / run_file(s, c)).exists()}
    if ("groundone", "none") not in runs:
        sys.exit(f"{sd}/groundone.parquet missing")
    m = {"protocol": "same K-stratified T1 answers as the latency runs; in-process MLX, one answer at a time, 3 warm-up "
                     "answers excluded. GroundOne: read = pass without markers, total = served pass, medians of interleaved "
                     "repetitions; LLM judges: read = time to first token, total = until the last token, 1 repetition. "
                     "decide = total - read. cache: what is in the KV cache before the clock starts (none; fixed "
                     "instructions; instructions + document), the same for every system. Ratios are ratios of medians; "
                     "95% intervals from 2,000 bootstrap resamples of answers.",
         # kept flat for cache=none (the first version of this report), per cache setting under "cache"
         "systems": {}, "speedup": {}, "cache": {}}
    for c in CACHES:
        if ("groundone", c) not in runs:
            continue
        g = runs[("groundone", c)].set_index("rid")
        block = {"systems": {}, "speedup": {}}
        for s in SYSTEMS:
            if (s, c) not in runs:
                continue
            d = runs[(s, c)].set_index("rid")
            block["systems"][s] = _summary(d)
            if s == "groundone":
                continue
            j = d.loc[d.index.intersection(g.index)]
            gg = g.loc[j.index]
            sp = {"all": {"total": _ratio_ci(j["total_s"], gg["total_s"]), "decide": _ratio_ci(j["decide_s"], gg["decide_s"])}}
            for b in BANDS:
                sel = j["kband"] == b
                if sel.any():
                    sp[b] = {"total": _ratio_ci(j["total_s"][sel], gg["total_s"][sel]),
                             "decide": _ratio_ci(j["decide_s"][sel], gg["decide_s"][sel])}
            block["speedup"][s] = sp
        m["cache"][c] = block
        if c == "none":
            m["systems"], m["speedup"] = block["systems"], block["speedup"]
        # what caching saves for each system, against its own cold start
        if c != "none":
            for s in block["systems"]:
                if (s, "none") in runs:
                    cold = runs[(s, "none")].set_index("rid")
                    warm = runs[(s, c)].set_index("rid")
                    common = cold.index.intersection(warm.index)
                    block.setdefault("saving_vs_cold", {})[s] = _ratio_ci(cold.loc[common, "total_s"], warm.loc[common, "total_s"])
    (sd / "metrics.json").write_text(json.dumps(m, indent=2))
    for c, block in m["cache"].items():
        for s, sp in block["speedup"].items():
            print(f"[{a.name} cache={c}] vs {s}: total {sp['all']['total']['ratio']:.2f}x, decide {sp['all']['decide']['ratio']:.1f}x; "
                  f"K>=14 total {sp.get('>=14', {}).get('total', {}).get('ratio', float('nan')):.2f}x")
        for s, r in block.get("saving_vs_cold", {}).items():
            print(f"[{a.name} cache={c}] {s}: cold / cached total = {r['ratio']:.2f}x")
