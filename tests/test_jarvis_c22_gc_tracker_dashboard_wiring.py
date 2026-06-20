"""Tests for the C22 Signum GC data-collection tracker wiring into the Jarvis morning
report + panel.

Proves the tracker section is surfaced in BOTH the morning-report markdown and the live
Jarvis panel HTML (report-present and no-report branches), that the wired tracker status
validates and stays research-only (no Signum/MCP/API/data-fetch/trading/scheduler/replay
capability), and that the two surface modules add no dangerous capability tokens for this
wiring."""
from __future__ import annotations

from pathlib import Path

import tools.sparta_autopilot_morning_report as mr
import jarvis_autopilot_morning_panel as panel
import sparta_commander.c22_signum_gc_data_collection_tracker_contract as trk

_GS = {"branch": "master", "staged": 0, "modified": 0, "untracked": 0, "clean": True}
_RUN = {"run_time": "t", "tasks_attempted": ["a"], "tasks_completed": ["a"],
        "tasks_failed": [], "tasks_skipped": [], "errors": [],
        "integrity_status": "INTACT", "explicit_status": None}
_CAND = {"C16": {"family": "x", "status": "REJECTED_KEPT_ON_RECORD", "active": False,
                 "next_action": "NONE (closed)"}}

_REPORT = mr.build_morning_report(_RUN, _GS, _CAND)
_MD = mr.render_markdown(_REPORT)
_PANEL = panel.build_autopilot_morning_panel(_REPORT)
_HTML = _PANEL["html"]


# ---- morning report surfaces the tracker -----------------------------------

def test_morning_report_has_tracker_section():
    assert "c22_gc_collection_tracker" in _REPORT
    s = _REPORT["c22_gc_collection_tracker"]
    assert trk.validate_collection_status(s)["valid"] is True
    assert "C22 Signum GC data-collection tracker" in _MD
    assert "HOLD_FOR_MORE_FROZEN_DATA_WINDOWS" in _MD
    # the live repo has at least the first window staged
    assert s["collected_windows"] >= 1
    assert s["required_windows"] == 20


# ---- panel (report + no-report) surfaces the tracker -----------------------

def test_panel_html_has_tracker_section():
    assert "c22_gc_collection_tracker" in _PANEL
    assert trk.validate_collection_status(_PANEL["c22_gc_collection_tracker"])["valid"]
    assert "C22 GC data-collection tracker" in _HTML
    assert _PANEL["c22_gc_collection_tracker"]["next_export_date"] in _HTML


def test_panel_no_report_still_shows_tracker():
    p = panel.build_autopilot_morning_panel(None)
    assert "c22_gc_collection_tracker" in p
    assert "C22 GC data-collection tracker" in p["html"]


# ---- the wired tracker stays research-only ---------------------------------

def test_wired_tracker_has_no_dangerous_capability():
    for surface in (_REPORT["c22_gc_collection_tracker"],
                    _PANEL["c22_gc_collection_tracker"]):
        for flag in ("connects_signum", "uses_mcp", "accesses_hyperliquid", "calls_api",
                     "fetches_data", "runs_replay", "builds_replay", "runs_labels",
                     "installs_scheduler", "triggers_scheduler", "places_orders",
                     "live_trading", "paper_trading", "modifies_c22_rules"):
            assert surface[flag] is False, flag
        assert surface["replay_locked"] is True
        assert surface["advances_nothing"] is True


# ---- the wiring added no scheduler/trading/fetch tokens to the surfaces -----

_FORBIDDEN_SURFACE_TOKENS = (
    "schtasks", "Register-ScheduledTask", "ScheduledTaskTrigger", "crontab",
    "schedule.every", "BackgroundScheduler", "BlockingScheduler",
    "import ccxt", "from ccxt", "import requests", "from requests",
    "place_order", "create_order", "api.binance", "MetaTrader",
)


def test_surfaces_add_no_scheduler_or_trading_code_for_tracker():
    for mod in (mr, panel, trk):
        src = Path(mod.__file__).read_text(encoding="utf-8")
        for tok in _FORBIDDEN_SURFACE_TOKENS:
            assert tok not in src, "%s: %s" % (Path(mod.__file__).name, tok)
    # the tracker contract is imported by both surfaces
    for mod in (mr, panel):
        src = Path(mod.__file__).read_text(encoding="utf-8")
        assert "c22_signum_gc_data_collection_tracker_contract" in src
