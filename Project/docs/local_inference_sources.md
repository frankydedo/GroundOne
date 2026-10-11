# Local inference: candidate sources (to review)

Collected 2026-10-11 from a web search on local LLM inference (hardware, open-weight models, consumer budgets).
Status 2026-10-11: up to five sources per section were downloaded to `Vault/raw/local_inference/` and ingested into the wiki
(see `Vault/changelog.md`, entry 2026-10-11; concepts Local Inference Hardware, Open-Weight Models, Privacy and Data
Sovereignty, Navier-Stokes Credit Dispute (2026)). Nothing is in the thesis yet.

Reliability tags:
- 🟢 primary: official spec page, paper, independent research group. Citable.
- 🟡 benchmark or review with measured numbers. Useful, verify before citing.
- ⚪ blog or aggregator. Orientation only, do not cite.

Many search hits are SEO sites that copy each other's numbers; prefer the 🟢 sources.

## 1. The big picture: why local inference matters

- 🟢 [Epoch AI: Frontier AI performance becomes accessible on consumer hardware within a year](https://epoch.ai/data-insights/consumer-gpu-model-gap). Models that run on one consumer GPU trail the frontier by 6–12 months. Key citation for Ch. 1.
- 🟢 [Epoch AI: What's the best model you can run on a single consumer GPU?](https://epochai.substack.com/p/whats-the-best-model-you-can-run)
- 🟢 [Epoch AI: Open-weight models (topic page)](https://epoch.ai/topics/open-models)
- 🟢 [Epoch AI: Open vs closed capability gap](https://epoch.ai/data-insights/open-closed-eci-gap)
- 🟢 [Stanford AI Index 2025: Technical performance](https://hai.stanford.edu/ai-index/2025-ai-index-report/technical-performance). Open/closed gap on Chatbot Arena from 8.04 % to 1.70 %; cost of GPT-3.5-level inference down about 280×.
- 🟢 [Artificial Analysis: Intelligence Index](https://artificialanalysis.ai/) and [Openness Index](https://artificialanalysis.ai/articles/announcing-artificial-analysis-openness-index). Up-to-date rankings of open-weight models.
- 🟢 [Artificial Analysis: GLM-5.2 leading open-weights model](https://artificialanalysis.ai/articles/glm-5-2-is-the-new-leading-open-weights-model-on-the-artificial-analysis-intelligence-index)
- 🟡 [HPCwire: Stanford AI Index on open vs proprietary models](https://www.hpcwire.com/aiwire/2025/04/09/stanfords-ai-index-highlights-growing-divide-between-open-and-proprietary-models/)

## 2. Open-weight models: definition and landscape

Definition
- 🟢 OSI Open Source AI Definition 1.0 (2024), https://opensource.org/ai. Separates open-weight (weights only) from open source (also training code and data information).
- ⚪ [Analytics Vidhya: Open source vs open weight](https://www.analyticsvidhya.com/blog/2025/04/open-weight-models/)
- ⚪ [Gumloop: Open weight vs open source](https://www.gumloop.com/blog/open-weight-vs-open-source)

Regulation
- 🟢 [Stanford CRFM: Foundation models under the EU AI Act](https://crfm.stanford.edu/2024/08/01/eu-ai-act.html)
- 🟡 [WilmerHale: Commission guidelines for general-purpose AI providers](https://www.wilmerhale.com/en/insights/blogs/wilmerhale-privacy-and-cybersecurity-law/20250724-european-commission-issues-guidelines-for-providers-of-general-purpose-ai-models). Open-source exemption, Art. 53(2).
- 🟡 [Orrick: The EU AI Act and open-source projects](https://orrick.com/Insights/2024/09/The-EU-AI-Act-Application-to-Open-Source-Projects)

Small and on-device models
- 🟢 [Small Language Models: Survey, Measurements, and Insights (arXiv 2409.15790)](https://arxiv.org/abs/2409.15790). 70 models of 100M–5B parameters, with on-device latency and memory measurements.
- 🟢 [A Survey on Small Language Models (Adobe et al., 2025)](https://research.adobe.com/publication/a-survey-on-small-language-models)
- 🟢 [Google: Introducing Gemma 3n (mobile-first)](https://developers.googleblog.com/en/introducing-gemma-3n/)

Comparisons (current)
- ⚪ [Codersera: Llama 4 vs Qwen 3.5 vs DeepSeek V4 vs Gemma 4 vs Mistral](https://codersera.com/blog/best-open-source-llm-2026-llama-4-qwen-3-5-deepseek-v4-gemma-4-mistral/)
- ⚪ [OwnYourMind: Open-weight model comparison](https://ownyourmind.ai/resources/open-weight-model-comparison/)
- ⚪ [Lushbinary: Best open-source LLMs, April 2026](https://lushbinary.com/blog/best-open-source-llms-april-2026-comparison-guide/)

## 3. Dedicated hardware: Mac Studio, NVIDIA DGX Spark, AMD Strix Halo

Official specifications
- 🟢 [NVIDIA DGX Spark: product page](https://www.nvidia.com/en-us/products/workstations/dgx-spark/) and [hardware overview](https://docs.nvidia.com/dgx/dgx-spark/hardware.html). GB10, 128 GB unified memory at 273 GB/s, 1 PFLOP FP4, about 240 W, about $4,699.
- 🟢 [Apple: Mac Studio (2025) tech specs](https://support.apple.com/en-us/122211). M4 Max up to 546 GB/s, M3 Ultra 819 GB/s, up to 256 GB.

Head-to-head
- 🟢 [EXO Labs: DGX Spark + Mac Studio, disaggregated inference](https://blog.exolabs.net/nvidia-dgx-spark/), reported by [Tom's Hardware](https://www.tomshardware.com/software/two-nvidia-dgx-spark-systems-combined-with-m3-ultra-mac-studio-to-create-blistering-llm-system-exo-labs-demonstrates-disaggregated-ai-inference-and-achieves-a-2-8-benchmark-boost). Spark wins prefill (compute), Mac wins decode (memory bandwidth): the same prefill/decode split the thesis relies on.
- 🟡 [OpenClaw: DGX Spark vs Mac Studio M3 Ultra](https://openclawdc.com/blog/dgx-spark-vs-mac-studio-m3-ultra-local-llm/). Spark about 3.8× faster prefill, M3 Ultra about 3.4× faster decode.
- 🟡 [IntuitionLabs: DGX Spark review](https://intuitionlabs.ai/articles/nvidia-dgx-spark-review)
- 🟡 [AIMultiple: DGX Spark alternatives](https://aimultiple.com/dgx-spark-alternatives)

AMD Strix Halo (Ryzen AI Max+ 395)
- 🟡 [Hardware Corner: AI Max+ 395 for LLM inference](https://www.hardware-corner.net/how-fast-ai-max-395-llm-20250317/)
- 🟡 [DataHardware: Strix Halo tokens per second, 2026](https://datahardware.ai/blog/strix-halo-tokens-per-second-2026). Dense vs MoE; about 215 GB/s measured bandwidth.
- 🟡 [PCWorld: Framework Desktop review](https://www.pcworld.com/article/2866400/framework-desktop-review.html). 128 GB unified memory, $1,999 at launch, later $3,449 because of the RAM shortage.
- 🟡 [Zenn: Nine months of local LLMs on Ryzen AI Max+ 395](https://zenn.dev/shuzan/articles/0605b909fb23e4?locale=en). Hands-on experience, software limits.
- ⚪ [Compute Market: AMD Ryzen AI Halo review](https://www.compute-market.com/blog/amd-ryzen-ai-halo-review-2026)

Cross-hardware benchmarks
- 🟡 [Presenc: Local LLM tokens-per-second benchmarks 2026](https://presenc.ai/research/local-llm-tokens-per-second-benchmarks-2026)

## 4. Consumer hardware under $3k

Apple
- 🟢 [Apple ML Research: LLMs with MLX and the M5 neural accelerators](https://machinelearning.apple.com/research/exploring-llms-mlx-m5). Time to first token 3.3–4× faster than M4, generation only 1.2–1.3×. The prefill/decode dichotomy again.
- 🟢 [arXiv 2511.05502: Local inference on Apple Silicon, MLX vs MLC vs Ollama vs llama.cpp vs PyTorch MPS](https://arxiv.org/abs/2511.05502)
- 🟡 [MLX discussion #2816 (M5 benchmarks)](https://github.com/ml-explore/mlx/discussions/2816)
- 🟡 [Davies Meyer: Mac mini M4 Pro 64 GB for local AI](https://ai-solutions.daviesmeyer.com/en/blog/mac-mini-m4-pro-lokale-ki-inferenz)
- ⚪ [LocalAIMaster: Apple Silicon AI buying guide](https://localaimaster.com/blog/apple-silicon-ai-buying-guide)

GPUs
- 🟡 [Corelab: Best GPU for local LLMs, VRAM tier list](https://corelab.tech/llmgpu/)
- 🟡 [PromptQuorum: Best GPUs for local LLMs](https://www.promptquorum.com/local-llms/best-gpus-for-local-llms)
- 🟡 [Bizon: Best GPU for LLM training and inference](https://bizon-tech.com/blog/best-gpu-llm-training-inference)
- ⚪ [RunAIHome: Best LLM for every RTX 50-series GPU](https://www.runaihome.com/blog/best-llm-every-rtx-50-series-gpu-2026/)
- 🟡 Intel Arc Pro B60, 24 GB at about $600: [GPU Dojo](https://gpudojo.com/arc-pro-b60), [Level1Techs thread](https://forum.level1techs.com/t/asrock-intel-b60-24-gb-for-local-ai/251192). Cheapest new 24 GB card.
- Context (unverified street prices): RTX 5090 at about twice MSRP because of the GDDR7 shortage; used RTX 3090 about $1,050–1,240.

PCs with an NPU
- 🟢 [Qualcomm Snapdragon X, 45 TOPS NPU (press release)](https://www.edge-ai-vision.com/2024/05/snapdragon-x-series-is-the-exclusive-platform-to-power-the-next-generation-of-windows-pcs-with-copilot-today/)
- ⚪ [BestLLMFor: LLMs on Snapdragon X Elite](https://bestllmfor.com/guide/snapdragon-x-elite-llm-local/). The NPU is used only through dedicated runtimes.

## 5. Academic surveys on on-device and edge inference

- 🟢 [Mobile Edge Intelligence for Large Language Models: A Contemporary Survey (arXiv 2407.18921)](https://arxiv.org/abs/2407.18921)
- 🟢 [Collaborative Inference between Edge SLMs and Cloud LLMs: A Survey (arXiv 2507.16731)](https://arxiv.org/abs/2507.16731)
- 🟢 [Large Models for Small Devices: Edge AI Deployment (arXiv 2608.15693)](https://arxiv.org/abs/2608.15693)
- 🟢 [Efficient Inference for Edge Large Language Models: A Survey (Tsinghua Sci. & Tech., 2025)](https://www.sciopen.com/article/10.26599/TST.2025.9010166)
- 🟢 [Optimizing Edge AI: A Comprehensive Survey (arXiv 2501.03265)](https://arxiv.org/abs/2501.03265)

## 6. Tools, quantization, cost and privacy

- 🟡 [Presenc: State of the llama.cpp ecosystem 2026](https://presenc.ai/research/llama-cpp-ecosystem-state-2026). Ollama about 52M monthly downloads; about 135k GGUF models on Hugging Face.
- 🟡 [PremAI: GGUF vs AWQ vs GPTQ vs bitsandbytes](https://blog.premai.io/llm-quantization-guide-gguf-vs-awq-vs-gptq-vs-bitsandbytes-compared-2026)
- ⚪ [DasRoot: GGUF quantization quality and speed on consumer GPUs](https://dasroot.net/posts/2026/02/gguf-quantization-quality-speed-consumer-gpus/)
- ⚪ [DasRoot: Privacy, local LLMs vs cloud APIs](https://dasroot.net/posts/2026/01/privacy-preserving-ai-local-llms-vs-cloud-apis-2026/)
- ⚪ [Ertas: Local inference vs API](https://www.ertas.ai/compare/local-inference-vs-api). Break-even estimates need checking.

## 7. Case study for privacy-critical use: the Navier–Stokes credit dispute (September 2026)

What happened (consistent across the sources below):
- On 2026-09-08 OpenAI announced that an unreleased model, run as a multi-agent system (up to about 10,000 agents for
  about 88 hours), had produced a proof on the Navier–Stokes Millennium problem: a *forced* blow-up construction (smooth
  data, smooth applied force, finite energy, singularity in finite time), formalised in Lean. Whether the formal
  statement matches the Clay problem is still under review by mathematicians.
- The day before, Tristan Buckmaster (NYU) and Levent Alpöge (Anthropic) had released a related blow-up result for the
  Euler equations, obtained with AI assistance. Buckmaster alleges that OpenAI started only after information about
  their unpublished work reached it, and that the OpenAI proof follows the same niche direction.
- The privacy-relevant point: the pair had been writing their drafts in OpenAI's Codex. Buckmaster: "I asked whether the
  model had been trained on, or had access to, our sessions in Codex, into which we had been putting all our drafts."
  OpenAI denies that anyone saw their work before release, but adds: "While unlikely, we cannot rule out that
  de-identified data derived from their usage of our products helped improve our models."

Why it matters here: nothing in the sources shows that private data was misused, and the dispute is mainly about
credit. What it does show is that a user who puts unpublished work into a cloud model cannot verify afterwards how that
data was used, and even the provider can only say it is "unlikely". With local inference the question does not arise.
If cited in the thesis, phrase it exactly this way (an unverifiable risk, not proven misuse). Note: the drafts were in
Codex (OpenAI's coding agent), not in ChatGPT conversations.

Sources
- 🟡 [Fortune (2026-09-08): OpenAI says it cracked Navier–Stokes; Buckmaster accusation, Tao's comment](https://www.fortune.com/2026/09/08/openai-says-it-cracked-navier-stokes-math-grand-challenge-buckmaster-accusation-cheating-intimidation-tao-lament/). Codex-sessions quote, Bubeck's denial, Terence Tao on "strip-mining of open problems".
- 🟡 [Live Science: "Why would you ruin your career?" OpenAI claims to have cracked one of math's greatest unsolved problems](https://livescience.com/physics-mathematics/mathematics/why-would-you-ruin-your-career-openai-claims-to-have-cracked-one-of-maths-greatest-unsolved-problems-but-mathematicians-allege-it-played-dirty)
- 🟡 [NYU Shanghai RITS: OpenAI claims a Navier–Stokes proof, amid a dispute over credit](https://rits.shanghai.nyu.edu/ai/openai-navier-stokes-proof-credit-dispute/). What exactly was proven (forced case), Lean status, OpenAI's de-identified-data statement verbatim.
- 🟡 [OfficeChai: OpenAI says it didn't see any of Buckmaster and Alpöge's work](https://officechai.com/ai/openai-says-it-didnt-see-any-of-buckmaster-and-alpoges-work-while-resolving-navier-stokes/). OpenAI's statement.
- 🟡 [The Next Web: Bubeck denies trying to cut Anthropic mathematician from credit](https://thenextweb.com/news/bubeck-navier-stokes-account-apology-altman)
- 🟡 [Plagiarism Today (2026-09-09): Who gets credit when AI makes a breakthrough?](https://www.plagiarismtoday.com/2026/09/09/who-gets-credit-when-ai-makes-a-breakthrough/). Credit and opaque training data.
- 🟡 [Ara (English): OpenAI claims to have solved a Millennium problem but is accused of plagiarism](https://en.ara.cat/media/openai-assures-that-it-has-solved-one-of-the-great-mathematical-problems-of-the-millennium-but-they-accuse-it-of-plagiarism_1_5844534.html)
- 🟡 [WBUR Here & Now (2026-09-11)](https://www.wbur.org/hereandnow/2026/09/11/open-ai-math-problem). Short summary.
- ⚪ [MindStudio: the Navier–Stokes plagiarism dispute](https://www.mindstudio.ai/blog/openai-navier-stokes-proof-controversy). Good on the difference between a model "looking up" a session and the session entering a later training run; contains a name error (Elgindi for Alpöge).
- ⚪ Blogs that draw the local-inference lesson explicitly (not read in full): [Your data never left your computer](https://koutian.is-a.dev/posts/2026/09/your-data-never-left-your-computer/), [Petronella: what the OpenAI math breakthrough means for private AI](https://petronellatech.com/blog/openai-math-breakthrough-what-it-means-for-private-ai/).
- 🟢 Background: [Navier–Stokes existence and smoothness (Wikipedia, problem statement)](https://en.wikipedia.org/wiki/Navier%E2%80%93Stokes_existence_and_smoothness) and the Clay Mathematics Institute problem description.

## Suggested minimal set for Ch. 1–2

Epoch AI (consumer vs frontier gap), Stanford AI Index (open vs closed gap), the OSI definition (open-weight), the DGX
Spark and Mac Studio spec pages, the Apple M5 study and EXO Labs (both support the prefill/decode argument), and one or
two on-device surveys. The 🟡 reviews could feed a hardware table with prices, citing the official pages for the specs.
