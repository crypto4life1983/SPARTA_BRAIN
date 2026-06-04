"""Bundle B — Strategy Factory readiness panels (read-only observation layer).

Covers the four additive ``/api/jarvis/status`` sections:
- ``factory_status``     (T1) — recent committed factory-report decisions,
- ``survival_ledger``    (T2) — pass/fail & survival aggregate,
- ``candidate_registry`` (T3) — research strategy candidates (NOT video assets),
- ``freshness_guard``    (T6) — live build HEAD vs current git HEAD.

Every assertion enforces the invariant: these panels READ only. They expose no
paper/live/broker affordance, fabricate no decision (missing -> UNKNOWN /
NOT_FOUND), and the status aggregate writes nothing.
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("fastapi")

import app as app_module

_REPO_ROOT = Path(__file__).resolve().parents[1]
_NEW_KEYS = ("factory_status", "survival_ledger", "candidate_registry",
             "freshness_guard", "strategy_factory_integration")


# --- status wiring --------------------------------------------------------

def test_status_exposes_four_readonly_panels():
    status = app_module.api_jarvis_status()
    # Presence-based, not an exact count: adding/removing unrelated panels must
    # not break this. Floor guard still fails loudly if the aggregate is empty.
    assert isinstance(status, dict)
    assert len(status) >= len(_NEW_KEYS)
    for key in _NEW_KEYS:
        assert key in status
        assert isinstance(status[key], dict)
        # every panel asserts its own read-only posture
        assert status[key].get("read_only") is True


def test_panels_never_enable_trading():
    status = app_module.api_jarvis_status()
    reg = status["candidate_registry"]
    assert reg["paper_ready"] is False
    assert reg["live_ready"] is False
    assert reg["broker_control"] is False
    assert reg["candidate_status"] == "RESEARCH_CANDIDATE_ONLY"


# --- T6 freshness guard ---------------------------------------------------

def test_freshness_fresh_when_heads_match():
    out = app_module._jarvis_freshness_guard(server_head="abc1234",
                                             current_head="abc1234")
    assert out["state"] == "fresh"
    assert out["stale"] is False
    assert out["read_only"] is True


def test_freshness_stale_when_heads_differ():
    out = app_module._jarvis_freshness_guard(server_head="abc1234",
                                             current_head="def5678")
    assert out["state"] == "stale"
    assert out["stale"] is True
    assert "restart" in out["detail"].lower()


def test_freshness_unknown_when_boot_head_missing(monkeypatch):
    # No recorded boot head (e.g. git unavailable at import) -> UNKNOWN, fail-safe.
    monkeypatch.setattr(app_module, "_JARVIS_SERVER_BOOT_HEAD", None)
    out = app_module._jarvis_freshness_guard(current_head="def5678")
    assert out["state"] == "unknown"
    assert out["stale"] is False


def test_boot_head_is_short_or_none():
    boot = app_module._JARVIS_SERVER_BOOT_HEAD
    assert boot is None or (isinstance(boot, str) and 0 < len(boot) <= 40)


# --- T1 decision extraction (fail-closed, never invented) -----------------

def test_decision_priority_match():
    out = app_module._jarvis_report_decision({"decision": "PARK_CANDIDATE"})
    assert out["decision"] == "PARK_CANDIDATE"
    assert out["field"] == "decision"


def test_decision_numbered_fallback():
    out = app_module._jarvis_report_decision({"8_verdict": "FAIL"})
    assert out["decision"] == "FAIL"
    assert out["field"] == "8_verdict"


def test_decision_suffix_fallback():
    out = app_module._jarvis_report_decision({"final_s26_verdict": "WATCH"})
    assert out["decision"] == "WATCH"
    assert out["field"] == "final_s26_verdict"


def test_decision_unknown_when_absent():
    out = app_module._jarvis_report_decision({"unrelated": "x"})
    assert out["decision"] is None
    assert out["field"] is None


def test_decision_handles_non_dict():
    assert app_module._jarvis_report_decision(["not", "a", "dict"]) == {
        "decision": None, "field": None}


# --- T1 factory status reads real committed reports -----------------------

def test_factory_status_reads_reports():
    out = app_module._jarvis_factory_status()
    assert out["read_only"] is True
    assert out["state"] in ("ready", "missing", "error")
    if out["state"] == "ready":
        assert out["report_count"] >= 1
        for r in out["latest_decisions"]:
            assert "name" in r and "decision" in r
            # a report with no decision field shows UNKNOWN, never invented
            assert isinstance(r["decision"], str)


# --- T2 survival ledger ---------------------------------------------------

def test_survival_ledger_shape():
    out = app_module._jarvis_survival_ledger()
    assert out["read_only"] is True
    assert out["state"] in ("ready", "not_found", "error")
    if out["state"] == "ready":
        assert isinstance(out["strategy_count"], int)
        assert isinstance(out["most_survivable"], list)
        assert isinstance(out["weakest"], list)


# --- T3 candidate registry is research-only, distinct from video assets ----

def test_candidate_registry_research_only():
    out = app_module._jarvis_candidate_registry()
    assert out["read_only"] is True
    assert out["paper_ready"] is False
    assert out["live_ready"] is False
    assert out["broker_control"] is False
    assert out["state"] in ("ready", "empty", "not_found", "error")
    if out["state"] == "ready":
        for c in out["candidates"]:
            assert c["deployment_status"] == "RESEARCH_ONLY"
            assert c["observation_tier"] in (
                "OBSERVED_SURVIVOR", "WEAK_CANDIDATE", "NO_EDGE_YET", "UNKNOWN")


# --- template exposes the panels but no control ---------------------------

def test_template_has_factory_panels_no_controls():
    body = (_REPO_ROOT / "templates" / "jarvis.html").read_text(encoding="utf-8")
    for pid in ("pFactoryReadiness", "pFactoryStatus", "pSurvivalLedger",
                "pCandidateRegistry", "pFreshness"):
        assert pid in body
    low = body.lower()
    assert "/api/jarvis/snapshot" not in low
    assert "/api/jarvis/refresh" not in low
    for tok in ("<button", "<form", "onclick", 'method="post"'):
        assert tok not in low
