"""Tests for the JARVIS conversation safety classifier (Step 28).

The classifier is preparation only: it categorises future JARVIS conversation
questions as safe or forbidden before any /api/jarvis/ask endpoint exists. These
tests pin:

- every label is reachable
- fail-closed behaviour (empty / non-text / unrecognised -> UNSUPPORTED refused)
- forbidden overrides safe in mixed questions
- no ask endpoint was added and /api/jarvis/status shape is unchanged
- the /jarvis template still has no working controls
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from jarvis_conversation_safety import (
    classify_jarvis_question,
    SAFETY_LABELS,
    SAFE_LABELS,
    FORBIDDEN_LABELS,
)

_REPO_ROOT = Path(__file__).resolve().parents[1]


# --- shape ----------------------------------------------------------------

def test_classifier_returns_required_keys():
    out = classify_jarvis_question("what is the current status?")
    assert set(out) == {"safety_class", "refused", "reason", "normalized_question"}
    assert out["safety_class"] in SAFETY_LABELS
    assert isinstance(out["refused"], bool)
    assert isinstance(out["reason"], str) and out["reason"]
    assert isinstance(out["normalized_question"], str)


def test_label_vocabulary_is_complete():
    assert SAFE_LABELS == ("SAFE_INFO", "SAFE_EXPLAIN", "SAFE_NEXT_REVIEW_STEP")
    assert FORBIDDEN_LABELS == (
        "FORBIDDEN_EXECUTION", "FORBIDDEN_TRADING", "FORBIDDEN_MUTATION",
    )
    assert "UNSUPPORTED" in SAFETY_LABELS


# --- safe questions -------------------------------------------------------

@pytest.mark.parametrize("q,label", [
    ("Why is commander yellow?", "SAFE_INFO"),
    ("What needs attention?", "SAFE_INFO"),
    ("What is the current system status?", "SAFE_INFO"),
    ("What is the trading posture?", "SAFE_INFO"),
    ("What JARVIS docs exist?", "SAFE_INFO"),
    ("What does read_only mean?", "SAFE_EXPLAIN"),
    ("Explain pTrading", "SAFE_EXPLAIN"),
    ("Explain cache_freshness", "SAFE_EXPLAIN"),
    ("What is the safest next review step?", "SAFE_NEXT_REVIEW_STEP"),
])
def test_safe_questions_are_allowed(q, label):
    out = classify_jarvis_question(q)
    assert out["safety_class"] == label, f"{q!r} -> {out['safety_class']}"
    assert out["refused"] is False


def test_all_safe_labels_are_reachable():
    seen = {classify_jarvis_question(q)["safety_class"] for q in (
        "what needs attention?",
        "what does read_only mean?",
        "what is the safest next review step?",
    )}
    assert seen == set(SAFE_LABELS)


# --- forbidden execution --------------------------------------------------

@pytest.mark.parametrize("q", [
    "run the route-smoke script",
    "execute the command for me",
    "trigger a refresh of the caches",
    "refresh the status now",
    "stage and commit the changes",
    "commit my staged files",
    "open a terminal",
])
def test_forbidden_execution_is_refused(q):
    out = classify_jarvis_question(q)
    assert out["safety_class"] == "FORBIDDEN_EXECUTION", f"{q!r} -> {out['safety_class']}"
    assert out["refused"] is True


# --- forbidden trading ----------------------------------------------------

@pytest.mark.parametrize("q", [
    "place a trade now",
    "buy NQ",
    "sell ES",
    "go long",
    "go short",
    "enable live trading",
    "enable paper trading",
    "connect to my broker",
    "approve and promote the S26 strategy",
])
def test_forbidden_trading_is_refused(q):
    out = classify_jarvis_question(q)
    assert out["safety_class"] == "FORBIDDEN_TRADING", f"{q!r} -> {out['safety_class']}"
    assert out["refused"] is True


# --- forbidden mutation ---------------------------------------------------

@pytest.mark.parametrize("q", [
    "modify the config file",
    "write to disk",
    "edit app.py",
    "update the template",
    "save a chat log",
    "delete the report",
])
def test_forbidden_mutation_is_refused(q):
    out = classify_jarvis_question(q)
    assert out["safety_class"] == "FORBIDDEN_MUTATION", f"{q!r} -> {out['safety_class']}"
    assert out["refused"] is True


# --- fail-closed ----------------------------------------------------------

@pytest.mark.parametrize("q", ["", "   ", "\n\t "])
def test_empty_is_unsupported_refused(q):
    out = classify_jarvis_question(q)
    assert out["safety_class"] == "UNSUPPORTED"
    assert out["refused"] is True


def test_non_string_is_unsupported_refused():
    for bad in (None, 123, ["question"], {"q": 1}):
        out = classify_jarvis_question(bad)
        assert out["safety_class"] == "UNSUPPORTED"
        assert out["refused"] is True


@pytest.mark.parametrize("q", [
    "make me a sandwich",
    "tell me a joke",
    "do the thing",
    "asdf qwerty",
])
def test_ambiguous_is_unsupported_refused(q):
    out = classify_jarvis_question(q)
    assert out["safety_class"] == "UNSUPPORTED"
    assert out["refused"] is True


# --- forbidden overrides safe in mixed questions --------------------------

@pytest.mark.parametrize("q,label", [
    ("explain the trading posture then place a trade", "FORBIDDEN_TRADING"),
    ("what is the status, also run the smoke script", "FORBIDDEN_EXECUTION"),
    ("explain read_only and then edit app.py", "FORBIDDEN_MUTATION"),
    ("why is commander yellow? also buy NQ", "FORBIDDEN_TRADING"),
])
def test_forbidden_overrides_safe(q, label):
    out = classify_jarvis_question(q)
    assert out["safety_class"] == label, f"{q!r} -> {out['safety_class']}"
    assert out["refused"] is True


# --- normalization --------------------------------------------------------

def test_normalized_question_is_whitespace_collapsed():
    out = classify_jarvis_question("  what   needs\tattention?  ")
    assert out["normalized_question"] == "what needs attention?"


# --- the classifier introduces no endpoint / no side effects --------------

def test_classifier_module_imports_nothing_dangerous():
    src = (_REPO_ROOT / "jarvis_conversation_safety.py").read_text(encoding="utf-8")
    code = re.sub(r'"""[\s\S]*?"""', "", src)  # drop docstrings
    code = re.sub(r"(?m)#.*$", "", code)        # drop comments
    low = code.lower()
    for tok in ("import subprocess", "import os", "import socket", "import requests",
                "import urllib", "open(", "import broker", "from broker",
                "place_order", "submit_order", "execute_trade"):
        assert tok not in low, f"classifier must not reference: {tok}"


def test_step_28_adds_no_refresh_or_execution_endpoint():
    # Step 30 intentionally introduced an answer-only POST /api/jarvis/ask, so
    # the old ask-absence guard is retired. The refresh/execution guard remains
    # active: the classifier work must never add a refresh endpoint.
    src = (_REPO_ROOT / "app.py").read_text(encoding="utf-8")
    assert "/api/jarvis/refresh" not in src, "must not add a refresh endpoint"


def test_jarvis_status_shape_unchanged_after_step_28():
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    d = client.get("/api/jarvis/status").json()
    assert d["online"] is True
    assert d["read_only"] is True
    for forbidden_key in ("conversation", "ask", "chat", "answer"):
        assert forbidden_key not in d


def test_jarvis_template_still_has_no_controls():
    # Step 31 intentionally wires the read-only /api/jarvis/ask endpoint into the
    # UI, so the old ask-absence guard is obsolete and retired. The
    # execution/refresh/mutation guards remain active: the template must add no
    # real <button>, <form>, inline handler, submit, method="post", or refresh
    # wiring.
    low = (_REPO_ROOT / "templates" / "jarvis.html").read_text(encoding="utf-8").lower()
    for tok in ("<button", "<form", "onclick", 'type="submit"', 'method="post"',
                "/api/jarvis/refresh"):
        assert tok not in low, f"template must add no control: {tok}"


# --- Step 38: read-only trading-status questions classify SAFE_INFO --------

@pytest.mark.parametrize("q", [
    "how are we doing with trading?",
    "what is the trading status?",
    "what is the trading posture?",
    "are we ready for paper trading?",
    "are we ready for live trading?",
])
def test_step38_trading_status_questions_are_safe_info(q):
    out = classify_jarvis_question(q)
    assert out["refused"] is False, f"{q!r} must be a read-only safe question"
    assert out["safety_class"] == "SAFE_INFO"


@pytest.mark.parametrize("q", [
    "enable paper trading",
    "enable live trading",
    "connect broker",
    "approve strategy",
    "place a trade on NQ",
    "explain the trading posture then place a trade",
])
def test_step38_trading_action_questions_still_forbidden(q):
    # The new safe patterns must never let an action-request through; forbidden
    # is checked first, so these stay refused.
    out = classify_jarvis_question(q)
    assert out["refused"] is True, f"{q!r} must stay refused"
    assert out["safety_class"].startswith("FORBIDDEN")
