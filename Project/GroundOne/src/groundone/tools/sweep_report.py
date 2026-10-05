"""Summarise short training runs (hyper-parameter sweeps) from their train_log.jsonl files.

Usage: python -m groundone.tools.sweep_report sweep-   (prefix of run names under models/)
Writes models/<prefix>summary.md and prints it: per run the config deltas, training loss, dev loss/accuracy by step,
and dev accuracy per question type at the end.
"""
import json
import sys

import yaml

from ..config import MODELS_DIR


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    prefix = argv[0] if argv else "sweep-"
    runs = sorted(d for d in MODELS_DIR.glob(f"{prefix}*") if (d / "train_log.jsonl").exists())
    if not runs:
        sys.exit(f"no runs with prefix {prefix!r} in {MODELS_DIR}")
    base_eval = None
    rows = []
    for d in runs:
        log = [json.loads(l) for l in open(d / "train_log.jsonl")]
        cfg = yaml.safe_load((d / "config.yaml").read_text())
        evals = [e for e in log if e["event"] == "eval"]
        if evals and evals[0]["step"] == 0:
            base_eval = evals[0]
        train = [e for e in log if e["event"] == "train"]
        end = next((e for e in log if e["event"] == "end"), None)
        rows.append({"run": d.name, "lr": cfg["lr"], "accum": cfg["accum"], "rank": cfg["rank"], "steps": cfg["max_steps"],
                     "evals": [(e["step"], round(e["dev_loss"], 4), round(e["dev_acc"], 3)) for e in evals if e["step"] > 0],
                     "train_loss_last": train[-1]["loss"] if train else None,
                     "end": end, "minutes": round(end["wall_hours"] * 60, 1) if end else None})
    lines = [f"# Sweep summary ({prefix}*)", ""]
    if base_eval:
        lines += [f"Untrained model on the same dev subset: loss {base_eval['dev_loss']:.4f}, accuracy {base_eval['dev_acc']:.3f} "
                  f"(by question: {base_eval['dev_acc_by_q']})", ""]
    lines += ["| run | lr | accum | steps | dev loss / acc during training | final dev loss | final dev acc | acc by question | minutes |",
              "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in sorted(rows, key=lambda r: r["end"]["dev_loss"] if r["end"] else 9):
        e = r["end"] or {}
        lines.append(f"| {r['run']} | {r['lr']:g} | {r['accum']} | {r['steps']} | "
                     f"{'; '.join(f's{s}: {l} / {a}' for s, l, a in r['evals'])} | {e.get('dev_loss', float('nan')):.4f} | "
                     f"{e.get('dev_acc', float('nan')):.3f} | {e.get('dev_acc_by_q')} | {r['minutes']} |")
    text = "\n".join(lines) + "\n"
    (MODELS_DIR / f"{prefix}summary.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
