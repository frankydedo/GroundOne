"""Phase 0, step 5: latency of System One readout vs generative judging, as a function of K and context length.

For one answer with K sentences over a shared context of ~L tokens, measure end-to-end time of:
  s1_shared : prefill the common prefix once, then one short suffix pass per sentence (cache trimmed back)
  s1_fresh  : one full forward pass per sentence (no prefix reuse)
  gen_terse : one prompt listing the K sentences, greedy generation of a compact verdict list
Decode speed (ms/token) is also recorded to estimate rationale-writing judges.
Usage: python 04_speed.py qwen0.5b|qwen3b
"""
import statistics as st
import sys
import time

import mlx.core as mx
import pandas as pd
from mlx_lm import load, stream_generate
from mlx_lm.models.cache import make_prompt_cache, trim_prompt_cache

from common import DATA, MODELS, RESULTS, log, write_json

key = sys.argv[1]
mx.set_memory_limit(int(7e9))
mx.set_cache_limit(int(1e9))
model, tok = load(MODELS[key])
A, B = tok.encode("A", add_special_tokens=False)[0], tok.encode("B", add_special_tokens=False)[0]
SYS = "You are a faithfulness verifier. Reply with one letter: A = supported, B = not supported."

df = pd.read_parquet(DATA / "eval_samples.parquet")
rs = df[df.set == "rt_sent"]
# long contexts to cut from, and answers with >= 8 sentences
docs = sorted(df[df.set.isin(["rt_resp", "rt_sent"])]["doc"].unique(), key=len, reverse=True)
answers = [g.sort_values("sent_idx")["claim"].tolist() for _, g in rs.groupby("response_id") if g["K"].iloc[0] >= 8][:3]


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


def s1_prompts(doc, sents):
    ans = " ".join(sents)
    return [tok.encode(chat(f"DOCUMENT:\n{doc}\n\nANSWER:\n{ans}\n\nFOCUS sentence:\n{s}\n\nIs the FOCUS sentence supported by the DOCUMENT?"),
                       add_special_tokens=False) for s in sents]


def run_shared(prompts):
    common = 0
    while all(len(p) > common for p in prompts) and len({p[common] for p in prompts}) == 1:
        common += 1
    common -= 1  # keep >= 1 suffix token for every prompt
    t = time.perf_counter()
    cache = make_prompt_cache(model)
    mx.eval(model(mx.array([prompts[0][:common]]), cache=cache))
    t_pre = time.perf_counter() - t
    probs = []
    for p in prompts:
        suf = p[common:]
        lg = model(mx.array([suf]), cache=cache)[0, -1]
        pr = mx.softmax(mx.stack([lg[A], lg[B]]).astype(mx.float32))
        mx.eval(pr)
        probs.append(float(pr[0].item()))
        trim_prompt_cache(cache, len(suf))
    return time.perf_counter() - t, t_pre, common, probs


def run_fresh(prompts):
    t = time.perf_counter()
    probs = []
    for p in prompts:
        lg = model(mx.array([p]))[0, -1]
        pr = mx.softmax(mx.stack([lg[A], lg[B]]).astype(mx.float32))
        mx.eval(pr)
        probs.append(float(pr[0].item()))
    return time.perf_counter() - t, probs


def run_gen(doc, sents):
    listing = "\n".join(f"{i+1}. {s}" for i, s in enumerate(sents))
    prompt = chat(f"DOCUMENT:\n{doc}\n\nSENTENCES:\n{listing}\n\nFor each sentence, say whether it is supported by the DOCUMENT. "
                  f"Reply only with one line per sentence in the form '<number>: supported' or '<number>: not supported'.")
    t = time.perf_counter()
    last = None
    for last in stream_generate(model, tok, prompt, max_tokens=12 * len(sents) + 10):
        pass
    total = time.perf_counter() - t
    return total, last.prompt_tokens, last.generation_tokens, last.generation_tps, last.text


# warm-up
p = s1_prompts(doc_of_len(200, 0), answers[0][:2])
run_shared(p); run_fresh(p); run_gen(doc_of_len(200, 0), answers[0][:2])
mx.reset_peak_memory()

rows = []
for L in [500, 1000, 2000]:
    for K in [1, 3, 8]:
        for rep in range(3):
            sents = answers[rep % len(answers)][:K]
            doc = doc_of_len(L, rep)
            prompts = s1_prompts(doc, sents)
            ts, tpre, common, p_sh = run_shared(prompts)
            tf, p_fr = run_fresh(prompts)
            tg, ptok, gtok, tps, text = run_gen(doc, sents)
            rows.append({"L": L, "K": K, "rep": rep, "prefix_tokens": common, "s1_shared_ms": ts * 1000,
                         "s1_prefill_ms": tpre * 1000, "s1_fresh_ms": tf * 1000, "gen_ms": tg * 1000,
                         "gen_prompt_tokens": ptok, "gen_tokens": gtok, "gen_tps": tps,
                         "max_abs_dp_shared_vs_fresh": max(abs(a - b) for a, b in zip(p_sh, p_fr)),
                         "gen_text": text[:300]})
        log(f"{key} L={L} K={K} shared={st.median(r['s1_shared_ms'] for r in rows[-3:]):.0f} "
            f"fresh={st.median(r['s1_fresh_ms'] for r in rows[-3:]):.0f} gen={st.median(r['gen_ms'] for r in rows[-3:]):.0f} ms")
res = pd.DataFrame(rows)
res.to_csv(RESULTS / f"04_speed_{key}.csv", index=False)
summary = res.groupby(["L", "K"])[["s1_shared_ms", "s1_prefill_ms", "s1_fresh_ms", "gen_ms", "gen_tokens", "gen_tps",
                                    "max_abs_dp_shared_vs_fresh"]].median().round(2)
summary["speedup_gen_over_shared"] = (summary["gen_ms"] / summary["s1_shared_ms"]).round(2)
summary["speedup_fresh_over_shared"] = (summary["s1_fresh_ms"] / summary["s1_shared_ms"]).round(2)
out = {"model": MODELS[key], "peak_mem_gb": mx.get_peak_memory() / 1e9,
       "decode_ms_per_token_median": float(1000 / res["gen_tps"].median()),
       "table": {f"L{l}_K{k}": v for (l, k), v in summary.to_dict("index").items()}}
write_json(RESULTS / f"04_speed_{key}.json", out)
log("done " + key)
