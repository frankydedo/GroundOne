"""Paths, model registry and defaults."""
import os
from pathlib import Path

# Software lives in Project/GroundOne; experiment data and outputs live in the workspace Project/ (one level up).
PACKAGE_ROOT = Path(__file__).resolve().parents[2]     # .../Project/GroundOne
PROJECT = Path(os.environ.get("GROUNDONE_WORKSPACE", PACKAGE_ROOT.parent))  # .../Project (workspace)
CONFIGS_DIR = PACKAGE_ROOT / "configs"
DATA_RAW = PROJECT / "data" / "raw"
DATA_PROCESSED = PROJECT / "data" / "processed"
OUTPUTS = PROJECT / "outputs"                          # everything the groundone commands generate
MODELS_DIR = OUTPUTS / "models"                        # trained adapters (gitignored)
RESULTS_DIR = OUTPUTS / "results"                      # metrics.json tracked, predictions gitignored
FIGURES_DIR = OUTPUTS / "figures"                      # thesis figures (PNG + captions)
LOGS_DIR = OUTPUTS / "logs"                            # memory-guard logs and job output
EXPERIMENTS = PROJECT / "experiments"                  # one-off studies: feasibility (Phase 0), eda

# Base checkpoints (MLX 8-bit conversions). Sizes are the thesis' two model sizes (D2, D17).
BASE_MODELS = {
    "0.5b": "lmstudio-community/Qwen2.5-0.5B-Instruct-MLX-8bit",
    "3b": "lmstudio-community/Qwen2.5-3B-Instruct-MLX-8bit",
}
DEFAULT_SIZE = "0.5b"
DEFAULT_PORT = 8019
DEFAULT_HOST = "127.0.0.1"
API_KEY_ENV = "GROUNDONE_API_KEY"

MAX_PROMPT_TOKENS = int(os.environ.get("GROUNDONE_MAX_TOKENS", 4096))  # per question (prefix + suffix)
MAX_BATCH = int(os.environ.get("GROUNDONE_MAX_BATCH", 32))             # suffixes per forward pass
MLX_MEMORY_LIMIT_GB = float(os.environ.get("GROUNDONE_MLX_MEM_GB", 8))


def resolve_model(size=None, adapter=None, base=None):
    """Return (base_repo, adapter_dir or None, display name).

    `adapter` may be a directory or the name of a run under models/. Its groundone.json (written by
    `groundone train`) records the base model, so `size` is optional when an adapter is given. `base` overrides the
    base checkpoint (e.g. the bf16 weights, to measure the effect of the 8-bit base the adapter was trained on).
    """
    import json
    adir = None
    if adapter:
        adir = Path(adapter)
        if not adir.exists():
            adir = MODELS_DIR / adapter
        if not (adir / "adapters.safetensors").exists():
            raise FileNotFoundError(f"No adapters.safetensors in {adir}")
        meta = json.loads((adir / "groundone.json").read_text()) if (adir / "groundone.json").exists() else {}
        size = size or meta.get("size")
    size = size or DEFAULT_SIZE
    if size not in BASE_MODELS:
        raise ValueError(f"Unknown size {size!r}; choose from {list(BASE_MODELS)}")
    name = f"groundone-{size}" + (f"-{adir.name}" if adir else "-base")
    if base:
        name += f"-on-{base.split('/')[-1]}"
    return base or BASE_MODELS[size], (str(adir) if adir else None), name
