Source: https://huggingface.co/LiquidAI/d1-3B/blob/051bcc464b01b9f92942b364d9586b0ef5912432/prompt.py and .../runner.py (repository code, verbatim) — retrieved 2026-10-10

## prompt.py
```python
"""The prompt and the readout. A System One decision is a single forward pass that stops at the answer
slot: everything the model sees is built here, and the answer is a softmax over its options' tokens.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Mapping, Sequence

# The system turn: none by default.
SYSTEMS: dict[str, str | None] = {
    "none": None,
    "isolated": (
        "You are a System One decision model. Answer only the current isolated "
        "question from the shared state. Other questions do not exist."
    ),
}
DEFAULT_SYSTEM = "none"

IM_START = "<|im_start|>"
IM_END = "<|im_end|>"


# --------------------------------------------------------------------------- #
# question types
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class Choice:
    instructions: str
    criteria: Mapping[str, str | None]
    type: str = "choice"


@dataclass(frozen=True)
class Noul:
    instructions: str
    criteria: Mapping[str, Any] | None = None
    type: str = "noul"


@dataclass(frozen=True)
class Score:
    instructions: str
    criteria: Sequence[str]
    type: str = "score"


Question = Choice | Noul | Score


# --------------------------------------------------------------------------- #
# verbalizer
# --------------------------------------------------------------------------- #


def option_codes(labels: Sequence[str]) -> list[str]:
    """Native letters when the labels already are letters, else A..Z, else 00..; one rule for every
    cardinality."""
    labs = [str(x).strip() for x in labels]
    if labs and all(len(k) == 1 and k.isalpha() for k in labs):
        return labs
    if len(labs) <= 26:
        return [chr(ord("A") + i) for i in range(len(labs))]
    return [f"{i:02d}" for i in range(len(labs))]


_FALLBACK_POOL = (
    [chr(c) for c in range(ord("A"), ord("Z") + 1)]
    + [f"{i:02d}" for i in range(100)]
    + [chr(c) for c in range(ord("a"), ord("z") + 1)]
    + [f"#{i}" for i in range(200)]
    # Where a tokenizer splits digits, "00".."99" and "#i" are two tokens, and two capital letters are
    # often one. Last in the pool, so a tokenizer with digit pairs never reaches it.
    + [chr(a) + chr(b) for a in range(ord("A"), ord("Z") + 1) for b in range(ord("A"), ord("Z") + 1)]
)


@lru_cache(maxsize=4096)
def _aliases_cached(tokenizer_key: int, codes: tuple[str, ...]) -> tuple[tuple[str, int], ...]:
    tokenizer = _TOKENIZERS[tokenizer_key]
    used: set[int] = set()
    out: list[tuple[str, int]] = []

    def take(raw: str) -> bool:
        enc = tokenizer.encode(raw, add_special_tokens=False)
        if len(enc) != 1 or enc[0] in used:
            return False
        out.append((raw, enc[0]))
        used.add(enc[0])
        return True

    for code in codes:
        if take(code):
            continue
        if not any(take(raw) for raw in _FALLBACK_POOL):
            raise RuntimeError(f"no single-token alias left for {len(codes)} options")
    return tuple(out)


_TOKENIZERS: dict[int, object] = {}


def aliases(tokenizer, labels: Sequence[str]) -> list[tuple[str, int]]:
    """Assign every label a distinct single-token code: [(code, token_id)].

    Memoised on the codes rather than on the labels: the codes are positional
    unless the labels are already letters, so every option list of one length
    shares an entry.
    """
    _TOKENIZERS.setdefault(id(tokenizer), tokenizer)
    codes = tuple(option_codes(labels))
    return list(_aliases_cached(id(tokenizer), codes))


@lru_cache(maxsize=8192)
def _ids_cached(tokenizer_key: int, texts: tuple[str, ...]) -> tuple[int, ...]:
    tokenizer = _TOKENIZERS[tokenizer_key]
    out, seen = [], set()
    for t in texts:
        enc = tokenizer.encode(t, add_special_tokens=False)
        if len(enc) == 1 and enc[0] not in seen:
            out.append(enc[0])
            seen.add(enc[0])
    return tuple(out)


def _ids(tokenizer, texts: Sequence[str]) -> list[int]:
    _TOKENIZERS.setdefault(id(tokenizer), tokenizer)
    return list(_ids_cached(id(tokenizer), tuple(texts)))


def as_question(q: Mapping | Question) -> Question:
    """A question in the Decision Index's JSON, `{"type": "noul" | "choice" | "score", "instructions",
    "criteria"}`, as one of the classes above; a class passes through."""
    if not isinstance(q, Mapping):
        return q
    kind = q.get("type", "choice")
    if kind == "noul":
        return Noul(q["instructions"], q.get("criteria"))
    if kind == "score":
        return Score(q["instructions"], list(q["criteria"]))
    return Choice(q["instructions"], q["criteria"])


YES_FORMS = ("yes", "Yes", "YES")
NO_FORMS = ("no", "No", "NO")


def readout_ids(tokenizer, q: Question) -> list[list[int]]:
    """Token ids to score, one group per option, max-pooled: the answer is a softmax over these and
    nothing else."""
    if isinstance(q, Noul):
        yes, no = _ids(tokenizer, YES_FORMS), _ids(tokenizer, NO_FORMS)
        if not yes or not no:
            raise RuntimeError("tokenizer has no single-token yes/no")
        return [yes, no]
    if isinstance(q, Score):
        groups = [_ids(tokenizer, [str(i)]) for i in range(len(q.criteria))]
        if any(not g for g in groups):
            raise RuntimeError(
                f"score with {len(q.criteria)} levels needs single-token digits; "
                "the primitive is defined for 2 to 10"
            )
        return groups
    groups = []
    for code, tid in aliases(tokenizer, list(q.criteria.keys())):
        extra = _ids(tokenizer, [f" {code}"])
        groups.append([tid] + [i for i in extra if i != tid])
    if not groups:
        raise RuntimeError("choice with no options")
    return groups


def readout(tokenizer, q: Question, logz, calibration=None) -> list[float]:
    """Option probabilities from the log-probabilities at the answer slot.

    `logz` is indexed by token id: a vocabulary tensor, or a dict holding at
    least the question's option tokens. Each option scores its best form.
    """
    scores = [max(float(logz[i]) for i in g) for g in readout_ids(tokenizer, q)]
    if calibration is not None:
        scores = calibration.apply(q, scores)
    m = max(scores)
    exps = [math.exp(s - m) for s in scores]
    return [e / sum(exps) for e in exps]


# --------------------------------------------------------------------------- #
# state and question rendering
# --------------------------------------------------------------------------- #


DEFAULT_MODEL = "LiquidAI/LFM2.5-VL-3B"

# How a state is rendered: `json_only`, the default, writes every state as the object it is; `json` keeps
# three shortcuts (`Message:`, `Passage:` / `Asked:`, a lone question's text); `sections` writes nested
# states as labelled blocks.
DEFAULT_STATE_STYLE = "json_only"


def _is_scalar(v: Any) -> bool:
    return v is None or isinstance(v, (str, int, float, bool)) and "\n" not in str(v)


def _sections(obj: Any, path: str, out: list[str]) -> None:  # noqa: C901
    """Flatten a nested state into labelled blocks, keeping real newlines.

    `json.dumps` escapes every newline inside a log line or a record, so a
    multi-line record would arrive as one string of `\n`; this keeps it readable.
    """
    head = f"[{path}]\n" if path else ""
    if isinstance(obj, dict):
        scalars = [(k, v) for k, v in obj.items() if _is_scalar(v)]
        rest = [(k, v) for k, v in obj.items() if not _is_scalar(v)]
        if scalars:
            body = "\n".join(f"{k}: {'' if v is None else v}" for k, v in scalars)
            out.append(f"{head}{body}")
        for k, v in rest:
            _sections(v, f"{path}.{k}" if path else str(k), out)
        return
    if isinstance(obj, (list, tuple)):
        if obj and all(_is_scalar(v) for v in obj):
            body = "\n".join(f"- {'' if v is None else v}" for v in obj)
            out.append(f"{head}{body}")
            return
        for i, v in enumerate(obj, start=1):
            _sections(v, f"{path} {i}/{len(obj)}" if path else f"{i}/{len(obj)}", out)
        return
    out.append(f"{head}{'' if obj is None else obj}")


def render_state(state: Any) -> str:
    if isinstance(state, str):
        return state
    out: list[str] = []
    _sections(state, "", out)
    return "\n\n".join(out)


def state_block(state: Any, style: str = DEFAULT_STATE_STYLE) -> str:
    """Flatten a state into the block that precedes QUESTION:.

    Without `_only`, three shapes get a shortcut: a bare utterance becomes
    `Message:`, a passage and a question `Passage:` / `Asked:`, a lone question
    its text. The `_only` styles (the default) render every state as the object
    it is.
    """
    if isinstance(state, dict) and not style.endswith("_only"):
        keys = set(state.keys())
        if keys == {"text"}:
            return f"Message: {state['text']}\n\n"
        if {"passage", "question"} <= keys and len(keys) == 2:
            return f"Passage: {state['passage']}\n\nAsked: {state['question']}\n\n"
        if keys == {"question"}:
            return f"{state['question']}\n\n"
    if style.startswith("json"):
        if isinstance(state, str):
            return f"{state}\n\n"
        return json.dumps(state, ensure_ascii=False, indent=2) + "\n\n"
    return f"{render_state(state)}\n\n"


_PLACEHOLDER = re.compile(r"^opt\d+$")


def _option_line(code: str, label: str, desc: str | None, style: str) -> str:
    text = desc or label.replace("_", " ")
    if style == "name_desc" and not _PLACEHOLDER.match(label) and label != text:
        return f"{code} {label}: {text}"
    return f"{code} {text}"


def question_block(tokenizer, q: Question, option_style: str = "desc") -> str:
    if isinstance(q, Choice):
        labels = list(q.criteria.keys())
        codes = aliases(tokenizer, labels)
        lines = "\n".join(
            _option_line(codes[i][0], lab, q.criteria[lab], option_style)
            for i, lab in enumerate(labels)
        )
        return (
            f"{q.instructions}\n\nOptions:\n{lines}\n\n"
            "Reply with the option code only."
        )
    if isinstance(q, Noul):
        extra = ""
        if q.criteria:
            extra = f"\nYes: {q.criteria.get('true')}\nNo: {q.criteria.get('false')}"
        return f"{q.instructions}{extra}\n\nReply with yes or no only."
    if isinstance(q, Score):
        legend = "\n".join(f"{i} {name}" for i, name in enumerate(q.criteria))
        return (
            f"{q.instructions}\n\n{legend}\n\n"
            f"Reply with a single digit 0-{len(q.criteria) - 1} only."
        )
    raise TypeError(f"unknown question type {type(q)}")


def prefix_text(
    tokenizer,
    state: Any,
    bos: str = "",
    style: str = DEFAULT_STATE_STYLE,
    system: str = DEFAULT_SYSTEM,
    images: str = "",
) -> str:
    """Everything before the question, shared by all questions on one state: the pictures' markup
    (`images`, as the chat template writes them) at the head of the user turn, then the state. With no
    state (`None`) the question follows the pictures directly."""
    text = SYSTEMS[system]
    turn = "" if text is None else f"{IM_START}system\n{text}{IM_END}\n"
    body = "" if state is None else f"{state_block(state, style)}\nQUESTION:\n"
    return f"{bos}{turn}{IM_START}user\n{images}{body}"


# What sits between the assistant header and the answer slot, per model type: nothing on LFM2-VL, whose
# template opens no reasoning block.
DEFAULT_LEAD = ""
LEADS: dict[str, str] = {}


def default_lead(model_type: str | None) -> str:
    """What a checkpoint's own template writes before a non-thinking answer."""
    return LEADS.get(model_type, DEFAULT_LEAD)


def suffix_text(
    tokenizer, q: Question, lead: str = DEFAULT_LEAD, option_style: str = "desc"
) -> str:
    """The question and the assistant header, up to the answer slot."""
    body = question_block(tokenizer, q, option_style)
    return f"{body}{IM_END}\n{IM_START}assistant\n{lead}"


def render(
    tokenizer,
    state: Any,
    q: Question,
    bos: str = "",
    lead: str = DEFAULT_LEAD,
    style: str = DEFAULT_STATE_STYLE,
    system: str = DEFAULT_SYSTEM,
    option_style: str = "desc",
    images: str = "",
) -> str:
    return prefix_text(tokenizer, state, bos, style, system, images) + suffix_text(
        tokenizer, q, lead, option_style
    )
```

## runner.py
```python
"""One-pass typed decisions on a causal LFM backbone.

The model sees the state and the question once, and the answer is read off the
logits at the answer slot. Nothing is decoded, so a schema violation is
impossible and `tokens generated per decision` is zero.
"""

from __future__ import annotations

import math
from typing import Any, Sequence

import torch

from .api import SystemOneApi
from .lfm2_vl import Lfm2ForCausalLM, Lfm2VlForConditionalGeneration
from .prompt import (
    DEFAULT_MODEL,
    DEFAULT_STATE_STYLE,
    DEFAULT_SYSTEM,
    IM_START,
    Question,
    default_lead,
    prefix_text,
    readout,
    render,
    suffix_text,
)

# Every picture is bounded at this many pixels before the processor.
VISION_MAX_PIXELS = 1024 * 1024


# LFM2 models run on the hybrid stack (`hybrid.py`); any other model type through transformers as it is.
MODELS = {
    "lfm2_vl": Lfm2VlForConditionalGeneration,
    "lfm2": Lfm2ForCausalLM,
}


def load_backbone(model_id: str = DEFAULT_MODEL, dtype=torch.bfloat16):
    """The checkpoint and its tokenizer, with SDPA attention."""
    from transformers import AutoModelForImageTextToText, AutoTokenizer, PretrainedConfig

    tok = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    kind = PretrainedConfig.get_config_dict(model_id)[0].get("model_type")
    cls = MODELS.get(kind, AutoModelForImageTextToText)
    return cls.from_pretrained(model_id, dtype=dtype, attn_implementation="sdpa"), tok


def cap_pixels(image, max_pixels: int = VISION_MAX_PIXELS):
    """A picture downscaled to at most `max_pixels`, bicubic."""
    image = image.convert("RGB") if hasattr(image, "convert") else image
    w, h = image.size
    if w * h <= max_pixels:
        return image
    try:
        from PIL import Image
    except ImportError as e:  # optional for text
        raise ImportError("resizing a picture needs Pillow") from e

    scale = math.sqrt(max_pixels / (w * h))
    return image.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.Resampling.BICUBIC)


class SystemOne(SystemOneApi):
    """State in, calibrated distribution out, one forward pass."""

    def __init__(
        self,
        model_id: str = DEFAULT_MODEL,
        device: str | None = None,
        calibration=None,
        lead: str | None = None,
        state_style: str = DEFAULT_STATE_STYLE,
        system: str = DEFAULT_SYSTEM,
        option_style: str = "desc",
        compile: bool = False,
        token_budget: int = 65536,
        model=None,
        tokenizer=None,
    ):
        """`model` and `tokenizer`, when given, are a backbone already loaded (`D1Model` passes itself);
        it stays on its device unless `device` says otherwise."""
        if model is None:
            model, tokenizer = load_backbone(model_id)
        else:
            model_id, device = model.config._name_or_path, device or next(model.parameters()).device
        self.model, self.tokenizer = model, tokenizer
        self.model_id = model_id
        if lead is None:
            lead = default_lead(self.model.config.model_type)
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        self.model.to(self.device).eval()
        bos = getattr(self.tokenizer, "bos_token", None)
        self.bos = bos if isinstance(bos, str) else ""
        self.calibration = calibration
        self.lead = lead
        self.state_style = state_style
        self.system = system
        self.option_style = option_style
        self.token_budget = token_budget
        self.processor = None
        # CUDA graphs for single questions on NVIDIA, where eager time is mostly kernel launches.
        if compile and torch.version.hip:
            raise ValueError("compile=True needs CUDA: on ROCm the CUDA graphs fault after a few dozen calls")
        self._one_pass = (torch.compile(self.model.forward, mode="reduce-overhead")
                          if compile else self.model)

    # ---------------------------------------------------------------- prompt

    def render(self, state: Any, q: Question) -> str:
        return render(
            self.tokenizer, state, q, self.bos, self.lead, self.state_style,
            self.system, self.option_style,
        )

    # --------------------------------------------------------------- forward

    def _logz_ids(self, rows: list[list[int]]) -> list[torch.Tensor]:
        """Log-softmax at the answer slot, one row per token list, in one pass.

        The rows are one tree (`hybrid.py`): their common start is its trunk and
        is read once; the rest of each row is a branch, packed with no padding.
        Mathematically each row alone; in bf16 the kernels differ by batch shape.
        """
        if len(rows) == 1:  # nothing to share: a plain chain is faster than a tree of one
            row = self._one_pass(input_ids=torch.tensor(rows, device=self.device), logits_to_keep=1).logits[0, -1]
            return [row.float() - torch.logsumexp(row.float(), dim=-1)]
        shared = 0  # every row keeps at least its last token
        while shared < min(map(len, rows)) - 1 and len({r[shared] for r in rows}) == 1:
            shared += 1
        return self._tree_logz(rows[0][:shared], [r[shared:] for r in rows])

    def _tree_logz(self, trunk: list[int], rows: list[list[int]], **vision) -> list[torch.Tensor]:
        """`trunk` then each of `rows`, read at each row's end."""
        packed = torch.tensor([t for r in rows for t in r], device=self.device)
        lengths = torch.tensor([len(r) for r in rows], device=self.device)
        trunk = torch.tensor([trunk], dtype=torch.long, device=self.device)
        logits = self.model.answer(trunk, packed, lengths, **vision).float()
        return list(logits - torch.logsumexp(logits, dim=-1, keepdim=True))

    def plan_batches(self, texts: Sequence[str], token_budget: int | None = None) -> list[list[int]]:
        """Consecutive batches of at most `token_budget` tokens: rows are packed,
        so a batch costs its real tokens."""
        return self._plan([len(self.tokenizer.encode(t, add_special_tokens=False)) for t in texts], token_budget)

    def _plan(self, lengths: Sequence[int], token_budget: int | None = None) -> list[list[int]]:
        if not lengths:
            return []
        budget = token_budget or self.token_budget
        out: list[list[int]] = [[]]
        used = 0
        for i, n in enumerate(lengths):
            if out[-1] and used + n > budget:
                out.append([])
                used = 0
            out[-1].append(i)
            used += n
        return out

    # --------------------------------------------------------------- readout

    def _readout(self, q: Question, logz: torch.Tensor) -> list[float]:
        return readout(self.tokenizer, q, logz, self.calibration)

    # ------------------------------------------------------------------- api

    @torch.inference_mode()
    def run(self, requests: Sequence[tuple[Any, list[Question], Sequence]]) -> list[tuple[list[list[float]], int]]:
        """Each `(state, questions, images)` request's probabilities and the tokens it read. Requests of one
        question and no pictures are packed together, one tree per token budget; any other request is its
        own pass, its state (and pictures) the trunk and its questions the branches."""
        out: list = [None] * len(requests)
        single = [i for i, (_, qs, images) in enumerate(requests) if len(qs) == 1 and not images]
        rows = [self.tokenizer.encode(self.render(requests[i][0], requests[i][1][0]), add_special_tokens=False)
                for i in single]
        for chunk in self._plan([len(r) for r in rows]):
            for j, z in zip(chunk, self._logz_ids([rows[j] for j in chunk])):
                out[single[j]] = ([self._readout(requests[single[j]][1][0], z)], len(rows[j]))
        for i, (state, qs, images) in enumerate(requests):
            if out[i] is None:
                out[i] = self._request(state, qs, images)
        return out

    def _request(self, state: Any, qs: list[Question], images: Sequence) -> tuple[list[list[float]], int]:
        pics = [cap_pixels(im) for im in images]
        prefix = prefix_text(self.tokenizer, state, self.bos, self.state_style, self.system,
                             self._image_markup(len(pics)) if pics else "")
        suffixes = [suffix_text(self.tokenizer, q, self.lead, self.option_style) for q in qs]
        vision: dict = {}
        if not pics:
            trunk = self.tokenizer.encode(prefix, add_special_tokens=False)
        elif len(qs) == 1:  # the whole prompt in one plain pass
            inputs = self._image_inputs(prefix + suffixes[0], pics)
            row = self._one_pass(**inputs, logits_to_keep=1).logits[0, -1].float()
            return [self._readout(qs[0], row - torch.logsumexp(row, dim=-1))], int(inputs["input_ids"].shape[1])
        else:
            vision = self._image_inputs(prefix, pics)
            trunk = vision.pop("input_ids")[0].tolist()
            vision.pop("attention_mask", None)
        branches = [self.tokenizer.encode(s, add_special_tokens=False) for s in suffixes]
        probs: list[list[float]] = []
        for chunk in self._plan([len(b) for b in branches]):
            zs = self._tree_logz(trunk, [branches[j] for j in chunk], **vision)
            probs += [self._readout(qs[j], z) for j, z in zip(chunk, zs)]
        return probs, len(trunk) + sum(map(len, branches))

    def tokens(self, state: Any, questions: Sequence[Question]) -> int:
        """The longest prompt one of `questions` makes over a text state: its state's tokens and its own."""
        prefix = prefix_text(self.tokenizer, state, self.bos, self.state_style, self.system)
        return len(self.tokenizer.encode(prefix, add_special_tokens=False)) + max(
            len(self.tokenizer.encode(suffix_text(self.tokenizer, q, self.lead, self.option_style),
                                      add_special_tokens=False)) for q in questions)

    # ---------------------------------------------------------------- vision

    def _image_markup(self, n: int) -> str:
        """What the chat template writes for `n` images at the head of a user turn (`<image>` each on LFM2-VL)."""
        if self.processor is None:
            self.processor = self._load_processor()
        msgs = [{"role": "user", "content": [*([{"type": "image"}] * n), {"type": "text", "text": "\x00"}]}]
        text = self.processor.apply_chat_template(msgs, add_generation_prompt=False, tokenize=False)
        head = f"{IM_START}user\n"
        return text[text.index(head) + len(head):text.index("\x00")]

    def _load_processor(self):
        from transformers import AutoProcessor

        return AutoProcessor.from_pretrained(self.model.config._name_or_path, trust_remote_code=True)

    def _image_inputs(self, text: str, images: Sequence) -> dict:
        """Token ids and pixel inputs for one prompt holding `images`; the prompt carries its own BOS."""
        inputs = self.processor(text=[text], images=[list(images)], return_tensors="pt", add_special_tokens=False)
        if "pixel_attention_mask" in inputs:
            # LFM2-VL's processor pads every image to 1024 patches and the tower
            # masks the padding out; cutting it gives the same answer for up to
            # half the work.
            n = int(inputs["pixel_attention_mask"].sum(1).max())
            inputs["pixel_values"] = inputs["pixel_values"][:, :n]
            inputs["pixel_attention_mask"] = inputs["pixel_attention_mask"][:, :n]
        return {k: (v.to(self.device) if hasattr(v, "to") else v) for k, v in inputs.items()}
```
