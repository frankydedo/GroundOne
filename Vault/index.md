# LLM Wiki

Knowledge base for the MSc thesis **[[GroundOne]]**: a specialist System One model for groundedness verification in local RAG.

## Thesis
- [[GroundOne]] (project summary; source of truth: `Project/docs/checkpoint_2026-10-10.md` and `implementation_plan.md`)
- [[GroundOne Results]] (all results, 2026-10-10)
- [[When System One Beats an LLM]] (synthesis, with the outcome of the thesis hypotheses)

## System One models
- [[System One Models]] (definition and taxonomy), [[Letter-Token Readout]] (letter logits vs generated answer)
- [[Jev]], [[TypeSafe AI]], [[Jev Input and Output Format]], [[Reinforcement Learning with Calibrated Decisions]], [[Jev vs LLMs Cost Comparison]]
- Open implementations: [[SemIf]], [[Rizzo-Flow]], [[CLM]], [[Jevlike]], [[Laya]]
- Ecosystem and evaluation: [[Decision-Model Landscape (Hugging Face, 2026)]] (survey of the `decision-model` tag: families, catalogue, on-device ports, red flags), [[Hugging Face decision-models Tag]], [[Decision-Model Benchmarks]]
- [[Mixture of Experts]], [[LangChain]]

## RAG, hallucination and verification
- [[Retrieval-Augmented Generation]], [[RAG Evaluation Frameworks]]
- [[Hallucination Detection]], [[Groundedness Verification]], [[Natural Language Inference]]
- [[LLM-as-a-Judge]], [[Verbalised vs Logit Confidence]], [[Constrained Decoding]]
- Benchmarks: [[LLM-AggreFact]] ([[LLM-AggreFact Sub-datasets]]), [[RAGTruth]]
- Encoder checkers: [[MiniCheck]], [[HHEM]], [[AlignScore]]

## Data
- [[Datasets for GroundOne]] (synthesis: origins, differences, which dataset for which experiment); EDA: [[GroundOne 2026 - EDA report (dataset)]]
- [[RAGTruth]] (training, T1), [[LLM-AggreFact]], [[LLM-AggreFact Sub-datasets]] (T2), [[VitaminC]] (T3); not used: [[ANLI]], [[MiniCheck Synthetic Data]]

## Calibration and decision-making
- [[Calibration]], [[Expected Calibration Error]], [[Selective Prediction]]

## Evaluation methodology
- [[Statistical Significance and Bootstrap]], [[Fine-tuning Instability and Seeds]]

## Models, training and inference
- [[Qwen2.5]], [[LoRA]]
- [[Prefill and Decode]], [[KV Cache]]

## Local inference (thesis pillar)
- [[On-Device Inference]], [[Apple Silicon and MLX]], [[Energy of LLM Inference]]
- [[Local Inference Hardware]] (Mac Studio, DGX Spark, Strix Halo, consumer GPUs: capacity, bandwidth, compute, power, price), [[Quantization]], [[Small Language Models]], [[Edge-Cloud Collaborative Inference]]
- [[Open-Weight Models]] (OSI definition, licences, open/closed gap, EU AI Act), [[Privacy and Data Sovereignty]], case study: [[Navier-Stokes Credit Dispute (2026)]]

## Archived (earlier tool-routing experiment)
- [[Function Calling]], [[Berkeley Function Calling Leaderboard]]

## Sources
**System One (grey literature)**
- [[jev_simone_rizzo]], [[JEV Video Description]], [[Jevs Architecture Unmasked]], [[Che cos'e Jev Spiegazione]], [[Introducing System One Models and Jev]], [[What Is Jev A Guide to TypeSafe AI]], [[Can Jev replace your LLM judge]]
- [[Kwok 2026 - Contrastive Language Models]], [[CLM README]], [[Rizzo-Flow README]], [[Rizzo-Flow training]], [[SemIf README]], [[SemIf RESULTS]]

**System One (2026 papers, cards and benchmarks; `decision-models` tag)**
- Papers: [[Deusser 2026 - Evaluating and Benchmarking the System One Model Jev (arXiv 2609.37647)]], [[Nandakishore 2026 - Laya as a Typed Probabilistic Assessor (arXiv 2609.33843)]], [[Azizi 2026 - Labels Override Definitions in Jev-Style Typed Decision Models (arXiv 2610.02586)]], [[Robles-Fernandez 2026 - Sciev Typed Scientific Decisions Without Generation (manuscript, sciev.org)]]
- Model cards: [[Convai Innovations 2026 - Laya model card]], [[Robles-Fernandez 2026 - Sciev model card]]
- Benchmarks and data: [[Yong 2026 - DecideBench dataset card]], [[Benchmark Heaven 2026 - JevBench v1.6.1 dataset card]], [[morrenhale 2026 - Decision benchmark Jev vs Laya vs Julia-1 dataset card]], [[pranaysuyash 2026 - Laya Formatting Fragility dataset card]], [[mlboydaisuke 2026 - Decision models on Core AI (JevBench public231) dataset card]], [[Sileo 2026 - tasksource-jev-typed-decisions dataset card]]

**System One (2026, `decision-model` tag: industry entrants, ports, papers)**
- Model cards: [[Cloudflare 2026 - Clef model card]], [[LiquidAI 2026 - d1-3B model card]], [[Perplexity 2026 - pplx-decider-v1.1-27b model card]], [[Strands Agents (Amazon) 2026 - strands-decider-2B-qwen3.5-v1 model card]], [[KR Labs and vLLM Semantic Router 2026 - Vela 2.0 9B model card]] (hallucination spans), [[Palmer 2026 - Kev-4B model card]], [[tokimoa 2026 - uratori-ja-4b model card]] (grounding, Japanese)
- On-device: [[mlx-community 2026 - clef-flash-4bit model card]], [[FluidInference 2026 - d1-omni-600M Core ML model card]], [[ggml-org 2026 - llama.cpp PR 29818 systemone API]]
- Leaderboard and data: [[multimodalart 2026 - Jev Decision Index (Hugging Face Space)]], [[Hugging Face 2026 - decision-model tag listing (2026-10-10)]]
- Papers: [[Li 2026 - JEV-as-a-Judge (arXiv 2609.26550)]], [[Guo 2026 - Just Ask Jev (arXiv 2609.29429)]], [[Deka 2026 - From Retrieval to Typed Decisions SBERT2S1 (arXiv 2610.02486)]]

**RAG, verification, judges**
- [[Lewis 2020 - Retrieval-Augmented Generation]], [[Niu 2024 - RAGTruth]], [[Tang 2024 - MiniCheck]], [[Tang 2024 - LLM-AggreFact Leaderboard]], [[Zha 2023 - AlignScore]], [[Vectara 2024 - HHEM-2.1-Open model card]], [[Ravi 2024 - Lynx]]
- [[Es 2024 - RAGAS]], [[Saad-Falcon 2024 - ARES]], [[Asai 2024 - Self-RAG]], [[Zheng 2023 - Judging LLM-as-a-Judge]]
- [[Nie 2020 - Adversarial NLI]], [[Williams 2018 - MultiNLI Broad-Coverage Challenge Corpus]]

**Datasets**
- Cards: [[Dataset card - ANLI]], [[Dataset card - LLM-AggreFact]], [[Dataset card - MiniCheck C2D-D2C]], [[Dataset card - RAGTruth README]]
- Papers: [[Schuster 2021 - VitaminC]]
- RAGTruth sources: [[Nguyen 2016 - MS MARCO]], [[See 2017 - Get To The Point]], [[Hermann 2015 - Teaching Machines to Read and Comprehend]], [[Yelp Open Dataset]]
- LLM-AggreFact sub-datasets: [[Tang 2023 - AggreFact]], [[Tang 2024 - TofuEval]], [[Kamoi 2023 - WiCE]], [[Jacovi 2024 - REVEAL]], [[Liu 2023 - Evaluating Verifiability in Generative Search Engines]], [[Wang 2024 - Factcheck-Bench]], [[Malaviya 2024 - ExpertQA]], [[Chen 2024 - Understanding Retrieval Augmentation for LFQA]]
- Project output: [[GroundOne 2026 - EDA report]]

**Calibration**
- [[Naeini 2015 - Obtaining Well Calibrated Probabilities Using Bayesian Binning]], [[Guo 2017 - On Calibration of Modern Neural Networks]], [[Kadavath 2022 - Language Models (Mostly) Know What They Know]], [[Tian 2023 - Just Ask for Calibration]], [[Geifman 2017 - Selective Classification for Deep Neural Networks]]

**Models, training, inference**
- [[Hu 2022 - LoRA]], [[Dettmers 2023 - QLoRA]], [[Qwen Team 2024 - Qwen2.5 Technical Report]], [[Pope 2023 - Efficiently Scaling Transformer Inference]], [[Kwon 2023 - PagedAttention vLLM]]
- Fine-tuning stability: [[Dodge 2020 - Fine-Tuning Pretrained LMs (weight init, data order, early stopping)]], [[Mosbach 2021 - On the Stability of Fine-tuning BERT]], [[Pascanu 2013 - On the difficulty of training RNNs (gradient clipping)]]

**Readout, confidence, decoding**
- [[Wang 2024 - My Answer is C (first-token probabilities vs text answers)]], [[Zheng 2024 - LLMs Are Not Robust Multiple Choice Selectors]], [[Zhao 2021 - Calibrate Before Use]], [[Xiong 2024 - Can LLMs Express Their Uncertainty]], [[Willard 2023 - Efficient Guided Generation for LLMs (Outlines)]]

**Statistical significance**
- [[Koehn 2004 - Statistical Significance Tests for MT Evaluation (paired bootstrap)]], [[Berg-Kirkpatrick 2012 - An Empirical Investigation of Statistical Significance in NLP]], [[Dror 2018 - The Hitchhiker's Guide to Testing Statistical Significance in NLP]]

**Local inference, hardware, energy**
- [[Patel 2024 - Splitwise (prefill vs decode phases)]], [[Alizadeh 2024 - LLM in a flash]], [[Gunter 2024 - Apple Intelligence Foundation Language Models]], [[MLX README (ml-explore)]], [[llama.cpp README (ggml-org)]], [[Apple 2024 - MacBook Pro 14-inch M4 tech specs]]

**Local inference landscape (ingest 2026-10-11; `raw/local_inference/`)**
- Trends and open models: [[Epoch AI 2025 - Frontier AI performance becomes accessible on consumer hardware within a year]], [[Epoch AI 2025 - What's the best model you can run on a single consumer GPU]], [[Epoch AI - Open vs closed capability gap (ECI)]], [[Stanford HAI 2025 - AI Index Report, Technical performance]], [[Artificial Analysis - Announcing the Openness Index]], [[OSI 2024 - The Open Source AI Definition 1.0]], [[Stanford CRFM 2024 - Foundation models under the EU AI Act]], [[WilmerHale 2025 - Commission guidelines for providers of general-purpose AI models]], [[Lu 2024 - Small Language Models, Survey, Measurements, and Insights (arXiv 2409.15790)]], [[Google 2025 - Introducing Gemma 3n]]
- Hardware: [[NVIDIA - DGX Spark hardware overview]], [[Apple 2025 - Mac Studio (2025) tech specs]], [[EXO Labs 2025 - NVIDIA DGX Spark and Mac Studio, disaggregated inference]], [[Hardware Corner 2025 - How fast is the AI Max+ 395 for LLM inference]], [[PCWorld - Framework Desktop review]], [[Apple ML Research 2025 - Exploring LLMs with MLX and the neural accelerators in the M5 GPU]], [[Rajesh 2025 - Local LLM inference on Apple Silicon, MLX vs MLC vs Ollama vs llama.cpp (arXiv 2511.05502)]], [[Corelab - Best GPU for local LLMs, VRAM tier list]], [[Level1Techs - ASRock Intel Arc Pro B60 24 GB for local AI]], [[Davies Meyer - Mac mini M4 Pro for local AI inference]]
- Edge-inference surveys: [[Qu 2024 - Mobile Edge Intelligence for LLMs, A Contemporary Survey (arXiv 2407.18921)]], [[Li 2025 - Collaborative Inference between Edge SLMs and Cloud LLMs, A Survey (arXiv 2507.16731)]], [[Das 2026 - Large Models for Small Devices, Edge AI Deployment (arXiv 2608.15693)]], [[Wang 2025 - Cognitive Edge Computing, Optimizing Large Models and AI Agents (arXiv 2501.03265)]]
- Tools, quantisation, privacy: [[Presenc 2026 - State of the llama.cpp ecosystem]], [[Presenc 2026 - Local LLM tokens-per-second benchmarks]], [[PremAI 2026 - LLM quantization guide, GGUF vs AWQ vs GPTQ vs bitsandbytes]], [[DasRoot 2026 - Privacy-preserving AI, local LLMs vs cloud APIs]]
- Second batch (quantisation, roofline, mobile, regulation, vendor specs): [[Dettmers 2022 - LLM.int8(), 8-bit Matrix Multiplication for Transformers at Scale (arXiv 2208.07339)]], [[Frantar 2023 - GPTQ, Accurate Post-Training Quantization for Generative Pre-trained Transformers (arXiv 2210.17323)]], [[Lin 2024 - AWQ, Activation-aware Weight Quantization for LLM Compression and Acceleration (arXiv 2306.00978)]], [[Leviathan 2023 - Fast Inference from Transformers via Speculative Decoding (arXiv 2211.17192)]], [[Williams 2009 - Roofline, An Insightful Visual Performance Model for Multicore Architectures]], [[Yuan 2024 - LLM Inference Unveiled, Survey and Roofline Model Insights (arXiv 2402.16363)]], [[Liu 2024 - MobileLLM, Optimizing Sub-billion Parameter Language Models for On-Device Use Cases (arXiv 2402.14905)]], [[Laskaridis 2024 - MELTing point, Mobile Evaluation of Language Transformers (arXiv 2403.12844)]], [[Xu 2025 - Fast On-device LLM Inference with NPUs (arXiv 2407.05858)]], [[Xue 2024 - PowerInfer-2, Fast Large Language Model Inference on a Smartphone (arXiv 2406.06282)]], [[EU 2016 - Regulation (EU) 2016-679, General Data Protection Regulation (GDPR)]], [[Apple Security 2024 - Private Cloud Compute, a new frontier for AI privacy in the cloud]], [[Apple 2026 - Mac mini tech specs]], [[Apple 2026 - MacBook Pro tech specs (M5 family)]], [[NVIDIA 2026 - GeForce graphics cards compare specs]]
- Specialised inference engines (2026-10-13): [[antirez 2026 - ds4, DeepSeek 4 Flash and PRO local inference engine (GitHub README)]], [[JustVugg 2026 - Colibri, frontier MoE models with experts streamed from disk (GitHub README)]]
- Navier–Stokes case: [[Fortune 2026 - OpenAI says it cracked Navier-Stokes, Buckmaster accusation]], [[NYU Shanghai RITS 2026 - OpenAI claims a Navier-Stokes proof amid a dispute over credit]], [[OfficeChai 2026 - OpenAI says it didn't see Buckmaster and Alpoge's work]], [[Plagiarism Today 2026 - Who gets credit when AI makes a breakthrough]], [[Live Science 2026 - Why would you ruin your career, OpenAI Navier-Stokes claim]]
- [[Samsi 2023 - From Words to Watts]], [[Luccioni 2024 - Power Hungry Processing]]

**Hallucination and fine-grained verification**
- [[Huang 2023 - A Survey on Hallucination in LLMs]], [[Laban 2022 - SummaC]], [[Min 2023 - FActScore]]

**Archived**
- [[Berkeley Function Calling Leaderboard V4]], [[Hugging Face Datasets BFCL]]
