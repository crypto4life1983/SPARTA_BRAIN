"""Tests for the Candidate #17 candidate-spec contract
(risk_adjusted_portfolio_construction_vol_targeted_allocation_v1).

Verifies: research-only, pure-spec-only, executes nothing; chain-gated on the
committed C17 proposal (frozen, this exact family); the candidate is materially
different from C1-C16 (portfolio construction / risk, NOT timing); all 16 required
spec sections present (universe / timeframe / method / weighting / rebalance / vol
lookback / risk target / gross cap / turnover / costs / baselines / primary +
secondary metrics / OOS / rejection criteria / next gate); the 37 bps cost model;
buy-and-hold + equal-weight baselines; risk-adjusted rejection criteria; downstream
gates locked; capability flags + scope locks; validator anti-tamper; module purity."""
from __future__ import annotations

import ast

import sparta_commander.risk_adjusted_portfolio_construction_vol_targeted_allocation_v1_candidate_spec_contract as c17  # noqa: E501


_R = c17.build_c17_spec(".", [])


# ---- core: research-only, pure, frozen, validates --------------------------

def test_spec_frozen_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_pure_spec_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"] == "C17_SPEC_FROZEN_FOR_HUMAN_REVIEW"
    assert c17.validate_c17_spec(_R)["valid"] is True


def test_candidate_identity():
    assert _R["candidate_id"] == "C17"
    assert _R["candidate_family"] == (
        "risk_adjusted_portfolio_construction_vol_targeted_allocation")
    assert _R["candidate_name"] == (
        "risk_adjusted_portfolio_construction_vol_targeted_allocation_v1")


# ---- chain gate on the committed C17 proposal ------------------------------

def test_chain_gated_on_frozen_c17_proposal():
    assert _R["source_proposal_verdict"] == "C17_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW"
    assert _R["source_proposal_valid"] is True
    assert _R["source_proposal_family"] == (
        "risk_adjusted_portfolio_construction_vol_targeted_allocation")
    bad = {**_R, "source_proposal_verdict": "C17_PROPOSAL_BLOCKED"}
    assert c17.validate_c17_spec(bad)["valid"] is False


def test_gate_sequence_preserved():
    assert _R["gate_sequence"] == [
        "family_proposal", "candidate_spec", "detector_spec_dry_run",
        "real_candle_labels_review", "fee_honest_replay_review",
        "rejection_or_promote_decision"]


# ---- material difference from C1-C16 (the whole point) ---------------------

def test_materially_different_from_c1_c16():
    assert _R["is_portfolio_construction"] is True
    assert _R["is_volatility_targeted"] is True
    assert _R["is_risk_parity"] is True
    assert _R["is_directional_timing_signal"] is False
    assert _R["is_market_neutral_pairs"] is False
    assert _R["candidate_not_in_rejected_ledger"] is True
    md = " || ".join(_R["material_difference_from_c1_c16"]).lower()
    assert "allocation" in md or "risk" in md
    assert "risk-adjusted" in md
    assert "timing" in md
    for bad_key in ("is_directional_timing_signal", "is_market_neutral_pairs"):
        bad = {**_R, bad_key: True}
        assert c17.validate_c17_spec(bad)["valid"] is False, bad_key


# ---- 1/2/3 universe / timeframe / method -----------------------------------

def test_universe_timeframe_method():
    assert _R["symbols"] == ["BTCUSD", "ETHUSD", "SOLUSD"]
    assert _R["timeframe"] == "D1"
    assert _R["portfolio_method"] == "volatility_targeted_risk_parity_allocation"
    bad = {**_R, "timeframe": "H1"}
    assert c17.validate_c17_spec(bad)["valid"] is False


# ---- 4-9 weighting / rebalance / vol lookback / risk target / cap / turnover

def test_spec_params_present():
    sp = _R["spec_params"]
    assert sp["weighting_rule"]                          # 4
    assert sp["rebalance_cadence"] == "weekly"           # 5
    assert sp["realized_vol_lookback_days"] == 30        # 6
    assert sp["target_portfolio_vol_annualized"] == 0.20  # 7
    assert sp["max_gross_exposure"] == 1.0               # 8
    assert sp["allow_short"] is False
    assert sp["allow_leverage_above_cap"] is False
    assert sp["max_avg_weekly_turnover"] == 0.20         # 9
    assert sp["one_edit_allowance_used"] is False
    assert _R["turnover_constraints"]["no_high_frequency_churn"] is True
    for bad_sp in ({"max_gross_exposure": 2.0}, {"allow_short": True},
                   {"allow_leverage_above_cap": True}):
        bad = {**_R, "spec_params": {**sp, **bad_sp}}
        assert c17.validate_c17_spec(bad)["valid"] is False, bad_sp


# ---- 10 cost model (37 bps) ------------------------------------------------

def test_cost_model_intact():
    assert _R["all_in_round_trip_bps"] == 37.0
    assert _R["fee_round_trip_bps"] + _R["slippage_round_trip_bps"] == 37.0
    assert _R["cost_assumptions"]["all_in_round_trip_bps"] == 37.0
    assert _R["cost_assumptions"]["cost_scales_with_turnover"] is True
    bad = {**_R, "all_in_round_trip_bps": 5.0}
    assert c17.validate_c17_spec(bad)["valid"] is False


# ---- 11 baselines: buy-and-hold + equal-weight basket ----------------------

def test_baselines_required():
    br = _R["baselines_required"]
    assert br["buy_and_hold_per_asset"]["required"] is True
    assert br["equal_weight_basket"]["required"] is True
    bad = {**_R, "baselines_required": {
        **br, "equal_weight_basket": {"required": False}}}
    assert c17.validate_c17_spec(bad)["valid"] is False


# ---- 12/13 primary + secondary metrics -------------------------------------

def test_primary_and_secondary_metrics():
    assert _R["primary_metrics"] == ["sharpe_ratio", "calmar_ratio", "max_drawdown"]
    for m in ("net_return", "turnover", "fee_drag", "stability"):
        assert m in _R["secondary_metrics"], m
    bad = {**_R, "primary_metrics": ["net_return"]}   # raw return is not primary
    assert c17.validate_c17_spec(bad)["valid"] is False


# ---- 14 OOS validation -----------------------------------------------------

def test_oos_validation_required():
    oos = _R["oos_validation"]
    assert oos["forward_oos_required"] is True
    assert oos["forward_oos_must_hold_risk_adjusted_edge"] is True
    assert oos["no_parameter_optimization"] is True
    assert oos["durability_window_days"] == 1095
    assert oos["recent_relevance_window_days_min"] == 90
    assert oos["recent_relevance_window_days_max"] == 180
    bad = {**_R, "oos_validation": {**oos, "forward_oos_required": False}}
    assert c17.validate_c17_spec(bad)["valid"] is False


# ---- 15 rejection criteria (risk-adjusted; raw return insufficient) --------

def test_rejection_criteria():
    rc = _R["rejection_criteria"]
    assert rc["reject_if_not_beat_buy_and_hold_risk_adjusted"] is True
    assert rc["reject_if_not_beat_equal_weight_basket_risk_adjusted"] is True
    assert rc["reject_if_max_drawdown_worse_than_buy_and_hold"] is True
    assert rc["reject_if_forward_oos_risk_adjusted_edge_fails"] is True
    assert rc["raw_return_alone_is_not_sufficient"] is True
    bad = {**_R, "rejection_criteria": {
        **rc, "raw_return_alone_is_not_sufficient": False}}
    assert c17.validate_c17_spec(bad)["valid"] is False


# ---- 16 next human gate after spec -----------------------------------------

def test_next_human_gate_after_spec():
    nra = c17.get_candidate_17_spec_next_action()
    assert nra == _R["next_required_action"]
    assert nra == _R["next_human_gate_after_spec"]
    assert nra == "HUMAN_DECISION_C17_ADVANCE_TO_DETECTOR_SPEC_DRY_RUN_OR_REJECT"
    for banned in ("PAPER", "LIVE", "EXECUTE", "BROKER", "ORDER", "FETCH",
                   "REPLAY", "PNL"):
        assert banned not in nra.upper(), banned


# ---- downstream gates locked + capability flags + scope locks --------------

def test_downstream_gates_locked():
    for gate in ("detector_gate_locked", "labels_gate_locked",
                 "replay_gate_locked", "paper_trading_gate_locked",
                 "live_gate_locked"):
        assert _R[gate] is True, gate
        bad = {**_R, gate: False}
        assert c17.validate_c17_spec(bad)["valid"] is False, gate


def test_ledger_21_anti_loop():
    assert _R["rejected_families_count"] == 21
    bad = {**_R, "rejected_families_count": 20}
    assert c17.validate_c17_spec(bad)["valid"] is False


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in c17._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert c17.validate_c17_spec(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_build", "no_data_fetch", "no_detector_run", "no_labels",
                 "no_replay", "no_backtest", "no_pnl", "no_optimization",
                 "no_commit", "no_push", "no_paper_trading", "no_live_trading",
                 "no_broker", "no_shorting", "no_leverage_above_cap"):
        assert _R["scope_locks"][must] is True, must


def test_label_no_profitability_claim():
    label = c17.get_candidate_17_spec_label()
    assert "RESEARCH ONLY" in label
    assert "NOT a profitability claim" in label or (
        "NOT A PROFITABILITY" in label.upper())
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
