---
title: "Live Science 2026 - Why would you ruin your career, OpenAI Navier-Stokes claim"
url: https://livescience.com/physics-mathematics/mathematics/why-would-you-ruin-your-career-openai-claims-to-have-cracked-one-of-maths-greatest-unsolved-problems-but-mathematicians-allege-it-played-dirty
published: 2026-09-09
accessed: 2026-10-11
extracted_with: trafilatura 2.3.1
---

# 'Why would you ruin your career?': OpenAI claims to have cracked one of math's greatest unsolved problems, but mathematicians allege it played dirty

A breakthrough on the Navier-Stokes equations could be worth a $1 million prize, but a mathematician has serious questions about how OpenAI got there so fast.

[Larissa G. Capella](https://www.livescience.com/author/larissa-g-capella)Edited by

[Ben Turner](https://www.livescience.com/author/ben-turner),

[Pandora Dewan](https://www.livescience.com/author/pandora-dewan),

[Brandon Specktor](https://www.livescience.com/author/brandon-specktor),

[Laura Mondragón](https://www.livescience.com/author/laura-mondragon)

[News](https://www.livescience.com/news)

[Follow us](https://google.com/preferences/source?q=livescience.com)

[<u>Tristan Buckmaster</u>](https://cims.nyu.edu/~tristanb/), a mathematician at New York University, had just spent months working on what he believed could be a life-defining mathematical proof. Then, during a Sept. 6 meeting with OpenAI employees, he claims that he was issued a stark warning: "Why would you ruin your career?"

That exchange, which Buckmaster described in a detailed public [<u>statement</u>](https://cims.nyu.edu/~tristanb/statement.pdf) this week, sits at the heart of a ballooning controversy around a famous set of mathematical equations called Navier-Stokes.

OpenAI says its [<u>artificial intelligence</u>](https://www.livescience.com/technology/artificial-intelligence) (AI) model has solved an outstanding problem tied to this 200-year-old set of fluid dynamics equations. The set of equations appears on the list of one of the seven [<u>Millennium Prize Problems</u>](https://www.claymath.org/millennium-problems/) posed by the Clay Mathematics Institute, and its solution comes with a $1 million reward. Buckmaster had been working on the same problem. And he has questions about how the company got there so fast.

## The OpenAI breakthrough

The [<u>Navier-Stokes equations</u>](https://www.grc.nasa.gov/www/k-12/airplane/nseqs.html) were formulated in the early 1800s by Claude-Louis Navier and George Gabriel Stokes. They're basically Newton's second law of motion for fluids, describing how any fluid moves: Push air with a fan blade, and the equations predict how that air will flow; or heat the atmosphere with sunlight, and they help forecast tomorrow's weather. They describe how planes fly and how blood moves through your arteries.

The problem is that nobody has proved whether the equations always produce finite answers. Could there be rare conditions that make the equations go haywire? This is called a "blowup," or singularity, which happens when a quantity that should represent something physical (like fluid speed or pressure) spirals toward impossible infinities at certain points in space and time.

Imagine the swirl of water circling a bathtub drain. The Navier-Stokes equations describe how it spins faster as it tightens toward the center. A blowup would mean the math predicts that spin is accelerating forever — an infinite speed at a single point. The bathtub can't do that, but if the equations can, that means the model we trusted for years is wrong and we wouldn't even know where it breaks.

Whether the Navier-Stokes equations can blow up is one of the most famous unsolved questions.

To find the answer, OpenAI used a technique called "forcing" — giving the simulated fluid a smooth, controlled nudge from the outside. Imagine flicking a spinning top with your finger to see if it would fall over — or, in the case of the Navier-Stokes equations, blow up.

OpenAI set roughly 10,000 AI agents to simultaneously work on the problem. The agents worked for about 88 hours straight, with 100 of them starting with the related [<u>Euler equations</u>](https://cdn.openai.com/pdf/315b36cd-ec98-4023-8342-93345194ece1/euler.pdf). This is a simpler cousin of Navier-Stokes that discards viscosity to describe fluid motion without internal friction.

After roughly 50 hours, OpenAI's agents found blowups in the Euler equations, OpenAI representatives [<u>wrote in a statement</u>](https://openai.com/index/navier-stokes-solution/). This discovery convinced them that Navier-Stokes was within reach, and they turned their attention to the bigger problem.

OpenAI described the singularity as a vortex spiraling tighter and tighter, stretching and thinning like pulled taffy. The result was a fluid that, mathematically, spins itself into infinity.

[<u>OpenAI ran the proof through a program called Lean</u>](https://github.com/openai/NavierStokesAndEuler), software that checks every step of a mathematical argument. The agents "sent 2.7 million messages and used approximately 130 billion output tokens," OpenAI representatives wrote in the statement. At a Sept. 8 news conference, company representatives said a similar effort performed by a customer would have cost $15 million.

## The controversy

The result has created a blowup of its own within [<u>mathematics</u>](https://www.livescience.com/physics-mathematics/mathematics), centered around claims that OpenAI's models may have been given a head start by using the work of Tristan Buckmaster and [<u>Levent Alpöge</u>](https://alpo.ge/), a mathematician at rival AI company Anthropic. 

The two mathematicians had been working on the same strategy (smooth forcing) applied to those same Euler equations. The approach itself was developed by [<u>Diego Córdoba</u>](https://www.icmat.es/people/dcordoba/), a mathematician at the Institute of Mathematical Sciences in Madrid, and [<u>Luis Martínez-Zoroa</u>](https://www.cunef.edu/en/faculty-and-research/martinez-zoroa-luis/), another mathematician at CUNEF University in Madrid. Almost no one else in the field was using it.

Buckmaster said that on Aug. 15 that he and Alpöge achieved blowup results for the Euler equations with smooth forcing. On Sept. 3, Buckmaster wrote that he received word through Alpöge that OpenAI had caught wind of their progress and adopted the same method.

"When I heard 'forced,'" Buckmaster wrote in his public statement, "it was a bright red flag."

His concern was that the smooth-forcing approach wasn't obvious or widespread. "The ideas making this line of attack possible are due to Córdoba and Martínez-Zoroa," Buckmaster wrote, crediting the two mathematicians who developed the technique. "Almost nobody else I know of was working on it."

And yet, [<u>according to OpenAI,</u>](https://openai.com/index/navier-stokes-solution/) the company launched its Navier-Stokes effort on Sept. 1 — the same day it heard "rumors of other Millennium Prize resolutions." Buckmaster claimed, in his public statement, that those rumors were about his and Alpöge's work specifically.

[<u>Sam Altman</u>](https://blog.samaltman.com/), OpenAI's CEO, acknowledged that the company had learned of Buckmaster and Alpöge's work before making its announcement. "We were curious if ours could do it too," he [<u>wrote on X</u>](https://x.com/sama/status/2097385167002415140). He added that "the approaches appear to be different" — a claim Buckmaster disputes.

OpenAI's statement names both Buckmaster and Alpöge, credits their independent resolution of the forced Euler problem, and says the company offered to co-publish.

## "I did not get an answer"

Buckmaster also revealed that he had been using OpenAI's Codex coding assistant throughout his research, putting drafts of the work into the tool. OpenAI trains its models on user interactions, and Buckmaster said he asked the company directly whether his Codex sessions had been accessed.

"I asked whether the model had been trained on, or had access to, our sessions in Codex, into which we had been putting all our drafts," he wrote. "I asked again, about training, and I did not get an answer."

OpenAI's enterprise agreements govern how customer data can be used. But it's unclear whether Buckmaster was using Codex under an enterprise agreement or as an individual consumer — a distinction that may determine whether his drafts were available for training.

[<u>In a statement on X</u>](https://x.com/OpenAI/status/2097375276384567642?s=46), OpenAI representatives denied that company employees or agents saw the pair's work "by any means" until it was publicly released. However, "we cannot rule out that de-identified data derived from their usage of our products helped improve our models," they added.

Then, there is the question of authorship. Buckmaster alleges that [<u>Sébastien Bubeck</u>](http://sbubeck.com/), who leads OpenAI's math research, twice pushed for Alpöge to be cut from the paper that the two mathematicians were preparing. Buckmaster emphasized that Alpöge works at Anthropic, a rival AI company.

It was at that same Sept. 6 meeting that Buckmaster claimed that OpenAI presented him with two options, both of which required cutting Alpöge from authorship. He declined and said he told Bubeck that if OpenAI released its result as proposed, he would go public. Bubeck allegedly replied, "If you don't want me to be nice, then I don't have to be nice."

Bubeck has flatly denied the allegations, calling them "false and inflammatory" in a statement on [<u>X</u>](https://x.com/SebastienBubeck/status/2097214122471432349?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E2097214122471432349%7Ctwgr%5E4bbdc967b3ad2101081f3e0ba76eeb38b61c2850%7Ctwcon%5Es1_c10&ref_url=https%3A%2F%2Fofficechai.com%2Fai%2Fopenais-sebastien-bubeck-calls-tristan-buckmasters-claims-of-trying-to-take-credit-for-fluid-dynamics-proofs-false-and-inflammatory%2F). "We did not use their prompt or proofs to prompt our models," Bubeck told [<u>Wired</u>](https://www.wired.com/story/openai-navier-stokes-math-discovery-academics/). Mark Chen, OpenAI's chief research officer, said at last night's news conference that he was "a little disappointed with the allegations."

"I have not seen OpenAI's proof," Buckmaster wrote. "I do not know what their model did, or how. I do not know whether our data was used. I am not accusing anyone of anything." He has called for an independent investigation into how OpenAI's work began.

In a closing line, he wrote, "I would much rather be talking about mathematics, Luis and Diego's ideas, and what this all means for the rest of us."

## The community response

Córdoba, one of the original developers of the forcing technique, said he was stunned by how quickly the result had materialized. "We're a little bit in shock," he told [<u>Scientific American</u>](https://www.scientificamerican.com/article/openai-claims-blockbuster-math-breakthrough-amid-swirl-of-controversy/).

Other mathematicians have also responded to the news, with some expressing open dismay at how the results were released.

##### Related stories

- [OpenAI's 'smartest' AI model was explicitly told to shut down — and it refused](https://www.livescience.com/technology/artificial-intelligence/openais-smartest-ai-model-was-explicitly-told-to-shut-down-and-it-refused)
- [New kind of AI uses a fresh approach to reasoning — researchers say it costs up to 11 times less to run than a leading OpenAI model](https://www.livescience.com/technology/artificial-intelligence/new-kind-of-ai-uses-a-fresh-approach-to-reasoning-researchers-say-it-costs-up-to-11-times-less-to-run-than-a-leading-openai-model)
- [No, OpenAI's models didn't go 'rogue' when they broke into Hugging Face. Here's what really happened.](https://www.livescience.com/technology/artificial-intelligence/no-openais-model-didnt-go-rogue-when-it-hacked-into-huggingface-heres-what-really-happened)

"We have now seen that even the rumor of someone working on a massive problem can trigger a massive amount of AI-powered effort to flatten it before the original research project has time to reach its full potential," [<u>Terence Tao</u>](https://www.math.ucla.edu/~tao/), a professor of mathematics at UCLA, [<u>wrote on Mastodon</u>](https://mathstodon.xyz/@tao/117237322160500501). "The incentives may now be pointing in the direction of no longer sharing any promising research directions with the broader community, which would reverse centuries of traditions of open science and do serious long-term damage to the future of the field."

OpenAI's proof still awaits formal peer review, and the Clay Mathematics Institute has not yet issued an official verdict confirming or denying OpenAI's proof. But the episode has already surfaced troubling questions for the mathematics community. For example, when a company trains its models on the interactions of millions of users, who really owns the answers that emerge? And what does AI's involvement mean for the [<u>future of the field</u>](https://www.livescience.com/physics-mathematics/mathematics/ai-is-solving-impossible-math-problems-can-it-best-the-worlds-top-mathematicians)?

Those questions, unlike the Navier-Stokes problem, may not have a clean proof.

**Help us improve Live Science Pro:** *We're always trying to make our content better. Leave us feedback about Pro here.*

[news explainers](https://www.livescience.com/tag/news-explainers)

Larissa G. Capella is a science writer based in Washington state. She obtained a B.S. in physics and a B.A. in English creative writing in 2024, which enabled her to pursue a career that integrates both disciplines. She reports mainly on environmental, Earth and physical sciences, but is always willing to write about any science that sparks her curiosity. Her work has appeared in Eos, Science News, Space.com, among others.

You must confirm your public display name before commenting

Please logout and then login again, you will then be prompted to enter your display name.
