Source: https://huggingface.co/tokimoa/uratori-ja-4b (revision 54700f5d0c8a3124ba8a5827bdcb23f18afc7dd0) — retrieved 2026-10-10

---
license: apache-2.0
language:
- ja
base_model: Qwen/Qwen3.5-4B
library_name: transformers
pipeline_tag: text-classification
datasets:
- tokimoa/uratori-ja-eval
tags:
- japanese
- grounding
- fact-verification
- rag
- decision-model
---

# uratori-ja-4b

uratori-ja-4b is a Japanese decision model. Given a text *state* (for example a source document and a claim) and one or more typed questions, it returns a probability distribution over the allowed answers in a single forward pass, without generating text. Three question types are supported: **noul** (yes/no), **choice** (pick one of 2 to 8 labelled options) and **score** (an ordinal scale with 2 to 10 levels).

It is trained for three jobs: checking whether a claim or an answer is supported by supplied evidence (grounding), comparing two documents (contradictions, meaning-changing edits, added claims) and judging retrieval results and answers in a RAG pipeline (relevance, sufficiency, faithfulness). The request and response format follows TypeSafe's `/v1/systemone` API so the same question definitions can be sent to either. uratori is an independent implementation inspired by TypeSafe's Jev and is not affiliated with TypeSafe.

[uratori-ja-310m](https://huggingface.co/tokimoa/uratori-ja-310m) runs on CPU and [uratori-ja-2b](https://huggingface.co/tokimoa/uratori-ja-2b) needs a smaller GPU; [uratori-ja-9b](https://huggingface.co/tokimoa/uratori-ja-9b) is more accurate and needs a larger one. A Japanese summary is at the end of this card (日本語の説明は末尾にあります).

## Model details

| | |
|---|---|
| Developed by | tokimoa |
| Base model | [Qwen/Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B) (Apache 2.0) |
| Architecture | the text decoder of Qwen3.5-4B (vision tower removed) with a LoRA adapter (rank 32, all linear layers) merged into the weights, plus a 2-layer scoring head read at an added `<opt>` token placed after each option |
| Parameters | 4.21B |
| Precision | bfloat16 (8.4 GB) |
| Maximum input | 4,096 tokens (state, question and options together); longer inputs raise an error instead of being truncated |
| Options | noul: 2 fixed; choice: 2 to 8; score: 2 to 10 levels |
| Calibration | temperature scaling per question type and option count, fitted on the `calibration` split of uratori-ja-eval; applied by default |
| Language | Japanese |
| Version | v1.1 |
| License | Apache 2.0 |
| Code | [github.com/tokimoa/uratori](https://github.com/tokimoa/uratori) (training, evaluation, `/v1/systemone` server) |

## Intended uses and limitations

Intended uses:

- Checking generated answers against the retrieved passages in a RAG system, and routing low-confidence cases to a stronger model or a person
- Detecting contradictions or meaning changes between two versions of a document
- Judging whether retrieved passages are relevant to, and sufficient for, a question
- Any yes/no, multiple-choice or ordinal judgment about Japanese text that can be stated as a question with explicit criteria

Out of scope:

- Generating or rewriting text
- Checking claims against world knowledge: the model only compares the claim with the text you supply
- Fully automated decisions with legal, financial or safety consequences; use the probability as a signal and keep a person in the loop
- Languages other than Japanese, images, and inputs longer than 4,096 tokens

## How to use

```bash
pip install torch "transformers>=5.18"
```

```python
from transformers import AutoModel, AutoTokenizer

repo = "tokimoa/uratori-ja-4b"
tokenizer = AutoTokenizer.from_pretrained(repo, trust_remote_code=True)
model = AutoModel.from_pretrained(repo, trust_remote_code=True).to("cuda").eval()

state = {
    "根拠": "返品は商品到着後14日以内に限り受け付けます。開封済みの商品は返品できません。",
    "主張": "開封済みの商品でも、到着から7日以内なら返品できる。",
}
questions = {
    "support": {
        "type": "choice",
        "instructions": "`主張` は `根拠` から支持されるか",
        "criteria": {
            "支持": "根拠だけから主張の全体が成り立つ。",
            "矛盾": "根拠と両立しない部分がある。",
            "情報不足": "矛盾はないが、根拠からは成否を決められない部分がある。",
        },
    },
    "contradict": {
        "type": "noul",
        "instructions": "`主張` は `根拠` と矛盾するか",
        "criteria": {"true": "根拠と両立しない部分がある。", "false": "両立しない部分はない。"},
    },
}
answers = model.predict(tokenizer, state, questions)
print(answers["support"]["choice"], answers["support"]["probabilities"])
# 矛盾 {'支持': 0.0, '矛盾': 1.0, '情報不足': 0.0}
print(answers["contradict"]["noul"])
# 0.95
```

The model code is included in this repository, so `trust_remote_code=True` is required. Needs a GPU with about 12 GB of memory. About 100 ms per question on an RTX 5090 (batch 8).

Input format:

| Field | Description |
|---|---|
| `state` | A string, or a dict of named texts. Keys of the dict can be referenced from `instructions` as `` `key` ``. |
| `questions` | A dict from your own question ids to question objects. Questions in one call share the state and are judged independently. |
| `type: "noul"` | `criteria` is optional: `{"true": "...", "false": "..."}`. Returns `noul`, the probability of yes. |
| `type: "choice"` | `criteria` maps each option label to its description (2 to 8 options). Returns `choice`, `probabilities` and `confidence`. |
| `type: "score"` | `criteria` is a list of level descriptions from lowest to highest (2 to 10 levels). Returns `score` (expected level), `probabilities`, `legend` and `confidence`. |

Probabilities are temperature-scaled by default; pass `calibrate=False` to `predict` for the raw softmax. `confidence` follows the formulas published for the TypeSafe API and measures how peaked the distribution is, not the probability of being right. Writing explicit criteria for noul questions is recommended; the model was trained mostly with them.

A `/v1/systemone`-compatible HTTP server that loads this model is in the [GitHub repository](https://github.com/tokimoa/uratori): `python -m uratori.serve.app --model tokimoa/uratori-ja-4b --device cuda`.

### MLX (Apple silicon)

Quantised MLX versions with a runner that needs only `mlx-lm`: [uratori-ja-4b-mlx-8bit](https://huggingface.co/tokimoa/uratori-ja-4b-mlx-8bit) (same accuracy as this model on the evaluation set) and [uratori-ja-4b-mlx-4bit](https://huggingface.co/tokimoa/uratori-ja-4b-mlx-4bit) (about 1 point lower, half the size).

### 4-bit loading (smaller GPU)

With [bitsandbytes](https://github.com/bitsandbytes-foundation/bitsandbytes) installed, the backbone can be loaded in NF4 so the model fits in about 3.5 GB of GPU memory. Measured on v1, accuracy on the evaluation set was 0.864 on test and 0.850 on challenge, within noise of the bfloat16 numbers. Keep the scoring head in full precision:

```python
from transformers import AutoModel, BitsAndBytesConfig
import torch

quant = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16,
                           bnb_4bit_use_double_quant=True, llm_int8_skip_modules=["head"])
model = AutoModel.from_pretrained("tokimoa/uratori-ja-4b", trust_remote_code=True,
                                  quantization_config=quant, device_map={"": "cuda"}).eval()
```

## Evaluation

All numbers are measured on [tokimoa/uratori-ja-eval](https://huggingface.co/datasets/tokimoa/uratori-ja-eval) with the weights published here, one question per call. The `test` split has 802 items and the `challenge` split has 300 harder items (prompt-injection attempts in the text, unusual registers, unseen question templates, longer documents). Labels are the majority vote of the draft's intended answer and three LLM judges (DeepSeek V4.1 Flash, Gemini 3.8 Flash, GPT-6 Luna), not human annotations; items where the four disagreed are kept and flagged (96 of 802 in test). Confidence intervals are 95% bootstrap intervals resampled by document family.

| Split | Items | Accuracy | 95% CI | Macro F1 | ECE | Brier |
|---|---|---|---|---|---|---|
| test | 802 | 0.872 | 0.852 to 0.892 | 0.863 | 0.032 | 0.195 |
| challenge | 300 | 0.870 | 0.831 to 0.905 | 0.867 | 0.043 | 0.198 |

Comparison on the same splits (accuracy):

| Model | Parameters | test (802) | challenge (300) |
|---|---|---|---|
| Jev 1.13.0 (TypeSafe API, measured 2026-10-05) | undisclosed | 0.903 | 0.900 |
| [uratori-ja-9b](https://huggingface.co/tokimoa/uratori-ja-9b) | 8.0B | 0.897 | 0.913 |
| **uratori-ja-4b** (this model) | 4.2B | 0.872 | 0.870 |
| [uratori-ja-2b](https://huggingface.co/tokimoa/uratori-ja-2b) | 1.9B | 0.781 | 0.797 |
| [uratori-ja-310m](https://huggingface.co/tokimoa/uratori-ja-310m) | 0.31B | 0.686 | 0.693 |
| Most frequent label per question type and option count | | 0.446 | 0.430 |
| Random | | 0.387 | 0.379 |

Breakdown on `test` (accuracy):

| By question type | noul | choice | score |
|---|---|---|---|
| | 0.906 | 0.834 | 0.884 |

| By task | grounding | comparison | RAG | writing requirements |
|---|---|---|---|---|
| | 0.873 | 0.891 | 0.848 | 0.859 |

| By labelled difficulty | clear | hard | ambiguous |
|---|---|---|---|
| | 0.921 | 0.891 | 0.717 |

Accuracy on minimal pairs (two items that differ in one detail and have different answers; both must be right): 0.730 on test.

Selective accuracy, keeping only the items whose top probability is highest:

| Items kept | top 30% | top 50% | top 70% | all |
|---|---|---|---|---|
| test | 0.983 | 0.973 | 0.952 | 0.872 |
| challenge | 1.000 | 0.980 | 0.957 | 0.870 |

### Long documents and passage selection (v1.1)

Two additional synthetic sets, labelled by the same three-judge vote as the main evaluation set, measured with this model's training-time predictions (not the published weights). Items on which the judges disagreed are included.

| Set | Items | Input length | This model | v1 | Jev 1.13.0 |
|---|---|---|---|---|---|
| Long documents | 128 | 3,000 to 6,000 tokens | 0.930 | 0.946 | 0.962 |
| Passage selection (4 options incl. "none") | 179 | about 600 tokens | 0.944 | 0.816 | 0.726 |

The long-document items are easier than the main set (all models score above 0.9); the point of the set is that accuracy does not fall with length. On passage selection the gain comes from the "none of the passages" items, which v1 and Jev mostly miss.

## Training

### Data

1. **Stage 1**: [JNLI](https://github.com/yahoojapan/JGLUE) (CC BY-SA 4.0) converted to the decision format: each premise/hypothesis pair becomes a support/contradict/neutral choice question or a yes/no question.
2. **Stage 2**: 49,668 synthetic items (state, question, answer) generated with DeepSeek V4.1 Flash, whose terms permit using outputs for training. Source documents are fictional business documents written by the generator, Japanese government FAQs ([JaGovFaqs-22k](https://huggingface.co/datasets/matsuxr/JaGovFaqs-22k), CC BY 4.0) and Japanese Wikipedia paragraphs (CC BY-SA 4.0). Questions come from 29 fixed templates (grounding, comparison, RAG, writing, routing) and from open questions the generator wrote itself; about 17,000 items form minimal pairs. The evaluation documents were never used for training. Five question templates used in the evaluation set were held out from training.
3. **Stage 3 (v1.1)**: 3,440 items whose documents are 3,000 to 6,000 tokens long and 3,000 items of a new question type, 「`回答` の根拠になっている段落は `段落1`、`段落2`、`段落3` のどれか」 (which passage, if any, supports the answer), both generated the same way as stage 2. 10,000 items from the stage 2 data were mixed in so the model does not drift from v1. A first attempt with lr 3e-5 lost 2 points on challenge; lr 1e-5 kept the v1 accuracy.

### Procedure

| Stage | Setting |
|---|---|
| 1 | JNLI converted to decision format, 19,816 items, 2 epochs, 256 tokens, batch 8 x 4 accumulation, lr 2e-4 (head 1e-3) |
| 2 | 49,668 synthetic items, 1 epoch, 1,280 tokens, batch 1 x 16 accumulation, lr 1e-4 (head 5e-4) |
| 3 | 16,281 items (6,440 new items plus 10,000 sampled from the stage 2 data; 159 skipped as too long), 1 epoch, 6,144 tokens (batches capped at 6,144 tokens in total), batch 4 x 4 accumulation, lr 1e-5 (head 1e-5), started from the v1 weights |

LoRA rank 32, alpha 64, dropout 0.05 on all linear layers; the embedding row of the added `<opt>` token and the head are trained in full. The adapter is merged into the base weights for release; merging changed 1 answer on the 300 challenge items.

The loss is cross-entropy over the options of each question, normalised per question type within a batch. Temperatures for calibration were fitted afterwards on the 600-item `calibration` split.

### Compute

One RTX 5090 (32 GB) for stages 1 and 2: stage 1 about 50 minutes, stage 2 about 4.4 hours. Stage 3 about 30 minutes on an RTX PRO 6000 Blackwell (96 GB).

## Limitations

- Accuracy is 0.872 on test; the model is wrong on roughly one item in 8. Use the probability to route uncertain items rather than acting on every answer.
- It is weaker on question templates it has not seen in training, on items our judges found ambiguous (0.717 on test), and on relative dates, numeric conditions and scope-limiting words such as 「原則として」.
- The evaluation inputs are at most about 750 tokens (median about 220). v1.1 was trained with inputs up to 6,144 tokens and accepts up to 4,096. On 128 synthetic items of 3,000 to 6,000 tokens it scored 0.93 (Jev 1.13.0: 0.96 on the same items); accuracy on long real documents has not been measured.
- Labels in the evaluation set are LLM majority votes. Where the judges disagreed, the model's accuracy is much lower and the labels themselves are uncertain.
- Each model was trained once (one seed). Run-to-run variance has not been measured for this model.
- Japanese only. Other languages, images and knowledge-based fact checking are out of scope.

## Bias, risks and ethical considerations

The training data is synthetic text about fictional organisations, plus public NLI and FAQ data; it does not cover every domain, register or document type, and the model may be systematically less accurate on text unlike its training data. Probabilities are calibrated on one evaluation set and should be re-checked on your own data before thresholds are used operationally. Do not use the output as the sole basis for decisions that affect people.

## Changelog

- **v1.1 (2026-10-07)**: continued training on 6,440 new items (documents of 3,000 to 6,000 tokens, and a new question type that asks which of several passages supports an answer) mixed with 10,000 items from the original data. test 0.867 → 0.872, challenge 0.863 → 0.870; passage selection 0.82 → 0.94. Input limit raised to 4,096 tokens.
- **v1 (2026-10-06)**: first release. test 0.867, challenge 0.863.

## License

Apache License 2.0. The base model Qwen/Qwen3.5-4B is distributed under the Apache 2.0 license; its notice is included in `NOTICE`.

## Citation

```bibtex
@misc{uratori2026,
  title  = {uratori: Japanese decision models for grounding checks, document comparison and RAG judgments},
  author = {tokimoa},
  year   = {2026},
  url    = {https://github.com/tokimoa/uratori}
}
```

## Contact

Open an issue at [github.com/tokimoa/uratori](https://github.com/tokimoa/uratori/issues).

## 日本語

uratori-ja-4b は、日本語の文章と質問を受け取り、文章を生成せずに答えの確率分布を 1 回の forward で返すモデルです。質問の型は、真偽（noul）、選択（choice、2〜8 択）、段階評価（score、2〜10 段階）の 3 つです。与えた根拠から主張や回答が支持されるかの検証、2 つの文書の比較（矛盾、意味の変更、追加された主張）、RAG の判断（検索結果の関連性と十分性、回答の忠実性）を対象に学習しています。入出力の形は TypeSafe の `/v1/systemone` API と同じにしてあります。TypeSafe の Jev に着想を得た独立の実装で、TypeSafe とは関係がありません。

CPU で動く [uratori-ja-310m](https://huggingface.co/tokimoa/uratori-ja-310m)、より小さい GPU で動く [uratori-ja-2b](https://huggingface.co/tokimoa/uratori-ja-2b)、より精度の高い [uratori-ja-9b](https://huggingface.co/tokimoa/uratori-ja-9b) があります。

使い方は上のコードのとおりです（`trust_remote_code=True` が必要です）。`state` は文字列か、名前つきの文章の dict で、dict のキーは質問文から `` `キー名` `` で参照できます。1 回の呼び出しに質問をいくつでも入れられ、質問どうしは独立に判定されます。確率は温度で校正した値です（`calibrate=False` で校正前の値）。入力が 4,096 トークンを超えると、切り詰めずにエラーになります。noul の criteria は省略できますが、はいといいえの条件を書いたほうが安定します。GPU が必要です（メモリ 12 GB 程度）。RTX 5090 で 1 問 100 ms 前後です。

評価は [uratori-ja-eval](https://huggingface.co/datasets/tokimoa/uratori-ja-eval) の test（802 問）と challenge（300 問）で、公開した重みそのもので測りました。正解は人が付けたものではなく、下書きの想定と 3 つの LLM の判定の多数決です。test の Accuracy は 0.872、challenge は 0.870。本家の Jev 1.13.0 は同じ問題で 0.903 と 0.900 です。

制限。判定は入力に与えた文章だけに基づき、モデルの知識で事実かどうかを確かめる用途には使えません。単独で結論を出す精度ではなく、確信度の低い件を LLM や人に回す前段として使うことを想定しています。学習で見ていない種類の質問、判定者が割れるような曖昧な問題、相対的な日付や数値の条件、「原則として」のような範囲を限定する語には弱いです。約 750 トークンを超える入力での挙動は測っていません。日本語専用です。

