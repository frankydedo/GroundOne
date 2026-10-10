---
type: source
author: "Philipp Koehn"
date: 2004
venue: "EMNLP 2004 (ACL Anthology W04-3250)"
url: "https://aclanthology.org/W04-3250/"
tags: [source, paper, statistics, significance-testing, bootstrap, paired-bootstrap, evaluation, machine-translation]
---
# Koehn 2004 – Statistical Significance Tests for Machine Translation Evaluation

**Raw file**: `raw/Koehn 2004 - Statistical Significance Tests for MT Evaluation (paired bootstrap)_ingested.pdf`

## Overview
BLEU is a corpus-level metric, not a mean of per-sentence scores, so the usual t-based confidence interval does not apply to it (§4). Koehn introduces two **bootstrap** procedures to NLP evaluation (§5–6): a percentile **confidence interval** for one system's score, and **paired bootstrap resampling** to decide whether one system beats another. He validates both empirically on Europarl, using a 30,000-sentence test set as the "true" score (§3, §7).

## Key Insights
1. **Test sets are not i.i.d. samples of sentences (§3.2–3.3).** BLEU on 100 blocks of 300 *consecutive* sentences ranges from 21 % to 37 % (Fig. 2). On 100 "broad samples" (sentences spread across the corpus) the spread is much smaller (Fig. 3). Neighbouring sentences share topic, style and source language, so their difficulty is correlated. Recommendation: build small test sets from many parts of a larger pool.
2. **Bootstrap confidence interval (§5).** Resample the n test sentences with replacement 1,000 times, recompute the metric each time, and drop the top and bottom 2.5 %. The key assumption is stated explicitly: resampling from the test set approximates drawing fresh test sets. On 100 test sets of 300 sentences, the "true" 30k BLEU (28.9) falls inside the 95 % interval 97 times (Fig. 6).
3. **Paired bootstrap (§6).** Resample the *same* sentence indices for both systems and count how often system A beats B. If A wins in ≥ 95 % of resamples, conclude A is better at the 95 % level. Pairing removes the shared, per-sentence difficulty from the comparison.
4. **Validation (§6–7).**
   - Spanish vs Danish (true difference 2.0 BLEU): a 300-sentence test set gives a significant win in 65 of 100 cases (Fig. 7).
   - Portuguese vs Danish (difference 0.5): 12 correct and 1 wrong conclusion out of 100 (Fig. 8), as expected at the 95 % level.
   - With 300 sentences, a 2–3 BLEU difference is detected reliably; 100 sentences produce more false conclusions (§7.1).
   - The estimates err on the side of caution: conclusions at the 90–94.9 % level are right 95 % of the time (Table 4).
5. **Scope.** Koehn's paired procedure counts wins over resamples; it is not the re-centred p-value later formalised by [[Berg-Kirkpatrick 2012 - An Empirical Investigation of Statistical Significance in NLP|Berg-Kirkpatrick et al. 2012]].

## Relevance to GroundOne
- GroundOne's `groundone bootstrap` (`eval/bootstrap.py`) is a direct descendant: **B = 2000** resamples, 95 % percentile intervals, and **paired** differences computed on the same resamples for both systems, using only the rows both systems scored.
- Koehn's observation that neighbouring sentences are correlated is the reason GroundOne uses a **cluster bootstrap**. The unit of resampling is the leakage group, not the sentence: RAGTruth source document on T1 (447 groups), document on T2 (8,329 groups, resampled within each dataset because the macro averages datasets), and Wikipedia page on T3 (1,257 groups). Sentences of one answer, and answers about one source, are strongly dependent. Resampling them independently would make the intervals too narrow.
- Koehn's validation shows that a paired bootstrap answers "would these two *fixed* systems still differ on a new test set from the same distribution?". It says nothing about re-training. This is the caveat GroundOne hit: run 1 vs run 2 of the 0.5B differ "significantly" on T2 macro (−0.013 [−0.024, −0.003]) and T3 AUROC (−0.025 [−0.037, −0.012]), although they share data, config and code and differ only in the seed. See [[Statistical Significance and Bootstrap]] and [[Fine-tuning Instability and Seeds]].
- Test-set size matters, as in Koehn §7.1. The K ≥ 14 slice of T1 has only 93 groups, and its intervals are correspondingly wide (3B − 0.5B +0.116 [+0.050, +0.180]).

## Links
- Concepts: [[Statistical Significance and Bootstrap]], [[Fine-tuning Instability and Seeds]]
- Related sources: [[Berg-Kirkpatrick 2012 - An Empirical Investigation of Statistical Significance in NLP]], [[Dror 2018 - The Hitchhiker's Guide to Testing Statistical Significance in NLP]], [[Dodge 2020 - Fine-Tuning Pretrained LMs (weight init, data order, early stopping)]]
- Thesis context: [[GroundOne]], [[RAGTruth]], [[LLM-AggreFact]], [[VitaminC]]
