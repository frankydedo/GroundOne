import sys; sys.path.insert(0, "scripts")
import time, mlx.core as mx
from mlx_lm import load
from s1engine import Engine
m, t = load("lmstudio-community/Qwen2.5-0.5B-Instruct-MLX-8bit"); e = Engine(m, t)
doc = "The Eiffel Tower is in Paris. It was completed in 1889 and is 330 metres tall. " * 20
sents = ["The tower is in Paris.", "It was finished in 1889.", "It is 500 metres tall.", "It is made of wood."] * 6
P = [t.encode(t.apply_chat_template([{"role":"user","content":f"DOCUMENT:\n{doc}\n\nQuestion about sentence [{i+1}]: {s} Supported? A yes, B no."}], tokenize=False, add_generation_prompt=True), add_special_tokens=False) for i, s in enumerate(sents)]
pb, info = e.score_batched(P); pf = e.score_fresh(P)
print("K", len(P), info, "max|dp|", max(abs(a[0]-b[0]) for a, b in zip(pb, pf)))
for f, name in [(lambda: e.score_batched(P), "batched"), (lambda: e.score_fresh(P), "fresh")]:
    tt = time.perf_counter(); f(); print(name, round((time.perf_counter()-tt)*1000), "ms")
print([round(p[0], 2) for p in pb[:4]])
