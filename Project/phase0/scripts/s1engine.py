"""Minimal System One engine for Phase 0b: shared prefix + K short suffixes scored in one batched pass.

score(prompts, letters) takes K full prompts (token lists) that share a common prefix, prefills the prefix
once, replicates its KV cache K times, runs all K suffixes as one right-padded batch, and reads the
logits of the allowed answer letters at each suffix's last real token. No text is generated.
"""
# pyrefly: ignore [missing-import]
import mlx.core as mx
# pyrefly: ignore [missing-import]
from mlx_lm.models.cache import make_prompt_cache


class Engine:
    def __init__(self, model, tok, letters=("A", "B", "C")):
        self.model, self.tok = model, tok
        self.ids = {L: tok.encode(L, add_special_tokens=False)[0] for L in letters}
        self.pad = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id

    @staticmethod
    def common_prefix(prompts):
        n = 0
        while all(len(p) > n for p in prompts) and len({p[n] for p in prompts}) == 1:
            n += 1
        return min(n, min(len(p) for p in prompts) - 1)  # keep >= 1 suffix token per prompt

    def _probs(self, logits_rows, letters):
        idx = mx.array([self.ids[L] for L in letters])
        sel = logits_rows[:, idx].astype(mx.float32)
        return mx.softmax(sel, axis=-1)

    def score_batched(self, prompts, letters=("A", "B")):
        """One prefill of the shared prefix + one batched pass over all suffixes."""
        n = self.common_prefix(prompts)
        cache = make_prompt_cache(self.model)
        mx.eval(self.model(mx.array([prompts[0][:n]]), cache=cache))
        K = len(prompts)
        for c in cache:  # replicate the prefix KV cache K times along the batch axis
            k, v = c.state
            c.state = (mx.repeat(k, K, axis=0), mx.repeat(v, K, axis=0))
        sufs = [p[n:] for p in prompts]
        S = max(len(s) for s in sufs)
        batch = mx.array([s + [self.pad] * (S - len(s)) for s in sufs])  # right padding: real tokens never see pads
        logits = self.model(batch, cache=cache)
        last = mx.array([len(s) - 1 for s in sufs])
        rows = logits[mx.arange(K), last]
        pr = self._probs(rows, letters)
        mx.eval(pr)
        return pr.tolist(), {"prefix_tokens": n, "max_suffix_tokens": S}

    def score_fresh(self, prompts, letters=("A", "B")):
        """Reference: one full forward pass per prompt (no sharing)."""
        out = []
        for p in prompts:
            lg = self.model(mx.array([p]))[:, -1]
            pr = self._probs(lg, letters)
            mx.eval(pr)
            out.append(pr.tolist()[0])
        return out
