---
type: source
author: "Nipun Sadvilkar (and Mark Neumann for the paper)"
date: 2020
venue: "GitHub repository README, nipunsadvilkar/pySBD (MIT licence badge; paper at NLP-OSS @ EMNLP 2020, pp. 110-114; retrieved 2026-10-18)"
url: "https://github.com/nipunsadvilkar/pySBD"
tags: [source, sentence-segmentation, rule-based, nlp-tool, train-inference-parity, groundone-pipeline]
---
# Sadvilkar – pySBD: rule-based sentence boundary detection (README)

**Raw file**: `raw/demo/Sadvilkar - pySBD, rule-based sentence boundary detection (GitHub README)_ingested.md`

## Overview
pySBD ("python Sentence Boundary Disambiguation") is a rule-based sentence boundary detector that "works out-of-the-box". It is **a direct port of the Ruby gem Pragmatic Segmenter**. The accompanying short paper, "PySBD: Pragmatic Sentence Boundary Disambiguation" (Sadvilkar and Neumann, NLP-OSS workshop at EMNLP 2020), is already in the thesis bibliography as `sadvilkar2020pysbd`. The README is undated; the date above is the paper's.

## Key Insights
- **Coverage**: 22 languages. The paper abstract reports that pySBD passes **97.92% of the Golden Rule Set** exemplars for English, "an improvement of 25% over the next best open source Python tool". The Golden Rules are a language-specific set of sentence-boundary exemplars inherited from Pragmatic Segmenter.
- **API**: `pysbd.Segmenter(language="en", clean=False).segment(text)`; the example keeps "Jonas E. Smith." and "p. 55." intact. It can run as a spaCy pipeline component (`PySBDFactory`) or via spaCy entry points.
- Install with `pip install pysbd`; MIT licence (badge); contributions of mis-segmented texts are invited.
- The README does not document the `char_span` option used by GroundOne (known from the code, not from this source).

## Relevance to GroundOne
- **Part of the trained interface**: `data/segment.py` splits answers on line breaks, applies `pysbd.Segmenter(language="en", clean=False, char_span=True)`, strips list markers and applies the checkable-content rule. The resulting sentences set the " Verdict:" markers at training, evaluation and serving time, so the demo must reproduce them exactly ([[Demo Application]]).
- **Porting is feasible because it is rules, not a model**: pySBD is itself a port (Ruby to Python), so a Swift port of the same regex rules is a bounded task. Validation plan: exact-match tests of the Swift port against pysbd on every answer in train/dev/T1–T3 plus the Golden Rule exemplars; report any mismatch rate. Apple's NLTokenizer is the alternative with an unknown algorithm and therefore a parity risk.
- A third route, embedding Python (or a small sidecar) only for segmentation, guarantees parity but reintroduces Python into an app whose point is a single native process ([[Demo Runtime Choice]]); it is a reasonable fallback if the port slips past the deadline.

## Links
- Concepts: [[Demo Application]], [[Demo Runtime Choice]], [[Retrieval-Augmented Generation]]
- Related: [[Apple 2026 - NLTokenizer documentation]], [[Swift.org 2026 - Platform support]]
