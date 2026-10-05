"""Single source of truth for GroundOne's prompt format and question set.

Training, evaluation and the inference engine all render prompts through this module, so the text the model is
trained on is exactly the text it sees at inference (plan §4.1, §6.2).

Layout (Qwen2.5 chat template):
    system: SYSTEM
    user:   DOCUMENT + numbered ANSWER sentences   <- shared prefix, identical for every question about this answer
            + one question about sentence [i]      <- short per-question suffix
    assistant: <one answer letter>                 <- logits of the allowed letters are read here
"""

# Bump whenever SYSTEM, QUESTIONS or the layout change: calibrations and results are tied to it.
PROMPT_VERSION = "groundone-v1"

SYSTEM = "You are a faithfulness verifier for retrieval-augmented answers."

# Answer classes used for three-way labels.
SUPPORTED, CONTRADICTED, NOT_MENTIONED = "supported", "contradicted", "not_mentioned"

# question type -> (template, allowed letters). Letter meanings are fixed (no shuffling, decision D3).
QUESTIONS = {
    "sup": ("Question about sentence [{i}]: is it fully supported by the DOCUMENT? "
            "Answer A for yes, B for no.", ("A", "B")),
    "three": ("Question about sentence [{i}]: compared with the DOCUMENT, is it supported, contradicted, or not mentioned? "
              "Answer A for supported, B for contradicted, C for not mentioned.", ("A", "B", "C")),
    "strict": ("Question about sentence [{i}]: under the STRICT rule (anything not stated in the DOCUMENT is an error), "
               "is it acceptable? Answer A for acceptable, B for error.", ("A", "B")),
    "lenient": ("Question about sentence [{i}]: under the LENIENT rule (only statements that contradict the DOCUMENT are "
                "errors; information the DOCUMENT does not mention is acceptable), is it acceptable? "
                "Answer A for acceptable, B for error.", ("A", "B")),
}
QTYPES = tuple(QUESTIONS)


def label_for(qtype, cls=None, binary=None):
    """Gold letter for a question type. `cls` is a three-way class; `binary` is 1 = supported, 0 = not (binary-only data)."""
    if cls is None:
        if qtype not in ("sup", "strict"):
            raise ValueError(f"{qtype} needs a three-way class")
        return "A" if binary == 1 else "B"
    if qtype in ("sup", "strict"):
        return "A" if cls == SUPPORTED else "B"
    if qtype == "lenient":
        return "B" if cls == CONTRADICTED else "A"
    if qtype == "three":
        return {SUPPORTED: "A", CONTRADICTED: "B", NOT_MENTIONED: "C"}[cls]
    raise ValueError(qtype)


def user_prefix(doc, sentences):
    """Shared part of the user message: the document and the numbered answer."""
    numbered = "\n".join(f"[{k + 1}] {s}" for k, s in enumerate(sentences))
    return f"DOCUMENT:\n{doc}\n\nANSWER (numbered sentences):\n{numbered}\n\n"


def question_text(qtype, idx):
    """Per-question suffix. `idx` is 0-based; sentences are numbered from 1 in the prompt."""
    return QUESTIONS[qtype][0].format(i=idx + 1)


def render(tokenizer, doc, sentences, idx, qtype):
    """Full chat prompt (string) ending right before the answer letter."""
    msgs = [{"role": "system", "content": SYSTEM},
            {"role": "user", "content": user_prefix(doc, sentences) + question_text(qtype, idx)}]
    return tokenizer.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)


def letters(qtype):
    return QUESTIONS[qtype][1]


# Human-readable names of the answers, in letter order (used by the API).
ANSWER_NAMES = {
    "sup": ("supported", "not_supported"),
    "three": (SUPPORTED, CONTRADICTED, NOT_MENTIONED),
    "strict": ("acceptable", "error"),
    "lenient": ("acceptable", "error"),
}
