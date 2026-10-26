"""MLX backend: load a Qwen2.5 checkpoint (+ optional LoRA adapter) and read answer-letter logits.

Two scoring paths, both without any text generation:
  score_shared  K prompts that share a long prefix (one answer, many questions): the common token prefix is
                prefilled once, its KV cache is replicated along the batch axis, and the K short suffixes run
                as right-padded batches (decision D14). Exact: equal to scoring each prompt alone.
  score_many    unrelated prompts (evaluation of pair datasets): length-sorted, right-padded batches.
Both return, per prompt, the raw logits of the requested letters (temperature is applied by the engine).
Design (b) runs one pass per answer (score_positions); with a prefilled prefix (prefill, score_positions_from) only
the tokens after it are processed, which is exact under causal attention (prefix caching, D32).
All MLX calls must happen on a single long-lived thread (see engine.Engine).
"""
import hashlib
import string
import time
from contextlib import contextmanager
from pathlib import Path

from .config import MAX_BATCH, MAX_PROMPT_TOKENS, MLX_MEMORY_LIMIT_GB
from .prompts import PROMPT_VERSION


_EXPLICIT_MASK = [False]


def _patch_qwen2_mask():
    """MLX 0.29.3's fused attention with mask="causal" is wrong for some shapes when several queries follow cached keys
    (e.g. 501 queries after 523 cached keys: errors up to 0.7 in the logits; with offset 0 or one query it is exact).
    Inside `explicit_offset_mask()` such calls get an explicit boolean causal mask instead, which matches a float32
    reference. Cold passes (offset 0) and decoding (one query) never take this path, so published results are unchanged."""
    from mlx_lm.models import base, qwen2
    if getattr(qwen2.create_attention_mask, "_groundone", False):
        return
    original = qwen2.create_attention_mask

    def create_attention_mask(h, cache=None, *args, **kwargs):
        offset = getattr(cache, "offset", 0) if cache is not None else 0
        if _EXPLICIT_MASK[0] and offset and h.shape[1] > 1:
            return base.create_causal_mask(h.shape[1], offset)
        return original(h, cache, *args, **kwargs)

    create_attention_mask._groundone = True
    qwen2.create_attention_mask = create_attention_mask


@contextmanager
def explicit_offset_mask():
    _patch_qwen2_mask()
    _EXPLICIT_MASK[0] = True
    try:
        yield
    finally:
        _EXPLICIT_MASK[0] = False


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

    # ------------------------------------------------------------------ prefix cache (D32)
    def prefill(self, ids, base=None):
        """KV state after reading `ids`, optionally continuing a shorter prefix `base` (whose ids must start `ids`).
        Returned as {"ids": tuple, "state": per-layer (keys, values)}; reusable by any sequence that starts with ids."""
        mx = self.mx
        cache, start = self._cache_from(base, ids)
        if start < len(ids):
            with explicit_offset_mask():
                mx.eval(self.model.model(mx.array([ids[start:]]), cache=cache))
        return {"ids": tuple(ids), "state": [c.state for c in cache]}

    def _cache_from(self, prefix, ids):
        from mlx_lm.models.cache import make_prompt_cache
        cache = make_prompt_cache(self.model)
        if prefix is None:
            return cache, 0
        n = len(prefix["ids"])
        if tuple(ids[:n]) != prefix["ids"]:
            raise ValueError("the sequence does not start with the cached prefix")
        for c, st in zip(cache, prefix["state"]):  # the state is sized exactly, so new tokens reallocate: never mutated
            c.state = st
        return cache, n

    def score_positions_from(self, prefix, ids, positions, letters=("A", "B", "C")):
        """Design (b) for one sequence with a prefilled prefix: the forward pass covers only ids[len(prefix):]; marker
        positions are absolute and must lie after the prefix. Same logits as score_positions on the whole sequence."""
        mx = self.mx
        from .readout import head
        cache, n = self._cache_from(prefix, ids)
        if not positions or min(positions) < n:
            raise ValueError("marker positions must lie after the cached prefix")
        with explicit_offset_mask():
            h = self.model.model(mx.array([ids[n:]]), cache=cache)
            lid = mx.array([self.letter_ids[L] for L in letters])
            lg = head(self.model, h[0, mx.array([p - n for p in positions])])[:, lid].astype(mx.float32)
            mx.eval(lg)
        return lg.tolist()

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

    def score_positions(self, seqs, positions, letters=("A", "B", "C"), token_budget=16384, with_argmax=False):
        """Design (b): one forward pass per sequence, letter logits read at each marker position.
        seqs: token lists; positions: list of position lists. Returns, per sequence, a list of logit triples.
        with_argmax=True also returns, per sequence, the full-vocabulary argmax token id at each marker (what greedy
        single-token generation would emit there; control B2)."""
        mx = self.mx
        from .readout import logits_at
        order = sorted(range(len(seqs)), key=lambda i: len(seqs[i]))
        lid = mx.array([self.letter_ids[L] for L in letters])
        result = [None] * len(seqs)
        amax = [None] * len(seqs)
        i = 0
        while i < len(order):
            j, longest = i, 0
            while j < len(order) and j - i < MAX_BATCH and max(longest, len(seqs[order[j]])) * (j - i + 1) <= token_budget:
                longest = max(longest, len(seqs[order[j]]))
                j += 1
            j = max(j, i + 1)
            idx = order[i:j]
            S = max(len(seqs[k]) for k in idx)
            batch = mx.array([seqs[k] + [self.pad] * (S - len(seqs[k])) for k in idx])
            rows = [b for b, k in enumerate(idx) for _ in positions[k]]
            cols = [p for k in idx for p in positions[k]]
            full = logits_at(self.model, batch, mx.array(rows), mx.array(cols))
            lg = full[:, lid].astype(mx.float32)
            am = mx.argmax(full, axis=1) if with_argmax else None
            mx.eval(lg, *([am] if with_argmax else []))
            flat, flat_am = lg.tolist(), am.tolist() if with_argmax else None
            n = 0
            for k in idx:
                result[k] = flat[n:n + len(positions[k])]
                if with_argmax:
                    amax[k] = flat_am[n:n + len(positions[k])]
                n += len(positions[k])
            i = j
        return (result, amax) if with_argmax else result

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
