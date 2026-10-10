---
type: concept
tags: [selective-prediction, abstention, risk-coverage, aurc, evaluation, groundone]
---
# Selective Prediction (reject option, abstention)

## Idea
A selective predictor may **abstain** ("don't know") on inputs where it is unsure. It trades **coverage** (the fraction of inputs it answers) for lower **risk** (the error rate on the inputs it does answer). The field is about 60 years old ([[Geifman 2017 - Selective Classification for Deep Neural Networks|Geifman & El-Yaniv 2017]], §1). The goal is a "dial" that sets the error rate you want while keeping coverage as high as possible.

**In plain words:** let the verifier decide on its own only when it is confident, and send the rest to a slower checker (an LLM judge or a human). The question is how much error remains on the cases it decides alone, and what share of cases it can decide alone.

## Formalism (Geifman & El-Yaniv §2)
- Selective classifier $(f,g)$: output $f(x)$ if $g(x)=1$, otherwise abstain.
- Threshold on a confidence function $\kappa$: $g_\theta(x)=\mathbb 1[\kappa(x)\ge\theta]$ (Eq. 3).
- **Coverage** $\phi(f,g)=\mathbb E[g(x)]$.
- **Selective risk** $R(f,g)=\dfrac{\mathbb E[\ell(f(x),y)\,g(x)]}{\phi(f,g)}$ (Eq. 1).
- **Risk–coverage (RC) curve**: selective risk as a function of coverage as $\theta$ is swept. It describes the whole performance profile.
- **AURC** (area under the RC curve): one number, lower is better. It was introduced in later work by the same group, not in the 2017 paper. A related number is Tian 2023's "AUC" of selective *accuracy* vs. coverage (higher is better).

Only the **ranking** produced by $\kappa$ matters. So **temperature scaling does not change the RC curve or AURC**. Calibration ([[Expected Calibration Error]]) and selective performance measure different things and should both be reported.

## Choosing thresholds
- **Fixed confidence cut-offs** (auto-accept above 0.9, escalate below 0.5) are only meaningful if the model is **calibrated**. This is the use case [[Reinforcement Learning with Calibrated Decisions]] and [[Jev]] advertise.
- **Target-risk thresholds with a guarantee: SGR** (Geifman Algorithm 1). Given a target risk $r^*$ and confidence $\delta$, binary-search $\theta$ on a labelled held-out set using a binomial tail bound, so that $\Pr\{R(f,g)>r^*\}<\delta$. Example: CIFAR-10, 1% error guaranteed at about 78% coverage with δ = 0.001 (Table 1). ImageNet top-5, 2% error at almost 60% coverage (abstract).
- **Cost-based thresholds**: if the cost of a missed hallucination and the cost of escalating are known, choose the θ that minimises expected cost. Geifman notes such costs are often hard to specify (§1).
- Confidence function: **softmax response** (max class probability) was as good as or better than MC-dropout in Geifman's experiments (Fig. 2), and costs nothing extra.

## Link to abstention in GroundOne
- Per sentence, $\kappa = \max(p_A,p_B)$ after the 2-way softmax *(superseded: the readout is now 3-way A/B/C, so $\kappa = \max(p_A,p_B,p_C)$ after calibration)*, or asymmetric thresholds on $P(\text{supported})$:
  - $P(\text{supported})\ge\theta_{hi}$ → mark green (auto-accept);
  - $P(\text{supported})\le\theta_{lo}$ → mark red (likely hallucination);
  - in between → **abstain / escalate** to a generative [[LLM-as-a-Judge]] or a human.

  This is the hybrid "System One gate, System Two fallback" from [[When System One Beats an LLM]].
- Report the **RC curve and AURC** for the 0.5B and 3B verifiers and the baselines. Also report the **coverage at a fixed risk** (e.g. "unsupported sentences accepted ≤ 5%"), ideally with an SGR-style guarantee on a held-out split.
- For hallucination detection the costs are asymmetric. A missed unsupported sentence is usually worse than a false alarm. Consider risk defined as the *false-accept rate* among accepted sentences, rather than plain 0/1 error.
- Earlier thesis routing work had an explicit abstain class (`Z`). For GroundOne, abstention is derived from the threshold instead, which avoids the "none of the above" bias [[Kadavath 2022 - Language Models (Mostly) Know What They Know|Kadavath]] found (§3.1).

## Evidence from GroundOne: AURC separates systems that ECE cannot (B0d, 2026-10-09)
In the equal-output comparison, zero-shot same-size judges and GroundOne received the **same** temperature + per-class bias calibration, fitted on 200 dev answers. They were evaluated on the 200-answer T1 latency subset:

| System | ECE after calibration | Binary AUROC | AURC (calibrated) |
| --- | --- | --- | --- |
| GroundOne 0.5B / 3B | 0.034 / 0.030 | 0.940 / 0.969 | **0.009 / 0.005** |
| Equal-output judge, logits, 0.5B / 3B | 0.039 / 0.041 | 0.483 / 0.681 | 0.063 / 0.048 |
| Equal-output judge, verbalised, 0.5B / 3B | 0.051 / 0.044 | 0.470 / 0.576 | 0.061 / 0.062 |

- Every system lands at ECE 0.03–0.05. A calibration map can match average confidence to the base rate even when the probabilities do not separate correct from wrong verdicts: the 0.5B judges have AUROC below 0.5. **AURC is 5–12× lower for GroundOne**, which is the number that matters for abstention and escalation.
- The same pattern appears in the literature: GPT-4 reaches ECE 0.064 on GSM8K by giving 100 % confidence to every answer, at chance-level failure prediction ([[Xiong 2024 - Can LLMs Express Their Uncertainty]] §5.2). See also [[Verbalised vs Logit Confidence]].
- **Rule for the thesis:** report the RC curve / AURC and AUROC next to ECE; never ECE alone.
- **Served threshold (D27).** The HTTP API labels a sentence "supported" iff calibrated P(supported) ≥ τ, with τ fitted on dev by maximising three-way macro recall (τ ≈ 0.90–0.94). This is a cost-agnostic operating point. A target-risk threshold (SGR-style, above) remains the principled alternative for a "System One gate, System Two fallback" deployment.

## Links
- [[Verbalised vs Logit Confidence]], [[Statistical Significance and Bootstrap]]
- [[Calibration]], [[Expected Calibration Error]], [[GroundOne]], [[Groundedness Verification]], [[Hallucination Detection]], [[LLM-as-a-Judge]], [[System One Models]], [[When System One Beats an LLM]], [[Reinforcement Learning with Calibrated Decisions]], [[Jev]]
- Sources: [[Geifman 2017 - Selective Classification for Deep Neural Networks]], [[Tian 2023 - Just Ask for Calibration]], [[Guo 2017 - On Calibration of Modern Neural Networks]], [[Xiong 2024 - Can LLMs Express Their Uncertainty]]
