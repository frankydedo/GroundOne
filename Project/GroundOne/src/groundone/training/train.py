"""LoRA fine-tuning of GroundOne (plan §6, D5).

- Loss: cross-entropy over the *allowed answer letters only* (A/B, or A/B/C for the three-way question), read at the
  last prompt token. The prompt is never supervised. Prompts come from groundone.prompts, as at inference.
- LoRA on all linear layers of all blocks, gradient checkpointing, length-bucketed batches under a token budget,
  gradient accumulation, AdamW with linear warm-up and cosine decay, one epoch by default.
- Every `--eval-every` steps: loss and accuracy on a fixed dev subset; the best checkpoint (lowest dev loss) is kept.
- Output (MLX adapter format, loadable by `groundone serve --adapter <dir>`):
    models/<run>/adapters.safetensors, adapter_config.json, groundone.json, train_log.jsonl, best/ (same files)
Hyper-parameters come from a YAML file (GroundOne/configs/*.yaml); command-line flags override it. The resolved
configuration is saved as models/<run>/config.yaml, so every run can be reproduced exactly.
Usage: groundone train --config configs/train_0.5b.yaml [--run NAME] [--max-hours 6.5]
"""
import argparse
import json
import math
import random
import shutil
import time
from pathlib import Path

from ..config import BASE_MODELS, CONFIGS_DIR, DATA_PROCESSED, MODELS_DIR
from ..prompts import PROMPT_VERSION, letters, render

LETTERS3 = ("A", "B", "C")


def load_jsonl(path):
    return [json.loads(l) for l in open(path)]


def make_batches(rows, token_budget, max_rows, seed):
    """Shuffle, sort within windows of 512 by length, pack under the token budget (rows * longest <= budget)."""
    rng = random.Random(seed)
    idx = list(range(len(rows)))
    rng.shuffle(idx)
    batches = []
    for w in range(0, len(idx), 512):
        win = sorted(idx[w:w + 512], key=lambda i: rows[i]["_len"])
        cur = []
        for i in win:
            longest = max([rows[j]["_len"] for j in cur] + [rows[i]["_len"]])
            if cur and (longest * (len(cur) + 1) > token_budget or len(cur) >= max_rows):
                batches.append(cur)
                cur = []
            cur.append(i)
        if cur:
            batches.append(cur)
    rng.shuffle(batches)
    return batches


def main(argv=None):
    ap = argparse.ArgumentParser(prog="groundone train")
    ap.add_argument("--config", help="YAML file with hyper-parameters (keys = option names with underscores)")
    ap.add_argument("--size", choices=list(BASE_MODELS))
    ap.add_argument("--data", default="v1", help="dataset version under data/processed/")
    ap.add_argument("--train", default="train_05b", help="training file (without .jsonl)")
    ap.add_argument("--run", help="run name; output in models/<run>/")
    ap.add_argument("--rank", type=int, default=16)
    ap.add_argument("--scale", type=float, default=2.0)
    ap.add_argument("--dropout", type=float, default=0.0)
    ap.add_argument("--lr", type=float, default=5e-5)
    ap.add_argument("--warmup", type=float, default=0.03)
    ap.add_argument("--epochs", type=float, default=1.0)
    ap.add_argument("--token-budget", type=int, default=4096, help="max padded tokens per micro-batch")
    ap.add_argument("--max-rows", type=int, default=16)
    ap.add_argument("--accum", type=int, default=2, help="micro-batches per optimiser step")
    ap.add_argument("--eval-every", type=int, default=250, help="optimiser steps between dev evaluations")
    ap.add_argument("--dev-size", type=int, default=600)
    ap.add_argument("--max-hours", type=float, default=0, help="stop cleanly after this wall time (0 = no limit)")
    ap.add_argument("--max-steps", type=int, default=0,
                    help="stop after N optimiser steps; the LR schedule (warm-up + cosine) is compressed to N steps")
    ap.add_argument("--eval-initial", type=int, default=1, help="1 = evaluate the untrained model at step 0")
    ap.add_argument("--seed", type=int, default=1234)
    ap.add_argument("--mem-gb", type=float, default=9.0)
    a = ap.parse_args(argv)
    if a.config:
        import yaml
        cfg_path = Path(a.config)
        if not cfg_path.exists():
            cfg_path = CONFIGS_DIR / a.config
        cfg = yaml.safe_load(cfg_path.read_text()) or {}
        unknown = set(cfg) - set(vars(a))
        if unknown:
            raise SystemExit(f"Unknown keys in {cfg_path}: {sorted(unknown)}")
        ap.set_defaults(**cfg)
        a = ap.parse_args(argv)  # command-line flags still override the YAML
    if not a.size or not a.run:
        raise SystemExit("size and run are required (in the YAML or as --size / --run)")

    import mlx.core as mx
    import mlx.nn as nn
    import mlx.optimizers as optim
    from mlx.utils import tree_flatten
    from mlx_lm import load
    from mlx_lm.tuner.trainer import grad_checkpoint
    from mlx_lm.tuner.utils import linear_to_lora_layers

    mx.set_memory_limit(int(a.mem_gb * 1e9))
    mx.set_cache_limit(int(1e9))
    mx.random.seed(a.seed)
    out = MODELS_DIR / a.run
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f"{out} exists and is not empty; choose a new --run name (runs are never overwritten)")
    out.mkdir(parents=True)
    log_f = open(out / "train_log.jsonl", "w")
    import yaml
    (out / "config.yaml").write_text(yaml.safe_dump({k: v for k, v in vars(a).items() if k != "config"}, sort_keys=False))

    def log(rec):
        rec["time"] = time.strftime("%H:%M:%S")
        log_f.write(json.dumps(rec) + "\n")
        log_f.flush()
        print(json.dumps(rec), flush=True)

    model, tok = load(BASE_MODELS[a.size])
    lid = {L: tok.encode(L, add_special_tokens=False)[0] for L in LETTERS3}
    pad = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id

    def prepare(items):
        rows = []
        for it in items:
            ids = tok.encode(render(tok, it["doc"], it["sentences"], it["idx"], it["qtype"]), add_special_tokens=False)
            allowed = letters(it["qtype"])
            rows.append({"ids": ids, "_len": len(ids), "n_opt": len(allowed), "gold": allowed.index(it["label"]),
                         "qtype": it["qtype"], "source": it["source"]})
        return rows

    d = DATA_PROCESSED / a.data
    train_rows = prepare(load_jsonl(d / f"{a.train}.jsonl"))
    rng = random.Random(a.seed)
    dev_items = []
    for name in ("dev_anli", "dev_ragtruth", "dev_minicheck"):
        items = load_jsonl(d / f"{name}.jsonl")
        for it in items:  # dev rows get a question type like training rows (fixed by seed)
            if it.get("cls") is None:
                it["qtype"], it["label"] = "sup", "A" if it["binary"] == 1 else "B"
            else:
                from ..prompts import label_for
                it["qtype"] = rng.choice(["sup", "three", "strict", "lenient"])
                it["label"] = label_for(it["qtype"], it["cls"])
        rng.shuffle(items)
        dev_items += items[: a.dev_size // 3]
    dev_rows = prepare(dev_items)

    model.freeze()
    lora_cfg = {"rank": a.rank, "scale": a.scale, "dropout": a.dropout}
    linear_to_lora_layers(model, len(model.layers), lora_cfg)
    grad_checkpoint(model.layers[0])
    n_train = sum(v.size for _, v in tree_flatten(model.trainable_parameters()))

    def batch_arrays(rows, idx):
        S = max(rows[i]["_len"] for i in idx)
        x = mx.array([rows[i]["ids"] + [pad] * (S - rows[i]["_len"]) for i in idx])
        last = mx.array([rows[i]["_len"] - 1 for i in idx])
        opt_ids = mx.array([[lid[L] for L in LETTERS3]] * len(idx))
        mask = mx.array([[0.0 if k < rows[i]["n_opt"] else -1e9 for k in range(3)] for i in idx])
        gold = mx.array([rows[i]["gold"] for i in idx])
        return x, last, opt_ids, mask, gold

    def letter_logits(m, x, last, opt_ids, mask):
        h = m(x)                                            # (B, S, V)
        h = h[mx.arange(x.shape[0]), last]                  # (B, V)
        return mx.take_along_axis(h, opt_ids, axis=1).astype(mx.float32) + mask

    def loss_fn(m, x, last, opt_ids, mask, gold):
        lg = letter_logits(m, x, last, opt_ids, mask)
        return nn.losses.cross_entropy(lg, gold, reduction="mean")

    loss_and_grad = nn.value_and_grad(model, loss_fn)
    batches = make_batches(train_rows, a.token_budget, a.max_rows, a.seed)
    total_micro = int(len(batches) * a.epochs)
    total_steps = max(1, total_micro // a.accum)
    if a.max_steps:  # short runs (hyper-parameter sweeps): compress the schedule so warm-up and decay both happen
        total_steps = min(total_steps, a.max_steps)
        total_micro = total_steps * a.accum
    warm = max(1, int(total_steps * a.warmup))
    sched = optim.join_schedules([optim.linear_schedule(1e-7, a.lr, warm), optim.cosine_decay(a.lr, total_steps - warm)], [warm])
    opt = optim.AdamW(learning_rate=sched, weight_decay=0.0)

    meta = {"size": a.size, "base_model": BASE_MODELS[a.size], "data": a.data, "train_file": a.train,
            "train_rows": len(train_rows), "train_tokens": sum(r["_len"] for r in train_rows),
            "micro_batches": total_micro, "steps": total_steps, "prompt_version": PROMPT_VERSION,
            "trainable_params": n_train, "args": vars(a), "started": time.strftime("%Y-%m-%d %H:%M:%S")}
    log({"event": "start", **{k: v for k, v in meta.items() if k != "args"}})

    def save(dirpath, extra):
        dirpath.mkdir(parents=True, exist_ok=True)
        mx.save_safetensors(str(dirpath / "adapters.safetensors"), dict(tree_flatten(model.trainable_parameters())))
        (dirpath / "adapter_config.json").write_text(json.dumps({"fine_tune_type": "lora", "num_layers": len(model.layers),
                                                                 "lora_parameters": lora_cfg}, indent=2))
        (dirpath / "groundone.json").write_text(json.dumps({**meta, **extra}, indent=2))

    def evaluate():
        model.eval()
        tot, correct, n = 0.0, 0, 0
        by_q = {}
        for b in make_batches(dev_rows, a.token_budget, a.max_rows, 0):
            x, last, opt_ids, mask, gold = batch_arrays(dev_rows, b)
            lg = letter_logits(model, x, last, opt_ids, mask)
            l = nn.losses.cross_entropy(lg, gold, reduction="sum")
            pred = mx.argmax(lg, axis=1)
            mx.eval(l, pred)
            tot += l.item()
            for i, p, g in zip(b, pred.tolist(), gold.tolist()):
                q = dev_rows[i]["qtype"]
                c, t = by_q.get(q, (0, 0))
                by_q[q] = (c + (p == g), t + 1)
                correct += p == g
                n += 1
        model.train()
        return {"dev_loss": tot / n, "dev_acc": correct / n, "dev_acc_by_q": {q: round(c / t, 4) for q, (c, t) in by_q.items()}}

    t_start = time.time()
    best = math.inf
    model.train()
    step, micro, acc_grads, run_loss, run_n = 0, 0, None, 0.0, 0
    stop_reason = "completed"
    if a.eval_initial:
        ev = evaluate()
        log({"event": "eval", "step": 0, **ev})
    for e in range(math.ceil(a.epochs)):
        for b in batches if e == 0 else make_batches(train_rows, a.token_budget, a.max_rows, a.seed + e):
            if micro >= total_micro:
                break
            loss, grads = loss_and_grad(model, *batch_arrays(train_rows, b))
            acc_grads = grads if acc_grads is None else nn.utils.tree_map(lambda u, v: u + v, acc_grads, grads)
            mx.eval(loss, acc_grads)
            run_loss += loss.item()
            run_n += 1
            micro += 1
            if micro % a.accum:
                continue
            opt.update(model, nn.utils.tree_map(lambda g: g / a.accum, acc_grads))
            mx.eval(model.trainable_parameters(), opt.state)
            acc_grads = None
            step += 1
            if step % 25 == 0:
                el = time.time() - t_start
                log({"event": "train", "step": step, "of": total_steps, "loss": round(run_loss / run_n, 4),
                     "lr": float(sched(step)), "elapsed_min": round(el / 60, 1),
                     "eta_min": round(el / step * (total_steps - step) / 60, 1), "peak_gb": round(mx.get_peak_memory() / 1e9, 2)})
                run_loss, run_n = 0.0, 0
            if step % a.eval_every == 0 or step == total_steps:
                ev = evaluate()
                log({"event": "eval", "step": step, **ev})
                save(out, {"last_step": step, **ev})
                if ev["dev_loss"] < best:
                    best = ev["dev_loss"]
                    save(out / "best", {"best_step": step, **ev})
            if a.max_hours and time.time() - t_start > a.max_hours * 3600:
                stop_reason = f"max-hours ({a.max_hours} h)"
                break
            if a.max_steps and step >= a.max_steps:
                stop_reason = f"max-steps ({a.max_steps})"
                break
        else:
            continue
        break
    ev = evaluate()
    save(out, {"last_step": step, "stop_reason": stop_reason, "finished": time.strftime("%Y-%m-%d %H:%M:%S"), **ev})
    if ev["dev_loss"] < best:
        save(out / "best", {"best_step": step, **ev})
    log({"event": "end", "step": step, "stop_reason": stop_reason, **ev,
         "wall_hours": round((time.time() - t_start) / 3600, 2)})
    if not (out / "best").exists():
        shutil.copytree(out, out / "best", ignore=shutil.ignore_patterns("best", "train_log.jsonl"))


if __name__ == "__main__":
    main()
