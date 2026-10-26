"""Native API contract (`POST /v1/verify`). Strict: unknown fields are rejected (422).

With a design (b) adapter (the default since D22, served since D27) the answer is segmented with the rule used for
training (data/segment.py); sentences without checkable content get no verdict (`scored: false`); all verdicts come
from one forward pass. `questions` then only selects which derived views of the three probabilities are returned.
"""
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

QType = Literal["sup", "three", "strict", "lenient"]


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class VerifyRequest(Strict):
    document: str = Field(min_length=1, max_length=200_000, description="Retrieved context the answer must be grounded in")
    answer: str | None = Field(default=None, max_length=50_000, description="Answer text; split into sentences by the server")
    sentences: list[str] | None = Field(default=None, min_length=1, max_length=128,
                                        description="Pre-split answer sentences (alternative to `answer`)")
    questions: list[QType] = Field(default=["three"], min_length=1, max_length=4,
                                   description="sup = supported?; three = supported/contradicted/not mentioned; "
                                               "strict / lenient = acceptable under that rule? (design b: views derived "
                                               "from the same three probabilities)")
    threshold: float | None = Field(default=None, ge=0.0, le=1.0,
                                    description="Design b: label 'supported' iff P(supported) >= threshold; default: the "
                                                "model's threshold fitted on dev, else the raw class-balanced argmax. "
                                                "Design a: flag if P(supported) < threshold; default 0.5")

    @model_validator(mode="after")
    def one_answer(self):
        if (self.answer is None) == (self.sentences is None):
            raise ValueError("Provide exactly one of `answer` or `sentences`")
        if len(set(self.questions)) != len(self.questions):
            raise ValueError("Duplicate question types")
        return self


class SentenceResult(Strict):
    index: int
    text: str
    scored: bool = Field(default=True, description="False for sentences without checkable content (no verdict)")
    p_supported: float | None = Field(description="P(supported); null if not scored (design a: only if `sup` was asked)")
    flagged: bool | None = Field(description="Strict error: the sentence is not labelled supported")
    flag_strict: bool | None = Field(default=None, description="Label is contradicted or not mentioned (design b)")
    flag_lenient: bool | None = Field(default=None, description="Label is contradicted (design b)")
    answers: dict[str, dict[str, float]] = Field(description="Per question type: probability of each answer")
    labels: dict[str, str] = Field(description="Per question type: most probable answer")


class VerifyResponse(Strict):
    model: str
    design: str = Field(default="a", description="Readout design: b = one pass with a marker per sentence")
    decision_rule: str | None = Field(default=None, description="How labels and flags are derived")
    threshold: float | None = Field(default=None, description="Threshold on P(supported) used for the labels")
    sentences: list[SentenceResult]
    n_decisions: int
    usage: dict[str, int]
    timing: dict[str, float]
    prefix_cache: str | None = Field(default=None, description="Design (b): prefix reused from the cache: answer prefix "
                                                               "(the unchanged first sentences of the last answer on this document), "
                                                               "document, instructions (document read now) or none (D32)")
    fingerprint: str
    calibrated: bool
