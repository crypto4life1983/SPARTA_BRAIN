"""Tests for the Crypto-D1 Candidate Research Lane status / bundle surface v1.

Proves: C16 lifecycle COMPLETE and visible (6 shipped gate commits); rejected
ledger is C1-C16 (21 families) and reused from REP; the next stage is AUTOMATION
READINESS, not another candidate; the overnight/morning automation path stays
research-only with all downstream capability blocked/locked; morning-report-style
output; human approval preserved; never recommends a trading/data-fetch action;
validator anti-tamper; module purity. Deterministic."""
from __future__ import annotations

import ast

import sparta_commander.crypto_d1_candidate_research_lane_status_v1_contract as lane
import sparta_commander.research_expansion_plan_v1_contract as rep


_R = lane.get_lane_status()


# ---- core: research-only, status-only, validates ---------------------------

def test_status_pure_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_pure_status_only"] is True
    assert lane.validate_lane_status(_R)["valid"] is True


# ---- C16 completion is visible ---------------------------------------------

def test_c16_lifecycle_complete_visible():
    assert _R["c16_lifecycle_complete"] is True
    assert _R["c16_candidate_family"] == "cointegration_pairs_market_neutral"
    assert _R["c16_rejection_verdict"] == "REJECT_C16_AT_LABELS"
    assert _R["c16_in_rejected_ledger"] is True
    gates = {g["stage"]: g["commit"] for g in _R["c16_lifecycle_gates"]}
    for stage in ("family_proposal", "candidate_spec",
                  "detector_spec_and_synthetic_dry_run", "real_candle_labels_review",
                  "rejection_record", "canonical_ledger_bump"):
        assert stage in gates, stage
        assert len(gates[stage]) == 40
    bad = {**_R, "c16_lifecycle_complete": False}
    assert lane.validate_lane_status(bad)["valid"] is False


# ---- rejected ledger C1-C16 (21) reused from REP ---------------------------

def test_rejected_ledger_is_c1_to_c16_21():
    assert _R["rejected_ledger_count"] == 21
    assert _R["rejected_ledger_is_c1_to_c16"] is True
    assert len(rep.REJECTED_FAMILIES_C1_TO_C16) == 21
    assert "cointegration_pairs_market_neutral" in _R["rejected_families"]
    assert "slow_vol_targeted_time_series_momentum" in _R["rejected_families"]
    bad = {**_R, "rejected_ledger_count": 20}
    assert lane.validate_lane_status(bad)["valid"] is False


# ---- C17 is the ACTIVE open candidate (not automation readiness, not new) --

def test_c17_is_active_open_candidate():
    assert _R["active_candidate"] == "C17"
    assert _R["open_candidate_gate"] is True
    assert _R["next_is_automation_readiness"] is False
    assert _R["automation_readiness_was_prior_stage"] is True
    assert _R["next_is_new_candidate"] is False
    assert _R["next_stage"] == "c17_real_candle_labels_decision"
    assert _R["next_required_action"] == (
        "HUMAN_DECISION_C17_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT")
    det = _R["active_candidate_detail"]
    assert det["family"] == "risk_adjusted_portfolio_construction_vol_targeted_allocation"
    assert det["name"] == "risk_adjusted_portfolio_construction_vol_targeted_allocation_v1"
    # C17 has advanced through the human detector-spec gate: detector spec +
    # synthetic dry-run is frozen for review
    assert det["verdict"] == "C17_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW"
    assert det["stage"] == "detector_spec_dry_run"
    assert det["stage_label"] == "DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW"
    assert det["method"] == "volatility_targeted_risk_parity_allocation"
    assert det["assets"] == ["BTCUSD", "ETHUSD", "SOLUSD"]
    assert det["timeframe"] == "D1"
    # detector dry-run posture is surfaced
    assert det["synthetic_fixtures_only"] is True
    assert det["dry_run_all_checks_pass"] is True
    assert det["dry_run_summary"]
    assert det["next_action"] == (
        "HUMAN_DECISION_C17_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT")
    # C17 present in the candidate lane as an active frozen detector dry-run
    c17 = next(c for c in _R["candidate_lane"] if c["candidate"] == "C17")
    assert c17["state"] == "DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW"
    # tamper: cannot fall back to automation readiness / no active candidate
    bad = {**_R, "next_is_automation_readiness": True}
    assert lane.validate_lane_status(bad)["valid"] is False
    bad2 = {**_R, "active_candidate": None}
    assert lane.validate_lane_status(bad2)["valid"] is False
    bad3 = {**_R, "open_candidate_gate": False}
    assert lane.validate_lane_status(bad3)["valid"] is False


def test_c16_remains_complete_and_kept_on_record():
    assert _R["c16_lifecycle_complete"] is True
    assert _R["c16_rejection_verdict"] == "REJECT_C16_AT_LABELS"
    c16 = next(c for c in _R["candidate_lane"] if c["candidate"] == "C16")
    assert c16["state"] == "REJECTED_KEPT_ON_RECORD"


# ---- overnight/morning automation stays research-only + locked -------------

def test_automation_path_research_only_and_locked():
    assert _R["overnight_automation_research_only"] is True
    assert _R["morning_report_research_only"] is True
    assert _R["real_data_qa_state"] == "BLOCKED"
    assert _R["replay_state"] == "BLOCKED"
    assert _R["paper_trading_state"] == "LOCKED"
    assert _R["live_trading_state"] == "LOCKED"
    sf = _R["safety_flags"]
    assert sf["read_only"] is True
    assert sf["overnight_automation_research_only"] is True
    assert sf["paper_or_live"] is False
    assert sf["starts_a_new_candidate"] is False
    bad = {**_R, "paper_trading_state": "UNLOCKED"}
    assert lane.validate_lane_status(bad)["valid"] is False


# ---- human approval preserved + never trading/data-fetch -------------------

def test_human_approval_and_no_trading_action():
    assert _R["requires_human_approval"] is True
    nra = _R["next_required_action"]
    for banned in ("PAPER", "LIVE", "EXECUTE", "BROKER", "ORDER", "FETCH",
                   "PROMOTE", "DEPLOY"):
        assert banned not in nra.upper(), banned
    # the next action is a human decision gate (advance C17 to spec, or reject)
    assert nra.startswith("HUMAN_DECISION_C17_")


# ---- candidate lane summary -------------------------------------------------

def test_candidate_lane_summary_all_rejected():
    lane_rows = {c["candidate"]: c for c in _R["candidate_lane"]}
    for cid in ("C13", "C14", "C15", "C16"):
        assert cid in lane_rows
        assert lane_rows[cid]["state"] == "REJECTED_KEPT_ON_RECORD"
    assert lane_rows["C16"]["rejected_at"] == "real_candle_labels"
    assert lane_rows["C14"]["rejected_at"] == "fee_honest_replay"


# ---- morning-report-style output -------------------------------------------

def test_summarize_for_morning_report():
    summ = lane.summarize_for_morning_report()
    assert summ["section"] == "candidate_research_lane_status"
    assert summ["c16_lifecycle_complete"] is True
    assert summ["rejected_ledger_count"] == 21
    assert summ["active_candidate"] == "C17"
    assert summ["open_candidate_gate"] is True
    assert summ["active_candidate_verdict"] == "C17_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW"
    assert "Risk-adjusted portfolio construction" in summ["active_candidate_label"]
    assert summ["active_candidate_stage"] == "detector_spec_dry_run"
    assert summ["active_candidate_stage_label"] == "DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW"
    assert summ["active_candidate_method"] == "volatility_targeted_risk_parity_allocation"
    assert summ["active_candidate_assets"] == ["BTCUSD", "ETHUSD", "SOLUSD"]
    assert summ["active_candidate_timeframe"] == "D1"
    assert summ["active_candidate_synthetic_fixtures_only"] is True
    assert summ["active_candidate_dry_run_all_checks_pass"] is True
    assert summ["active_candidate_dry_run_summary"]
    assert summ["next_stage"] == "c17_real_candle_labels_decision"
    assert summ["next_is_automation_readiness"] is False
    assert summ["next_is_new_candidate"] is False
    assert summ["next_required_action"] == (
        "HUMAN_DECISION_C17_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT")
    assert summ["overnight_automation_research_only"] is True
    assert summ["executes_nothing"] is True


# ---- capability flags ------------------------------------------------------

def test_capability_flags_all_false_and_tamper_rejected():
    for flag in lane._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert lane.validate_lane_status(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_execute", "no_detector", "no_labels", "no_replay", "no_pnl",
                 "no_optimization", "no_data_fetch", "no_commit", "no_push",
                 "no_new_candidate", "no_broker", "no_paper_trading",
                 "no_live_trading"):
        assert _R["scope_locks"][must] is True, must


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(lane.__file__, encoding="utf-8").read()
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
