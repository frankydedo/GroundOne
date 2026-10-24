"""Fixtures for the Swift conformance test of the demo app (demo_architecture.md §5.3).

For N frozen T1 answers, stratified by K as the latency subset, writes what the Swift port must reproduce: token ids
and marker positions of the design-(b) prompt, raw A/B/C logits at the markers, calibrated probabilities and served
labels. A second file holds every T1 answer as raw text with the pysbd segmentation, for the (reported, not gated)
segmentation agreement. Outputs go to outputs/demo/fixtures/ (gitignored, like the other predictions).

Usage (from Project/GroundOne, under the guard):
  .venv/bin/python -m groundone.tools.export_fixtures --adapter g1-3b-b1/best --n 200
  .venv/bin/python -m groundone.tools.export_fixtures --segmentation
"""
import argparse
import json

from ..baselines.judges import k_stratified
from ..calibration import decide_three
from ..config import DATA_RAW, MODELS_DIR, OUTPUTS
from ..data.build import OUT, k_band
from ..prompts import MARKER, PROMPT_VERSION_MARKED, encode_marked

FIXTURES = OUTPUTS / "demo" / "fixtures"


def export_model(adapter, n):
    from ..engine import Engine
    cal_path = MODELS_DIR / adapter / "calibration.json"
    engine = Engine.load(None, adapter, str(cal_path))
    be, cal = engine.backend, engine.calibration
    tok = be.tokenizer
    recs = [json.loads(l) for l in open(OUT / "test_ragtruth.jsonl")]
    nb = len({k_band(r["meta"]["K"]) for r in recs})
    sample = k_stratified(recs, n // nb)
    tau = cal.thresholds["three"]
    items = []
    for r in sample:
        scored = [y is not None for y in r["labels"]]
        ids, pos = encode_marked(tok, r["doc"], r["sentences"], scored)
        logits = engine._run(be.score_positions, [ids], [pos])[0] if pos else []
        probs = [cal.probs("three", lg) for lg in logits]
        items.append({"id": r["id"], "task": r["task"], "doc": r["doc"], "sentences": r["sentences"], "scored": scored,
                      "ids": ids, "positions": pos, "logits": logits, "probs": probs,
                      "labels": [decide_three(p, tau) for p in probs]})
    out = {"adapter": adapter, "base_model": be.metadata["base_model"], "prompt_version": PROMPT_VERSION_MARKED,
           "marker": MARKER, "letter_ids": [be.letter_ids[L] for L in "ABC"],
           "calibration": {"temperature": cal.temperatures["three"], "bias": cal.biases["three"], "threshold": tau},
           "tokenizer_probe": {s: tok.encode(s, add_special_tokens=False) for s in
                               (MARKER, "\n", "[1] The café costs $4.50 – “cheap”.", "<|im_start|>system\n")},
           "n": len(items), "items": items}
    FIXTURES.mkdir(parents=True, exist_ok=True)
    path = FIXTURES / f"conformance-{adapter.split('/')[0]}.json"
    path.write_text(json.dumps(out))
    print(f"{path}: {len(items)} answers, {sum(len(i['positions']) for i in items)} markers ({nb} K bands)")


def export_segmentation():
    from ..data.segment import segment
    recs = [json.loads(l) for l in open(OUT / "test_ragtruth.jsonl")]
    want = {r["meta"]["response_id"]: r["id"] for r in recs}
    items = []
    for line in open(DATA_RAW / "ragtruth" / "response.jsonl"):
        x = json.loads(line)
        if str(x["id"]) in want:
            segs = segment(x["response"])
            items.append({"id": want[str(x["id"])], "text": x["response"],
                          "sentences": [s.text for s in segs], "checkable": [s.checkable for s in segs]})
    FIXTURES.mkdir(parents=True, exist_ok=True)
    path = FIXTURES / "segmentation-t1.json"
    path.write_text(json.dumps({"segmenter": "pysbd + list markers + checkable rule (data/segment.py)", "items": items}))
    print(f"{path}: {len(items)} answers")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--adapter")
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--segmentation", action="store_true")
    a = ap.parse_args(argv)
    if a.segmentation:
        export_segmentation()
    if a.adapter:
        export_model(a.adapter, a.n)


if __name__ == "__main__":
    main()
