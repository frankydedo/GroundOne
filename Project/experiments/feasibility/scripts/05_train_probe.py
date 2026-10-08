"""Phase 0, step 6: LoRA training memory/speed probe with the GroundOne loss (not a real training run).

Custom MLX loop (mlx_lm.lora's data pipeline is incompatible with transformers 5.x here):
LoRA on all linear layers of all blocks, gradient checkpointing, batch size 1,
loss = cross-entropy over the two answer logits (A = supported, B = not supported) at the last prompt position.
Examples are padded with extra documents to ~N tokens. Runs 30 steps and records peak memory and step time.
Usage: python 05_train_probe.py qwen0.5b|qwen3b 1024|2048
"""
import sys
import time

import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
import pandas as pd
from mlx_lm import load
from mlx_lm.tuner.trainer import grad_checkpoint
from mlx_lm.tuner.utils import linear_to_lora_layers

from common import DATA, MODELS, RESULTS, log, write_json

key, n_tok = sys.argv[1], int(sys.argv[2])
STEPS = 30
mx.set_memory_limit(int(9e9))
mx.set_cache_limit(int(1e9))
model, tok = load(MODELS[key])
A, B = tok.encode("A", add_special_tokens=False)[0], tok.encode("B", add_special_tokens=False)[0]
SYS = "You are a faithfulness verifier. Decide whether the CLAIM is fully supported by the DOCUMENT. Reply with one letter: A = supported, B = not supported."

mc = pd.concat([pd.read_parquet(DATA / "minicheck_c2d.parquet"), pd.read_parquet(DATA / "minicheck_d2c.parquet")]).sample(frac=1, random_state=0)
docs = mc["doc"].tolist()
batches = []
for i, r in enumerate(mc.head(STEPS).itertuples()):
    doc, j = r.doc, i
    while len(tok.encode(doc, add_special_tokens=False)) < n_tok - 120:
        j += 1
        doc += "\n\n" + docs[j % len(docs)]
    doc = tok.decode(tok.encode(doc, add_special_tokens=False)[: n_tok - 120])
    prompt = tok.apply_chat_template([{"role": "system", "content": SYS},
                                      {"role": "user", "content": f"DOCUMENT:\n{doc}\n\nCLAIM:\n{r.claim}"}],
                                     tokenize=False, add_generation_prompt=True)
    batches.append((tok.encode(prompt, add_special_tokens=False), 0 if r.label == 1 else 1))

model.freeze()
linear_to_lora_layers(model, len(model.layers), {"rank": 16, "scale": 2.0, "dropout": 0.0})
grad_checkpoint(model.layers[0])
n_train = sum(v.size for _, v in nn.utils.tree_flatten(model.trainable_parameters()))
log(f"{key} trainable params {n_train/1e6:.1f}M, examples ~{sum(len(x) for x, _ in batches)/len(batches):.0f} tokens")


def loss_fn(m, x, y):
    lg = m(x)[:, -1, :]
    two = mx.stack([lg[:, A], lg[:, B]], axis=-1).astype(mx.float32)
    return nn.losses.cross_entropy(two, y).mean()


loss_and_grad = nn.value_and_grad(model, loss_fn)
opt = optim.AdamW(learning_rate=1e-4)
mx.reset_peak_memory()
times, losses = [], []
for step, (ids, y) in enumerate(batches):
    t = time.perf_counter()
    loss, grads = loss_and_grad(model, mx.array([ids]), mx.array([y]))
    opt.update(model, grads)
    mx.eval(model.trainable_parameters(), opt.state, loss)
    times.append(time.perf_counter() - t)
    losses.append(float(loss.item()))
    if step % 10 == 0:
        log(f"step {step} loss {losses[-1]:.3f} {times[-1]:.2f}s peak {mx.get_peak_memory()/1e9:.2f} GB")
steady = sorted(times[5:])[len(times[5:]) // 2]
res = {"model": MODELS[key], "target_tokens": n_tok, "trainable_params_m": n_train / 1e6,
       "peak_mem_gb": mx.get_peak_memory() / 1e9, "sec_per_step_median": steady,
       "tokens_per_sec": n_tok / steady, "loss_first5": losses[:5], "loss_last5": losses[-5:],
       "est_hours_35k_examples_1_epoch": 35000 * steady / 3600}
write_json(RESULTS / f"05_train_probe_{key}_{n_tok}.json", res)
log(f"done {key} {n_tok}: peak {res['peak_mem_gb']:.2f} GB, {steady:.2f} s/step, est. {res['est_hours_35k_examples_1_epoch']:.1f} h for 35k examples at this length")
