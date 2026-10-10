Source: https://huggingface.co/vllm-sr/Vela-2.0-9B (revision 068425bb145c05884a98b870c219047da22d9aea): README.md, then EVALUATION.md and TRAINING.md from the same repository — retrieved 2026-10-10

---
license: apache-2.0
pipeline_tag: zero-shot-classification
base_model:
- vllm-sr/Decision-2.0-Lux-9B
base_model_relation: finetune
datasets:
- nvidia/Aegis-AI-Content-Safety-Dataset-2.0
- ToxicityPrompts/PolyGuardMix
- nvidia/Nemotron-Safety-Guard-Dataset-v3
- microsoft/llmail-inject-challenge
- OpenSafetyLab/Salad-Data
- KRLabsOrg/lettucedetect-prose-hallucination
- KRLabsOrg/lettucedetect-code-hallucination
- numind/NuNER
- urchade/pile-mistral-v0.1
- knowledgator/GLINER-multi-task-synthetic-data
- nlpaueb/finer-139
- tonytan48/Re-DocRED
- MultiCoNER/multiconer_v2
- martinjosifoski/SynthIE
- rajpurkar/squad_v2
- hotpotqa/hotpot_qa
- google-research-datasets/natural_questions
- KRLabsOrg/verbatim-spans
- KRLabsOrg/tool-output-extraction-swebench
language:
- ar
- zh
- cs
- nl
- en
- fr
- de
- hi
- it
- ja
- ko
- pl
- pt
- ru
- es
- sv
- th
tags:
- decision-model
- system-one
- qwen3.5
- semantic-router
- vela
- zero-shot-classification
- token-classification
- named-entity-recognition
- pii-detection
- hallucination-detection
- content-safety
- multilingual
- long-context
---

<div align="center">
  <img src="https://huggingface.co/vllm-sr/Vela-2.0-9B/resolve/main/assets/vela2-banner.jpg" alt="Vela 2.0: Towards Open Foundation Routing Models. vLLM Semantic Router x KR Labs" width="100%" />
  <p>
    <a href="https://vllm-sr.ai/"><strong>Docs</strong></a> |
    <a href="https://vllm-sr.ai/blog/vela-2-0-open-foundation-routing-models"><strong>Blog</strong></a> |
    <a href="https://github.com/vllm-project/semantic-router"><strong>GitHub</strong></a> |
    <a href="https://huggingface.co/collections/vllm-sr/vela-20"><strong>Vela 2.0 collection</strong></a>
  </p>
</div>

# Vela 2.0 9B

**Open Foundation Routing Models**

*Routing decisions. Safety checks. Precise text spans.*

The largest hybrid member of Vela 2.0: high-accuracy multilingual routing, long-document PII and hallucination detection, with open-label spans through one interface.

Define options, labels and rubrics at request time. Ask multiple named questions about a request, context and answer, and receive structured decisions with the text spans that support your workflow.

1. **High-accuracy decisions.** A 41.63 Jev Decision Index with optional Noul calibration, plus 0.989 AUC on unseen prompt-attack families.
2. **Routing and safety together.** Use one request for routing, prompt-attack checks, PII and unsupported-claim detection.
3. **Decisions at span resolution.** Return precise text locations for trained router labels and open-label extraction, with probabilities and character offsets.

| Specification | Value |
| --- | --- |
| Reported parameters | 7.9B |
| Backbone | 32-layer Qwen3.5 hybrid: Gated DeltaNet and gated GQA |
| Input limit | 16,384 tokens |
| Output | Choice, Yes/no (Noul), Score, Span and Set; no text generation |
| Evaluated precision | FP32 parameters; bf16 backbone autocast on GPU; FP32 heads |
| GPU parameter memory | About 32 GB in FP32 |
| Licence | Apache-2.0 |

## Quickstart

Install the dependencies, load the model and ask for routing and spans in one request:

For focused examples, see [Span questions](#span-questions-locate-text) and [Set questions](#set-questions-select-multiple-labels) below.

```bash
pip install torch "transformers>=5.17" safetensors tokenizers numpy
pip install flash-linear-attention   # GPU: the Gated-DeltaNet kernel used in evaluation (optional, much faster)
```

```python
from transformers import AutoModel

m = AutoModel.from_pretrained("vllm-sr/Vela-2.0-9B", trust_remote_code=True)
m = m.to("cuda")   # parameters load in FP32; on GPU the backbone runs under bf16 autocast (heads FP32)

PII_LABELS = m.vela2_engine.cal["pii_schema"]["labels"]   # the 17 trained PII types

result = m.system_one(
    state={"request": "Hi, I'm Tom Baker (tom.baker@example.com). What is the maximum daily dose of paracetamol for an adult?",
           "source": "For adults, the maximum dose of paracetamol is 4 grams in 24 hours, taken as 500 mg to 1 g every 4 to 6 hours.",
           "answer": "Adults can take up to 6 grams of paracetamol in 24 hours, in doses of 500 mg to 1 g every 4 to 6 hours."},
    questions={
        "pii": {"type": "span", "instructions": "Which spans are personal information?", "criteria": PII_LABELS,
                "over": "request"},
        "halu": {"type": "span", "instructions": "Which spans of the answer are not supported by the context?",
                 "criteria": {"unsupported": "a claim not supported by the context"}},   # over the answer by default
        "domain": {"type": "choice", "instructions": "Which subject area is this request about?", "over": "request",
                   "criteria": {"health": "medicine, clinical practice, nutrition, ageing or sexual health",
                                "math": "arithmetic, algebra, geometry, statistics or other mathematics",
                                "other": "a subject that fits none of the listed areas"}},
    })
```

Recorded response excerpt from this release; the [full response](USAGE.md#routing-and-span-questions) includes usage and thresholds:

```json
{
  "answers": {
    "domain": {
      "type": "choice",
      "choice": "health",
      "confidence": 0.977,
      "probabilities": {
        "health": 0.988,
        "math": 0.0,
        "other": 0.012
      }
    }
  },
  "spans": {
    "pii": [
      {
        "label": "PERSON",
        "start": 8,
        "end": 17,
        "text": "Tom Baker",
        "probability": 0.999
      },
      {
        "label": "EMAIL_ADDRESS",
        "start": 19,
        "end": 40,
        "text": "tom.baker@example.com",
        "probability": 1.0
      }
    ],
    "halu": [
      {
        "label": "unsupported",
        "start": 22,
        "end": 29,
        "text": "6 grams",
        "probability": 0.982
      }
    ]
  },
  "span_heads": {
    "pii": "router",
    "halu": "router"
  }
}
```

GPU with bf16 autocast is the evaluated setting. FP32 on CPU or GPU is also supported; fp16 is not. Parameter memory above excludes runtime allocations. See [precision and execution](USAGE.md#precision-and-execution).

### Span questions: locate text

Use `"type": "span"` to extract text with labels and character offsets. Set `criteria` to a label-to-description mapping and `over` to the state field to inspect. This PII example reuses `m` and the trained `PII_LABELS` from above:

```python
span_result = m.system_one(
    state={"request": "Hi, I'm Tom Baker (tom.baker@example.com)."},
    questions={
        "pii": {
            "type": "span",
            "instructions": "Which spans are personal information?",
            "criteria": PII_LABELS,
            "over": "request",
        }
    },
)
print(span_result["spans"]["pii"])
```

Each returned span includes `label`, `text`, `start`, `end` and `probability`. Offsets use Unicode code points, with `start` inclusive and `end` exclusive, in the selected field. The first example also shows hallucination detection: use the `unsupported` label, target `over="answer"`, and supply grounding text in `state["source"]`.

**Two span heads, one interface.** The router span head handles trained PII, hallucination and toxic labels. The broad span head handles open-label extraction. The engine selects a head for each span question; you can also set `"head": "router"` or `"head": "broad"`. See [span-head selection](USAGE.md#span-head-selection). For entities, relations and evidence examples, see [open-label extraction](USAGE.md#open-label-extraction).

### Set questions: select multiple labels

Use `"type": "set"` when zero, one or several labels can apply. Supply your labels and descriptions in `criteria`; each label is scored independently. This example reuses `m` from above:

```python
set_result = m.system_one(
    state="My card was charged twice and the parcel never arrived.",
    questions={
        "issues": {
            "type": "set",
            "instructions": "Which issues does the customer report?",
            "criteria": {
                "billing": "payments, charges, refunds or invoices",
                "shipping": "delivery of an order or a parcel",
                "login": "signing in, passwords or account access",
            },
        }
    },
)
print(set_result["sets"]["issues"]["selected"])
print(set_result["sets"]["issues"]["probabilities"])
```

Read the selected labels and all per-label probabilities from `sets["issues"]`. Probabilities do not need to sum to one. Labels are selected when their probability exceeds the question's threshold; omit `threshold` to use shipped calibration, or add it to the question to set your own cutoff. The applied value is returned in `set_result["thresholds"]["issues"]`.

## Questions and outputs

| Question | Use it for | Output |
| --- | --- | --- |
| **Choice** | Route a request or select one of 2–255 supplied options. | Selected key and distribution |
| **Yes/no (Noul)** | Check a condition against the state. | P(yes) |
| **Score** | Rate against 2–10 ordered levels. | Expected level and distribution |
| **Span** | Locate personal information, unsupported claims, entities, relations or evidence. | Text spans, character offsets and probabilities |
| **Set** | Select any number of supplied labels. | Selected labels and per-label probabilities |

Span offsets refer to Unicode code points in the selected text. Span and Set answers also provide Yes/no views in the SystemOne response. [Output semantics and thresholds](USAGE.md#output-semantics) explain these fields.

## Results

Selected results for this checkpoint. [Full evaluation](EVALUATION.md) includes every benchmark, family comparison and scoring protocol.

| Benchmark | Result | Metric and mode |
| --- | ---: | --- |
| Safety, 14 public sets | **0.921** | Mean AUC; trained task families |
| Prompt attacks, unseen families | **0.989** | AUC |
| PII, 8K-token documents | **0.940** | F1; shipped calibration |
| Hallucination, 10,698 examples | **0.885** | Example-F1 |
| ACL-Verbatim evidence | **24.5** | Word-F1; broad span head, zero-shot |
| Jev Decision Index 0.2.1 | **41.63** | 38 benchmarks; `noul_calibration=True` |

- **Evaluation:** checkpoint selection, temperatures and thresholds used dev data. Safety results cover trained task families; they are not zero-shot comparisons.
- **Calibration:** Jev uses optional `noul_calibration=True`; the default score is 41.09. PII uses shipped calibration. [All evaluation modes](EVALUATION.md).

## Architecture

<p align="center"><img src="https://huggingface.co/vllm-sr/Vela-2.0-9B/resolve/main/assets/architecture/04-vela-2.0-9b-architecture.png" alt="Vela 2.0 9B model architecture" width="720" /></p>

This model has its own 32-layer hybrid backbone, with Gated DeltaNet and gated GQA blocks, a candidate head, and separate router/broad span-head weights. [Editable SVG](assets/architecture/04-vela-2.0-9b-architecture.svg).

<details>
<summary>Operator and readout diagrams</summary>

**Gated DeltaNet**

<p align="center"><img src="https://huggingface.co/vllm-sr/Vela-2.0-9B/resolve/main/assets/architecture/07-gated-deltanet.png" alt="Vela 2.0 hybrid backbone: Gated DeltaNet operator" width="100%" /></p>

Causal QKV convolution feeds the gated-delta update, followed by per-head normalization and output gating. [Editable SVG](assets/architecture/07-gated-deltanet.svg).

**Gated GQA and SwiGLU**

<p align="center"><img src="https://huggingface.co/vllm-sr/Vela-2.0-9B/resolve/main/assets/architecture/08-gated-gqa-swiglu.png" alt="Vela 2.0 hybrid backbone: gated GQA and SwiGLU operators" width="100%" /></p>

Gated GQA uses partial RoPE on Q/K and a sigmoid output gate; SwiGLU uses separate up and gate projections. [Editable SVG](assets/architecture/08-gated-gqa-swiglu.svg).

**Candidate readout**

<p align="center"><img src="https://huggingface.co/vllm-sr/Vela-2.0-9B/resolve/main/assets/architecture/09-decoder-candidate-head.png" alt="Vela 2.0 hybrid models: CandidateHead bilinear and MLP scoring" width="100%" /></p>

CandidateHead combines scaled bilinear and additive MLP scores over runtime options, then applies task-specific calibration. [Editable SVG](assets/architecture/09-decoder-candidate-head.svg).

**Router and broad span heads**

<p align="center"><img src="https://huggingface.co/vllm-sr/Vela-2.0-9B/resolve/main/assets/architecture/10-decoder-span-heads.png" alt="Vela 2.0 hybrid models: word-label SpanHeadV2 and router/broad selection" width="100%" /></p>

Router and broad span heads have separate weights, with one selected for each span question. Overlapping word logits are combined before decoding. [Editable SVG](assets/architecture/10-decoder-span-heads.svg).

**State prefix and question isolation**

<p align="center"><img src="https://huggingface.co/vllm-sr/Vela-2.0-9B/resolve/main/assets/architecture/11-state-prefix-and-question-isolation.png" alt="Vela 2.0 hybrid models: state prefix reuse and isolated question blocks" width="100%" /></p>

For a fixed rendered state, each question block sees the same state prefix and its own causal tokens. Additional span questions use separate sequences. [Editable SVG](assets/architecture/11-state-prefix-and-question-isolation.svg).

</details>

Choice, Yes/no, Score and Set share a candidate readout. Router and broad span heads use the same word-by-label topology with separate weights. The hybrid backbone reuses the state prefix within each rendered sequence; execution details are in [USAGE.md](USAGE.md#precision-and-execution).

## Reference

| Document | Contents |
| --- | --- |
| [USAGE.md](USAGE.md) | Full examples and recorded responses, typed parts, head selection, calibration, SDK and HTTP serving |
| [EVALUATION.md](EVALUATION.md) | Complete family results, research versus shipped PII modes, benchmark protocols and evaluation disclosures |
| [TRAINING.md](TRAINING.md) | Training stages, data mixtures, provenance, licences and release files |
| [PARITY.md](PARITY.md) | Export parity against the research scorer |

## Credit and citation

Vela 2.0 is led by KR Labs and [vLLM Semantic Router](https://github.com/vllm-project/semantic-router).

Read the [Vela 2.0 technical overview](https://vllm-sr.ai/blog/vela-2-0-open-foundation-routing-models/).

```bibtex
@misc{vela2_9b_2026,
  title        = {Vela 2.0: Towards Open Foundation Routing Models},
  author       = {{KR Labs} and {vLLM Semantic Router}},
  year         = {2026},
  note         = {Blog post. Model: vllm-sr/Vela-2.0-9B},
  howpublished = {\url{https://vllm-sr.ai/blog/vela-2-0-open-foundation-routing-models/}}
}
```

## Licence

Apache-2.0 for this model's weights, code and documentation. It is derived from [Decision-2.0-Lux-9B](https://huggingface.co/vllm-sr/Decision-2.0-Lux-9B) (Apache-2.0), itself built on Qwen3.5-9B (Apache-2.0); their licences and notices are passed on in `LICENSE`, `NOTICE`, `ATTRIBUTIONS.md` and `LICENSES/`. Changes against Decision-2.0-Lux-9B: [MODIFICATIONS.md](MODIFICATIONS.md). Training data keep their own licences, some of them CC-BY-SA share-alike.

# Evaluation: Vela 2.0 9B

[Model card](README.md) · [Usage](USAGE.md) · [Training](TRAINING.md)

The tables retain the full released results, including comparisons and task breakdowns. Test texts are held out of training; calibration and release-selection protocols are described separately below.

## Family results

<p align="center"><img src="https://huggingface.co/vllm-sr/Vela-2.0-9B/resolve/main/assets/vela2-family.jpg" alt="Four sizes, one family: 0.3B, 0.8B, 4B, 9B" width="80%" /></p>

| Model | Safety (AUC, 14 sets) | PII, 8K (F1; Vela 2.0 shipped calibration) | Hallucination (F1) | RAGTruth (F1) | fast-decisions | Jev Index (Vela 2.0: `noul_calibration=True`) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| **Vela 2.0 9B** | 0.921 | **0.940** | 0.885 | 0.774 | 62.5 | 41.63 |
| [Vela 2.0 0.3B (encoder)](https://huggingface.co/vllm-sr/Vela-2.0-0.3B) | 0.871 | 0.929 | 0.848 | 0.706 | 49.4 | – |
| [Vela 2.0 0.8B](https://huggingface.co/vllm-sr/Vela-2.0-0.8B) | 0.875 | 0.603 | 0.828 | 0.652 | 56.8 | 16.01 |
| [Vela 2.0 4B](https://huggingface.co/vllm-sr/Vela-2.0-4B) | **0.921** | 0.906 | 0.874 | 0.770 | 61.5 | 31.91 |
| Vela 1.0 specialists (one model per task) | – | 0.908 | 0.875 | 0.747 | – | – |
| [LettuceDetect v2 qwen-2b](https://huggingface.co/KRLabsOrg/lettucedect-v2-qwen-2b) (generative, hallucination only) | – | – | **0.921** | **0.817** | – | – |
| [LettuceDetect v2 mmBERT-base](https://huggingface.co/KRLabsOrg/lettucedect-v2-mmbert-base) (hallucination only) | – | – | 0.869 | 0.743 | – | – |
| [GLiNER2.5-Decide](https://huggingface.co/fastino/GLiNER2.5-Decide) | 0.704 | – | – | – | **62.9** | – |
| [Decision-2.0-Lux-9B](https://huggingface.co/vllm-sr/Decision-2.0-Lux-9B) (our base, Decision 2.0) | – | – | – | – | – | **46.23** |

The decoder checkpoints, temperatures and thresholds were selected on dev data only. The **0.3B encoder follows a different release-selection protocol**: final release selection also considered test results. Its 0.929 shipped 8K PII result uses a threshold floor lowered after the test effect was seen; the test-blind 0.001 floor gives 0.896, and the research scorer gives 0.894. The 0.3B fast-decisions result is not an independent zero-shot evaluation for that checkpoint. See the [0.3B evaluation disclosures](https://huggingface.co/vllm-sr/Vela-2.0-0.3B/blob/main/EVALUATION.md).

| Comparison detail | Protocol |
| --- | --- |
| LettuceDetect v2, RAGTruth | Re-scored by us on the same 2,700 rows, using its own evaluation input; reproduces its model cards |
| LettuceDetect v2, 10,698 examples | Values from its model cards on the same test set |
| Jev Decision Index | Edition 0.2.1, 38 general decision benchmarks; optional Noul calibration enabled |
| This decoder, default Jev mode | 41.09 with optional Noul calibration off |
| Decision 2.0 bases | Same harness, reproducing released cards within 0.1: Eos 20.14, Nox 42.55, Lux 46.23 |

The routing recipe trades part of the base model's general-decision score for the router tasks. The family table keeps the base and specialist references visible so that this tradeoff can be assessed.

## Router tasks against per-task references

PII rows in this table use the research scorer's per-length dev thresholds. All other metrics retain the released task definitions. The delta column is paired against the named task reference.

| Task | Reference model | Reference score | **Vela 2.0 9B (research PII thresholds)** | Δ points [95% CI] | Vela 2.0 0.8B | Vela 2.0 4B | Vela 2.0 0.3B |
|---|---|---:|---:|---:|---:|---:|---:|
| Request harm, RTP-LX (AUC) | Safety | 0.761 | **0.801** | +4.0 [+3.4, +4.5] | 0.710 | 0.774 | 0.728 |
| Hate speech, Multilingual HateCheck (AUC) | Safety | 0.646 | **0.855** | +20.9 [+20.3, +21.5] | 0.653 | 0.769 | 0.662 |
| Request harm, CultureGuard (AUC) | Safety | 0.863 | **0.902** | +4.0 [+3.6, +4.2] | 0.850 | 0.898 | 0.900 |
| Prompt attacks, unseen families (AUC) | Guard | 0.792 | **0.989** | +19.8 [+15.4, +23.9] | 0.940 | 0.985 | 0.882 |
| Domain (macro-F1) | Domain | 0.831 | **0.844** | +1.3 [−0.3, +2.8] | 0.759 | 0.820 | 0.825 |
| Modality (macro-F1) | Modality | 0.889 | **1.000** | +11.1 [+9.4, +12.7] | **1.000** | **1.000** | 0.961 |
| Fact-check needed (macro-F1) | FactCheck | 0.501 | **1.000** | +49.9 [+46.1, +53.5] | 0.999 | **1.000** | 0.997 |
| Feedback (macro-F1) | Feedback | 0.425 | 0.939 | +51.3 [+48.8, +54.1] | 0.904 | 0.920 | **0.989** |
| PII, short texts (F1) | PII | 0.976 | 0.985 | +0.9 [+0.1, +1.9] | 0.984 | 0.987 | **0.995** |
| PII, 4K-token documents (F1) | PII | 0.928 | 0.965 | +3.6 [−0.3, +6.8] | 0.624 | 0.898 | **0.987** |
| PII, 8K-token documents (F1) | PII | 0.908 | **0.940** | +3.2 [−1.1, +7.0] | 0.603 | 0.905 | 0.894 |
| Hallucination, 10,698 examples (F1) | Halu | 0.875 | **0.885** | +1.0 [+0.4, +1.7] | 0.828 | 0.874 | 0.848 |
| RAGTruth (F1) | LettuceDetect v2 mmBERT | 0.743 | **0.774** | +3.0 [+0.5, +5.4] | 0.652 | 0.770 | 0.706 |
| Toxic spans (char-F1) | mmBERT span head | **0.451** | 0.446 | −0.5 [−1.2, +0.2] | 0.366 | 0.379 | 0.423 |

### PII calibration modes

| Mode for this checkpoint | Short / 4K / 8K F1 |
| --- | --- |
| Research scorer, per-length dev thresholds | 0.985 / 0.965 / 0.940 |
| Shipped calibration, end to end | 0.987 / 0.959 / 0.940 |

The family summary uses shipped 8K calibration; the router comparison uses research-scoring thresholds. Both decoder modes are dev-selected. The 0.3B encoder's research and shipped results, and its test-informed release selection, are disclosed next to the family table above.

## Safety, all 14 sets (AUC)

| set | **Vela 2.0 9B** | Vela 2.0 0.8B | Vela 2.0 4B | Vela 2.0 0.3B | Vela 1.0 | GLiNER2.5-Decide |
|---|---:|---:|---:|---:|---:|---:|
| RTP-LX, request harm | **0.801** | 0.710 | 0.774 | 0.728 | 0.761 | 0.642 |
| Multilingual HateCheck | **0.855** | 0.653 | 0.769 | 0.662 | 0.646 | 0.602 |
| XSTest, request harm | **0.990** | 0.854 | 0.967 | 0.890 | 0.782 | 0.807 |
| CultureGuard, request harm | **0.902** | 0.850 | 0.898 | 0.900 | 0.863 | 0.674 |
| Prompt attacks, unseen families | **0.989** | 0.940 | 0.985 | 0.882 | 0.792 | 0.893 |
| Prompt attacks, known families | **0.962** | 0.948 | 0.956 | 0.950 | 0.820 | 0.569 |
| deepset prompt injections | **0.990** | 0.970 | 0.989 | 0.957 | 0.779 | 0.761 |
| CultureGuard, response harm | **0.941** | 0.860 | 0.937 | 0.916 | 0.828 | 0.624 |
| AEGIS 2.0, response harm | 0.931 | 0.883 | **0.934** | 0.917 | 0.872 | 0.660 |
| PolyGuard, response harm | **0.957** | 0.901 | 0.925 | 0.936 | 0.884 | 0.759 |
| Do-Not-Answer, response harm | 0.777 | 0.883 | **0.931** | 0.656 | 0.418 | 0.416 |
| Do-Not-Answer, refusal | 0.913 | **0.918** | 0.893 | 0.896 | – | 0.886 |
| XSTest, refusal | 0.989 | 0.973 | **0.992** | 0.955 | – | 0.887 |
| PolyGuard, refusal | 0.894 | 0.907 | 0.945 | **0.947** | – | 0.683 |
| **mean** | 0.921 | 0.875 | **0.921** | 0.871 | – | 0.704 |

These comparisons cover trained safety families. They are not zero-shot comparisons against GLiNER2.5-Decide, which was not trained on these families. Vela 1.0 uses Safety for harm and Guard for attacks; it has no refusal output.

## General and held-out decisions

| benchmark | **Vela 2.0 9B** | Vela 2.0 0.8B | Vela 2.0 4B | Vela 2.0 0.3B | reference |
|---|---:|---:|---:|---:|---|
| `fastino/fast-decisions` (17 domains) | 62.5 | 56.8 | 61.5 | 49.4 | GLiNER2.5-Decide 62.9 |
| MASSIVE, unseen scenarios: intent / scenario accuracy | 0.763 / 0.871 | 0.544 / 0.632 | 0.727 / 0.814 | 0.510 / 0.575 | – |
| QASC, 8-way science QA (held out) | 0.644 | 0.434 | 0.640 | 0.251 | chance 0.125 |
| Super-NI task 1568 (held out) | 0.574 | 0.340 | 0.494 | 0.370 | – |

Differences are paired bootstrap 95% intervals with 2,000 resamples. This decoder's checkpoint, temperatures and thresholds were chosen on dev data only. The 0.3B fast-decisions figure follows the encoder's separately disclosed release-selection protocol and is not an independent zero-shot result for that checkpoint.

## Open extraction benchmarks

The broad span head is evaluated on open-label NER, relations, extractive QA and evidence. **SQuAD v2 dev is not zero-shot for this model**: its training split is in the broad-head data. NER and ACL-Verbatim are evaluated with the held-out protocols below.

| Model | NER, 7 sets (F1) | Relations, CoNLL04 (F1) | SQuAD v2 dev (F1) | ACL-Verbatim evidence (word F1) | Latency, 3K-token context (ms) |
|---|---:|---:|---:|---:|---:|
| **Vela 2.0 9B, broad span head** | 43.5 | **10.1** | **71.5** | 24.5 | 2288 |
| [GLiNER2.5-base](https://huggingface.co/fastino/gliner2.5-base-v1) | 55.9 | 8.5 | 45.5 | 2.8 | **360** |
| [GLiNER2.5-Decide](https://huggingface.co/fastino/GLiNER2.5-Decide) | 51.5 | 1.5 | 46.0 | 2.3 | 415 |
| [GLiFormer-base](https://huggingface.co/knowledgator/gliformer-base-v1) | 60.4 | 8.6 | 53.1 | 2.7 | 386 |
| [GLiFormer-large](https://huggingface.co/knowledgator/gliformer-large-v1) | **63.6** | 6.2 | 47.0 | 7.0 | 930 |
| [GLiNER large-v2.5](https://huggingface.co/gliner-community/gliner_large-v2.5) | 61.3 | 7.5 | 54.9 | 4.6 | 496 |
| [ACL-Verbatim ModernBERT](https://huggingface.co/KRLabsOrg/acl-verbatim-modernbert) (trained in-domain, evidence only) | – | – | – | **53.4** | – |

NER per set (CrossNER and MIT, strict micro-F1, label names only):

| Model | AI | Literature | Music | Politics | Science | Movie | Restaurant | mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **Vela 2.0 9B, broad span head** | 39.6 | 34.7 | 40.2 | 50.9 | 56.7 | 45.7 | 36.7 | 43.5 |
| [GLiNER2.5-base](https://huggingface.co/fastino/gliner2.5-base-v1) | 52.5 | 52.2 | 57.4 | 63.2 | 59.3 | **60.6** | 46.4 | 55.9 |
| [GLiNER2.5-Decide](https://huggingface.co/fastino/GLiNER2.5-Decide) | 48.8 | 48.0 | 56.2 | 63.5 | 47.0 | 55.5 | 41.6 | 51.5 |
| [GLiFormer-base](https://huggingface.co/knowledgator/gliformer-base-v1) | **56.4** | 62.6 | 67.6 | 71.4 | 67.5 | 56.8 | 40.5 | 60.4 |
| [GLiFormer-large](https://huggingface.co/knowledgator/gliformer-large-v1) | 54.2 | 60.3 | 66.7 | 71.8 | **70.0** | 60.4 | **61.9** | **63.6** |
| [GLiNER large-v2.5](https://huggingface.co/gliner-community/gliner_large-v2.5) | **56.4** | **65.6** | **71.4** | **72.4** | 65.0 | 53.7 | 44.9 | 61.3 |

| Evaluation | Protocol |
| --- | --- |
| Shared harness | Every model is scored by us on the same rows; reproduces the GLiFormer-base card on all seven NER sets and the gliner_large-v2.5 card average within 0.2 |
| NER | CrossNER and MIT; dataset's full label list per sentence, label names only; strict entity-level micro-F1 following GLiNER evaluation |
| Thresholds | GLiNER-family baselines: 0.5 defaults; this model: shipped broad-head threshold 0.5 |
| Relations | Per `(entity, relation type)`, ask “Which spans are the relation of entity?” over the sentence; tail-span micro-F1 on CoNLL04, SciERC, NYT11 and FewRel (one split) |
| Relation baselines | GLiNER-family models receive the same query as an entity label |
| SQuAD v2 | Train split is in the broad-head data; dev F1 is not zero-shot |
| ACL-Verbatim | Held out; paragraph-scale evidence in scientific papers |
| ACL-Verbatim ModernBERT reference | Trained on ACL-Verbatim itself, evidence only |
| Latency | One question per call, approximately 3K-token multi-passage context, mean over 100 questions after five warm-up calls, one A40 GPU for every model |

### Router versus broad head on zero-shot dev

These ablations are on held-out **dev sets**, distinct from the benchmark test results above. Values use the original 0–1 F1 scale.

| Task | Router span head | Broad span head |
| --- | ---: | ---: |
| NER | 0.219 | 0.427 |
| Relations | 0.230 | 0.510 |
| Verbatim evidence | 0.424 | 0.487 |

The broad head was added with the backbone, candidate head and router span head frozen. Router outputs were checked to be bitwise identical on 700 rows; see [training stages](TRAINING.md#training-stages).

# Training: Vela 2.0 9B

[Model card](README.md) · [Usage](USAGE.md) · [Evaluation](EVALUATION.md)

## Training stages

This model starts from [Decision-2.0-Lux-9B](https://huggingface.co/vllm-sr/Decision-2.0-Lux-9B), built on Qwen3.5-9B. Three stages add the Vela routing recipe and span capabilities:

| Stage | Steps | Updated parameters | Tasks and recipe |
| --- | ---: | --- | --- |
| 1. Vela routing recipe | 4,000 | Full fine-tune | Safety, prompt attacks, hallucination and PII spans; domain, modality, fact-check and feedback; general decisions from Decision 1.0 source families in our own wording; synthetic router-style questions in 21 languages |
| 2. Router span head | 3,000 | New word-by-label span head; backbone frozen | PII, hallucination and toxic spans |
| 3. Broad span head | 3,000 | Second span head; everything else frozen | Initialised from router head; 90% open-label extraction steps and 10% replay of stage-2 span data |

Stage 1 replays Decision 2.0 training rows on 7.5% of steps, with a KL term to the base to retain part of its general decisions. Stage 3 leaves the backbone, candidate head and router span head unchanged: router outputs were checked to be bitwise identical to the model without the broad head on 700 rows.

## Data mixtures

| data | sources | share of steps (stage 1) |
|---|---|---|
| safety / attack | AEGIS 2.0, PolyGuardMix, Nemotron-Safety-Guard v3, LLMail-Inject, Salad-Data | 12.2% |
| hallucination spans | LettuceDetect prose + code | 11.3% |
| PII | generated long-document PII, 17 types | 27.8% |
| router tasks | Global-MMLU, Aya, DiffusionDB, WildFeedback, router PII recipe, Presidio replay | 3.8% |
| general decisions | SNLI, BoolQ, ARC, MASSIVE, HelpSteer2, KLUE, JGLUE, SocialIQA, CosmosQA, TyDi QA, OASST1, AfriSenti, Super-NI, SentiMix | 12.5% |
| synthetic router-style decisions | generated with Qwen3-30B-A3B-Instruct-2507, kept only when a blind re-label agrees | 23.1% |
| Decision 2.0 replay | Decision 2.0 training rows (not redistributed) | 7.5% |
| small in-house set | | ~2% |

| data | sources (licence) | share of steps (stage 3) |
|---|---|---|
| NER, open labels | NuNER (MIT), pile-mistral (Apache-2.0), GLiNER multi-task synthetic (Apache-2.0), FiNER-139 (CC-BY-SA-4.0), Re-DocRED (MIT) | 22.5% |
| NER, MultiCoNER v2 | MultiCoNER v2 (CC-BY-4.0) | 9.0% |
| NER, Few-NERD | Few-NERD (CC-BY-SA-4.0) | 6.7% |
| NER, multilingual | Universal NER (CC-BY-SA-4.0) | 6.7% |
| relations (entity-anchored) | GLiNER multi-task synthetic (Apache-2.0), Re-DocRED (MIT), SynthIE (MIT) | 15.8% |
| entity-linking mentions | SynthIE (MIT), Re-DocRED (MIT) | 6.7% |
| RAG / extractive evidence | GLiNER multi-task synthetic (Apache-2.0), SQuAD v2 train (CC-BY-SA-4.0), HotpotQA train (CC-BY-SA-4.0), Natural Questions train (CC-BY-SA-3.0), KRLabsOrg verbatim-spans (RAGBench part) (Apache-2.0, over RAGBench CC-BY-4.0), KRLabsOrg tool-output extraction (Apache-2.0) | 22.5% |
| router span replay | the router span data of stage 2 (PII, hallucination, toxic) | 10.0% |

## Held-out data and provenance

- Broad-head zero-shot dev excludes 16 MultiCoNER / Few-NERD entity types and 79 hashed open labels from training.
- It also holds out Serbian Universal NER, hashed relation types (15% of Wikidata relations), and whole datasets: AskNews-NER, NCBI disease and ACL-Verbatim.
- Data are deduplicated against all benchmark texts: CrossNER, MIT Movie / Restaurant, the four relation sets, SQuAD v2 dev and ACL-Verbatim test. Training and evaluation rows are deduplicated against every test set.
- Entity descriptions for some open labels were written with Qwen2.5-7B-Instruct.
- NuNER, pile-mistral, GLiNER multi-task, SynthIE and verbatim-spans contain LLM-generated labels.

## Release files

| file | what |
|---|---|
| `model-*.safetensors` | backbone + decision heads and the router span head |
| `broad_head.safetensors` | the broad span head |
| `modeling_vela2.py`, `configuration_vela2.py` | `AutoModel` remote code |
| `vela2_inference.py`, `vela2_serve.py` | the engine (SystemOne, `predict()`, shortcuts, span-head dispatch) and an optional HTTP server |
| `calibration.json`, `config.json` | temperatures, thresholds, PII rule, broad-head threshold, optional noul calibration; geometry |
| `PARITY.md` | export parity against the research scorer |

## Licences and modifications

Weights, code and documentation are Apache-2.0. Base-model licences and notices are retained in `LICENSE`, `NOTICE`, `ATTRIBUTIONS.md` and `LICENSES/`; see [MODIFICATIONS.md](MODIFICATIONS.md) for changes against Decision 2.0. Training data retain their own licences, including the CC-BY-SA sources listed above.

