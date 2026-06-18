"""Tests for the Candidate #17 family-proposal contract
(risk_adjusted_portfolio_construction_vol_targeted_allocation_v1).

Verifies: research-only, pure-proposal-only; chain-gated on the next-strategy memo
recommending exactly this direction; it is a PORTFOLIO-CONSTRUCTION candidate (not
directional timing, not pairs) NOT in the C1-C16 ledger; all 9 explanation sections
present (thesis / difference / BTC-ETH-SOL / vol-target+risk-parity / risk-adjusted
metrics / cost+turnover / OOS / safety / next gate); proposal only (no detector/
labels/replay/PnL/optimization/data fetch); downstream gates locked; validator
anti-tamper; module purity."""
from __future__ import annotations

import ast

import sparta_commander.risk_adjusted_portfolio_construction_vol_targeted_allocation_v1_proposal_contract as c17  # noqa: E501
import sparta_commander.research_expansion_plan_v1_contract as rep


_R = c17.build_c17_proposal(".", [])


# ---- core: research-only, pure, frozen, validates --------------------------

def test_proposal_frozen_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_pure_proposal_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"] == "C17_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW"
    assert c17.validate_c17_proposal(_R)["valid"] is True


def test_candidate_identity():
    assert _R["candidate_id"] == "C17"
    assert _R["candidate_family"] == (
        "risk_adjusted_portfolio_construction_vol_targeted_allocation")
    assert _R["candidate_name"] == (
        "risk_adjusted_portfolio_construction_vol_targeted_allocation_v1")


# ---- chain gate: memo recommends this direction ----------------------------

def test_chain_gated_on_memo_recommendation():
    assert _R["source_memo_recommends_this"] is True
    assert _R["source_memo_valid"] is True
    assert _R["approved_direction_key"] == (
        "risk_adjusted_portfolio_construction_vol_targeted_allocation")
    assert _R["approved_via"] == (
        "HUMAN_DECISION_APPROVE_NEXT_RESEARCH_DIRECTION_THEN_BUILD_CANDIDATE_PROPOSAL")


# ---- identity + anti-loop --------------------------------------------------

def test_portfolio_construction_identity_and_anti_loop():
    assert _R["is_portfolio_construction"] is True
    assert _R["is_directional_timing_signal"] is False
    assert _R["is_market_neutral_pairs"] is False
    assert _R["candidate_not_in_rejected_ledger"] is True
    assert _R["candidate_family"] not in rep.REJECTED_FAMILIES_C1_TO_C16
    assert _R["rejected_families_count"] == 21
    for bad_key in ("is_portfolio_construction",):
        bad = {**_R, bad_key: False}
        assert c17.validate_c17_proposal(bad)["valid"] is False
    bad2 = {**_R, "is_directional_timing_signal": True}
    assert c17.validate_c17_proposal(bad2)["valid"] is False


# ---- the 9 explanation sections --------------------------------------------

def test_strategy_thesis_and_difference():
    assert "risk" in _R["strategy_thesis"].lower()
    md = " || ".join(_R["why_different_from_c1_c16"]).lower()
    assert "allocation" in md and "timing" in md
    assert "risk-adjusted" in md
    assert len(_R["why_different_from_c1_c16"]) >= 5


def test_universe_btc_eth_sol_only():
    assert _R["symbols"] == ["BTCUSD", "ETHUSD", "SOLUSD"]
    assert _R["timeframe"] == "D1"


def test_portfolio_construction_idea():
    pc = _R["portfolio_construction_idea"]
    assert pc["method"] == "volatility_targeting_plus_risk_parity"
    assert "inverse_volatility" in pc["risk_parity_weighting"]
    assert pc["max_gross_exposure_cap"] == 1.0
    assert "low-turnover" in pc["rebalance_policy"]


def test_evaluation_metrics_risk_adjusted_vs_buy_and_hold():
    em = _R["evaluation_metrics"]
    for m in ("sharpe_ratio", "calmar_ratio", "max_drawdown"):
        assert m in em["primary_risk_adjusted"], m
    assert em["turnover"]
    assert em["net_return_vs_buy_and_hold"]
    assert "buy-and-hold" in em["baseline"].lower()
    assert "risk-adjusted" in em["win_condition"].lower()
    bad = {**_R, "evaluation_metrics": {**em, "win_condition": "higher raw return"}}
    assert c17.validate_c17_proposal(bad)["valid"] is False


def test_cost_and_turnover_constraints():
    ct = _R["cost_and_turnover"]
    assert ct["all_in_round_trip_bps"] == 37.0
    assert ct["cost_scales_with_turnover"] is True
    assert ct["no_high_frequency_churn"] is True
    assert ct["turnover_constraint"]
    bad = {**_R, "cost_and_turnover": {**ct, "all_in_round_trip_bps": 5.0}}
    assert c17.validate_c17_proposal(bad)["valid"] is False


def test_oos_validation_requirement():
    oos = _R["oos_validation"]
    assert oos["forward_oos_required"] is True
    assert oos["forward_oos_must_hold_risk_adjusted_edge"] is True
    assert oos["durability_window_days"] == 1095
    assert oos["no_parameter_optimization"] is True
    bad = {**_R, "oos_validation": {**oos, "forward_oos_required": False}}
    assert c17.validate_c17_proposal(bad)["valid"] is False


def test_safety_boundaries_and_next_gate():
    sb = " || ".join(_R["safety_boundaries"]).lower()
    assert "research-only" in sb
    assert "no paper trading" in sb and "no live trading" in sb
    assert "no shorting" in sb or "long-or-flat" in sb
    assert _R["next_human_gate_after_proposal"] == (
        "HUMAN_DECISION_C17_ADVANCE_TO_CANDIDATE_SPEC_OR_REJECT")
    assert _R["next_required_action"] == (
        "HUMAN_DECISION_C17_ADVANCE_TO_CANDIDATE_SPEC_OR_REJECT")


# ---- gate sequence + downstream locks --------------------------------------

def test_gate_sequence_preserved_and_downstream_locked():
    assert _R["gate_sequence"] == [
        "family_proposal", "candidate_spec", "detector_spec_dry_run",
        "real_candle_labels_review", "fee_honest_replay_review",
        "rejection_or_promote_decision"]
    for gate in ("spec_gate_locked", "detector_gate_locked", "labels_gate_locked",
                 "replay_gate_locked", "paper_trading_gate_locked",
                 "live_gate_locked"):
        assert _R[gate] is True, gate
        bad = {**_R, gate: False}
        assert c17.validate_c17_proposal(bad)["valid"] is False, gate


# ---- capability flags + scope locks ----------------------------------------

def test_capability_flags_all_false_and_tamper_rejected():
    for flag in c17._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert c17.validate_c17_proposal(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_build", "no_detector", "no_labels", "no_replay", "no_pnl",
                 "no_optimization", "no_data_fetch", "no_commit", "no_push",
                 "no_broker", "no_order_logic", "no_leverage_above_cap",
                 "no_shorting", "no_paper_trading", "no_live_trading"):
        assert _R["scope_locks"][must] is True, must


def test_label_no_readiness_claim():
    label = c17.get_candidate_17_proposal_label()
    assert "RESEARCH ONLY" in label
    assert "PROPOSAL ONLY" in label.upper() or "PURE PROPOSAL" in label.upper()
    for banned in ("PROFITABLE", "EDGE CONFIRMED", "READY FOR LIVE",
                   "APPROVED FOR PAPER", "APPROVED FOR LIVE"):
        assert banned not in label.upper(), banned


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(c17.__file__, encoding="utf-8").read()
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
