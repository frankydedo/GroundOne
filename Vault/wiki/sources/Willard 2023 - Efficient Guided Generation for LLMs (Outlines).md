---
type: source
author: "Brandon T. Willard, Rémi Louf"
date: 2023
venue: "arXiv preprint 2307.09702 (Normal Computing)"
url: "https://arxiv.org/abs/2307.09702"
tags: [source, paper, constrained-decoding, guided-generation, structured-output, regex, cfg, outlines, llm]
---
# Willard 2023 – Efficient Guided Generation for Large Language Models (Outlines)

**Raw file**: `raw/Willard 2023 - Efficient Guided Generation for LLMs (Outlines)_ingested.pdf`

## Overview
Guided (constrained) generation forces an LLM's output to match a **regular expression** or a **context-free grammar** (JSON, Python, SQL…). The usual approach masks invalid tokens at every step by scanning the whole vocabulary and partially re-matching the output so far, which costs O(N) per token for a vocabulary of size N (§1, §2.2). The paper recasts regex matching as transitions of a **finite-state machine (FSM)** and **pre-indexes the vocabulary** by FSM state. The set of allowed next tokens then becomes a hash-map lookup, O(1) on average (§3). It extends the idea to LALR(1) parsers via pushdown automata (§4) and is implemented in the open-source library **Outlines**.

## Key Insights
1. **Masking formalism (§2.2, Algorithm 2).** A boolean mask $m$ over the vocabulary turns the next-token distribution into a conditional distribution with restricted support: $\tilde\alpha = m \odot \alpha$, then sample from it. Any constraint expressible as "which tokens may come next" fits this form.
2. **FSM index (§3, Algorithms 3–4).** For every vocabulary string and every FSM state it could start in, precompute the state sequence it would traverse. This builds a map σ: state → allowed tokens. At generation time, track the FSM state and look up σ. Construction is a one-off cost outside the sampling loop.
3. **Examples (§3.1).** With GPT-2 medium, unguided generation answers "In what year was Noam Chomsky born?" with rambling text; the regex `\s*19[0-9]{2}` forces "1952". Similar examples are given for yes/no answers and IP addresses.
4. **Speed (§3.2).** Against the Guidance library, which re-matches from the start and scans the 50,257-token vocabulary at each step, Outlines' cost stays flat as the number of generated tokens grows, while Guidance's grows. This is a single-sample timing on one prompt, not a broad benchmark.
5. **Grammars (§4).** Pushdown-automaton states combined with per-terminal FSMs and a trie index handle CFGs. A naively built index for a Python grammar takes about 50 MB (§5).
6. **Discussion (§5).** The authors suggest using the index during training to spare the model from learning syntax, and **measuring the discrepancy between masked and raw logits** as an evaluation tool.

## Relevance to GroundOne
- **GroundOne's readout is constrained decoding of length one.** Restricting the softmax at each " Verdict:" marker to the logits of "A", "B" and "C" is exactly Willard's Algorithm 2 with a fixed mask of three tokens and no sampling. No FSM is needed because the "grammar" is one token from a closed set. This is why GroundOne has 0 % format failures by construction. See [[Letter-Token Readout]] and [[Constrained Decoding]].
- **Control B2 is Willard's suggested measurement (§5).** B2 compares the masked decision (readout) with the unmasked argmax (generated token) on the same logits. The gap is +0.25 three-way for the 0.5B and +0.07 for the 3B on T1. The masked tokens hold only about 4–5 % of the probability mass at the markers.
- **Limitation of the judge baselines.** The generative judges were run *without* grammar-constrained decoding, to keep the same protocol for B0a, B0b and B0d. The 0.5B judges therefore fail on format: 23 % for terse, 97 % for verbose, and 24 % / 31 % for the B0d logit / verbal variants. With an Outlines-style regex or JSON constraint these failure rates would drop, likely to near zero. Accuracy and calibration would not necessarily improve, because the model's judgement is unchanged. Decoding could also get slightly slower or faster depending on the implementation. The thesis states this as a limitation; a constrained run of the terse 0.5B judge would quantify how much of its 0.233 three-way is format and how much is judgement.
- **Speed is not the issue here.** Masking keeps the autoregressive decode loop. A constrained judge still generates K verdicts (or a JSON object) token by token, so GroundOne's latency advantage (≈ 2× over terse, ≈ 6× over verbose at K ≥ 14) is not affected by constraining the judges' format. See [[Prefill and Decode]].

## Links
- Concepts: [[Constrained Decoding]], [[Letter-Token Readout]], [[LLM-as-a-Judge]], [[System One Models]]
- Related sources: [[Wang 2024 - My Answer is C (first-token probabilities vs text answers)]], [[Zheng 2023 - Judging LLM-as-a-Judge]] (format failures of judges)
- Thesis context: [[GroundOne]], [[Jev Input and Output Format]], [[Function Calling]]
