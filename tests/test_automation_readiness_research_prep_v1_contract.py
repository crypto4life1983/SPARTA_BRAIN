"""Tests for the Automation Readiness research-prep spec v1.

Proves (the 10 required points): (1) C16 complete visible; (2) rejected ledger
C1-C16/21; (3) next_required_action = BUILD_AUTOMATION_READINESS_STEP_RESEARCH_ONLY;
(4) run-record gate no longer HUMAN_DECISION_ON_NEXT_CANDIDATE_FAMILY (aligned);
(5/6) morning report §13/§14 still show automation readiness; (7) no surface
recommends BUILD_NEXT_CANDIDATE_FAMILY_PROPOSAL; (8) overnight research-only;
(9) real-data-QA/replay BLOCKED; (10) paper/micro-live/live LOCKED. Plus: allowed
vs forbidden action sets, validator anti-tamper, module purity. Deterministic."""
from __future__ import annotations

import ast

import sparta_commander.automation_readiness_research_prep_v1_contract as arp
import tools.sparta_autopilot_morning_report as mr


_R = arp.build_automation_readiness_research_prep()


def _clean_git():
    return {"branch": "master", "staged": 0, "modified": 0, "untracked": 0,
            "clean": True, "tracked_change_lines": [],
            "ahead_behind": {"upstream": "origin/master", "ahead": 0,
                             "behind": 0, "in_sync": True}}


# ---- core: research-only, prep-spec-only, validates ------------------------

def test_prep_pure_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_pure_prep_spec_only"] is True
    assert arp.validate_automation_readiness_research_prep(_R)["valid"] is True


# ---- (1) C16 complete + (2) ledger 21 --------------------------------------

def test_c16_complete_and_ledger_21():
    assert _R["c16_lifecycle_complete"] is True
    assert _R["rejected_ledger_count"] == 21


# ---- (3) next action + (4) run-record gate aligned -------------------------

def test_next_action_and_run_record_gate_aligned():
    assert _R["next_required_action"] == "BUILD_AUTOMATION_READINESS_STEP_RESEARCH_ONLY"
    assert _R["run_record_next_human_gate"] == "BUILD_AUTOMATION_READINESS_STEP_RESEARCH_ONLY"
    assert _R["run_record_next_human_gate"] != "HUMAN_DECISION_ON_NEXT_CANDIDATE_FAMILY"
    assert _R["surfaces_agree"] is True
    bad = {**_R, "run_record_next_human_gate": "HUMAN_DECISION_ON_NEXT_CANDIDATE_FAMILY"}
    assert arp.validate_automation_readiness_research_prep(bad)["valid"] is False


# ---- (5/6/7) morning report surfaces agree, no candidate drift -------------

def test_morning_report_sections_agree_no_candidate_drift():
    report = mr.build_morning_report(
        {"run_time": "t", "tasks_attempted": ["a"], "tasks_completed": ["a"],
         "tasks_failed": [], "tasks_skipped": [], "errors": [],
         "integrity_status": "INTACT", "explicit_status": None},
        _clean_git(),
        {"C16": {"family": "cointegration_pairs_market_neutral",
                 "status": "REJECTED_KEPT_ON_RECORD", "active": False,
                 "next_action": "NONE (closed)"}})
    ap = report["autopilot_plan"]
    ar = report["automation_readiness"]
    # (5) §13 clean-tree plan
    assert ap["next_safe_action"] == "RECOMMEND_AUTOMATION_READINESS_STEP"
    # (6) §14
    assert ar["next_stage"] == "automation_readiness"
    assert ar["next_required_action"] == "BUILD_AUTOMATION_READINESS_STEP_RESEARCH_ONLY"
    md = mr.render_markdown(report)
    assert "AUTOMATION READINESS" in md
    # (7) no candidate drift on any surface
    assert "BUILD_NEXT_CANDIDATE_FAMILY_PROPOSAL" not in md
    assert ar["next_is_new_candidate"] is False
    assert _R["next_is_new_candidate"] is False


# ---- (8/9/10) research-only + downstream blocked/locked --------------------

def test_research_only_and_downstream_blocked_locked():
    assert _R["overnight_automation_research_only"] is True
    assert _R["goal_is_live_trading"] is False
    assert _R["real_data_qa_state"] == "BLOCKED"
    assert _R["replay_state"] == "BLOCKED"
    assert _R["paper_trading_state"] == "LOCKED"
    assert _R["live_trading_state"] == "LOCKED"
    for bad_key, val in (("real_data_qa_state", "UNLOCKED"),
                         ("paper_trading_state", "UNLOCKED")):
        bad = {**_R, bad_key: val}
        assert arp.validate_automation_readiness_research_prep(bad)["valid"] is False


# ---- allowed vs forbidden overnight actions --------------------------------

def test_allowed_and_forbidden_action_sets():
    allowed = _R["allowed_next_research_prep_actions"]
    assert "rejected_ledger_lessons_memo_draft" in allowed
    assert "evidence_summary_draft" in allowed
    assert _R["all_next_actions_are_advisory_human_gated"] is True
    forb = _R["forbidden_overnight_actions"]
    for must in ("create_new_candidate", "run_replay", "compute_pnl",
                 "fetch_data", "paper_trade", "live_trade", "broker_order",
                 "auto_commit", "auto_push"):
        assert must in forb, must
    # no unsafe action leaked into the allowed set
    for bad in ("create_new_candidate", "run_replay", "fetch_data", "paper_trade",
                "live_trade", "broker_order"):
        assert bad not in allowed
    # the existing 4 safe overnight tasks are recognized
    for t in ("integrity_audit", "contract_certification_sweep",
              "safety_test_suite_report", "seed_research_brief_draft"):
        assert t in _R["allowed_overnight_tasks_research_only"]


def test_summarize_for_morning_report():
    summ = arp.summarize_for_morning_report()
    assert summ["section"] == "automation_readiness_research_prep"
    assert summ["c16_lifecycle_complete"] is True
    assert summ["rejected_ledger_count"] == 21
    assert summ["next_required_action"] == "BUILD_AUTOMATION_READINESS_STEP_RESEARCH_ONLY"
    assert summ["run_record_next_human_gate"] == "BUILD_AUTOMATION_READINESS_STEP_RESEARCH_ONLY"
    assert summ["next_is_new_candidate"] is False
    assert summ["goal_is_live_trading"] is False
    assert summ["executes_nothing"] is True


# ---- capability flags + scope locks ----------------------------------------

def test_capability_flags_all_false_and_tamper_rejected():
    for flag in arp._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert arp.validate_automation_readiness_research_prep(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_execute", "no_new_candidate", "no_detector", "no_labels",
                 "no_replay", "no_pnl", "no_data_fetch", "no_commit", "no_push",
                 "no_broker", "no_paper_trading", "no_live_trading",
                 "no_autonomous_trading"):
        assert _R["scope_locks"][must] is True, must


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(arp.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch(", "open("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
              "subprocess", "websockets", "aiohttp", "schedule", "threading",
              "asyncio", "telegram", "csv", "hashlib", "os", "io", "shutil",
              "ssl", "ftplib", "pathlib", "datetime", "random"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned), imported & banned
    for call in ast.walk(tree):
        if isinstance(call, ast.Call):
            name = (call.func.attr if isinstance(call.func, ast.Attribute)
                    else getattr(call.func, "id", ""))
            assert name not in ("open", "exec", "eval", "compile"), name
