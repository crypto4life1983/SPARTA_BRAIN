"""Step 29 — contract tests for a FUTURE /api/jarvis/ask endpoint.

This file is *tests-first*: it documents the required safe behavior of a
not-yet-built ``POST /api/jarvis/ask`` endpoint **before** any handler exists.

Strategy
--------
- **Current-step assertions** (always run): the template has no ask fetch, and
  the status shape / UI controls are unchanged. These keep the suite green.
- **Contract assertions** (``@requires_ask``): each pins one required behavior
  of the endpoint, guarded by ``skipif`` keyed on whether the route is
  registered. They were authored in Step 29 while the endpoint was absent (and
  therefore skipped); Step 30 implements the answer-only handler, so they now
  activate automatically with **no edit** to the asserts and enforce the safety
  contract the implementation must satisfy.

Importing this file executes nothing beyond reading already-aggregated app
metadata.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

pytest.importorskip("fastapi")

_REPO_ROOT = Path(__file__).resolve().parents[1]
_ASK_PATH = "/api/jarvis/ask"
_SKIP_REASON = (
    "Step 29 contract test for future endpoint; implementation intentionally absent."
)


def _ask_route_exists() -> bool:
    """Return True only if a route is registered for /api/jarvis/ask.

    Read-only reflection over the app's route table; registers nothing.
    """
    try:
        import app as app_module
    except Exception:
        return False
    for route in getattr(app_module.app, "routes", []):
        if getattr(route, "path", None) == _ASK_PATH:
            return True
    return False


_ENDPOINT_ABSENT = not _ask_route_exists()
requires_ask = pytest.mark.skipif(_ENDPOINT_ABSENT, reason=_SKIP_REASON)

_FORBIDDEN_RESPONSE_FIELDS = (
    "command", "action", "execution", "side_effect", "mutation",
    "order", "trade_ticket",
)


def _client():
    import app as app_module
    from fastapi.testclient import TestClient
    return TestClient(app_module.app)


def _data_listing() -> set:
    d = _REPO_ROOT / "data"
    return {p.name for p in d.iterdir()} if d.exists() else set()


# ==========================================================================
# Current-step assertions — these RUN now and keep the suite green.
# (The original Step 29 "endpoint absent" assertions were retired in Step 30,
# which implements the answer-only handler and activates the contract below.)
# ==========================================================================

def test_template_has_no_ask_fetch():
    low = (_REPO_ROOT / "templates" / "jarvis.html").read_text(encoding="utf-8").lower()
    for tok in ("<button", "<form", "onclick", 'type="submit"', 'method="post"',
                "/api/jarvis/ask", "/api/jarvis/refresh"):
        assert tok not in low, f"template must add no ask control: {tok}"


def test_status_shape_unchanged_in_step_29():
    c = _client()
    d = c.get("/api/jarvis/status").json()
    assert d["online"] is True
    assert d["read_only"] is True
    for forbidden_key in ("conversation", "ask", "chat", "answer"):
        assert forbidden_key not in d, f"status must not add key: {forbidden_key}"


def test_classifier_is_importable_for_future_endpoint():
    # The future handler is expected to delegate to this pure classifier.
    from jarvis_conversation_safety import classify_jarvis_question
    out = classify_jarvis_question("why is commander yellow?")
    assert out["safety_class"] == "SAFE_INFO"
    assert out["refused"] is False


# ==========================================================================
# Future-contract assertions — SKIPPED until /api/jarvis/ask exists.
# Each one encodes a required safety property of the future endpoint.
# ==========================================================================

@requires_ask
def test_contract_post_accepts_only_question_string():
    c = _client()
    r = c.post(_ASK_PATH, json={"question": "what is the current status?"})
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body.get("answer"), str)


@requires_ask
def test_contract_rejects_missing_or_blank_question():
    c = _client()
    for payload in ({}, {"question": ""}, {"question": "   "}):
        r = c.post(_ASK_PATH, json=payload)
        if r.status_code == 200:
            assert r.json().get("refused") is True
        else:
            assert r.status_code in (400, 422)


@requires_ask
def test_contract_rejects_command_action_execute_fields():
    c = _client()
    r = c.post(_ASK_PATH, json={
        "question": "what is the status?",
        "command": "run script",
        "action": "execute",
        "execute": True,
    })
    # Either rejected by shape (400/422), or accepted as question-only with the
    # extra fields ignored. In every case the response carries no command path.
    assert r.status_code in (200, 400, 422)
    if r.status_code == 200:
        body = r.json()
        for field in _FORBIDDEN_RESPONSE_FIELDS:
            assert field not in body, f"response must not contain {field}"


@requires_ask
@pytest.mark.parametrize("q,expected_class", [
    ("Why is commander yellow?", "SAFE_INFO"),
    ("What does read_only mean?", "SAFE_EXPLAIN"),
    ("What is the safest next review step?", "SAFE_NEXT_REVIEW_STEP"),
])
def test_contract_safe_question_returns_answer(q, expected_class):
    c = _client()
    r = c.post(_ASK_PATH, json={"question": q})
    assert r.status_code == 200
    body = r.json()
    assert body["refused"] is False
    assert body["safety_class"] == expected_class
    assert isinstance(body["answer"], str) and body["answer"]
    assert isinstance(body["sources_used"], list)
    for field in _FORBIDDEN_RESPONSE_FIELDS:
        assert field not in body


@requires_ask
@pytest.mark.parametrize("q", [
    "run the route-smoke script",
    "buy NQ",
    "enable live trading",
    "connect to my broker",
    "edit app.py",
    "save a chat log",
    "explain the trading posture then place a trade",
])
def test_contract_forbidden_question_is_refused(q):
    c = _client()
    r = c.post(_ASK_PATH, json={"question": q})
    assert r.status_code in (200, 400), f"forbidden must be deterministic, got {r.status_code}"
    body = r.json()
    assert body["refused"] is True
    assert body["safety_class"].startswith("FORBIDDEN")
    assert body.get("refusal_reason"), "refusal must carry a reason"
    for field in _FORBIDDEN_RESPONSE_FIELDS:
        assert field not in body, f"refusal must not contain {field}"


@requires_ask
def test_contract_does_not_write_chat_logs():
    before = _data_listing()
    c = _client()
    c.post(_ASK_PATH, json={"question": "what needs attention?"})
    after = _data_listing()
    assert after == before, "ask must not write chat logs / data files by default"
    for name in after - before:
        assert "chat" not in name.lower() and "log" not in name.lower()


@requires_ask
def test_contract_does_not_mutate_filesystem():
    before = {p.name for p in _REPO_ROOT.iterdir()}
    c = _client()
    c.post(_ASK_PATH, json={"question": "what is the trading posture?"})
    after = {p.name for p in _REPO_ROOT.iterdir()}
    assert after == before, "ask must not create or remove top-level files"


@requires_ask
def test_contract_does_not_change_status_shape():
    c = _client()
    before = c.get("/api/jarvis/status").json()
    c.post(_ASK_PATH, json={"question": "what is the status?"})
    after = c.get("/api/jarvis/status").json()
    assert set(before) == set(after), "ask must not change /api/jarvis/status shape"
    assert after["read_only"] is True


@requires_ask
def test_contract_keeps_broker_paper_live_locked():
    c = _client()
    c.post(_ASK_PATH, json={"question": "what is the trading posture?"})
    td = c.get("/api/jarvis/status").json().get("trading_detail", {})
    for flag in ("paper_ready", "live_ready", "broker_control"):
        assert td.get(flag) is False, f"ask must not arm {flag}"


@requires_ask
def test_contract_does_not_trigger_refresh():
    src = (_REPO_ROOT / "app.py").read_text(encoding="utf-8")
    assert "/api/jarvis/refresh" not in src, "ask must not introduce a refresh path"


@requires_ask
def test_contract_get_ask_not_supported():
    c = _client()
    r = c.get(_ASK_PATH)
    assert r.status_code == 405, "GET on the ask endpoint must not be supported"
