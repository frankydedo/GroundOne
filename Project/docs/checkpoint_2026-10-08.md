# Checkpoint 1: where GroundOne stands (2026-10-08)

A short account of what has been done, how, what came out, and what follows from it. Details and every number with
its source: `thesis_notes.md`; decisions: `implementation_plan.md` §3; dataset: `dataset_plan.md` and the data card.

---

## 1. The question

Can a **compact language model, specialised in one decision and used as a System One** (one forward pass, verdicts
read from answer-letter logits, no generated text), verify RAG answers sentence by sentence more accurately and faster
than generative judges and existing verifiers, on a 16 GB laptop?

**The decision.** For every sentence of an answer, the document either *supports* it, *contradicts* it, or *does not
mention* it.

**K.** The number of sentences of the answer, i.e. of decisions. It is the variable on which the System One is compared
with generative judges.

## 2. What was done

| Step | What | How |
| --- | --- | --- |
| Feasibility | Is there room for a System One, and is it faster? | Zero-shot readout vs encoders and generative judges (Phase 0/0b, Oct 5) |
| Task definition | One three-way decision per sentence; binary score and strict/lenient policies derived from the three probabilities | Replaced an earlier four-question design that confused training (D20) |
| Dataset | Training on **RAGTruth only** (13,203 answers, 90,795 labelled sentences). Three test sets: **T1** RAGTruth test, **T2** LLM-AggreFact, **T3** VitaminC | Test sets built and checked first, then frozen with hashes. Labels agree 98.75 % with LLM-AggreFact's independent ones; no leakage (D21) |
| Readout | A marker after every sentence; all K verdicts read in **one pass**; output head applied only at the markers | Design (b), D22; design (a), one question per sentence, kept as fallback |
| Models | GroundOne **0.5B** (all answers, 5.4 h) and **3B** (6,500 answers, 12.25 h) | LoRA r16 on all layers, class-weighted loss, MLX 8-bit, best checkpoint on dev |
| Calibration | Temperature + bias fitted on dev | D24 |
| Baselines | Word overlap and sentence-only cues; untrained models; terse and verbose generative judges; Rizzo-Flow 4B; MiniCheck-RoBERTa, HHEM | Same frozen tests and metrics. Subsamples for the slow systems |
| Latency | Seconds per answer as a function of K | 200 T1 answers (50 per K band), in-process MLX, same machine |
| EDA | Sources and built dataset | Found two surface cues: word overlap, data-to-text templates |
| Thesis | First drafts of Ch. 3, 4, 5, 6 and of the summary | From `thesis_notes.md` |
| Workspace | Restructured: `outputs/`, `experiments/`, `jobs/`, `envs/` | Verified end to end |

## 3. Results

**Accuracy on the RAG test set (T1, 17,284 sentences)**

| System | Three-way balanced accuracy | AUROC (supported vs not) |
| --- | --- | --- |
| Word overlap (no model) | – | 0.737 |
| Sentence-only classifier (ignores the document) | 0.570 | – |
| Untrained 0.5B / 3B | 0.372 / 0.437 | 0.502 / 0.726 |
| MiniCheck-RoBERTa / HHEM | – | 0.814 / 0.821 |
| Rizzo-Flow 4B, general System One (300 answers) | 0.603 | 0.894 |
| **GroundOne 0.5B** | **0.769** (0.798 on Rizzo's answers) | **0.905** |
| **GroundOne 3B** | **0.832** (0.840 on Rizzo's answers) | **0.940** |

- **External benchmark (T2, 0.5B).** 70.1 macro balanced accuracy (zero-shot 0.5B 64.2; zero-shot 7B 72.8). On the RAG subset 74.4, equal to MiniCheck-RoBERTa (74.6).
- **Different domain (T3, VitaminC).** 0.442 (0.5B) and 0.527 (3B), against Rizzo-Flow 0.712. For MiniCheck-RoBERTa (AUROC 0.968) T3 is in its training distribution.

**Latency** (median seconds per answer, answers with K ≥ 14)

| Model size | GroundOne | Terse judge | Verbose judge | One question per sentence (design a) |
| --- | --- | --- | --- | --- |
| 0.5B | **0.41** | 0.80 (2.0×) | 2.51 (6.1×) | 0.59 |
| 3B | **2.57** | 4.44 (1.7×) | 15.86 (6.2×) | 3.83 |

- The advantage grows with K.
- Small judges also break the output format: 23 % (terse) and 97 % (verbose) unparsable verdicts for the 0.5B; 0 % for GroundOne.

**Calibration.** On T1 the binary ECE drops from 0.30 to 0.019 (0.5B) and from 0.18 to 0.019 (3B). It does not transfer to VitaminC.

## 4. Takeaways

1. **Specialisation works where it was aimed.** In the RAG domain a 0.5B specialist beats an 8× larger general-purpose System One and the dedicated encoders. The gain comes from training: the untrained models are near chance.
2. **The System One advantage is real and grows with K.** It is about 2× over a terse judge and about 6× over a verbose one at K ≥ 14, with always-valid output. Accuracy does not drop on long answers, which is where the speed matters.
3. **The dataset is the main constraint.** Contradictions are concentrated in data-to-text, so outside it they are learned only in part (QA and summarisation recall 0.03 → 0.30 with the 3B). Size helps; data would help more.
4. **One blind spot.** Hallucinations hidden in sentences that copy the source but change a detail (number, name). The 3B shrinks it but does not remove it.
5. **Not a general fact checker.** Transfer to VitaminC is weak, and there the 3B gains from size, not from the RAG training.
6. **Calibration is cheap and effective in domain**, but must be fitted on data like the deployment's. Calibrated probabilities make selective prediction effective (AURC 0.010–0.015 on T1).
7. **Honest caveats for the thesis**:
   - in-domain training favours GroundOne on the RAGTruth columns;
   - summarisation: the encoder matches the 3B and beats the 0.5B;
   - single seed per model;
   - subsamples for the slow baselines.

## 5. What remains (to 2026-10-30)

- **Measurements**:
  - T2 for the 3B;
  - bootstrap confidence intervals;
  - decide on the single-token generation control (B2);
  - optionally, latency of Rizzo-Flow and the encoders in comparable conditions (see the fairness note in `thesis_notes.md`).
- **Software**: HTTP API on design (b); demo (local RAG chat, or the grounded wiki-ingestion loop).
- **Thesis**: Ch. 1, 2, 7, 8; revision of Ch. 3–6; supervisor names and degree programme.
