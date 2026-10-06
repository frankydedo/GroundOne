"""Training and dev rows for readout design (a): one prompt per scored sentence, the single three-way question (D20).

Reads the answer-level records of Project/data/processed/groundone/ and writes:
  train_rows_a.jsonl  class-balanced sample of scored training sentences (default 3,500 per class); each row keeps the
                      full numbered answer as context, so positions and K follow the natural distribution
  dev_rows_a.jsonl    fixed class-balanced dev subset (default 200 per class) with block = task, for checkpoint
                      selection on mean balanced accuracy (train.py --dev-file dev_rows_a --select bacc)
Usage: groundone data rows [--per-class 3500] [--dev-per-class 200]
"""
import argparse
import json
import random
from collections import Counter

from ..prompts import SUPPORTED, CONTRADICTED, NOT_MENTIONED, label_for
from .build import OUT

CLASSES = (SUPPORTED, CONTRADICTED, NOT_MENTIONED)


def sentences(name):
    out = []
    for l in open(OUT / f"{name}.jsonl"):
        r = json.loads(l)
        for i, y in enumerate(r["labels"]):
            if y is not None:
                out.append({"id": f"{r['id']}-{i}", "source": r["source"], "group": r["group"], "task": r["task"],
                            "doc": r["doc"], "sentences": r["sentences"], "idx": i, "cls": y, "K": r["meta"]["K"]})
    return out


def balanced(items, per_class, rng):
    out = []
    for c in CLASSES:
        pool = [x for x in items if x["cls"] == c]
        rng.shuffle(pool)
        out += pool[:per_class]
    rng.shuffle(out)
    return [{**x, "qtype": "three", "label": label_for("three", x["cls"])} for x in out]


def main(argv=None):
    ap = argparse.ArgumentParser(prog="groundone data rows")
    ap.add_argument("--per-class", type=int, default=3500)
    ap.add_argument("--dev-per-class", type=int, default=200)
    ap.add_argument("--seed", type=int, default=1234)
    a = ap.parse_args(argv)
    rng = random.Random(a.seed)
    train = balanced(sentences("train"), a.per_class, rng)
    dev = [{**x, "block": x["task"]} for x in balanced(sentences("dev"), a.dev_per_class, rng)]
    for name, rows in (("train_rows_a", train), ("dev_rows_a", dev)):
        with open(OUT / f"{name}.jsonl", "w") as f:
            for x in rows:
                f.write(json.dumps(x, ensure_ascii=False) + "\n")
        print(f"{name}: {len(rows)} rows, {dict(Counter(x['cls'] for x in rows))}, tasks {dict(Counter(x['task'] for x in rows))}")


if __name__ == "__main__":
    main()
