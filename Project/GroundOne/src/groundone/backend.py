"""MLX backend: load a Qwen2.5 checkpoint (+ optional LoRA adapter) and read answer-letter logits.

Two scoring paths, both without any text generation:
  score_shared  K prompts that share a long prefix (one answer, many questions): the common token prefix is
                prefilled once, its KV cache is replicated along the batch axis, and the K short suffixes run
                as right-padded batches (decision D14). Exact: equal to scoring each prompt alone.
  score_many    unrelated prompts (evaluation of pair datasets): length-sorted, right-padded batches.
Both return, per prompt, the raw logits of the requested letters (temperature is applied by the engine).
All MLX calls must happen on a single long-lived thread (see engine.Engine).
"""
import hashlib
import string
import time
from pathlib import Path

from .config import MAX_BATCH, MAX_PROMPT_TOKENS, MLX_MEMORY_LIMIT_GB
from .prompts import PROMPT_VERSION


class Backend:
    def __init__(self, base_repo, adapter_dir=None, name=None):
        import mlx.core as mx
        from mlx_lm import load
        self.mx = mx
        mx.set_memory_limit(int(MLX_MEMORY_LIMIT_GB * 1e9))
        mx.set_cache_limit(int(1e9))
        t = time.perf_counter()
        self.model, self.tokenizer = load(base_repo, adapter_path=adapter_dir)
        self.model.eval()
        self.letter_ids = {}
        for L in string.ascii_uppercase:
            ids = self.tokenizer.encode(L, add_special_tokens=False)
            if len(ids) != 1:
                raise RuntimeError(f"Letter {L!r} is not a single token")
            self.letter_ids[L] = ids[0]
        self.pad = self.tokenizer.pad_token_id if self.tokenizer.pad_token_id is not None else self.tokenizer.eos_token_id
        sha = None
        if adapter_dir:
            sha = hashlib.sha256((Path(adapter_dir) / "adapters.safetensors").read_bytes()).hexdigest()
        self.metadata = {
            "name": name or base_repo, "base_model": base_repo, "adapter": adapter_dir, "adapter_sha256": sha,
            "prompt_version": PROMPT_VERSION, "runtime": "mlx", "load_seconds": round(time.perf_counter() - t, 2),
            "fingerprint": hashlib.sha256(f"{base_repo}|{sha}|{PROMPT_VERSION}".encode()).hexdigest()[:16],
        }

    # ------------------------------------------------------------------ helpers
    def encode(self, text):
        ids = self.tokenizer.encode(text, add_special_tokens=False)
        if len(ids) > MAX_PROMPT_TOKENS:
            raise ValueError(f"Prompt has {len(ids)} tokens; the limit is {MAX_PROMPT_TOKENS} (GROUNDONE_MAX_TOKENS)")
        return ids

    def _read(self, logits_rows, letters_list):
        mx = self.mx
        rows = logits_rows.astype(mx.float32)
        mx.eval(rows)
        out = []
        for i, letters in enumerate(letters_list):
            idx = mx.array([self.letter_ids[L] for L in letters])
            out.append(rows[i][idx].tolist())
        return out

    @staticmethod
    def common_prefix(prompts):
        n = 0
        while all(len(p) > n for p in prompts) and len({p[n] for p in prompts}) == 1:
            n += 1
        return min(n, min(len(p) for p in prompts) - 1)  # keep >= 1 suffix token per prompt

    # ------------------------------------------------------------------ scoring
    def score_shared(self, prompts, letters_list):
        """prompts: list of token lists sharing a prefix. Returns (logits per prompt, timing)."""
        mx = self.mx
        from mlx_lm.models.cache import make_prompt_cache
        t0 = time.perf_counter()
        n = self.common_prefix(prompts) if len(prompts) > 1 else len(prompts[0]) - 1
        cache = make_prompt_cache(self.model)
        if n > 0:
            mx.eval(self.model(mx.array([prompts[0][:n]]), cache=cache))
        prefix_state = [c.state if n > 0 else None for c in cache]
        t1 = time.perf_counter()
        out = []
        for start in range(0, len(prompts), MAX_BATCH):
            chunk = prompts[start:start + MAX_BATCH]
            K = len(chunk)
            bcache = make_prompt_cache(self.model)
            if n > 0:
                for c, (k, v) in zip(bcache, prefix_state):
                    c.state = (mx.repeat(k, K, axis=0), mx.repeat(v, K, axis=0))
            sufs = [p[n:] for p in chunk]
            S = max(len(s) for s in sufs)
            batch = mx.array([s + [self.pad] * (S - len(s)) for s in sufs])  # right padding: real tokens never see pads
            logits = self.model(batch, cache=bcache)
            rows = logits[mx.arange(K), mx.array([len(s) - 1 for s in sufs])]
            out += self._read(rows, letters_list[start:start + K])
        t2 = time.perf_counter()
        return out, {"prefix_tokens": n, "suffix_tokens": sum(len(p) - n for p in prompts),
                     "prefill_seconds": t1 - t0, "batch_seconds": t2 - t1}

    def score_many(self, prompts, letters_list, token_budget=8192):
        """Unrelated prompts, batched by length (no shared cache). Returns logits in input order."""
        mx = self.mx
        order = sorted(range(len(prompts)), key=lambda i: len(prompts[i]))
        result = [None] * len(prompts)
        i = 0
        while i < len(order):
            j, longest = i, 0
            while j < len(order) and j - i < MAX_BATCH and max(longest, len(prompts[order[j]])) * (j - i + 1) <= token_budget:
                longest = max(longest, len(prompts[order[j]]))
                j += 1
            j = max(j, i + 1)
            idx = order[i:j]
            S = max(len(prompts[k]) for k in idx)
            batch = mx.array([prompts[k] + [self.pad] * (S - len(prompts[k])) for k in idx])
            logits = self.model(batch)
            rows = logits[mx.arange(len(idx)), mx.array([len(prompts[k]) - 1 for k in idx])]
            for k, r in zip(idx, self._read(rows, [letters_list[k] for k in idx])):
                result[k] = r
            i = j
        return result
