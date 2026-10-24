"""Summary and figures of the demo case study (D30): injected errors through the verify-and-revise loop.

Reads outputs/demo/casestudy/<run>/rows.jsonl (written by `g1studio casestudy`) and writes
outputs/demo/casestudy/summary.json (shown in the app's Measurements view) and PNG figures with captions in
outputs/figures/demo/. Wording follows the honesty rule (§8): "accepted by GroundOne", not "correct".

Usage (from Project/): GroundOne/.venv/bin/python experiments/demo/scripts/casestudy_report.py casestudy-g1-3b-b1 [...]
"""
import json
import statistics as st
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

P = Path(__file__).resolve().parents[3]
CS = P / "outputs/demo/casestudy"
FIG = P / "outputs/figures/demo"
KINDS = ["number", "name", "date", "fabricated"]
BLUE, GREY, PURPLE = "#1f5fbf", "#8c8c9e", "#9e5cb3"


def rate(xs):
    xs = [x for x in xs if x is not None]
    return round(sum(map(bool, xs)) / len(xs), 4) if xs else None


def med(xs):
    xs = [x for x in xs if x is not None]
    return round(st.median(xs), 3) if xs else None


def words(s):
    import re
    return {w for w in re.findall(r"[a-z0-9]+", s.lower()) if len(w) > 2}


def jaccard(a, b):
    x, y = words(a), words(b)
    return len(x & y) / len(x | y) if x and y else 0.0


def repair_mode(r, inj):
    """For a removed error: 'restored' (original value back), 'rewritten' (a sentence close to the injected one remains),
    'deleted' (no such sentence: information lost, as CoVe gains precision partly by deletion)."""
    import re
    sents = re.split(r"(?<=[.!?])\s+", r["final_text"])
    if inj["kind"] != "fabricated" and inj["right"] and inj["right"] in r["final_text"]:
        return "restored"
    if inj["kind"] == "fabricated":
        return "deleted"
    return "rewritten" if any(jaccard(x, inj["injected"]) >= 0.4 for x in sents) else "deleted"


def summarise(rows, meta, injected=None):
    out = {"answers": len(rows), "verifier": meta.get("verifier"), "generator": meta.get("generator"),
           "input": meta.get("input", "injected.jsonl"), "revision": meta.get("revision", "uniform")}
    present = [r["error_present_by_round"] for r in rows]
    final = [p[-1] for p in present]
    out["detection"] = {
        "groundone_flags_injected_sentence": rate(r["g1_flags_injected"] for r in rows),
        "judge_flags_injected_sentence": rate(None if r["judge_label_injected"] is None else r["judge_label_injected"] != "supported" for r in rows),
        "judge_output_fully_parsed": rate(r["judge_parsed"] for r in rows),
        "groundone_false_alarm_share_other_sentences": round(sum(r["g1_false_alarms_draft0"] for r in rows) / max(sum(r["other_scored_sentences"] for r in rows), 1), 4),
    }
    for k in KINDS:
        sub = [r for r in rows if r["kind"] == k]
        if sub:
            out["detection"][f"groundone_flags_{k}"] = rate(r["g1_flags_injected"] for r in sub)
    out["error_survival"] = {
        "without_loop": 1.0,
        "after_round_1": rate(p[1] if len(p) > 1 else p[-1] for p in present),
        "after_round_2_final": rate(final),
        "survival_when_flagged": rate(r["error_present_by_round"][-1] for r in rows if r["g1_flags_injected"]),
        "survival_when_missed": rate(r["error_present_by_round"][-1] for r in rows if r["g1_flags_injected"] is False),
    }
    for k in KINDS:
        sub = [r for r in rows if r["kind"] == k]
        if sub:
            out["error_survival"][f"final_{k}"] = rate(r["error_present_by_round"][-1] for r in sub)
    swaps = [r for r in rows if r["kind"] != "fabricated" and r["g1_flags_injected"]]
    out["repairs"] = {
        "swaps_flagged": len(swaps),
        "swaps_original_value_restored": rate(r["restored_right"] for r in swaps),
        "other_sentences_kept_verbatim": round(sum(r["other_sentences_kept_verbatim"] for r in rows) / max(sum(r["other_scored_sentences"] for r in rows), 1), 4),
        "final_status_accepted_by_groundone": rate(r["status"] == "accepted" for r in rows),
        "mean_rewrite_rounds": round(st.mean(r["rounds"] for r in rows), 3),
    }
    survivors = [r for r in rows if r["error_present_by_round"][-1]]
    out["repairs"]["survivors_still_flagged"] = sum(r["status"] != "accepted" for r in survivors)
    out["repairs"]["survivors_accepted_by_groundone"] = sum(r["status"] == "accepted" for r in survivors)
    if injected:
        removed = [r for r in rows if not r["error_present_by_round"][-1]]
        modes = [repair_mode(r, injected[r["id"]]) for r in removed]
        for m in ("restored", "rewritten", "deleted"):
            out["repairs"][f"removed_errors_{m}"] = modes.count(m)
    ver0 = [r["verification_s"][0] for r in rows]
    judge = [r["judge_s"] for r in rows]
    gen_rewrites = [g for r in rows for g in r["generation_s"][1:]]
    ver_all = sum(sum(r["verification_s"]) for r in rows)
    gen_all = sum(sum(r["generation_s"]) for r in rows)
    out["timing_seconds"] = {
        "groundone_pass_median": med(ver0),
        "judge_median": med(judge),
        "judge_over_groundone_median_ratio": med([j / v for j, v in zip(judge, ver0) if j and v]),
        "rewrite_generation_median": med(gen_rewrites),
        "verification_share_of_loop_time": round(ver_all / max(ver_all + gen_all, 1e-9), 4),
        "judge_generated_tokens_median": med([r["judge_generated_tokens"] for r in rows]),
        "verifier_input_tokens_median": med([r["verifier_input_tokens"] for r in rows]),
    }
    out["memory_gb"] = {"mlx_peak_during_loop": max((r["mlx_peak_gb"] or 0) for r in rows),
                        **{k: v for k, v in (meta.get("memory_after_load") or {}).items()}}
    return out


def figures(rows, run, tag, injected=None):
    FIG.mkdir(parents=True, exist_ok=True)
    if injected:
        # 3. what happened to each injected error, by kind
        cats = [("restored", "original value restored", "#2e8b57"), ("rewritten", "sentence rewritten", "#7fbf8f"),
                ("deleted", "sentence deleted", "#c9c9d3"), ("flagged", "still present, still flagged", "#d98b0d"),
                ("missed", "still present, accepted by GroundOne", "#c0392b")]
        fig, ax = plt.subplots(figsize=(7.2, 3.0))
        for y, k in enumerate(KINDS):
            sub = [r for r in rows if r["kind"] == k]
            counts = {c: 0 for c, _, _ in cats}
            for r in sub:
                if r["error_present_by_round"][-1]:
                    counts["missed" if r["status"] == "accepted" else "flagged"] += 1
                else:
                    counts[repair_mode(r, injected[r["id"]])] += 1
            left = 0
            for c, label, color in cats:
                ax.barh(y, counts[c], left=left, color=color, edgecolor="white", label=label if y == 0 else None)
                left += counts[c]
        ax.set_yticks(range(len(KINDS)), KINDS)
        ax.invert_yaxis()
        ax.set_xlabel("injected errors (25 per type)")
        ax.legend(frameon=False, fontsize=7, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.28))
        ax.spines[["top", "right"]].set_visible(False)
        fig.tight_layout()
        fig.savefig(FIG / f"casestudy_outcomes_{tag}.png", dpi=200)
        (FIG / f"casestudy_outcomes_{tag}.txt").write_text(
            f"Outcome of each injected error after the loop ({run}). For swapped numbers, names and dates, removal mostly "
            "happens by deleting the sentence (the correct information is lost too) rather than by restoring the value from "
            "the document; for fabricated sentences deletion is the right repair. Errors still present are either still "
            "flagged (shown highlighted under the policy) or accepted by GroundOne (a miss).")
        plt.close(fig)
    # 1. survival of the injected error by round and kind
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    for k, c in zip(KINDS, [BLUE, "#2e8b57", "#d98b0d", "#c0392b"]):
        sub = [r for r in rows if r["kind"] == k]
        if not sub:
            continue
        ys = [rate((r["error_present_by_round"][min(i, len(r["error_present_by_round"]) - 1)]) for r in sub) for i in range(3)]
        ax.plot([0, 1, 2], [y * 100 for y in ys], marker="o", lw=2, color=c, label=f"{k} (n={len(sub)})")
    ax.set_xticks([0, 1, 2], ["no loop", "after 1 rewrite", "after 2 rewrites"])
    ax.set_ylabel("answers still containing\nthe injected error (%)")
    ax.set_ylim(0, 105)
    ax.grid(axis="y", alpha=0.3)
    ax.legend(frameon=False, fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG / f"casestudy_survival_{tag}.png", dpi=200)
    (FIG / f"casestudy_survival_{tag}.txt").write_text(
        f"Injected-error case study ({run}): share of answers that still contain the injected error before the loop, after "
        "one and after two rewrite rounds, by error type. The error position and wrong string are the ground truth "
        "(independent of GroundOne); a rewrite counts as removing the error when the wrong string (or a sentence close to the "
        "fabricated one) is no longer in the answer.")
    plt.close(fig)
    # 2. GroundOne pass vs generative judge, per answer
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    v = sorted(r["verification_s"][0] for r in rows)
    j = sorted(r["judge_s"] for r in rows if r["judge_s"])
    ax.boxplot([v, j], orientation="horizontal", widths=0.5, patch_artist=True,
               boxprops=dict(facecolor="#e8f1ff"), medianprops=dict(color=BLUE, lw=2))
    ax.set_yticks([1, 2], ["GroundOne\n(one forward pass)", "generative judge\n(same base, no adapter)"])
    ax.set_xlabel("seconds per answer")
    ax.grid(axis="x", alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG / f"casestudy_judge_time_{tag}.png", dpi=200)
    (FIG / f"casestudy_judge_time_{tag}.txt").write_text(
        f"Inside the demo app ({run}, Swift + MLX, M4 16 GB): time to verify each injected answer with GroundOne (one "
        "forward pass, verdicts at the markers) and with the generative judge of the comparison mode (Qwen2.5-3B 8-bit base "
        "without the adapter, B0a terse prompt, greedy). Same answers, same process, calls serialised on the GPU.")
    plt.close(fig)


def main():
    runs = sys.argv[1:] or ["casestudy-g1-3b-b1"]
    summary = {}
    for run in runs:
        d = CS / run
        rows = [json.loads(l) for l in open(d / "rows.jsonl")]
        meta = json.loads((d / "meta.json").read_text()) if (d / "meta.json").exists() else {}
        injected = {json.loads(l)["id"]: json.loads(l) for l in open(CS / meta.get("input", "injected.jsonl"))}
        summary[run] = summarise(rows, meta, injected)
        figures(rows, run, run.replace("casestudy-", ""), injected)
    for f in sorted(CS.glob("bestofn-*.jsonl")):
        rows = [json.loads(l) for l in open(f)]
        if rows:
            summary[f.stem] = {"equal_compute": {
                "documents": len(rows),
                "loop_accepted_by_groundone": rate(r["loop_accepted"] for r in rows),
                "loop_first_draft_accepted": rate(r["loop_first_draft_accepted"] for r in rows),
                "loop_seconds_median": med([r["loop_seconds"] for r in rows]),
                "loop_generated_tokens_median": med([r["loop_generated_tokens"] for r in rows]),
                "best_of_n_accepted_by_groundone": rate(r["bon_accepted"] for r in rows),
                "best_of_n_samples_used_mean": round(st.mean(r["bon_samples_used"] for r in rows), 3),
                "best_of_n_seconds_median": med([r["bon_seconds"] for r in rows]),
                "best_of_n_generated_tokens_median": med([r["bon_generated_tokens"] for r in rows]),
            }}
    flat = {f"{run} · {k}": v for run, s in summary.items() for k, v in s.items() if isinstance(v, dict)}
    (CS / "summary.json").write_text(json.dumps(flat, indent=2))
    (CS / "summary_full.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
