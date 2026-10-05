"""TypeSafe/Jev-compatible wire format (`POST /v1/systemone`, `GET /v1/models`), the same contract Rizzo-Flow serves.

A client written for the hosted Jev API (or for Rizzo-Flow) can point at GroundOne by changing only the base URL.
Request: {"state": text or JSON, "model": name, "questions": {key: noul | choice | score}}.
Each question becomes a lettered multiple-choice suffix after the shared state prefix; all questions are scored in
one batched pass (same engine as /v1/verify). Nothing is generated.

Honesty notes (also returned in `x_groundone`):
- The response `model` field always names the local GroundOne model, never Jev; any `jev-*` / `rizzo-*` name is
  accepted as an alias.
- GroundOne is fine-tuned for groundedness questions. Generic questions are answered by the same model and readout,
  but their accuracy is not part of the thesis' claims.
- `confidence` follows the public TypeSafe formula (n·p_max − 1)/(n − 1): it describes the distribution's shape and
  is not a calibrated probability of being correct.
"""
import json
import string
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, JsonValue

LOCAL_ALIAS = "groundone-latest"
FOREIGN_ALIASES = ("jev-", "rizzo-")
MAX_OPTIONS = 26
MAX_LEVELS = 10
SYSTEM = "You are a fast decision system. Read the STATE and answer the question with a single letter."
Structured = str | dict[str, JsonValue] | list[JsonValue]


class Wire(BaseModel):
    model_config = ConfigDict(extra="forbid")


class NoulCriteria(Wire):
    true: Structured | None = None
    false: Structured | None = None


class NoulQuestion(Wire):
    type: Literal["noul"]
    instructions: Structured
    criteria: NoulCriteria | None = None


class ChoiceQuestion(Wire):
    type: Literal["choice"]
    instructions: Structured
    criteria: dict[str, Structured | None] = Field(min_length=2, max_length=MAX_OPTIONS)


class ScoreQuestion(Wire):
    type: Literal["score"]
    instructions: Structured
    criteria: list[Structured] = Field(min_length=2, max_length=MAX_LEVELS)


WireQuestion = Annotated[NoulQuestion | ChoiceQuestion | ScoreQuestion, Field(discriminator="type")]


class SystemOneRequest(BaseModel):
    # Unknown top-level fields are ignored (the official SDKs forward extra fields), as Rizzo-Flow does.
    model_config = ConfigDict(extra="ignore")
    state: Structured
    model: str = Field(min_length=1, max_length=128)
    questions: dict[str, WireQuestion] = Field(min_length=1, max_length=64)


class UnknownModel(ValueError):
    pass


def text(value):
    return value.strip() if isinstance(value, str) else json.dumps(value, ensure_ascii=False, sort_keys=True)


def resolve_model(requested, served):
    if requested in (LOCAL_ALIAS, served) or requested.startswith(FOREIGN_ALIASES):
        return served
    raise UnknownModel(f"Unknown model {requested!r}. Use {LOCAL_ALIAS!r}, {served!r} or a jev-*/rizzo-* alias.")


def list_models(served):
    desc = "Local GroundOne (Qwen2.5 System One, logit readout, MLX). Specialised in groundedness verification."
    return {"models": [
        {"name": LOCAL_ALIAS, "description": desc, "release_date": "2026-10-05"},
        {"name": served, "description": desc, "release_date": "2026-10-05"},
        {"name": "jev-latest", "description": f"Compatibility alias, answered by {served} (not TypeSafe Jev).",
         "release_date": "2026-10-05"},
    ]}


def options_of(q):
    """Return (option names, option descriptions) for a wire question."""
    if isinstance(q, NoulQuestion):
        c = q.criteria
        return ["true", "false"], [
            "Yes" + (f": {text(c.true)}" if c and c.true is not None else ""),
            "No" + (f": {text(c.false)}" if c and c.false is not None else ""),
        ]
    if isinstance(q, ChoiceQuestion):
        names = list(q.criteria)
        return names, [n if d is None else f"{n}: {text(d)}" for n, d in q.criteria.items()]
    return [str(i) for i in range(len(q.criteria))], [text(level) for level in q.criteria]


def render(tokenizer, state, q):
    names, descs = options_of(q)
    letters = string.ascii_uppercase[:len(names)]
    opts = "\n".join(f"{L}. {d}" for L, d in zip(letters, descs))
    user = (f"STATE:\n{text(state)}\n\n"                       # shared prefix across questions
            f"QUESTION: {text(q.instructions)}\n{opts}\nAnswer with the letter of the best option.")
    msgs = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]
    return tokenizer.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True), tuple(letters), names


def confidence(ps):
    n = len(ps)
    return max(0.0, min(1.0, (n * max(ps) - 1) / (n - 1)))


def build_answer(q, names, probs):
    named = dict(zip(names, probs))
    if isinstance(q, NoulQuestion):
        return {"type": "noul", "noul": named["true"]}
    if isinstance(q, ChoiceQuestion):
        return {"type": "choice", "choice": max(named, key=named.get), "probabilities": named, "confidence": confidence(probs)}
    return {"type": "score", "score": sum(i * p for i, p in enumerate(probs)),
            "legend": {str(i): text(level) for i, level in enumerate(q.criteria)},
            "probabilities": named, "confidence": confidence(probs)}
