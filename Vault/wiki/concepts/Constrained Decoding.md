---
type: concept
tags: [constrained-decoding, guided-generation, structured-output, llm-as-a-judge, format-failures, groundone]
---
# Constrained Decoding

## Definition
**Constrained (guided) decoding** restricts which tokens an LLM may emit at each generation step, so that the output is guaranteed to match a format: a fixed set of labels, a regular expression, a JSON schema or a context-free grammar. At each step a boolean mask over the vocabulary sets the logits of disallowed tokens to −∞ before the argmax or sampling ([[Willard 2023 - Efficient Guided Generation for LLMs (Outlines)|Willard 2023]] §2.2, Algorithm 2).

**In plain words:** the model still writes token by token, but any token that would break the required format is forbidden. The output always parses. The model's judgement is not improved; it is only kept inside the allowed answers.

## How it is implemented
- **Naive masking.** At each step, scan the whole vocabulary (~10⁴–10⁵ tokens) and check each candidate against the constraint, re-matching the text generated so far. This costs O(N) per token, plus a cost that grows with the output length.
- **FSM indexing (Outlines).** Compile the regex to a finite-state machine and precompute, for every FSM state, the set of vocabulary tokens that keep the match alive. At generation time, track the state and look up the mask in O(1) on average (Willard §3). Grammars (JSON, Python, SQL) use pushdown automata with a trie index (Willard §4); an index for a Python grammar took about 50 MB.
- **Degenerate case: one step, closed label set.** If the answer is a single token from a fixed set, the mask is constant and there is no state to track. This is a **letter-token readout** ([[Letter-Token Readout]]).

## Why it matters for LLM judges
- Generative judges must emit a parseable verdict. Small models often do not: they echo the input, add preambles, drop labels or truncate JSON. Format failures then count as errors or need lenient parsing that can itself bias results. Example: in GroundOne's B0d-verbal 0.5B, tied unlabelled vectors resolved to "A" inflated macro from 0.081 to 0.234.
- [[Zheng 2023 - Judging LLM-as-a-Judge|Zheng 2023]] report up to 3.8 % wrong-format outputs even for large API judges (Table 2); [[Wang 2024 - My Answer is C (first-token probabilities vs text answers)|Wang 2024]] document preambles, hedges and refusals in instruction-tuned models.
- Constraining the format removes these failures, but **not the decode cost**. A constrained judge still generates its verdicts, or a whole JSON object, autoregressively, so its latency profile is unchanged ([[Prefill and Decode]]). It also does not change what the model believes. If the unconstrained model wanted to write a preamble, the constrained one is forced into a letter that may reflect a weak preference, the same tension Wang describe between first-token and text answers.

## GroundOne
- **The readout is constrained decoding of length one.** At each " Verdict:" marker the softmax is taken over the logits of A/B/C only. Format failures are therefore impossible (0 % in every run), and no tokens are generated. The **B2** control measures what happens without the mask on the same logits. The 0.5B emits " A", " ", "1", " The"…: 24.7 % format failures, and three-way accuracy drops 0.769 → 0.521. The 3B shows 1.2 % failures (0.832 → 0.761). Willard §5 suggest exactly this masked-vs-raw comparison as an evaluation tool.
- **The judge baselines were run without constraints**, to keep one protocol across B0a/B0b/B0d. The 0.5B judges fail on format at high rates:

| Judge (0.5B, latency subset) | Format failures | Three-way (failures counted wrong) |
| --- | --- | --- |
| Terse (B0a) | 23 % | 0.233 |
| Verbose (B0b) | 97 % | 0.017 |
| Equal-output, logits (B0d-logit) | 23.5 % | 0.234 |
| Equal-output, verbalised JSON (B0d-verbal) | 30.9 % | 0.234 (0.081 strict) |

  The 3B judges have 0–7.6 % failures, so this caveat matters mainly for the 0.5B.
- **Limitation, as stated in the thesis notes.** "Grammar-constrained decoding was not used, so that the protocol stays the same as B0a/B0b. This is a limitation for the 0.5B failure rates." The low 0.5B judge scores mix *inability to follow the format* with *inability to judge*.
- **What a constrained run would show (not run).** A regex such as `^([ABC]\n){K}$` for the terse judge, or a JSON schema for B0d, would bring format failures to about 0. The judges' accuracy would probably still sit far below GroundOne: the 3B judges, which rarely fail on format, reach only 0.39–0.41 three-way against 0.900. Latency at K ≥ 14 would stay about 2× (terse) to 6× (verbose) above GroundOne. Running it would turn the limitation into a measured result. Outlines supports MLX models, but this was not checked in the project environment.

## Links
- Sources: [[Willard 2023 - Efficient Guided Generation for LLMs (Outlines)]], [[Wang 2024 - My Answer is C (first-token probabilities vs text answers)]], [[Zheng 2023 - Judging LLM-as-a-Judge]]
- Concepts: [[Letter-Token Readout]], [[LLM-as-a-Judge]], [[Verbalised vs Logit Confidence]], [[System One Models]], [[Prefill and Decode]], [[Function Calling]], [[Jev Input and Output Format]]
- Thesis context: [[GroundOne]]
