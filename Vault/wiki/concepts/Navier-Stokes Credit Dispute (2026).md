---
type: concept
tags: [concept, case-study, privacy, cloud-ai, openai, codex, credit, locality-pillar]
---
# Navier–Stokes Credit Dispute (2026)

In September 2026 OpenAI announced an AI-produced proof on the Navier–Stokes Millennium problem, and two mathematicians who had been working on the same direction, partly inside an OpenAI product, disputed the credit. For the thesis the case matters for one narrow reason: it shows that a user who puts unpublished work into a cloud model cannot verify afterwards how that data was used. See [[Privacy and Data Sovereignty]].

## What was claimed
- **OpenAI, 2026-09-08**: a forced blow-up for the 3D incompressible Navier–Stokes equations: an initially smooth fluid at rest, with a smooth applied force and finite energy, develops a singularity in finite time (Clay statement C, "and D" according to OpenAI). Produced by an internal multi-agent system (about 10,000 agents; for Navier–Stokes alone about 2.7M messages and 130B tokens; about 88 h from launch), formalised in Lean in about 17 h ([[NYU Shanghai RITS 2026 - OpenAI claims a Navier-Stokes proof amid a dispute over credit|RITS]]).
- **Status**: no peer review yet; the Clay Institute still lists the problem as unsolved. Lean guarantees the steps, not that the formal statement encodes the Clay problem as intended (RITS, [[Live Science 2026 - Why would you ruin your career, OpenAI Navier-Stokes claim|Live Science]], [[OfficeChai 2026 - OpenAI says it didn't see Buckmaster and Alpoge's work|OfficeChai]]).
- **Buckmaster (NYU) and Alpöge (Anthropic)**: forced blow-up results for the porous medium, 2D Boussinesq and 3D Euler equations, obtained with AI assistance and verified in Lean, released 2026-09-07/08; their Navier–Stokes proof was incomplete.

## Timeline (cross-checked; sources disagree on some steps)
| Date (2026) | Event | Sources |
| --- | --- | --- |
| 15 Aug | Buckmaster–Alpöge forced Euler blow-up; Lean check 22 Aug | RITS, Live Science |
| 1 Sep | OpenAI hears rumours of the result and launches agents on the Millennium problems | RITS, Live Science, PT (Fortune: rumour was about Anthropic) |
| 3 Sep | Contact between Buckmaster and OpenAI (accounts differ on who initiated it) | Fortune, OfficeChai, Live Science, PT |
| 5 Sep | OpenAI's Navier–Stokes resolution | RITS |
| 6 Sep | Call(s) with Sébastien Bubeck; authorship offers that, per Buckmaster, would have dropped Alpöge; Bubeck denies it | Fortune, Live Science, PT, RITS |
| 7–8 Sep | Buckmaster's statement and the pair's Lean preprints; OpenAI's announcement and statement on X | all |

## The data question (the part relevant to the thesis)
- The pair had been writing their drafts in **OpenAI's Codex**. Buckmaster: "I asked whether the model had been trained on, or had access to, our sessions in Codex, into which we had been putting all our drafts" ([[Fortune 2026 - OpenAI says it cracked Navier-Stokes, Buckmaster accusation|Fortune]], Live Science).
- **OpenAI**: researchers and agents "did not see any of their work through any means until they released it publicly", "no specific user data was accessed", but "While unlikely, we cannot rule out that de-identified data derived from their usage of our products helped improve our models" (RITS and Live Science verbatim; OfficeChai).
- Live Science notes it was unclear whether Buckmaster used Codex as a consumer or under an enterprise agreement, which may decide whether his sessions were eligible for training.
- Buckmaster himself said he was "not accusing anyone of anything" (OfficeChai).

## Honest reading for the thesis
- **Nothing in the sources shows that private data was misused.** The dispute is mainly about credit and about the compute gap between a lab and two researchers ([[Plagiarism Today 2026 - Who gets credit when AI makes a breakthrough|Plagiarism Today]]; Terence Tao on the "strip-mining of open problems", Fortune).
- **What it does show**: once work is inside a hosted model, neither the user nor, by its own statement, the provider can rule out that it contributed to the provider's models. The guarantee is contractual and unverifiable; the user's only evidence is the provider's word.
- **With local inference the question does not arise**: the data never leaves the device ([[On-Device Inference]]). This is the strongest concrete example available for the privacy argument of Ch. 1, if phrased as an *unverifiable risk*, not as proven misuse. Note: Codex, not ChatGPT conversations.

## Source quality
- Use **RITS** and **Live Science** for verbatim quotes; RITS states it was drafted with AI assistance. **Fortune** is a newsletter with opinion. **OfficeChai** inverts which Euler result is forced. **Plagiarism Today** is opinion with factual slips. Cost estimates vary ($2M–$22.5M; $15M customer-equivalent).

## Links
- Sources: [[Fortune 2026 - OpenAI says it cracked Navier-Stokes, Buckmaster accusation]], [[NYU Shanghai RITS 2026 - OpenAI claims a Navier-Stokes proof amid a dispute over credit]], [[OfficeChai 2026 - OpenAI says it didn't see Buckmaster and Alpoge's work]], [[Plagiarism Today 2026 - Who gets credit when AI makes a breakthrough]], [[Live Science 2026 - Why would you ruin your career, OpenAI Navier-Stokes claim]]
- Concepts: [[Privacy and Data Sovereignty]], [[On-Device Inference]]
