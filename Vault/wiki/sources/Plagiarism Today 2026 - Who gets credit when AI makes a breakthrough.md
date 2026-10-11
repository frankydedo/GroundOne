---
type: source
author: "Plagiarism Today (author not named in the extraction)"
date: 2026-09-09
venue: "Plagiarism Today, blog on plagiarism and copyright (published 2026-09-09; retrieved 2026-10-11)"
url: "https://www.plagiarismtoday.com/2026/09/09/who-gets-credit-when-ai-makes-a-breakthrough/"
tags: [source, blog, opinion, navier-stokes, openai, credit-dispute, attribution, privacy, compute-inequality, ai-for-math]
---
# Plagiarism Today 2026 – Who Gets Credit When AI Makes a Breakthrough?

**Raw file**: `raw/local_inference/Plagiarism Today 2026 - Who gets credit when AI makes a breakthrough_ingested.md`

## Overview
An **opinion piece** from a blog on plagiarism and attribution. It summarises the dispute from secondary reports (Engadget, Tom's Hardware, DataCamp) and Buckmaster's statement, then discusses two concerns:
1. whether OpenAI trained on Buckmaster and Alpöge's work;
2. whether labs with massive compute can pre-empt human researchers once a rumour of progress spreads.

It also raises the question of credit and citation for AI-produced results. The author describes themself as "an AI skeptic". The summary contains **several imprecisions** (insight 6), so it is useful for the *framing* of the credit question, not for facts.

## Key Insights
1. **Claims as reported.** OpenAI's 88-hour run "spent more than 300 billion output tokens", and the whole attempt cost "roughly $22.5 million in compute" (citing DataCamp). If accepted, it would be only the second Millennium Prize Problem solved. Navier–Stokes is described as unsolved "for over 90 years".
2. **Timeline (as reported).**
   - 1 Sept: OpenAI heard a rumour and started.
   - About 50 h later: Euler proof; then "another 88 hours" for Navier–Stokes.
   - 3 Sept: Buckmaster heard a rumour that *Anthropic* had solved a major problem and contacted OpenAI to clarify that the work was a personal collaboration, not institutional.
   - 6 Sept: Buckmaster, without Alpöge, met Bubeck, "one day after OpenAI finished its proof but was waiting on verification".
3. **Allegations as reported.** Per Buckmaster, Bubeck offered two options: sole authorship crediting OpenAI's models (omitting Alpöge), or a joint release with OpenAI, also removing Alpöge. The quotes "Why would you ruin your career?" and "If you don't want me to be nice, then I don't have to be nice" are attributed to Bubeck by Buckmaster. Alpöge is described as "working in his personal capacity". Per Tom's Hardware, Buckmaster "paid for much of the compute time he used himself".
4. **The data point.** Bubeck "strongly asserted that OpenAI had not seen their work previously, but could not say for certain if their model had been trained on Buckmaster and Alpöge's work since it had been uploaded to the service". This is a paraphrase, not a quote. It is consistent in substance with OpenAI's "cannot rule out" sentence in [[NYU Shanghai RITS 2026 - OpenAI claims a Navier-Stokes proof amid a dispute over credit]].
5. **The author's arguments (opinion).**
   - OpenAI's Euler method differs, but its Navier–Stokes approach follows the Córdoba–Martínez-Zoroa line the pair used.
   - OpenAI's paper cites 29 sources (including Córdoba and Martínez-Zoroa), but neither readers nor OpenAI can know whether that list is complete, since the model was trained on "countless other mathematicians' work". Citation is also how faulty work gets caught.
   - Compute asymmetry: a lab can "simply drop millions of dollars in compute time on the problem based on a rumor alone", which is "grossly unfair" to individuals and universities.
   - Open question: who gets credit for an AI discovery — the prompter, the trainer, or the authors of the work the model relied on most?
6. **Imprecisions and contradictions.**
   - "300 billion output tokens" for the 88-hour run conflates totals. Per RITS and Live Science, about 300B tokens is the total across all problems, and about 130B went to Navier–Stokes.
   - "Another 88 hours" after a 50-hour Euler run contradicts RITS: resolution "about 88 hours after launch".
   - The option wording differs from Fortune's (see [[Fortune 2026 - OpenAI says it cracked Navier-Stokes, Buckmaster accusation]]).
   - "Blow up" is glossed as producing "results that were not physically possible", a loose description.
   - The page says both sides published "their proofs (or at least some of them)".

## Relevance to GroundOne
- **Indirect, and mainly about credit.** The page's main subject is attribution, which is outside the thesis. Its data paragraph supports the same narrow point as the other pages: a user who uploaded unpublished work to a cloud service cannot get certainty about whether it was trained on, and even the provider "could not say for certain" ([[Privacy and Data Sovereignty]], proposed). Running everything locally removes this uncertainty ([[On-Device Inference]]).
- **Do not overstate.** The author says "everyone has stopped short of saying that this is a work of plagiarism". The thesis should likewise not imply misuse.
- The compute-asymmetry argument has a loose parallel with the thesis theme of independence from large providers, but it is about research priority, not data privacy. Use it, if at all, only as context.

## Links
- Concepts: [[Navier-Stokes Credit Dispute (2026)]] (proposed), [[Privacy and Data Sovereignty]] (proposed), [[On-Device Inference]]
- Related sources: [[Fortune 2026 - OpenAI says it cracked Navier-Stokes, Buckmaster accusation]], [[NYU Shanghai RITS 2026 - OpenAI claims a Navier-Stokes proof amid a dispute over credit]], [[OfficeChai 2026 - OpenAI says it didn't see Buckmaster and Alpoge's work]], [[Live Science 2026 - Why would you ruin your career, OpenAI Navier-Stokes claim]]
