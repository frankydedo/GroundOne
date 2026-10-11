---
title: "Level1Techs - ASRock Intel Arc Pro B60 24 GB for local AI"
url: https://forum.level1techs.com/t/asrock-intel-b60-24-gb-for-local-ai/251192
published: 2026-06-09
accessed: 2026-10-11
extracted_with: trafilatura 2.3.1
---

So, short and sweet - looking for local AI inference only in teh 24 GB VRAM class and relatively cheap.

Can get A B60 24 GB card (under 1000 AUD/640 euro/however many USA dollars), target platform is CachyOS / Ollama running Vulkan to act as a model host for Openclaw/Hermes/whatever.

Has anyone run Ollama with this and care to comment? Looks good on paper, have heard earlier drivers are crap, but with rolling release this is/should be better?

Nah, the 3090 is 1.5x the price for a 5 year old card.

Zero interest in doing that. If I buy a B60 new it is a tax deduction too, so essentially it will cost me $650 AUD vs. $1500 for a 5 year old 3090.

3090 isn’t that much faster, and really - its the capacity I’m interested in. Speed isn’t bad; its going to be used to drive agents with tool use.

Already considered the 3090 and no fucking way am I spending 1500 on a 5 year old GPU. If I’m going to spend stupid money I’d buy an Nvidia Spark instead.

That is just flat out wrong, the memory bandwidth of the 3090 is 950 GB/s and the B60 is only 450 GB/s, the 3090 is going to give you 2-3 times the performance of the B60.

As @SlothUnleashed says, this is flat wrong. The 3090 is the fastest card you can get in the 24GB capacity, apart from the 4090 and - in some situations - the 7900XTX.

In my testing, it’s three to four times the speed of the B60 in AI workloads.

I’m not arguing with your case on the tax deduction side of things, but it’s way faster than anything Intel have on the market.

However, you really should consider the software support side of things. Intel’s software stack is terrible - it’s slow, it’s fragmented and it’s not particularly well-supported.

The 3090 isn’t that much faster that I am willing to spend 1.5x the price on a 5 year old card. Its also going into a small form factor box that I would not put a 3090 into.

Is a 3090 faster? Sure. It’s outside of scope for the purposes of this discussion due to both age and power supply requirements.

Looking at benchmarks, the B60 looks fast enough for my use case.

Maybe I need to clarify intent of this discussion:

Thread wasn’t “recommend me the fastest card I can get for local inference”.
its more “does this specific card have any major problems” with regards to the state of the current drivers.

If no one has any experience with the battlemage situation on linux then I guess I’ll figure it out myself.

However, you really should consider the software support side of things. Intel’s software stack is terrible - it’s slow, it’s fragmented and it’s not particularly well-supported.

More specifics? From what I’ve been able to determine the driver situation seems to be much better with up to date software and is not a fundamental card issue.

I do not plan on running CUDA, OPTIX, Games, etc. on this box. I have plenty of other systems for that.

It’s well-documented all over this forum, and many others. Intel only directly support running vLLM for inference. If you want to do that, you’re stuck with Intel’s own distribution of it (llm-scaler), which is usually months behind mainline and thus model support lags a long way behind current releases. That’s a very real problem when the pace of AI development is faster than almost anything we’ve seen before, with new model architectures being released all the time.

Intel’s software stack is also fragmented and unpredictable outside of that. For any given model, you might find that SYCL is faster, or Vulkan, or even OpenVINO, but there’s little documentation about which one you should use and not much in the way of logic involved in choosing one; worse, when any of them are slower, they’re really slow. It can often be quite painful just getting them working. You’re going to hit similar problems with Ollama as you would with vLLM - their pulls from llama.cpp are infrequent, and so you’re not going to get the fixes that do get implemented for Intel cards until much later.

Talking of llama.cpp fixes, SYCL and Intel/Vulkan are not a priority for the project. The sequence for releases tends to be CPU/CUDA first, then ROCm, then Vulkan/AMD, then Vulkan/Intel some time later, then SYCL, then all the smaller backends (Hexagon/OpenVINO/etc) when anybody can be bothered.

Intel’s also, thus far, got a track record of abandoning frameworks and architectures when they release The New Shiny - they completely abandoned Alchemist owners and left them stuck with the old (also abandoned) IPEX-LLM implementation as soon as Battlemage was released. I would fully expect them to do the same when Celestial is released, so if you’re going to buy a Battlemage card…you should treat the Celestial release as the EOL date for Battlemage as far as AI inference is concerned.

Basically, it’s not just about drivers. This is just my experience, having tracked the development with Intel cards and AI frameworks since Alchemist was first released; you can summarise it as “Intel talk a big game, but they rarely even get the basics right”. Performance is way behind even the mainstream cards from Nvidia and AMD, and they’re usually pretty frustrating in use.

TL;DR: It’s fine as a hobbyist card to play with and has some cool features, but it’s not ready for a serious work or production environment.

My B70 arrived just about a week ago. I haven’t spent much time with it yet, but so far it’s pretty decent for the price. I’ve had the best results with Vulkan running Qwen 3.6 27b.

I mostly bought the card for SR-IOV. That’s where the Arc Pro lineup becomes an unprecedented value IMO. Being able to partition it out to multiple VMs is awesome.

Overall, they’re competent cards with a promising future, but the software stack still needs a lot of work. Once the Linux 7.1 and 7.2 kernels ship things should improve.

So far I haven’t had any major issues aside from this multi-monitor bug:

(Copied from my Discord message yesterday)

“Trying to run both monitors at 120Hz on my Ubuntu 26.04 workstation with a 40" Dell U4025QW (5120x2160@120Hz) and 27" Dell U2725QE (4k@120Hz) just doesn’t seem to work, and I get some visual glitching on the desktop. 60Hz works, but still has visual glitching occasionally. This is a non-issue with other GPUs.

From my research it appears to be a pipe joiner issue where the 5k2k@120Hz display needs two pipes, and when the 27" is thrown into the mix, they collide causing the 5k2k display to drop down to 60Hz.”

…but it’s being fixed, so all good I suppose. Just don’t expect Nvidia (or even AMD) levels of support or performance yet. I also wouldn’t buy an Arc Pro with the expectation of AMD levels of support in 2026. Time well tell how serious Intel is about these GPUs, and how much effort goes into making them a success.

For the price and what you’re looking to do, I’d take a hard look at a Radeon 7900 XT (20GB) or 7900 XTX (24GB). Both can be found cheaper than a B60, have much better support, and very good performance.

Arc Pro owners are essentially beta testers for Intel lol.

Also, the stock Intel black & blue aesthetic makes the B70 one of the best looking GPUs I’ve seen in quite awhile.

Thanks guys that’s more of the info I’m looking for.

To paint the picture pretty clearly (because its kinda extreme specific edge case):

Its single purpose in life would be an Ollama/Vulkan backend running on a mostly headless box or as a secondary card in a box with a 6900XT in it for video stuff.

Use case:

hobbyist/home use with Hermes or Openclaw primarily aimed at basic tool use for web scraping/summary and email triage / basic project tracking with anything super complex being handed off to OpenAi or anthropic.

Speed is nowhere near as important (as it won’t be acting much as an interactive chatbot) as having 24 GB of VRAM - specifically 24 GB or more, as a lot of decent local models are tuned for that memory size with decent sized (64k-128k) context window.

I’m specifically looking to run say, 16-30B models with fairly heavy quantisation to fit a decent context window - so things with 20GB not really what I’m looking for. People aren’t aiming good local models at 20 GB, they’re aiming to fit them in 24 GB because thats the memory size of the 3090, etc. Again… memory size is the only reason I’m chasing this card, not for any major speed demand (any GPU > CPU which is the currently available alternative).

I’d be tempted to run it in CPU, but I’d need to throw more RAM at a box and that’s expensive anyway… and Cpu will be MUCH slower than even a lower end GPU… even Vega 64 rips compared to Ryzen, its just hampered by VRAM size which limits me to shittier models that aren’t really good enough for tool use.

If Mac Minis weren’t so expensive and hard to get right now I’d be buying a 32 GB Mac mini for this. May just end up doing that anyway (because that gets your agent clean access to iCloud app which I use)… but that’s pretty much what everyone else already did

I already have a few nice things set up with my agent (project tracking, daily email briefing, etc.) but it’s burning tokens pretty hard (luckily on a flat codex sub price but that’s probably not going to last forever) and a local model will offload a lot of that - assuming I can run something in the 24 GB sort of memory size.

Honestly, in your position I’d be tempted to get a second 6900XT for 32GB total VRAM. Use what you need for your LLM, and whatever’s left can go to the video processing. Cheaper, and more effective.

That’s an option I had not considered - how much of a fuck around is setting up 2x 6900XT or similar with Ollama?

Other caveats with that:

One of the boxes I’d be putting it in doesn’t have room (micro-ATX case, only single GPU slot) - its a spare PC which currently has no other purpose.

My main box… with the 6900XT - could be annoying if I was using it for gaming and an email/web hook/etc. comes in that then kicks of Ollama for email or alert classification…. also its buying another 5 year old card…

So there’s a definite plus for getting a single card solution for the spare/idle box…

edit:

just checked eBay - 69000XTs are about the same price as I’d be paying in post tax-deduction terms as a brand new b60… 650-750 AUD.

Maybe I should just wait until tax time and see what return I get. might be enough to go more than halfway towards a Mac Studio with 96 GB

Kill two birds with one stone, upgrade my ancient 5900XT build and get a shitload of local VRAM in one go.

I do try and claim all my computer stuff on tax (legitimately, its educational). I got a tax bill one year and this makes sure I don’t

It’s not particularly difficult with Vulkan - as long as you set it to offload everything to the GPU, it’ll just take care of it.

Just as a small point, though, you might want to look into running llama.cpp raw - with the new router mode, it has most of the features of Ollama (including the web UI), including a few that Ollama doesn’t have - like per-model configuration, for example. That’ll give you a lot more options for tuning, and it’ll definitely be faster, for free.

Do you not get to offset used equipment against your tax down under? We can do that as sole-traders in the UK, and it’s very handy for the thrifty among us…
