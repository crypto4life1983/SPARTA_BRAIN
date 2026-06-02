"""Tests for the JARVIS Strategy Factory / Mission Flow panel (additive, display-only).

Coverage:
- the new Strategy Factory section + #pStrategyFlow panel render in the page
- all six internal views are present (Overview / Workflow / Pipeline /
  Combined View / Current Run / Strategy Board)
- the human workflow stages and machine pipeline stages render in order text
- the "You are here" marker and the five status-colour legend labels render
- the panel is display-only: no <form>, no inline on*-handlers, no fetch/XHR,
  and no order/broker/execution control affordances inside the block
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
    # back up to the opening div of the panel
    open_idx = body.rfind("<div", 0, start)
    # the panel is closed before the next jv-section divider ("Strategy Factory
    # Readiness"); slice up to that marker to capture the whole block.
    end = body.index("Strategy Factory Readiness", start)
    return body[open_idx:end]


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
    # six clickable tabs + six tab panels
    block = _strategy_flow_block(body)
    assert block.count('class="jv-sf-tab') == 6
    assert block.count('class="jv-sf-view') == 6


def test_workflow_stages_render_in_order():
    block = _strategy_flow_block(_page())
    stages = [
        "Idea Intake", "Research Review", "Candidate Creation", "Build Bundle",
        "Run Tests", "Generate Report", "Decision", "Commit / Archive / Promote",
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
        "Raw Data", "Data QA", "Dataset Freeze", "Strategy Engine", "Backtest",
        "Fees / Slippage", "OOS Validation", "Stress Test", "Risk Scoring",
        "Final Report", "Paper Trading Gate", "Micro-Live Gate",
    ]
    last = -1
    for s in stages:
        idx = block.find(s)
        assert idx != -1, f"missing pipeline stage: {s}"
        assert idx > last, f"pipeline stage out of order: {s}"
        last = idx


def test_combined_view_has_you_are_here_marker():
    block = _strategy_flow_block(_page())
    assert "You are here" in block
    # both lanes labelled in the combined view
    assert "Workflow &middot; human" in block
    assert "Pipeline &middot; machine" in block


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
    # no client-side execution / network affordances inside the block.
    # NB: the words "broker"/"trading" appear in READ-ONLY disclaimers ("controls
    # no broker, paper, or live execution"), so we forbid concrete control verbs
    # and network calls, not safety-disclaimer nouns.
    for forbidden in (
        "fetch(", "xmlhttprequest", "place_order", "submit_order",
        "execute_trade", "websocket", "eval(", "broker_login", "broker_control",
    ):
        assert forbidden not in block, f"forbidden affordance in panel: {forbidden}"


def test_strategy_flow_switcher_script_is_scoped_and_inert():
    body = _page()
    # the switcher targets only the panel and never fetches or mutates state
    assert 'getElementById(\'pStrategyFlow\')' in body
    # isolate the switcher script and confirm it has no network/exec calls
    marker = "Mission Flow: isolated, display-only sub-tab switcher"
    assert marker in body
    tail = body[body.index(marker):]
    script = tail[: tail.index("</script>") + len("</script>")].lower()
    for forbidden in ("fetch(", "xmlhttprequest", "eval(", "place_order",
                      "submit_order", "execute_trade"):
        assert forbidden not in script, f"switcher must not contain {forbidden}"


def test_status_api_unchanged_no_strategy_flow_keys():
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    data = client.get("/api/jarvis/status").json()
    # this UI is static; it must not have added any feed keys
    assert "strategy_flow" not in data


# --- truthful-state pins (state-accuracy patch) ----------------------------
# These guard against the panel ever again implying invented progress for the
# Crypto-D1 research candidate (no data fetched, no baseline, no passed backtest).

def test_no_invented_crypto_d1_backtest_pass():
    block = _strategy_flow_block(_page())
    # the old misleading board card claimed a passed Crypto-D1 backtest
    assert "Crypto-D1 Baseline" not in block
    assert 'Pipeline: Backtest &middot; <span style="color:var(--jv-ok)">Passed</span>' \
        not in block


def test_pipeline_oos_validation_not_active():
    block = _strategy_flow_block(_page())
    # OOS Validation must not be shown as the active stage for Crypto-D1
    assert ('is-active"><span class="ndot"></span>'
            '<span class="nlbl">OOS Validation') not in block
    # post-Bundle-21: the QA runtime tool is built, so Data QA is no longer the
    # "active / next" pipeline node -- it is a watch node awaiting operator data.
    assert ('is-active"><span class="ndot"></span>'
            '<span class="nlbl">Data QA') not in block
    assert ('is-watch"><span class="ndot"></span>'
            '<span class="nlbl">Data QA') in block
    # the stale "QA runtime tool next" framing must be gone from the panel
    assert "QA runtime tool next" not in block


def test_current_run_reflects_real_crypto_d1_state():
    block = _strategy_flow_block(_page())
    for token in (
        "Operator readiness / missing-items review",
        "Readiness gate complete; real-data intake not ready",
        "Complete (Bundle 21)",
        "NOT_READY_FOR_REAL_DATA",
        "16 listed",
        "None against real data",
        "Data fetched",
        "None yet",
        "WATCH / MIXED",
        "data/crypto_d1_research/",
    ):
        assert token in block, f"missing truthful Current Run token: {token}"
    # the stale Bundle-19-era framing must be gone
    for stale in ("Data-readiness / QA tooling", "Authorization gate complete"):
        assert stale not in block, f"stale Current Run token still present: {stale}"


def test_current_run_acknowledges_bundle22_checklist():
    block = _strategy_flow_block(_page())
    # Bundle 22 sits ALONGSIDE the Bundle 21 readiness gate, never relabelling it.
    assert "Complete (Bundle 21)" in block  # readiness gate label unchanged
    for token in (
        "Missing-items checklist",
        "Bundle 22",
        "16 items MISSING / PENDING",
    ):
        assert token in block, f"missing Bundle 22 checklist token: {token}"
    # safety state must not have moved
    assert "NOT_READY_FOR_REAL_DATA" in block
    assert "WATCH / MIXED" in block


def test_workflow_and_pipeline_acknowledge_bundle22_checklist():
    block = _strategy_flow_block(_page())
    # Workflow detail: 16 operator items tracked in the Bundle 22 checklist.
    assert "Bundle&nbsp;22 Operator Missing-Items Checklist" in block
    # Pipeline detail: checklist complete, source-agnostic (no source approved).
    assert "Bundle&nbsp;22 missing-items checklist is complete" in block
    assert "no source named or approved" in block
    # source-agnostic guarantee: no concrete venue named on the dashboard
    assert "Kraken" not in block


def test_strategy_board_crypto_d1_reflects_readiness_gate():
    block = _strategy_flow_block(_page())
    # the board card must carry the post-Bundle-21 truth, not the old "QA tooling next"
    assert "readiness gate complete" in block
    assert "16 operator items pending" in block
    assert "authorization complete, QA tooling next" not in block
    # Bundle 22 checklist acknowledged alongside the Bundle 21 gate
    assert "checklist (Bundle 22)" in block
    assert "16 items MISSING / PENDING" in block


def test_strategy_board_trued_to_registry_no_fake_pass():
    block = _strategy_flow_block(_page())
    # real registry candidate names appear; none asserts a passed/live status
    assert "Crypto-D1 Protocol" in block
    assert "Arbitrage Research Protocol" in block
    # board carries WATCH/IDEA/PARKED registry statuses, never a green pass led
    for status in ("WATCH", "IDEA", "PARKED"):
        assert status in block, f"missing registry status on board: {status}"
