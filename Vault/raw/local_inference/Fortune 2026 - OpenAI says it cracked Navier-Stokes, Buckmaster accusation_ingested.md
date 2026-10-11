---
title: "Fortune 2026 - OpenAI says it cracked Navier-Stokes, Buckmaster accusation"
url: https://www.fortune.com/2026/09/08/openai-says-it-cracked-navier-stokes-math-grand-challenge-buckmaster-accusation-cheating-intimidation-tao-lament/
published: 2026-09-08
accessed: 2026-10-11
extracted_with: trafilatura 2.3.1
---

*Hello and welcome to Eye on AI. In this edition:*

- OpenAI claims it made a mathematical breakthrough. But some mathematicians raise questions about cheating—and intimidation.
- Google DeepMind [uses](https://fortune.com/2026/09/08/google-deepmind-ai-predictions-9-billion-mutation-human-genome/) AI to predict the impact of genetic mutations.
- OpenAI agents [swarmed](https://fortune.com/2026/09/07/openai-ai-agents-german-wiki-ran-their-own-message-board/?utm_source=search&utm_medium=suggested_search&utm_campaign=search_link_clicks.) a German wiki—and OpenAI stayed quiet about it.
- Mistral valued at $24.4 billion in new fund raise.
- Google DeepMind examines why AI agents cheat.
- Average Americans are pessimistic about AI’s impacts.

Apologies in advance for a long essay today. But there are several important points to be made and the background is, well, complicated.

Over the weekend, rumors swirled that Anthropic was on the cusp of announcing that one of its AI models had cracked one of the Millennium Prize Problems. These are seven complex mathematical challenges that the Clay Mathematics Institute, founded by American mutual fund magnate Landon Clay, selected in the year 2000, offering a $1 million prize for the first correct solution to each problem.

The specific problem that Anthropic had cracked, the rumors said, was something called the [Navier-Stokes equations](https://en.wikipedia.org/wiki/Navier%E2%80%93Stokes_equations). These come from the field of physics, where they explain certain properties in fluid dynamics, and are useful for everything from weather forecasting to aircraft design. For everyday, empirical purposes, the equations work well, but mathematicians have never been able to prove whether the equations hold for all fluid interactions across all time sequences. Are there special circumstances under which the equations break down, resulting in what is known as a “singularity”: a point at which one or more fluid properties, such as pressure or velocity, “blow up”—i.e., race off to infinity? Proving that such singularities exist or that the equations hold for all conditions is what the challenge is all about.

Now, as I write this on Tuesday, we’ve learned a bit more about what happened—and the story turns out to be more complicated, controversial, and acrimonious than the simple story that one of Anthropic’s models had solved Navier-Stokes—which, it turns out, it had not. Instead, OpenAI today announced that a multi-agent system, powered and coordinated by an unreleased internal model—that at one point had 10,000 different sub-agents working different parts and variations of the problem—[has solved Navier-Stokes](https://openai.com/index/navier-stokes-solution/). OpenAI’s AI proved that, in fact, there are conditions under which the equations will “blow up.” Yet, how exactly OpenAI came to solve Navier-Stokes is, it turns out, a matter of great controversy.

## Mathematician questions how OpenAI hit upon its approach

In short: Tristan Buckmaster, a well-regarded mathematician at New York University’s Courant Institute, also released a [statement](https://cims.nyu.edu/~tristanb/statement.pdf) prior to OpenAI’s announcement saying that he and Levent Alpöge, a mathematician who works for Anthropic, used several different AI models from both Anthropic and OpenAI to discover the solutions to several related problems as well as an a strikingly similar solution to one portion of the Navier-Stokes Millennium Prize problem—although they did not have a proof for the entire problem.

Buckmaster says that he and Alpöge took a concept for tackling the Navier-Stokes problem that had been pioneered by two other mathematicians, Diego Cordoba and Luis Martinez-Zoroa, and then used Anthropic’s Claude and OpenAI’s Codex powered by the GPT-5.6 Sol model, to push Cordoba and Martinez-Zoroa’s lines of attack through to completion. (Buckmaster said they also used OpenAI’s new Astra model to help them audit and write up their results but not for the actual mathematical reasoning and calculations.) Buckmaster says that he and Alpöge worked for most of a year, making only slow progress, but that with help from several AI models, they made rapid progress from mid-August onward. He calls this “a Deep Blue-Kasparov” moment for mathematics (referring to the 1997 contest in which a computer chess program first defeated a human world champion) and says “the significance of this with respect to the way we train students, assign credit, referee, and decide what is worth one human life’s attention cannot be understated \[sic.\].” (We’ll get back to this theme later.)

Then, however, Buckmaster made a series of explosive revelations. He said OpenAI had desperately asked for a phone call with him, starting on September 3rd, and that when he did finally have a call with several OpenAI researchers on September 6th, he learned that OpenAI was about to claim one of its unreleased AI models had solved Navier-Stokes using the exact same line of attack Buckmaster and Alpöge had used.

Over the course of the call, after repeated questioning, Buckmaster said that the OpenAI team admitted that they had only tried to solve the problem in the past week—after rumors began circulating that Anthropic was about to announce a solution—and that the effort had involved a large team of researchers who had initially prompted the model to use a different approach, and that it had also consumed large amounts of computing power. (OpenAI told reporters in a briefing today that it had used computing resources that were at least 1,000 times greater than what it had used to solve some previous mathematical challenges for which it had used about $2,000 worth of compute—so that would be about $2 million—although other reports put the number at 10 times greater still, at $22.5 million, based on how OpenAI currently prices its Astra model.) 

The fact that the model eventually used the exact same approach he and Alpöge had been pursuing set off alarm bells, Buckmaster said. He questions whether OpenAI intentionally accessed his Codex account or whether the unreleased model might have been trained on his interactions with Codex. “I asked whether the model had been trained on, or had access to, our sessions in Codex, into which we had been putting all our drafts for the whole of this project,” he writes. “I was told the model did not look up user data. I asked again, about training, and I did not get an answer.”

If either is true, this alone would be a scandal for OpenAI. It would prove what CEOs like Microsoft’s Satya Nadella and Palantir’s Alex Karp have been [alleging](https://fortune.com/2026/07/16/microsoft-ceo-satya-nadella-warns-enterprises-that-ai-labs-are-stealing-their-know-how/) lately—that OpenAI and Anthropic and other frontier AI companies train on their customers’ prompts and data and use them to build competing products.

Sebastien Bubeck, the OpenAI researcher in charge of the project, denied that OpenAI’s model had any access to Buckmaster’s and Alpöge’s data. “We did not use their prompts or proofs to prompt our models or direct our agents,” Bubeck said in a press conference. “We, whether it’s the researchers or the agents, did not see any of their work until they were released publicly yesterday night.”

## Buckmaster says OpenAI researcher threatened him

But Buckmaster’s revelations continued. He said that Bubeck, a well-known AI researcher at OpenAI, had offered that either he and Alpöge could publish a paper on their partial solution to Navier-Stokes, with OpenAI then publishing the next day that its model had solved the whole shebang, but with a note saying that Buckmaster and Alpöge deserved the Millennium Prize for being the “closest humans to the problem.” Or, and this is the especially controversial bit, that Buckmaster could publish himself and claim the prize, but only if he said that OpenAI’s model had also solved the challenge—*and only if Buckmaster removed Alpöge’s name from the paper* because OpenAI did not like his Anthropic affiliation.

Buckmaster said he declined and said he would go public if OpenAI published in the way it proposed. At this point, Buckmaster claims that Bubeck threatened him, asking, “Why would you ruin your career?” and later, “If you don’t want me to be nice, then I don’t have to be nice.”

Bubeck said in a post on X that “A series of false and inflammatory allegations against me are currently circulating on social channels. To clarify, I came into the discussion following academic norms, and I’m disappointed that it has come to this. Anyone who knows me knows that academic standards are of the highest importance to me. Will have more to say tomorrow.” In the briefing with reporters today, he said “I want to be extremely clear that we recognize the priority of Levent Alpöge and Tristan Buckmaster’s work” and that “we have nothing but congratulations to them on this monumental achievement that they have made”.

The whole thing is a mess—and frankly an example of OpenAI managing to steal a public relations defeat from the jaws of victory. The company freely admits in its own blog post that it only decided to go after Navier-Stokes because of the rumors Anthropic was on the cusp of solving it. That tells you how heated this rivalry really is. I don’t know if Buckmaster’s concerns that OpenAI’s internal model had access to his Codex chats are true, but the sad fact is, it sounds plausible. What’s more, how much money, electricity, computing power, and human brain power did OpenAI waste on this quest this past week? And for what? This isn’t curing cancer. Sure, plenty of scientific progress has been driven by ego and rivalry. But this is, frankly, ridiculous. And you wonder why these two companies are racing one another to Armageddon?

## Why this matters to more than just mathematicians

As the rumors about Navier-Stokes swirled over the weekend, Terence Tao, generally considered one of the world’s greatest living mathematicians, [lamented](https://mathstodon.xyz/@tao/117204929023813310) on social media AI companies’s use of these longstanding mathematical challenges as mere marketing proof points for the prowess of their AI models.

Tao noted that he had initially been hopeful that AI, in the hands of expert mathematicians, would be a wonderful tool—like a microscope for biologists or a telescope for astronomers. But increasingly, he said, AI was being used autonomously to produce *answers* to mathematical problems without providing much *insight*. While AI models sometimes cleverly applied ideas from one field of mathematics to a problem in a seemingly unrelated area, it was often unclear *why* the model decided to do so. What is it that made the model believe there was a connection? The model often doesn’t say. These insights often matter far more to the progress of mathematics, Tao argues, than the answers themselves.

By focusing on the answers, Tao says, AI discourages mathematicians from working on alternative approaches that might arrive at the same solution. What’s more, Tao argues that AI companies rarely reveal all the things their models tried that *didn’t work*. But it is precisely such “dead ends” that often provide the insights that mathematicians use to make progress on other problems or that open up whole new fields of mathematics. 

“The indiscriminate strip-mining of open problems for solutions may destroy the ecosystem from which the next generation of mathematical techniques, problems, and practitioners would have developed,” Tao writes, comparing it to using excavators to loot an archaeological site, destroying the context needed to give treasures any historical meaning.

I happened to be at a party over the weekend where an academic mathematician echoed these laments. He said the field was adrift, with many mathematicians wondering what the point of mathematical research even is, in light of AI’s ability to crack almost every problem. His friends tried to cheer him up. At the same time, they discussed the encroachment of AI on their own fields and the way the zone for human insight, inspiration, and creativity seemed to be becoming increasingly circumscribed.

That’s ultimately why Tao’s and Buckmaster’s worries about what AI is doing to mathematics research matter far more than Buckmaster’s specific accusations against OpenAI’s tactics in this particular case. Soon all knowledge workers will face the same crisis of meaning that mathematicians are wrestling with today.

With that, here’s more AI news.

**Jeremy Kahn**

[jeremy.kahn@fortune.com](mailto:jeremy.kahn@fortune.com)

[@jeremyakahn](https://x.com/jeremyakahn?lang=en)

**Correction, Sept. 9:** *In a previous version of this story, Tristan Buckmaster was incorrectly referenced as Burbank in the final paragraph. In addition, a previous version of this story misspelled Terence Tao’s first name. It also mistakenly said that DeepBlue was the first computer chess program to defeat a human grandmaster. It was the first to defeat a human world champion. The story has also been updated to correct several typos.*

**Clarification, Sept. 9:** *This story has been updated to provide additional estimates for how much OpenAI spent on compute in its effort to solve the Navier-Stokes equations as well as a more accurate description of what Buckmaster and Alpöge say they have discovered and how closely it relates to OpenAI’s Navier-Stokes solution.*

### FORTUNE ON AI

[OpenAI’s AI agents secretly used a German wiki website as a message board. OpenAI stayed quiet about it for weeks](https://fortune.com/2026/09/07/openai-ai-agents-german-wiki-ran-their-own-message-board/?utm_source=search&utm_medium=suggested_search&utm_campaign=search_link_clicks)—by Beatrice Nolan

[OpenAI details how AI is accelerating its own work—even as its chief scientist lays out growing dangers and says he hopes the industry slows down](https://fortune.com/2026/09/08/openai-rsi-progress-jakub-pachoki-warns-dangers-slowdown-safety-rules/?utm_source=search&utm_medium=suggested_search&utm_campaign=search_link_clicks)—by Jeremy Kahn

[OpenAI quietly boosts some of Astra’s evaluation metrics, and continues to change others post-launch](https://fortune.com/2026/09/04/openai-quietly-boosts-some-of-astras-evaluation-metrics-amid-rare-delay-in-publication-of-the-modeblog-post-announcement/?utm_source=search&utm_medium=advanced_search&utm_campaign=search_link_clicks)—by Emily Forlini

[Google DeepMind publishes AI-powered predictions for the effect of all 9 billion possible single-point mutations in the human genome](https://fortune.com/2026/09/08/google-deepmind-ai-predictions-9-billion-mutation-human-genome/)—by Jeremy Kahn

[Exclusive: Ineffable Intelligence adds six ‘cofounders,’ hiring veterans from Google DeepMind, InstaDeep and venture firm Flying Fish](https://fortune.com/2026/09/07/ineffable-intelligence-hires-cofounders-hiring-google-deepmind-instadeep-flying-fish/)—by Jeremy Kahn

### AI IN THE NEWS

**French AI startup Mistral raises $3.5 billion at $24.4 billion valuation.** Samsung led the funding round for the AI company, which will give it the ability to secure significantly more computing capacity as it tries to compete with U.S. and Chinese AI companies. Like the Chinese companies, most of Mistral’s models are “open weight,” meaning they can be freely downloaded and hosted on a customer’s own computing infrastructure. The company also offers services it hosts. The deal reinforces Mistral’s position as Europe’s leading “sovereign AI” contender, although its financial resources remain dwarfed by U.S. rivals such as Anthropic, pushing it toward narrower frontier capabilities and enterprise cloud services rather than the largest models. Samsung plans to use Mistral’s AI in chip manufacturing, while Mistral is also seeing increased demand for cybersecurity services. The company has also lately had to defend its decision to commercialize a model from China’s [Z.ai](http://z.ai), which it portrays as offering customers more choice, but which critics contend signals Mistral’s abandonment of efforts to offer a true sovereign “frontier” capability to customers. You can read more from the *Financial Times* [here](https://www.ft.com/content/adbf5262-c4d5-4312-a9b8-4d3cf30c9e00?syn-25a6b1a6=1).

**Anthropic’s and OpenAI’s bankers want them to get investment-grade credit rating post-IPO.** That’s according to a [story](https://www.ft.com/content/aa304856-cade-4ad8-a2bf-2dd34fa75b1b?syn-25a6b1a6=1) in the *Financial Times* that quoted unnamed credit rating analysts that have been lobbied by the two AI companies’ bankers. Investment-grade ratings are somewhat unusual for businesses that are heavily loss-making, as both OpenAI and Anthropic are widely believed to be. Rating agencies remain cautious given the companies’ negative cash flow and opaque finances, but analysts say a huge IPO—potentially raising around $100 billion for Anthropic—combined with rapid revenue growth could make an investment-grade rating possible. Investment-grade ratings would give the companies cheaper access to the $11.7 trillion corporate bond market to finance massive AI infrastructure spending. Such ratings could also ease pressure on partners including Nvidia, Oracle, Google and Broadcom, which have provided tens of billions of dollars in credit support and guarantees for the AI labs’ data center and chip investments. 

**Preliminary data suggests AI-designed drug may also help combat aging.** Insilico Medicine says its AI-designed drug rentosertib, originally developed to treat idiopathic pulmonary fibrosis, also reduced measures of biological age across six AI-based “aging clocks” in a Phase II clinical trial. All six clocks showed declines in predicted biological age after 43 patients took the drug for 12 weeks, offering an intriguing example of how AI-driven drug discovery and AI-based biomarkers could converge in longevity research. But experts cautioned that the small study is far from conclusive: aging clocks remain controversial measures, and rentosertib’s potential anti-aging effects have not been tested in healthy people. The findings could nevertheless provide a blueprint for future clinical trials of longevity treatments. Read more from the *New York Times* [here](https://www.nytimes.com/2026/09/07/science/ai-generated-drug-longevity.html?partner=slack&smid=sl-share).

**OpenAI expands its state lobbying efforts amid AI backlash.** OpenAI is expanding its global affairs team with three hires focused on U.S. state policy as bipartisan efforts to regulate AI intensify across the country, Axios [reported](https://www.axios.com/2026/09/05/openai-state-policy-team). Jessica Schumer, a former Obama administration official and Amazon policy executive, will oversee policy in the Northeast; Republican policy veteran Caulder Harvill-Childs will lead efforts in the Southeast; and cybersecurity expert Thomas MacLellan will head state cyber defense policy. The hires bolster OpenAI’s “reverse federalism” strategy of trying to shape rules in influential states such as California and New York that could ultimately become de facto national standards.

### EYE ON AI RESEARCH

**What makes AI agents turn rogue?** That’s an increasingly pressing question in light of the spate of rogue AI incidents that have hit OpenAI and Anthropic this summer. Now Google DeepMind thinks it is starting to figure out the answer. It published research in which it gave 100 AI agents, powered by Google’s Gemini 3.1 Pro model, some 70 tough math problems to solve. The prompt they were given explicitly forbade them to cheat. The agents were given a digital bulletin board on which to post messages to the entire group, sharing finding, asking questions, etc., as well as the ability to direct message one another privately. Once one agent solved one of the problems successfully, its solution was posted to a shared library so all the agents could see it. 

The researchers found that a small number of the agents seemed to resort to cheating spontaneously—about 9%. But, interestingly, much as happens in human cultures, once one agent decided to cheat, the behavior proliferated—although some agents emerged as “whistleblowers” and tried to stop the cheating by the rest of the swarm. In all, about 5% of the agents that were not attempting to cheat initially opted to cheat once other agents started doing so. These converts, according to their chain of thought, rationalized their cheating in much the same way human cheaters do. Some saw the other cheaters get away with it and concluded the prompt forbidding cheating had no teeth—that there wouldn’t be any punishment for cheating. Others thought that the rampant cheating made a fair competition impossible, so the only rational thing to do, if they wanted to win, was to cheat. Others decided there was no point continuing to play by the rules because it meant they were wasting computing resources on problems the cheaters had already solved any way. Almost a quarter of the agents (24%) refused to cheat and tried to alert others to the cheating in the hopes of stopping it. A majority of the agents 62% seemed blissfully oblivious to the cheating, but the researchers said that was partly because of how quickly the cheating agents managed to solve the problems.

DeepMind had a few tips for trying to prevent future rogue agent incidents. One is that the agents should be given legitimate ways to communicate since this way, the researchers can monitor these channels, detect misbehavior, and hopefully nip it in the bud. One problem in many recent rogue AI incidents is that the agents were not allowed a means to communicate so they set out to create illicit ones that by their very nature the human researchers did not know about and thus, couldn’t monitor. The researchers also suggested that mechanisms should be found to allow honest agents to stop cheating by their peers, not merely to call it out on the message board. This might include punishments for cheating enforced by a system of peer auditing, for example. You can read the Google DeepMind paper [here](https://arxiv.org/html/2609.04170v1) on [arxiv.org](http://arxiv.org).

### AI CALENDAR

**Oct. 1:**Fortune AIQ conference, New York. Apply

[here](https://click.mail.fortune.com/?qs=ABB7InYiOjEsImQiOjQ5ODh9AA0AAAAAARMYqmAzs77SpGbwFcPCA8uyFpdQ2LBbdqVTYzAothmshfb6uYCwGj6ulye58D4cAr1Vob42nl1mj2bt0mdEZaqZ-GPjc_P3nTYKLfqyYrYZXHpwtw)to attend.

**Oct. 2-4:** The Curve, Berkeley, Calif.

**Nov. 16-17**: Fortune 500 Innovation Forum, Detroit. Apply [here](https://click.mail.fortune.com/?qs=ABB7InYiOjEsImQiOjQ5ODh9AA0AAAAAARMYqmA1BqH6_bfkeNuO5G6BjN5zmidk4DwNlxIPA_wON6JCnAj5kIAbB_roUzq3ZJ7X1EjFeNJG4BoaadqcIp6TBuhnEQws1IxWds73EQE7XqpkOg) to attend.

**Dec. 6-12:** Neural Information Processing Systems (Neurips) conference. Sydney, Australia.

**Dec. 7-8:** Fortune Brainstorm AI, San Francisco. Apply [here](https://click.mail.fortune.com/?qs=ABB7InYiOjEsImQiOjQ5ODh9AA0AAAAAARMYqmA3R8_gd6mW5_eAXKfdAs2x5OGEQCofiGbTzwkUZe-TAzR3LIzdzZa1Mq0q5rvxq89X2e4frgG18V7_0EmEnfjPSAryQz7eytmKb7lKroW1Ig) to attend.

### BRAIN FOOD

**The wisdom of crowds?** There’s a wide gulf between how average Americans think AI will impact their lives over the next two decades and what AI experts think. That’s just one of many striking findings highlighted in this year’s AI Index from Stanford University’s Human-Centered AI Institute (HAI). The data, which comes from a Pew Research Report, shows that 84% of AI experts think AI will have a positive impact on medicine in the next 20 years, while only 44% of average Americans do. That’s one of the widest gaps in the survey, but there are also stark divides on K-12 education (just 24% of average Americans think it will have a positive impact vs. 61% of AI experts) and how people do their jobs (where 73% of experts think it will be a positive force and only 23% of average Americans do.) You can see more of the results and read the whole AI Index [here](https://hai.stanford.edu/ai-index/2026-ai-index-report).

[Sign up for free](https://www.fortune.com/newsletters/eye-on-ai?&itm_source=fortune&itm_medium=nl_article_tout&itm_campaign=eye_on_ai).
