"""Thesis figures. `groundone figures all|phase0|sweep|training RUN|results|eda|dataset|benchmarks` writes PNGs + index.md to Project/outputs/figures/.

Rule for the project: every phase must leave figures behind (plots are thesis material). Add a function here whenever a
new kind of result appears, and run `groundone figures all` after each phase.
"""
import shutil
import sys

from ..config import EXPERIMENTS, FIGURES_DIR, MODELS_DIR


def eda_copy():
    """The EDA has its own scripts (Project/EDA); mirror its figures so figures/ is the one place to look."""
    src = EXPERIMENTS / "eda" / "report" / "figures"
    dst = FIGURES_DIR / "eda"
    if src.exists():
        dst.mkdir(parents=True, exist_ok=True)
        for p in src.glob("*.png"):
            shutil.copy2(p, dst / p.name)
        print(f"  copied {len(list(src.glob('*.png')))} EDA figures to outputs/figures/eda (captions: experiments/eda/report/eda_report.md)")


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    what = argv[0] if argv else "all"
    from . import phase0, results, training
    if what in ("phase0", "all"):
        phase0.main()
    if what in ("sweep", "all"):
        training.sweep_figures()
    if what == "training":
        training.run_figures(argv[1])
    if what == "diagnostics":
        from . import diagnostics
        diagnostics.main(argv[1])
    if what == "all":
        for d in sorted(MODELS_DIR.glob("*/train_log.jsonl")):
            if not d.parent.name.startswith("sweep-"):
                training.run_figures(d.parent.name)
    if what == "results":  # legacy: systems evaluated on the earlier test files
        results.main()
    if what in ("eda", "all"):
        eda_copy()
    if what in ("dataset", "all"):
        from . import dataset
        dataset.main()
    if what in ("benchmarks", "all"):
        from . import benchmarks
        benchmarks.main()
