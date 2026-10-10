---
type: source
author: "Taylor Berg-Kirkpatrick, David Burkett, Dan Klein"
date: 2012
venue: "EMNLP-CoNLL 2012, pp. 995–1005 (ACL Anthology D12-1091)"
url: "https://aclanthology.org/D12-1091/"
tags: [source, paper, statistics, significance-testing, bootstrap, paired-bootstrap, domain-shift, evaluation]
---
# Berg-Kirkpatrick 2012 – An Empirical Investigation of Statistical Significance in NLP

**Raw file**: `raw/Berg-Kirkpatrick 2012 - An Empirical Investigation of Statistical Significance in NLP_ingested.pdf`

## Overview
An empirical study of how **paired bootstrap p-values** behave in practice across summarisation, dependency parsing, machine translation, word alignment and constituency parsing. Two questions:
1. How does significance relate to the size of the metric gain, the test-set size and the similarity of the compared systems (§3–4.1)?
2. Does significance on one test set predict which system is better on new data, in domain and out of domain (§4.2)?

To get thousands of comparable systems, the authors use published shared-task outputs (TAC 2008, CoNLL 2007, WMT 2010). They also train variants of the same parsers and MT systems on **resampled training sets** (§3.2).

## Key Insights
1. **The test (§2.1, Fig. 1).** Draw b bootstrap samples of the test set and count how often the resampled gain $\delta(x^{(i)})$ exceeds $2\delta(x)$. The bootstrap distribution is centred on the observed gain, not on the null, so it has to be re-centred. Then $p \approx s/b$. The common variant that counts $\delta(x^{(i)}) < 0$ is equivalent when the bootstrap distribution is symmetric (footnote 2). The bootstrap is preferred to approximate randomisation for this null hypothesis (footnote 1). Per-sentence sufficient statistics make it fast for any metric.
2. **"Rule-of-thumb" thresholds exist but are fragile (§3).** For example, 1.10 ROUGE on TAC 2008, and 0.47 / 0.57 F1 for WSJ constituency parsing (same / different model type). Thresholds depend on system similarity and test-set size, so they cannot replace a test.
3. **Correlated systems reach significance with smaller gains (§3.1–3.2).** Systems from the same group, system combinations, or variants of one base model are more correlated. Their comparisons lie on a separate curve that reaches high confidence at smaller gains (Figs. 2–8). Example: dependency parsing threshold 1.20 for same-model pairs vs 1.51 for different-model pairs.
4. **Test size matters most, with diminishing returns (§4.1).** Brown corpus parsing: the p < 0.05 threshold is 3.00 F1 on 100 sentences and 0.22 F1 on all ~24K sentences (Figs. 9–10), roughly following $1/\sqrt n$. For a fixed size, the domain changes the curve little (Fig. 11).
5. **In-domain, p-values are well calibrated; across domains, they are not (§4.2).** When test sets are drawn i.i.d. from Brown, 92 % of comparisons with p ∈ [0.04, 0.06] pick the truly better system. A p ≈ 0.05 on WSJ section 23 predicts the winner on section 22 83 % of the time, on section 24 71 %, and on Brown 48 %, i.e. no information. Only p < 0.00125 on section 23 reasonably predicted the Brown result (Table 1).
6. **Conclusion (§5).** Significance is a necessary minimum, not a guarantee of practical or out-of-domain superiority.

## Relevance to GroundOne
- **Explains the run-1 vs run-2 result.** Two GroundOne 0.5B runs with different seeds are *maximally correlated systems*: same data, recipe and architecture. By point 3, tiny gains are enough for significance. So a paired cluster bootstrap flags T2 macro −0.013 and T3 AUROC −0.025 as "significant", although the difference is pure seed noise. The bootstrap is correct about the question it answers (these two fixed checkpoints differ on this distribution); it does not answer whether one *recipe* beats another. See [[Statistical Significance and Bootstrap]].
- **Training-set resampling (§3.2) is a variance source the test-set bootstrap ignores.** Berg-Kirkpatrick use it to *simulate* research variants. For GroundOne it points to the missing term: variance from re-training (seed, data order), which [[Dodge 2020 - Fine-Tuning Pretrained LMs (weight init, data order, early stopping)|Dodge 2020]] measures directly.
- **Domain shift (point 5) matters for T1 → T2/T3.** GroundOne's significant wins on T1 (in-domain RAGTruth) do not license claims on VitaminC (T3, out of domain), where GroundOne actually loses to MiniCheck and Rizzo-Flow. T2 is a mix of domains, and individual T2 datasets move by up to 10 points between seeds. The thesis already restricts T2/T3 claims; this paper is the citation for doing so.
- **Re-centring check.** GroundOne reports a two-sided bootstrap p. It should state which variant is used (counting sign flips of the paired difference vs the re-centred $2\delta$ rule); they agree when the bootstrap distribution is symmetric.

## Links
- Concepts: [[Statistical Significance and Bootstrap]], [[Fine-tuning Instability and Seeds]]
- Related sources: [[Koehn 2004 - Statistical Significance Tests for MT Evaluation (paired bootstrap)]], [[Dror 2018 - The Hitchhiker's Guide to Testing Statistical Significance in NLP]], [[Dodge 2020 - Fine-Tuning Pretrained LMs (weight init, data order, early stopping)]]
- Thesis context: [[GroundOne]], [[LLM-AggreFact]], [[VitaminC]], [[RAGTruth]]
