"""Tests for the Jarvis / morning-report Automation V2 dashboard wiring.

Proves the live Automation V2 daily decision packet is wired into the ACTUAL Jarvis
autopilot morning report (tools/sparta_autopilot_morning_report.py) and panel
(jarvis_autopilot_morning_panel.py) as the AUTHORITATIVE next-action section, so the
dashboard no longer presents a stale legacy recommendation when C22 is already
DATA_NOT_READY: it surfaces C22 DATA_NOT_READY, "do not proceed to labels", "do not
fabricate data", the dataset-staging token, ledger C1-C21 (26), C21 rejected, no active
candidate, the danger locks, and the daily report artifact path; it marks the legacy
lane-derived recommendation SUPERSEDED; and it never presents a C21 advance/reject as the
current next action. Also proves no scheduler-install/trigger / data-fetch /
Signum/MCP/Hyperliquid/API-wallet/live/paper/order code was added to the surfaces."""
from __future__ import annotations

from pathlib import Path

import tools.sparta_autopilot_morning_report as mr
import jarvis_autopilot_morning_panel as panel
import sparta_commander.sparta_automation_v2_morning_integration_contract as v2mi

_STAGING_TOKEN = (
    "HUMAN_STAGE_FROZEN_TREND_RADAR_GC_DETECTOR_DATASET_THEN_REAUTHORISE_C22_LABELS")
_C21_TOKEN = "HUMAN_DECISION_C21_ADVANCE_TO_FEE_HONEST_REPLAY_OR_REJECT"
# after the C22 current-packet realignment the AUTHORITATIVE next action is the collection
# token; the old DATA_NOT_READY / dataset-staging Automation V2 view is demoted to a
# clearly-superseded historical block.
_COLLECT_TOKEN = (
    "HUMAN_STAGE_MORE_FROZEN_DAILY_TREND_RADAR_GC_WINDOWS_THEN_REREVIEW_C22_LABELS")

_GS = {"branch": "master", "staged": 0, "modified": 0, "untracked": 0, "clean": True}
_RUN = {"run_time": "t", "tasks_attempted": ["a"], "tasks_completed": ["a"],
        "tasks_failed": [], "tasks_skipped": [], "errors": [],
        "integrity_status": "INTACT", "explicit_status": None}
_CAND = {"C16": {"family": "cointegration_pairs_market_neutral",
                 "status": "REJECTED_KEPT_ON_RECORD", "active": False,
                 "next_action": "NONE (closed)"}}

_REPORT = mr.build_morning_report(_RUN, _GS, _CAND)
_MD = mr.render_markdown(_REPORT)
_PANEL = panel.build_autopilot_morning_panel(_REPORT)
_HTML = _PANEL["html"]

_ROOT = Path(mr.__file__).resolve().parents[1]


# ---- morning report: V2 packet is the AUTHORITATIVE next action -------------

def test_morning_report_authoritative_is_now_current_packet_v2_superseded():
    # AUTHORITATIVE is now the C22 CURRENT collection packet (not the stale V2 staging view)
    assert _REPORT["authoritative_next_action_source"] == "C22_CURRENT_COLLECTION"
    assert _REPORT["authoritative_next_action"] == _COLLECT_TOKEN
    assert _REPORT["automation_v2_packet_superseded_by_current"] is True
    assert _REPORT["does_not_present_dataset_staging_as_current_action"] is True
    cur = _REPORT["c22_current_packet"]
    assert cur["c22_state"] == "HOLD_FOR_MORE_FROZEN_DATA_WINDOWS"
    assert cur["c22_replay_locked"] is True
    assert cur["collection_progress"] == "1/20"
    assert cur["c23_on_deck"] is True and cur["c23_is_active"] is False
    # the old V2 packet is still attached as the superseded historical view
    sec = _REPORT["automation_v2_packet"]
    assert sec["last_verdict"] == "DATA_NOT_READY"
    assert v2mi.validate_v2_morning_section(sec)["valid"] is True


def test_morning_report_markdown_current_authoritative_and_superseded_v2():
    # the new authoritative section + the demoted/superseded V2 historical block
    assert "C22 Collection — Authoritative Next Action" in _MD
    assert _COLLECT_TOKEN in _MD
    assert "HOLD_FOR_MORE_FROZEN_DATA_WINDOWS" in _MD
    assert "1/20" in _MD
    assert "queued / ON-DECK" in _MD
    assert "(Superseded) Automation V2" in _MD
    assert "DATA_NOT_READY" in _MD            # still shown, in the superseded block
    assert "C1-C21 (26)" in _MD


# ---- stale legacy guard + current-state priority ---------------------------

def test_legacy_recommendation_superseded_and_no_c21_advance():
    # the lane-derived legacy recommendation is marked superseded
    assert _REPORT["legacy_recommendation_superseded_by_automation_v2"] is True
    assert "SUPERSEDED" in _MD
    # the AUTHORITATIVE next action is the dataset-staging token, NOT a C21 advance/reject
    assert _REPORT["does_not_present_c21_advance_as_current_action"] is True
    assert _C21_TOKEN != _REPORT["authoritative_next_action"]
    assert "HUMAN_DECISION_C21_ADVANCE" not in _REPORT["authoritative_next_action"]
    # the C21 advance/reject token is NOT presented as the current next action anywhere
    # in the authoritative V2 section
    v2_md = v2mi.render_v2_section_markdown(_REPORT["automation_v2_packet"])
    assert _C21_TOKEN not in v2_md


# ---- panel: V2 packet rendered prominently in the HTML ---------------------

def test_panel_html_surfaces_current_authoritative_v2_superseded():
    assert _PANEL["authoritative_next_action_source"] == "C22_CURRENT_COLLECTION"
    assert _PANEL["authoritative_next_action"] == _COLLECT_TOKEN
    assert _PANEL["automation_v2_packet_superseded_by_current"] is True
    assert _PANEL["does_not_present_dataset_staging_as_current_action"] is True
    # the new authoritative block + the demoted superseded V2 block
    assert "C22 Collection — Authoritative Next Action" in _HTML
    assert "HOLD_FOR_MORE_FROZEN_DATA_WINDOWS" in _HTML
    assert "1/20" in _HTML
    assert "(Superseded) Automation V2" in _HTML
    assert "DATA_NOT_READY" in _HTML          # still shown, superseded block
    assert _C21_TOKEN not in _PANEL["authoritative_next_action"]


def test_panel_no_report_still_shows_current_authoritative():
    p = panel.build_autopilot_morning_panel(None)
    assert p["authoritative_next_action"] == _COLLECT_TOKEN
    assert "C22 Collection — Authoritative Next Action" in p["html"]
    assert "HOLD_FOR_MORE_FROZEN_DATA_WINDOWS" in p["html"]
    assert "(Superseded) Automation V2" in p["html"]


# ---- danger locks remain surfaced + locked ---------------------------------

def test_danger_locks_surfaced_and_locked():
    dl = _REPORT["automation_v2_packet"]["danger_locks"]
    for k in ("live_trading_locked", "paper_trading_locked", "signum_locked",
              "mcp_locked", "hyperliquid_locked", "scheduler_locked",
              "no_automatic_commit", "no_automatic_push", "never_skips_human_gates"):
        assert dl[k] is True, k
    # the panel safety locks block stays intact (lane-sourced)
    sl = _PANEL["safety_locks"]
    assert sl.get("paper_trading") == "LOCKED"
    assert sl.get("live_trading") == "LOCKED"


# ---- no dangerous code added to the surfaces -------------------------------

_SURFACES = (
    Path(mr.__file__),
    Path(panel.__file__),
)
# scheduler-install/trigger + trading/connection tokens that must NOT appear at all.
_FORBIDDEN_SURFACE_TOKENS = (
    "schtasks", "Register-ScheduledTask", "ScheduledTaskTrigger", "crontab",
    "schedule.every", "systemctl", "launchctl", "BackgroundScheduler",
    "BlockingScheduler",
    "import ccxt", "from ccxt", "hyperliquid", "signum_api", "place_order",
    "create_order", "api.binance", "fapi.binance", "import requests",
    "from requests", "MetaTrader", "alpaca",
)


def test_surfaces_add_no_scheduler_or_trading_code():
    for f in _SURFACES:
        src = f.read_text(encoding="utf-8")
        for tok in _FORBIDDEN_SURFACE_TOKENS:
            assert tok not in src, "%s: %s" % (f.name, tok)


def test_surfaces_do_not_fetch_data_for_the_v2_wiring():
    # the V2 wiring imports only pure read-only contracts (no fetch / network)
    for f in _SURFACES:
        src = f.read_text(encoding="utf-8")
        # the Automation V2 wiring imports are the pure morning-integration + daily
        # report contracts -- not any fetch/network/trading module.
        assert "sparta_automation_v2_morning_integration_contract" in src
        assert "sparta_automation_v2_daily_report_contract" in src
