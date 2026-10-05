"""Temperature scaling per question type (plan §4.4, D6).

A calibration file is bound to the model fingerprint (base model + adapter hash + prompt version): loading it on a
different model raises. Fitting minimises NLL of softmax(logits / T) on dev predictions, one T per question type.
"""
import json
import math
from pathlib import Path


def softmax(xs, t=1.0):
    m = max(x / t for x in xs)
    e = [math.exp(x / t - m) for x in xs]
    s = sum(e)
    return [v / s for v in e]


def nll(rows, t):
    """rows: list of (logits, gold_index)."""
    return -sum(math.log(max(softmax(l, t)[g], 1e-12)) for l, g in rows) / max(len(rows), 1)


def fit_temperature(rows, lo=0.05, hi=20.0, iters=60):
    """Golden-section search on log T (NLL is unimodal in practice for temperature scaling)."""
    a, b = math.log(lo), math.log(hi)
    gr = (math.sqrt(5) - 1) / 2
    c, d = b - gr * (b - a), a + gr * (b - a)
    for _ in range(iters):
        if nll(rows, math.exp(c)) < nll(rows, math.exp(d)):
            b = d
        else:
            a = c
        c, d = b - gr * (b - a), a + gr * (b - a)
    return math.exp((a + b) / 2)


class Calibration:
    def __init__(self, temperatures, fingerprint, meta=None):
        self.temperatures, self.fingerprint, self.meta = dict(temperatures), fingerprint, meta or {}

    def t(self, qtype):
        return self.temperatures.get(qtype, 1.0)

    def save(self, path):
        Path(path).write_text(json.dumps({"fingerprint": self.fingerprint, "temperatures": self.temperatures,
                                          "meta": self.meta}, indent=2))

    @classmethod
    def load(cls, path, fingerprint=None):
        d = json.loads(Path(path).read_text())
        if fingerprint and d["fingerprint"] != fingerprint:
            raise ValueError(f"Calibration {path} was fitted for model {d['fingerprint']}, not {fingerprint}")
        return cls(d["temperatures"], d["fingerprint"], d.get("meta"))
