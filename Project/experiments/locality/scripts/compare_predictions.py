"""Compare two prediction files of the same frozen test (same sentences): probability differences and decision agreement.

Used for the offline proof (expect identical predictions) and for the 8-bit vs bf16 base comparison.
Usage: .venv/bin/python ../experiments/locality/scripts/compare_predictions.py RESULTS_A RESULTS_B SUITE OUT_JSON
"""
import json
import sys

import numpy as np
import pandas as pd

from groundone.config import RESULTS_DIR


def main(a, b, suite, out):
    A = pd.read_parquet(RESULTS_DIR / a / suite / "predictions.parquet")
    B = pd.read_parquet(RESULTS_DIR / b / suite / "predictions.parquet")
    m = A.merge(B, on="id", suffixes=("_a", "_b"))
    pa, pb = np.stack(m["p_a"].values), np.stack(m["p_b"].values)
    d = np.abs(pa - pb)
    ma = json.loads((RESULTS_DIR / a / suite / "metrics.json").read_text())
    mb = json.loads((RESULTS_DIR / b / suite / "metrics.json").read_text())
    res = {"a": a, "b": b, "suite": suite, "sentences_compared": int(len(m)), "sentences_a": int(len(A)), "sentences_b": int(len(B)),
           "identical": bool(np.array_equal(pa, pb)),
           "abs_diff_p": {"mean": float(d.mean()), "p99": float(np.quantile(d, 0.99)), "max": float(d.max())},
           "argmax_agreement": float((pa.argmax(1) == pb.argmax(1)).mean()),
           "three_way_bacc": {"a": ma["all"]["macro_recall"], "b": mb["all"]["macro_recall"]},
           "auroc": {"a": ma["all"]["binary"]["auroc"], "b": mb["all"]["binary"]["auroc"]}}
    (RESULTS_DIR / out).parent.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / out).write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:5])
