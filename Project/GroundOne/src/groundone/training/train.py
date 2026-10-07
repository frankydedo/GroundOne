"""LoRA fine-tuning of GroundOne (plan §6, D5).

- Loss: cross-entropy over the *allowed answer letters only* (A/B, or A/B/C for the three-way question), read at the
  last prompt token. The prompt is never supervised. Prompts come from groundone.prompts, as at inference.
- LoRA on all linear layers of all blocks, gradient checkpointing, length-bucketed batches under a token budget,
  gradient accumulation, AdamW with linear warm-up and cosine decay, one epoch by default.
- Design (b), the default: one row per answer; a marker follows every scored sentence and the loss is the class-weighted
  cross-entropy over A/B/C at all markers (each class weighted to contribute equally). Design (a): one row per question.
- Every `--eval-every` steps: loss and accuracy on a fixed dev subset; the best checkpoint is kept in best/.
  With `--dev-file dev_mix` (data v2, D22) the dev rows carry their question and a block (ANLI pair / ANLI multi-sentence
  / RAGTruth / MiniCheck); balanced accuracy is computed per (block, question) and `--select bacc` keeps the checkpoint
  with the highest mean of these (`dev_score`) instead of the lowest dev loss.
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
from ..prompts import LETTERS_MARKED, PROMPT_VERSION, PROMPT_VERSION_MARKED, encode_marked, letters, render

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
    ap.add_argument("--dev-size", type=int, default=600, help="v1-style dev: rows drawn from dev_anli/ragtruth/minicheck")
    ap.add_argument("--dev-file", default="", help="fixed dev file with qtype/label/block per row (e.g. dev_mix); overrides --dev-size")
    ap.add_argument("--select", choices=["loss", "bacc"], default="loss", help="best/ = lowest dev loss or highest dev_score")
    ap.add_argument("--max-hours", type=float, default=0, help="stop cleanly after this wall time (0 = no limit)")
    ap.add_argument("--max-steps", type=int, default=0,
                    help="stop after N optimiser steps; the LR schedule (warm-up + cosine) is compressed to N steps")
    ap.add_argument("--eval-initial", type=int, default=1, help="1 = evaluate the untrained model at step 0")
    ap.add_argument("--seed", type=int, default=1234)
    ap.add_argument("--design", choices=["a", "b"], default="b",
                    help="b (default): one row per answer, verdicts read at a marker after each scored sentence; "
                         "a: one row per question (prompt + question suffix)")
    ap.add_argument("--sample", type=int, default=0, help="design b: random subset of N training answers (0 = all)")
    ap.add_argument("--dev-sample", type=int, default=0, help="design b: fixed random subset of N dev answers (0 = all)")
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
                         "qtype": it["qtype"], "source": it["source"], "block": it.get("block", it["source"])})
        return rows

    d = DATA_PROCESSED / a.data
    CLS = ("supported", "contradicted", "not_mentioned")

    def prepare_b(records, weights):
        rows = []
        for r in records:
            scored = [l is not None for l in r["labels"]]
            ids, pos = encode_marked(tok, r["doc"], r["sentences"], scored)
            golds = [CLS.index(l) for l in r["labels"] if l is not None]
            rows.append({"ids": ids, "_len": len(ids), "pos": pos, "golds": golds, "w": [weights[g] for g in golds],
                         "block": r["task"], "source": r["source"]})
        return rows

    if a.design == "b":
        recs = load_jsonl(d / f"{a.train}.jsonl")
        if a.sample:
            recs = random.Random(a.seed).sample(recs, min(a.sample, len(recs)))
        counts = [sum(l == c for r in recs for l in r["labels"]) for c in CLS]
        total = sum(counts)
        class_w = [total / (3 * n) for n in counts]  # balanced: each class contributes equally to the loss
        train_rows = prepare_b(recs, class_w)
        dev_recs = load_jsonl(d / f"{a.dev_file or 'dev'}.jsonl")
        if a.dev_sample:
            dev_recs = random.Random(0).sample(dev_recs, min(a.dev_sample, len(dev_recs)))
        dev_rows_b = prepare_b(dev_recs, class_w)
    else:
        train_rows = prepare(load_jsonl(d / f"{a.train}.jsonl"))
    rng = random.Random(a.seed)
    dev_items = load_jsonl(d / f"{a.dev_file}.jsonl") if a.dev_file and a.design == "a" else []
    for name in ([] if (a.dev_file or a.design == "b") else ("dev_anli", "dev_ragtruth", "dev_minicheck")):
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
    dev_rows = prepare(dev_items) if a.design == "a" else dev_rows_b

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

    from ..readout import logits_at
    lid3 = mx.array([lid[L] for L in LETTERS_MARKED])

    def batch_arrays_b(rows, idx):
        S = max(rows[i]["_len"] for i in idx)
        x = mx.array([rows[i]["ids"] + [pad] * (S - rows[i]["_len"]) for i in idx])
        r = mx.array([b for b, i in enumerate(idx) for _ in rows[i]["pos"]])
        c = mx.array([p for i in idx for p in rows[i]["pos"]])
        gold = mx.array([g for i in idx for g in rows[i]["golds"]])
        w = mx.array([v for i in idx for v in rows[i]["w"]])
        return x, r, c, gold, w

    def logits_b(m, x, r, c):
        return logits_at(m, x, r, c)[:, lid3].astype(mx.float32)

    def loss_fn_b(m, x, r, c, gold, w):
        ce = nn.losses.cross_entropy(logits_b(m, x, r, c), gold, reduction="none")
        return (ce * w).sum() / w.sum()

    if a.design == "b":
        batch_arrays, loss_fn = batch_arrays_b, loss_fn_b
    loss_and_grad = nn.value_and_grad(model, loss_fn)
    batches = make_batches(train_rows, a.token_budget, a.max_rows, a.seed)
    total_micro = int(len(batches) * a.epochs)
    total_steps = max(1, total_micro // a.accum)
    if a.max_steps:  # short runs (hyper-parameter sweeps): compress the schedule so warm-up and decay both happen
        total_steps = min(total_steps, a.max_steps)
        total_micro = total_steps * a.accum
    warm = max(1, int(total_steps * a.warmup))
    sched = optim.join_schedules([optim.linear_schedule(1e-7, a.lr, warm), optim.cosine_decay(a.lr, max(1, total_steps - warm))], [warm])
    opt = optim.AdamW(learning_rate=sched, weight_decay=0.0)

    meta = {"size": a.size, "base_model": BASE_MODELS[a.size], "data": a.data, "train_file": a.train,
            "train_rows": len(train_rows), "train_tokens": sum(r["_len"] for r in train_rows),
            "micro_batches": total_micro, "steps": total_steps, "design": a.design,
            "prompt_version": PROMPT_VERSION_MARKED if a.design == "b" else PROMPT_VERSION,
            "trainable_params": n_train, "args": vars(a), "started": time.strftime("%Y-%m-%d %H:%M:%S")}
    if a.design == "b":
        meta.update({"train_answers": len(train_rows), "train_decisions": sum(len(r["golds"]) for r in train_rows),
                     "dev_answers": len(dev_rows), "class_weights": dict(zip(CLS, [round(v, 3) for v in class_w]))})
    log({"event": "start", **{k: v for k, v in meta.items() if k != "args"}})

    def save(dirpath, extra):
        dirpath.mkdir(parents=True, exist_ok=True)
        mx.save_safetensors(str(dirpath / "adapters.safetensors"), dict(tree_flatten(model.trainable_parameters())))
        (dirpath / "adapter_config.json").write_text(json.dumps({"fine_tune_type": "lora", "num_layers": len(model.layers),
                                                                 "lora_parameters": lora_cfg}, indent=2))
        (dirpath / "groundone.json").write_text(json.dumps({**meta, **extra}, indent=2))

    def evaluate_b():
        model.eval()
        tot, wsum, correct, n = 0.0, 0.0, 0, 0
        hits, share = {}, [0, 0, 0]
        for b in make_batches(dev_rows, a.token_budget, a.max_rows, 0):
            x, r, c, gold, w = batch_arrays_b(dev_rows, b)
            lg = logits_b(model, x, r, c)
            ce = nn.losses.cross_entropy(lg, gold, reduction="none")
            pred = mx.argmax(lg, axis=1)
            mx.eval(ce, pred)
            tot += (ce * w).sum().item()
            wsum += w.sum().item()
            blocks = [dev_rows[i]["block"] for i in b for _ in dev_rows[i]["pos"]]
            for blk, p, g in zip(blocks, pred.tolist(), gold.tolist()):
                for key in (blk, "all"):
                    hc = hits.setdefault(key, {}).setdefault(g, [0, 0])
                    hc[0] += p == g
                    hc[1] += 1
                share[p] += 1
                correct += p == g
                n += 1
        model.train()
        rec = {k: sum(c_ / t for c_, t in gs.values()) / len(gs) for k, gs in hits.items()}
        bacc = {f"{k}|three": round(v, 4) for k, v in sorted(rec.items()) if k != "all"}
        return {"dev_loss": tot / wsum, "dev_acc": correct / n, "dev_acc_by_q": {"three": round(correct / n, 4)},
                "dev_bacc": bacc, "dev_score": round(sum(bacc.values()) / len(bacc), 4),
                "dev_macro_recall_all": round(rec["all"], 4),
                "dev_pred_share": {k: round(v / n, 4) for k, v in zip(CLS, share)}}

    def evaluate():
        if a.design == "b":
            return evaluate_b()
        model.eval()
        tot, correct, n = 0.0, 0, 0
        by_q, hits = {}, {}  # hits[(block, qtype)][gold] = [correct, total]
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
                hc = hits.setdefault((dev_rows[i]["block"], q), {}).setdefault(g, [0, 0])
                hc[0] += p == g
                hc[1] += 1
                correct += p == g
                n += 1
        model.train()
        # balanced accuracy = mean recall over the gold answers present in the group
        bacc = {f"{b}|{q}": round(sum(c / t for c, t in gs.values()) / len(gs), 4) for (b, q), gs in sorted(hits.items())}
        return {"dev_loss": tot / n, "dev_acc": correct / n, "dev_acc_by_q": {q: round(c / t, 4) for q, (c, t) in by_q.items()},
                "dev_bacc": bacc, "dev_score": round(sum(bacc.values()) / len(bacc), 4)}

    def better(ev, best):
        return ev["dev_score"] > best if a.select == "bacc" else ev["dev_loss"] < best

    def key(ev):
        return ev["dev_score"] if a.select == "bacc" else ev["dev_loss"]

    t_start = time.time()
    best = -math.inf if a.select == "bacc" else math.inf
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
                if better(ev, best):
                    best = key(ev)
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
    if better(ev, best):
        save(out / "best", {"best_step": step, **ev})
    log({"event": "end", "step": step, "stop_reason": stop_reason, **ev,
         "wall_hours": round((time.time() - t_start) / 3600, 2)})
    if not (out / "best").exists():
        shutil.copytree(out, out / "best", ignore=shutil.ignore_patterns("best", "train_log.jsonl"))


if __name__ == "__main__":
    main()
