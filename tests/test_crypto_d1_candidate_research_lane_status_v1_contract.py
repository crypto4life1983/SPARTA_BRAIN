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

def test_rejected_ledger_is_c1_to_c19_24():
    assert _R["rejected_ledger_count"] == 24
    assert _R["rejected_ledger_is_c1_to_c19"] is True
    assert len(rep.REJECTED_FAMILIES_C1_TO_C19) == 24
    assert "cointegration_pairs_market_neutral" in _R["rejected_families"]
    assert "slow_vol_targeted_time_series_momentum" in _R["rejected_families"]
    assert ("risk_adjusted_portfolio_construction_vol_targeted_allocation"
            in _R["rejected_families"])
    assert "h4_trend_following_market_structure" in _R["rejected_families"]
    assert ("oos_validated_beta_neutral_cross_sectional_relative_value"
            in _R["rejected_families"])
    assert _R["c18_in_rejected_ledger"] is True
    assert _R["c19_in_rejected_ledger"] is True
    bad = {**_R, "rejected_ledger_count": 23}
    assert lane.validate_lane_status(bad)["valid"] is False


# ---- C20 is the ACTIVE open candidate at family_proposal; C19 kept on record --

def test_c20_active_candidate_at_family_proposal():
    assert _R["active_candidate"] == "C20"
    assert _R["open_candidate_gate"] is True
    assert _R["next_is_automation_readiness"] is False
    assert _R["next_is_new_candidate"] is False
    assert _R["next_stage"] == "c20_candidate_spec_decision"
    assert _R["next_required_action"] == (
        "HUMAN_DECISION_C20_ADVANCE_TO_CANDIDATE_SPEC_OR_REJECT")
    det = _R["active_candidate_detail"]
    assert det["candidate"] == "C20"
    assert det["family"] == "mechanically_neutral_spot_perp_basis_funding_carry"
    assert det["verdict"] == "C20_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW"
    assert det["stage"] == "family_proposal"
    assert det["stage_label"] == "PROPOSAL_FROZEN_FOR_HUMAN_REVIEW"
    assert det["timeframe"] == "D1"
    assert det["universe"] == ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    assert det["is_market_neutral"] is True
    assert det["is_mechanically_neutral_same_asset"] is True
    assert det["return_source_is_carry_not_timing"] is True
    assert len(det["proposal_commit"]) == 40
    assert det["next_action"] == "HUMAN_DECISION_C20_ADVANCE_TO_CANDIDATE_SPEC_OR_REJECT"
    # C20 present in the candidate lane as an active frozen proposal
    c20 = next(c for c in _R["candidate_lane"] if c["candidate"] == "C20")
    assert c20["state"] == "PROPOSED_FROZEN_FOR_HUMAN_REVIEW"
    assert c20["stage"] == "family_proposal"
    # tamper: cannot drop the active candidate / close the gate / mis-state neutrality
    bad = {**_R, "active_candidate": None}
    assert lane.validate_lane_status(bad)["valid"] is False
    bad2 = {**_R, "open_candidate_gate": False}
    assert lane.validate_lane_status(bad2)["valid"] is False
    bad3 = {**_R, "next_is_automation_readiness": True}
    assert lane.validate_lane_status(bad3)["valid"] is False


def test_c19_kept_on_record_as_last_rejected():
    assert _R["last_rejected_candidate"] == "C19"
    rej = _R["last_rejected_candidate_detail"]
    assert rej["family"] == "oos_validated_beta_neutral_cross_sectional_relative_value"
    assert rej["verdict"] == "C19_REJECTED_AT_REAL_CANDLE_LABELS"
    assert rej["rejected_at"] == "real_candle_labels_neutrality_gate"
    assert rej["rejection_reason"]
    assert rej["is_market_neutral"] is True
    assert len(rej["labels_review_commit"]) == 40
    # C19 present in the candidate lane as REJECTED at the labels/neutrality gate
    c19 = next(c for c in _R["candidate_lane"] if c["candidate"] == "C19")
    assert c19["state"] == "REJECTED_KEPT_ON_RECORD"
    assert c19["rejected_at"] == "real_candle_labels_neutrality_gate"


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
    # C20 active -> the next action is the human candidate-spec-or-reject decision
    assert nra == "HUMAN_DECISION_C20_ADVANCE_TO_CANDIDATE_SPEC_OR_REJECT"


# ---- candidate lane summary -------------------------------------------------

def test_candidate_lane_summary_rejected_plus_c20_active():
    lane_rows = {c["candidate"]: c for c in _R["candidate_lane"]}
    for cid in ("C13", "C14", "C15", "C16", "C17", "C18", "C19"):
        assert cid in lane_rows
        assert lane_rows[cid]["state"] == "REJECTED_KEPT_ON_RECORD"
    assert lane_rows["C16"]["rejected_at"] == "real_candle_labels"
    assert lane_rows["C14"]["rejected_at"] == "fee_honest_replay"
    assert lane_rows["C17"]["rejected_at"] == "fee_honest_replay"
    assert lane_rows["C18"]["rejected_at"] == "fee_honest_replay"
    assert lane_rows["C19"]["rejected_at"] == "real_candle_labels_neutrality_gate"
    assert lane_rows["C20"]["state"] == "PROPOSED_FROZEN_FOR_HUMAN_REVIEW"


# ---- morning-report-style output -------------------------------------------

def test_summarize_for_morning_report():
    summ = lane.summarize_for_morning_report()
    assert summ["section"] == "candidate_research_lane_status"
    assert summ["c16_lifecycle_complete"] is True
    assert summ["rejected_ledger_count"] == 24
    assert summ["active_candidate"] == "C20"
    assert summ["active_candidate_verdict"] == "C20_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW"
    assert summ["active_candidate_stage"] == "family_proposal"
    assert summ["active_candidate_is_market_neutral"] is True
    assert summ["open_candidate_gate"] is True
    assert summ["last_rejected_candidate"] == "C19"
    assert summ["last_rejected_candidate_verdict"] == "C19_REJECTED_AT_REAL_CANDLE_LABELS"
    assert summ["last_rejected_candidate_rejected_at"] == (
        "real_candle_labels_neutrality_gate")
    assert summ["last_rejected_candidate_reason"]
    assert summ["next_stage"] == "c20_candidate_spec_decision"
    assert summ["next_is_automation_readiness"] is False
    assert summ["next_is_new_candidate"] is False
    assert summ["next_required_action"] == (
        "HUMAN_DECISION_C20_ADVANCE_TO_CANDIDATE_SPEC_OR_REJECT")
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
