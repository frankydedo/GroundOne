# Checkpoint 2: everything done so far and the results (2026-10-10)

Replaces `checkpoint_2026-10-08.md` as the current summary. Every number below comes from `outputs/results/*/metrics.json`. The full reasoning behind each result is in `thesis_notes.md`, decisions are in `implementation_plan.md` §3 (D1–D26), and the dataset is described in `dataset_plan.md` and the data card. The live results matrix is in `tracker.md`.

---

## 1. The question

Can a compact language model, specialised in one decision and used as a **System One**, verify RAG answers sentence by sentence better, faster and with more usable probabilities than generative judges and dedicated verifiers, on a 16 GB laptop? A System One runs one forward pass, reads the verdicts from answer-letter logits and generates no text.

- **The decision.** For each sentence of an answer, the retrieved document *supports* it, *contradicts* it, or *does not mention* it.
- **K** is the number of sentences, i.e. of decisions per answer. It is the variable on which System One and generative judges are compared.
- **Setting.** Fully local: Qwen2.5 0.5B and 3B, LoRA, MLX 8-bit, Apple M4 16 GB. Nothing leaves the machine.

## 2. What was done, in order

| Step | What | Key choice |
| --- | --- | --- |
| Feasibility (Phase 0/0b, Oct 5) | Zero-shot readout vs encoders and judges | Showed room for training. A speed advantage over judges exists only with batched multi-sentence scoring |
| Task (D20) | One three-way decision per sentence; binary score and strict/lenient policies derived from the 3 probabilities | Replaced a 4-question design that confused training |
| Dataset (D21) | Rebuilt from scratch; RAGTruth as the only training source; 3 test sets built, checked and frozen **before** training | Labels agree 98.75 % with LLM-AggreFact's independent labels; leakage check by group passes |
| Readout (D22) | Marker " Verdict:" after each sentence; all K verdicts read in **one pass**; output head only at the markers | Design (a), one question per sentence, kept as fallback |
| Training (D23) | GroundOne 0.5B on all 13,203 answers (5.5 h); 3B on 6,500 answers (12.25 h) | LoRA r16 on all linear layers, class-weighted loss over the 3 letters, best checkpoint on dev |
| Calibration (D24) | Temperature + per-class bias fitted on dev | Decisions use the raw output; probabilities are calibrated |
| Baselines | Word overlap; sentence-only classifier; untrained models (B1); terse and verbose judges (B0a/B0b); Rizzo-Flow 4B (B3); MiniCheck-RoBERTa and HHEM (B4) | Same frozen tests and metrics; subsamples for the slow systems |
| Latency | Seconds per answer vs K; 200 T1 answers, 50 per K band, in-process MLX | Claims only between MLX in-process systems |
| Equal-output judge (D25) | Judge that must return GroundOne's content (label + 3 probabilities): verbalised in JSON or read from logits; calibrated like GroundOne | Requested by the author for output parity |
| Bootstrap | 95 % CIs and paired tests, cluster resampling by source document | One claim tempered (T2 vs MiniCheck) |
| Control B2 | Same weights and pass, verdict = token the model would generate | Quantifies the value of the restricted readout |
| Energy | Joules per answer with powermetrics, net of idle | First measurement for the locality pillar |
| Seeds (D26) | Second 0.5B run. Seed 4321 collapsed and was stopped; seed 777 completed | The stopped run is disclosed, not hidden |
| Software | Package `groundone`: CLI, HTTP API (still design a), memory guard, figures, matrix, bootstrap | All long runs under the guard; no time limits |
| Thesis | Drafts of Ch. 3–6 and the summary; abstract v0.3.1 | Ch. 1, 2, 7, 8 pending |

## 3. Data

| Split | Source | Size | Decisions (sup / con / nm) |
| --- | --- | --- | --- |
| Train | RAGTruth train | 13,203 answers | 90,795 (79,898 / 4,039 / 6,858) |
| Dev | RAGTruth train, 10 % of sources | 1,468 answers | 9,996 |
| **T1** | RAGTruth test | 2,647 answers | 17,284 (15,745 / 584 / 955) |
| **T2** | LLM-AggreFact test (binary, evaluation only) | 29,320 pairs | 22,832 supported / 6,488 unsupported |
| **T3** | VitaminC test (balanced, other domain) | 3,000 pairs | 1,000 / 1,000 / 1,000 |

There are two surface cues: word overlap (AUROC 0.737 on T1) and data-to-text templates (a sentence-only classifier reaches 0.570 three-way). Contradictions are rare (4 %) and concentrated in data-to-text.

## 4. Results

### 4.1 Accuracy on the frozen tests

| System | T1 three-way | T1 AUROC | T2 macro / RAG subset | T3 three-way | T3 AUROC |
| --- | --- | --- | --- | --- | --- |
| **GroundOne 0.5B** (run 1 / run 2) | 0.769 / 0.767 | 0.905 / 0.907 | 70.1 / 74.4 · 71.5 / 74.3 | 0.442 / 0.434 | 0.722 / 0.747 |
| **GroundOne 3B** | **0.832** | **0.940** | **74.8 / 76.9** | 0.527 | 0.817 |
| Untrained 0.5B / 3B (B1) | 0.372 / 0.437 | 0.502 / 0.726 | – | 0.334 / 0.531 | 0.503 / 0.821 |
| MiniCheck-RoBERTa (B4) | – | 0.814 | 74.0 / 74.6 | – | **0.968** (VitaminC is in its training lineage) |
| HHEM-2.1 (B4) | – | 0.821 | – | – | 0.795 |
| Rizzo-Flow 4B (B3), on its subsample | 0.603 | 0.894 | 60.9 (1,100 items) | **0.712** | 0.909 |
| Word overlap | – | 0.737 | – | – | 0.698 |
| Published zero-shot Qwen2.5-7B | – | – | 72.8 | – | – |

On Rizzo-Flow's 300 T1 answers, GroundOne scores 0.798 (0.5B) and 0.840 (3B).

**Significance** (cluster bootstrap, B = 2000):
- On T1, GroundOne beats every baseline. The 3B beats the 0.5B by +0.063 [+0.052, +0.076], and by +0.116 at K ≥ 14.
- **On T2 the 3B is on par with MiniCheck** (+0.8, CI −0.5 to +2.1, not significant) and above it on the RAG subset (+2.4 [+1.4, +3.3]). The 0.5B is below MiniCheck on the T2 macro (−3.9).
- On T3, Rizzo-Flow and MiniCheck beat GroundOne.

### 4.2 Speed, output parity, energy (latency subset, 200 T1 answers)

| System | Three-way | Format failures | s/answer K ≥ 14 | Calibrated AURC | J/answer |
| --- | --- | --- | --- | --- | --- |
| **GroundOne 0.5B** | **0.835** | 0 % | **0.41** | **0.009** | **5.5** |
| Terse judge 0.5B | 0.233 | 23 % | 0.80 (1.95×) | – | 8.9 |
| Verbose judge 0.5B | 0.017 | 97 % | 2.51 (6.2×) | – | 22.5 |
| Equal-output judge 0.5B, logits / verbalised | 0.234 / 0.234 (0.081) | 24 % / 31 % | 0.81 / 2.47 | 0.063 / 0.061 | – |
| **GroundOne 3B** | **0.900** | 0 % | **2.57** | **0.005** | **33.1** |
| Terse judge 3B | 0.390 | 0.1 % | 4.44 (1.73×) | – | 43.3 |
| Verbose judge 3B | 0.402 | 7.6 % | 15.86 (6.2×) | – | 111.7 |
| Equal-output judge 3B, logits / verbalised | 0.390 / 0.410 | 0.1 % / 0 % | 4.38 / 17.00 | 0.048 / 0.062 | – |

AURC (area under the risk–coverage curve) measures how well the probabilities rank sentences by error risk. Lower is better.

- **Speed.** The speed-up grows with K. Its 95 % CIs are narrow: 1.82–2.14× and 5.72–6.67× for the 0.5B.
- **Output parity.** With the same output (label + 3 calibrated probabilities), every judge stays far behind. Judge AUROC ranges from 0.47 to 0.68, against 0.94–0.97 for GroundOne.
- **Verbalised probabilities carry almost no information.** The 3B writes a one-hot vector for 93 % of the sentences. The 0.5B writes uninformative, tied vectors, so its real macro is 0.081.
- **ECE alone is misleading.** After calibration every system reaches 0.03–0.05. AUROC and AURC are the discriminating metrics.
- **Energy.** GroundOne uses the least energy, but its advantage (1.3–1.6× over terse, 3.4–4.1× over verbose) is smaller than its speed advantage. A single long pass draws more power (16 W, against 11–14 W for decoding).

### 4.3 Calibration

The binary ECE on T1 drops from 0.30 to 0.019 (0.5B) and from 0.18 to 0.019 (3B). Run 2 behaves the same (0.23 → 0.020). Calibration does not transfer to VitaminC.

### 4.4 Readout vs generation (control B2, full T1)

| | Readout | Generated token |
| --- | --- | --- |
| 0.5B three-way | 0.769 | 0.521 (24.7 % format failures, 74 % agreement) |
| 3B three-way | 0.832 | 0.761 (1.2 % failures, 92 % agreement) |

After " Verdict:" the model would write the *spaced* letter (" A"). The three readout letters hold only about 4–5 % of the probability mass. The restricted loss makes GroundOne a 3-way classifier on top of the LM, not a faster generator, which is the definition of a System One. With identical weights and pass, the restricted readout is worth +0.07 to +0.25.

### 4.5 Robustness

- **Seeds.** Two completed 0.5B runs agree on the aggregates (T1 0.769 vs 0.767; AUROC 0.905 vs 0.907; T2 70.1 vs 71.5). They differ in per-class recall (±0.04) and in small slices (K ≥ 14, T3 AUROC, ±0.025). Single T2 datasets move by up to 10 points.
- **One run collapsed.** Seed 4321 fell to a constant predictor (dev 0.333 at step 300) and was stopped at step ≈ 470. There is no gradient clipping in the training loop.
- **Error analysis.** The blind spot is sentences that copy the source but alter a detail. In the high-overlap bin (> 0.7), contradicted recall is 0.24 (0.5B) and 0.36 (3B).

## 5. Takeaways (what the thesis can claim)

1. **Specialisation works in the RAG domain.** A 0.5B specialist beats the encoders and an 8× larger general-purpose System One on T1. The gain comes from training: the untrained models are near chance.
2. **The System One advantage is real.** It is about 2× faster than a terse and 6× faster than a verbose judge at K ≥ 14, always produces valid output, and gives far better probabilities at equal output. Its energy advantage is real but smaller than its speed advantage.
3. **The restricted readout matters in itself** (B2), and matters more the smaller the model.
4. **Calibration is cheap and effective in domain.** It must be judged with AUROC and AURC, not with ECE alone.
5. **Limits.**
   - Weak transfer outside RAG: on T3 the trained 3B is no better than the untrained 3B.
   - Rare contradictions outside data-to-text.
   - The copied-but-altered blind spot.
   - On T2 the 3B is on par with MiniCheck, not above it.
   - The recipe can collapse on some seeds.
6. **Fairness caveats.**
   - In-domain training favours GroundOne on T1.
   - The judges are zero-shot.
   - Subsamples are used for the slow baselines.
   - There is no latency claim against Rizzo-Flow (HTTP, other runtime) or the encoders.

## 6. Open items (experiments until 2026-10-30)

- **Measurements.** Add the new pairs to the bootstrap (run 1 vs run 2, B2 vs readout).
- **Locality pillar, remaining items:**
  - offline proof (`HF_HUB_OFFLINE=1` plus network monitoring);
  - memory when co-resident with a generator;
  - licence table;
  - cost against a hosted judge;
  - overview of local inference in Ch. 1–2.
- **Software.** HTTP API on design (b) with coherent output (labels and flags from one rule), then the demo. Optional: the grounded wiki-ingestion loop.
- **Thesis.**
  - Update Ch. 3–6 with B0d, B2, energy, run 2, the CIs and the System One framing.
  - Add one output example per system.
  - Write Ch. 1, 2, 7 and 8.
  - Fill in supervisors and degree programme.
- **Possible, not planned.** A fix for the collapse (gradient clipping or lower LR, on new seeds); training the spaced letters. Either would be a declared change of recipe.
