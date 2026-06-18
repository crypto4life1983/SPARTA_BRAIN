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


# --- Safe Research Autopilot v1 planner output in the JARVIS panel ---------- #

def test_panel_surfaces_autopilot_plan_recommendation():
    rep = _success_report()
    rep["autopilot_plan"] = {
        "next_safe_action": "BUILD_NEXT_CANDIDATE_FAMILY_PROPOSAL",
        "would_auto_advance": True, "is_hard_stop": False,
        "stopped_before": None, "requires_human_approval": False,
        "recommended_token": "BUILD_NEXT_CANDIDATE_FAMILY_PROPOSAL_ONLY",
        "reason": "no active candidate; recommend opening next proposal",
        "planner_is_read_only": True, "planner_executes_nothing": True,
    }
    p = panel.build_autopilot_morning_panel(rep)
    assert p["autopilot_plan"]["next_safe_action"] == (
        "BUILD_NEXT_CANDIDATE_FAMILY_PROPOSAL")
    html = p["html"]
    assert "Safe Research Autopilot" in html
    assert "BUILD_NEXT_CANDIDATE_FAMILY_PROPOSAL" in html
    assert "executes nothing" in html


def test_panel_surfaces_autopilot_hard_stop_before_labels():
    rep = _success_report()
    rep["autopilot_plan"] = {
        "next_safe_action": "STOP_BEFORE_REAL_CANDLE_LABELS",
        "would_auto_advance": False, "is_hard_stop": True,
        "stopped_before": "real_candle_labels",
        "requires_human_approval": True,
        "recommended_token":
            "HUMAN_DECISION_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT",
        "reason": "detector dry-run ready; next gate is real-candle labels",
        "planner_is_read_only": True, "planner_executes_nothing": True,
    }
    html = panel.build_autopilot_morning_panel(rep)["html"]
    assert "Hard-stops before: real_candle_labels" in html
    assert "HUMAN_DECISION_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT" in html


def test_missing_report_panel_has_empty_autopilot_plan():
    p = panel.build_autopilot_morning_panel(None)
    assert p["autopilot_plan"] == {}


# --- C16 / ledger-21 / automation-readiness / safety locks alignment -------- #

def test_panel_shows_c16_complete_and_ledger_22():
    p = panel.build_autopilot_morning_panel(_success_report())
    ar = p["automation_readiness"]
    assert ar["c16_lifecycle_complete"] is True
    assert ar["rejected_ledger_count"] == 22
    h = p["html"]
    assert "ACTIVE CANDIDATE" in h
    assert "22" in h


def test_panel_shows_c18_active_at_proposal_gate():
    p = panel.build_autopilot_morning_panel(_success_report())
    ar = p["automation_readiness"]
    assert ar["active_candidate"] == "C18"
    assert ar["open_candidate_gate"] is True
    assert ar["next_required_action"] == (
        "HUMAN_DECISION_C18_ADVANCE_TO_CANDIDATE_SPEC_OR_REJECT")
    assert ar["section13_recommendation_when_clean"] == "RECOMMEND_GATE_DECISION"
    assert ar["section14_present"] is True
    assert ar["surfaces_agree"] is True
    assert ar["next_is_new_candidate"] is False
    assert ar["next_is_automation_readiness"] is False
    assert ar["active_candidate_verdict"] == "C18_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW"
    assert ar["active_candidate_timeframe"] == "H4"
    assert ar["last_rejected_candidate"] == "C17"
    h = p["html"]
    assert "HUMAN_DECISION_C18_ADVANCE_TO_CANDIDATE_SPEC_OR_REJECT" in h
    assert "ACTIVE CANDIDATE" in h
    assert "C18_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW" in h
    assert "H4 market-structure" in h
    assert "exact system" in h          # honesty disclosure rendered
    assert "C17_REJECTED_AT_FEE_HONEST_REPLAY" in h   # C17 still shown as last rejected


def test_panel_human_gate_workflow_c18_open_gate():
    p = panel.build_autopilot_morning_panel(_success_report())
    w = p["human_gate_workflow"]
    assert w["available"] is True
    assert w["has_open_human_gate"] is True
    assert w["active_candidate"] == "C18"
    assert w["recommended_decision"] == "ADVANCE C18 TO CANDIDATE SPEC"
    assert w["current_human_gate"] == (
        "HUMAN_DECISION_C18_ADVANCE_TO_CANDIDATE_SPEC_OR_REJECT")
    assert w["approval_text_to_paste"]
    assert w["ready_for_commit"] is False
    assert w["commit_approval_text"] is None
    h = p["html"]
    # dashboard generates the copyable C18 approval text + allows/forbids + bypass
    assert "Human-gate approval workflow" in h
    assert "ADVANCE C18 TO CANDIDATE SPEC" in h
    assert "HUMAN_DECISION_C18_ADVANCE_TO_CANDIDATE_SPEC_OR_REJECT" in h
    assert "Do not commit or push" in h
    assert "build the candidate-spec contract" in h
    assert "no detector build" in h
    assert "BYPASS" in h


def test_panel_shows_safety_locks():
    p = panel.build_autopilot_morning_panel(_success_report())
    sl = p["safety_locks"]
    assert sl["real_data_qa"] == "BLOCKED"
    assert sl["replay"] == "BLOCKED"
    assert sl["paper_trading"] == "LOCKED"
    assert sl["micro_live"] == "LOCKED"
    assert sl["live_trading"] == "LOCKED"
    assert "Safety locks" in p["html"]


def test_panel_not_only_c10_c12_shows_full_lane():
    # the committed lane truth exposes C13-C16, independent of the stale
    # latest.json candidate_status (which only carried C10-C12).
    p = panel.build_autopilot_morning_panel(_success_report())
    lane = {c["candidate"] for c in p["automation_readiness"]["candidate_lane"]}
    assert {"C13", "C14", "C15", "C16"}.issubset(lane)
    h = p["html"]
    for cid in ("C13", "C14", "C15", "C16"):
        assert cid in h
    assert "cointegration_pairs_market_neutral" in h


def test_panel_drift_warning_when_next_candidate_token_appears():
    rep = _success_report()
    rep["autopilot_plan"] = {
        "next_safe_action": "BUILD_NEXT_CANDIDATE_FAMILY_PROPOSAL",
        "recommended_token": "BUILD_NEXT_CANDIDATE_FAMILY_PROPOSAL_ONLY"}
    p = panel.build_autopilot_morning_panel(rep)
    assert p["drift_warning"] is True
    assert "NEXT-CANDIDATE DRIFT" in p["html"]
    # an aligned report (automation readiness) -> no drift warning
    rep2 = _success_report()
    rep2["autopilot_plan"] = {
        "next_safe_action": "RECOMMEND_AUTOMATION_READINESS_STEP",
        "recommended_token": "BUILD_AUTOMATION_READINESS_STEP_RESEARCH_ONLY"}
    rep2["what_to_do_next"] = "next stage is automation readiness"
    p2 = panel.build_autopilot_morning_panel(rep2)
    assert p2["drift_warning"] is False


def test_panel_dirty_tree_warns_but_does_not_hide_c16():
    rep = _success_report()
    rep["git_status_summary"] = {"branch": "master", "staged": 0, "modified": 3,
                                 "untracked": 0, "clean": False}
    p = panel.build_autopilot_morning_panel(rep)
    assert p["git_dirty_warning"] is True
    h = p["html"]
    assert "DIRTY" in h
    # C16 / lane status still fully visible despite the dirty tree
    assert p["automation_readiness"]["c16_lifecycle_complete"] is True
    assert p["automation_readiness"]["rejected_ledger_count"] == 22
    assert p["automation_readiness"]["active_candidate"] == "C18"
    assert "ACTIVE CANDIDATE" in h


def test_no_report_still_shows_c16_and_c18_active():
    p = panel.build_autopilot_morning_panel(None)
    ar = p["automation_readiness"]
    assert ar["c16_lifecycle_complete"] is True
    assert ar["rejected_ledger_count"] == 22
    assert ar["active_candidate"] == "C18"
    assert ar["last_rejected_candidate"] == "C17"
    assert ar["next_required_action"] == (
        "HUMAN_DECISION_C18_ADVANCE_TO_CANDIDATE_SPEC_OR_REJECT")
    assert "ACTIVE CANDIDATE" in p["html"]
    assert "C18_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW" in p["html"]


def test_panel_run_metadata_and_seed_brief_path():
    rep = _success_report()
    rep["files_created_or_changed"] = [
        "C:/SPARTA_BRAIN/data/overnight_autopilot/reports/"
        "seed_brief_draft_20260618T050002Z.md"]
    p = panel.build_autopilot_morning_panel(rep)
    assert p["latest_run_record_id"] == rep["run_id"]
    assert "seed_brief_draft" in (p["seed_brief_path"] or "")
    assert "Latest seed brief" in p["html"]
    assert rep["run_id"] in p["html"]


def test_no_next_candidate_drift_on_aligned_success_report():
    # the real aligned morning report carries no next-candidate token in its plan
    p = panel.build_autopilot_morning_panel(_success_report())
    assert p["drift_warning"] is False


# --- next-strategy research memo on the panel ------------------------------- #

def test_panel_shows_next_strategy_memo():
    p = panel.build_autopilot_morning_panel(_success_report())
    nm = p["next_strategy_memo"]
    assert nm["available"] is True
    assert nm["recommended_direction_key"] == (
        "risk_adjusted_portfolio_construction_vol_targeted_allocation")
    assert "Risk-adjusted portfolio construction" in nm["recommended_direction"]
    assert len(nm["ranked_directions"]) >= 3
    assert nm["creates_candidate_id"] is False
    h = p["html"]
    assert "Next-strategy research memo" in h
    assert "led to C17" in h
    assert "Risk-adjusted portfolio construction" in h
    assert "created no candidate" in h


def test_no_report_still_shows_next_strategy_memo():
    p = panel.build_autopilot_morning_panel(None)
    nm = p["next_strategy_memo"]
    assert nm["available"] is True
    assert nm["recommended_direction_key"] == (
        "risk_adjusted_portfolio_construction_vol_targeted_allocation")
    assert "Next-strategy research memo" in p["html"]
