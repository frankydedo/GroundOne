---
type: concept
tags: [concept, dataset, fact-verification, contrastive, three-way, test-data]
---
# VitaminC

**VitaminC** is a contrastive fact-verification dataset built from Wikipedia revisions ([[Schuster 2021 - VitaminC]], NAACL 2021). It has 488,904 claim–evidence pairs labelled SUPPORTS / REFUTES / NOT ENOUGH INFO. Its "real" part has claims written by 70 trained annotators about real factual edits; the synthetic part is derived from FEVER and has no NEI. Licence: CC BY-SA 3.0.

## Why it is contrastive
- A factual revision gives two almost identical evidence sentences.
- A claim is supported by one version and refuted by the other, or left without enough information when no contradiction can be written.
- A model must therefore look at the exact fact (often a number), not at word overlap.

## Role in GroundOne (decided 2026-10-06)
- **Test T3 only**, not training. It is a sample of the real test split, stratified by class.
- **Purpose.** An independent, reliable check of the three-way distinction [[Groundedness Verification|contradicted vs not mentioned]] (Fleiss κ = 0.71). This is needed because [[RAGTruth]] reports no agreement for the conflict vs baseless type.
- **Mapping.** SUPPORTS → supported, REFUTES → contradicted, NEI → not_mentioned.
- **Limits.** Single-sentence Wikipedia evidence, K = 1, many numerical claims. It tests transfer from RAG training data, not the K advantage.
- **Overlap.** Its Wikipedia sentences could coincide with LLM-AggreFact's WiCE or REVEAL. This does not matter for test-only use, and it would need a leakage check if VitaminC were ever used for training.

## GroundOne results on T3 (2026-10-10)
- Three-way balanced accuracy: GroundOne 0.442 (0.5B), 0.434 (run 2), 0.527 (3B); AUROC 0.722 / 0.747 / 0.817.
- **The untrained 3B scores the same** (0.531 / 0.821), so the 3B's T3 level comes from model size, not from the RAG training: transfer outside RAG is weak.
- [[Rizzo-Flow]] 4B: 0.712 / 0.909 on 600 pairs, where GroundOne scores 0.442 / 0.537 (AUROC 0.744 / 0.845).
- [[MiniCheck]]-RoBERTa AUROC 0.968, but VitaminC is in its training lineage (via [[AlignScore]] data), so it is not a transfer result. [[HHEM]] 0.795.
- Calibration fitted on RAGTruth dev does not transfer to T3; the served threshold rule loses 0.02–0.04 there.
- Blind spot: paraphrased support is rarely recognised (supported recall 0.02–0.04 when word overlap ≤ 0.4). See [[GroundOne Results]], [[GroundOne 2026 - EDA report (dataset)]].

## Links
[[Schuster 2021 - VitaminC]], [[Datasets for GroundOne]], [[Natural Language Inference]], [[ANLI]], [[RAGTruth]], [[LLM-AggreFact]], [[GroundOne]]
