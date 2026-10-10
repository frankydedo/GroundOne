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
- Ecosystem and evaluation: [[Hugging Face decision-models Tag]], [[Decision-Model Benchmarks]]
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
- [[Samsi 2023 - From Words to Watts]], [[Luccioni 2024 - Power Hungry Processing]]

**Hallucination and fine-grained verification**
- [[Huang 2023 - A Survey on Hallucination in LLMs]], [[Laban 2022 - SummaC]], [[Min 2023 - FActScore]]

**Archived**
- [[Berkeley Function Calling Leaderboard V4]], [[Hugging Face Datasets BFCL]]
