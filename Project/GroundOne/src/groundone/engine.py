"""Thread-safe long-lived service around the MLX backend.

All model work runs on ONE worker thread that lives as long as the process: web servers call from short-lived pool
threads, and MLX/Metal contexts must not hop threads (lesson from LightningRoute and Rizzo-Flow). Requests are
serialised by a lock; parallelism is *inside* a request (K questions in one batched pass).

/v1/verify follows the adapter's readout design (read from its groundone.json): design (b), the default since D22, is
served since D27 (one pass, a marker per scored sentence, coherent labels from calibrated probabilities and the dev
threshold); design (a) remains for base models and design-(a) adapters. /v1/systemone (generic questions) uses (a).
Design (b) keeps a prefix cache (D32): the fixed instructions are prefilled once, and the last few documents' KV
states are kept (LRU), so a new answer on a cached document costs only the answer's tokens. The last answer verified
on each document is kept too: a new answer that shares its first sentences (a rewrite of a later sentence) reuses their
verdicts and is read only from the first changed token. Exact under causal
attention; GROUNDONE_PREFIX_CACHE=0 disables it.
"""
import json
import os
import time
from collections import OrderedDict, defaultdict
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

from . import compat
from .calibration import Calibration, decide_three, softmax
from .prompts import ANSWER_NAMES, letters, render
from .text import split_sentences


def common_prefix_len(a, b):
    n = 0
    for x, y in zip(a, b):
        if x != y:
            break
        n += 1
    return n


class Engine:
    def __init__(self, backend, calibration_path=None, design="a"):
        self.backend = backend
        self.design = design
        self.calibration = (Calibration.load(calibration_path, backend.metadata["fingerprint"])
                            if calibration_path else None)
        self._lock = Lock()
        self._worker = ThreadPoolExecutor(max_workers=1, thread_name_prefix="groundone-mlx")
        self.prefix_cache = os.environ.get("GROUNDONE_PREFIX_CACHE", "1") != "0"
        self._fixed = None                 # KV state of the fixed instructions
        self._docs = OrderedDict()         # head ids (instructions + document) -> KV state, least recently used first
        self._answers = {}                 # head ids -> last answer verified on it: ids, KV state, marker logits
        self.max_cached_docs = 4

    @classmethod
    def load(cls, size=None, adapter=None, calibration=None, base=None):
        from .backend import Backend
        from .config import resolve_model
        base, adir, name = resolve_model(size, adapter, base)
        ex = ThreadPoolExecutor(max_workers=1, thread_name_prefix="groundone-mlx")
        backend = ex.submit(Backend, base, adir, name).result()  # load on the same thread that will run inference
        meta = Path(adir) / "groundone.json" if adir else None
        design = json.loads(meta.read_text()).get("design", "a") if meta and meta.exists() else "a"
        eng = cls(backend, calibration, design)
        eng._worker.shutdown(wait=True)
        eng._worker = ex
        return eng

    @property
    def name(self):
        return self.backend.metadata["name"]

    def _probs(self, qtype, logits, multi):
        return self.calibration.probs(qtype, logits, multi) if self.calibration else softmax(logits)

    def _run(self, fn, *args):
        with self._lock:
            return self._worker.submit(fn, *args).result()

    # ------------------------------------------------------------------ native: /v1/verify
    def verify(self, req):
        if self.design == "b":
            return self._verify_b(req)
        t0 = time.perf_counter()
        sentences = req.sentences or [s for _, _, s in split_sentences(req.answer)]
        if not sentences:
            raise ValueError("The answer contains no sentence")
        thr = req.threshold if req.threshold is not None else 0.5
        tok = self.backend.tokenizer
        jobs = [(i, q) for i in range(len(sentences)) for q in req.questions]
        prompts = [self.backend.encode(render(tok, req.document, sentences, i, q)) for i, q in jobs]
        t1 = time.perf_counter()
        logits, timing = self._run(self.backend.score_shared, prompts, [letters(q) for _, q in jobs])
        res = [{"index": i, "text": s, "answers": {}, "labels": {}} for i, s in enumerate(sentences)]
        for (i, q), lg in zip(jobs, logits):
            ps = self._probs(q, lg, len(sentences) > 1)
            names = ANSWER_NAMES[q]
            res[i]["answers"][q] = dict(zip(names, ps))
            res[i]["labels"][q] = names[max(range(len(ps)), key=ps.__getitem__)]
        for r in res:
            sup = r["answers"].get("sup")
            r["p_supported"] = sup["supported"] if sup else None
            r["flagged"] = (r["p_supported"] < thr) if sup else None
        return {
            "model": self.name, "design": "a", "decision_rule": "argmax per question; flagged iff P(supported) < threshold",
            "threshold": thr, "sentences": res, "n_decisions": len(jobs),
            "usage": {"input_tokens": timing["prefix_tokens"] + timing["suffix_tokens"], "output_tokens": 0},
            "timing": {"total_seconds": time.perf_counter() - t0, "encode_seconds": t1 - t0,
                       "prefill_seconds": timing["prefill_seconds"], "batch_seconds": timing["batch_seconds"]},
            "fingerprint": self.backend.metadata["fingerprint"], "calibrated": self.calibration is not None,
        }

    def _verify_b(self, req):
        """Design (b): segment with the training rule, one forward pass, verdicts at the markers (D22, D27).

        Labels, flags and the returned probabilities follow one rule: with a threshold (the request's, else the one
        fitted on dev), "supported" iff P(supported) >= threshold, else the more probable of the other two; without
        any threshold, the argmax of the raw (class-balanced) logits, the decision used in the evaluation (D24)."""
        from .config import MAX_PROMPT_TOKENS
        from .data.segment import is_checkable, segment
        from .prompts import encode_marked
        t0 = time.perf_counter()
        if req.sentences:
            sents = [(s, is_checkable(s)) for s in req.sentences]
        else:
            sents = [(s.text, s.checkable) for s in segment(req.answer)]
        if not sents:
            raise ValueError("The answer contains no sentence")
        tok = self.backend.tokenizer
        ids, pos = encode_marked(tok, req.document, [s for s, _ in sents], [c for _, c in sents])
        if len(ids) > MAX_PROMPT_TOKENS:
            raise ValueError(f"Prompt has {len(ids)} tokens; the limit is {MAX_PROMPT_TOKENS} (GROUNDONE_MAX_TOKENS)")
        t1 = time.perf_counter()
        cached = "none"
        if not pos:
            logits = []
        elif self.prefix_cache:
            logits, cached = self._run(self._score_cached, req.document, ids, pos)
        else:
            logits = self._run(self.backend.score_positions, [ids], [pos])[0]
        t2 = time.perf_counter()
        cal = self.calibration
        thr = req.threshold if req.threshold is not None else (cal.thresholds.get("three") if cal else None)
        if thr is not None:
            rule = ("calibrated probabilities; " if cal else "uncalibrated probabilities; ") + \
                   "supported iff P(supported) >= threshold, else argmax(contradicted, not mentioned)"
        else:
            rule = "argmax of the raw class-balanced logits (no threshold available)"
        names = ANSWER_NAMES["three"]
        res, it = [], iter(logits)
        for i, (s, checkable) in enumerate(sents):
            r = {"index": i, "text": s, "scored": checkable, "answers": {}, "labels": {}, "p_supported": None,
                 "flagged": None, "flag_strict": None, "flag_lenient": None}
            if checkable:
                lg = next(it)
                p = cal.probs("three", lg) if cal else softmax(lg)
                k = decide_three(p, thr) if thr is not None else max(range(3), key=lg.__getitem__)
                views = {"three": (dict(zip(names, p)), names[k]),
                         "sup": ({"supported": p[0], "not_supported": 1 - p[0]}, "supported" if k == 0 else "not_supported"),
                         "strict": ({"acceptable": p[0], "error": 1 - p[0]}, "acceptable" if k == 0 else "error"),
                         "lenient": ({"acceptable": 1 - p[1], "error": p[1]}, "error" if k == 1 else "acceptable")}
                for q in dict.fromkeys(["three", *req.questions]):
                    r["answers"][q], r["labels"][q] = views[q]
                r.update(p_supported=p[0], flagged=k != 0, flag_strict=k != 0, flag_lenient=k == 1)
            res.append(r)
        return {
            "model": self.name, "design": "b", "decision_rule": rule, "threshold": thr, "sentences": res,
            "n_decisions": len(pos), "usage": {"input_tokens": len(ids), "output_tokens": 0},
            "timing": {"total_seconds": time.perf_counter() - t0, "encode_seconds": t1 - t0, "forward_seconds": t2 - t1},
            "prefix_cache": cached,
            "fingerprint": self.backend.metadata["fingerprint"], "calibrated": cal is not None,
        }

    def _score_cached(self, document, ids, pos):
        """Runs on the worker thread. Reuses the document's KV state if cached, else prefills it from the fixed
        instructions and caches it; then reads the answer only. Returns (logits, which prefix was reused)."""
        from .prompts import marked_prefix_lengths
        be = self.backend
        n_fixed, n_head = marked_prefix_lengths(be.tokenizer, document)
        key = tuple(ids[:n_head])
        if key in self._docs:
            self._docs.move_to_end(key)
            hit = "document"
        else:
            if self._fixed is None or self._fixed["ids"] != tuple(ids[:n_fixed]):
                self._fixed = be.prefill(ids[:n_fixed])
            self._docs[key] = be.prefill(ids[:n_head], base=self._fixed)
            while len(self._docs) > self.max_cached_docs:
                self._docs.popitem(last=False)
            self._answers.pop(key, None)
            hit = "instructions"
        last = self._answers.get(key)
        n = common_prefix_len(last["ids"], ids) if last else 0
        old = dict(zip(last["pos"], last["logits"])) if last else {}
        keep = [p for p in pos if p < n and p in old]
        if keep:
            # the answer shares its first sentences with the last one verified on this document (e.g. a rewrite that
            # changed a later sentence): their verdicts are unchanged, the rest is read from the first changed token
            todo = [p for p in pos if p not in keep]
            n = min(n, todo[0]) if todo else n
            if todo:
                fresh, full = be.score_positions_from(be.slice_prefix(last, n), ids, todo, keep=True)
            else:   # every verdict is unchanged; keep only the part of the state that matches this answer
                fresh, full = [], (last if tuple(last["ids"]) == tuple(ids) else be.slice_prefix(last, n))
            got = {**{p: old[p] for p in keep}, **dict(zip(todo, fresh))}
            logits = [got[p] for p in pos]
            hit = "answer prefix"
        else:
            logits, full = be.score_positions_from(self._docs[key], ids, pos, keep=True)
        self._answers[key] = {**full, "pos": list(pos), "logits": logits}
        return logits, hit

    # ------------------------------------------------------------------ compatible: /v1/systemone
    def systemone(self, req):
        served = compat.resolve_model(req.model, self.name)
        t0 = time.perf_counter()
        tok = self.backend.tokenizer
        rendered = {k: compat.render(tok, req.state, q) for k, q in req.questions.items()}
        keys = list(rendered)
        prompts = [self.backend.encode(rendered[k][0]) for k in keys]
        logits, timing = self._run(self.backend.score_shared, prompts, [rendered[k][1] for k in keys])
        answers = {k: compat.build_answer(req.questions[k], rendered[k][2], softmax(lg)) for k, lg in zip(keys, logits)}
        return {
            "model": served, "answers": answers,
            "usage": {"input_tokens": timing["prefix_tokens"] + timing["suffix_tokens"], "output_tokens": 0},
            "x_groundone": {"timing": {**timing, "total_seconds": time.perf_counter() - t0},
                            "fingerprint": self.backend.metadata["fingerprint"],
                            "note": "Generic questions are answered outside GroundOne's specialisation (groundedness)."},
        }

    # ------------------------------------------------------------------ batch prediction (evaluation, calibration)
    def predict(self, items, temperature=True, progress=None):
        """items: dicts with doc, sentences, idx, qtype. Returns list of (raw logits, probabilities).

        Items sharing (doc, sentences) are scored with the shared prefix; single-question groups are batched together.
        """
        tok = self.backend.tokenizer
        groups = defaultdict(list)
        for n, it in enumerate(items):
            groups[(it["doc"], tuple(it["sentences"]))].append(n)
        out = [None] * len(items)
        singles = [g[0] for g in groups.values() if len(g) == 1]
        multis = [g for g in groups.values() if len(g) > 1]
        done = 0
        for start in range(0, len(singles), 256):
            idx = singles[start:start + 256]
            prompts = [self.backend.encode(render(tok, items[n]["doc"], items[n]["sentences"], items[n]["idx"], items[n]["qtype"])) for n in idx]
            lgs = self._run(self.backend.score_many, prompts, [letters(items[n]["qtype"]) for n in idx])
            for n, lg in zip(idx, lgs):
                out[n] = lg
            done += len(idx)
            if progress:
                progress(done, len(items))
        for g in multis:
            prompts = [self.backend.encode(render(tok, items[n]["doc"], items[n]["sentences"], items[n]["idx"], items[n]["qtype"])) for n in g]
            lgs, _ = self._run(self.backend.score_shared, prompts, [letters(items[n]["qtype"]) for n in g])
            for n, lg in zip(g, lgs):
                out[n] = lg
            done += len(g)
            if progress and done % 500 < len(g):
                progress(done, len(items))
        return [(lg, self._probs(it["qtype"], lg, len(it["sentences"]) > 1) if temperature else softmax(lg))
                for lg, it in zip(out, items)]
