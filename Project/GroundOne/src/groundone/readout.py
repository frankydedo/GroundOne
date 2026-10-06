"""Logits at selected positions only (design b): run the transformer body, gather the hidden states at the marker
positions, and apply the output head there. Avoids materialising (batch x length x vocabulary) logits."""


def head(model, h):
    if getattr(model.args, "tie_word_embeddings", False):
        return model.model.embed_tokens.as_linear(h)
    return model.lm_head(h)


def logits_at(model, x, rows, cols):
    """x: (B, S) token ids; rows, cols: flat index arrays of the positions to read. Returns (N, vocab) logits."""
    h = model.model(x)
    return head(model, h[rows, cols])
