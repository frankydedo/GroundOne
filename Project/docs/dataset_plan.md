# GroundOne dataset plan

Status: v1.1 (2026-10-06), sources decided. Decisions D20 and D21 in `implementation_plan.md` §3.
This document specifies how the training, development and test data are built from scratch.
Nothing is trained until the test set of §4 is built, validated and frozen.
The thesis (Ch. 4) describes only the dataset produced by this plan.

---

## 1. What the model must learn

**Input.**
- A retrieved document `C`: passages for a question, a news article, or structured data.
- An answer `A` written by an LLM, split into sentences `s_1 … s_K`.

**Output.** For every sentence `s_i`, one decision with three classes and their probabilities:

| Class | Definition | Letter |
| --- | --- | --- |
| supported | everything `s_i` states is said or directly implied by `C` | A |
| contradicted | some part of `s_i` conflicts with `C` | B |
| not_mentioned | `s_i` adds information that `C` neither contains nor contradicts | C |

**Precedence.** If a sentence has both a conflicting part and an unverifiable part, it is *contradicted*.
Truth in the real world is irrelevant: only the document counts. RAGTruth's `implicit_true` spans therefore stay *not_mentioned*.

**K is the number of sentences of the answer.** K is the variable on which the System One is compared with generative judges. The central figure of the thesis plots accuracy and latency against K on the same test answers. The speed advantage at high K only matters if accuracy holds at high K. Therefore:
- the training data must contain long answers and late sentence positions;
- the test set must contain enough answers in every K band.

**Derived outputs.** These are computed from the three probabilities, not learned separately:
- binary groundedness: `P(supported)`; this is what the LLM-AggreFact comparison uses;
- strict rule: flag a sentence if `P(supported) < τ`;
- lenient rule: flag a sentence if `P(contradicted) > τ`.

**Binary-only labels.** Some sources only say *supported* / *not supported*. For those, the training loss maximises `P(contradicted) + P(not_mentioned)` when the label is *not supported* (a partial label).

## 2. Requirements the data must satisfy

| # | Requirement | Why |
| --- | --- | --- |
| R1 | Human labels for every test item; for training, human or human-verified labels (purely LLM-generated labels only as a documented fallback) | The test must be trustworthy without our own annotation |
| R2 | Multi-sentence answers with natural K, long answers included (K ≥ 14) | The task and the K experiment |
| R3 | Enough *contradicted* and *not_mentioned* examples, in the RAG domain if possible | They are 3 % and 5 % of RAGTruth test sentences |
| R4 | Documents of realistic length, up to the 2,048-token cap | Local RAG contexts; memory limit on 16 GB |
| R5 | Licences that allow fine-tuning for the training sources | LLM-AggreFact forbids it (D18) |
| R6 | No document or sentence of any test set reaches dev or train | Earlier projects had leaks |
| R7 | The test set is frozen before training, with hashes | No silent changes after seeing results |

## 3. Sources and their role

### 3.1 Already on disk

| Source | Licence | What it gives | Role |
| --- | --- | --- | --- |
| **RAGTruth** (Niu et al., ACL 2024) | MIT | 17,790 LLM answers (6 models) over 2,965 sources. Tasks: QA, summarisation, data-to-text. Span annotations: Evident/Subtle Conflict and Evident/Subtle Baseless Info. Official train/test split by source | **Core.** Test T1 (official test split); dev and train from the train split. The only source in the RAG domain with natural multi-sentence answers and the conflict vs baseless distinction |
| **LLM-AggreFact** (Tang et al., 2024) | CC BY-ND 4.0, gated: evaluation only | 29,320 human-labelled (document, claim) test pairs from 11 datasets, binary | **Test T2 only** (external benchmark, leaderboard-comparable). Never used for training, calibration or selection (D18) |
| **ANLI** R1–R3 | CC BY-NC 4.0 | 163K human three-way (premise, hypothesis) pairs, adversarial, short Wikipedia-style premises | Not used (§3.2): VitaminC covers the same boundary with factual text |
| **MiniCheck synthetic** C2D + D2C | as released with MiniCheck (verify before release of adapters) | 14K binary (document, claim) pairs on multi-sentence documents, built for LLM-AggreFact-style checks | Candidate training supplement (binary, partial-label loss) |

**Measured RAGTruth sentence statistics.**
- Quality *good* only: 17,617 answers.
- Rule-based splitter for now; it is replaced in Step 1 of §7.

| Split | Answers | Sentences | supported | contradicted | not_mentioned | K mean (max) |
| --- | --- | --- | --- | --- | --- | --- |
| train | 14,942 | 117,526 | 104,890 | 4,635 | 8,001 | 7.9 (52) |
| test | 2,675 | 19,902 | 18,301 | 602 | 999 | 7.4 (29) |

- **Test contradicted sentences by task:** data-to-text 459, summarisation 112, QA only 31.
- **Test answers by K:** 1–4: 541; 5–8: 1,287; 9–13: 649; ≥ 14: 198.

### 3.2 Candidates verified (2026-10-06, primary sources: papers, GitHub, HF cards)

| Source | Licence | Labels and who made them | Fit | Decision |
| --- | --- | --- | --- | --- |
| **VitaminC** (Schuster et al., NAACL 2021) | CC BY-SA 3.0 | Claim–evidence pairs, SUPPORTS / REFUTES / NOT ENOUGH INFO. Claims written by 70 trained annotators; Fleiss κ = 0.71 on 2K pairs. Contrastive: a small Wikipedia revision flips the label | Exactly the contradicted vs not_mentioned boundary; pair format (K = 1); 371K train / 55K test (real subset ≈ 249K train) | **Train** (real subset, sampled) and **test T3** |
| **ANAH**, English part (Ji et al., ACL 2024) | Apache 2.0 | Sentence level: No Hallucination / Contradictory / Unverifiable / No Fact. GPT-4 pre-annotation, verified and corrected by humans (GPT-4 vs final agreement 87 %) | Same three classes, sentence level, long reference documents; short answers (~2.5 sentences); ~6.6K English sentences, minority classes well represented | **Train** (No Fact → no label, as in §4) |
| **Trivia++** (Chen et al., ACL 2026) | Paper: CC BY 4.0; repository: CC BY-NC-ND 4.0 (conflict) | Sentence level: Supported / Contradicted / Not Mentioned / Supplementary; crowd, Fleiss κ = 0.46 | The only external RAG benchmark with our label set and multi-sentence answers (645 test answers) | **Secondary external test T4**, evaluation only, after checking the licence and the definition of *Supplementary* |
| **RAGTruth re-annotation** (RT4CHART, 2026) | not verified | Re-annotation of the full RAGTruth test split (Entailed / Contradicted / Baseless) by two annotators; finds 1.68× more hallucinated answers than the original | Independent check of T1 labels, including the type | **Check C7** on T1, if the data and licence allow |
| RAGBench (Friel et al., 2024) | CC BY 4.0 | Sentence-level binary labels made by GPT-4 | Long contexts and answers; ExpertQA subset leaks into LLM-AggreFact | Fallback only (partial-label loss, without `expertqa`) |
| ANLI | CC BY-NC 4.0 | Human three-way, adversarial NLI | Short premises, adversarial, far from RAG; VitaminC covers the same boundary with factual text | **Not used** |
| ANAH-v2, HaluEval, HaluBench, FaithBench, FEVER, MNLI/SNLI, DocNLI, PsiloQA, SciHal, CAQA | – | model-generated labels, answer-level labels, missing evidence for NEI, or leakage (HaluBench contains RAGTruth test answers) | – | **Not used** |

### 3.3 Decision on sources

- **Training sources**
  - **RAGTruth train**: the core. All sources except the dev share; full answers; all sentences.
  - **ANAH (English)**: sentence-level three-way labels on real LLM answers and documents. It adds *contradicted* and *not_mentioned* examples outside RAGTruth's three tasks.
  - **VitaminC (real subset, sampled)**: pair data aimed at the contradicted vs not_mentioned boundary.
  - **MiniCheck synthetic**: binary, partial-label loss. Long multi-sentence documents of the kind LLM-AggreFact contains.
  - Fallback if long contexts turn out to be under-represented: RAGBench without `expertqa`.
- **Test sets**
  - **T1** RAGTruth test.
  - **T2** LLM-AggreFact test.
  - **T3** VitaminC test (real, human, balanced three-way).
  - **T4 (secondary)** Trivia++ test.
- **Reliability caveats this choice must report**
  - RAGTruth reports annotator agreement (91.8 % per answer, 78.8 % per span), but none for the conflict vs baseless *type*.
  - A 2026 re-annotation found many unmarked hallucinations in the RAGTruth test, so T1 under-counts *contradicted* and *not_mentioned*.
  - Mitigation, in place of our own annotation:
    - the three-way claim rests on T3, which has κ = 0.71, as well as on T1;
    - T1 labels are cross-checked against the independent re-annotation (C7) when it is available;
    - both points are stated as threats to validity.

## 4. Test sets (built first, then frozen)

### T1: RAGTruth test, the primary in-domain test

- **Content.** All quality-*good* answers of the official test split: 2,675 answers, 450 sources, 3 tasks.
- **Scoring.** Every sentence of an answer is a decision. The numbered answer shown to the model is the full answer.
- **Labels.** Sentence class from span overlap, with the precedence of §1. Documented edge cases:
  - `implicit_true` spans: *not_mentioned*;
  - spans crossing a sentence boundary: label every sentence they touch;
  - answers with no span: all sentences *supported*.
- **Segmentation.** One standard segmenter for everything: test, dev, train and inference.
  - It is chosen *a priori* (pysbd: rule-based, handles abbreviations and decimals). Agreement with LLM-AggreFact is only *reported* as validation (C2), never optimised, so nothing is tuned on a test set.
  - Measured with the current regex splitter on the 19,902 test sentences:
    - 76.5 % are exactly an LLM-AggreFact claim;
    - 22.1 % are absent from LLM-AggreFact, and about half of these are fragments from splitting decimals ("rating of 4." + "0 stars");
    - the rest are sentences without checkable content that LLM-AggreFact dropped ("Sure!", "Elements:", "Based on the provided passages, … is:").
- **Sentences without checkable content.** They stay in the numbered answer as context but are not decisions: no label, no score, `label: null` in the output JSON.
  - They are detected by a short, documented rule: no content word, a trailing colon introducing a list, a greeting, or a refusal formula.
  - The same rule is applied everywhere.
  - K counts the scored sentences.
- **Reported metrics.**
  - three-way macro-F1 and per-class recall;
  - binary balanced accuracy at 0.5 and AUROC;
  - strict and lenient rule accuracy;
  - all of the above per task and per K band (1–4, 5–8, 9–13, ≥ 14), and per answer (all K sentences correct);
  - 95 % confidence intervals by bootstrap over answers.
- **Small cells.** Any reported cell with fewer than 30 gold examples of a class (for example *contradicted* in QA) is shown with its CI and marked as indicative.

### T2: LLM-AggreFact test, the external benchmark

- **Content.** 29,320 pairs, unchanged, K = 1, binary.
- **Scoring.** `P(supported)` at threshold 0.5. Report the 11-way macro balanced accuracy and the RAG subset (RAGTruth, LFQA, ClaimVerify, ExpertQA).
- **Long documents.** Over the cap, chunk and take the maximum over chunks, as MiniCheck does, and report how many items needed it.
- **Overlap with T1.** Its RAGTruth part is the same data as T1, so it is reported separately and not counted twice.

### T3: VitaminC test, three-way with balanced classes

- **Content.** The official test split, real (human-written) claims only, sampled stratified by class to about 3,000 pairs. Evidence pages stay disjoint from the training sample (leakage check by page).
- **Purpose.** Measure contradicted vs not_mentioned with clean labels (κ = 0.71) and balanced classes. T1 has only 602 contradicted sentences.
- **Caveats.**
  - VitaminC is also a training source, so T3 is in-distribution for the pair format.
  - It is not a RAG test: it supports the three-way claim, not the K claim.

### T4: Trivia++ test (secondary, external)
- 645 multi-sentence RAG answers with sentence labels Supported / Contradicted / Not Mentioned / Supplementary.
- Evaluation only.
- **Used only if both checks pass:**
  - the licence permits evaluation use;
  - the definition of *Supplementary* maps to one of our classes without ambiguity (expected: *not_mentioned*, since grounding is relative to the document).
- Otherwise it is dropped and this is stated.

### Reliability checks, run before freezing (no manual annotation)

| Check | Pass criterion | If it fails |
| --- | --- | --- |
| C1 Label provenance | every test label comes from human annotators of the published dataset | drop the source from test |
| C2 Segmentation | with the a-priori segmenter + content rule: ≥ 90 % of LLM-AggreFact RAGTruth claims found exactly among our scored sentences, and ≤ 10 % of our scored sentences absent from LLM-AggreFact (reported, not optimised) | inspect the error types; fix only rule-level bugs (e.g. decimals), document them; T1 results are also reported on the matched subset |
| C3 Label derivation | our binary label (supported vs not) agrees ≥ 97 % with LLM-AggreFact's independent label on matched sentences (earlier measurement with the regex splitter: 98.6 %); disagreements listed in the data card | inspect the rule; fix and re-run |
| C4 Class and K coverage | counts per class × task × K band tabulated; cells < 30 flagged | report as indicative (no relabelling) |
| C5 Reference baselines | MiniCheck-RoBERTa on T2 within ±1.5 points of its published 73.5; majority and random baselines reported for T1 and T3 | debug the evaluation code before any GroundOne result |
| C7 Independent T1 labels | if the RAGTruth test re-annotation (RT4CHART) is available with a usable licence: agreement of our T1 three-way labels with it, per class; T1 results also reported against it | report the limitation; the three-way claim rests on T3 |
| C6 Freeze | test files + manifest with SHA-256; evaluation reads only through the manifest; any later change requires a decision-log entry | – |

**When manual annotation would become strictly necessary.**
- If C2 or C3 fail and cannot be fixed by rule.
- RAGTruth reports no agreement for the conflict vs baseless type (§3.3). This alone does not make annotation necessary, because the three-way claim is also tested on T3 (κ = 0.71) and C7 may give an independent check.

In that case a small audit of the T1 three-way labels (about 150 sentences) would be the minimal fix, and it is proposed to the author before anything else is done.

## 5. Development set

- **What it is for.** Checkpoint selection and calibration only. Never used for training. Same format as T1.
- **Groups.** 10 % of RAGTruth train sources, held out by `source_id` (about 1,500 answers, all their sentences). Every additional training source contributes a small dev part, split by its own group key.
- **Selection metric.**
  - three-way macro-F1 on RAGTruth dev (primary);
  - binary balanced accuracy on the binary dev parts (secondary, used to break ties).
  - Fixed before training.
- **Calibration.** Fitted on dev: temperature plus bias per prompt format.

## 6. Training set

**Storage.** One record per answer, independent of the readout design of §8:
```
{id, source, group, task, doc, sentences: [...], labels: [supported|contradicted|not_mentioned|unsupported], meta: {K, model, ...}}
```
`unsupported` marks binary-only labels.

**Composition principles.**
- RAGTruth train is the core: all remaining sources, full answers, all sentences.
- Supplements only where they fix a measured gap: *contradicted* and *not_mentioned* volume and balance (R3), long documents.
- **Class balance** by loss weighting or by masking part of the *supported* sentences in the loss, never by cutting answers. The model must always see whole answers.
- **K coverage.** Long answers kept, and weighted up if the K ≥ 14 band is too thin.
- **Token budget per night (to be measured on the final format).**
  - 0.5B: about 15 M tokens.
  - 3B: about 6–7 M tokens. The 3B is trained on a stratified subset; same composition, smaller size.
- **Checks on train.** Leakage (§2, R6) against T1–T3, including LLM-AggreFact documents and claims. A claim-only shortcut baseline (a classifier that sees only the sentence) on train and test, to expose label cues.

## 7. Build order and acceptance (target: frozen data by Thu 2026-10-09)

1. **Segmenter and content rule.** Install pysbd in the venv, implement the content rule, then measure C2. *Accept:* C2 passes.
2. **T1 and T2.** Build, run C1–C5. *Accept:* all pass; data card section written; figures (class × task × K, token lengths) in `Project/figures/dataset/`.
3. **T3, T4, C7.** Download VitaminC, Trivia++ and (if available) the RAGTruth re-annotation. Check licences. Build T3 (and T4 if its checks pass), run C1, C4, C5 and C7.
4. **Freeze.** C6: manifest with hashes committed.
5. **Dev.** Build, then run the leakage check against T1–T3.
6. **Training sources.** Download ANAH. Convert RAGTruth train, ANAH (English), VitaminC train (real subset) and MiniCheck synthetic to the record format. Run the leakage check against all test sets, including n-gram claim checks against LLM-AggreFact's Wikipedia-based subsets (WiCE, REVEAL) for ANAH and VitaminC.
7. **Training mix.** Apply the budget of the readout design chosen in §8, then run the leakage and shortcut checks. Write the data card (composition, origin, licence, rationale), which becomes thesis Ch. 4.

Code. A new `groundone.data` builder, one module per source plus a `freeze` step. `leakage.py` and `shortcut.py` are adapted to the answer-level records. Output goes to `Project/data/processed/groundone/`.

## 8. Dependency: readout design (decided before Step 7)

The dataset is stored per answer, so it serves both designs. The design decides how many labels fit in the budget.

**(a) Current design.** Prefix (document + numbered answer) once, then K short question suffixes in one batch.
- Exact and implemented.
- In training, each row is one prompt for one sentence. 15 M tokens ≈ 16K labelled sentences out of the ~105K available in RAGTruth train.

**(b) K readouts in one pass.** A marker after each sentence; the letter logits are read at every marker in the same forward pass.
- In training, one row per answer carries K labels. All RAGTruth train sentences fit in about 12 M tokens: roughly 7 times more supervision for the same cost, which matters most for the 3B.
- At inference, one pass for all K decisions.
- Cost: sentence *i* sees only the previous sentences, and the engine and training loop are new.
- **Gate.** A half-day prototype on a subset compares (a) and (b) on dev macro-F1 and latency. (b) is adopted only if it is not worse on dev.

## 9. Out of scope for the dataset
- LLM-AggreFact for anything but evaluation.
- Our own annotation, unless §4 makes it strictly necessary.
- Languages other than English.
