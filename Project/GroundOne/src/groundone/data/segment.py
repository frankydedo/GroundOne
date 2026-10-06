"""Sentence segmentation and the "checkable content" rule, shared by dataset building and inference (dataset plan §4).

segment(text) -> list of Sentence(start, end, text, checkable)
  1. split on line breaks (answers often contain lists and headings on separate lines);
  2. split each line with pysbd (rule-based; handles abbreviations and decimals such as "4.0 stars");
  3. strip leading list markers ("3. ", "a) ", "* ", "- "): they are layout, not content;
  4. mark sentences without checkable content: they stay in the numbered answer as context, but are not decisions.
Character offsets refer to the original text, so span annotations (RAGTruth) can be mapped onto sentences.
The rule was written a priori; its agreement with LLM-AggreFact's own segmentation is only reported (check C2).
"""
import re
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Sentence:
    start: int
    end: int
    text: str
    checkable: bool


_LIST = re.compile(r"^(?:\d{1,2}[.)]|[a-z]\)|[*•\-–])\s+")
_CITATION = re.compile(r"^\(?\s*(passages?|source|document)\s*[\d,\s and]*\)?[.\s]*$", re.I)
_WORD = re.compile(r"[A-Za-z0-9][A-Za-z0-9'’\-]*")
# conversational / meta formulas with no claim about the document
_META = re.compile(
    r"^(sure|certainly|of course|okay|ok|great|absolutely|yes|no problem)\b[\s!,.]*$"
    r"|^(here (is|are)|below (is|are)|i hope (this|that) helps|let me know|feel free|thank you|thanks)\b"
    r"|^(sure|certainly|of course|absolutely)[,!.]?\s*(i can|i'd be happy|i would be happy|i'll|here)\b"
    r"|^that'?s (it|all)\b[\s!.]*$"
    r"|^(i'?m sorry|sorry\b|unable to answer|i (cannot|can't|am unable to) (answer|provide|determine|find))"
    r"|\b(i am|i'm|we are) unable to (answer|provide|determine)\b"
    r"|^(the (given|provided) (passages?|information|text|context|data) (does|do) not (contain|provide|mention|include|specify|say))",
    re.I)


@lru_cache(maxsize=1)
def _seg():
    import pysbd
    return pysbd.Segmenter(language="en", clean=False, char_span=True)


def is_checkable(s):
    """False for sentences without checkable content: fewer than 2 words, a heading that introduces a list (trailing colon),
    or a conversational / refusal formula."""
    t = s.strip().strip("*#-•> \t").strip()
    if len(_WORD.findall(t)) < 2:
        return False
    if t.endswith(":") or _CITATION.match(t):
        return False
    return not _META.search(t)


def segment(text):
    out = []
    pos = 0
    for line in text.split("\n"):
        if line.strip():
            for span in _seg().segment(line):
                raw = span.sent
                lead = len(raw) - len(raw.lstrip())
                body = raw.strip()
                m = _LIST.match(body)
                if m:
                    lead += m.end()
                    body = body[m.end():].strip()
                if body:
                    a = pos + span.start + lead
                    out.append(Sentence(a, a + len(body), body, is_checkable(body)))
        pos += len(line) + 1
    return out
