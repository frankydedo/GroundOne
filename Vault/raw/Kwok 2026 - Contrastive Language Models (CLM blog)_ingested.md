---
source: https://contrastive-lm.notion.site
accessed: 2026-10-05
citation: "Kwok, J., Kang, H., Suresh, T., Saad-Falcon, J., Pavone, M., Ré, C., Mirhoseini, A. (2026). Contrastive Language Models: A System One Model for Fast and Generalizable Decision-Making. Notion Blog, posted 2026-09-23."
note: "Converted from the public Notion page via its page-data API; images/videos are referenced as Notion attachment ids only."
---

# Contrastive Language Models
> ***A System One Approach for Fast and Generalizable Decision-Making***
[Jacky Kwok](https://jackyk02.github.io/)⁍, [Hangoo Kang](https://hgkang02.github.io/), [Tarun Suresh](https://tarsur909.github.io/), [Jon Saad-Falcon](https://jonsaadfalcon.com/), [Marco Pavone](https://research.nvidia.com/person/marco-pavone)
[Christopher Ré](https://cs.stanford.edu/~chrismre/), [Azalia Mirhoseini](https://azaliamirhoseini.com/) Stanford University  NVIDIA Research 
⁍ Project Lead
🗓️ Posted: Sep 23, 2026
> 
New Architecture, Data Recipe, and Scaling Laws <!-- header_4 -->
- We introduce Contrastive Language Models (CLMs), a new class of **System One model **trained with a **contrastive learning** objective that connects **states and actions**.
- We release **CLM-8B**, which is pre-trained on **60M Nemotron Q&A pairs**, mid-trained on **30M synthetic hard negatives**, and post-trained on **1M agentic trajectories**.
- **CLM-8B** delivers performance comparable to **Jev** across computer-use, gaming, and tool-calling tasks, while achieving up to **9× lower latency**. When fine-tuned as a trajectory reward model, CLM also **sets a new SOTA** on challenging agentic coding benchmarks, including [DeepSWE](https://deepswe.datacurve.ai/) (81.6%) and [Terminal Bench 2.1](https://www.tbench.ai/?version=2.1) (87.6%).
- We build an ultra-efficient training and serving infra for CLM by **disaggregating states and actions**, allowing their embeddings to be cached and reused independently.
- We establish **scaling laws for CLMs** and show that the test contrastive loss decreases predictably as a **power law** in training **compute**, **model size**, and **dataset size**.
Try [CLM on GitHub](https://github.com/Contrastive-LM/CLM):
[image: attachment:c814f420-daca-404b-ba0d-4aa08390e190:git.png]


### Overview
[image: attachment:236bfbeb-eaf6-4d54-bdec-7a6daa0d881a:image.png]
CLM first trains a **state encoder** and an **action encoder** on a large-scale dataset with a **contrastive objective** (InfoNCE), so that each state is pulled toward the ground truth action that was taken and pushed away from all others. The two encoders then serve directly as a **zero-shot action classifier**.
At deployment, given the current state and a set of candidate actions, CLM scores each action by how well its embedding aligns with the state embedding and selects the highest-scoring action. 
Dino Run (CLM vs. Jev) <!-- header_4 -->
[image: attachment:83e15cea-6c39-49c2-8289-edfc5227a685:clm_game_race.gif]

- ***Super Mario Demo***
  ***                 CLM  *****(~4x Faster than Jev)  *****                                                              Jev***
[video: attachment:cccfa762-363d-40bc-a382-9f30cd9844aa:clm_vs_jev_2-1.mp4]
- ***WikiRacing Demo***
  Starting from the Wikipedia page on ***plate tectonics***, can a CLM navigate to the destination page on ***bioluminescence***?
[video: attachment:d6edaf9b-1a08-4b21-ac38-8b565d207687:wiki_plate.mp4]


### Zero-shot Evaluation
[image: attachment:0f30b6a6-7aaa-42bb-97b4-2a32d439f0c8:5.png]
Across **computer-use, gaming, and tool-calling tasks**, CLM-8B performs on par with Jev while running **up to 9× faster**. The speedups are most pronounced when the number of candidate actions is large (e.g., WikiRacing) or when actions can be frequently reused across states (e.g., T-Rex Game).


### Agentic Benchmarks
[image: attachment:f80107f6-9401-457a-b4e3-b7f19c65fbaa:a7e072a8-a2c1-4f31-9c10-1ab9771b4c69.png]
We find that **Jev fails to serve as a verifier** for long-horizon tasks, performing below the random-selection (Pass@1) baseline. In contrast, with lightweight fine-tuning, CLM achieves **SOTA performance** on challenging agentic benchmarks, including **DeepSWE (81.6%)** and **Terminal-Bench 2.1 (87.6%)**, while delivering **4–6× faster inference than Jev**.
For each task, we sample multiple candidate solutions using **Opus 5 for DeepSWE** and **Fable 5 for Terminal-Bench 2.1**. CLM or Jev then serves as the verifier, selecting the best solution from the candidate set. We evaluate performance on **38 held-out DeepSWE tasks** and **30 held-out Terminal-Bench 2.1 tasks**. Latency is measured on an H100 GPU.

### Model Architecture
A CLM consists of a **state encoder** and an **action encoder**, as illustrated in Figure 1. Both encoders map their respective inputs into a shared embedding space, where the score of a state–action pair is computed as the **cosine similarity** between their embeddings.
[image: attachment:dda173a5-6d73-440b-aa70-a430bc3c8048:image.png]
Each encoder consists of a frozen LLM backbone followed by a trainable projection head. We take the hidden state of the final token, normalize it, and pass it through a MLP projection head. Only the 20M-parameter projection head is trained; the LLM remains frozen and never receives gradients. This design makes our scaling experiments inexpensive to run. We precompute the LLM embeddings once, then reuse them to train projection heads across different setups. A full **pre-training run** on the Nemotron DQA dataset takes about **an hour** on a single RTX 4090 GPU.
Most importantly, since **states and actions are disaggregated**, their **embeddings can be cached independently**. In settings where the state evolves continuously (e.g., Super Mario) while the action set remains fixed, **we only need to recompute the state embedding at each step and can reuse the cached action embeddings**. This substantially reduces inference cost, with the efficiency gains becoming increasingly significant as the number of candidate actions and context length grows. At ~1k candidates, CLM is **13x faster** than Jev.
[image: attachment:05c1cd4f-d11d-47a6-8056-d644de99183e:image.png]
- Click to View More Experimental Details
  Since candidate action embeddings are cached, each CLM query requires only a single forward pass over the state followed by cosine-similarity computation against the cached candidate embeddings. We measure the practical efficiency gains against two baselines: **constrained decoding** using the same Qwen3-8B backbone (a single prefill over the state and all candidate options, followed by a softmax over option labels) and **Jev**, accessed through the TypeSafe API. All experiments use a **200-token state** on a single **4090 GPU **with 5 trials.
  1. **Scaling the number of candidates.** With 15 tokens per candidate, CLM latency increases only slightly, from **36 ms with 1 candidate** to **44 ms with 1,024 candidates**. Constrained decoding must process every candidate on every query, reaching 4.3 s and making it roughly 97× slower than CLM at 1k candidates. Jev increases from 131 ms to 579 ms, making **CLM roughly 13× faster at 1,024 candidates**.
  1. **Scaling candidate length.** With the number of candidates fixed at **5**, CLM latency remains essentially flat at **~36 ms** as candidate length increases from 1 to 2,048 tokens. In contrast, constrained decoding grows from **49 ms** to **3.4 s**, making it approximately **95× slower than CLM**. Jev reaches **333 ms**, approximately **9× slower than CLM**.
  Note: The projection head is a three-layer MLP that maps the 4,096-dimensional Qwen3-8B hidden state to a 512-dimensional embedding through a width of 1,536 (4096 → 1536 → 1536 → 512, GELU activations and a LayerNorm on the hidden layer).
**How does “Action Caching” work for CLM in Super Mario?** <!-- header_4 -->
[image: attachment:2a68d3a0-87a6-44f4-9324-d9d70f16e1ab:image.png]
The 4 action embeddings are precomputed before gameplay begins. At each step, only the new game state passes through the state encoder. Its embedding ⁍ is then scored against the cached action embeddings ⁍ , and the highest-scoring action is executed. This reduces the cost from **5** **forward passes to just 1 per step.**

### Training Algorithm
CLM is trained with a bidirectional InfoNCE loss. Given a batch of ⁍ matched state-action pairs, we compute a ⁍ similarity matrix. For each positive pair ⁍, we optimize retrieval in both directions: ⁍ and ⁍: 
$$\mathcal{L}_{\mathrm{CLM}}
=
-\frac{1}{2B}\sum_i
\left[
\log
\frac{\exp\left(s_i^\top a_i/\tau\right)}
{\sum_j \exp\left(s_i^\top a_j/\tau\right)}
+
\log
\frac{\exp\left(a_i^\top s_i/\tau\right)}
{\sum_j \exp\left(a_i^\top s_j/\tau\right)}
\right]$$
For mid-training, we extend the bidirectional InfoNCE objective with hard negatives. Let ⁍ denote a hard negative action for state ⁍. For the state-to-action direction, the loss is:
$$\mathcal{L}_{s\rightarrow a}^{\mathrm{hard}}
=
-\frac{1}{B}\sum_i
\log
\frac{
\exp\left(s_i^\top a_i/\tau\right)
}{
{\sum_j \exp\left(s_i^\top a_j/\tau\right)}
+
\sum_k \exp\left(s_i^\top h_{ik}^{(a)}/\tau\right)
}$$

### Scaling Laws for Verification
[image: attachment:e1c57b73-ee6a-4ad7-b458-f42b9d37376b:image.png]
We find that the test InfoNCE loss ⁍ scales as a power law with training compute ⁍, dataset size ⁍, projection-head size ⁍, and encoder size ⁍. These dimensions must be scaled jointly to achieve the optimal verification performance. When each scale factor is not bottlenecked by the others, the dependence on each variable ⁍ can be described as:
$$L(X) \approx  \left(\frac{X_c}{X}\right)^{\alpha_X},$$
where ⁍ is a fitted scale constant and ⁍ is the corresponding scaling exponent following Kaplan et al. Notably, scaling the encoder size yields the strongest gains. Experiments are conducted on the Nemotron DQA dataset and evaluated on a held-out dataset. 
**Data vs. Optimal Model Size** <!-- header_4 -->
[image: attachment:557b3ec6-b39a-4491-b6d5-a004141f39ae:image.png]
We fix a compute budget ⁍ and plot the test loss against the parameter count of the projection head ⁍, with each curve corresponding to a different data budget ⁍. In log-parameter space, each iso-FLOP curve is well approximated by a parabola, and its minimum identifies the optimal head size for that data budget. As the budget grows, the optimum shifts steadily toward larger heads. Specifically, the optimal size grows almost exactly linearly with the number of training tokens ⁍, at roughly **310 tokens per parameter**.

### Data Recipe
CLM is trained in three stages, with each stage introducing a progressively harder form of **state–action alignment**. Pre-training learns broad semantic representations, mid-training develops fine-grained discrimination, and post-training adapts the representation space for action classification.
[image: attachment:0aa38822-3af3-411d-b75f-79c124efc5c3:AdobeExpressPhotos_f97a482330874a9cbeb2a21fbaafe78b_CopyEdited.png]
**Stage 1 — Pre-training.** We first pre-train CLM on an internet-scale question–answer dataset containing **~60M pairs from Nemotron DQA**. We treat each question as the **state** and its answer as the corresponding **action**. This stage learns broad semantic representations from a diverse corpus.
**Stage 2 — Mid-training.** We then introduce **~30M synthetic hard negatives** generated by *Gemini 2.5 Flash-Lite*. For a subset of Nemotron DQA questions, we construct semantically similar but incorrect answers. These negatives are precomputed and incorporated into the **InfoNCE loss** using Equation 2, enabling more fine-grained discrimination between plausible actions.
**Stage 3 — Post-training.** Finally, we post-train CLM on **~1M agent trajectories** from the **Agent Data Protocol (ADP)** dataset, supplemented by terminal traces from **Endless-Terminals**, **LiteCoder-Terminal-SFT**. Each trajectory step is represented as a **state–action pair**, where the state contains the agent’s current context and the action corresponds to the decision taken at that step. This adapts the learned representation space for action classification in agentic environments.
Evaluating CLM after Pre-training <!-- header_4 -->
[image: attachment:bdb83c27-badd-4864-991e-77124cec9976:image.png]
We first evaluate **CLM-8B immediately after pre-training.** As illustrated above, when asked *“Who wrote the play Romeo and Juliet?”*, the Qwen3-8B embeddings assign the highest probability to an incorrect answer and ranks *“William Shakespeare”* third. 
In contrast, CLM-8B correctly ranks *“William Shakespeare”* first with **54.2%. **This suggests that **pre-training reshapes the model’s representations into a useful decision space.**
**Data Mixture for Post-Training** <!-- header_4 -->
[image: attachment:043e5478-9555-4d18-9039-d38c01500692:image.png]
To preserve the general representations learned during pre-training, we use **co-training with data replay** rather than fine-tuning exclusively on agentic traces. Specifically, **40%** of the post-training mixture consists of the Nemotron DQA examples, while the remaining **60%** are agentic trajectories.
This replay substantially mitigates catastrophic forgetting. With replay, the Nemotron hard-negative top-1 accuracy decreases slightly from **69% to 68.5%**. In contrast, when training on agentic data alone for the same number of agentic steps, the accuracy drops to 56.2%.
**Why Not Train on Hard Negatives from the Start?** <!-- header_4 -->
[image: attachment:3b48f497-5985-448a-90dd-f00941f5614b:image.png]
We compare two training strategies under a fixed compute budget:
- **Pre-train + Mid-train:** pre-train on the full Nemotron DQA corpus with bidirectional InfoNCE, then briefly mid-train on hard negatives using Equation 2.
- **Hard negatives from scratch:** train on Nemotron DQA and hard negatives jointly from the beginning.
We evaluate on ~100K held-out questions, each with one gold answer and 10 hard negatives. The top-1 accuracy measures whether the gold answer ranks highest. We find that pre-training alone reaches **52.1%** without seeing any hard negatives. A short mid-training stage then boosts accuracy to **69.2%**. In contrast, training with hard negatives from the start improves quickly but peaks at **62.4%** before overfitting. The two-stage recipe achieves **7% higher accuracy **at fixed budget.
> 
**Takeaway: **Hard negatives work best as a refinement signal on top of pre-training, rather than as a substitute for it.

### CLM Playground
[image: attachment:94562134-d4e9-4915-88de-60ab3fddda42:playground.png]
CLM comes with a playground on [GitHub](https://github.com/Contrastive-LM/CLM). Write a state, add typed questions, and see CLM's full probability distribution over the answers in milliseconds. 

### Does CLM work for robotics?
[video: attachment:b819b8ed-7db9-4117-8d8f-91f9b7e90aaa:6.mp4]
We released a robotics variant of CLM earlier this year. See the [CoVer-VLA paper](https://arxiv.org/abs/2602.12281) for more details on **verification scaling **for vision-language-action (VLA) models.

## Join us!
> 
 We call on the community to join us in this effort, either by providing your feedback or contributing to the project!
Please don’t hesitate to get in touch:
**Github Repo:** [https://github.com/Contrastive-LM/CLM](https://github.com/Contrastive-LM/CLM)
**Join Discord:** [https://discord.gg/5dAQEDJBs](https://discord.gg/5dAQEDJBs)
**Contact:** jackykwok@stanford.edu

## Conclusion
CLM opens up a new direction for scalable, reliable, and fast verification. Moving forward, we plan to explore several key directions:
1. **Scaling Experiments:** Extend our scaling-law experiments to substantially larger backbones and study how verification performance can be further scaled
1. **Vision and multimodal support:** Extend CLM to include images, video, and other modalities for robotics and computer-use tasks.
1. **Scaling the data recipe:** Expand pre-training, hard-negative mining, and agentic post-training.
**…and more to come.**

**CLM-8B** is part of our scaling ladder, where we train models across multiple scales to establish scaling laws and predict performance at larger scales. A **multimodal CLM-35B** is now in training with more data, compute, and parameters. Stay tuned for the release early next month 🚀

## **Citation**
If you find CLM useful, please consider citing it:
```XML
@misc{kwok2026contrastivelanguagemodels,
  title={Contrastive Language Models: A System One Approach for Fast and Generalizable Decision-Making},
  author={Jacky Kwok and Hangoo Kang and Tarun Suresh and Jon Saad-Falcon and Marco Pavone and Christopher Ré and Azalia Mirhoseini},  
  year={2026},
  note={Notion Blog}
}
```

