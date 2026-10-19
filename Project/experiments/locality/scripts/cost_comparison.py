"""Order-of-magnitude cost of verifying N RAG answers: hosted LLM judge (API list prices) vs GroundOne on the laptop.

Hosted: input = median T1 document + answer tokens (Qwen2.5 tokenizer; provider tokenizers differ by a few per cent)
plus a judge-instruction overhead; output = tokens per answer measured for our 3B judges (terse and verbose).
Prices: official pages accessed 2026-10-19 (copies in Vault/raw/local_inference/), standard tier, short context, USD.
Local: measured net chip energy per answer (powermetrics: CPU + GPU + ANE, no DRAM/display/SSD) x EU average household
electricity price (Eurostat, second half of 2025). Excludes hardware cost and quality differences.
Usage (from Project/GroundOne): .venv/bin/python ../experiments/locality/scripts/cost_comparison.py
"""
import json
import statistics

from groundone.config import RESULTS_DIR
from groundone.data.build import OUT

N = 10_000
INSTRUCTION_TOKENS = 150
PRICES = {  # USD per 1M tokens (input, output), standard tier, accessed 2026-10-19
    "Claude Haiku 5.5": (0.10, 0.50), "Claude Sonnet 5.5": (2.00, 10.00), "Claude Opus 5.5": (4.00, 20.00),
    "gpt-6-luna": (0.10, 0.50), "gpt-6.1-sol": (2.00, 10.00), "gpt-6-astra": (10.00, 50.00),
    "Gemini 3.5 Flash-Lite": (0.30, 2.50), "Gemini 3.8 Flash": (0.75, 3.75), "Gemini 4 Argon": (2.00, 10.00),
}
EUR_PER_KWH = 0.2896  # EU average household price incl. taxes, 2nd half 2025 (Eurostat)


def main():
    recs = [json.loads(l) for l in open(OUT / "test_ragtruth.jsonl")]
    doc_answer = statistics.median(r["meta"]["n_tokens"] for r in recs)
    tin = doc_answer + INSTRUCTION_TOKENS
    out_tok = {k: json.loads((RESULTS_DIR / f"judge-{k}-3b" / "latency" / "metrics.json").read_text())["latency_all"]["mean_generated_tokens"]
               for k in ("terse", "verbose")}
    hosted = {m: {k: round(N * (tin * pi + o * po) / 1e6, 2) for k, o in out_tok.items()} for m, (pi, po) in PRICES.items()}
    local = {}
    for size, name in (("0.5B", "energy-g1-05b"), ("3B", "energy-g1-3b")):
        j = json.loads((RESULTS_DIR / name / "energy" / "metrics.json").read_text())["energy"]["net_joules_per_answer"]
        kwh = N * j / 3.6e6
        local[f"GroundOne {size}"] = {"joules_per_answer": round(j, 2), "kwh": round(kwh, 4), "eur": round(kwh * EUR_PER_KWH, 4)}
    res = {"answers": N, "input_tokens_per_answer": tin, "median_doc_answer_tokens": doc_answer,
           "judge_output_tokens_per_answer": out_tok, "hosted_usd": hosted, "local_energy": local,
           "eur_per_kwh": EUR_PER_KWH, "prices_accessed": "2026-10-19",
           "notes": "list prices, standard tier, short context, no caching or batch discounts; local = chip energy only, "
                    "no hardware amortisation; quality of hosted judges not measured"}
    (RESULTS_DIR / "locality").mkdir(exist_ok=True)
    (RESULTS_DIR / "locality" / "cost_comparison.json").write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
