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

def test_template_has_no_execution_or_refresh_control():
    # Step 31 intentionally wired the shell to the answer-only POST
    # /api/jarvis/ask, so the old ask-absence guard is retired. The
    # execution/form/refresh guards remain active: the template must add no
    # <button>, <form>, inline handler, submit, method="post", or refresh wiring.
    low = (_REPO_ROOT / "templates" / "jarvis.html").read_text(encoding="utf-8").lower()
    for tok in ("<button", "<form", "onclick", 'type="submit"', 'method="post"',
                "/api/jarvis/refresh"):
        assert tok not in low, f"template must add no execution/refresh control: {tok}"


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


# ==========================================================================
# Step 38 — answer-quality for read-only operator trading-status questions.
# These prove the safe answers now summarize the actual read-only trading
# posture (read_only / paper_ready / live_ready / broker_control) instead of a
# generic safety shell, WITHOUT loosening any refusal behavior.
# ==========================================================================

_STEP38_TRADING_QUESTIONS = (
    "how are we doing with trading?",
    "what is the trading status?",
    "what is the trading posture?",
    "are we ready for paper trading?",
    "are we ready for live trading?",
)


@requires_ask
@pytest.mark.parametrize("q", _STEP38_TRADING_QUESTIONS)
def test_step38_trading_question_is_safe_and_reports_posture(q):
    c = _client()
    r = c.post(_ASK_PATH, json={"question": q})
    assert r.status_code == 200
    body = r.json()
    assert body["refused"] is False, f"{q!r} must be answerable read-only"
    assert body["safety_class"] == "SAFE_INFO"
    ans = body["answer"].lower()
    # The four posture fields must all be named in the answer.
    for field in ("read_only", "paper_ready", "live_ready", "broker_control"):
        assert field in ans, f"{q!r} answer must mention {field}"
    # Observation-only posture; paper/live not armed.
    assert "observation-only" in ans
    assert "paper_ready=false" in ans
    assert "live_ready=false" in ans
    assert "trading_detail" in body["sources_used"]
    for field in _FORBIDDEN_RESPONSE_FIELDS:
        assert field not in body


@requires_ask
def test_step38_trading_answer_invents_no_performance_claims():
    c = _client()
    body = c.post(_ASK_PATH, json={"question": "how are we doing with trading?"}).json()
    ans = body["answer"].lower()
    # No invented profit / readiness / validation language.
    for banned in ("profit", "pnl", "return", "win rate", "ready to trade",
                   "validated", "approved"):
        assert banned not in ans, f"answer must not invent {banned!r}"


@requires_ask
@pytest.mark.parametrize("q", [
    "place a trade on NQ",
    "buy NQ",
    "sell ES",
    "go long",
    "enable paper trading",
    "enable live trading",
    "connect broker",
    "approve strategy",
    "run script",
    "refresh status",
    "modify file",
])
def test_step38_forbidden_questions_still_refused(q):
    c = _client()
    body = c.post(_ASK_PATH, json={"question": q}).json()
    assert body["refused"] is True, f"{q!r} must stay refused"
    assert body["safety_class"].startswith("FORBIDDEN")
    assert body.get("refusal_reason")
    for field in _FORBIDDEN_RESPONSE_FIELDS:
        assert field not in body


@requires_ask
def test_step38_forbidden_override_on_mixed_intent():
    c = _client()
    body = c.post(_ASK_PATH, json={
        "question": "explain the trading posture then place a trade",
    }).json()
    assert body["refused"] is True
    assert body["safety_class"] == "FORBIDDEN_TRADING"


@requires_ask
def test_step38_status_shape_unchanged_after_trading_ask():
    c = _client()
    before = c.get("/api/jarvis/status").json()
    c.post(_ASK_PATH, json={"question": "how are we doing with trading?"})
    after = c.get("/api/jarvis/status").json()
    assert set(before) == set(after)
    assert after["read_only"] is True
    td = after.get("trading_detail", {})
    for flag in ("paper_ready", "live_ready", "broker_control"):
        assert td.get(flag) is False


# ==========================================================================
# Step 41 — natural trading-status phrase coverage. Casual phrasings like
# "how is the trading doing?" must answer with the observation-only posture
# (refused=false) instead of being refused as UNSUPPORTED, while mixed
# forbidden wording still refuses.
# ==========================================================================

_STEP41_NATURAL_QUESTIONS = (
    "how is the trading doing?",
    "how's the trading doing?",
    "how’s the trading doing?",
    "how is trading doing?",
    "how are trades doing?",
    "how is our trading doing?",
    "how is the trading bot doing?",
    "how is the trading system doing?",
    "how is paper trading doing?",
    "how is live trading doing?",
    "what's going on with trading?",
    "what’s going on with trading?",
    "give me trading status",
    "tell me trading status",
    "trading update",
    "trading overview",
    "are we doing good with trading?",
    "are we okay with trading?",
)


@requires_ask
@pytest.mark.parametrize("q", _STEP41_NATURAL_QUESTIONS)
def test_step41_natural_trading_question_reports_posture(q):
    c = _client()
    r = c.post(_ASK_PATH, json={"question": q})
    assert r.status_code == 200
    body = r.json()
    assert body["refused"] is False, f"{q!r} must be answerable read-only"
    assert body["safety_class"] == "SAFE_INFO"
    ans = body["answer"].lower()
    assert "observation-only" in ans
    assert "read_only=true" in ans
    assert "paper_ready=false" in ans
    assert "live_ready=false" in ans
    assert "broker_control=false" in ans
    assert "trading_detail" in body["sources_used"]
    for field in _FORBIDDEN_RESPONSE_FIELDS:
        assert field not in body


@requires_ask
def test_step41_natural_answer_invents_no_performance_claims():
    c = _client()
    body = c.post(_ASK_PATH, json={"question": "how is the trading doing?"}).json()
    ans = body["answer"].lower()
    for banned in ("profit", "pnl", "return", "win rate", "ready to trade",
                   "validated", "approved"):
        assert banned not in ans, f"answer must not invent {banned!r}"


@requires_ask
@pytest.mark.parametrize("q", [
    "how is trading doing then place a trade",
    "trading update and buy NQ",
    "tell me trading status and enable live trading",
    "how is the bot doing and connect broker",
    "trading overview then run script",
    "are we okay with trading then approve strategy",
])
def test_step41_natural_phrases_with_forbidden_intent_refused(q):
    c = _client()
    body = c.post(_ASK_PATH, json={"question": q}).json()
    assert body["refused"] is True, f"{q!r} must stay refused"
    assert body["safety_class"].startswith("FORBIDDEN")
    assert body.get("refusal_reason")
    for field in _FORBIDDEN_RESPONSE_FIELDS:
        assert field not in body


@requires_ask
def test_step41_status_shape_unchanged_after_natural_ask():
    c = _client()
    before = c.get("/api/jarvis/status").json()
    c.post(_ASK_PATH, json={"question": "how is the trading doing?"})
    after = c.get("/api/jarvis/status").json()
    assert set(before) == set(after)
    assert after["read_only"] is True
    td = after.get("trading_detail", {})
    for flag in ("paper_ready", "live_ready", "broker_control"):
        assert td.get(flag) is False


# ==========================================================================
# Step 43 — "what changed?" change-summary questions. JARVIS keeps no stored
# snapshot, so these answer refused=false with a CURRENT read-only status
# summary that explicitly says it cannot compare against a previous baseline
# and claims no verified changes. Mixed forbidden wording still refuses.
# ==========================================================================

_STEP43_WHAT_CHANGED_QUESTIONS = (
    "what changed since last check?",
    "what changed since yesterday?",
    "what changed today?",
    "what is new?",
    "what new commits happened?",
    "what new trading reports appeared?",
    "what warnings changed?",
    "what changed in JARVIS?",
    "summarize current changes",
    "give me a change summary",
    "what changed since I last checked?",
)


@requires_ask
@pytest.mark.parametrize("q", _STEP43_WHAT_CHANGED_QUESTIONS)
def test_step43_what_changed_question_is_safe_and_summarizes_current(q, monkeypatch, tmp_path):
    # Force the no-snapshot path so this keeps validating the Step 43 baseline
    # behavior even when an offline runtime snapshot happens to exist on disk.
    import app as app_module
    monkeypatch.setattr(app_module, "_JARVIS_LATEST_SNAPSHOT", tmp_path / "missing.json")
    c = _client()
    r = c.post(_ASK_PATH, json={"question": q})
    assert r.status_code == 200
    body = r.json()
    assert body["refused"] is False, f"{q!r} must be answerable read-only"
    assert body["safety_class"] == "SAFE_INFO"
    ans = body["answer"].lower()
    # Must state it cannot compare against a previous baseline/snapshot.
    assert "no baseline" in ans or "no previous" in ans or "no stored" in ans, (
        f"{q!r} answer must say no baseline/snapshot is available")
    assert "cannot compare" in ans or "no previous baseline" in ans, (
        f"{q!r} answer must say it cannot compare yet")
    # Must summarize current read-only status, clearly labeled as current.
    assert "current" in ans
    assert isinstance(body["sources_used"], list) and body["sources_used"]
    for field in _FORBIDDEN_RESPONSE_FIELDS:
        assert field not in body


@requires_ask
def test_step43_what_changed_does_not_claim_verified_changes(monkeypatch, tmp_path):
    import app as app_module
    monkeypatch.setattr(app_module, "_JARVIS_LATEST_SNAPSHOT", tmp_path / "missing.json")
    c = _client()
    body = c.post(_ASK_PATH, json={"question": "what changed since last check?"}).json()
    ans = body["answer"].lower()
    # With no baseline it must not assert that anything changed, nor invent
    # performance/readiness claims.
    for banned in ("has changed", "have changed", "newly added",
                   "profit", "pnl", "win rate", "ready to trade",
                   "validated", "approved"):
        assert banned not in ans, f"answer must not assert/invent {banned!r}"
    # It must explicitly claim no changes without a baseline.
    assert "claiming no changes" in ans or "no changes" in ans


@requires_ask
@pytest.mark.parametrize("q", [
    "what changed and refresh status",
    "what changed and run git log",
    "what changed and write a snapshot",
    "what changed and save this state",
    "what changed and execute report generator",
    "what changed and clean untracked files",
    "what changed and start trading",
    "summarize changes then place a trade",
    "what new reports appeared then approve strategy",
])
def test_step43_what_changed_with_forbidden_intent_refused(q):
    c = _client()
    body = c.post(_ASK_PATH, json={"question": q}).json()
    assert body["refused"] is True, f"{q!r} must stay refused"
    assert body["safety_class"].startswith("FORBIDDEN")
    assert body.get("refusal_reason")
    for field in _FORBIDDEN_RESPONSE_FIELDS:
        assert field not in body


@requires_ask
def test_step43_status_shape_unchanged_after_what_changed_ask():
    c = _client()
    before = c.get("/api/jarvis/status").json()
    c.post(_ASK_PATH, json={"question": "what changed since last check?"})
    after = c.get("/api/jarvis/status").json()
    assert set(before) == set(after)
    assert after["read_only"] is True
    td = after.get("trading_detail", {})
    for flag in ("paper_ready", "live_ready", "broker_control"):
        assert td.get(flag) is False


# ==========================================================================
# Step 47 — read-only comparison against the offline-generated latest snapshot.
# JARVIS may READ storage/jarvis/snapshots/latest_snapshot.json display-only and
# report verified differences vs current read-only status. It writes nothing,
# never authorizes trading, and fails closed on a missing/corrupt snapshot.
# All tests install a temp snapshot path via monkeypatch so they never depend on
# or mutate the real runtime snapshot.
# ==========================================================================

def _build_current_snapshot():
    """Build the current snapshot-shaped view the same way the app does."""
    import app as app_module
    from tools.jarvis_snapshot_report import build_snapshot
    return build_snapshot(app_module.api_jarvis_status())


def _install_snapshot(monkeypatch, tmp_path, data):
    """Write a snapshot (dict -> json, or raw str for corrupt) and point the
    app's latest-snapshot path at it. Returns the temp path."""
    import json as _json
    import app as app_module
    p = tmp_path / "latest_snapshot.json"
    p.write_text(data if isinstance(data, str) else _json.dumps(data), encoding="utf-8")
    monkeypatch.setattr(app_module, "_JARVIS_LATEST_SNAPSHOT", p)
    return p


@requires_ask
def test_step47_missing_snapshot_keeps_no_baseline_answer(monkeypatch, tmp_path):
    import app as app_module
    monkeypatch.setattr(app_module, "_JARVIS_LATEST_SNAPSHOT", tmp_path / "absent.json")
    c = _client()
    body = c.post(_ASK_PATH, json={"question": "what changed since last snapshot?"}).json()
    assert body["refused"] is False
    assert body["safety_class"] == "SAFE_INFO"
    ans = body["answer"].lower()
    assert "no stored baseline" in ans or "no previous" in ans
    assert "cannot compare" in ans
    assert "current status:" in ans
    for field in _FORBIDDEN_RESPONSE_FIELDS:
        assert field not in body


@requires_ask
def test_step47_valid_snapshot_shows_comparison_section(monkeypatch, tmp_path):
    _install_snapshot(monkeypatch, tmp_path, _build_current_snapshot())
    c = _client()
    body = c.post(_ASK_PATH, json={"question": "what changed since last snapshot?"}).json()
    assert body["refused"] is False
    assert body["safety_class"] == "SAFE_INFO"
    ans = body["answer"]
    assert "Verified changes since latest snapshot" in ans
    assert "Current status:" in ans
    assert "Unknown / not compared" in ans
    assert "latest_snapshot" in body["sources_used"]
    for field in _FORBIDDEN_RESPONSE_FIELDS:
        assert field not in body


@requires_ask
def test_step47_changed_git_head_reported_as_verified_change(monkeypatch, tmp_path):
    import copy
    prev = copy.deepcopy(_build_current_snapshot())
    prev.setdefault("git", {})["head"] = "deadbee"
    _install_snapshot(monkeypatch, tmp_path, prev)
    c = _client()
    ans = c.post(_ASK_PATH, json={"question": "what new commits happened?"}).json()["answer"]
    assert "git HEAD changed deadbee" in ans


@requires_ask
def test_step47_changed_commander_state_and_warnings_reported(monkeypatch, tmp_path):
    import copy
    prev = copy.deepcopy(_build_current_snapshot())
    cs = prev.setdefault("commander_snapshot", {})
    cs["overall_state"] = "__prev_state__"
    cs["warnings"] = []  # force a different warning count
    _install_snapshot(monkeypatch, tmp_path, prev)
    c = _client()
    ans = c.post(_ASK_PATH, json={"question": "what warnings changed?"}).json()["answer"]
    assert "commander state changed __prev_state__" in ans
    assert "warning count changed" in ans


@requires_ask
def test_step47_changed_trading_posture_reported_without_authorizing(monkeypatch, tmp_path):
    import copy
    prev = copy.deepcopy(_build_current_snapshot())
    # Pretend the previous snapshot had paper_ready True; current is locked False.
    prev.setdefault("trading_detail", {})["paper_ready"] = True
    _install_snapshot(monkeypatch, tmp_path, prev)
    c = _client()
    body = c.post(_ASK_PATH, json={"question": "what changed since last snapshot?"}).json()
    ans = body["answer"]
    assert "trading posture paper_ready changed True -> False" in ans
    assert "no trading authorized" in ans.lower()
    # The answer reports a flag change but authorizes nothing and adds no
    # command/order fields, and live status flags stay locked.
    for field in _FORBIDDEN_RESPONSE_FIELDS:
        assert field not in body
    td = c.get("/api/jarvis/status").json()["trading_detail"]
    for flag in ("paper_ready", "live_ready", "broker_control"):
        assert td.get(flag) is False


@requires_ask
def test_step47_changed_latest_report_list_reported(monkeypatch, tmp_path):
    import copy
    prev = copy.deepcopy(_build_current_snapshot())
    prev["trading_latest_reports"] = [
        {"name": "__old_report__", "path": "x", "modified_at": "t", "has_md": True}
    ]
    _install_snapshot(monkeypatch, tmp_path, prev)
    c = _client()
    ans = c.post(_ASK_PATH, json={"question": "what new trading reports appeared?"}).json()["answer"]
    assert "latest trading reports changed" in ans
    assert "removed __old_report__" in ans


@requires_ask
def test_step47_corrupt_snapshot_fails_closed(monkeypatch, tmp_path):
    _install_snapshot(monkeypatch, tmp_path, "{ this is not valid json ")
    c = _client()
    r = c.post(_ASK_PATH, json={"question": "what changed since last snapshot?"})
    assert r.status_code == 200  # did not crash
    body = r.json()
    assert body["refused"] is False
    ans = body["answer"].lower()
    assert "unavailable or invalid" in ans
    assert "current status:" in ans
    assert "verified changes since latest snapshot" not in ans


@requires_ask
def test_step47_ask_does_not_write_or_modify_snapshot(monkeypatch, tmp_path):
    import app as app_module
    # Dedicated sandbox so the global conftest isolation dir (created directly
    # under tmp_path) does not register as a stray write.
    sandbox = tmp_path / "snap_dir"
    sandbox.mkdir()
    p = _install_snapshot(monkeypatch, sandbox, _build_current_snapshot())
    before_bytes = p.read_bytes()
    before_mtime = p.stat().st_mtime_ns
    c = _client()
    c.post(_ASK_PATH, json={"question": "what changed since last snapshot?"})
    c.post(_ASK_PATH, json={"question": "summarize current changes"})
    assert p.read_bytes() == before_bytes, "ask must not modify the snapshot file"
    assert p.stat().st_mtime_ns == before_mtime, "ask must not rewrite the snapshot file"
    # The ask path created no new files in the snapshot's directory.
    assert [x.name for x in sandbox.iterdir()] == [p.name]


@requires_ask
@pytest.mark.parametrize("q", [
    "what changed since last snapshot and refresh status",
    "what changed since last snapshot and write a snapshot",
    "what changed since last snapshot and start trading",
])
def test_step47_forbidden_mixed_with_snapshot_phrasing_refused(q, monkeypatch, tmp_path):
    _install_snapshot(monkeypatch, tmp_path, _build_current_snapshot())
    c = _client()
    body = c.post(_ASK_PATH, json={"question": q}).json()
    assert body["refused"] is True
    assert body["safety_class"].startswith("FORBIDDEN")
    for field in _FORBIDDEN_RESPONSE_FIELDS:
        assert field not in body


@requires_ask
def test_step47_status_shape_unchanged_after_compare_ask(monkeypatch, tmp_path):
    _install_snapshot(monkeypatch, tmp_path, _build_current_snapshot())
    c = _client()
    before = c.get("/api/jarvis/status").json()
    c.post(_ASK_PATH, json={"question": "what changed since last snapshot?"})
    after = c.get("/api/jarvis/status").json()
    assert set(before) == set(after)
    assert len(after) == 24
    assert after["read_only"] is True


def test_step47_template_has_no_snapshot_or_refresh_control():
    low = (_REPO_ROOT / "templates" / "jarvis.html").read_text(encoding="utf-8").lower()
    assert "/api/jarvis/snapshot" not in low
    assert "/api/jarvis/refresh" not in low
    for tok in ("<button", "<form", "onclick", 'method="post"'):
        assert tok not in low


def test_step47_no_snapshot_or_refresh_endpoint():
    c = _client()
    assert c.post("/api/jarvis/snapshot").status_code == 404
    assert c.get("/api/jarvis/snapshot").status_code == 404
    assert c.post("/api/jarvis/refresh").status_code == 404
    assert c.get("/api/jarvis/refresh").status_code == 404
    src = (_REPO_ROOT / "app.py").read_text(encoding="utf-8")
    assert "/api/jarvis/snapshot" not in src
    assert "/api/jarvis/refresh" not in src
