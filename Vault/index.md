# LLM Wiki

Knowledge base for the MSc thesis **[[GroundOne]]**: a specialist System One model for groundedness verification in local RAG.

## Thesis
- [[GroundOne]] (project summary; source of truth: `Project/docs/implementation_plan.md`)
- [[When System One Beats an LLM]] (synthesis)

## System One models
- [[System One Models]] (definition and taxonomy)
- [[Jev]], [[TypeSafe AI]], [[Jev Input and Output Format]], [[Reinforcement Learning with Calibrated Decisions]], [[Jev vs LLMs Cost Comparison]]
- Open implementations: [[SemIf]], [[Rizzo-Flow]], [[CLM]], [[Jevlike]]
- [[Mixture of Experts]], [[LangChain]]

## RAG, hallucination and verification
- [[Retrieval-Augmented Generation]], [[RAG Evaluation Frameworks]]
- [[Hallucination Detection]], [[Groundedness Verification]], [[Natural Language Inference]]
- [[LLM-as-a-Judge]]
- Benchmarks: [[LLM-AggreFact]], [[RAGTruth]]
- Encoder checkers: [[MiniCheck]], [[HHEM]], [[AlignScore]]

## Calibration and decision-making
- [[Calibration]], [[Expected Calibration Error]], [[Selective Prediction]]

## Models, training and inference
- [[Qwen2.5]], [[LoRA]]
- [[Prefill and Decode]], [[KV Cache]]

## Archived (earlier tool-routing experiment)
- [[Function Calling]], [[Berkeley Function Calling Leaderboard]]

## Sources
**System One (grey literature)**
- [[jev_simone_rizzo]], [[JEV Video Description]], [[Jevs Architecture Unmasked]], [[Che cos'e Jev Spiegazione]], [[Introducing System One Models and Jev]], [[What Is Jev A Guide to TypeSafe AI]], [[Can Jev replace your LLM judge]]
- [[Kwok 2026 - Contrastive Language Models]], [[CLM README]], [[Rizzo-Flow README]], [[Rizzo-Flow training]], [[SemIf README]], [[SemIf RESULTS]]

**RAG, verification, judges**
- [[Lewis 2020 - Retrieval-Augmented Generation]], [[Niu 2024 - RAGTruth]], [[Tang 2024 - MiniCheck]], [[Tang 2024 - LLM-AggreFact Leaderboard]], [[Zha 2023 - AlignScore]], [[Vectara 2024 - HHEM-2.1-Open model card]], [[Ravi 2024 - Lynx]]
- [[Es 2024 - RAGAS]], [[Saad-Falcon 2024 - ARES]], [[Asai 2024 - Self-RAG]], [[Zheng 2023 - Judging LLM-as-a-Judge]]
- [[Nie 2020 - Adversarial NLI]], [[Williams 2018 - MultiNLI Broad-Coverage Challenge Corpus]]

**Calibration**
- [[Naeini 2015 - Obtaining Well Calibrated Probabilities Using Bayesian Binning]], [[Guo 2017 - On Calibration of Modern Neural Networks]], [[Kadavath 2022 - Language Models (Mostly) Know What They Know]], [[Tian 2023 - Just Ask for Calibration]], [[Geifman 2017 - Selective Classification for Deep Neural Networks]]

**Models, training, inference**
- [[Hu 2022 - LoRA]], [[Dettmers 2023 - QLoRA]], [[Qwen Team 2024 - Qwen2.5 Technical Report]], [[Pope 2023 - Efficiently Scaling Transformer Inference]], [[Kwon 2023 - PagedAttention vLLM]]

**Archived**
- [[Berkeley Function Calling Leaderboard V4]], [[Hugging Face Datasets BFCL]]
