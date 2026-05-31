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
def test_step38_trading_question_is_safe_and_translated(q):
    # Reconciled for JARVIS Trading Executive Translation v1: trading-status
    # questions now answer in research-framed executive language by default and
    # HIDE the raw posture flags; operator mode (on request) still exposes them.
    c = _client()
    r = c.post(_ASK_PATH, json={"question": q})
    assert r.status_code == 200
    body = r.json()
    assert body["refused"] is False, f"{q!r} must be answerable read-only"
    assert body["safety_class"] == "SAFE_INFO"
    ans = body["answer"].lower()
    # Executive default: safety phrasing + research framing, NO raw posture flags.
    assert "no live or paper trades" in ans
    assert "research" in ans
    for flag in ("read_only=true", "paper_ready=false", "live_ready=false",
                 "broker_control=false"):
        assert flag not in ans, f"{q!r} executive answer must hide {flag}"
    assert "trading_detail" in body["sources_used"]
    for field in _FORBIDDEN_RESPONSE_FIELDS:
        assert field not in body
    # Operator mode (on request) exposes the four posture flags + exact counts.
    op = c.post(_ASK_PATH, json={"question": q + " operator mode"}).json()
    assert op["refused"] is False and op["safety_class"] == "SAFE_INFO"
    olow = op["answer"].lower()
    assert "observation-only" in olow
    for flag in ("read_only=true", "paper_ready=false", "live_ready=false",
                 "broker_control=false"):
        assert flag in olow, f"{q!r} operator answer must expose {flag}"


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
def test_step41_natural_trading_question_is_translated(q):
    # Reconciled for JARVIS Trading Executive Translation v1: natural trading-
    # status phrasings answer in research-framed executive language by default
    # (no raw posture flags); operator mode still exposes the posture flags.
    c = _client()
    r = c.post(_ASK_PATH, json={"question": q})
    assert r.status_code == 200
    body = r.json()
    assert body["refused"] is False, f"{q!r} must be answerable read-only"
    assert body["safety_class"] == "SAFE_INFO"
    ans = body["answer"].lower()
    assert "no live or paper trades" in ans
    assert "research" in ans
    for flag in ("read_only=true", "paper_ready=false", "live_ready=false",
                 "broker_control=false"):
        assert flag not in ans, f"{q!r} executive answer must hide {flag}"
    assert "trading_detail" in body["sources_used"]
    for field in _FORBIDDEN_RESPONSE_FIELDS:
        assert field not in body
    # Operator mode (on request) exposes the four posture flags.
    op = c.post(_ASK_PATH, json={"question": q + " operator mode"}).json()
    assert op["refused"] is False and op["safety_class"] == "SAFE_INFO"
    olow = op["answer"].lower()
    for flag in ("read_only=true", "paper_ready=false", "live_ready=false",
                 "broker_control=false"):
        assert flag in olow, f"{q!r} operator answer must expose {flag}"


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
    assert len(after) == 28
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


# ==========================================================================
# JARVIS Conversational Intelligence v1 — natural read-only conversation.
# Greetings, "how are you", morning briefing, Strategy Factory status, SPARTA
# Brain status, and a last-24h trading recap must answer naturally (refused=
# false, SAFE_INFO) from the read-only status aggregate, WITHOUT inventing any
# trade performance and WITHOUT loosening any refusal, route, or storage guard.
# ==========================================================================

_CI_BANNED_PERF = ("profit", "pnl", "win rate", "return of", "% return",
                   "ready to trade", "validated", "approved", "made $", "earned")


@requires_ask
@pytest.mark.parametrize("q", [
    "hi",
    "hello",
    "hey jarvis",
    "good morning",
    "good evening",
])
def test_ci_greetings_return_natural_response(q):
    c = _client()
    r = c.post(_ASK_PATH, json={"question": q})
    assert r.status_code == 200
    body = r.json()
    assert body["refused"] is False, f"{q!r} greeting must be answered read-only"
    assert body["safety_class"] == "SAFE_INFO"
    ans = body["answer"].lower()
    # A natural greeting that orients the operator, not a robotic flag dump.
    assert ("hello" in ans or "good morning" in ans or "online" in ans)
    assert "read-only" in ans
    for field in _FORBIDDEN_RESPONSE_FIELDS:
        assert field not in body


@requires_ask
@pytest.mark.parametrize("q", [
    "how are you?",
    "how are you doing?",
    "how's it going?",
])
def test_ci_how_are_you_is_natural_status(q):
    c = _client()
    body = c.post(_ASK_PATH, json={"question": q}).json()
    assert body["refused"] is False
    assert body["safety_class"] == "SAFE_INFO"
    ans = body["answer"].lower()
    assert "online" in ans and "read-only" in ans
    # Grounded in the real commander snapshot, not invented.
    assert "commander" in ans
    assert "commander_snapshot" in body["sources_used"]


@requires_ask
@pytest.mark.parametrize("q", [
    "give me a morning briefing",
    "brief me",
    "morning briefing please",
])
def test_ci_morning_briefing_summarizes_readonly(q):
    c = _client()
    body = c.post(_ASK_PATH, json={"question": q}).json()
    assert body["refused"] is False
    assert body["safety_class"] == "SAFE_INFO"
    ans = body["answer"].lower()
    assert "briefing" in ans
    # Executive default: read-only trading posture in plain words, research
    # framing, and a next step — without raw posture flags or counts.
    assert "observation-only" in ans
    assert "no live or paper trades were executed" in ans
    assert "research" in ans
    # No invented performance.
    for banned in _CI_BANNED_PERF:
        assert banned not in ans, f"briefing must not invent {banned!r}"
    assert "commander_snapshot" in body["sources_used"]


@requires_ask
@pytest.mark.parametrize("q", [
    "what happened in trading last 24 hours?",
    "what happened with our trades?",
    "trading recap for the last 24 hours",
    "what happened with my trades yesterday?",
])
def test_ci_trading_24h_is_readonly_and_no_fake_pnl(q):
    # Reconciled for JARVIS Trading Executive Translation v1: the 24h recap now
    # answers in research-framed executive language by default (no raw posture
    # flags); operator mode still exposes posture flags + report names.
    c = _client()
    body = c.post(_ASK_PATH, json={"question": q}).json()
    assert body["refused"] is False, f"{q!r} must be answerable read-only"
    assert body["safety_class"] == "SAFE_INFO"
    ans = body["answer"].lower()
    # Must clearly state no live/paper trades and no realized performance.
    assert "no live or paper trades" in ans
    assert "research" in ans
    # Executive default hides raw posture flags.
    for flag in ("read_only=true", "paper_ready=false", "live_ready=false",
                 "broker_control=false"):
        assert flag not in ans, f"{q!r} executive recap must hide {flag}"
    # Must NOT invent any numeric / performance claim.
    for banned in _CI_BANNED_PERF:
        assert banned not in ans, f"trading recap must not invent {banned!r}"
    assert "trading_detail" in body["sources_used"]
    for field in _FORBIDDEN_RESPONSE_FIELDS:
        assert field not in body
    # Operator mode (on request) exposes posture flags.
    op = c.post(_ASK_PATH, json={"question": q + " operator mode"}).json()
    assert op["refused"] is False and op["safety_class"] == "SAFE_INFO"
    olow = op["answer"].lower()
    assert "observation-only" in olow
    for flag in ("read_only=true", "paper_ready=false", "live_ready=false",
                 "broker_control=false"):
        assert flag in olow, f"{q!r} operator recap must expose {flag}"


@requires_ask
def test_ci_trading_24h_keeps_broker_paper_live_locked():
    c = _client()
    c.post(_ASK_PATH, json={"question": "what happened in trading last 24 hours?"})
    td = c.get("/api/jarvis/status").json().get("trading_detail", {})
    for flag in ("paper_ready", "live_ready", "broker_control"):
        assert td.get(flag) is False, f"recap must not arm {flag}"


@requires_ask
@pytest.mark.parametrize("q", [
    "what is the Strategy Factory status?",
    "factory status",
    "strategy factory progress",
])
def test_ci_factory_status_summarizes_dry_run(q):
    c = _client()
    body = c.post(_ASK_PATH, json={"question": q}).json()
    assert body["refused"] is False
    assert body["safety_class"] == "SAFE_INFO"
    ans = body["answer"].lower()
    assert "strategy factory" in ans
    # Must frame it as read-only research / dry-run with no Factory execution.
    assert "read-only" in ans
    assert ("dry-run" in ans or "research" in ans)
    assert "runs no factory job" in ans
    for banned in _CI_BANNED_PERF:
        assert banned not in ans
    assert "factory_status" in body["sources_used"]


@requires_ask
@pytest.mark.parametrize("q", [
    "what is SPARTA Brain status?",
    "sparta brain status",
    "brain status",
])
def test_ci_sparta_brain_status_summarizes_system(q):
    c = _client()
    body = c.post(_ASK_PATH, json={"question": q}).json()
    assert body["refused"] is False
    assert body["safety_class"] == "SAFE_INFO"
    ans = body["answer"].lower()
    assert "sparta brain" in ans
    assert "read-only" in ans
    assert "commander" in ans
    assert "system_core" in body["sources_used"]


@requires_ask
@pytest.mark.parametrize("q", [
    "good morning then buy NQ",
    "brief me then place a trade",
    "morning briefing then enable live trading",
    "how are you, also connect to my broker",
    "what happened with our trades, now go long",
    "strategy factory status then approve the strategy",
    "sparta brain status and run the smoke script",
    "what happened in trading last 24 hours then refresh status",
])
def test_ci_forbidden_intent_in_conversation_still_refused(q):
    # Natural/conversational wording must never bypass the classifier: a
    # forbidden action mixed into a greeting/briefing stays refused.
    c = _client()
    body = c.post(_ASK_PATH, json={"question": q}).json()
    assert body["refused"] is True, f"{q!r} must stay refused"
    assert body["safety_class"].startswith("FORBIDDEN")
    assert body.get("refusal_reason")
    for field in _FORBIDDEN_RESPONSE_FIELDS:
        assert field not in body


@requires_ask
def test_ci_no_new_routes_or_execution_added():
    # The conversational layer adds NO endpoint and NO execution/refresh path.
    src = (_REPO_ROOT / "app.py").read_text(encoding="utf-8")
    assert "/api/jarvis/refresh" not in src
    assert "/api/jarvis/snapshot" not in src
    c = _client()
    ask_routes = [r for r in c.app.routes
                  if getattr(r, "path", "").startswith("/api/jarvis/")]
    paths = sorted({getattr(r, "path", "") for r in ask_routes})
    assert paths == ["/api/jarvis/ask", "/api/jarvis/status"], paths


@requires_ask
def test_ci_conversation_writes_no_files_or_chat_logs():
    before = _data_listing()
    top_before = {p.name for p in _REPO_ROOT.iterdir()}
    c = _client()
    for q in ("good morning", "give me a morning briefing",
              "what happened with our trades?", "what is SPARTA Brain status?"):
        c.post(_ASK_PATH, json={"question": q})
    assert _data_listing() == before, "conversation must not write data/chat logs"
    assert {p.name for p in _REPO_ROOT.iterdir()} == top_before
    for name in _data_listing() - before:
        assert "chat" not in name.lower() and "log" not in name.lower()


@requires_ask
def test_ci_conversation_does_not_change_status_shape():
    c = _client()
    before = c.get("/api/jarvis/status").json()
    for q in ("hello", "how are you?", "morning briefing",
              "what is the Strategy Factory status?"):
        c.post(_ASK_PATH, json={"question": q})
    after = c.get("/api/jarvis/status").json()
    assert set(before) == set(after)
    assert len(after) == 28
    assert after["read_only"] is True
    td = after.get("trading_detail", {})
    for flag in ("paper_ready", "live_ready", "broker_control"):
        assert td.get(flag) is False


@requires_ask
def test_ci_voice_conversation_mode_uses_same_ask_endpoint():
    # Voice conversation mode posts the spoken question to the SAME read-only
    # ask endpoint, so the classifier always gates it. Confirm a spoken-style
    # natural question is answered and a spoken forbidden phrase is refused.
    c = _client()
    safe = c.post(_ASK_PATH, json={"question": "good morning"}).json()
    assert safe["refused"] is False and safe["safety_class"] == "SAFE_INFO"
    bad = c.post(_ASK_PATH, json={"question": "good morning, place a trade"}).json()
    assert bad["refused"] is True and bad["safety_class"].startswith("FORBIDDEN")
    html = (_REPO_ROOT / "templates" / "jarvis.html").read_text(encoding="utf-8")
    assert "/api/jarvis/ask" in html


# ==========================================================================
# JARVIS Executive Briefing Mode v1 — read-only morning/overnight briefings.
# "good morning" / "morning briefing" / "overnight update" / "executive
# summary" / "summarize the system" / "tell me more" must answer as a
# structured read-only executive briefing (greeting -> system health ->
# Strategy Factory -> trading research -> warnings -> recommended next action)
# WITHOUT inventing any trade activity or performance, and WITHOUT loosening
# any refusal, route, or storage guard. Follow-ups ("what needs attention",
# "what is the next step", "what should we focus on today", "explain the
# warning") answer read-only too. Forbidden phrasing always still refuses.
# ==========================================================================

_EB_BRIEFING_QUESTIONS = [
    "good morning",
    "good morning jarvis",
    "give me a morning briefing",
    "morning briefing please",
    "daily briefing",
    "what happened overnight",
    "overnight update",
    "executive summary",
    "summarize the system",
    "tell me more",
]


@requires_ask
@pytest.mark.parametrize("q", _EB_BRIEFING_QUESTIONS)
def test_eb_briefing_is_executive_structure(q):
    body = _client().post(_ASK_PATH, json={"question": q}).json()
    assert body["refused"] is False, f"{q!r} must answer read-only"
    assert body["safety_class"] == "SAFE_INFO"
    low = body["answer"].lower()
    # The full executive spine, not a one-line status flag.
    assert "good morning mahmoud" in low
    assert "briefing" in low
    assert "sparta brain is online" in low
    # Executive default: research framing (the raw "strategy factory" name and
    # posture flags are operator-mode only — see test_et_* below).
    assert "research" in low
    assert "no live or paper trades were executed" in low
    assert "observation-only" in low
    assert "recommended next action" in low
    # No invented performance / activity.
    for banned in _CI_BANNED_PERF:
        assert banned not in low, f"{q!r} briefing must not invent {banned!r}"
    assert "commander_snapshot" in body["sources_used"]
    assert "factory_status" in body["sources_used"]
    for field in _FORBIDDEN_RESPONSE_FIELDS:
        assert field not in body


@requires_ask
def test_eb_greeting_good_morning_becomes_briefing():
    # "good morning" is upgraded from a robotic status line into a full briefing.
    body = _client().post(_ASK_PATH, json={"question": "good morning"}).json()
    assert body["refused"] is False and body["safety_class"] == "SAFE_INFO"
    assert "executive briefing" in body["answer"].lower()
    assert len(body["answer"]) > 200


@requires_ask
@pytest.mark.parametrize("q", ["what happened overnight", "overnight update"])
def test_eb_overnight_update_is_readonly_no_fake_trades(q):
    body = _client().post(_ASK_PATH, json={"question": q}).json()
    assert body["refused"] is False and body["safety_class"] == "SAFE_INFO"
    low = body["answer"].lower()
    assert "no live or paper trades were executed" in low
    assert "observation-only" in low
    # Executive default: no raw posture flags (those are operator-mode only).
    assert "paper_ready=false" not in low and "read_only=true" not in low
    for banned in _CI_BANNED_PERF:
        assert banned not in low, f"overnight update must not invent {banned!r}"


@requires_ask
def test_eb_briefing_keeps_trading_flags_locked():
    c = _client()
    c.post(_ASK_PATH, json={"question": "good morning"})
    td = c.get("/api/jarvis/status").json().get("trading_detail", {})
    for flag in ("paper_ready", "live_ready", "broker_control"):
        assert td.get(flag) is False, f"briefing must not arm {flag}"


@requires_ask
@pytest.mark.parametrize("q", [
    "what needs attention",
    "what needs attention now",
    "anything that needs attention?",
])
def test_eb_attention_lists_warnings_readonly(q):
    body = _client().post(_ASK_PATH, json={"question": q}).json()
    assert body["refused"] is False, f"{q!r} must answer read-only"
    assert body["safety_class"] == "SAFE_INFO"
    low = body["answer"].lower()
    assert "attention" in low
    assert "recommended next action" in low
    assert "authorizes no action" in low
    for banned in _CI_BANNED_PERF:
        assert banned not in low
    assert "commander_snapshot" in body["sources_used"]


@requires_ask
@pytest.mark.parametrize("q", [
    "what is the next step",
    "what should we focus on today",
    "what to focus on next",
])
def test_eb_followups_recommend_next_action(q):
    body = _client().post(_ASK_PATH, json={"question": q}).json()
    assert body["refused"] is False, f"{q!r} must answer read-only"
    assert body["safety_class"] == "SAFE_INFO"
    low = body["answer"].lower()
    assert "recommended focus" in low
    assert "observation-only" in low
    for banned in _CI_BANNED_PERF:
        assert banned not in low


@requires_ask
def test_eb_explain_warning_is_readonly_explanation():
    body = _client().post(_ASK_PATH, json={"question": "explain the warning"}).json()
    assert body["refused"] is False
    assert body["safety_class"] == "SAFE_EXPLAIN"
    low = body["answer"].lower()
    assert "warning" in low
    assert "authorizes no action" in low
    for banned in _CI_BANNED_PERF:
        assert banned not in low
    assert "commander_snapshot" in body["sources_used"]


@requires_ask
@pytest.mark.parametrize("q", [
    "good morning then buy NQ",
    "morning briefing then place a trade",
    "what happened overnight then enable live trading",
    "executive summary then run the smoke script",
    "summarize the system and commit the changes",
    "what is the next step, then approve the strategy",
    "what should we focus on today and connect to my broker",
    "tell me more then refresh status",
    "what needs attention then go long",
])
def test_eb_forbidden_intent_in_briefing_still_refused(q):
    # Executive-briefing phrasing must never smuggle a forbidden action past the
    # classifier; forbidden is matched FIRST, so these stay refused.
    body = _client().post(_ASK_PATH, json={"question": q}).json()
    assert body["refused"] is True, f"{q!r} must stay refused"
    assert body["safety_class"].startswith("FORBIDDEN")
    assert body.get("refusal_reason")
    for field in _FORBIDDEN_RESPONSE_FIELDS:
        assert field not in body


@requires_ask
def test_eb_no_new_routes_or_execution_added():
    src = (_REPO_ROOT / "app.py").read_text(encoding="utf-8")
    assert "/api/jarvis/refresh" not in src
    assert "/api/jarvis/snapshot" not in src
    c = _client()
    paths = sorted({getattr(r, "path", "") for r in c.app.routes
                    if getattr(r, "path", "").startswith("/api/jarvis/")})
    assert paths == ["/api/jarvis/ask", "/api/jarvis/status"], paths


@requires_ask
def test_eb_briefing_writes_no_files_or_chat_logs():
    before = _data_listing()
    top_before = {p.name for p in _REPO_ROOT.iterdir()}
    c = _client()
    for q in ("good morning", "what happened overnight", "executive summary",
              "what needs attention", "what is the next step",
              "explain the warning"):
        c.post(_ASK_PATH, json={"question": q})
    assert _data_listing() == before, "briefing must not write data/chat logs"
    assert {p.name for p in _REPO_ROOT.iterdir()} == top_before
    for name in _data_listing() - before:
        assert "chat" not in name.lower() and "log" not in name.lower()


@requires_ask
def test_eb_briefing_does_not_change_status_shape():
    c = _client()
    before = c.get("/api/jarvis/status").json()
    for q in ("good morning", "executive summary", "what needs attention",
              "what is the next step"):
        c.post(_ASK_PATH, json={"question": q})
    after = c.get("/api/jarvis/status").json()
    assert set(before) == set(after)
    assert len(after) == 28
    assert after["read_only"] is True
    td = after.get("trading_detail", {})
    for flag in ("paper_ready", "live_ready", "broker_control"):
        assert td.get(flag) is False


# ==========================================================================
# JARVIS Executive Translation Mode v1 — the briefing/status answer has two
# read-only modes. Executive mode (default) translates internal facts into
# customer/investor-friendly business language and HIDES raw implementation
# detail (exact counts, report names, raw warning text, posture flags).
# Operator mode (triggered by "operator mode" / "show technical details" /
# "diagnostics" / "exact counts") still EXPOSES the full technical detail.
# Neither mode invents trades or performance, and forbidden phrasing always
# still refuses.
# ==========================================================================

# Raw tokens that must appear ONLY in operator mode, never in executive mode.
_ET_RAW_TOKENS = (
    "read_only=true",
    "paper_ready=false",
    "live_ready=false",
    "broker_control=false",
    "committed reports",
    "candidate(s)",
    "warning(s)",
)

_ET_EXECUTIVE_TRIGGERS = [
    "good morning",
    "executive briefing",
    "morning briefing",
    "summarize the system",
    "what is the status",
]


@requires_ask
@pytest.mark.parametrize("q", _ET_EXECUTIVE_TRIGGERS)
def test_et_executive_mode_hides_raw_details(q):
    body = _client().post(_ASK_PATH, json={"question": q}).json()
    assert body["refused"] is False, f"{q!r} must answer read-only"
    assert body["safety_class"] == "SAFE_INFO"
    low = body["answer"].lower()
    # Customer/investor-friendly framing, no raw implementation detail.
    for tok in _ET_RAW_TOKENS:
        assert tok not in low, f"executive mode must hide raw token {tok!r}"
    assert "sparta brain is online" in low
    # Safety phrasing is preserved in plain words.
    assert "observation-only" in low
    assert "no live or paper trades were executed" in low
    for banned in _CI_BANNED_PERF:
        assert banned not in low, f"executive mode must not invent {banned!r}"


@requires_ask
@pytest.mark.parametrize("q", [
    "operator mode",
    "morning briefing, show technical details",
    "good morning, operator mode",
    "diagnostics",
    "give me the exact counts",
])
def test_et_operator_mode_exposes_raw_details(q):
    body = _client().post(_ASK_PATH, json={"question": q}).json()
    assert body["refused"] is False, f"{q!r} must answer read-only"
    assert body["safety_class"] == "SAFE_INFO"
    low = body["answer"].lower()
    assert "operator briefing" in low
    # Full technical detail is exposed: posture flags, raw counts, raw factory.
    assert "read_only=true" in low
    assert "paper_ready=false" in low and "live_ready=false" in low
    assert "research candidate(s)" in low
    assert "warning(s)" in low
    assert "strategy factory" in low


@requires_ask
@pytest.mark.parametrize("q", ["operator mode", "good morning, operator mode"])
def test_et_operator_mode_invents_no_trades_or_performance(q):
    body = _client().post(_ASK_PATH, json={"question": q}).json()
    low = body["answer"].lower()
    assert "no live or paper trades were executed" in low
    assert "observation-only" in low
    for banned in _CI_BANNED_PERF:
        assert banned not in low, f"operator mode must not invent {banned!r}"


@requires_ask
def test_et_executive_status_is_translated():
    body = _client().post(_ASK_PATH, json={"question": "what is the status"}).json()
    assert body["refused"] is False and body["safety_class"] == "SAFE_INFO"
    low = body["answer"].lower()
    for tok in _ET_RAW_TOKENS:
        assert tok not in low, f"executive status must hide {tok!r}"
    assert "observation-only" in low


@requires_ask
def test_et_operator_status_exposes_posture():
    body = _client().post(
        _ASK_PATH, json={"question": "what is the status, operator mode"}).json()
    assert body["refused"] is False and body["safety_class"] == "SAFE_INFO"
    low = body["answer"].lower()
    assert "operator detail" in low
    assert "read_only=true" in low and "broker_control=false" in low


@requires_ask
@pytest.mark.parametrize("q", [
    "operator mode",
    "show technical details",
    "show me the details",
    "diagnostics",
    "give me the exact counts",
])
def test_et_operator_triggers_classify_safe(q):
    body = _client().post(_ASK_PATH, json={"question": q}).json()
    assert body["refused"] is False, f"{q!r} operator trigger must be read-only"
    assert body["safety_class"] == "SAFE_INFO"


@requires_ask
@pytest.mark.parametrize("q", [
    "operator mode then buy NQ",
    "show technical details and commit the changes",
    "diagnostics then place a trade",
    "exact counts then enable live trading",
    "good morning, operator mode, then connect to my broker",
])
def test_et_forbidden_intent_in_operator_mode_still_refused(q):
    # Operator-mode phrasing must never smuggle a forbidden action: forbidden is
    # matched FIRST, so these stay refused.
    body = _client().post(_ASK_PATH, json={"question": q}).json()
    assert body["refused"] is True, f"{q!r} must stay refused"
    assert body["safety_class"].startswith("FORBIDDEN")
    assert body.get("refusal_reason")
    for field in _FORBIDDEN_RESPONSE_FIELDS:
        assert field not in body


@requires_ask
def test_et_modes_add_no_routes_and_write_nothing():
    src = (_REPO_ROOT / "app.py").read_text(encoding="utf-8")
    assert "/api/jarvis/refresh" not in src
    assert "/api/jarvis/snapshot" not in src
    before = _data_listing()
    top_before = {p.name for p in _REPO_ROOT.iterdir()}
    c = _client()
    paths = sorted({getattr(r, "path", "") for r in c.app.routes
                    if getattr(r, "path", "").startswith("/api/jarvis/")})
    assert paths == ["/api/jarvis/ask", "/api/jarvis/status"], paths
    for q in ("good morning", "operator mode", "what is the status",
              "morning briefing, show technical details", "diagnostics"):
        c.post(_ASK_PATH, json={"question": q})
    assert _data_listing() == before, "translation modes must not write files"
    assert {p.name for p in _REPO_ROOT.iterdir()} == top_before


# ==========================================================================
# JARVIS Chief of Staff Mode v1 — strategic, contextual, demo-ready answers.
# Strategic questions ("what should we work on today", "smartest next move",
# "what is the priority", "big picture", "where are we", "why does this
# matter", "are we ready to demo") return an advice-only structured read
# (situation -> what changed -> why it matters -> focus -> what not to do ->
# next action). Product-demo questions ("what is SPARTA Brain", "what is
# JARVIS") return a plain-language overview. Everything is read-only, invents
# no trades/performance, keeps operator mode, and forbidden phrasing refuses.
# ==========================================================================

_COS_STRATEGIC_QUESTIONS = [
    "what should we work on today",
    "what is the smartest next move",
    "what is the priority",
    "give me the big picture",
    "explain where we are",
    "why does this matter",
    "are we ready to demo",
]


@requires_ask
@pytest.mark.parametrize("q", _COS_STRATEGIC_QUESTIONS)
def test_cos_strategic_answer_is_structured_and_readonly(q):
    body = _client().post(_ASK_PATH, json={"question": q}).json()
    assert body["refused"] is False, f"{q!r} must answer read-only"
    assert body["safety_class"] in ("SAFE_INFO", "SAFE_EXPLAIN")
    low = body["answer"].lower()
    # The chief-of-staff spine.
    assert "chief-of-staff" in low
    assert "current situation" in low
    assert "what changed recently" in low
    assert "why it matters" in low
    assert "recommended focus" in low
    assert "what not to do" in low
    assert "one clear next action" in low
    # Advice only, never a command.
    assert "advice only" in low
    assert "authorizes no action" in low
    # Safety phrasing preserved; no invented performance.
    assert "observation-only" in low
    assert "no live or paper trades were executed" in low
    for banned in _CI_BANNED_PERF:
        assert banned not in low, f"{q!r} must not invent {banned!r}"
    assert "recommended_next_actions" in body["sources_used"]
    for field in _FORBIDDEN_RESPONSE_FIELDS:
        assert field not in body


@requires_ask
@pytest.mark.parametrize("q", [
    "what should we work on today",
    "what is the priority",
    "are we ready to demo",
])
def test_cos_recommendation_is_advice_not_command(q):
    # The recommendation never arms trading or authorizes execution.
    c = _client()
    body = c.post(_ASK_PATH, json={"question": q}).json()
    low = body["answer"].lower()
    assert "advice only" in low
    assert "do not enable paper or live trading" in low
    td = c.get("/api/jarvis/status").json().get("trading_detail", {})
    for flag in ("paper_ready", "live_ready", "broker_control"):
        assert td.get(flag) is False, f"chief-of-staff must not arm {flag}"


@requires_ask
@pytest.mark.parametrize("q", [
    "what is SPARTA Brain",
    "what is JARVIS",
    "describe SPARTA Brain to a customer",
    "what should I tell someone about SPARTA Brain",
])
def test_cos_demo_overview_describes_product_readonly(q):
    body = _client().post(_ASK_PATH, json={"question": q}).json()
    assert body["refused"] is False, f"{q!r} must answer read-only"
    low = body["answer"].lower()
    assert "ai command center" in low
    assert "jarvis" in low and ("voice interface" in low or "chief of staff" in low)
    assert "research engine" in low
    assert "research-only" in low
    assert "no live or paper trades were executed" in low
    for banned in _CI_BANNED_PERF:
        assert banned not in low, f"{q!r} demo must not invent {banned!r}"


@requires_ask
def test_cos_unknown_data_is_not_invented():
    # When the factory has no readable decision the answer says so rather than
    # fabricating a result, and still invents no performance.
    body = _client().post(
        _ASK_PATH, json={"question": "what is the smartest next move"}).json()
    low = body["answer"].lower()
    assert "research" in low
    for banned in _CI_BANNED_PERF:
        assert banned not in low
    # No fabricated strategy success language.
    for bad in ("strategy succeeded", "winning strategy", "profitable"):
        assert bad not in low


@requires_ask
@pytest.mark.parametrize("q", [
    "what should we work on today then buy NQ",
    "what is the priority, then place a trade",
    "big picture then enable live trading",
    "are we ready to demo and connect to my broker",
    "what is SPARTA Brain then run the smoke script",
    "smartest next move then commit the changes",
])
def test_cos_forbidden_intent_still_refused(q):
    body = _client().post(_ASK_PATH, json={"question": q}).json()
    assert body["refused"] is True, f"{q!r} must stay refused"
    assert body["safety_class"].startswith("FORBIDDEN")
    assert body.get("refusal_reason")
    for field in _FORBIDDEN_RESPONSE_FIELDS:
        assert field not in body


@requires_ask
@pytest.mark.parametrize("q", ["are we ready to sell", "should we sell now"])
def test_cos_sell_stays_forbidden_trading(q):
    # "sell" remains a forbidden trading token by design; product-readiness must
    # be phrased as "ready to demo / ship / launch" instead.
    body = _client().post(_ASK_PATH, json={"question": q}).json()
    assert body["refused"] is True
    assert body["safety_class"] == "FORBIDDEN_TRADING"


@requires_ask
def test_cos_operator_mode_still_works():
    # Operator mode is preserved alongside chief-of-staff mode.
    body = _client().post(_ASK_PATH, json={"question": "operator mode"}).json()
    assert body["refused"] is False and body["safety_class"] == "SAFE_INFO"
    low = body["answer"].lower()
    assert "operator briefing" in low
    assert "read_only=true" in low
    assert "research candidate(s)" in low


@requires_ask
def test_cos_adds_no_routes_and_writes_nothing():
    src = (_REPO_ROOT / "app.py").read_text(encoding="utf-8")
    assert "/api/jarvis/refresh" not in src
    assert "/api/jarvis/snapshot" not in src
    before = _data_listing()
    top_before = {p.name for p in _REPO_ROOT.iterdir()}
    c = _client()
    paths = sorted({getattr(r, "path", "") for r in c.app.routes
                    if getattr(r, "path", "").startswith("/api/jarvis/")})
    assert paths == ["/api/jarvis/ask", "/api/jarvis/status"], paths
    for q in ("what is the priority", "big picture", "what is SPARTA Brain",
              "are we ready to demo", "explain where we are"):
        c.post(_ASK_PATH, json={"question": q})
    assert _data_listing() == before, "chief-of-staff must not write files"
    assert {p.name for p in _REPO_ROOT.iterdir()} == top_before


@requires_ask
def test_cos_does_not_change_status_shape():
    c = _client()
    before = c.get("/api/jarvis/status").json()
    for q in ("what is the priority", "what is SPARTA Brain",
              "smartest next move", "are we ready to demo"):
        c.post(_ASK_PATH, json={"question": q})
    after = c.get("/api/jarvis/status").json()
    assert set(before) == set(after)
    assert len(after) == 28
    assert after["read_only"] is True
    td = after.get("trading_detail", {})
    for flag in ("paper_ready", "live_ready", "broker_control"):
        assert td.get(flag) is False


# ==========================================================================
# JARVIS Trading Executive Translation v1
# Natural trading-status and strategy-status questions answer in research-
# framed executive language by default (no raw posture flags / counts), while
# operator mode (on request) still exposes the four posture flags and exact
# counts. Both keep the trading-safety phrasing; both are equally read-only.
# Forbidden trading commands still refuse.
# ==========================================================================

_TET_TRADING_QUESTIONS = (
    "what is the trading status",
    "what's happening with trading",
    "trading update",
    "how is trading going",
    "what happened with trading",
    "what happened in trading",
    "how are our strategies doing",
    "what is the status of the trading bot",
)


@requires_ask
@pytest.mark.parametrize("q", _TET_TRADING_QUESTIONS)
def test_tet_trading_status_is_executive_by_default(q):
    c = _client()
    body = c.post(_ASK_PATH, json={"question": q}).json()
    assert body["refused"] is False, f"{q!r} must answer read-only"
    assert body["safety_class"] in ("SAFE_INFO", "SAFE_EXPLAIN")
    ans = body["answer"].lower()
    # Executive default: research framing + safety phrasing, NO raw posture flags.
    assert "research" in ans
    assert "no live or paper trades" in ans
    for flag in ("read_only=true", "paper_ready=false", "live_ready=false",
                 "broker_control=false"):
        assert flag not in ans, f"{q!r} executive answer must hide {flag}"
    assert "trading_detail" in body["sources_used"]


@requires_ask
@pytest.mark.parametrize("q", _TET_TRADING_QUESTIONS)
def test_tet_trading_status_invents_no_performance(q):
    c = _client()
    ans = c.post(_ASK_PATH, json={"question": q}).json()["answer"].lower()
    for banned in _CI_BANNED_PERF:
        assert banned not in ans, f"{q!r} must not invent {banned!r}"
    for fabricated in ("strategy succeeded", "winning strategy", "profitable",
                       "fills", "executed a trade"):
        assert fabricated not in ans, f"{q!r} must not fabricate {fabricated!r}"


@requires_ask
@pytest.mark.parametrize("q", [
    "what is the trading status operator mode",
    "trading update show technical details",
    "how are our strategies doing operator mode",
    "what is the status of the trading bot diagnostics",
])
def test_tet_operator_mode_exposes_posture(q):
    c = _client()
    body = c.post(_ASK_PATH, json={"question": q}).json()
    assert body["refused"] is False
    assert body["safety_class"] == "SAFE_INFO"
    low = body["answer"].lower()
    assert "observation-only" in low
    for flag in ("read_only=true", "paper_ready=false", "live_ready=false",
                 "broker_control=false"):
        assert flag in low, f"{q!r} operator answer must expose {flag}"
    # Operator detail still invents no performance.
    for banned in _CI_BANNED_PERF:
        assert banned not in low


@requires_ask
@pytest.mark.parametrize("q", [
    "what is the trading status then place a trade",
    "trading update and buy NQ",
    "how is trading going then enable live trading",
    "how are our strategies doing and connect to my broker",
    "what happened in trading then approve the strategy",
    "trading status operator mode then sell ES",
])
def test_tet_forbidden_trading_command_still_refuses(q):
    c = _client()
    body = c.post(_ASK_PATH, json={"question": q}).json()
    assert body["refused"] is True, f"{q!r} must refuse"
    assert body["safety_class"].startswith("FORBIDDEN")
    assert body.get("refusal_reason")
    for field in _FORBIDDEN_RESPONSE_FIELDS:
        assert field not in body


@requires_ask
def test_tet_strategy_status_classifies_safe():
    from jarvis_conversation_safety import classify_jarvis_question
    for q in ("how are our strategies doing", "strategy status",
              "strategies update", "how is our strategy doing"):
        out = classify_jarvis_question(q)
        assert out["refused"] is False, f"{q!r} should be a read-only safe question"
        assert out["safety_class"] in ("SAFE_INFO", "SAFE_EXPLAIN")


@requires_ask
def test_tet_keeps_trading_flags_locked_and_shape():
    c = _client()
    before = c.get("/api/jarvis/status").json()
    for q in _TET_TRADING_QUESTIONS:
        c.post(_ASK_PATH, json={"question": q})
    after = c.get("/api/jarvis/status").json()
    assert set(before) == set(after)
    assert len(after) == 28
    assert after["read_only"] is True
    td = after.get("trading_detail", {})
    for flag in ("paper_ready", "live_ready", "broker_control"):
        assert td.get(flag) is False


@requires_ask
def test_tet_adds_no_routes_and_writes_nothing():
    src = (_REPO_ROOT / "app.py").read_text(encoding="utf-8")
    assert "/api/jarvis/refresh" not in src
    assert "/api/jarvis/snapshot" not in src
    before = _data_listing()
    top_before = {p.name for p in _REPO_ROOT.iterdir()}
    c = _client()
    paths = sorted({getattr(r, "path", "") for r in c.app.routes
                    if getattr(r, "path", "").startswith("/api/jarvis/")})
    assert paths == ["/api/jarvis/ask", "/api/jarvis/status"], paths
    for q in _TET_TRADING_QUESTIONS:
        c.post(_ASK_PATH, json={"question": q})
    assert _data_listing() == before, "trading translation must not write files"
    assert {p.name for p in _REPO_ROOT.iterdir()} == top_before
