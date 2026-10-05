"""Text utilities shared by data building, evaluation and the engine."""
import hashlib
import re

_SENT_RE = re.compile(r"[^.!?\n]+(?:[.!?]+|$)", re.M)


def split_sentences(text):
    """Rule-based sentence splitter (same rule as Phase 0 and the EDA). Returns (start, end, sentence)."""
    out = []
    for m in _SENT_RE.finditer(text):
        s = m.group(0)
        if len(s.strip()) < 3:
            continue
        start = m.start() + (len(s) - len(s.lstrip()))
        end = m.end() - (len(s) - len(s.rstrip()))
        out.append((start, end, text[start:end]))
    return out


def norm(text):
    return re.sub(r"\s+", " ", str(text).strip().lower())


def h(*parts):
    """Stable short hash of normalised text parts (used by the leakage check)."""
    return hashlib.sha1("\x1f".join(norm(p) for p in parts).encode()).hexdigest()[:16]
