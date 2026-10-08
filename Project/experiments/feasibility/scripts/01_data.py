"""Phase 0, step 1: download data, check access/licences/sizes, build evaluation samples."""
import json
import random
import urllib.request
from collections import Counter

import pandas as pd
from huggingface_hub import HfApi, hf_hub_download

from common import DATA, RESULTS, SEED, log, split_sentences, write_json

api = HfApi()
report = {}


def card_info(repo, repo_type):
    try:
        info = api.repo_info(repo, repo_type=repo_type)
        cd = getattr(info, "card_data", None) or getattr(info, "cardData", None)
        lic = cd.get("license") if cd else None
        return {"license": lic, "gated": getattr(info, "gated", None)}
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)[:200]}


# ---------------- LLM-AggreFact ----------------
rng = random.Random(SEED)

def do_aggrefact():
    log("LLM-AggreFact")
    agg = {}
    for split in ["dev", "test"]:
        p = hf_hub_download("lytang/LLM-AggreFact", f"data/{split}-00000-of-00001.parquet", repo_type="dataset")
        agg[split] = pd.read_parquet(p)
    report["llm_aggrefact"] = {
        "card": card_info("lytang/LLM-AggreFact", "dataset"),
        "columns": list(agg["test"].columns),
        "sizes": {k: len(v) for k, v in agg.items()},
        "per_dataset_test": agg["test"].groupby("dataset")["label"].agg(["count", "mean"]).round(3).to_dict("index"),
        "per_dataset_dev": agg["dev"].groupby("dataset")["label"].agg(["count", "mean"]).round(3).to_dict("index"),
        "doc_chars_test": agg["test"]["doc"].str.len().describe().round(0).to_dict(),
    }
    for k, v in agg.items():
        v.to_parquet(DATA / f"aggrefact_{k}.parquet")

    # stratified test sample: up to 50 per dataset, docs <= 8000 chars (~2k tokens) to keep the run tractable
    test = agg["test"].copy()
    test["doc_len"] = test["doc"].str.len()
    rows = []
    excluded_long = {}
    for name, g in test.groupby("dataset"):
        short = g[g["doc_len"] <= 8000]
        excluded_long[name] = round(1 - len(short) / len(g), 3)
        n = min(50, len(short))
        rows.append(short.sample(n=n, random_state=SEED))
    sample = pd.concat(rows).reset_index(drop=True)
    sample["uid"] = [f"agg{i}" for i in range(len(sample))]
    sample.to_parquet(DATA / "sample_aggrefact.parquet")
    report["llm_aggrefact"]["sample"] = {
        "n": len(sample),
        "per_dataset": sample["dataset"].value_counts().to_dict(),
        "share_of_docs_over_8000_chars_excluded": excluded_long,
    }
    log(f"  sample {len(sample)}")


try:
    do_aggrefact()
except Exception as e:  # noqa: BLE001
    report['llm_aggrefact'] = {'error': str(e)[:400], 'card': card_info('lytang/LLM-AggreFact', 'dataset')}
    log('  LLM-AggreFact unavailable: ' + str(e)[:120])

# ---------------- RAGTruth ----------------
log("RAGTruth")
base = "https://raw.githubusercontent.com/ParticleMedia/RAGTruth/main/dataset/"
for fn in ["response.jsonl", "source_info.jsonl"]:
    dst = DATA / f"ragtruth_{fn}"
    if not dst.exists():
        urllib.request.urlretrieve(base + fn, dst)
resp = [json.loads(l) for l in open(DATA / "ragtruth_response.jsonl")]
src = {d["source_id"]: d for d in (json.loads(l) for l in open(DATA / "ragtruth_source_info.jsonl"))}
lic = None
try:
    lic_txt = urllib.request.urlopen("https://raw.githubusercontent.com/ParticleMedia/RAGTruth/main/LICENSE").read().decode()[:300]
    lic = lic_txt.splitlines()[0]
except Exception as e:  # noqa: BLE001
    lic = f"no LICENSE file found ({str(e)[:80]})"
split_counts = Counter(r.get("split") for r in resp)
task_counts = Counter(src[r["source_id"]]["task_type"] for r in resp)
span_flags = Counter()
for r in resp:
    for lab in r.get("labels", []):
        span_flags["spans"] += 1
        span_flags["implicit_true"] += bool(lab.get("implicit_true"))
        span_flags["due_to_null"] += bool(lab.get("due_to_null"))
report["ragtruth"] = {
    "license": lic,
    "responses": len(resp),
    "sources": len(src),
    "split_counts": dict(split_counts),
    "task_counts": dict(task_counts),
    "span_flags": dict(span_flags),
    "response_keys": list(resp[0].keys()),
    "source_keys": list(next(iter(src.values())).keys()),
}


def context_of(s):
    info = s["source_info"]
    if s["task_type"] == "QA":
        return f"Question: {info['question']}\n\n{info['passages']}"
    if s["task_type"] == "Summary":
        return info if isinstance(info, str) else json.dumps(info)
    return json.dumps(info, ensure_ascii=False)


# sentence-level labels on the test split: unsupported if the sentence overlaps any span
sent_rows = []
for r in resp:
    if r.get("split") != "test":
        continue
    s = src[r["source_id"]]
    spans = [(l["start"], l["end"]) for l in r.get("labels", [])]
    sents = split_sentences(r["response"])
    for i, (a, b, t) in enumerate(sents):
        unsup = any(a < e and s0 < b for s0, e in spans)
        sent_rows.append({
            "response_id": r["id"], "source_id": r["source_id"], "task": s["task_type"],
            "model": r["model"], "sent_idx": i, "n_sents": len(sents),
            "sentence": t, "label": int(not unsup),
        })
sent_df = pd.DataFrame(sent_rows)
report["ragtruth"]["test_sentences"] = {
    "n": len(sent_df),
    "supported_rate": round(float(sent_df["label"].mean()), 3),
    "by_task": sent_df.groupby("task")["label"].agg(["count", "mean"]).round(3).to_dict("index"),
    "sentences_per_response": sent_df.groupby("response_id")["n_sents"].first().describe().round(2).to_dict(),
}

# sample whole responses (keeps K sentences together) for QA + Summary; ~120 responses
test_resp = [r for r in resp if r.get("split") == "test" and src[r["source_id"]]["task_type"] in ("QA", "Summary")]
rng.shuffle(test_resp)
chosen, ctx_rows = [], []
for r in test_resp:
    ctx = context_of(src[r["source_id"]])
    if len(ctx) > 8000:
        continue
    chosen.append(r["id"])
    ctx_rows.append({"response_id": r["id"], "context": ctx, "response": r["response"], "task": src[r["source_id"]]["task_type"]})
    if len(chosen) >= 120:
        break
rt_sample = sent_df[sent_df["response_id"].isin(chosen)].merge(pd.DataFrame(ctx_rows), on=["response_id", "task"])
rt_sample["uid"] = [f"rt{i}" for i in range(len(rt_sample))]
rt_sample.to_parquet(DATA / "sample_ragtruth.parquet")
report["ragtruth"]["sample"] = {
    "responses": len(chosen), "sentences": len(rt_sample),
    "supported_rate": round(float(rt_sample["label"].mean()), 3),
    "by_task": rt_sample["task"].value_counts().to_dict(),
}
log(f"  sample {len(chosen)} responses / {len(rt_sample)} sentences")

# ---------------- training sources ----------------
log("Training sources")
mc = {}
for name, fn in [("c2d", "data/c2d-00000-of-00001-5a473df7966a0bbe.parquet"), ("d2c", "data/d2c-00000-of-00001-fb38b2c3dc66f609.parquet")]:
    df = pd.read_parquet(hf_hub_download("lytang/C2D-and-D2C-MiniCheck", fn, repo_type="dataset"))
    df.to_parquet(DATA / f"minicheck_{name}.parquet")
    mc[name] = {"n": len(df), "columns": list(df.columns)}
report["minicheck_train"] = {"card": card_info("lytang/C2D-and-D2C-MiniCheck", "dataset"), **mc}
try:
    from datasets import load_dataset
    anli = load_dataset("facebook/anli")
    report["anli"] = {"card": card_info("facebook/anli", "dataset"), "splits": {k: len(v) for k, v in anli.items()}}
except Exception as e:  # noqa: BLE001
    report["anli"] = {"error": str(e)[:300]}
for repo, t in [("vectara/hallucination_evaluation_model", "model"), ("lytang/MiniCheck-Flan-T5-Large", "model"),
                ("lytang/MiniCheck-RoBERTa-Large", "model"), ("lytang/MiniCheck-DeBERTa-v3-Large", "model"),
                ("Qwen/Qwen2.5-0.5B-Instruct", "model"), ("Qwen/Qwen2.5-3B-Instruct", "model"), ("Qwen/Qwen2.5-7B-Instruct", "model")]:
    report.setdefault("model_cards", {})[repo] = card_info(repo, t)

write_json(RESULTS / "01_data.json", report)
log("done")
