"""Tests with the real 0.5B model (slow): run with `pytest -m model`."""
import pytest

pytestmark = pytest.mark.model


@pytest.fixture(scope="module")
def engine():
    from groundone.engine import Engine
    return Engine.load("0.5b")


def test_batched_equals_one_pass_per_question(engine):
    """D14: scoring K questions over a shared prefix in one batch must equal scoring each prompt alone."""
    from groundone.prompts import letters, render
    b = engine.backend
    doc = "The Eiffel Tower is in Paris. It was completed in 1889 and is 330 metres tall. " * 5
    sents = ["The tower is in Paris.", "It was finished in 1889.", "It is 500 metres tall."]
    jobs = [(i, q) for i in range(3) for q in ("sup", "three", "strict", "lenient")]
    prompts = [b.encode(render(b.tokenizer, doc, sents, i, q)) for i, q in jobs]
    lets = [letters(q) for _, q in jobs]
    shared, _ = engine._run(b.score_shared, prompts, lets)
    alone = [engine._run(b.score_many, [p], [L])[0] for p, L in zip(prompts, lets)]
    many = engine._run(b.score_many, prompts, lets)
    for s, a, m in zip(shared, alone, many):
        assert max(abs(x - y) for x, y in zip(s, a)) < 2e-2
        assert max(abs(x - y) for x, y in zip(m, a)) < 2e-2


def test_cached_prefix_equals_one_pass(engine):
    """D32: reading the answer after a cached document (built on cached instructions) gives the logits of one pass."""
    from groundone.prompts import encode_marked, marked_prefix_lengths
    b = engine.backend
    doc = "The Eiffel Tower is in Paris. It was completed in 1889 and is 330 metres tall. " * 5
    sents = ["The tower is in Paris.", "It was finished in 1889.", "It is 500 metres tall."]
    ids, pos = encode_marked(b.tokenizer, doc, sents, [True] * 3)
    n_fixed, n_head = marked_prefix_lengths(b.tokenizer, doc)
    assert 0 < n_fixed < n_head < pos[0]
    one = engine._run(b.score_positions, [ids], [pos])[0]
    fixed = engine._run(b.prefill, ids[:n_fixed])
    head = engine._run(b.prefill, ids[:n_head], fixed)
    for prefix in (fixed, head, engine._run(b.prefill, ids[:n_head])):
        cached = engine._run(b.score_positions_from, prefix, ids, pos)
        for x, y in zip(cached, one):
            assert max(abs(u - v) for u, v in zip(x, y)) < 2e-2
    again = engine._run(b.score_positions_from, head, ids, pos)   # the cached state is not mutated by a read
    assert max(abs(u - v) for x, y in zip(again, engine._run(b.score_positions_from, head, ids, pos)) for u, v in zip(x, y)) == 0


def test_verify_end_to_end(engine):
    from groundone.schema import VerifyRequest
    r = engine.verify(VerifyRequest(document="Paris is the capital of France.",
                                    answer="Paris is the capital of France. It has 90 million inhabitants.",
                                    questions=["sup", "three"]))
    assert len(r["sentences"]) == 2 and r["n_decisions"] == 4
    for s in r["sentences"]:
        assert abs(sum(s["answers"]["three"].values()) - 1) < 1e-6
