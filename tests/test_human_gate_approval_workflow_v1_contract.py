"""Tests for the Dashboard Human-Gate Approval Workflow v1 contract.

Verifies: research-only, pure-workflow-only, executes nothing; mirrors the lane's
CURRENT open human gate (C17 at SPEC_FROZEN_FOR_HUMAN_REVIEW -> detector-spec
gate); emits the exact copyable approval text (gate token + recommended decision +
stop-before-commit guard); lists the research-only allows and the full forbid set
(data fetch / detection / labels / replay / backtest / PnL / optimization / paper /
live / broker / order); advances nothing (no auto-advance, no C17 advance); the
future-ready ready-for-commit field is empty now; downstream gates locked; bypass
warning present; capability flags + scope locks; validator anti-tamper; purity."""
from __future__ import annotations

import ast

import sparta_commander.human_gate_approval_workflow_v1_contract as hgw
import sparta_commander.crypto_d1_candidate_research_lane_status_v1_contract as lane


_R = hgw.build_human_gate_workflow()

GATE = "HUMAN_DECISION_OPEN_CANDIDATE_22_FAMILY_PROPOSAL_OR_HOLD"


# ---- core: research-only, pure, validates ----------------------------------

def test_workflow_research_only_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_pure_workflow_only"] is True
    assert _R["executes_nothing"] is True
    assert hgw.validate_human_gate_workflow(_R)["valid"] is True


# ---- 1/2/3 mirrors the lane's current candidate / stage / gate -------------

def test_mirrors_lane_c21_open_gate():
    ls = lane.get_lane_status()
    # C21 is REJECTED -> there is NO open candidate ADVANCE gate; the lane's next
    # required action is the C22 family-proposal readiness (an open-candidate decision,
    # not a candidate ADVANCE gate the workflow registry maps).
    assert ls["active_candidate"] is None
    assert _R["active_candidate"] is None
    assert _R["has_open_human_gate"] is False
    assert _R["current_human_gate"] == GATE == ls["next_required_action"]
    # tamper: claiming an open gate while the lane has none must fail
    bad = {**_R, "has_open_human_gate": True}
    assert hgw.validate_human_gate_workflow(bad)["valid"] is False


# ---- 4 no open candidate gate -> no advance recommendation -----------------

def test_recommended_decision_advance_c21_to_spec():
    assert "NO OPEN CANDIDATE GATE" in _R["recommended_decision"]
    assert "Candidate #22 family-proposal readiness" in _R["recommended_decision"]
    assert _R["stage_after_approval"] is None


# ---- 5 no copyable advance-approval text when no gate is open --------------

def test_copyable_approval_text_present():
    assert _R["approval_text_to_paste"] is None
    assert _R["reject_text_to_paste"] is None


# ---- 7 the gate-invariant operational forbids still hold -------------------

def test_approval_forbids_invariant():
    # gate-invariant operational forbids present even with no open gate.
    forbids = " || ".join(_R["approval_forbids"]).lower()
    for must in ("data fetch", "replay", "optimization",
                 "paper/live/broker/order"):
        assert must in forbids, must


# ---- 5 (negative) does not auto-advance C17 --------------------------------

def test_does_not_auto_advance():
    assert _R["would_auto_advance"] is False
    assert _R["advances_c17"] is False
    assert _R["human_paste_required"] is True
    assert _R["promotes_gate"] is False
    assert _R["bypasses_human_gate"] is False
    for bad_key in ("would_auto_advance", "advances_c17", "promotes_gate",
                    "bypasses_human_gate"):
        bad = {**_R, bad_key: True}
        assert hgw.validate_human_gate_workflow(bad)["valid"] is False, bad_key


# ---- 6/7 C17 rejected; downstream locked -----------------------------------

def test_c20_rejected_and_downstream_locked():
    # the workflow does not change the lane: C21 is the last rejected (at replay), C20
    # the prior rejected (at replay)
    ls = lane.get_lane_status()
    assert (ls["last_rejected_candidate_detail"]["verdict"]
            == "C21_REJECTED_AT_FEE_HONEST_REPLAY")
    assert (ls["prior_rejected_candidate_detail"]["verdict"]
            == "C20_REJECTED_AT_FEE_HONEST_REPLAY")
    assert _R["downstream_gates_locked"] is True
    sl = _R["safety_locks"]
    assert sl["real_data_qa"] == "BLOCKED"
    assert sl["replay"] == "BLOCKED"
    assert sl["paper_trading"] == "LOCKED"
    assert sl["live_trading"] == "LOCKED"
    bad = {**_R, "downstream_gates_locked": False}
    assert hgw.validate_human_gate_workflow(bad)["valid"] is False


# ---- 10 bypass warning -----------------------------------------------------

def test_bypass_warning_present():
    assert _R["gate_bypass_warning"]
    assert "BYPASS" in _R["gate_bypass_warning"]
    bad = {**_R, "gate_bypass_warning": ""}
    assert hgw.validate_human_gate_workflow(bad)["valid"] is False


# ---- 11 future-ready ready-for-commit field --------------------------------

def test_ready_for_commit_future_ready_field_empty_now():
    assert _R["ready_for_commit"] is False
    assert _R["ready_for_commit_unit"] is None
    assert _R["commit_approval_text"] is None
    # the helper formats a token only when a unit is actually given
    assert hgw.build_commit_approval_text(None) is None
    txt = hgw.build_commit_approval_text("dashboard_human_gate_approval_workflow_v1",
                                         ["a.py", "b.py"])
    assert txt.startswith(
        "APPROVE_COMMIT_DASHBOARD_HUMAN_GATE_APPROVAL_WORKFLOW_V1")
    assert "a.py" in txt and "b.py" in txt
    # a fabricated commit token in the record must fail validation
    bad = {**_R, "ready_for_commit": True, "commit_approval_text": "APPROVE_COMMIT_X"}
    assert hgw.validate_human_gate_workflow(bad)["valid"] is False


# ---- capability flags + scope locks ----------------------------------------

def test_capability_flags_all_false_and_tamper_rejected():
    for flag in hgw._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert hgw.validate_human_gate_workflow(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_execute", "no_advance_gate", "no_build", "no_detector_spec",
                 "no_dry_run_build", "no_detector_run", "no_labels", "no_replay",
                 "no_pnl", "no_optimization", "no_data_fetch", "no_commit",
                 "no_push", "no_broker", "no_order_logic", "no_paper_trading",
                 "no_live_trading", "no_gate_skip", "no_human_gate_bypass"):
        assert _R["scope_locks"][must] is True, must


def test_summarize_for_panel():
    s = hgw.summarize_for_panel()
    assert s["active_candidate"] is None
    assert s["has_open_human_gate"] is False
    assert s["current_human_gate"] == GATE
    assert "NO OPEN CANDIDATE GATE" in s["recommended_decision"]
    assert s["approval_text_to_paste"] is None
    assert s["would_auto_advance"] is False
    assert s["ready_for_commit"] is False
    assert s["commit_approval_text"] is None
    assert s["executes_nothing"] is True


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(hgw.__file__, encoding="utf-8").read()
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
