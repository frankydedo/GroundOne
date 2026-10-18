"""Co-residence on the 16 GB laptop (RQ4 / H4): generator and GroundOne verifier in one process.

One process loads the demo generator (Qwen2.5-3B-Instruct, MLX 4-bit) and a GroundOne verifier (design b, calibrated),
then, for answers sampled from T1, generates a new answer from the document and verifies it sentence by sentence.
Reports MLX peak memory, process peak RSS, load times, generation and verification time per answer.
The retrieved document is given (as in RAGTruth): no retriever is loaded; a BM25 index over a few documents is
negligible and an embedding retriever is measured with the demo.

All MLX work runs on the engine's single worker thread (Metal contexts must not change thread).
Usage (from Project/GroundOne, under the guard):
  .venv/bin/python ../experiments/locality/scripts/coresidence.py --verifier g1-3b-b1/best --name coresidence-3b
"""
import argparse
import json
import random
import resource
import sys
import time

import mlx.core as mx

from groundone.config import MODELS_DIR, RESULTS_DIR
from groundone.data.build import OUT
from groundone.engine import Engine
from groundone.schema import VerifyRequest

GENERATOR = "mlx-community/Qwen2.5-3B-Instruct-4bit"
TASK_PROMPT = {
    "Summary": "Write a short summary of the document.",
    "QA": "Answer the question contained in the document, using only the passages it provides.",
    "Data2txt": "Write a short overview of the business described by the structured data in the document.",
}


def gb(x):
    return round(x / 1e9, 3)


def peak_rss_gb():
    return gb(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)  # bytes on macOS


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--verifier", required=True, help="adapter, e.g. g1-3b-b1/best")
    ap.add_argument("--name", required=True)
    ap.add_argument("--n", type=int, default=30, help="answers, stratified by task")
    ap.add_argument("--max-tokens", type=int, default=300)
    a = ap.parse_args(argv)
    out = RESULTS_DIR / a.name
    if out.exists():
        sys.exit(f"{out} exists: results are create-only")

    recs = [json.loads(l) for l in open(OUT / "test_ragtruth.jsonl")]
    rng = random.Random(0)
    sample = [r for t in TASK_PROMPT for r in rng.sample([x for x in recs if x["task"] == t], a.n // len(TASK_PROMPT))]

    mem = {"start_rss_gb": peak_rss_gb()}
    t = time.perf_counter()
    cal = MODELS_DIR / a.verifier / "calibration.json"
    engine = Engine.load(None, a.verifier, str(cal) if cal.exists() else None)
    mem["verifier_load_s"] = round(time.perf_counter() - t, 2)
    mem["after_verifier"] = {"mlx_active_gb": gb(engine._run(mx.get_active_memory)), "peak_rss_gb": peak_rss_gb()}

    def load_gen():
        from mlx_lm import load
        return load(GENERATOR)

    t = time.perf_counter()
    gen_model, gen_tok = engine._run(load_gen)
    mem["generator_load_s"] = round(time.perf_counter() - t, 2)
    mem["after_generator"] = {"mlx_active_gb": gb(engine._run(mx.get_active_memory)), "peak_rss_gb": peak_rss_gb()}
    engine._run(mx.reset_peak_memory)

    def generate(doc, task):
        from mlx_lm import generate as mlx_generate
        msgs = [{"role": "system", "content": "You are a helpful assistant. Use only the document."},
                {"role": "user", "content": f"{TASK_PROMPT[task]}\n\nDOCUMENT:\n{doc}"}]
        prompt = gen_tok.encode(gen_tok.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False))
        t0 = time.perf_counter()
        text = engine._run(lambda: mlx_generate(gen_model, gen_tok, prompt, max_tokens=a.max_tokens, verbose=False))
        return text, time.perf_counter() - t0, len(prompt), len(gen_tok.encode(text))

    rows = []
    for i, r in enumerate(sample):
        text, gen_s, prompt_tokens, gen_tokens = generate(r["doc"], r["task"])
        t0 = time.perf_counter()
        res = engine.verify(VerifyRequest(document=r["doc"], answer=text))
        ver_s = time.perf_counter() - t0
        rows.append({"id": r["id"], "task": r["task"], "prompt_tokens": prompt_tokens, "generated_tokens": gen_tokens,
                     "generation_s": round(gen_s, 3), "verification_s": round(ver_s, 3),
                     "K": res["n_decisions"], "flagged": sum(1 for s in res["sentences"] if s.get("flagged"))})
        print(f"[{i + 1}/{len(sample)}] {r['task']} gen {gen_s:.1f}s ({gen_tokens} tok) verify {ver_s:.2f}s K={res['n_decisions']}", flush=True)

    def med(k):
        v = sorted(x[k] for x in rows)
        return v[len(v) // 2]
    metrics = {
        "verifier": a.verifier, "generator": GENERATOR, "answers": len(rows), "max_tokens": a.max_tokens,
        "memory": {**mem, "peak_during_loop": {"mlx_peak_gb": gb(engine._run(mx.get_peak_memory)), "peak_rss_gb": peak_rss_gb()}},
        "median": {k: med(k) for k in ("generation_s", "verification_s", "generated_tokens", "K", "prompt_tokens")},
        "verification_share_of_total": round(sum(x["verification_s"] for x in rows) /
                                             sum(x["verification_s"] + x["generation_s"] for x in rows), 4),
        "protocol": "one process, generator 4-bit + GroundOne design b calibrated; greedy generation; T1 documents, "
                    "stratified by task (seed 0); MLX memory from mx.get_*_memory, RSS from getrusage",
    }
    out.mkdir(parents=True)
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2))
    (out / "answers.jsonl").write_text("\n".join(json.dumps(x) for x in rows) + "\n")
    print(json.dumps(metrics, indent=1))


if __name__ == "__main__":
    main()
