> **Historical report (2026-10-05).** It documents the feasibility tests that motivated the project. Several choices described here were later superseded: the four-question design (D15 → D20), ANLI and MiniCheck as data (→ D21), and the batched-question readout (→ design b, D22). Current state: `implementation_plan.md` §2.1 and `thesis_notes.md`.

# Phase 0 report: feasibility of GroundOne

Run on the night of 2026-10-05, 01:00–03:00. Hardware: M4 MacBook Pro, 16 GB unified memory, MLX 0.29.3 / mlx-lm 0.29.1, PyTorch 2.11 (MPS).
Code, logs and raw outputs: `Project/phase0/` (`scripts/`, `logs/`, `results/`). No training of GroundOne was done; everything is zero-shot or a short probe.

> **Update (same day): Phase 0b, at the end of this report, supersedes the speed conclusion below.** With batched scoring the System One is ≈2× faster than a terse and ≈6× faster than a verbose generative judge at K = 24. Read §1–§7 as the record of the first test.

**Recommendation (Phase 0): GO on the task, but the thesis argument must change.** The data exist, the task is within reach, the small model has a lot of headroom and training fits in memory. However, the **speed advantage of the System One over a terse generative judge is essentially zero** on both model sizes, and **an off-the-shelf encoder (MiniCheck-RoBERTa) already matches the zero-shot 3B** at a fraction of its latency. The thesis cannot claim "System One is faster than an LLM judge" in general; see §7 for the options. This is the decision the author has to take before Phase 1.

---

## 1. Criteria at a glance

| # | Criterion | Result | Verdict |
| --- | --- | --- | --- |
| G1 | Datasets available, human labels, usable licences | All available (LLM-AggreFact after the author requested access). Licences: RAGTruth MIT, MiniCheck synthetic data MIT, ANLI CC-BY-NC 4.0, LLM-AggreFact CC-BY-ND 4.0 | ✅ PASS (non-commercial / no-derivatives terms are fine for a thesis) |
| G2 | Zero-shot 3B readout clearly above chance (BAcc ≥ ~0.60) | 0.760 on LLM-AggreFact, 0.713 RAGTruth sentences, 0.639 ANLI | ✅ PASS |
| G3 | Headroom for the 0.5B: best small encoder clearly above zero-shot 0.5B | MiniCheck-RoBERTa 0.759 vs 0.5B 0.595 on LLM-AggreFact (+16 pts); 0.782 vs 0.662 on RAGTruth sentences (+12 pts) | ✅ PASS for 0.5B. For 3B: no headroom vs encoders on LLM-AggreFact, some on RAGTruth sentences |
| G4 | Shared-prefix System One ≥ ~1.5× faster than a terse generative judge at K = 8 | 0.5B: 1.03× (1 000-token context), 0.91× (2 000). 3B: 1.11× and 1.03× | ❌ FAIL |
| G5 | LoRA training fits: 0.5B, and 3B at ≥ 1 024 tokens | Peak 2.1 GB (0.5B, 1 024 tok) … 5.9 GB (3B, 2 048 tok) | ✅ PASS on memory; **time** is the binding constraint (§6) |

---

## 2. What was run

| Step | What | Status |
| --- | --- | --- |
| Data | LLM-AggreFact (dev 30 420 / test 29 320), RAGTruth (17 790 responses), MiniCheck C2D+D2C (14 395), ANLI | done |
| Zero-shot readout (B1) | Qwen2.5-0.5B and 3B (MLX 8-bit), P(supported) = softmax over the logits of "A"/"B", no generation | done on all 1 780 evaluation items |
| Encoders (B4) | MiniCheck-RoBERTa-L on all items; HHEM-2.1-open and MiniCheck-DeBERTa-v3-L on a random stratified subsample of 150 per set; MiniCheck-Flan-T5-L | Flan-T5 **killed by the memory guard** (free memory < 2 GB); not run |
| Speed | System One with shared prefix vs without, vs terse generative judge; K = 1, 3, 8 sentences; context 500/1 000/2 000 tokens; 3 repetitions | done for 0.5B and 3B |
| Training probe | 30 LoRA steps, all linear layers, gradient checkpointing, restricted A/B cross-entropy loss, at 1 024 and 2 048 tokens | done for 0.5B and 3B |
| Not run (by decision) | Qwen2.5-7B (published leaderboard number used instead), Rizzo-Flow (to be done in daytime) | — |

Evaluation sample (`phase0/data/eval_samples.parquet`):

| Set | Items | % supported | Notes |
| --- | --- | --- | --- |
| LLM-AggreFact | 550 | 59.8 % | 50 per sub-dataset (11), test split, documents ≤ 8 000 characters (excludes 39 % of ClaimVerify and 32 % of Wice; < 10 % elsewhere) |
| RAGTruth sentences | 630 (100 responses, mean K = 6.3) | 87.5 % | test split, QA + Summary, half hallucinated / half clean responses; label = unsupported if the sentence overlaps any annotated span |
| RAGTruth responses | 300 | 50 % | whole response as the claim (not a fair input for sentence-level encoders) |
| ANLI dev | 300 | 29.7 % | 100 per round; entailment → supported |

---

## 3. Accuracy (balanced accuracy at threshold 0.5)

### 3.1 Full evaluation sample (Qwen readout and MiniCheck-RoBERTa, same 1 780 items)

| Set | Qwen 0.5B zero-shot | Qwen 3B zero-shot | MiniCheck-RoBERTa |
| --- | --- | --- | --- |
| LLM-AggreFact (550) | 0.595 (AUROC 0.646) | **0.760** (0.828) | **0.759** (0.824) |
| RAGTruth sentences (630) | 0.662 (0.707) | 0.713 (0.782) | **0.782** (0.852) |
| ANLI (300) | 0.571 (0.582) | 0.639 (0.702) | **0.661** (0.782) |
| RAGTruth responses (300) | 0.530 | 0.603 | 0.653 |

### 3.2 All systems on the same random subsample (150 per set)

| Set | 0.5B | 3B | RoBERTa | HHEM | DeBERTa |
| --- | --- | --- | --- | --- | --- |
| LLM-AggreFact | 0.592 | **0.756** | **0.756** | 0.750 | 0.706 |
| RAGTruth sentences | 0.614 | 0.636 | **0.720** | 0.657 | 0.682 |
| ANLI | 0.576 | 0.681 | **0.704** | 0.575 | 0.665 |

Published reference (LLM-AggreFact leaderboard, full test set, not re-run): MiniCheck-FT5 75.0, Qwen2.5-7B-Instruct 72.8, HHEM 71.8, AlignScore 70.5, Qwen2.5-0.5B-Instruct 64.2.

Reading:
- Our numbers are on a filtered sample (short documents) and are probably optimistic compared with the full benchmark; the ranking, not the absolute level, is what matters here.
- Zero-shot 0.5B is weak everywhere: the specialisation claim has room (≈ 12–16 points to the encoders).
- Zero-shot 3B already ties the encoders on LLM-AggreFact, but not on RAGTruth sentences, which is the RAG setting of the thesis.
- In 100 % of items the most likely next token of both Qwen models was "A" or "B": the single-token readout format works without any training.

## 4. Calibration (ECE, 15 bins; lower is better)

| Set | 0.5B | 3B | RoBERTa | HHEM (150) |
| --- | --- | --- | --- | --- |
| LLM-AggreFact | 0.118 | 0.221 | 0.172 | 0.194 |
| RAGTruth sentences | 0.315 | 0.316 | 0.190 | 0.112 |
| ANLI | 0.231 | 0.249 | 0.178 | 0.273 |

Zero-shot Qwen probabilities are poorly calibrated (ECE 0.22–0.32 on the 3B), worse than the encoders. No temperature scaling was applied yet. This leaves a clear, measurable target for fine-tuning plus temperature scaling, and none of the published verifiers reports calibration.

## 5. Speed (end-to-end time for one answer of K sentences; median of 3)

| Model | Context | K | System One, shared prefix | System One, no sharing | Terse generative judge |
| --- | --- | --- | --- | --- | --- |
| 0.5B | 1 000 tok | 1 | 384 ms | 376 ms | 373 ms |
| 0.5B | 1 000 tok | 8 | 572 ms | 3 269 ms | 589 ms |
| 0.5B | 2 000 tok | 8 | 958 ms | 6 198 ms | 872 ms |
| 3B | 1 000 tok | 1 | 2 249 ms | 2 216 ms | 2 243 ms |
| 3B | 1 000 tok | 8 | 3 163 ms | 19 266 ms | 3 524 ms |
| 3B | 2 000 tok | 8 | 5 347 ms | 36 093 ms | 5 512 ms |

- Decode cost: 5.9 ms/token (0.5B), 31.8 ms/token (3B). The terse judge wrote ~4–5 tokens per sentence (35–39 tokens for K = 8), so its decoding costs only ~0.2 s (0.5B) to ~1.2 s (3B) on top of the same prefill.
- **Prefill dominates**: reading a 2 000-token context costs ~0.74 s (0.5B) and ~4.3 s (3B) for every method.
- Shared-prefix scoring is exact: the probabilities equal those of separate passes (max |Δp| = 0.000).
- Prefix sharing is essential (5–7× faster than separate passes at K = 8), but the terse generative judge gets the same benefit for free, because it also reads the context once.
- Not measured: a judge that writes a rationale before each verdict. Using the measured decode speed, 60 rationale tokens per sentence at K = 8 would add ~2.8 s (0.5B) or ~15 s (3B), i.e. roughly 3–4× slower than the System One. This is an **estimate** and must be measured before it is claimed.
- Not measured: how often the generative judge breaks the output format (the generated text was not saved correctly; to fix in Phase 2).
- Encoder latency per item (p50): RoBERTa 185 ms, HHEM 120 ms, versus 200 ms (0.5B) and 1.2 s (3B) for the Qwen readout on LLM-AggreFact items.

## 6. Training probe (30 steps, LoRA r = 16 on all linear layers of all blocks, gradient checkpointing, batch 1)

| Model | Example length | Trainable params | Peak memory | Time per step |
| --- | --- | --- | --- | --- |
| 0.5B | ~970 tokens | 8.8 M | 2.06 GB | 1.55 s |
| 0.5B | ~1 990 tokens | 8.8 M | 2.62 GB | 3.71 s |
| 3B | ~970 tokens | 29.9 M | 5.12 GB | 7.70 s |
| 3B | ~1 990 tokens | 29.9 M | 5.92 GB | 16.53 s |

- Memory is not a problem, even for the 3B at 2 048 tokens (the run never got below 4.2 GB free).
- Time is. MiniCheck training examples are short (median 286 tokens, p90 382; ANLI ~160). At the measured cost per token, one epoch of the full MiniCheck recipe (~35K examples) takes roughly **3–4 hours on the 0.5B** and **~17 hours on the 3B** (estimates). The 3B must therefore be trained on a subset (~10K examples ≈ one night) or for less than one epoch.
- The loss was noisy at learning rate 1e-4 (e.g. 7.7 at step 10 on the 3B): the learning rate needs tuning in Phase 3.
- The standard `mlx_lm.lora` data pipeline is incompatible with the installed `transformers` 5.x; the probe used a small custom MLX training loop with the restricted A/B loss, which is what the plan needs anyway.

## 7. What this means for the thesis (decision for the author)

What holds:
1. **Specialisation is the strongest available claim.** The 0.5B is ~16 points below the encoders zero-shot and is cheap to train (hours). If fine-tuning closes most of that gap, a 0.5B System One that matches a 3B/7B zero-shot judge is a clean result.
2. **Calibration is open territory.** Zero-shot Qwen is badly calibrated; fine-tuning plus temperature scaling can be measured against both LLM judges and encoders, and the published verifiers do not report it.
3. **Against rationale-writing judges** (the common LLM-as-a-judge practice) the System One should be several times faster; to be measured.

What does not hold:
4. **"System One is faster than an LLM judge"** is false against a terse generative judge of the same size: the difference is within ±10 %. The thesis must state this.
5. **"LLM-based verification beats encoders"** is not supported zero-shot: MiniCheck-RoBERTa is as accurate as the 3B on LLM-AggreFact, better on RAGTruth sentences, and ~6× faster.

Options for the framing (to decide together):
- **A. Honest decomposition (recommended).** Keep the plan; the thesis question becomes "where does a specialised System One win, and where not". Report the null speed result against terse judges, the gain against rationale judges, the specialisation gain of the 0.5B, and calibration. The encoder comparison becomes RQ5 with a likely negative answer, which is fine if stated.
- **B. Focus on the 0.5B as the product.** Make the fine-tuned 0.5B the GroundOne model; the 3B becomes a zero-shot reference only. This saves ~17 h of training and puts all effort into accuracy and calibration of the small model.
- **C. Add a capability encoders lack** (the policy-conditioning experiment E2), to give the LLM-based verifier a reason to exist beyond speed. Costs extra time; only if A/B leave room.

A and B combine well. C is optional.

## 8. Limitations of this Phase 0

- Small samples (150–630 items per set); differences under ~4–5 points are within noise.
- Documents longer than 8 000 characters were excluded, which biases LLM-AggreFact towards easier items.
- A single zero-shot prompt per model; no prompt tuning.
- Encoders run with my own chunking (≈ 400 words, max over chunks) on MPS, not with the official MiniCheck package; numbers can differ slightly from the papers.
- Speed: 3 repetitions per configuration, no thermal control (fans were active), single answer set.
- The generative judge's outputs were not saved, so its accuracy and format-failure rate are unknown.
- Flan-T5 MiniCheck was not evaluated (memory guard).

## 9. Incidents during the night

- An earlier attempt froze the Mac before any model was loaded (swap > 30 GB). The most likely suspect is a crash-looping `watchman` service (31 crash reports in the same window), not a Phase 0 job; not proven. All later jobs ran under a memory guard (`phase0/scripts/watchdog.py`) that kills a job when free memory drops below 2 GB; it was triggered once (MiniCheck-Flan-T5). Swap never grew by more than ~3 GB.
- Bugs fixed during the run: an incompatible HHEM / `transformers` version (separate environment), a non-random subsample for HHEM/DeBERTa (rerun with a stratified random sample; the earlier numbers were discarded), two failed attempts of the training probe (data format; replaced by a custom loop).

---

# Phase 0b (2026-10-05, 09:00–10:22): re-test centred on the System One's strengths

Code: `phase0/scripts/s1engine.py`, `06_speed_batched.py`, `07_flex.py`, `08_gen_judges.py`. Same models (untrained Qwen2.5-0.5B/3B in System One mode), same machine, memory guard on (never triggered; min free memory 2.8 GB).

## B1. Batched System One vs terse and verbose generative judges

Engine change: the shared prefix is prefilled once, its KV cache is replicated K times, and all K short suffixes ("Question about sentence [3]: …") run in **one batched pass**. Probabilities are identical to scoring each question separately (max |Δp| = 0.00000). K = 24 means 8 sentences × 3 questions (supported? contradicted? mentioned at all?). Median of 3 runs (verbose: 2 runs, 1,000-token context only).

**3B**
| Context | K | System One | Terse judge | Verbose judge | Gain vs terse | Gain vs verbose |
| --- | --- | --- | --- | --- | --- | --- |
| 1,000 | 1 | 2.20 s | 2.20 s | 2.75 s | 1.0× | 1.2× |
| 1,000 | 3 | 2.36 s | 2.70 s | 5.65 s | 1.1× | 2.4× |
| 1,000 | 8 | 2.77 s | 3.85 s | 9.23 s | 1.4× | 3.3× |
| 1,000 | 24 | 3.70 s | 7.15 s | 21.4 s | **1.9×** | **5.8×** |
| 500 | 24 | 2.69 s | 4.53 s | – | 1.7× | – |
| 2,000 | 24 | 5.81 s | 9.13 s | – | 1.6× | – |

**0.5B**
| Context | K | System One | Terse judge | Verbose judge | Gain vs terse | Gain vs verbose |
| --- | --- | --- | --- | --- | --- | --- |
| 1,000 | 8 | 0.45 s | 0.65 s | 1.35 s | 1.4× | 3.0× |
| 1,000 | 24 | 0.60 s | 1.26 s | 3.47 s | **2.1×** | **5.7×** |
| 500 | 24 | 0.43 s | 1.12 s | – | 2.6× | – |
| 2,000 | 24 | 1.03 s | 1.06 s | – | 1.0× | – |

- The gain **grows with K** on both sizes, as expected, and shrinks with context length (prefill is shared by all methods).
- The verbose judge wrote ~20–31 tokens per decision, not the 60 assumed in the plan, so the gains vs verbose are lower than estimated but still 3–6× at K ≥ 8.
- **The speed comparison is conservative.** The generative judges did not always do the whole job: at K = 24 the 3B terse judge sometimes answered only 8 of 24 items, and the 0.5B often copied the format template ("<item id>: no"). Shorter outputs make them faster than a correct judge would be.

Criteria: G4b (≥ 1.5× vs terse at K = 24) ✅ for 3B at all context lengths and for 0.5B up to 1,000 tokens; ❌ for 0.5B at 2,000 tokens. G4b (≥ 3× vs verbose at K = 8) ✅ 3B (3.3×), borderline 0.5B (3.0×). G4c (gain grows with K) ✅.

## B2. Accuracy and format reliability of the generative judges (100 RAGTruth responses, 630 sentences)

| Judge | Format failures | BAcc | Time per response (p50) |
| --- | --- | --- | --- |
| 0.5B terse | 2.4 % | 0.516 | 0.41 s |
| 0.5B verbose | **97.3 %** | 0.506 | 1.26 s |
| 3B terse | 0.0 % | 0.673 | 2.07 s |
| 3B verbose | 6.5 % | 0.645 | 7.20 s |
| *System One readout, same 630 sentences (Phase 0, one sentence per prompt)* | *0 % by construction* | *0.5B 0.662 · 3B 0.713* | – |

- The System One readout is **at least as accurate** as both generative judges of the same size, and much more accurate on the 0.5B, which cannot follow the generative format (97 % failures in verbose mode). Asking for a rationale did not improve accuracy on the 3B (0.645 vs 0.673).
- Caveat: the prompts differ (one sentence per prompt for the readout, all sentences in one prompt for the judges).

## B3. Flexibility probe (zero-shot, existing labels only)

Class counts: ANLI 89 supported / 93 contradicted / 118 not mentioned; RAGTruth sentences 551 / 18 / 61 (too few contradictions for a reliable three-way estimate).

| | 0.5B ANLI | 0.5B RAGTruth | 3B ANLI | 3B RAGTruth | MiniCheck ANLI | MiniCheck RAGTruth |
| --- | --- | --- | --- | --- | --- | --- |
| Three-way macro recall (chance 0.33) | 0.341 | 0.301 | **0.465** | **0.486** | n/a (cannot express it) | n/a |
| Strict rule, BAcc | 0.429 | 0.498 | 0.495 | 0.515 | **0.661** | **0.782** |
| Lenient rule, BAcc | 0.484 | 0.600 | 0.494 | 0.518 | 0.522 | **0.750** |

- **Zero-shot, the models do not follow rules written in the prompt.** Under both rule prompts the 3B answers "error" almost always (mean P(acceptable) ≈ 0.01), so its balanced accuracy is ≈ 0.5. This is probably partly a prompt problem (the rule prompts invert the meaning of the letters compared with the plain question), but zero-shot it is a failure.
- The 3B handles the three-way question above chance (0.47–0.49), the 0.5B does not.
- MiniCheck on RAGTruth scores well on the lenient labels too (0.750) because contradictions are only 3 % of sentences there: strict and lenient labels almost coincide. **ANLI is the informative set for the rule test.**

Criterion G6 ❌ zero-shot (three-way borderline for the 3B only; rule-following absent). As planned, flexibility becomes a **training target**: GroundOne must be trained on the three-way format and on rule-conditioned examples (gold labels derivable from ANLI and RAGTruth), and the comparison with MiniCheck is made after training.

## Phase 0b conclusion

The System One's advantages are real but have to be stated precisely:
1. **Speed:** the gain over generative judges grows with the number of decisions per context: ~2× over a terse judge and ~6× over a verbose judge at K = 24, with exact (not approximate) probabilities. It is small at K ≤ 3 and on long contexts for the 0.5B.
2. **Reliability:** always exactly K valid answers; small generative judges break the format (up to 97 % failures) or skip items.
3. **Accuracy:** zero-shot readout ≥ generative judges of the same size on RAGTruth sentences.
4. **Flexibility:** not available zero-shot; it has to come from training. This makes it part of GroundOne's specialisation, and a fair test against MiniCheck after training.
