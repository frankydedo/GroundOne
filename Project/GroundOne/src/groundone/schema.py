"""Native API contract (`POST /v1/verify`). Strict: unknown fields are rejected (422)."""
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
    questions: list[QType] = Field(default=["sup"], min_length=1, max_length=4,
                                   description="sup = supported?; three = supported/contradicted/not mentioned; "
                                               "strict / lenient = acceptable under that rule?")
    threshold: float = Field(default=0.5, ge=0.0, le=1.0, description="Flag a sentence if P(supported) < threshold")

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
    p_supported: float | None = Field(description="From the `sup` question; null if it was not asked")
    flagged: bool | None = Field(description="p_supported < threshold")
    answers: dict[str, dict[str, float]] = Field(description="Per question type: probability of each answer")
    labels: dict[str, str] = Field(description="Per question type: most probable answer")


class VerifyResponse(Strict):
    model: str
    sentences: list[SentenceResult]
    n_decisions: int
    usage: dict[str, int]
    timing: dict[str, float]
    fingerprint: str
    calibrated: bool
