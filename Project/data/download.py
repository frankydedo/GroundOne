"""Download every dataset used by GroundOne into Project/data/raw/ and write manifest.json.

Re-running is safe: files that already exist are kept (re-hashed, not re-downloaded).
LLM-AggreFact is gated on Hugging Face: log in (`hf auth login`) and accept its terms first.
Usage: python download.py   (from any directory; uses the Phase 0 environment)
"""
import hashlib
import json
import time
import urllib.request
from pathlib import Path

import pandas as pd
from huggingface_hub import hf_hub_download

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"
RAW.mkdir(exist_ok=True)

SOURCES = {
    "anli": {"origin": "huggingface: facebook/anli", "license": "CC BY-NC 4.0",
             "use": "three-way NLI pairs (entailment / neutral / contradiction); training and rule experiments"},
    "ragtruth": {"origin": "github: ParticleMedia/RAGTruth (dataset/)", "license": "MIT",
                 "use": "RAG responses with span-level hallucination labels; in-domain train and test"},
    "minicheck_synth": {"origin": "huggingface: lytang/C2D-and-D2C-MiniCheck", "license": "MIT",
                        "use": "synthetic multi-sentence grounding data (MiniCheck training recipe)"},
    "llm_aggrefact": {"origin": "huggingface: lytang/LLM-AggreFact (gated)", "license": "CC BY-ND 4.0",
                      "use": "main out-of-distribution benchmark (dev for checks only, test for evaluation)"},
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch_anli(dst):
    from datasets import load_dataset
    ds = load_dataset("facebook/anli")
    out = []
    for split in ds:
        f = dst / f"{split}.parquet"
        if not f.exists():
            ds[split].to_pandas().to_parquet(f)
        out.append(f)
    return out


def fetch_ragtruth(dst):
    base = "https://raw.githubusercontent.com/ParticleMedia/RAGTruth/main/dataset/"
    out = []
    for fn in ["response.jsonl", "source_info.jsonl"]:
        f = dst / fn
        if not f.exists():
            urllib.request.urlretrieve(base + fn, f)
        out.append(f)
    return out


def fetch_hf_parquets(dst, repo, files):
    out = []
    for name, remote in files.items():
        f = dst / f"{name}.parquet"
        if not f.exists():
            pd.read_parquet(hf_hub_download(repo, remote, repo_type="dataset")).to_parquet(f)
        out.append(f)
    return out


FETCH = {
    "anli": fetch_anli,
    "ragtruth": fetch_ragtruth,
    "minicheck_synth": lambda d: fetch_hf_parquets(d, "lytang/C2D-and-D2C-MiniCheck", {
        "c2d": "data/c2d-00000-of-00001-5a473df7966a0bbe.parquet",
        "d2c": "data/d2c-00000-of-00001-fb38b2c3dc66f609.parquet"}),
    "llm_aggrefact": lambda d: fetch_hf_parquets(d, "lytang/LLM-AggreFact", {
        "dev": "data/dev-00000-of-00001.parquet", "test": "data/test-00000-of-00001.parquet"}),
}


def n_rows(f):
    if f.suffix == ".parquet":
        return len(pd.read_parquet(f))
    return sum(1 for _ in open(f))


manifest = {"created": time.strftime("%Y-%m-%d %H:%M:%S"), "datasets": {}}
for name, meta in SOURCES.items():
    d = RAW / name
    d.mkdir(exist_ok=True)
    print(f"[{name}] ...", flush=True)
    files = FETCH[name](d)
    manifest["datasets"][name] = {**meta, "files": {f.name: {"rows": n_rows(f), "bytes": f.stat().st_size, "sha256": sha256(f)}
                                                     for f in files}}
    print(f"[{name}] " + ", ".join(f"{k}: {v['rows']} rows" for k, v in manifest["datasets"][name]["files"].items()), flush=True)
(ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2))
print("manifest written")
