"""Tests for the JARVIS Autopilot Morning Report panel (read-only view layer).

Proves: JARVIS renders a SUCCESS report; renders a FAILED report (with errors);
handles a missing report ("No morning report generated yet."); the C10
closed/rejected status appears; an open C11 gate + its exact paste-text appears;
and NO paper/live/broker/order/trading capability or readiness claim appears."""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import jarvis_autopilot_morning_panel as panel  # noqa: E402


# --- fixtures --------------------------------------------------------------- #

def _success_report():
    return {
        "run_status": "SUCCESS",
        "last_run_time": "2026-06-16T05:00:45Z",
        "run_id": "overnight_20260616T050004Z",
        "tasks_attempted": ["nightly_integrity", "seed_brief_draft"],
        "tasks_completed": ["nightly_integrity", "seed_brief_draft"],
        "tasks_failed": [],
        "error_summary": [],
        "candidate_status": {
            "C10": {"family": "intraweek_calendar_seasonality_drift",
                    "status": "REJECTED_KEPT_ON_RECORD", "active": False,
                    "next_action": "NONE (closed, kept on record)"},
            "C11": {"family": "cross_asset_dispersion_reversion",
                    "status": "PROPOSED (proposal-only)", "active": False,
                    "next_action": "HUMAN_DECISION_C11_ADVANCE_TO_SPEC_OR_REJECT_PROPOSAL"},
        },
        "next_required_human_gate": {
            "candidate": "C11",
            "action": "HUMAN_DECISION_C11_ADVANCE_TO_SPEC_OR_REJECT_PROPOSAL",
            "approval_text_to_paste": "APPROVE_C11_ADVANCE_TO_CANDIDATE_SPEC",
            "reject_text_to_paste": "REJECT_C11_FAMILY_PROPOSAL"},
        "git_status_summary": {"branch": "master", "staged": 0, "modified": 0,
                               "untracked": 4400},
        "ahead_behind": {"ahead": 0, "behind": 0, "in_sync": True},
        "what_to_do_next": "Last run was success. The open decision is on C11.",
    }


def _failed_report():
    r = _success_report()
    r["run_status"] = "FAILED"
    r["tasks_completed"] = ["nightly_integrity"]
    r["tasks_failed"] = ["seed_brief_draft"]
    r["error_summary"] = ["seed_brief_draft: boom"]
    r["what_to_do_next"] = "The last run FAILED and stopped safely."
    return r


# --- SUCCESS ---------------------------------------------------------------- #

def test_renders_success_report():
    p = panel.build_autopilot_morning_panel(_success_report())
    assert p["available"] is True
    assert p["run_status"] == "SUCCESS"
    h = p["html"]
    assert 'data-run-status="SUCCESS"' in h
    assert "Run: SUCCESS" in h
    assert "2026-06-16T05:00:45Z" in h
    assert "nightly_integrity" in h
    assert "Tasks attempted" in h and "Tasks completed" in h
    assert "Git" in h and "branch master" in h
    assert panel.LATEST_MD_REL in h  # path to full report


# --- FAILED ----------------------------------------------------------------- #

def test_renders_failed_report_with_errors():
    p = panel.build_autopilot_morning_panel(_failed_report())
    assert p["run_status"] == "FAILED"
    h = p["html"]
    assert 'data-run-status="FAILED"' in h
    assert "Run: FAILED" in h
    assert "Tasks FAILED" in h
    assert "seed_brief_draft: boom" in h
    assert "jv-am-bad" in h  # failed status styling class


# --- missing report --------------------------------------------------------- #

def test_handles_missing_report():
    p = panel.build_autopilot_morning_panel(None)
    assert p["available"] is False
    assert p["run_status"] == "NO_REPORT"
    h = p["html"]
    assert "No morning report generated yet." in h
    assert 'data-run-status="NO_REPORT"' in h


def test_load_latest_report_missing_file_returns_none(tmp_path):
    assert panel.load_latest_report(tmp_path) is None


def test_load_latest_report_reads_json(tmp_path):
    d = tmp_path / "reports" / "autopilot_morning"
    d.mkdir(parents=True)
    (d / "latest.json").write_text(json.dumps(_success_report()),
                                   encoding="utf-8")
    rep = panel.load_latest_report(tmp_path)
    assert rep is not None and rep["run_status"] == "SUCCESS"
    p = panel.build_autopilot_morning_panel(rep)
    assert p["run_status"] == "SUCCESS"


# --- C10 closed / rejected -------------------------------------------------- #

def test_c10_closed_rejected_appears():
    p = panel.build_autopilot_morning_panel(_success_report())
    assert p["candidate_status"]["C10"]["status"] == "REJECTED_KEPT_ON_RECORD"
    h = p["html"]
    assert "REJECTED_KEPT_ON_RECORD" in h
    assert "intraweek_calendar_seasonality_drift" in h


# --- C11 open gate + paste text --------------------------------------------- #

def test_c11_open_gate_and_paste_text_appears():
    p = panel.build_autopilot_morning_panel(_success_report())
    g = p["next_human_gate"]
    assert g["candidate"] == "C11"
    assert g["approval_text_to_paste"] == "APPROVE_C11_ADVANCE_TO_CANDIDATE_SPEC"
    h = p["html"]
    assert "Next human decision" in h
    assert "HUMAN_DECISION_C11_ADVANCE_TO_SPEC_OR_REJECT_PROPOSAL" in h
    assert "APPROVE_C11_ADVANCE_TO_CANDIDATE_SPEC" in h
    assert "REJECT_C11_FAMILY_PROPOSAL" in h


def test_no_open_gate_shows_none():
    r = _success_report()
    r["next_required_human_gate"] = {"candidate": None, "action": "NONE",
                                     "approval_text_to_paste": None,
                                     "reject_text_to_paste": None}
    h = panel.build_autopilot_morning_panel(r)["html"]
    assert "None open." in h


# --- no paper/live/broker/order claim --------------------------------------- #

def test_no_paper_live_broker_order_claim_in_html():
    for rep in (_success_report(), _failed_report(), None):
        h = panel.build_autopilot_morning_panel(rep)["html"].lower()
        for banned in ("approved for paper", "approved for live",
                       "paper ready", "live ready", "ready for live",
                       "ready for paper", "profit guarantee", "place order",
                       "broker connected", "buy ", "sell "):
            assert banned not in h, banned
        assert "no paper/live-readiness claim" in h


def test_panel_module_has_no_execution_imports():
    src = (Path(panel.__file__)).read_text(encoding="utf-8")
    for banned in ("import ccxt", "from ccxt", "import requests",
                   "import binance", "import alpaca", "subprocess",
                   "place_order", "create_order", "os.system", "broker_login"):
        assert banned not in src, banned


def test_panel_flags_no_paper_live_readiness():
    for rep in (_success_report(), None):
        assert panel.build_autopilot_morning_panel(rep)[
            "no_paper_live_readiness_claim"] is True
