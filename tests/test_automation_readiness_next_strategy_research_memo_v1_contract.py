"""Tests for the Automation Readiness next-strategy research memo v1.

Proves: memo uses the C1-C16/21 rejected ledger; does NOT include excluded
families as proposed directions; creates NO candidate id; authorizes no detection/
labels/replay/PnL/optimization/data fetch; keeps real-data-QA/replay BLOCKED and
paper/micro-live/live LOCKED; requires human approval before any candidate; the
next_required_action remains BUILD_AUTOMATION_READINESS_STEP_RESEARCH_ONLY. Plus
the ranked directions + recommendation, validator anti-tamper, module purity."""
from __future__ import annotations

import ast

import sparta_commander.automation_readiness_next_strategy_research_memo_v1_contract as memo
import sparta_commander.research_expansion_plan_v1_contract as rep


_R = memo.build_next_strategy_research_memo()


# ---- core: research-only, memo-only, validates -----------------------------

def test_memo_pure_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_research_memo_only"] is True
    assert memo.validate_next_strategy_research_memo(_R)["valid"] is True


# ---- uses C1-C16 / 21 rejected ledger --------------------------------------

def test_uses_c1_to_c16_21_ledger():
    assert _R["rejected_ledger_count"] == 21
    assert _R["uses_c1_to_c16_ledger"] is True
    assert len(rep.REJECTED_FAMILIES_C1_TO_C16) == 21
    assert "cointegration_pairs_market_neutral" in _R["rejected_families_c1_to_c16"]
    # the documented C10-C16 lessons are summarized in "what failed"
    wf = _R["what_failed"]
    for k in ("calendar_seasonality_c10", "single_bar_conviction_continuation_c14",
              "slow_time_series_momentum_carry_c15",
              "cointegration_pairs_market_neutral_c16"):
        assert wf.get(k)


# ---- does NOT include excluded families as directions ----------------------

def test_directions_do_not_include_rejected_families():
    assert _R["directions_are_distinct_from_rejected_ledger"] is True
    keys = {d["key"] for d in _R["next_research_directions"]}
    assert keys.isdisjoint(set(rep.REJECTED_FAMILIES_C1_TO_C16))
    # a tampered direction that IS a rejected family is rejected
    bad = {**_R, "next_research_directions": [
        {"key": "slow_vol_targeted_time_series_momentum", "rank": 1}]}
    assert memo.validate_next_strategy_research_memo(bad)["valid"] is False


# ---- does NOT create a candidate id ----------------------------------------

def test_no_candidate_id_created():
    assert _R["is_active_candidate"] is False
    assert _R["creates_candidate_id"] is False
    assert _R["candidate_id"] is None
    assert _R["creates_candidate"] is False
    bad = {**_R, "candidate_id": "C17"}
    assert memo.validate_next_strategy_research_memo(bad)["valid"] is False
    bad2 = {**_R, "creates_candidate_id": True}
    assert memo.validate_next_strategy_research_memo(bad2)["valid"] is False


# ---- authorizes no detection/labels/replay/PnL/optimization/data fetch -----

def test_no_research_execution_authorized():
    for flag in ("runs_detector", "runs_labels", "runs_replay", "computes_pnl",
                 "optimizes_parameters", "relabels", "fetches_data"):
        assert _R[flag] is False, flag
    for lock in ("no_detector", "no_labels", "no_replay", "no_pnl",
                 "no_optimization", "no_relabel", "no_data_fetch"):
        assert _R["scope_locks"][lock] is True, lock


# ---- keeps locks -----------------------------------------------------------

def test_locks_remain_blocked_and_locked():
    assert _R["overnight_automation_research_only"] is True
    assert _R["real_data_qa_state"] == "BLOCKED"
    assert _R["replay_state"] == "BLOCKED"
    assert _R["paper_trading_state"] == "LOCKED"
    assert _R["live_trading_state"] == "LOCKED"
    for bad_key, val in (("real_data_qa_state", "UNLOCKED"),
                         ("live_trading_state", "UNLOCKED")):
        bad = {**_R, bad_key: val}
        assert memo.validate_next_strategy_research_memo(bad)["valid"] is False


# ---- requires human approval before any candidate --------------------------

def test_requires_human_approval_before_candidate():
    assert _R["requires_human_approval_before_candidate"] is True
    assert _R["human_approval_before_candidate"] == (
        "HUMAN_DECISION_APPROVE_NEXT_RESEARCH_DIRECTION_THEN_BUILD_CANDIDATE_PROPOSAL")
    bad = {**_R, "requires_human_approval_before_candidate": False}
    assert memo.validate_next_strategy_research_memo(bad)["valid"] is False


# ---- next_required_action unchanged ----------------------------------------

def test_next_required_action_remains_automation_readiness():
    assert _R["next_required_action"] == "BUILD_AUTOMATION_READINESS_STEP_RESEARCH_ONLY"
    bad = {**_R, "next_required_action": "BUILD_NEXT_CANDIDATE_FAMILY_PROPOSAL"}
    assert memo.validate_next_strategy_research_memo(bad)["valid"] is False


# ---- ranked directions + recommendation ------------------------------------

def test_ranked_directions_and_recommendation():
    ds = _R["next_research_directions"]
    assert 3 <= len(ds) <= 5
    ranks = [d["rank"] for d in ds]
    assert ranks == sorted(ranks)
    rec = _R["recommended_direction"]
    assert rec["key"] == "risk_adjusted_portfolio_construction_vol_targeted_allocation"
    assert rec["rank"] == 1
    assert rec["is_directional_timing_signal"] is False
    # the memo records WHY the recommendation avoids the C1-C16 failure modes
    why = _R["why_recommended_is_different"].lower()
    assert "buy-and-hold" in why
    assert "risk-adjusted" in why
    assert "timing" in why


# ---- failure patterns + traits ---------------------------------------------

def test_failure_patterns_and_traits_present():
    patterns = " || ".join(_R["common_failure_patterns"]).lower()
    assert "carry trap" in patterns or "buy-and-hold" in patterns
    assert "forward-oos" in patterns
    assert "cost erosion" in patterns
    assert "rarity" in patterns
    assert len(_R["traits_to_avoid"]) >= 5
    assert len(_R["traits_to_prefer"]) >= 5
    avoid = " || ".join(_R["traits_to_avoid"]).lower()
    assert "directional crypto beta" in avoid
    assert "anti-loop" in avoid or "c1-c16" in avoid


# ---- morning-report summary ------------------------------------------------

def test_summarize_for_morning_report():
    summ = memo.summarize_for_morning_report()
    assert summ["section"] == "next_strategy_research_memo"
    assert summ["rejected_ledger_count"] == 21
    assert summ["creates_candidate_id"] is False
    assert summ["next_required_action"] == "BUILD_AUTOMATION_READINESS_STEP_RESEARCH_ONLY"
    assert summ["requires_human_approval_before_candidate"] is True
    assert len(summ["ranked_directions"]) >= 3
    assert summ["executes_nothing"] is True


# ---- capability flags + scope locks ----------------------------------------

def test_capability_flags_all_false_and_tamper_rejected():
    for flag in memo._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert memo.validate_next_strategy_research_memo(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_execute", "no_create_candidate", "no_candidate_id",
                 "no_detector", "no_replay", "no_data_fetch", "no_commit",
                 "no_push", "no_paper_trading", "no_live_trading",
                 "no_reuse_of_rejected_family"):
        assert _R["scope_locks"][must] is True, must


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(memo.__file__, encoding="utf-8").read()
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
