---
type: source
author: "Larissa G. Capella (Live Science; edited by Ben Turner, Pandora Dewan, Brandon Specktor, Laura Mondragón)"
date: 2026-09-09
venue: "Live Science, news explainer (published 2026-09-09; retrieved 2026-10-11)"
url: "https://livescience.com/physics-mathematics/mathematics/why-would-you-ruin-your-career-openai-claims-to-have-cracked-one-of-maths-greatest-unsolved-problems-but-mathematicians-allege-it-played-dirty"
tags: [source, journalism, navier-stokes, openai, codex, privacy, user-data, training-data, credit-dispute, ai-for-math]
---
# Live Science 2026 – "Why Would You Ruin Your Career?": OpenAI's Navier–Stokes Claim

**Raw file**: `raw/local_inference/Live Science 2026 - Why would you ruin your career, OpenAI Navier-Stokes claim_ingested.md`

## Overview
A news explainer for a general audience. It covers the Navier–Stokes problem (with a bathtub-drain analogy), OpenAI's forced blow-up claim and run statistics, the forcing technique of Córdoba and Martínez-Zoroa, Buckmaster's account, his questions about his **Codex drafts**, OpenAI's "cannot rule out" statement, and Terence Tao's warning about open science. It is the most balanced popular account in the set. It gives Buckmaster's own disclaimer ("I am not accusing anyone of anything") and raises the **consumer vs enterprise** question of whether his data was eligible for training. The extraction includes some site boilerplate (related stories, comment prompt) but is otherwise complete.

## Key Insights
1. **The claim.** OpenAI used "forcing" (a smooth external nudge). About 10,000 agents worked for about 88 hours, 100 of them starting on Euler. After about 50 hours they found Euler blow-ups, then moved to Navier–Stokes. The singularity is "a vortex spiraling tighter and tighter, stretching and thinning like pulled taffy". The proof was run through **Lean**. Per OpenAI, the agents "sent 2.7 million messages and used approximately 130 billion output tokens". At the 8 Sept news conference, representatives said a similar effort by a customer "would have cost $15 million".
2. **The forcing approach.** It was developed by **Diego Córdoba** (ICMAT, Madrid) and **Luis Martínez-Zoroa** (CUNEF, Madrid). Buckmaster: "The ideas making this line of attack possible are due to Córdoba and Martínez-Zoroa … Almost nobody else I know of was working on it."
3. **Timeline per Buckmaster.**
   - **15 Aug**: he and Alpöge achieved Euler blow-up with smooth forcing.
   - **3 Sept**: he heard "through Alpöge" that OpenAI had caught wind of their progress and adopted the same method ("When I heard 'forced,' it was a bright red flag").
   - **6 Sept**: meeting with OpenAI.

   OpenAI says it launched its effort on **1 Sept**, the day it heard "rumors of other Millennium Prize resolutions". Buckmaster says those rumours concerned his and Alpöge's work. Sam Altman on X: "We were curious if ours could do it too", and "the approaches appear to be different", a claim Buckmaster disputes. OpenAI's statement credits the pair's "independent resolution of the forced Euler problem" and says OpenAI offered to co-publish.
4. **The Codex question (key passage).** Buckmaster used Codex throughout, "putting drafts of the work into the tool". He wrote: "I asked whether the model had been trained on, or had access to, our sessions in Codex, into which we had been putting all our drafts … I asked again, about training, and I did not get an answer."
   - Live Science states that "OpenAI trains its models on user interactions".
   - It notes that enterprise agreements govern customer data, and that "it's unclear whether Buckmaster was using Codex under an enterprise agreement or as an individual consumer — a distinction that may determine whether his drafts were available for training".
5. **OpenAI's data statement (X).** The company denied that employees or agents saw the work "by any means" before release. However, "we cannot rule out that de-identified data derived from their usage of our products helped improve our models."
6. **Authorship and intimidation.**
   - Buckmaster alleges that Bubeck ("who leads OpenAI's math research") twice pushed for Alpöge to be cut, and that at the 6 Sept meeting both options required cutting Alpöge.
   - The quote "Why would you ruin your career?" (title and lede) and "If you don't want me to be nice, then I don't have to be nice" are attributed to Bubeck by Buckmaster.
   - Bubeck: "false and inflammatory"; to Wired: "We did not use their prompt or proofs to prompt our models."
   - Mark Chen (chief research officer) was "a little disappointed with the allegations".
7. **Buckmaster's disclaimer.** "I have not seen OpenAI's proof. I do not know what their model did, or how. I do not know whether our data was used. I am not accusing anyone of anything." He calls for an independent investigation into how OpenAI's work began.
8. **Community.** Córdoba to *Scientific American*: "We're a little bit in shock." Tao (Mastodon): "We have now seen that even the rumor of someone working on a massive problem can trigger a massive amount of AI-powered effort to flatten it … The incentives may now be pointing in the direction of no longer sharing any promising research directions with the broader community, which would reverse centuries of traditions of open science." The proof awaits peer review, and Clay has issued no verdict.

## Relevance to GroundOne
- **The clearest statement of the privacy mechanism.** The question is not whether OpenAI misused data (no evidence; Buckmaster accuses no one). The point is that *the user cannot know*: whether his drafts were eligible for training depended on contract terms he and the journalists could not resolve, and the provider "cannot rule out" a contribution of de-identified data. On a fully local stack this whole category of question disappears: the data never leaves the laptop ([[Privacy and Data Sovereignty]], proposed; [[On-Device Inference]]).
- **A RAG-relevant generalisation.** Grounded verification over confidential or unpublished documents is exactly the setting where sending documents and answers to a cloud judge creates this exposure ([[Retrieval-Augmented Generation]], [[Groundedness Verification]], [[LLM-as-a-Judge]]). GroundOne's 16 GB laptop deployment is the locality answer ([[GroundOne]]).
- **Tao's point on incentives** (researchers may stop sharing promising directions) is a second-order consequence of the same unverifiability, but it concerns open science and is best kept as context.

## Links
- Concepts: [[Navier-Stokes Credit Dispute (2026)]] (proposed), [[Privacy and Data Sovereignty]] (proposed), [[On-Device Inference]], [[Retrieval-Augmented Generation]], [[Groundedness Verification]], [[LLM-as-a-Judge]], [[GroundOne]]
- Related sources: [[Fortune 2026 - OpenAI says it cracked Navier-Stokes, Buckmaster accusation]], [[NYU Shanghai RITS 2026 - OpenAI claims a Navier-Stokes proof amid a dispute over credit]], [[OfficeChai 2026 - OpenAI says it didn't see Buckmaster and Alpoge's work]], [[Plagiarism Today 2026 - Who gets credit when AI makes a breakthrough]]
