"""Calibration per question type (plan §4.4, D6, D23).

A calibration file is bound to the model fingerprint (base model + adapter hash + prompt version): loading it on a
different model raises. Two maps are fitted on dev predictions by minimising NLL:
  temperature  softmax(logits / T)                  one T per key (v1 behaviour)
  affine       softmax(logits / T + b), b[0] = 0     T and a bias per answer letter (D23): also corrects a shifted decision
               boundary, which temperature alone cannot do (diagnosis of g1-05b-v1, analysis_2026-10-06.md §3.3)
Keys are a question type ("sup") or a question type in one prompt format ("sup@pair", "sup@multi": the format is known
at inference, K = 1 or K > 1). Lookup falls back from "q@format" to "q" to no calibration.
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


def affine_probs(logits, t=1.0, bias=None):
    bias = bias or [0.0] * len(logits)
    return softmax([x / t + b for x, b in zip(logits, bias)])


def affine_nll(rows, t, bias):
    return -sum(math.log(max(affine_probs(l, t, bias)[g], 1e-12)) for l, g in rows) / max(len(rows), 1)


def fit_affine(rows):
    """T and biases (first letter's bias fixed at 0) minimising dev NLL. Starts from the fitted temperature."""
    import numpy as np
    from scipy.optimize import minimize
    n = len(rows[0][0])
    L = np.array([l for l, _ in rows], float)
    G = np.array([g for _, g in rows])

    def f(x):
        z = L * np.exp(-x[0]) + np.concatenate([[0.0], x[1:]])
        z -= z.max(1, keepdims=True)
        return float(-(z[np.arange(len(G)), G] - np.log(np.exp(z).sum(1))).mean())

    x0 = np.concatenate([[math.log(fit_temperature(rows))], np.zeros(n - 1)])
    x = minimize(f, x0, method="L-BFGS-B", bounds=[(math.log(0.05), math.log(50.0))] + [(-20, 20)] * (n - 1)).x
    return float(math.exp(x[0])), [0.0] + [float(v) for v in x[1:]]


class Calibration:
    def __init__(self, temperatures, fingerprint, meta=None, biases=None):
        self.temperatures, self.fingerprint, self.meta = dict(temperatures), fingerprint, meta or {}
        self.biases = dict(biases or {})

    def key(self, qtype, multi=None):
        if multi is not None and f"{qtype}@{'multi' if multi else 'pair'}" in self.temperatures:
            return f"{qtype}@{'multi' if multi else 'pair'}"
        return qtype

    def t(self, qtype, multi=None):
        return self.temperatures.get(self.key(qtype, multi), 1.0)

    def probs(self, qtype, logits, multi=None):
        k = self.key(qtype, multi)
        return affine_probs(logits, self.temperatures.get(k, 1.0), self.biases.get(k))

    def save(self, path):
        Path(path).write_text(json.dumps({"fingerprint": self.fingerprint, "temperatures": self.temperatures,
                                          "biases": self.biases, "meta": self.meta}, indent=2))

    @classmethod
    def load(cls, path, fingerprint=None):
        d = json.loads(Path(path).read_text())
        if fingerprint and d["fingerprint"] != fingerprint:
            raise ValueError(f"Calibration {path} was fitted for model {d['fingerprint']}, not {fingerprint}")
        return cls(d["temperatures"], d["fingerprint"], d.get("meta"), d.get("biases"))
