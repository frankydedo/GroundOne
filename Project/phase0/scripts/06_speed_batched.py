"""Phase 0b, N1-N4: batched System One vs terse and verbose generative judges, as K grows.

One answer of up to 8 numbered sentences over a shared context of ~L tokens. K decisions:
  K = 1, 3, 8   -> one question ("fully supported?") for 1, 3, 8 sentences
  K = 24        -> three questions (supported? contradicted? mentioned at all?) for 8 sentences
Methods:
  s1_batched : prefill once, K short suffixes ("Sentence [3]: is it fully supported ...?") in one batched pass
  gen_terse  : one prompt, greedy output '<id>: yes|no' per decision
  gen_verbose: one prompt, one short reasoning sentence then 'Verdict: yes|no' per decision
Usage: python 06_speed_batched.py qwen0.5b|qwen3b
"""
import statistics as st
import sys
import time

import mlx.core as mx
import pandas as pd
from mlx_lm import load, stream_generate

from common import DATA, MODELS, RESULTS, log, write_json
from s1engine import Engine

key = sys.argv[1]
mx.set_memory_limit(int(8e9))
mx.set_cache_limit(int(1e9))
model, tok = load(MODELS[key])
eng = Engine(model, tok)
SYS = "You are a faithfulness verifier for retrieval-augmented answers."
QUESTIONS = {"sup": "is it fully supported by the DOCUMENT?",
             "con": "is it contradicted by the DOCUMENT?",
             "men": "is its content mentioned in the DOCUMENT at all?"}

df = pd.read_parquet(DATA / "eval_samples.parquet")
rs = df[df.set == "rt_sent"]
docs = sorted(df[df.set.isin(["rt_resp", "rt_sent"])]["doc"].unique(), key=len, reverse=True)
answers = [g.sort_values("sent_idx")["claim"].tolist()[:8] for _, g in rs.groupby("response_id") if g["K"].iloc[0] >= 8][:3]


def doc_of_len(n_tok, i):
    ids = []
    for d in docs[i:] + docs[:i]:
        ids += tok.encode(d + "\n\n", add_special_tokens=False)
        if len(ids) >= n_tok:
            break
    return tok.decode(ids[:n_tok])


def chat(user):
    return tok.apply_chat_template([{"role": "system", "content": SYS}, {"role": "user", "content": user}],
                                   tokenize=False, add_generation_prompt=True)


def body(doc, sents):
    return f"DOCUMENT:\n{doc}\n\nANSWER (numbered sentences):\n" + "\n".join(f"[{i+1}] {s}" for i, s in enumerate(sents))


def decisions(K):
    n_s = 8 if K == 24 else K
    qs = ["sup", "con", "men"] if K == 24 else ["sup"]
    return n_s, [(i, q) for i in range(n_s) for q in qs]


def s1_prompts(doc, sents, decs):
    b = body(doc, sents)
    return [tok.encode(chat(f"{b}\n\nQuestion about sentence [{i+1}]: {QUESTIONS[q]} Answer A for yes, B for no."),
                       add_special_tokens=False) for i, q in decs]


def gen_prompt(doc, sents, decs, verbose):
    items = "\n".join(f"{i+1}{q[0]}: sentence [{i+1}] - {QUESTIONS[q]}" for i, q in decs)
    if verbose:
        fmt = ("For each item write exactly one line: '<item id>: <one short sentence of reasoning> Verdict: yes' "
               "or '... Verdict: no'.")
    else:
        fmt = "For each item write exactly one line: '<item id>: yes' or '<item id>: no'. Nothing else."
    return chat(f"{body(doc, sents)}\n\nITEMS:\n{items}\n\n{fmt}")


def run_gen(prompt, max_tokens):
    t, text, last = time.perf_counter(), "", None
    for last in stream_generate(model, tok, prompt, max_tokens=max_tokens):
        text += last.text
    return (time.perf_counter() - t) * 1000, last.generation_tokens, last.generation_tps, text


# correctness check: batched == fresh, and warm-up
doc0 = doc_of_len(300, 0)
n_s, decs = decisions(3)
pr = s1_prompts(doc0, answers[0][:n_s], decs)
pb, _ = eng.score_batched(pr)
pf = eng.score_fresh(pr)
max_dp = max(abs(a[0] - b[0]) for a, b in zip(pb, pf))
log(f"batched vs fresh max |dp| = {max_dp:.5f}")
run_gen(gen_prompt(doc0, answers[0][:n_s], decs, False), 20)
mx.reset_peak_memory()

rows = []
for L in [500, 1000, 2000]:
    for K in [1, 3, 8, 24]:
        for rep in range(3):
            n_s, decs = decisions(K)
            sents = answers[rep % len(answers)][:n_s]
            doc = doc_of_len(L, rep)
            prompts = s1_prompts(doc, sents, decs)
            t = time.perf_counter()
            _, info = eng.score_batched(prompts)
            t_s1 = (time.perf_counter() - t) * 1000
            g_ms, g_tok, g_tps, g_txt = run_gen(gen_prompt(doc, sents, decs, False), 8 * K + 10)
            row = {"L": L, "K": K, "rep": rep, "s1_batched_ms": t_s1, **info,
                   "terse_ms": g_ms, "terse_tokens": g_tok, "terse_text": g_txt}
            if L == 1000 and rep < 2:  # verbose judge only at the middle context length, 2 reps (slow)
                v_ms, v_tok, _, v_txt = run_gen(gen_prompt(doc, sents, decs, True), 60 * K + 20)
                row.update({"verbose_ms": v_ms, "verbose_tokens": v_tok, "verbose_text": v_txt})
            rows.append(row)
        last = [r for r in rows if r["L"] == L and r["K"] == K]
        msg = f"{key} L={L} K={K} s1={st.median(r['s1_batched_ms'] for r in last):.0f} terse={st.median(r['terse_ms'] for r in last):.0f}"
        if "verbose_ms" in last[0]:
            msg += f" verbose={st.median(r['verbose_ms'] for r in last if 'verbose_ms' in r):.0f}"
        log(msg + " ms")
res = pd.DataFrame(rows)
res.to_parquet(RESULTS / f"06_speed_batched_{key}.parquet")
num = [c for c in ["s1_batched_ms", "terse_ms", "terse_tokens", "verbose_ms", "verbose_tokens", "prefix_tokens", "max_suffix_tokens"] if c in res]
summ = res.groupby(["L", "K"])[num].median()
summ["gain_vs_terse"] = summ["terse_ms"] / summ["s1_batched_ms"]
if "verbose_ms" in summ:
    summ["gain_vs_verbose"] = summ["verbose_ms"] / summ["s1_batched_ms"]
out = {"model": MODELS[key], "batched_vs_fresh_max_dp": max_dp, "peak_mem_gb": mx.get_peak_memory() / 1e9,
       "table": {f"L{l}_K{k}": {c: (None if pd.isna(v) else round(float(v), 2)) for c, v in r.items()}
                 for (l, k), r in summ.to_dict("index").items()}}
write_json(RESULTS / f"06_speed_batched_{key}.json", out)
log("done " + key)
