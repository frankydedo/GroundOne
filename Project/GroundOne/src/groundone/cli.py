"""`groundone` command-line interface.

  groundone serve      [--size 0.5b|3b] [--adapter RUN] [--calibration FILE] [--host] [--port]
  groundone verify     FILE.json [--size] [--adapter]            one request, no server (same JSON as POST /v1/verify)
  groundone systemone  FILE.json [--size] [--adapter]            one Jev-compatible request, no server
  groundone schema     [--response] [--compat]                   JSON Schema of the API
  groundone models                                                base models and trained runs available locally
  groundone data       build | check | shortcut | freeze | rows  dataset (docs/dataset_plan.md), leakage, shortcut, freeze tests
  groundone train      --config train_0.5b.yaml [...]             LoRA fine-tuning (design b by default)
  groundone calibrate-b --adapter RUN/best --name NAME            temperature + bias on dev (design b)
  groundone test       --suite t1|t2|t3 --name NAME [--adapter RUN]   frozen GroundOne test sets (three-way)
  groundone matrix     [--print]                                  results matrix (all systems x test sets) -> docs/tracker.md
  groundone guard      QUEUE.txt                                  run long jobs one at a time under the memory guard
  groundone figures    all | dataset | benchmarks | training RUN | eda | phase0   thesis figures -> Project/figures/
  groundone baselines  frozen | judges [...]                      baselines on the frozen tests; generative judges + latency
  legacy (earlier datasets, kept for reference): groundone eval | calibrate, groundone baselines encoder | rizzo
"""
import argparse
import json
import sys
from pathlib import Path


def _model_args(p):
    p.add_argument("--size", choices=["0.5b", "3b"], help="base model size (default 0.5b, or the adapter's size)")
    p.add_argument("--adapter", help="trained run under models/ or a directory with adapters.safetensors")
    p.add_argument("--calibration", help="calibration.json (default: <adapter>/calibration.json if present)")


def _engine(a):
    from .config import resolve_model
    from .engine import Engine
    cal = a.calibration
    if cal is None and a.adapter:
        cand = Path(resolve_model(a.size, a.adapter)[1]) / "calibration.json"
        cal = str(cand) if cand.exists() else None
    return Engine.load(a.size, a.adapter, cal)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    # sub-commands with their own parsers
    passthrough = {"figures": ("figures", "main"), "train": ("training.train", "main"), "eval": ("eval.evaluate", "main"), "test": ("eval.tests", "main"), "matrix": ("tools.matrix", "main"),
                   "calibrate": ("eval.evaluate", "calibrate"), "calibrate-b": ("eval.calibrate_b", "main"), "guard": ("tools.watchdog", "main")}
    if argv and argv[0] in passthrough:
        mod, fn = passthrough[argv[0]]
        module = __import__(f"groundone.{mod}", fromlist=[fn])
        return getattr(module, fn)(argv[1:])
    if argv and argv[0] == "baselines":
        sub = argv[1] if len(argv) > 1 else ""
        mods = {"rizzo": "rizzo", "encoder": "encoders", "frozen": "frozen", "judges": "judges"}
        if sub not in mods:
            sys.exit("usage: groundone baselines rizzo|encoder|frozen|judges [...]")
        return __import__(f"groundone.baselines.{mods[sub]}", fromlist=["main"]).main(argv[2:])
    if argv and argv[0] == "data":
        sub = argv[1] if len(argv) > 1 else ""
        mods = {"rows": ("rows", "main"), "build": ("build", "main"), "freeze": ("build", "freeze"), "check": ("leakage", "main"), "shortcut": ("shortcut", "main")}
        if sub not in mods:
            sys.exit("usage: groundone data build|check|shortcut|freeze|rows")
        mod, fn = mods[sub]
        return getattr(__import__(f"groundone.data.{mod}", fromlist=[fn]), fn)(argv[2:])

    ap = argparse.ArgumentParser(prog="groundone", description="GroundOne: local System One groundedness verifier",
                                 epilog="Also: data build|check|shortcut, train, calibrate, eval, guard (see --help of each)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("serve", help="start the HTTP API")
    _model_args(s)
    s.add_argument("--host", default=None)
    s.add_argument("--port", type=int, default=None)
    v = sub.add_parser("verify", help="verify one request from a JSON file (no server)")
    _model_args(v)
    v.add_argument("file", type=Path)
    c = sub.add_parser("systemone", help="answer one Jev-compatible request from a JSON file (no server)")
    _model_args(c)
    c.add_argument("file", type=Path)
    sc = sub.add_parser("schema", help="print the JSON Schema of the API")
    sc.add_argument("--response", action="store_true")
    sc.add_argument("--compat", action="store_true", help="the /v1/systemone request schema")
    sub.add_parser("models", help="list base models and trained runs")
    a = ap.parse_args(argv)

    if a.cmd == "serve":
        import uvicorn
        from .api import create_app
        from .config import DEFAULT_HOST, DEFAULT_PORT
        engine = _engine(a)
        print(f"GroundOne {engine.name} ready; fingerprint {engine.backend.metadata['fingerprint']}; "
              f"calibrated={engine.calibration is not None}", flush=True)
        uvicorn.run(create_app(engine), host=a.host or DEFAULT_HOST, port=a.port or DEFAULT_PORT)
    elif a.cmd == "verify":
        from .schema import VerifyRequest
        req = VerifyRequest.model_validate_json(a.file.read_text())
        print(json.dumps(_engine(a).verify(req), indent=2))
    elif a.cmd == "systemone":
        from .compat import SystemOneRequest
        req = SystemOneRequest.model_validate_json(a.file.read_text())
        print(json.dumps(_engine(a).systemone(req), indent=2))
    elif a.cmd == "schema":
        if a.compat:
            from .compat import SystemOneRequest as M
        elif a.response:
            from .schema import VerifyResponse as M
        else:
            from .schema import VerifyRequest as M
        print(json.dumps(M.model_json_schema(), indent=2))
    elif a.cmd == "models":
        from .config import BASE_MODELS, MODELS_DIR
        print("Base models:")
        for k, v in BASE_MODELS.items():
            print(f"  {k:5s} {v}")
        print(f"Trained runs ({MODELS_DIR}):")
        for d in sorted(MODELS_DIR.glob("*/groundone.json")) if MODELS_DIR.exists() else []:
            m = json.loads(d.read_text())
            print(f"  {d.parent.name:24s} size={m.get('size')} step={m.get('last_step')} dev_acc={m.get('dev_acc')} "
                  f"calibrated={(d.parent / 'calibration.json').exists()}")


if __name__ == "__main__":
    main()
