"""Tests for the Automation Readiness bundle/surface integration v1.

Proves: (1) C16 lifecycle complete is visible; (2) the candidate-lane next stage is
automation_readiness; (3) no new candidate is recommended on any surface; (4) the
automation path stays research-only; (5) real-data-QA/replay stay BLOCKED; (6)
paper/micro-live/live stay LOCKED; (7) the morning / autopilot / bundle /
coordinator surfaces AGREE (same automation-readiness token). Plus: the coordinator
idle/default no longer drifts to next-candidate, SARA's generic idle is overridden,
validator anti-tamper, module purity. Deterministic."""
from __future__ import annotations

import ast

import sparta_commander.automation_readiness_bundle_integration_v1_contract as ari
import sparta_commander.crypto_d1_candidate_research_lane_status_v1_contract as lane
import sparta_commander.gate_decision_coordinator_v1_contract as gdc


_R = ari.build_automation_readiness_integration()


# ---- core: research-only, integration-only, validates ----------------------

def test_integration_pure_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_pure_integration_only"] is True
    assert ari.validate_automation_readiness_integration(_R)["valid"] is True


# ---- 1. C16 complete is visible --------------------------------------------

def test_c16_complete_visible():
    assert _R["c16_lifecycle_complete"] is True
    assert _R["rejected_ledger_count"] == 21


# ---- 2. next directive = C17 spec decision (lane has active candidate) ------

def test_next_directive_is_c17_spec_decision():
    assert _R["active_candidate"] == "C17"
    assert _R["open_candidate_gate"] is True
    assert _R["next_is_automation_readiness"] is False
    assert _R["next_stage"] == "c17_candidate_spec_decision"
    assert _R["next_required_action"] == (
        "HUMAN_DECISION_C17_ADVANCE_TO_CANDIDATE_SPEC_OR_REJECT")
    assert "Risk-adjusted portfolio construction" in _R["active_candidate_label"]
    assert _R["active_candidate_verdict"] == "C17_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW"


# ---- 3. no new candidate recommended on any surface ------------------------

def test_no_new_candidate_recommended():
    assert _R["next_is_new_candidate"] is False
    assert _R["no_new_candidate_recommended"] is True
    assert _R["recommends_new_candidate"] is False
    assert _R["starts_a_new_candidate"] is False
    bad = {**_R, "next_is_new_candidate": True}
    assert ari.validate_automation_readiness_integration(bad)["valid"] is False


# ---- 4. automation remains research-only -----------------------------------

def test_automation_research_only():
    assert _R["automation_research_only"] is True
    assert _R["overnight_automation_research_only"] is True


# ---- 5. real-data-QA / replay remain BLOCKED -------------------------------

def test_real_data_qa_and_replay_blocked():
    assert _R["real_data_qa_state"] == "BLOCKED"
    assert _R["replay_state"] == "BLOCKED"
    assert _R["downstream_blocked_and_locked"] is True
    bad = {**_R, "replay_state": "UNLOCKED"}
    assert ari.validate_automation_readiness_integration(bad)["valid"] is False


# ---- 6. paper / micro-live / live remain LOCKED ----------------------------

def test_paper_micro_live_live_locked():
    assert _R["paper_trading_state"] == "LOCKED"
    assert _R["live_trading_state"] == "LOCKED"
    # the lane status (authoritative) keeps micro-live locked too
    ls = lane.get_lane_status()
    assert ls["safety_flags"]["micro_live_locked"] is True
    bad = {**_R, "paper_trading_state": "UNLOCKED"}
    assert ari.validate_automation_readiness_integration(bad)["valid"] is False


# ---- 7. morning / autopilot / bundle / coordinator surfaces agree ----------

def test_surfaces_agree_on_c17_directive():
    assert _R["surfaces_agree"] is True
    assert _R["all_tokens_match"] is True
    s = _R["surfaces"]
    token = "HUMAN_DECISION_C17_ADVANCE_TO_CANDIDATE_SPEC_OR_REJECT"
    assert s["lane_status_next"] == token
    assert s["coordinator_command"] == token
    assert s["lane_morning_next"] == token
    assert s["coordinator_recommendation_kind"] == gdc.REC_GATE_DECISION
    # the SARA generic idle (build a proposal) is OVERRIDDEN by the lane directive
    assert _R["sara_generic_idle_overridden_by_lane_directive"] is True
    assert _R["sara_generic_idle_action"] == gdc._sara.ACTION_BUILD_PROPOSAL
    bad = {**_R, "surfaces_agree": False}
    assert ari.validate_automation_readiness_integration(bad)["valid"] is False


def test_coordinator_idle_defers_to_lane_c17_gate():
    # the coordinator's clean+synced+no-open-gate-in-state branch defers to the
    # lane, which now has C17 as the active open candidate -> C17 spec decision,
    # not a new candidate and not automation readiness.
    d = gdc.coordinate({
        "repo": {"clean": True, "ahead": 0, "behind": 0,
                 "uncommitted_changes": False},
        "ledger": {"canonical_count": 21, "expected_count": 21, "reconciles": True},
        "candidates": {"C16": {"family": "cointegration_pairs_market_neutral",
                               "status": "REJECTED_KEPT_ON_RECORD", "active": False,
                               "next_action": "NONE__C16_CLOSED", "shipped": True}}})
    assert d["recommendation_kind"] == gdc.REC_GATE_DECISION
    assert d["next_safe_command"] == (
        "HUMAN_DECISION_C17_ADVANCE_TO_CANDIDATE_SPEC_OR_REJECT")
    assert d["next_research_recommended"] is False
    assert d["detected_gate"] == "active_candidate_open_gate"


# ---- morning-report-style output -------------------------------------------

def test_summarize_for_morning_report():
    summ = ari.summarize_for_morning_report()
    assert summ["section"] == "candidate_lane_directive"
    assert summ["c16_lifecycle_complete"] is True
    assert summ["rejected_ledger_count"] == 21
    assert summ["active_candidate"] == "C17"
    assert summ["open_candidate_gate"] is True
    assert summ["next_stage"] == "c17_candidate_spec_decision"
    assert summ["next_required_action"] == (
        "HUMAN_DECISION_C17_ADVANCE_TO_CANDIDATE_SPEC_OR_REJECT")
    assert summ["next_is_automation_readiness"] is False
    assert summ["next_is_new_candidate"] is False
    assert summ["surfaces_agree"] is True
    assert summ["executes_nothing"] is True


# ---- capability flags + scope locks ----------------------------------------

def test_capability_flags_all_false_and_tamper_rejected():
    for flag in ari._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert ari.validate_automation_readiness_integration(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_execute", "no_detector", "no_labels", "no_replay", "no_pnl",
                 "no_data_fetch", "no_commit", "no_push", "no_new_candidate",
                 "no_broker", "no_paper_trading", "no_live_trading"):
        assert _R["scope_locks"][must] is True, must


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(ari.__file__, encoding="utf-8").read()
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
