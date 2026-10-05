"""Thread-safe long-lived service around the MLX backend.

All model work runs on ONE worker thread that lives as long as the process: web servers call from short-lived pool
threads, and MLX/Metal contexts must not hop threads (lesson from LightningRoute and Rizzo-Flow). Requests are
serialised by a lock; parallelism is *inside* a request (K questions in one batched pass).
"""
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

from . import compat
from .calibration import Calibration, softmax
from .prompts import ANSWER_NAMES, letters, render
from .text import split_sentences


class Engine:
    def __init__(self, backend, calibration_path=None):
        self.backend = backend
        self.calibration = (Calibration.load(calibration_path, backend.metadata["fingerprint"])
                            if calibration_path else None)
        self._lock = Lock()
        self._worker = ThreadPoolExecutor(max_workers=1, thread_name_prefix="groundone-mlx")

    @classmethod
    def load(cls, size=None, adapter=None, calibration=None):
        from .backend import Backend
        from .config import resolve_model
        base, adir, name = resolve_model(size, adapter)
        ex = ThreadPoolExecutor(max_workers=1, thread_name_prefix="groundone-mlx")
        backend = ex.submit(Backend, base, adir, name).result()  # load on the same thread that will run inference
        eng = cls(backend, calibration)
        eng._worker.shutdown(wait=True)
        eng._worker = ex
        return eng

    @property
    def name(self):
        return self.backend.metadata["name"]

    def _t(self, qtype):
        return self.calibration.t(qtype) if self.calibration else 1.0

    def _run(self, fn, *args):
        with self._lock:
            return self._worker.submit(fn, *args).result()

    # ------------------------------------------------------------------ native: /v1/verify
    def verify(self, req):
        t0 = time.perf_counter()
        sentences = req.sentences or [s for _, _, s in split_sentences(req.answer)]
        if not sentences:
            raise ValueError("The answer contains no sentence")
        tok = self.backend.tokenizer
        jobs = [(i, q) for i in range(len(sentences)) for q in req.questions]
        prompts = [self.backend.encode(render(tok, req.document, sentences, i, q)) for i, q in jobs]
        t1 = time.perf_counter()
        logits, timing = self._run(self.backend.score_shared, prompts, [letters(q) for _, q in jobs])
        res = [{"index": i, "text": s, "answers": {}, "labels": {}} for i, s in enumerate(sentences)]
        for (i, q), lg in zip(jobs, logits):
            ps = softmax(lg, self._t(q))
            names = ANSWER_NAMES[q]
            res[i]["answers"][q] = dict(zip(names, ps))
            res[i]["labels"][q] = names[max(range(len(ps)), key=ps.__getitem__)]
        for r in res:
            sup = r["answers"].get("sup")
            r["p_supported"] = sup["supported"] if sup else None
            r["flagged"] = (r["p_supported"] < req.threshold) if sup else None
        return {
            "model": self.name, "sentences": res, "n_decisions": len(jobs),
            "usage": {"input_tokens": timing["prefix_tokens"] + timing["suffix_tokens"], "output_tokens": 0},
            "timing": {"total_seconds": time.perf_counter() - t0, "encode_seconds": t1 - t0,
                       "prefill_seconds": timing["prefill_seconds"], "batch_seconds": timing["batch_seconds"]},
            "fingerprint": self.backend.metadata["fingerprint"], "calibrated": self.calibration is not None,
        }

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
        return [(lg, softmax(lg, self._t(it["qtype"]) if temperature else 1.0)) for lg, it in zip(out, items)]
