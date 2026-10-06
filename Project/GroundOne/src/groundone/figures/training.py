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
    if any("dev_bacc" in e for e in ev):  # fixed dev with all questions (data v2, D22)
        evb = [e for e in ev if "dev_bacc" in e]
        steps = [e["step"] for e in evb]
        fig, axes = plt.subplots(1, 2, figsize=(10, 3.4), sharey=True)
        for ax, part, names in [(axes[0], 1, list(Q_COLORS)), (axes[1], 0, ["anli_pair", "anli_multi", "ragtruth", "minicheck"])]:
            for k, nm in enumerate(names):
                ys = []
                for e in evb:
                    v = [x for g, x in e["dev_bacc"].items() if g.split("|")[part] == nm]
                    ys.append(sum(v) / len(v) if v else None)
                if any(y is not None for y in ys):
                    ax.plot(steps, ys, marker="o", color=Q_COLORS.get(nm, SERIES[k]), label=nm)
            ax.plot(steps, [e["dev_score"] for e in evb], color=INK2, ls="--", label="dev score")
            ax.axhline(0.5, color=NEUTRAL, lw=1, ls=":")
            ax.set_xlabel("optimiser step")
            ax.legend(fontsize=7)
        axes[0].set_title("by question (mean over blocks)", fontsize=9)
        axes[1].set_title("by block (mean over questions)", fontsize=9)
        axes[0].set_ylabel("dev balanced accuracy")
        g.save(fig, "dev_bacc_by_question_and_block", f"Balanced accuracy on the fixed dev set (every item with all four "
               f"questions) during training of run {run}; dev score = mean over (block, question), used to pick best/. "
               f"Chance is 0.5 for binary questions and 0.33 for the three-way question.", f"models/{run}/train_log.jsonl")
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
