"""Tests for the JARVIS Strategy Factory / Mission Flow panel (additive, display-only).

State target: Bundle 48 static sync. The panel is a read-only map of the
Strategy Factory backbone + fake-only lane + Crypto-D1 contract chain
(Bundles 42-48) being complete on paper, with the current gate
PAUSE_AND_OPERATOR_REVIEW_BEFORE_REAL_STRATEGY_INTAKE, the next required action
BUILD_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT, and real strategy
intake still blocked.

Coverage:
- the Strategy Factory section + #pStrategyFlow panel render in the page
- all six internal views are present (Overview / Workflow / Pipeline /
  Combined View / Current Run / Strategy Board)
- the human workflow stages and machine pipeline stages render in order
- the "You are here" badge is OWNED by the active card (no free-floating,
  page-centered marker) and points to the Operator Review gate
- the machine lane is trued to Bundle 48 (no stale "Crypto-D1 Intake
  Reconciliation - Next / not started"); the research-only dry-run preview
  contract is the next machine step
- the visible current stage / next action match the mission_flow_status backend
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

def test_bundle48_vocabulary_present():
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
        # Crypto-D1 contract chain (Bundles 42-48) complete on paper
        "Bundle 47",
        "Bundle 48",
        "Crypto-D1 Post-Boundary Research-Only Next-Step Contract",
        "Crypto-D1 Research-Only Dry-Run Preview Contract",
        "Real Data QA",
        "Baseline Backtest",
        # gate
        "PAUSE_AND_OPERATOR_REVIEW_BEFORE_REAL_STRATEGY_INTAKE",
        # next required action (research-only dry-run preview, to be built)
        "BUILD_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT",
    ):
        assert token in block, f"missing Bundle 48 token: {token}"


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
    # the gate id is still present, but only as a hidden tooltip/debug attribute
    assert "PAUSE_AND_OPERATOR_REVIEW_BEFORE_REAL_STRATEGY_INTAKE" in block
    # the active marker sits on the Operator Review node, OWNS the in-card
    # "You are here" badge, shows the clean human label "Current Review", and
    # carries the technical gate id in title/data-debug
    assert (
        'is-active" title="Gate: PAUSE_AND_OPERATOR_REVIEW_BEFORE_REAL_STRATEGY_INTAKE" '
        'data-debug="PAUSE_AND_OPERATOR_REVIEW_BEFORE_REAL_STRATEGY_INTAKE">'
        '<span class="jv-sf-here-in">&#x25C9; You are here</span>'
        '<span class="ndot"></span>'
        '<span class="nlbl">Operator Review Before Real Strategy Intake</span>'
        '<span class="nst">Current Review</span>'
    ) in block


def test_long_gate_id_not_rendered_inside_visible_status_pill():
    """The long technical gate id must never sit inside a visible .nst pill;
    it is allowed only in hidden title/data-debug attributes."""
    block = _strategy_flow_block(_page())
    gate = "PAUSE_AND_OPERATOR_REVIEW_BEFORE_REAL_STRATEGY_INTAKE"
    # find every status-pill body and confirm none contains the raw gate id
    for pill in re.findall(r'<span class="nst">(.*?)</span>', block):
        assert gate not in pill, f"raw gate id leaked into a visible pill: {pill!r}"
    # the clean human label is what the active card shows instead
    assert '<span class="nst">Current Review</span>' in block


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


def test_current_run_reflects_bundle48_state():
    block = _strategy_flow_block(_page())
    for token in (
        "Current gate",
        "PAUSE_AND_OPERATOR_REVIEW_BEFORE_REAL_STRATEGY_INTAKE",
        "Operator Review Before Real Strategy Intake",
        "Latest completed bundle",
        "Bundle 48",
        "Bundle 48 &middot; Crypto-D1 Post-Boundary Research-Only Next-Step Contract",
        "Bundle 48 post-boundary next-step contract complete; dry-run preview contract not yet built",
        "BUILD_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT",
        "Crypto-D1 Research-Only Dry-Run Preview Contract",
        "Crypto-D1 Intake Reconciliation",
    ):
        assert token in block, f"missing Bundle 48 Current Run token: {token}"
    # stale Bundle-47-as-latest Current Run framing must be gone
    for stale in (
        "Bundle 47 boundary contract complete; post-boundary contract not yet defined",
        "DEFINE_NEXT_RESEARCH_ONLY_CRYPTO_D1_POST_BOUNDARY_CONTRACT",
        "Bundle 47 &middot; Crypto-D1 Human-Approved Offline Acquisition Execution Boundary Contract",
        "Next &middot; to be defined",
    ):
        assert stale not in block, f"stale Current Run token still present: {stale}"
    # stale Bundle-40-era Current Run framing must be gone
    for stale in (
        "Fake Lane Closure complete; real intake not started",
        "OPERATOR_REVIEW_BEFORE_CRYPTO_D1_OR_REAL_STRATEGY_INTAKE",
        "Recommended next phase",
    ):
        assert stale not in block, f"stale Current Run token still present: {stale}"
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


# --- Block 80A: visual-QA contract (marker anchoring + truth sync) ----------

def test_active_card_owns_you_are_here_badge():
    """The 'You are here' badge is rendered INSIDE the active Operator Review
    card (in both the Workflow lane and the Combined View lane), so it visually
    points to that card rather than floating in the page center."""
    block = _strategy_flow_block(_page())
    owned = (
        'data-debug="PAUSE_AND_OPERATOR_REVIEW_BEFORE_REAL_STRATEGY_INTAKE">'
        '<span class="jv-sf-here-in">&#x25C9; You are here</span>'
    )
    # appears in the Workflow lane AND the Combined View lane
    assert block.count(owned) >= 2, "active card must own the in-card badge"


def test_no_floating_center_you_are_here_marker():
    """The old free-floating, page-centered 'You are here' pill is gone; only
    the in-card badge (.jv-sf-here-in) remains."""
    block = _strategy_flow_block(_page())
    # the page-centered wrapper that previously held the floating pill is gone
    assert "text-align:center;margin:2px 0 8px;" not in block
    # the standalone floating pill class (jv-sf-here, NOT the in-card
    # jv-sf-here-in) must not appear anywhere in the panel
    assert 'class="jv-sf-here"' not in block
    assert '<div class="jv-sf-here">' not in block


def test_machine_lane_truth_synced_to_bundle48():
    """The machine lane reflects the Crypto-D1 contract chain (Bundles 42-48)
    complete on paper, with Bundle 48 as the latest completed bundle and the
    research-only dry-run preview contract as the next machine step."""
    block = _strategy_flow_block(_page())
    for n in ("Bundle 42", "Bundle 43", "Bundle 44",
              "Bundle 45", "Bundle 46", "Bundle 47", "Bundle 48"):
        assert n in block, f"missing completed bundle marker: {n}"
    # Bundle 48 (post-boundary next-step) is complete; dry-run preview is next
    assert "Crypto-D1 Post-Boundary Research-Only Next-Step Contract" in block
    assert "Crypto-D1 Research-Only Dry-Run Preview Contract" in block
    assert "Next &middot; to be built" in block
    # Bundle 48 latest-completed status surfaced in accessible data attributes
    assert 'data-debug="BUNDLE_48_COMPLETE"' in block
    assert 'title="Latest completed bundle: Bundle 48"' in block
    # the stale Bundle-47-as-latest attributes must be gone
    assert 'data-debug="BUNDLE_47_COMPLETE"' not in block
    assert 'title="Latest completed bundle: Bundle 47"' not in block


def test_no_stale_reconciliation_next_not_started():
    """Crypto-D1 Intake Reconciliation must NOT still read 'Next / not started'
    now that backend latest_completed_bundle is Bundle 48 (it is COMPLETE)."""
    block = _strategy_flow_block(_page())
    assert (
        '<span class="nlbl">Crypto-D1 Intake Reconciliation</span>'
        '<span class="nst">Next &middot; not started</span>'
    ) not in block
    # no node anywhere in the panel should still be marked "Next · not started"
    assert "Next &middot; not started" not in block


def test_visible_current_stage_matches_mission_flow_backend():
    """The visible "you are here" anchor matches the backend's CURRENT human
    stage label. This pins only the STABLE part of the contract: the current
    human stage (Operator Review Before Real Strategy Intake) does not move as
    new research-only paper bundles are appended downstream. The exact
    latest-bundle counter is deliberately NOT asserted here because it advances
    as later bundles land; the static panel's bundle pins are covered by the
    dedicated truth-sync tests above.

    Skips (rather than errors) if the backend module is not importable, e.g.
    while it is mid-edit. A mid-edit backend can raise NameError (not just
    ImportError), so this catches any import-time exception."""
    try:
        from sparta_commander import (  # noqa: WPS433 - guarded backend import
            strategy_factory_mission_flow_status as mf,
        )
    except Exception as exc:  # noqa: BLE001 - backend may be broken mid-edit
        pytest.skip(f"mission_flow_status backend not importable: {exc!r}")
    block = _strategy_flow_block(_page())
    status = mf.get_mission_flow_status()
    current = [s for s in status["human_workflow"]
               if s["state"] == mf.STATE_CURRENT]
    assert len(current) == 1, "backend must have exactly one current stage"
    # the backend's single current human stage is the panel's "you are here"
    assert current[0]["label"] in block
    assert current[0]["label"] == "Operator Review Before Real Strategy Intake"


# --- Block 82: static fallback aligned to committed Bundle 48 backend truth --

def test_static_fallback_matches_bundle48_backend_truth():
    """The visible static dashboard fallback must match the committed backend
    truth at Block 81 / Bundle 48: latest_completed_bundle = Bundle 48, current
    stage = research-only dry-run preview contract required, next required
    action = BUILD_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT.

    Skips (rather than errors) if the backend module is not importable, e.g.
    while it is mid-edit (a mid-edit backend can raise NameError, not just
    ImportError), so this catches any import-time exception."""
    try:
        from sparta_commander import (  # noqa: WPS433 - guarded backend import
            strategy_factory_mission_flow_status as mf,
        )
    except Exception as exc:  # noqa: BLE001 - backend may be broken mid-edit
        pytest.skip(f"mission_flow_status backend not importable: {exc!r}")
    status = mf.get_mission_flow_status()
    assert status["latest_completed_bundle"] == (
        "Bundle 48 - Crypto-D1 Post-Boundary Research-Only Next-Step Contract"
    )
    assert status["current_stage"] == (
        "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT_REQUIRED"
    )
    assert status["next_required_action"] == (
        "BUILD_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT"
    )
    block = _strategy_flow_block(_page())
    # the visible static panel carries Bundle 48 as the latest completed bundle
    assert (
        "Bundle 48 &middot; Crypto-D1 Post-Boundary Research-Only Next-Step "
        "Contract"
    ) in block
    assert 'data-debug="BUNDLE_48_COMPLETE"' in block
    assert 'title="Latest completed bundle: Bundle 48"' in block
    # the visible next required action matches the backend exactly
    assert status["next_required_action"] in block
    # the next visible machine step is the research-only dry-run preview contract
    assert "Crypto-D1 Research-Only Dry-Run Preview Contract" in block
    assert "Next &middot; to be built" in block
    # no stale Bundle-47-as-latest framing leaks into the visible panel
    assert 'data-debug="BUNDLE_47_COMPLETE"' not in block
    assert "DEFINE_NEXT_RESEARCH_ONLY_CRYPTO_D1_POST_BOUNDARY_CONTRACT" not in block


def test_safety_disclaimers_still_present_in_panel():
    """The panel must still make the read-only posture explicit: no real data
    acquisition / fetch / inspection / QA / baseline / backtest / simulation /
    broker-exchange / paper-live / automation / runtime-registry-dashboard
    write is unlocked."""
    block = _strategy_flow_block(_page()).lower()
    for phrase in (
        "data acquisition",
        "data fetch",
        "data inspection",
        "qa",
        "baseline",
        "backtest",
        "simulation",
        "broker/exchange",
        "paper/live",
        "automation",
        "runtime/registry/dashboard",
    ):
        assert phrase in block, f"missing safety disclaimer phrase: {phrase}"
    assert "executes nothing" in block
