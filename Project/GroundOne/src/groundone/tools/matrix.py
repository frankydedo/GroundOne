"""Results matrix: every system on every test set, read from outputs/results/*/metrics.json (never typed by hand).

Writes a Markdown block between the markers `<!-- results-matrix:start -->` and `<!-- results-matrix:end -->` in
docs/tracker.md (or prints it with --print). Re-run after every new result: `groundone matrix`.
Columns: T1 RAGTruth test (three-way balanced accuracy, binary balanced accuracy at 0.5, AUROC), T2 LLM-AggreFact
(macro over 11 datasets, RAG subset), T3 VitaminC (three-way, AUROC), median seconds per answer at K >= 14 on the
latency subset, calibrated binary ECE on T1.
"""
import argparse
import json

from ..config import PROJECT, RESULTS_DIR, DATA_PROCESSED

START, END = "<!-- results-matrix:start -->", "<!-- results-matrix:end -->"
SYSTEMS = [  # (label, results folder, note)
    ("GroundOne 0.5B", "g1-05b-b1", ""),
    ("GroundOne 3B", "g1-3b-b1", ""),
    ("Untrained 0.5B (design a)", "untrained-05b", ""),
    ("Untrained 3B (design a)", "untrained-3b", "T1 on 600 answers"),
    ("MiniCheck-RoBERTa", "minicheck-roberta", "binary only; T2 from the earlier run on the same test; T3 in its training lineage"),
    ("HHEM-2.1-open", "hhem", "binary only"),
    ("Rizzo-Flow 4B Q4", "rizzo-flow-4b-q4", "T1 300 answers, T3 600 pairs; T2 earlier run on 1,100 items"),
]
LEGACY_T2 = {"minicheck-roberta": "minicheck-roberta", "rizzo-flow-4b-q4": "rizzo-flow-4b-q4"}  # same frozen T2 file
JUDGES = [("GroundOne 0.5B", "g1-05b-b1"), ("Terse judge 0.5B", "judge-terse-05b"), ("Verbose judge 0.5B", "judge-verbose-05b"),
          ("Equal-output judge, verbalised 0.5B", "judge-json-05b"), ("Equal-output judge, logits 0.5B", "judge-tlogit-05b"),
          ("GroundOne 3B", "g1-3b-b1"), ("Terse judge 3B", "judge-terse-3b"), ("Verbose judge 3B", "judge-verbose-3b"),
          ("Equal-output judge, verbalised 3B", "judge-json-3b"), ("Equal-output judge, logits 3B", "judge-tlogit-3b")]


def load(name, suite):
    p = RESULTS_DIR / name / suite / "metrics.json"
    return json.loads(p.read_text()) if p.exists() else None


def legacy_t2(name):
    p = PROJECT / "_archive" / "results-legacy-v1" / LEGACY_T2.get(name, "-") / "aggrefact" / "metrics.json"
    return json.loads(p.read_text()) if p.exists() else None


def f(x, pct=False):
    if x is None:
        return "–"
    return f"{x * 100:.1f}" if pct else f"{x:.3f}"


def block_of(m):
    return m.get("binary") or m["all"]["binary"]


def bold_best(rows, cols, lower_is_better=()):
    """Bold the best numeric value of each listed column (ties all bold). rows: list of cell lists."""
    for c in cols:
        vals = []
        for r in rows:
            try:
                vals.append(float(r[c].rstrip("%")))
            except (ValueError, AttributeError):
                vals.append(None)
        nums = [v for v in vals if v is not None]
        if len(nums) < 2:
            continue
        best = min(nums) if c in lower_is_better else max(nums)
        for r, v in zip(rows, vals):
            if v is not None and v == best:
                r[c] = f"**{r[c]}**"


def build():
    head = ("| System | T1 three-way | T1 binary bacc | T1 AUROC | T2 macro | T2 RAG subset | T3 three-way | T3 AUROC | "
            "s/answer K≥14 | T1 ECE (cal.) | Notes |")
    rows = [head, "| " + " | ".join(["---"] * 11) + " |"]
    cells_all = []
    for label, name, note in SYSTEMS:
        t1, t3, t2 = load(name, "t1"), load(name, "t3"), load(name, "t2") or legacy_t2(name)
        lat, cal = load(name, "latency"), load(name, "calibration")
        cells = [label,
                 f(t1["all"]["macro_recall"]) if t1 and "all" in t1 else "–",
                 f(block_of(t1)["bacc"]) if t1 else "–", f(block_of(t1)["auroc"]) if t1 else "–",
                 f(t2.get("macro_bacc"), True) if t2 else "–", f(t2.get("rag_subset_bacc"), True) if t2 else "–",
                 f(t3["all"]["macro_recall"]) if t3 and "all" in t3 else "–",
                 f(block_of(t3)["auroc"]) if t3 else "–",
                 f"{lat['latency_by_K_band']['>=14']['median_s']:.2f}" if lat and ">=14" in lat.get("latency_by_K_band", {}) else "–",
                 f(cal["t1"]["affine"]["binary"]["ece15"]) if cal and "t1" in cal else "–", note]
        cells_all.append(cells)
    bold_best(cells_all, cols=range(1, 10), lower_is_better=(8, 9))
    rows += ["| " + " | ".join(c) + " |" for c in cells_all]
    ref = load("g1-05b-b1", "t1") or {}
    shortcut = json.loads((DATA_PROCESSED / "groundone" / "shortcut_report.json").read_text())
    t3ref = load("g1-05b-b1", "t3") or {}
    rows.append(f"| Word overlap (no model) | – | – | {f(ref.get('baseline_word_overlap_auroc'))} | – | – | – | "
                f"{f(t3ref.get('baseline_word_overlap_auroc'))} | – | – | never reads the document as a whole |")
    rows.append(f"| Sentence only (n-grams) | {f(shortcut.get('test_ragtruth'))} | – | – | – | – | "
                f"{f(shortcut.get('test_vitaminc'))} | – | – | – | ignores the document |")
    rows.append("| *Published (leaderboard)* | – | – | – | Qwen2.5-0.5B 64.2 · Qwen2.5-7B 72.8 · MiniCheck-FT5 75.0 | – | – | – | – | – | not re-run |")
    jrows = ["| System (latency subset: 200 T1 answers) | Three-way (failures wrong) | Format failures | s/answer K≥14 | "
             "s/answer overall | Generated tokens/answer | Binary ECE raw | Binary ECE cal. |",
             "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    jcells = []
    for label, name in JUDGES:
        m = load(name, "latency")
        cp = RESULTS_DIR / name / "latency" / "calibration.json"
        c = json.loads(cp.read_text())["t1"] if cp.exists() else None
        if m:
            jcells.append([label, f"{m['macro_recall_failures_wrong']:.3f}", f"{m['format_failure_rate'] * 100:.1f}%",
                           f"{m['latency_by_K_band']['>=14']['median_s']:.2f}", f"{m['latency_all']['median_s']:.2f}",
                           f"{m['latency_all']['mean_generated_tokens']:.0f}",
                           f(c["raw"]["binary"]["ece15"]) if c else "–", f(c["affine"]["binary"]["ece15"]) if c else "–"])
    for size in ("0.5B", "3B"):  # bold within each model size: the comparison is at equal size
        bold_best([r for r in jcells if r[0].endswith(size)], cols=range(1, 8), lower_is_better=(2, 3, 4, 5, 6, 7))
    jrows += ["| " + " | ".join(c) + " |" for c in jcells]
    return "\n".join([START, "", "\n".join(rows), "", "\n".join(jrows), "",
                      "*Generated by `groundone matrix` from `outputs/results/*/metrics.json`; do not edit by hand. "
                      "**Bold** = best value in its column among the listed systems (lowest for latency, ECE, failures and "
                      "tokens; in the judge table, within each model size). ECE in the judge table: sentences with a valid "
                      "verdict, calibration fitted on 200 dev answers (`judges-calibrate`); terse and verbose judges give "
                      "no probabilities. Check the notes before reading a bold cell: some values come from subsamples or from a "
                      "system whose training data include that test's source.*", "", END])


def main(argv=None):
    ap = argparse.ArgumentParser(prog="groundone matrix")
    ap.add_argument("--print", action="store_true", help="print instead of writing docs/tracker.md")
    a = ap.parse_args(argv)
    md = build()
    if a.print:
        print(md)
        return
    p = PROJECT / "docs" / "tracker.md"
    s = p.read_text()
    if START in s and END in s:
        s = s[:s.index(START)] + md + s[s.index(END) + len(END):]
    else:
        anchor = "## To-dos"
        s = s.replace(anchor, "## Results matrix\n\n" + md + "\n\n" + anchor, 1)
    p.write_text(s)
    print("results matrix written to", p)


if __name__ == "__main__":
    main()
