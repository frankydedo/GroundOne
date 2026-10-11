---
title: "NYU Shanghai RITS 2026 - OpenAI claims a Navier-Stokes proof amid a dispute over credit"
url: https://rits.shanghai.nyu.edu/ai/openai-navier-stokes-proof-credit-dispute/
published: 2026-09-09
accessed: 2026-10-11
extracted_with: trafilatura 2.3.1
---

# OpenAI Claims a Navier–Stokes Proof, Amid a Dispute Over Credit

[Provided by Utku Ege Tuluk](https://library.nyu.edu/people/utku-ege-tuluk/)

**On September 8, 2026, OpenAI published a claimed resolution of the Navier–Stokes existence and smoothness problem** — one of the Clay Mathematics Institute’s seven Millennium Prize Problems — together with a formalization in the Lean proof assistant. The company says the proof was produced by roughly 10,000 coordinating agents running on an unreleased internal model, over about 88 hours. The announcement arrived one day after NYU mathematician Tristan Buckmaster and Anthropic researcher Levent Alpöge posted their own Lean-verified blow-up proofs for related fluid equations, and the two releases have become the subject of a public dispute over credit.

Intermediate

## What Was Claimed

The Navier–Stokes equations apply Newton’s second law to a fluid treated as a continuous medium, and they underpin aircraft design, weather forecasting, and models of blood flow. The Millennium Prize question asks whether a three-dimensional incompressible fluid that starts out moving smoothly can stop being smooth — whether speeds inside it can grow without bound in finite time, despite viscosity, which tends to damp motion out.

OpenAI states that its system produced an analytical proof and a Lean formalization that an initially smooth fluid at rest, subject to a smooth applied force and holding finite energy throughout, develops exactly such a singularity. In the Clay problem’s own notation, this establishes statement “C” — and, OpenAI says, “D” — meaning the result is a disproof of global smoothness rather than a proof of it.

The mechanism is a vortex. In OpenAI’s description, the swirl “spirals inward and gets increasingly elongated, like spaghetti,” its central region shrinking as it speeds up in a way that keeps total energy finite. The difficulty, the company writes, is that the acceleration, pressure-gradient, momentum-transfer and viscosity terms “must both become big yet cancel in a precise way,” so that the breakdown emerges from the fluid’s own motion rather than from an infinite force applied by hand.

## How the Result Was Produced

OpenAI’s account of the run is unusually specific. Training on the internal model — described as “significantly more capable than GPT‑6 Astra” — began August 28. On September 1, after hearing rumors that two Millennium Prize problems had been resolved, the company pointed the model at every open problem on the list. Agents were given a cached copy of the internet and the ability to run code, then split into groups that could communicate internally, with different groups receiving different variants of each problem statement.

A warm-up problem came back first: roughly 100 agents working about 50 hours produced a disproof of regularity for the Euler equations — Navier–Stokes with the viscosity term removed — in the unforced case. OpenAI then concentrated resources on Navier–Stokes, seeding the agents with the Euler result and using Codex to consolidate insights across groups. The resolution arrived September 5, about 88 hours after launch; Lean formalization and verification took a further 17 hours via GPT‑6 Astra. Across all attempted problems the agents exchanged 4.9 million messages and produced about 300 billion output tokens, of which 2.7 million messages and roughly 130 billion tokens went to Navier–Stokes. On a call with reporters, OpenAI executives put the compute cost in the “millions of dollars,” Axios reported. The company says it does not intend to claim the $1 million prize.

## The Concurrent Work and the Dispute

Buckmaster and Alpöge posted three preprints on September 8 establishing finite-time blow-up with smooth forcing for the incompressible porous medium equation, the two-dimensional Boussinesq system, and the three-dimensional incompressible Euler equations, with Lean formalizations in a public repository. Per their account, the first blow-up solution came on August 15 and Lean verification followed on August 22. Their extension to Navier–Stokes has not been released; Buckmaster has said the Lean verification for it is incomplete. Buckmaster described the models’ first English write-up as “the most horrendous I have ever read,” and called the moment “a Deep Blue–Kasparov moment” for mathematics.

Buckmaster has publicly alleged that OpenAI proposed he write up a joint result as sole author, leaving Alpöge off the paper because Alpöge works for Anthropic, and that when he said he would make their interactions public, OpenAI researcher Sébastien Bubeck responded, “Why would you ruin your career?” Bubeck has called Buckmaster’s characterization “false and inflammatory.” In a fuller statement, Bubeck said he had never asked for Alpöge to be removed from Alpöge’s own work and published a message showing him contacting Alpöge directly to propose a coordinated release; by his account, the confusion arose during a call on which he learned the pair had resolved Euler rather than the full Navier–Stokes problem. On the question of data, Bubeck said, “We did not use their prompt or proofs to prompt our models.” OpenAI’s post states that neither its researchers nor its agents saw the pair’s work before public release, while adding: “While unlikely, we cannot rule out that de-identified data derived from their usage of our products helped improve our models.” Writing on X, OpenAI CEO Sam Altman said, “Now that we can see their work, the approaches appear to be different.” The two Euler results do differ in a checkable respect — OpenAI’s is the unforced case, Buckmaster and Alpöge’s the forced one.

## What This Means

The mathematical claim and the credit dispute are on different clocks. A Lean formalization is a strong guarantee that a proof’s steps follow from its stated assumptions, and it is why both parties could publish within days rather than months. It is not a guarantee that the formal statement is the theorem people think it is — checking that the formalized hypotheses faithfully encode the Clay problem is human work, and that reading is still under way across the fluid-dynamics community. Reactions collected by *Scientific American* reflect the pace: Diego Córdoba, whose “forcing” approach underlies the recent progress, said, “We’re a little bit in shock,” and Luis Silvestre of the University of Chicago said, “Yesterday and today are crazy days. We’re all, in the community, discussing the implications of this.”

The operational question here is narrower than “can AI do mathematics.” It is what a research group should assume about the frontier lab whose tools it is using, and what norms — disclosure, embargo, authorship, data handling — the field wants around results produced this way. Those norms do not yet exist in written form, which is why a week of private calls and rumors has ended up being adjudicated on social media.

## Related Coverage

- [OpenAI Launches GPT-6 Astra, Its First ‘Critical’ Cyber Model](https://rits.shanghai.nyu.edu/ai/openai-gpt-6-astra-critical-cyber/) — the released model that OpenAI says its internal system now outperforms, and the one used for the Lean verification step.
- [AI Wins Gold at 2025 International Mathematical Olympiad](https://rits.shanghai.nyu.edu/ai/ai-wins-gold-at-2025-international-mathematical-olympiad/) — the previous marker on this curve, fourteen months earlier.
- [OpenAI Launches GPT-5.6 Family: Sol, Terra, and Luna](https://rits.shanghai.nyu.edu/ai/openai-launches-gpt-5-6-family-sol-terra-and-luna-reach-general-availability/) — one of the model families Buckmaster lists among the tools used on the Euler write-ups.

*This post was drafted with AI assistance and reviewed by RITS staff.*
