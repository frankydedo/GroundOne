"""Training figures: one run (loss curves, dev accuracy per question, LR) and sweeps (runs compared)."""
import json

from ..config import MODELS_DIR
from .style import INK2, NEUTRAL, SERIES, Group, plt

Q_COLORS = {"sup": SERIES[0], "three": SERIES[1], "strict": SERIES[2], "lenient": SERIES[3]}


def read_log(run):
    return [json.loads(l) for l in open(MODELS_DIR / run / "train_log.jsonl")]


def run_figures(run):
    log = read_log(run)
    g = Group(f"training-{run}")
    tr = [e for e in log if e["event"] == "train"]
    ev = [e for e in log if e["event"] == "eval"]
    if not tr and not ev:
        print(f"  no train/eval events in {run}")
        return
    fig, ax = plt.subplots(figsize=(7, 3.2))
    if tr:
        ax.plot([e["step"] for e in tr], [e["loss"] for e in tr], color=SERIES[0], lw=1.2, alpha=0.8, label="training loss (25-step mean)")
    if ev:
        ax.plot([e["step"] for e in ev], [e["dev_loss"] for e in ev], color=SERIES[1], marker="o", label="dev loss")
    ax.set_xlabel("optimiser step")
    ax.set_ylabel("cross-entropy over answer letters")
    ax.legend()
    g.save(fig, "loss", f"Training and dev loss of run {run} (loss restricted to the allowed answer letters).", f"models/{run}/train_log.jsonl")
    if ev:
        fig, ax = plt.subplots(figsize=(7, 3.2))
        for q, col in Q_COLORS.items():
            pts = [(e["step"], e["dev_acc_by_q"][q]) for e in ev if q in e.get("dev_acc_by_q", {})]
            if pts:
                ax.plot(*zip(*pts), marker="o", color=col, label=q)
        ax.plot([e["step"] for e in ev], [e["dev_acc"] for e in ev], color=INK2, ls="--", label="all")
        ax.set_xlabel("optimiser step")
        ax.set_ylabel("dev accuracy")
        ax.set_ylim(0, 1)
        ax.legend(ncol=5, loc="lower right")
        g.save(fig, "dev_accuracy_by_question", f"Dev accuracy per question type during training (run {run}; fixed dev subset).",
               f"models/{run}/train_log.jsonl")
    if tr:
        fig, ax = plt.subplots(figsize=(7, 2.6))
        ax.plot([e["step"] for e in tr], [e["lr"] for e in tr], color=NEUTRAL)
        ax.set_xlabel("optimiser step")
        ax.set_ylabel("learning rate")
        g.save(fig, "learning_rate", f"Learning-rate schedule (linear warm-up, cosine decay) of run {run}.", f"models/{run}/train_log.jsonl")
    g.write_index(f"Training figures: {run}")


def sweep_figures(prefix="sweep-"):
    runs = sorted(d.name for d in MODELS_DIR.glob(f"{prefix}*") if (d / "train_log.jsonl").exists())
    if not runs:
        return
    g = Group("sweep")
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.2))
    base = None
    for i, r in enumerate(runs):
        log = read_log(r)
        ev = [e for e in log if e["event"] == "eval"]
        if ev and ev[0]["step"] == 0:
            base = ev[0]
        ev = [e for e in ev if e["step"] > 0]
        cfg = [e for e in log if e["event"] == "start"][0]
        label = r.replace(prefix, "")
        steps = [e["step"] / cfg["steps"] for e in ev]  # fraction of the (compressed) schedule, comparable across runs
        axes[0].plot([0] + steps, [base["dev_loss"] if base else None] + [e["dev_loss"] for e in ev], marker="o", color=SERIES[i], label=label)
        axes[1].plot([0] + steps, [base["dev_acc"] if base else None] + [e["dev_acc"] for e in ev], marker="o", color=SERIES[i], label=label)
    for ax, ylab in zip(axes, ("dev loss", "dev accuracy")):
        ax.set_xlabel("fraction of the short schedule")
        ax.set_ylabel(ylab)
    axes[0].legend(fontsize=7)
    g.save(fig, "sweep_dev_curves", "Short hyper-parameter sweep on the 0.5B (same ~2,200 examples in the same order per "
           "run, compressed schedule, fixed dev subset of 300): dev loss and accuracy. Step 0 is the untrained model.",
           f"models/{prefix}*/train_log.jsonl")
    g.write_index(f"Sweep figures ({prefix}*)")
