"""API, schema and compatibility tests with a fake backend (no model weights needed)."""
import pytest
from fastapi.testclient import TestClient

from groundone.api import create_app
from groundone.calibration import Calibration, softmax
from groundone.engine import Engine
from groundone.prompts import label_for


class FakeTokenizer:
    pad_token_id = 0
    eos_token_id = 0

    def encode(self, text, add_special_tokens=False):
        return [ord(c) % 250 + 1 for c in text]

    def apply_chat_template(self, msgs, tokenize=False, add_generation_prompt=True):
        return "".join(f"<{m['role']}>{m['content']}" for m in msgs) + "<assistant>"


class FakeBackend:
    """Always prefers the first letter (logit 2 vs 0), so every answer is 'A' with p = e^2/(e^2+n-1)."""
    def __init__(self):
        self.tokenizer = FakeTokenizer()
        self.metadata = {"name": "groundone-test", "fingerprint": "f" * 16, "prompt_version": "test"}
        self.calls = []

    def encode(self, text):
        return self.tokenizer.encode(text)

    def score_shared(self, prompts, letters_list):
        self.calls.append(len(prompts))
        return [[2.0] + [0.0] * (len(L) - 1) for L in letters_list], {
            "prefix_tokens": 10, "suffix_tokens": 5 * len(prompts), "prefill_seconds": 0.0, "batch_seconds": 0.0}

    def score_many(self, prompts, letters_list):
        return [[2.0] + [0.0] * (len(L) - 1) for L in letters_list]

    def score_positions(self, seqs, positions, letters=("A", "B", "C")):
        """Design (b): marker j gets logits LOGITS_B[j % len]; one call per request is recorded."""
        self.calls.append(("b", sum(len(p) for p in positions)))
        return [[LOGITS_B[j % len(LOGITS_B)] for j in range(len(p))] for p in positions]


# raw logits per marker: clear supported; borderline (raw argmax = not mentioned, softmax P(supported) = 0.45); contradicted
LOGITS_B = [[3.0, 0.0, 0.0], [0.0, -2.0, 0.2], [0.0, 2.0, 0.0]]


@pytest.fixture
def client():
    engine = Engine(FakeBackend())
    return TestClient(create_app(engine, api_key="")), engine


def test_verify_splits_and_scores_all_questions_in_one_pass(client):
    c, engine = client
    r = c.post("/v1/verify", json={"document": "Paris is in France.", "answer": "Paris is in France. It is big.",
                                   "questions": ["sup", "three", "lenient"]})
    assert r.status_code == 200, r.text
    j = r.json()
    assert [s["text"] for s in j["sentences"]] == ["Paris is in France.", "It is big."]
    assert j["n_decisions"] == 6 and engine.backend.calls == [6]          # 2 sentences x 3 questions, one batched call
    s0 = j["sentences"][0]
    assert set(s0["answers"]) == {"sup", "three", "lenient"}
    assert abs(sum(s0["answers"]["three"].values()) - 1) < 1e-9
    assert s0["labels"]["three"] == "supported" and s0["flagged"] is False
    assert j["usage"]["output_tokens"] == 0


@pytest.mark.parametrize("body", [
    {"document": "x"},                                                     # no answer
    {"document": "x", "answer": "a.", "sentences": ["a"]},                 # both
    {"document": "x", "answer": "a.", "questions": ["nope"]},              # unknown question
    {"document": "x", "answer": "a.", "extra": 1},                          # unknown field (strict contract)
    {"document": "x", "answer": "a.", "questions": ["sup", "sup"]},        # duplicate
])
def test_verify_rejects_invalid_requests(client, body):
    assert client[0].post("/v1/verify", json=body).status_code == 422


def test_systemone_matches_typesafe_wire_shape(client):
    c, engine = client
    r = c.post("/v1/systemone", json={
        "state": "Help! My payouts have been failing for 3 days.", "model": "jev-latest", "trace_id": "ignored",
        "questions": {
            "is_urgent": {"type": "noul", "instructions": "Does this convey urgency?"},
            "team": {"type": "choice", "instructions": "Which team?", "criteria": {"billing": "Payments", "technical": None}},
            "mood": {"type": "score", "instructions": "How frustrated?", "criteria": ["Calm", "Frustrated", "Very angry"]},
        }})
    assert r.status_code == 200, r.text
    j = r.json()
    assert j["model"] == "groundone-test"                                    # never reports Jev
    assert engine.backend.calls == [3]                                      # one shared-state pass for 3 questions
    a = j["answers"]
    assert a["is_urgent"]["type"] == "noul" and 0.5 < a["is_urgent"]["noul"] < 1
    assert a["team"]["choice"] == "billing" and set(a["team"]["probabilities"]) == {"billing", "technical"}
    assert a["mood"]["type"] == "score" and a["mood"]["legend"]["2"] == "Very angry" and 0 <= a["mood"]["score"] <= 2
    assert j["usage"]["output_tokens"] == 0


def test_systemone_unknown_model_is_400(client):
    r = client[0].post("/v1/systemone", json={"state": "s", "model": "gpt-4",
                                              "questions": {"q": {"type": "noul", "instructions": "?"}}})
    assert r.status_code == 400 and r.json()["detail"]["error_type"] == "api_usage_error"


def test_bearer_auth_on_compat_routes():
    c = TestClient(create_app(Engine(FakeBackend()), api_key="secret"))
    assert c.get("/v1/models").status_code == 401
    assert c.get("/v1/models", headers={"Authorization": "Bearer secret"}).status_code == 200
    assert c.get("/health").status_code == 200                              # health stays open


def test_label_mapping_from_three_way_classes():
    assert [label_for(q, "supported") for q in ("sup", "three", "strict", "lenient")] == ["A", "A", "A", "A"]
    assert [label_for(q, "contradicted") for q in ("sup", "three", "strict", "lenient")] == ["B", "B", "B", "B"]
    assert [label_for(q, "not_mentioned") for q in ("sup", "three", "strict", "lenient")] == ["B", "C", "B", "A"]
    assert label_for("sup", binary=1) == "A" and label_for("sup", binary=0) == "B"


# ---------------------------------------------------------------- design (b), served since D27
@pytest.fixture
def client_b():
    engine = Engine(FakeBackend(), design="b")
    return TestClient(create_app(engine, api_key="")), engine


ANSWER_B = "Sure! Paris is the capital of France. It has 90 million inhabitants. It is in Germany."


def test_verify_b_one_pass_and_unscored_sentences(client_b):
    c, engine = client_b
    r = c.post("/v1/verify", json={"document": "Paris is the capital of France.", "answer": ANSWER_B})
    assert r.status_code == 200, r.text
    j = r.json()
    assert j["design"] == "b" and j["usage"]["output_tokens"] == 0
    scored = [s for s in j["sentences"] if s["scored"]]
    assert engine.backend.calls == [("b", len(scored))] and j["n_decisions"] == len(scored) == 3   # one forward pass
    unscored = [s for s in j["sentences"] if not s["scored"]]
    assert [s["text"] for s in unscored] == ["Sure!"] and unscored[0]["answers"] == {} and unscored[0]["p_supported"] is None


def test_verify_b_labels_flags_and_probabilities_are_coherent(client_b):
    c, engine = client_b
    engine.calibration = Calibration({"three": 1.0}, "f" * 16, biases={"three": [0.0, 0.0, 0.0]}, thresholds={"three": 0.4})
    j = c.post("/v1/verify", json={"document": "d", "answer": ANSWER_B, "questions": ["three", "strict", "lenient"]}).json()
    assert j["threshold"] == 0.4 and "threshold" in j["decision_rule"]
    for s in (s for s in j["sentences"] if s["scored"]):
        p, lab = s["answers"]["three"], s["labels"]["three"]
        assert (lab == "supported") == (p["supported"] >= j["threshold"])          # label follows the shown probability
        assert s["flag_strict"] == (lab != "supported") == s["flagged"]
        assert s["flag_lenient"] == (lab == "contradicted")
        assert s["labels"]["strict"] == ("acceptable" if lab == "supported" else "error")
    assert [s["labels"]["three"] for s in j["sentences"] if s["scored"]] == ["supported", "supported", "contradicted"]
    j2 = c.post("/v1/verify", json={"document": "d", "answer": ANSWER_B, "threshold": 0.6}).json()   # request override
    assert [s["labels"]["three"] for s in j2["sentences"] if s["scored"]] == ["supported", "not_mentioned", "contradicted"]


def test_verify_b_without_threshold_uses_raw_argmax(client_b):
    c, _ = client_b
    j = c.post("/v1/verify", json={"document": "d", "answer": ANSWER_B}).json()
    assert j["threshold"] is None and "raw" in j["decision_rule"]
    assert [s["labels"]["three"] for s in j["sentences"] if s["scored"]] == ["supported", "not_mentioned", "contradicted"]
    assert abs(j["sentences"][2]["p_supported"] - softmax(LOGITS_B[1])[0]) < 1e-9
