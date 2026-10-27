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


# ---------------------------------------------------------------------------------------------------- design (b)
# One forward pass per answer: a marker follows every scored sentence and the letter logits are read at the marker's
# last token (docs/dataset_plan.md §8; default design). Causal attention: the verdict on sentence i sees the document
# and sentences 1..i. Nothing after the last marker matters, so the sequence ends there. Pieces are tokenised
# separately and concatenated, so marker positions are exact and identical at training and inference.
PROMPT_VERSION_MARKED = "groundone-v2-marked"
INSTRUCTION_MARKED = ("Check each sentence of the ANSWER against the DOCUMENT. After each sentence give a verdict: "
                      "A if the DOCUMENT supports it, B if the DOCUMENT contradicts it, C if the DOCUMENT does not mention it.")
MARKER = " Verdict:"
LETTERS_MARKED = ("A", "B", "C")  # supported, contradicted, not_mentioned


def encode_marked(tokenizer, doc, sentences, scored):
    """Token ids and marker positions for one answer. `scored[i]` is True for sentences that get a verdict."""
    enc = lambda t: tokenizer.encode(t, add_special_tokens=False)  # noqa: E731
    head = (f"<|im_start|>system\n{SYSTEM}<|im_end|>\n<|im_start|>user\n{INSTRUCTION_MARKED}\n\n"
            f"DOCUMENT:\n{doc}\n\nANSWER:\n")
    ids, pos = enc(head), []
    marker, newline = enc(MARKER), enc("\n")
    for k, (s, sc) in enumerate(zip(sentences, scored)):
        ids += enc(f"[{k + 1}] {s}")
        if sc:
            ids += marker
            pos.append(len(ids) - 1)
        ids += newline
    return ids, pos


def marked_head(tokenizer, doc):
    """The two reusable prefixes of `encode_marked`: the length of the fixed instructions (system + instruction, the
    same for every request) and the token ids of the whole head up to "ANSWER:" (fixed instructions + document).
    Causal attention makes their KV cache exactly reusable by any answer on the same document (prefix caching, D32)."""
    enc = lambda t: tokenizer.encode(t, add_special_tokens=False)  # noqa: E731
    full = enc(f"<|im_start|>system\n{SYSTEM}<|im_end|>\n<|im_start|>user\n{INSTRUCTION_MARKED}\n\nDOCUMENT:\n{doc}\n\nANSWER:\n")
    fixed = enc(f"<|im_start|>system\n{SYSTEM}<|im_end|>\n<|im_start|>user\n{INSTRUCTION_MARKED}\n\n")
    n = 0
    while n < min(len(fixed), len(full)) and fixed[n] == full[n]:  # tokens can merge across the boundary
        n += 1
    return n, full


def marked_prefix_lengths(tokenizer, doc):
    """Token lengths of the fixed instructions and of the whole head (see `marked_head`)."""
    n, full = marked_head(tokenizer, doc)
    return n, len(full)
