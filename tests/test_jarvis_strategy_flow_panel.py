"""Tests for the JARVIS Strategy Factory / Mission Flow panel (additive, display-only).

State target: Bundle 40 static sync. The panel is a read-only map of the
Strategy Factory backbone + fake-only lane being complete on paper, with the
current gate PAUSE_AND_OPERATOR_REVIEW_BEFORE_REAL_STRATEGY_INTAKE and real
strategy intake still blocked.

Coverage:
- the Strategy Factory section + #pStrategyFlow panel render in the page
- all six internal views are present (Overview / Workflow / Pipeline /
  Combined View / Current Run / Strategy Board)
- the Bundle 40 human workflow stages and machine pipeline stages render in order
- the "You are here" marker points to PAUSE_AND_OPERATOR_REVIEW_BEFORE_REAL_STRATEGY_INTAKE
- the stale Bundle-21/22 "Build Bundle / Operator readiness" active marker is gone
- locked/blocked gates are preserved (Real Strategy Intake, Real Data QA,
  Baseline Backtest, Paper Trading Gate, Micro-Live Gate)
- the panel is display-only: no <form>, no inline on*-handlers, no fetch/XHR,
  and no order/broker/upload/autopilot/execution control affordances
- GET /api/jarvis/status is unchanged by this UI (no new keys introduced here)

This panel adds NO backend behavior: it is static markup switched client-side.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

pytest.importorskip("fastapi")

_REPO_ROOT = Path(__file__).resolve().parents[1]


def _page() -> str:
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    r = client.get("/jarvis")
    assert r.status_code == 200
    return r.text


def _strategy_flow_block(body: str) -> str:
    """Return only the #pStrategyFlow panel markup, so 'forbidden affordance'
    assertions are scoped to the new block and never to the wider page."""
    start = body.index('id="pStrategyFlow"')
    open_idx = body.rfind("<div", 0, start)
    end = body.index("Strategy Factory Readiness", start)
    return body[open_idx:end]


# --- structural pins -------------------------------------------------------

def test_strategy_factory_section_and_panel_render():
    body = _page()
    assert "Strategy Factory" in body
    assert 'id="pStrategyFlow"' in body
    assert "Mission Flow" in body
    assert "DISPLAY ONLY" in body


def test_strategy_flow_has_all_six_views():
    body = _page()
    for label in (
        "Overview", "Workflow", "Pipeline",
        "Combined View", "Current Run", "Strategy Board",
    ):
        assert label in body, f"missing Strategy Factory view: {label}"
    block = _strategy_flow_block(body)
    assert block.count('class="jv-sf-tab') == 6
    assert block.count('class="jv-sf-view') == 6


# --- Bundle 40 vocabulary present ------------------------------------------

def test_bundle40_vocabulary_present():
    block = _strategy_flow_block(_page())
    for token in (
        # human lane
        "Backbone Build",
        "Fake Lane",
        "Operator Review Before Real Strategy Intake",
        "Real Strategy Intake",
        # machine lane
        "Strategy Factory Backbone",
        "Fake Dry Walk",
        "Fake Report Renderer",
        "Fake Lane Closure",
        "Crypto-D1 Intake Reconciliation",
        "Real Data QA",
        "Baseline Backtest",
        # gate
        "PAUSE_AND_OPERATOR_REVIEW_BEFORE_REAL_STRATEGY_INTAKE",
        # recommended next phase
        "OPERATOR_REVIEW_BEFORE_CRYPTO_D1_OR_REAL_STRATEGY_INTAKE",
    ):
        assert token in block, f"missing Bundle 40 token: {token}"


def test_workflow_stages_render_in_order():
    block = _strategy_flow_block(_page())
    stages = [
        "Idea Intake", "Research Review", "Candidate Creation",
        "Backbone Build", "Fake Lane",
        "Operator Review Before Real Strategy Intake", "Real Strategy Intake",
    ]
    last = -1
    for s in stages:
        idx = block.find(s)
        assert idx != -1, f"missing workflow stage: {s}"
        assert idx > last, f"workflow stage out of order: {s}"
        last = idx


def test_pipeline_stages_render_in_order():
    block = _strategy_flow_block(_page())
    stages = [
        "Strategy Factory Backbone", "Fake Dry Walk", "Fake Report Renderer",
        "Fake Lane Closure", "Crypto-D1 Intake Reconciliation", "Real Data QA",
        "Baseline Backtest", "Paper Trading Gate", "Micro-Live Gate",
    ]
    last = -1
    for s in stages:
        idx = block.find(s)
        assert idx != -1, f"missing pipeline stage: {s}"
        assert idx > last, f"pipeline stage out of order: {s}"
        last = idx


# --- "You are here" marker location ----------------------------------------

def test_you_are_here_points_to_operator_review_gate():
    block = _strategy_flow_block(_page())
    assert "You are here" in block
    assert "PAUSE_AND_OPERATOR_REVIEW_BEFORE_REAL_STRATEGY_INTAKE" in block
    # the active marker sits on the Operator Review node and names the gate
    assert (
        'is-active"><span class="ndot"></span>'
        '<span class="nlbl">Operator Review Before Real Strategy Intake</span>'
        '<span class="nst">Current &middot; You are here &middot; '
        'PAUSE_AND_OPERATOR_REVIEW_BEFORE_REAL_STRATEGY_INTAKE'
    ) in block


def test_combined_view_lane_tags_present():
    block = _strategy_flow_block(_page())
    assert "Workflow &middot; human" in block
    assert "Pipeline &middot; machine" in block


# --- stale Bundle-21/22 active marker is gone ------------------------------

def test_stale_build_bundle_active_marker_gone():
    block = _strategy_flow_block(_page())
    # "Build Bundle" must not be the active "You are here" stage anymore
    assert (
        'is-active"><span class="ndot"></span>'
        '<span class="nlbl">Build Bundle'
    ) not in block
    # the old Crypto-D1 readiness framing must be gone from the panel
    assert "Operator readiness / missing-items review" not in block
    assert "Bundle 22" not in block
    assert "Bundle&nbsp;22" not in block
    assert "missing-items checklist" not in block.lower()


# --- locked / blocked gates preserved --------------------------------------

def test_blocked_and_locked_gates_preserved():
    block = _strategy_flow_block(_page())
    # Real Strategy Intake is blocked / not started
    assert (
        'is-blocked"><span class="ndot"></span>'
        '<span class="nlbl">Real Strategy Intake</span>'
        '<span class="nst">Blocked &middot; not started'
    ) in block
    # Real Data QA blocked
    assert (
        'is-blocked"><span class="ndot"></span>'
        '<span class="nlbl">Real Data QA</span><span class="nst">Blocked'
    ) in block
    # Baseline Backtest blocked
    assert (
        'is-blocked"><span class="ndot"></span>'
        '<span class="nlbl">Baseline Backtest</span><span class="nst">Blocked'
    ) in block
    # Paper Trading Gate locked
    assert (
        '<span class="nlbl">Paper Trading Gate</span>'
        '<span class="nst">Locked &middot; human approval required'
    ) in block
    # Micro-Live Gate locked
    assert (
        '<span class="nlbl">Micro-Live Gate</span>'
        '<span class="nst">Locked &middot; never automated'
    ) in block


# --- legend + display-only safety ------------------------------------------

def test_status_colour_legend_present():
    block = _strategy_flow_block(_page())
    for label in (
        "Not started", "Active", "Complete / passed",
        "Watch / waiting", "Blocked / failed",
    ):
        assert label in block, f"missing legend label: {label}"


def test_strategy_flow_block_is_display_only():
    block = _strategy_flow_block(_page()).lower()
    # no real form controls / submit surface inside the block
    for tag in ("<form", "<button", "<input", "<select", "<textarea"):
        assert tag not in block, f"display-only block must not contain {tag}"
    # no inline event handlers (handlers live in an isolated, scoped script)
    assert not re.search(r"on\w+\s*=", block), "no inline on*-handlers allowed"
    # no client-side execution / network / control affordances inside the block.
    # NB: nouns like "broker"/"trading"/"live"/"paper" appear in READ-ONLY
    # disclaimers, so we forbid concrete control verbs / surfaces, not nouns.
    for forbidden in (
        "fetch(", "xmlhttprequest", "place_order", "submit_order",
        "execute_trade", "websocket", "eval(", "broker_login",
        "broker_control", "autopilot", "upload(", "deploy(",
        "enable_live", "go_live",
    ):
        assert forbidden not in block, f"forbidden affordance in panel: {forbidden}"


def test_strategy_flow_switcher_script_is_scoped_and_inert():
    body = _page()
    # the switcher targets only the panel and never fetches or mutates state
    assert "getElementById('pStrategyFlow')" in body
    marker = "Mission Flow: isolated, display-only sub-tab switcher"
    assert marker in body
    tail = body[body.index(marker):]
    script = tail[: tail.index("</script>") + len("</script>")].lower()
    for forbidden in ("fetch(", "xmlhttprequest", "eval(", "place_order",
                      "submit_order", "execute_trade"):
        assert forbidden not in script, f"switcher must not contain {forbidden}"


# --- backend status API unchanged by this static UI ------------------------

def test_status_api_unchanged_no_strategy_flow_keys():
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    data = client.get("/api/jarvis/status").json()
    assert "strategy_flow" not in data


# --- truthful-state pins ----------------------------------------------------

def test_no_invented_backtest_pass():
    block = _strategy_flow_block(_page())
    # the panel must never claim a passed/green baseline or backtest
    assert "Crypto-D1 Baseline" not in block
    assert 'Pipeline: Backtest &middot; <span style="color:var(--jv-ok)">Passed</span>' \
        not in block
    # the removed live-baseline re-label JS must not resurface in the panel
    assert "V002 baseline" not in block
    assert "(V002 baseline)" not in block


def test_current_run_reflects_bundle40_state():
    block = _strategy_flow_block(_page())
    for token in (
        "Current gate",
        "PAUSE_AND_OPERATOR_REVIEW_BEFORE_REAL_STRATEGY_INTAKE",
        "Operator Review Before Real Strategy Intake",
        "Fake Lane Closure complete; real intake not started",
        "OPERATOR_REVIEW_BEFORE_CRYPTO_D1_OR_REAL_STRATEGY_INTAKE",
        "Crypto-D1 Intake Reconciliation",
    ):
        assert token in block, f"missing Bundle 40 Current Run token: {token}"
    # stale Crypto-D1 readiness-era tokens must be gone
    for stale in ("NOT_READY_FOR_REAL_DATA", "QA_WARN on V002",
                  "readiness gate", "9 COMPLETE", "7 MISSING"):
        assert stale not in block, f"stale Current Run token still present: {stale}"


def test_strategy_board_trued_to_registry_no_fake_pass():
    block = _strategy_flow_block(_page())
    # real registry candidate names appear; none asserts a passed/live status
    assert "Crypto-D1 Protocol" in block
    assert "Arbitrage Research Protocol" in block
    for status in ("WATCH", "IDEA", "PARKED"):
        assert status in block, f"missing registry status on board: {status}"
