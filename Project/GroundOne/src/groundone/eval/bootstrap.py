"""Bootstrap confidence intervals and paired tests from saved predictions (no model is run).

Resampling unit = the leakage group of each record (data/processed/groundone/*.jsonl `group`: RAGTruth source document
for T1 and the latency subset, document for T2, Wikipedia page for T3), so correlated sentences and answers move
together. T2 is resampled within each dataset (its macro averages the datasets). A paired comparison evaluates both
systems on the same resamples of the rows that both scored (e.g. Rizzo-Flow's subsample). 95 % percentile intervals;
two-sided bootstrap p = 2 min(P(d <= 0), P(d >= 0)), floored at 1/B.
Metrics are recomputed with the same definitions as `groundone test` (three-way macro recall of the argmax of the raw
probabilities, D24; binary balanced accuracy at 0.5; AUROC of P(supported)); the point estimates must equal metrics.json.
Output: results/bootstrap/{metrics.json, summary.md}; figures/bootstrap/.
Usage: groundone bootstrap [--reps 2000] [--seed 0]
"""
import argparse
import json

import numpy as np
import pandas as pd
from scipy.stats import rankdata

from ..config import PROJECT, RESULTS_DIR
from ..data.build import OUT
from .evaluate import RAG_SUBSET
from .tests import CLASSES, overlap

LEGACY = PROJECT / "_archive" / "results-legacy-v1"
T1_SYSTEMS = {"GroundOne 0.5B": "g1-05b-b1", "GroundOne 0.5B, run 2": "g1-05b-s3", "GroundOne 3B": "g1-3b-b1", "Untrained 0.5B": "untrained-05b",
              "Untrained 3B": "untrained-3b", "Rizzo-Flow 4B": "rizzo-flow-4b-q4", "d1-3B": "d1-3b", "MiniCheck-RoBERTa": "minicheck-roberta",
              "HHEM": "hhem"}
T2_SYSTEMS = {"GroundOne 0.5B": RESULTS_DIR / "g1-05b-b1", "GroundOne 0.5B, run 2": RESULTS_DIR / "g1-05b-s3",
              "GroundOne 3B": RESULTS_DIR / "g1-3b-b1",
              "MiniCheck-RoBERTa": LEGACY / "minicheck-roberta", "Rizzo-Flow 4B": LEGACY / "rizzo-flow-4b-q4",
              "d1-3B": RESULTS_DIR / "d1-3b"}
JUDGES = {"Terse judge": "judge-terse", "Verbose judge": "judge-verbose", "Equal-output, logits": "judge-tlogit",
          "Equal-output, verbalised": "judge-json"}
PAIRS = [  # (test, metric, A, B): difference A - B
    ("t1", "three_way", "GroundOne 3B", "GroundOne 0.5B"), ("t1", "auroc", "GroundOne 3B", "GroundOne 0.5B"),
    ("t1_k14", "three_way", "GroundOne 3B", "GroundOne 0.5B"),
    ("t1", "three_way", "GroundOne 0.5B", "GroundOne 0.5B, run 2"), ("t1", "auroc", "GroundOne 0.5B", "GroundOne 0.5B, run 2"),
    ("t1_k14", "three_way", "GroundOne 0.5B", "GroundOne 0.5B, run 2"),
    ("t2", "macro_bacc", "GroundOne 0.5B", "GroundOne 0.5B, run 2"), ("t3", "three_way", "GroundOne 0.5B", "GroundOne 0.5B, run 2"),
    ("t3", "auroc", "GroundOne 0.5B", "GroundOne 0.5B, run 2"),
    ("t1", "three_way", "GroundOne 0.5B", "B2 0.5B (generated token)"), ("t1", "three_way", "GroundOne 3B", "B2 3B (generated token)"),
    ("t1_k14", "three_way", "GroundOne 0.5B", "B2 0.5B (generated token)"),
    ("t1_k14", "three_way", "GroundOne 3B", "B2 3B (generated token)"),
    ("t1", "three_way", "GroundOne 0.5B", "Untrained 0.5B"), ("t1", "three_way", "GroundOne 3B", "Untrained 3B"),
    ("t1", "auroc", "GroundOne 0.5B", "Word overlap"), ("t1", "auroc", "GroundOne 3B", "Word overlap"),
    ("t1", "auroc", "GroundOne 0.5B", "MiniCheck-RoBERTa"), ("t1", "auroc", "GroundOne 0.5B", "HHEM"),
    ("t1", "auroc", "GroundOne 3B", "MiniCheck-RoBERTa"), ("t1", "auroc", "GroundOne 3B", "HHEM"),
    ("t1", "bacc", "GroundOne 0.5B", "MiniCheck-RoBERTa"), ("t1", "bacc", "GroundOne 0.5B", "HHEM"),
    ("t1", "bacc", "GroundOne 3B", "MiniCheck-RoBERTa"), ("t1", "bacc", "GroundOne 3B", "HHEM"),
    ("t1", "three_way", "GroundOne 0.5B", "Rizzo-Flow 4B"), ("t1", "three_way", "GroundOne 3B", "Rizzo-Flow 4B"),
    ("t1", "auroc", "GroundOne 0.5B", "Rizzo-Flow 4B"), ("t1", "auroc", "GroundOne 3B", "Rizzo-Flow 4B"),
    ("t1", "three_way", "GroundOne 0.5B", "d1-3B"), ("t1", "three_way", "GroundOne 3B", "d1-3B"),
    ("t1", "auroc", "GroundOne 0.5B", "d1-3B"), ("t1", "auroc", "GroundOne 3B", "d1-3B"),
    ("t1_k14", "three_way", "GroundOne 3B", "d1-3B"),
    ("t3", "three_way", "GroundOne 3B", "d1-3B"), ("t3", "auroc", "GroundOne 3B", "d1-3B"),
    ("t2", "macro_bacc", "GroundOne 3B", "d1-3B"), ("t2", "macro_bacc", "GroundOne 0.5B", "d1-3B"),
    ("t2", "rag_bacc", "GroundOne 3B", "d1-3B"),
    ("t2", "macro_bacc", "GroundOne 3B", "MiniCheck-RoBERTa"), ("t2", "rag_bacc", "GroundOne 3B", "MiniCheck-RoBERTa"),
    ("t2", "macro_bacc", "GroundOne 0.5B", "MiniCheck-RoBERTa"), ("t2", "rag_bacc", "GroundOne 0.5B", "MiniCheck-RoBERTa"),
    ("t2", "macro_bacc", "GroundOne 3B", "GroundOne 0.5B"),
    ("t2", "macro_bacc", "GroundOne 0.5B", "Rizzo-Flow 4B"), ("t2", "macro_bacc", "GroundOne 3B", "Rizzo-Flow 4B"),
    ("t3", "three_way", "GroundOne 3B", "GroundOne 0.5B"), ("t3", "auroc", "GroundOne 3B", "GroundOne 0.5B"),
    ("t3", "three_way", "Rizzo-Flow 4B", "GroundOne 3B"), ("t3", "auroc", "Rizzo-Flow 4B", "GroundOne 3B"),
    ("t3", "auroc", "MiniCheck-RoBERTa", "GroundOne 3B"), ("t3", "auroc", "GroundOne 3B", "Word overlap"),
] + [("lat", m, f"GroundOne {s}", f"{j} {s}") for s in ("0.5B", "3B") for j in JUDGES
     for m in ("three_way", "speedup_k14")]
TESTS = {"t1": "T1 RAGTruth", "t1_k14": "T1 RAGTruth, K ≥ 14", "t2": "T2 LLM-AggreFact", "t3": "T3 VitaminC",
         "lat": "Latency subset (200 T1 answers)"}


# ------------------------------------------------------------------ data
def groups_of(name):
    return {r["id"]: r["group"] for r in (json.loads(l) for l in open(OUT / f"{name}.jsonl"))}


def records(name):
    return {r["id"]: r for r in (json.loads(l) for l in open(OUT / f"{name}.jsonl"))}


def frame_sentences(path, recs):
    """One row per scored sentence: id, group, y (class index), pred (-1 = no verdict), psup."""
    df = pd.read_parquet(path)
    aid = df["id"].str.rsplit("-", n=1).str[0]
    out = pd.DataFrame({"id": df["id"], "group": aid.map(lambda a: recs[a]["group"]),
                        "y": [CLASSES.index(c) for c in df["cls"]]})
    if "p" in df:
        P = np.array([list(p) for p in df["p"]], float)
        out["pred"], out["psup"] = P.argmax(1), P[:, 0]
    else:
        out["pred"], out["psup"] = -2, df["p_supported"].to_numpy()  # -2: binary-only system
    return out


def overlap_frame(ref, recs):
    i = ref["id"].str.rsplit("-", n=1)
    sent = [recs[a]["sentences"][int(k)] for a, k in zip(i.str[0], i.str[1])]
    docs = [recs[a]["doc"] for a in i.str[0]]
    return ref[["id", "group", "y"]].assign(pred=-2, psup=[overlap(s, d) for s, d in zip(sent, docs)])


def frame_b2(path, recs):
    """Control B2: verdict = generated token at the markers (-1 = format failure, always wrong); no probabilities."""
    df = pd.read_parquet(path)
    aid = df["id"].str.rsplit("-", n=1).str[0]
    return pd.DataFrame({"id": df["id"], "group": aid.map(lambda a: recs[a]["group"]),
                         "y": [CLASSES.index(c) for c in df["cls"]], "pred": df["pred_generate"].astype(int)})


def frame_latency(path, recs):
    df = pd.read_parquet(path)
    P = [json.loads(p) if isinstance(p, str) else p for p in df["p"]]
    lab = df["label"] if "label" in df else pd.Series([None] * len(df))
    pred = [(int(l) if l is not None and not pd.isna(l) else int(np.argmax(p))) if p is not None else -1
            for p, l in zip(P, lab)]
    return pd.DataFrame({"id": df["id"], "rid": df["rid"], "group": df["rid"].map(lambda a: recs[a]["group"]),
                         "y": [CLASSES.index(c) for c in df["cls"]], "pred": pred,
                         "sec": df["answer_seconds"], "kband": df["kband"]})


def frame_t2(path, groups):
    """Items a system skipped (no score, e.g. over Rizzo-Flow's context limit) are dropped, as in its own metrics."""
    df = pd.read_parquet(path / ("aggrefact" if "legacy" in str(path) else "t2") / "predictions.parquet")
    df = df[df["p_supported"].notna()]
    return pd.DataFrame({"id": df["id"], "group": df["id"].map(groups), "dataset": df["dataset"],
                         "y": df["label"].astype(int), "psup": df["p_supported"].astype(float)})


# ------------------------------------------------------------------ metrics on a row subset
def m_three_way(d):
    y, p = d["y"].to_numpy(), d["pred"].to_numpy()
    return float(np.mean([(p[y == k] == k).mean() for k in range(3) if (y == k).any()]))


def m_auroc(d):
    y = (d["y"].to_numpy() == 0) if "dataset" not in d else d["y"].to_numpy().astype(bool)
    n1, n0 = y.sum(), (~y).sum()
    r = rankdata(np.clip(d["psup"].to_numpy(), 1e-7, 1 - 1e-7))
    return float((r[y].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def _bacc(y, p):
    pred = p >= 0.5
    return float(np.nanmean([pred[y].mean() if y.any() else np.nan, (~pred[~y]).mean() if (~y).any() else np.nan]))


def m_bacc(d):
    return _bacc(d["y"].to_numpy() == 0, d["psup"].to_numpy())


def m_macro(d, subset=None):
    vals = [_bacc(g["y"].to_numpy().astype(bool), g["psup"].to_numpy()) for k, g in d.groupby("dataset")
            if subset is None or k in subset]
    return float(np.mean(vals))


METRICS = {"three_way": m_three_way, "auroc": m_auroc, "bacc": m_bacc, "macro_bacc": m_macro,
           "rag_bacc": lambda d: m_macro(d, RAG_SUBSET)}


# ------------------------------------------------------------------ resampling
def resamples(frame, reps, rng, strata=None):
    """Yield row-index arrays of cluster bootstrap resamples (groups drawn with replacement, within each stratum)."""
    codes, uniq = pd.factorize(frame["group"])
    rows = pd.Series(np.arange(len(frame))).groupby(codes).apply(np.array).to_dict()
    if strata is None:
        pools = [np.arange(len(uniq))]
    else:
        st = pd.Series(frame[strata].to_numpy()).groupby(codes).first()
        pools = [np.array(g.index) for _, g in st.groupby(st)]
    for _ in range(reps):
        pick = np.concatenate([rng.choice(pool, len(pool)) for pool in pools])
        yield np.concatenate([rows[g] for g in pick])


def ci(vals):
    return [float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))]


def p_two_sided(d, reps):
    return float(max(2 * min((d <= 0).mean(), (d >= 0).mean()), 1 / reps))


# ------------------------------------------------------------------ main
def main(argv=None):
    ap = argparse.ArgumentParser(prog="groundone bootstrap")
    ap.add_argument("--reps", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args(argv)
    rng = np.random.default_rng(a.seed)

    t1r, t3r = records("test_ragtruth"), records("test_vitaminc")
    F = {"t1": {}, "t3": {}, "t2": {}, "lat": {}}
    for label, name in T1_SYSTEMS.items():
        for t, recs in (("t1", t1r), ("t3", t3r)):
            p = RESULTS_DIR / name / t / "predictions.parquet"
            if p.exists():
                F[t][label] = frame_sentences(p, recs)
    for s, tag in (("0.5B", "05b"), ("3B", "3b")):
        F["t1"][f"B2 {s} (generated token)"] = frame_b2(RESULTS_DIR / f"b2-{tag}" / "t1" / "predictions.parquet", t1r)
    F["t1"]["Word overlap"] = overlap_frame(F["t1"]["GroundOne 0.5B"], t1r)
    F["t3"]["Word overlap"] = overlap_frame(F["t3"]["GroundOne 0.5B"], t3r)
    F["t1_k14"] = {k: v[v["id"].isin(pd.read_parquet(RESULTS_DIR / "g1-05b-b1" / "t1" / "predictions.parquet")
                                        .query("kband == '>=14'")["id"])] for k, v in F["t1"].items()}
    g2 = groups_of("test_aggrefact")
    for label, path in T2_SYSTEMS.items():
        if (path / ("aggrefact" if "legacy" in str(path) else "t2") / "predictions.parquet").exists():
            F["t2"][label] = frame_t2(path, g2)
    for s, tag in (("0.5B", "05b"), ("3B", "3b")):
        F["lat"][f"GroundOne {s}"] = frame_latency(RESULTS_DIR / f"g1-{tag}-b1" / "latency" / "predictions.parquet", t1r)
        for j, name in JUDGES.items():
            F["lat"][f"{j} {s}"] = frame_latency(RESULTS_DIR / f"{name}-{tag}" / "latency" / "predictions.parquet", t1r)

    report = {"protocol": {"reps": a.reps, "seed": a.seed, "interval": "95% percentile", "unit": "leakage group",
                           "t2": "resampled within dataset"}, "systems": {}, "pairs": []}
    # single-system intervals
    single = {"t1": ("three_way", "auroc", "bacc"), "t1_k14": ("three_way",), "t3": ("three_way", "auroc"),
              "t2": ("macro_bacc", "rag_bacc"), "lat": ("three_way",)}
    for test, metrics in single.items():
        for label, fr in F[test].items():
            ms = [m for m in metrics if not (m in ("three_way",) and "pred" in fr and (fr["pred"] == -2).all())
                  and not (m in ("auroc", "bacc") and "psup" not in fr)]
            if not ms:
                continue
            strata = "dataset" if test == "t2" else None
            vals = {m: [] for m in ms}
            for idx in resamples(fr, a.reps, rng, strata):
                d = fr.iloc[idx]
                for m in ms:
                    vals[m].append(METRICS[m](d))
            report["systems"].setdefault(test, {})[label] = {
                m: {"value": METRICS[m](fr), "ci95": ci(vals[m]), "n_rows": int(len(fr)),
                    "n_groups": int(fr["group"].nunique())} for m in ms}
            print(f"  {test:7s} {label:28s} " + "  ".join(f"{m} {METRICS[m](fr):.3f} [{ci(vals[m])[0]:.3f}, {ci(vals[m])[1]:.3f}]"
                                                         for m in ms), flush=True)
    # paired differences
    for test, metric, A, B in PAIRS:
        if A not in F[test] or B not in F[test]:
            continue
        fa, fb = F[test][A], F[test][B]
        common = set(fa["id"]) & set(fb["id"])
        fa = fa[fa["id"].isin(common)].sort_values("id").reset_index(drop=True)
        fb = fb[fb["id"].isin(common)].sort_values("id").reset_index(drop=True)
        if metric == "speedup_k14":
            fa = fa[fa["kband"] == ">=14"].drop_duplicates("rid").sort_values("rid").reset_index(drop=True)
            fb = fb[fb["kband"] == ">=14"].drop_duplicates("rid").sort_values("rid").reset_index(drop=True)
            fn = lambda da, db: float(db["sec"].median() / da["sec"].median())  # noqa: E731
            point = fn(fa, fb)
            vals = np.array([fn(fa.iloc[i], fb.iloc[i]) for i in resamples(fa, a.reps, rng)])
            entry = {"test": test, "metric": metric, "A": A, "B": B, "ratio_B_over_A": point, "ci95": ci(vals),
                     "n_answers": int(len(fa))}
            print(f"  {test:7s} {metric:11s} {B} / {A}: {point:.2f}x [{ci(vals)[0]:.2f}, {ci(vals)[1]:.2f}]", flush=True)
        else:
            f = METRICS[metric]
            strata = "dataset" if test == "t2" else None
            va, vb = f(fa), f(fb)
            d = np.array([f(fa.iloc[i]) - f(fb.iloc[i]) for i in resamples(fa, a.reps, rng, strata)])
            entry = {"test": test, "metric": metric, "A": A, "B": B, "A_value": va, "B_value": vb, "diff": va - vb,
                     "ci95": ci(d), "p": p_two_sided(d, a.reps), "n_rows": int(len(fa)),
                     "n_groups": int(fa["group"].nunique())}
            print(f"  {test:7s} {metric:11s} {A} - {B}: {va - vb:+.3f} [{ci(d)[0]:+.3f}, {ci(d)[1]:+.3f}] "
                  f"p={entry['p']:.4f} (n={len(fa)})", flush=True)
        report["pairs"].append(entry)

    out = RESULTS_DIR / "bootstrap"
    out.mkdir(parents=True, exist_ok=True)
    (out / "metrics.json").write_text(json.dumps(report, indent=2, default=float))
    (out / "summary.md").write_text(summary_md(report))
    figure(report)
    print(f"bootstrap written to {out}", flush=True)


def fmt_p(p, reps):
    return f"< {1 / reps:.4f}".rstrip("0") if p <= 1 / reps else f"{p:.3f}"


def summary_md(r):
    reps = r["protocol"]["reps"]
    lines = ["# Bootstrap intervals and paired tests", "",
             f"*Generated by `groundone bootstrap` (B = {reps}, cluster resampling by leakage group; T2 within dataset). "
             f"Do not edit by hand.*", "", "## Paired differences (A − B, same resamples, rows scored by both)", "",
             "| Test | Metric | A | B | A | B | A − B [95 % CI] | p | rows (groups) |", "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for e in r["pairs"]:
        if e["metric"] == "speedup_k14":
            continue
        lines.append(f"| {TESTS[e['test']]} | {e['metric']} | {e['A']} | {e['B']} | {e['A_value']:.3f} | {e['B_value']:.3f} | "
                     f"{e['diff']:+.3f} [{e['ci95'][0]:+.3f}, {e['ci95'][1]:+.3f}] | {fmt_p(e['p'], reps)} | "
                     f"{e['n_rows']} ({e['n_groups']}) |")
    lines += ["", "## Speed-up at K ≥ 14 (median seconds of B / median seconds of A, paired answers)", "",
              "| A | B | Speed-up [95 % CI] | answers |", "| --- | --- | --- | --- |"]
    for e in r["pairs"]:
        if e["metric"] == "speedup_k14":
            lines.append(f"| {e['A']} | {e['B']} | {e['ratio_B_over_A']:.2f}× [{e['ci95'][0]:.2f}, {e['ci95'][1]:.2f}] | {e['n_answers']} |")
    lines += ["", "## Single-system intervals", "", "| Test | System | Metric | Value [95 % CI] | rows (groups) |",
              "| --- | --- | --- | --- | --- |"]
    for test, systems in r["systems"].items():
        for label, ms in systems.items():
            for m, v in ms.items():
                lines.append(f"| {TESTS[test]} | {label} | {m} | {v['value']:.3f} [{v['ci95'][0]:.3f}, {v['ci95'][1]:.3f}] | "
                             f"{v['n_rows']} ({v['n_groups']}) |")
    return "\n".join(lines) + "\n"


def figure(r):
    from ..figures.style import INK2, NEUTRAL, SERIES, Group, plt
    rows = [e for e in r["pairs"] if e["metric"] != "speedup_k14" and e["test"] != "lat"]
    fig, ax = plt.subplots(figsize=(7.2, 0.28 * len(rows) + 1.0))
    for k, e in enumerate(rows[::-1]):
        lo, hi = e["ci95"]
        col = SERIES[0] if lo > 0 else SERIES[1] if hi < 0 else NEUTRAL
        ax.plot([lo, hi], [k, k], color=col, lw=2, solid_capstyle="round")
        ax.plot([e["diff"]], [k], "o", color=col, ms=5)
    ax.axvline(0, color=INK2, lw=1)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([f"{TESTS[e['test']].split(' ')[0] + (' K≥14' if e['test'] == 't1_k14' else '')} · {e['metric']} · "
                        f"{e['A']} − {e['B']}" for e in rows[::-1]], fontsize=7)
    ax.set_xlabel("difference A − B with 95 % bootstrap interval (blue: A better, orange: B better, grey: not significant)")
    ax.grid(axis="y", visible=False)
    g = Group("bootstrap")
    g.save(fig, "paired_differences", "Paired differences between systems on the frozen test sets with 95 % cluster-"
           "bootstrap intervals (resampling by source document / page; T2 within dataset). An interval that crosses zero "
           "means the difference is not significant at the 5 % level.", "results/bootstrap/metrics.json")
    g.write_index("Bootstrap intervals and paired tests")


if __name__ == "__main__":
    main()
