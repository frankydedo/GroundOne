---
type: source
author: "Liyan Tang, Igor Shalyminov, Amy Wing-mei Wong, Jon Burnsky, Jake W. Vincent, Yu'an Yang, Siffi Singh, Song Feng, Hwanjun Song, Hang Su, Lijia Sun, Yi Zhang, Saab Mansour, Kathleen McKeown"
date: 2024
venue: "NAACL 2024 (Long Papers), pp. 4455–4480"
url: https://arxiv.org/abs/2402.13249
tags: [source, paper, dataset, benchmark, dialogue-summarization, hallucination, sentence-level, llm-aggrefact]
---
# Tang 2024 - TofuEval

**Raw file**: `raw/Tang 2024 - TofuEval_ingested.pdf`
**Data**: github.com/amazon-science/tofueval

TofuEval is a benchmark for **topic-focused dialogue summarization** written by LLMs. Professional linguists provided **sentence-level binary** factual-consistency labels with written explanations. Its two halves are the **TofuEval-MediaS** and **TofuEval-MeetB** sub-datasets of [[LLM-AggreFact]].

## Overview
- **Documents (§3.1, Table 5)**: 50 test-set documents each from:
  - **MediaSum**: NPR/CNN interview transcripts. Average 970 words, 16.6 turns, 5.7 speakers.
  - **MeetingBank**: US city-council meetings. Average 930 words, 19.9 turns, 4.9 speakers.

  Documents were sampled at **800–1,200 words** so that they fit every summarizer's context. Word counts use NLTK.
- **Topics (§3.2)**: an LLM generated 3 topics per document with a zero-shot prompt (App. C.1). Humans then categorized them as main (about 75%) or marginal topics.
- **Summarizers (§3.3, App. B)**: **GPT-3.5-Turbo, Vicuna-7B, WizardLM-7B/13B/30B**, temperature 0.7, prompted for a summary under 50 words on the topic.
- **Size**: 50 docs × 2 datasets × 3 topics × 5 LLMs = 1,500 summaries. 23 non-summaries were removed, leaving **1,479 summaries (3,966 sentences)**. The split is **70/30 dev/test by document** (§3.3).
- **Labels (§3.4)**: a sentence is consistent "if the sentence is **stated or implied** by the document". Annotators wrote an explanation for every inconsistent sentence. An error taxonomy was added later (App. G).
- **Annotators**: **professional linguistic data annotators** with native-level English, trained through a practice session and pilot rounds with feedback (App. F.3).
- **Agreement (App. F.4)**: factual consistency **κ = 0.42 (MediaSum) and 0.34 (MeetingBank)**, i.e. fair to moderate. After annotation, **the authors re-reviewed the labels and removed false-positive "inconsistent" labels** using the explanations, with the summarizer identity hidden.

## Key insights
- Sentence-level error rates (Table 2) average 17.5% / 27.8% (MediaSum main / marginal topics) and 14.4% / 27.8% (MeetingBank). GPT-3.5-Turbo is lowest (4.4–13.6%).
- **Marginal topics roughly double the error rate**, mostly through *extrinsic information*: the model falls back on its own knowledge when the topic is barely discussed in the document (§4).
- Larger LLMs are not necessarily more faithful. As evaluators, every LLM except GPT-4 underperformed non-LLM metrics such as AlignScore and SummaC (§5).

## How it appears in LLM-AggreFact
- **Claim** = one summary **sentence**. **Document** = the full dialogue transcript, about 1K words. Our EDA gives a median of about 1,000 Qwen tokens.
- The binary labels are kept as they are (MiniCheck App. C.2).
- **Label balance (our EDA, test)**: MediaS **76.3%** and MeetB **80.6%** supported.
- **Size**: LLM-AggreFact lists 1,800/726 (MediaS) and 1,607/772 (MeetB) dev/test, about 4.9K sentences in total. This does not reconcile with the paper's 3,966 sentences, and the difference is not explained in the sources read.

## Caveats
- Agreement on factual consistency is only fair to moderate, and the authors' one-directional clean-up (removing false *inconsistent* labels) may bias the labels towards "supported".
- The informal, multi-speaker input means verification needs speaker attribution and discourse tracking (who said what), which news-trained NLI models handle poorly.

## Relevance to GroundOne
- It is the closest LLM-AggreFact analogue to **query-focused** generation over a long context: the topic plays the role of the query. Answers generated about marginal topics resemble RAG answers drawn from weakly relevant retrieved chunks.
- The documents are about 1K tokens, which fits a 2,048-token cap.

## Links
[[LLM-AggreFact]], [[LLM-AggreFact Sub-datasets]], [[Tang 2023 - AggreFact]], [[Tang 2024 - MiniCheck]], [[AlignScore]], [[LLM-as-a-Judge]], [[Hallucination Detection]], [[Groundedness Verification]], [[GroundOne]]
