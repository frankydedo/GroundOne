---
type: source
author: "Apple Inc."
date: 2026
venue: "Apple Developer Documentation, Natural Language framework, NLTokenizer class (documentation JSON; retrieved 2026-10-18)"
url: "https://developer.apple.com/documentation/naturallanguage/nltokenizer"
tags: [source, apple, natural-language, sentence-segmentation, tokenization, train-inference-parity]
---
# Apple 2026 – NLTokenizer documentation

**Raw file**: `raw/demo/Apple 2026 - NLTokenizer documentation_ingested.md`

## Overview
`NLTokenizer` is "a tokenizer that segments natural language text into semantic units". **Very short page**: one overview paragraph, a threading note and three topic titles. It does not describe the segmentation algorithm, abbreviation handling or language coverage.

## Key Insights
- Units are those of `NLTokenUnit`: **word, sentence, paragraph or document**. The caller sets the unit, assigns a string and enumerates token ranges with `enumerateTokensInRange:usingBlock:`.
- Use an instance on **one thread or dispatch queue at a time** (serialise calls or create one instance per thread/queue).
- Topics (not extracted): Creating a tokenizer, Configuring a tokenizer, Enumerating the tokens; further detail is in the "Tokenizing natural language text" article (not ingested).

## Relevance to GroundOne
- **Train/inference parity risk.** GroundOne was trained and evaluated on sentences produced by `data/segment.py`: split on line breaks, then **pysbd** (`language="en", clean=False, char_span=True`), then list-marker stripping and the "checkable content" rule. The sentence boundaries decide where the " Verdict:" markers go, hence K and which spans get a verdict. NLTokenizer's sentence unit uses an undocumented, different algorithm, so the app cannot assume equal output.
- **Options for the demo** ([[Demo Application]]): (a) a Swift port of pysbd's rules (it is itself a port of the Ruby Pragmatic Segmenter, so the rules are portable regex logic) plus the same pre/post-processing; (b) NLTokenizer with a measured agreement rate against pysbd on the dev and frozen-test answers, reported in the thesis; (c) both, with NLTokenizer as a fallback. Option (a), validated by exact-match tests on the dataset answers and pysbd's Golden Rules, is the only one that preserves "training text == inference text"; option (b) is acceptable only with the mismatch rate stated.
- The character-range API is convenient for mapping verdicts back onto the original text for highlighting, as `char_span=True` does in Python.

## Links
- Concepts: [[Demo Application]], [[Demo Runtime Choice]], [[On-Device Inference]]
- Related: [[Sadvilkar - pySBD, rule-based sentence boundary detection (GitHub README)]], [[Apple 2026 - NLEmbedding documentation]], [[Swift.org 2026 - Platform support]]
