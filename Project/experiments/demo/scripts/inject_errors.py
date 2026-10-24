"""Injected-error set for the demo case study (D30, demo_architecture.md §8 and decision 13).

Takes T1 answers whose reference labels are all "supported" and that GroundOne 3B accepts (every scored sentence
supported under the served rule: calibrated P(supported) >= tau), and injects exactly one controlled error per answer:
a swapped number, a swapped name, a swapped date (each replaced by one absent from the document), or one fabricated
sentence inserted after a random sentence. The injected position and the wrong string are the ground truth, independent
of GroundOne. 100 answers, 25 per error type, stratified by task where possible; seed 0.

Usage (from Project/): GroundOne/.venv/bin/python experiments/demo/scripts/inject_errors.py [--out NAME] [--exclude NAME] [--seed S]
Output: outputs/demo/casestudy/injected.jsonl (+ a summary on stdout). A second, disjoint set (answers not in --exclude)
was drawn to evaluate the revision prompt chosen after inspecting the first set.
"""
import json
import math
import random
import re
from pathlib import Path

import pandas as pd

P = Path(__file__).resolve().parents[3]
T1 = P / "data/processed/groundone/test_ragtruth.jsonl"
PRED = P / "outputs/results/g1-3b-b1/t1/predictions.parquet"
CAL = P / "outputs/models/g1-3b-b1/best/calibration.json"
CSDIR = P / "outputs/demo/casestudy"

NAMES = ["Margaret Okafor", "Henrik Dalberg", "Lucia Ferrante", "Tomasz Wielgosz", "Aiko Tanabe", "Rafael Quintero",
         "Ingrid Solheim", "Dmitri Volkov", "Priya Raman", "Olusegun Adeyemi", "Clara Whitfield", "Mateo Arrieta"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November",
          "December"]
FABRICATED = {
    "Summary": ["The findings were later reviewed by an independent panel at the University of Geneva in 2009.",
                "Officials said a formal inquiry would be completed within six weeks.",
                "The announcement was welcomed by more than 40 local organisations."],
    "QA": ["This was confirmed by a 2011 study from the University of Toronto.",
           "Most experts recommend repeating the process every 18 months.",
           "The method was first introduced in Sweden in the early 1970s."],
    "Data2txt": ["It also offers free valet parking and live jazz on Friday evenings.",
                 "The owner has run the business for more than 25 years.",
                 "It was named the best brunch spot in the city by a local magazine in 2019."],
}
NUM = re.compile(r"(?<![\w.])(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)(?![\w.]*\d)")
YEAR = re.compile(r"\b(19[5-9]\d|20[0-3]\d)\b")
MONTH = re.compile(r"\b(" + "|".join(MONTHS) + r")\b")
NAME = re.compile(r"\b([A-Z][a-z]+(?: [A-Z][a-z]+)+)\b")


def calibrated(p, t, b):
    z = [math.log(max(x, 1e-12)) / t + bb for x, bb in zip(p, b)]
    m = max(z)
    e = [math.exp(v - m) for v in z]
    return [v / sum(e) for v in e]


def swap_number(s, doc, rng):
    nums = [m for m in NUM.finditer(s) if not YEAR.fullmatch(m.group(1))]
    if not nums:
        return None
    m = rng.choice(nums)
    v = m.group(1)
    x = float(v.replace(",", ""))
    for f in rng.sample([2, 3, 0.5, 1.5, 4, 10], 6):
        new = x * f
        new_s = f"{int(round(new)):,}" if "," in v else (str(int(round(new))) if "." not in v else f"{new:.1f}")
        if new_s != v and new_s not in doc:
            return s[:m.start(1)] + new_s + s[m.end(1):], v, new_s
    return None


def swap_date(s, doc, rng):
    ys = list(YEAR.finditer(s))
    if ys:
        m = rng.choice(ys)
        for d in rng.sample([-7, -5, -3, 3, 5, 7], 6):
            new = str(int(m.group(1)) + d)
            if new not in doc:
                return s[:m.start(1)] + new + s[m.end(1):], m.group(1), new
    ms = list(MONTH.finditer(s))
    if ms:
        m = rng.choice(ms)
        for new in rng.sample(MONTHS, 12):
            if new != m.group(1) and new not in doc:
                return s[:m.start(1)] + new + s[m.end(1):], m.group(1), new
    return None


def swap_name(s, doc, rng):
    cands = [m for m in NAME.finditer(s) if m.start() > 0 and m.group(1).split()[0] not in MONTHS]
    if not cands:
        return None
    m = rng.choice(cands)
    for new in rng.sample(NAMES, len(NAMES)):
        if new not in doc:
            return s[:m.start(1)] + new + s[m.end(1):], m.group(1), new
    return None


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="injected.jsonl")
    ap.add_argument("--exclude", default=None)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    OUT = CSDIR / a.out
    if OUT.exists():
        raise SystemExit(f"{OUT} exists")
    excluded = {json.loads(l)["id"] for l in open(CSDIR / a.exclude)} if a.exclude else set()
    cal = json.loads(CAL.read_text())
    t, b, tau = cal["temperatures"]["three"], cal["biases"]["three"], cal["thresholds"]["three"]
    pred = pd.read_parquet(PRED)
    accepted_by_rid = {}
    for _, r in pred.iterrows():
        rid = r["id"].rsplit("-", 1)[0]
        ok = calibrated(list(r["p"]), t, b)[0] >= tau and r["cls"] == "supported"
        accepted_by_rid[rid] = accepted_by_rid.get(rid, True) and ok
    recs = [json.loads(l) for l in open(T1)]
    pool = [r for r in recs if accepted_by_rid.get(r["id"]) and all(y in ("supported", None) for y in r["labels"])
            and sum(y is not None for y in r["labels"]) >= 2 and r["id"] not in excluded]
    rng = random.Random(a.seed)
    rng.shuffle(pool)
    kinds = {"number": swap_number, "name": swap_name, "date": swap_date}
    out, used = [], set()
    for kind in ["number", "name", "date", "fabricated"]:
        per_task = {"Summary": 0, "QA": 0, "Data2txt": 0}
        n = 0
        queues = {t: [r for r in pool if r["task"] == t] for t in per_task}
        order = [q[i] for i in range(max(map(len, queues.values()))) for q in queues.values() if i < len(q)]
        for r in order:  # round robin over tasks
            if n == 25:
                break
            if r["id"] in used:
                continue
            scored = [i for i, y in enumerate(r["labels"]) if y is not None]
            sents = list(r["sentences"])
            if kind == "fabricated":
                i = rng.choice(scored)
                fab = rng.choice(FABRICATED[r["task"]])
                if fab in r["doc"]:
                    continue
                sents.insert(i + 1, fab)
                item = {"injected_index": i + 1, "original": None, "injected": fab, "wrong": fab, "right": None}
            else:
                res = None
                for i in rng.sample(scored, len(scored)):
                    res = kinds[kind](sents[i], r["doc"], rng)
                    if res:
                        break
                if not res:
                    continue
                new, right, wrong = res
                item = {"injected_index": i, "original": sents[i], "injected": new, "wrong": wrong, "right": right}
                sents[i] = new
            used.add(r["id"])
            per_task[r["task"]] += 1
            n += 1
            out.append({"id": r["id"], "task": r["task"], "kind": kind, "doc": r["doc"],
                        "answer_original": " ".join(r["sentences"]), "answer_injected": " ".join(sents),
                        "sentences_injected": sents, **item})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("".join(json.dumps(x) + "\n" for x in out))
    print(f"pool {len(pool)} accepted all-supported answers; wrote {len(out)} to {OUT}")
    print(pd.DataFrame(out).groupby(["kind", "task"]).size().unstack(fill_value=0))


if __name__ == "__main__":
    main()
