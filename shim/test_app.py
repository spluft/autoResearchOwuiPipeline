import json
import pytest
from fastapi.testclient import TestClient

import app as shim

client = TestClient(shim.app)

GOOD_REQ = {
    "model": "whatever",
    "input": json.dumps({"user_request": "почини лог", "tool": {"name": "terminal"},
                         "arguments": {"command": "rm -rf /var/log"}}),
    "questions": [{"type": "predicate", "name": "requires_confirmation",
                   "instructions": "dangerous?"}],
}


def patch_upstream(result):
    async def fake(payload):
        fake.last_payload = payload
        return result
    shim.call_upstream = fake
    return fake


@pytest.fixture(autouse=True)
def restore():
    original = shim.call_upstream
    yield
    shim.call_upstream = original


def test_happy_path_translates_both_dialects():
    fake = patch_upstream((200, {"answers": {"requires_confirmation":
                          {"type": "noul", "noul": 0.93}}}, ""))
    r = client.post("/decisions", json=GOOD_REQ)
    assert r.status_code == 200
    assert r.json() == {"answers": [{"name": "requires_confirmation",
                                     "type": "predicate", "probability": 0.93}]}
    # outbound body is systemone dialect
    assert fake.last_payload["questions"]["requires_confirmation"]["type"] == "noul"
    assert isinstance(fake.last_payload["state"], str)
    assert fake.last_payload["model"] == shim.MODEL


def test_edge_values_accepted():
    for p in (0.0, 1.0):
        patch_upstream((200, {"answers": {"requires_confirmation": {"noul": p}}}, ""))
        r = client.post("/decisions", json=GOOD_REQ)
        assert r.status_code == 200
        assert r.json()["answers"][0]["probability"] == p


def test_upstream_http_error_fails_closed():
    patch_upstream((429, None, "http_429"))
    assert client.post("/decisions", json=GOOD_REQ).status_code == 502


def test_upstream_timeout_fails_closed():
    patch_upstream((0, None, "ConnectTimeout"))
    assert client.post("/decisions", json=GOOD_REQ).status_code == 502


def test_upstream_missing_answer_fails_closed():
    patch_upstream((200, {"answers": {}}, ""))
    assert client.post("/decisions", json=GOOD_REQ).status_code == 502


def test_upstream_out_of_range_fails_closed():
    patch_upstream((200, {"answers": {"requires_confirmation": {"noul": 7}}}, ""))
    assert client.post("/decisions", json=GOOD_REQ).status_code == 502


def test_upstream_bool_rejected():
    patch_upstream((200, {"answers": {"requires_confirmation": {"noul": True}}}, ""))
    assert client.post("/decisions", json=GOOD_REQ).status_code == 502


def test_bad_request_missing_input():
    bad = {k: v for k, v in GOOD_REQ.items() if k != "input"}
    assert client.post("/decisions", json=bad).status_code == 400


def test_bad_request_wrong_question_type():
    bad = dict(GOOD_REQ, questions=[{"type": "score", "name": "x"}])
    assert client.post("/decisions", json=bad).status_code == 400


def test_bad_request_duplicate_names():
    q = {"type": "predicate", "name": "a"}
    assert client.post("/decisions", json=dict(GOOD_REQ, questions=[q, q])).status_code == 400


def test_multiple_questions_roundtrip():
    req = dict(GOOD_REQ, questions=[{"type": "predicate", "name": "a"},
                                    {"type": "predicate", "name": "b"}])
    patch_upstream((200, {"answers": {"a": {"noul": 0.1}, "b": {"noul": 0.9}}}, ""))
    r = client.post("/decisions", json=req)
    assert r.status_code == 200
    probs = {a["name"]: a["probability"] for a in r.json()["answers"]}
    assert probs == {"a": 0.1, "b": 0.9}


def test_state_truncated_to_max():
    fake = patch_upstream((200, {"answers": {"requires_confirmation": {"noul": 0.5}}}, ""))
    client.post("/decisions", json=dict(GOOD_REQ, input="x" * (shim.MAX_STATE + 1000)))
    assert len(fake.last_payload["state"]) == shim.MAX_STATE
