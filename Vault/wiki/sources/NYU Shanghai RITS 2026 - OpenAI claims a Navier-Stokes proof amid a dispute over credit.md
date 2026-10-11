---
type: source
author: "NYU Shanghai RITS (\"Provided by Utku Ege Tuluk\"; drafted with AI assistance and reviewed by RITS staff)"
date: 2026-09-09
venue: "NYU Shanghai Research Institute / RITS AI news explainer (published 2026-09-09; retrieved 2026-10-11)"
url: "https://rits.shanghai.nyu.edu/ai/openai-navier-stokes-proof-credit-dispute/"
tags: [source, explainer, navier-stokes, openai, lean, formal-verification, privacy, user-data, credit-dispute, ai-for-math]
---
# NYU Shanghai RITS 2026 – OpenAI Claims a Navier–Stokes Proof, Amid a Dispute Over Credit

**Raw file**: `raw/local_inference/NYU Shanghai RITS 2026 - OpenAI claims a Navier-Stokes proof amid a dispute over credit_ingested.md`

## Overview
A concise and technically careful explainer of the case. It covers what OpenAI claims to have proven (finite-time blow-up for forced Navier–Stokes, with a Lean formalisation), how the run was organised (timeline, agents, tokens), Buckmaster and Alpöge's concurrent preprints, and the credit and data dispute. It ends with a sober assessment of what a Lean proof does and does not guarantee. It is **the most detailed source in the set on the mathematics and the OpenAI timeline**, and it quotes OpenAI's sentence on user data verbatim. The footer states that the post "was drafted with AI assistance and reviewed by RITS staff".

## Key Insights
1. **What OpenAI claims (published 8 Sept 2026).** An analytical proof plus a **Lean** formalisation that "an initially smooth fluid at rest, subject to a smooth applied force and holding finite energy throughout, develops exactly such a singularity". In the Clay problem's notation this is statement "C" ("and, OpenAI says, 'D'"), i.e. **a disproof of global smoothness**, not a proof of it. The mechanism is a vortex that "spirals inward and gets increasingly elongated, like spaghetti"; the terms "must both become big yet cancel in a precise way".
2. **OpenAI's timeline (from its own account).**
   - Training of the internal model ("significantly more capable than GPT‑6 Astra") began **28 Aug**.
   - On **1 Sept**, "after hearing rumors that two Millennium Prize problems had been resolved", OpenAI pointed it at every open problem on the list. Agents had a cached copy of the internet, code execution and group communication, with problem-statement variants per group.
   - Warm-up: about 100 agents for about 50 h produced a disproof of regularity for **unforced Euler**.
   - Then Navier–Stokes, seeded with the Euler result, with Codex consolidating insights. **Resolution on 5 Sept, about 88 h after launch.**
   - Lean formalisation and verification took 17 more hours with GPT‑6 Astra.
3. **Scale.** About 10,000 coordinating agents. Across all problems: 4.9 million messages and about 300 billion output tokens; for Navier–Stokes alone, 2.7 million messages and about 130 billion tokens. Compute cost "millions of dollars" (via Axios). OpenAI "does not intend to claim the $1 million prize".
4. **Buckmaster and Alpöge's work.** Three preprints posted 8 Sept proving finite-time blow-up **with smooth forcing** for the incompressible porous medium equation, 2D Boussinesq and **3D incompressible Euler**, with Lean formalisations in a public repository. First blow-up solution on **15 Aug**, Lean verification on **22 Aug**. Their Navier–Stokes extension is unreleased, and Buckmaster says its Lean verification is incomplete. He called the models' first English write-up "the most horrendous I have ever read" and the moment "a Deep Blue–Kasparov moment".
5. **Dispute.**
   - Buckmaster alleges OpenAI proposed he write up a joint result as sole author, leaving Alpöge off because he works for Anthropic. He also alleges that Bubeck said "Why would you ruin your career?"
   - Bubeck calls the characterisation "false and inflammatory". He says he never asked for Alpöge to be removed from Alpöge's own work, published a message in which he contacts Alpöge to propose a coordinated release, and attributes the confusion to learning on the call that the pair had resolved Euler, not full Navier–Stokes.
6. **The data statements.** Bubeck: "We did not use their prompt or proofs to prompt our models." OpenAI's post: neither researchers nor agents saw the work before release, "**While unlikely, we cannot rule out that de-identified data derived from their usage of our products helped improve our models.**" Sam Altman on X: "Now that we can see their work, the approaches appear to be different." RITS notes the Euler results differ checkably: **OpenAI's is unforced, the pair's is forced.**
7. **Assessment.** "A Lean formalization is a strong guarantee that a proof's steps follow from its stated assumptions", but "not a guarantee that the formal statement is the theorem people think it is". Checking that the formal hypotheses encode the Clay problem is human work still under way. Reactions via *Scientific American*: Córdoba, "We're a little bit in shock"; Luis Silvestre (Chicago), "Yesterday and today are crazy days." The operational question is "what a research group should assume about the frontier lab whose tools it is using", and norms on disclosure, embargo, authorship and data handling "do not yet exist in written form".
8. **Internal inconsistency.** The page says OpenAI's announcement "arrived one day after" the pair "posted" their proofs, but also dates the pair's preprints to 8 Sept, the same day as OpenAI's publication. Other sources put the pair's public release on the night of 7 Sept or the morning of 8 Sept (US time).

## Relevance to GroundOne
- **The citable sentence for the locality pillar** is OpenAI's own wording here: "While unlikely, we cannot rule out that de-identified data derived from their usage of our products helped improve our models." Even the provider can only call reuse of a user's data "unlikely", not exclude it. A user who submits unpublished work to a cloud model therefore cannot verify afterwards how it was used. Local inference removes the question, because the data never leaves the device ([[Privacy and Data Sovereignty]], proposed; [[On-Device Inference]]).
- **Honest limits.** RITS reports no evidence of misuse. The approaches are said to differ (unforced vs forced Euler), and the dispute is mainly about **credit and authorship**. The thesis should use the case to illustrate the *unverifiability* of cloud data handling, not to allege misuse.
- **The RITS framing fits the thesis.** "What a research group should assume about the frontier lab whose tools it is using" is the same concern that motivates verifying RAG answers locally over confidential documents ([[Retrieval-Augmented Generation]], [[Groundedness Verification]]).
- Side note: the Lean caveat (a formal proof guarantees the steps, not that the statement is the intended one) parallels the thesis's own caution that a verifier checks support against the given document, not truth.

## Links
- Concepts: [[Navier-Stokes Credit Dispute (2026)]] (proposed), [[Privacy and Data Sovereignty]] (proposed), [[On-Device Inference]], [[Retrieval-Augmented Generation]], [[Groundedness Verification]]
- Related sources: [[Fortune 2026 - OpenAI says it cracked Navier-Stokes, Buckmaster accusation]], [[OfficeChai 2026 - OpenAI says it didn't see Buckmaster and Alpoge's work]], [[Plagiarism Today 2026 - Who gets credit when AI makes a breakthrough]], [[Live Science 2026 - Why would you ruin your career, OpenAI Navier-Stokes claim]]
