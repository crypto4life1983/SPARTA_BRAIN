"""Tests for the Candidate #21 family-proposal contract
(low_turnover_same_asset_spot_perp_funding_carry_v1).

Verifies: research-only, pure-proposal-only, executes nothing; chain-gated on the
FROZEN_AND_READY data-readiness review; a LOW-TURNOVER mechanically-neutral same-asset
spot/perp funding-carry family NOT in the C1-C20 (25) ledger; mechanical (not estimated)
neutrality is gate zero; low turnover / hold persistence is a first-class design
constraint; carry (not buy-and-hold beta, not OHLCV timing) return source; built ON the
preserved C20 lesson but NOT a rescue/retune of C20 (C20 stays rejected); frozen public
spot/perp/funding-only universe (no fetch, no XAUUSD/new instrument); materially different
from C20 + the rest; six low-turnover sub-families; market-neutral + risk-adjusted +
turnover-efficient + forward-OOS evaluation judged vs random/null (NOT buy-and-hold) with
37 bps + perp frictions reserved for replay; preserves the gate sequence; downstream gates
locked; does NOT start C22; capability flags + scope locks; validator anti-tamper; module
purity."""
from __future__ import annotations

import ast

import sparta_commander.low_turnover_same_asset_spot_perp_funding_carry_v1_proposal_contract as c21p  # noqa: E501
import sparta_commander.research_expansion_plan_v1_contract as rep


_R = c21p.build_c21_proposal(".", [])


def test_proposal_frozen_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_pure_proposal_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"] == "C21_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW"
    assert c21p.validate_c21_proposal(_R)["valid"] is True


def test_candidate_identity():
    assert _R["candidate_id"] == "C21"
    assert _R["candidate_family"] == (
        "low_turnover_same_asset_spot_perp_funding_carry")
    assert _R["candidate_name"].endswith("_v1")


def test_chain_gated_on_frozen_dataset():
    assert _R["data_readiness_valid"] is True
    assert _R["data_readiness_verdict"] == (
        "FROZEN_AND_READY_FOR_RESEARCH_ONLY_BASIS_FUNDING_STUDY")
    assert _R["promoted_from_data_readiness_review"] == (
        "crypto_basis_funding_data_readiness_review_v1")
    bad = {**_R, "data_readiness_verdict": "SOMETHING_ELSE"}
    assert c21p.validate_c21_proposal(bad)["valid"] is False


def test_low_turnover_mechanically_neutral_carry_not_timing():
    assert _R["is_market_neutral"] is True
    assert _R["is_mechanically_neutral_same_asset"] is True
    assert _R["is_estimated_cross_asset_neutral"] is False
    assert _R["return_source_is_carry_not_timing"] is True
    assert _R["is_low_turnover"] is True
    assert _R["prioritizes_hold_persistence"] is True
    assert _R["carries_buy_and_hold_beta"] is False
    assert _R["is_directional_timing_signal"] is False
    lt = _R["low_turnover_design_principle"]
    assert lt["is_first_class_design_constraint"] is True
    assert lt["prioritizes_hold_persistence"] is True
    assert lt["entry_exit_sparse_and_cost_aware_from_the_start"] is True
    for bad_flag, val in (("is_low_turnover", False),
                          ("prioritizes_hold_persistence", False),
                          ("is_estimated_cross_asset_neutral", True)):
        bad = {**_R, bad_flag: val}
        assert c21p.validate_c21_proposal(bad)["valid"] is False, bad_flag


def test_not_a_rescue_or_retune_of_c20_lesson_preserved():
    assert _R["is_rescue_or_retune_of_c20"] is False
    assert _R["c20_remains_rejected"] is True
    lp = _R["c20_lesson_preserved"]
    assert lp["carry_source_is_real"] is True
    assert lp["c20_failed_due_to_churn_cost_not_signal"] is True
    assert lp["always_on_neutral_carry_net_return"] == 0.211648
    assert lp["always_on_neutral_carry_sharpe"] == 1.087808
    assert lp["btc_eth_carry_strongest"] is True
    assert lp["c20_status"] == "REJECTED_AT_FEE_HONEST_REPLAY_KEPT_ON_RECORD"
    assert lp["c21_is_rescue_or_retune_of_c20"] is False
    # cannot flip to a C20 rescue/retune or drop the preserved lesson
    bad = {**_R, "is_rescue_or_retune_of_c20": True}
    assert c21p.validate_c21_proposal(bad)["valid"] is False
    bad2 = {**_R, "c20_remains_rejected": False}
    assert c21p.validate_c21_proposal(bad2)["valid"] is False


def test_materially_different_from_c1_c20():
    assert _R["candidate_family"] not in set(rep.REJECTED_FAMILIES_C1_TO_C20)
    assert _R["candidate_not_in_rejected_ledger"] is True
    assert _R["rejected_families_count"] == 25
    diffs = " ".join(_R["why_different_from_c1_c20"])
    for must in ("C20", "LOW-TURNOVER", "PERSISTENCE", "CARRY"):
        assert must in diffs, must
    # explicitly contrasts with C20's high-turnover / 704 round-trips
    assert "704" in diffs or "round-trip" in diffs.lower()


def test_universe_frozen_public_no_fetch_no_new_instrument():
    assert _R["universe"] == ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    assert _R["timeframe"] == "D1"
    assert _R["uses_frozen_public_spot_perp_funding_only"] is True
    assert _R["no_new_data_fetch"] is True
    assert _R["no_new_instrument_class"] is True
    dr = _R["data_requirements"]
    assert dr["spot_perp_funding_d1"]["available_locally"] is True
    assert dr["no_data_fetched_here"] is True
    assert dr["no_xauusd_or_new_instrument_class"] is True


def test_six_low_turnover_sub_families():
    subs = {s["key"] for s in _R["sub_families"]}
    assert len(_R["sub_families"]) == 6
    for must in ("persistent_positive_carry_hold", "carry_regime_gated_hold",
                 "funding_threshold_hysteresis_hold", "slow_periodic_rebalanced_carry",
                 "top_carry_asset_concentration_hold",
                 "always_on_carry_with_breakdown_circuit_breaker"):
        assert must in subs, must


def test_evaluation_turnover_aware_vs_random_null_cost_reserved():
    em = _R["evaluation_metrics"]
    assert "net_price_beta_mechanical" in em["primary_market_neutral"]
    for m in ("sharpe_ratio", "calmar_ratio", "max_drawdown"):
        assert m in em["risk_adjusted"]
    assert "round_trips_per_year" in em["turnover_efficiency"]
    assert em["low_turnover_is_evaluation_dimension"] is True
    assert "random" in em["win_condition"].lower()
    assert em["judged_against_buy_and_hold"] is False
    ct = _R["cost_assumptions"]
    assert ct["all_in_round_trip_bps"] == 37.0
    assert ct["round_trip_cost_per_trade_bps"] == 74.0
    assert ct["applied_here"] is False
    assert ct["cost_applied_only_at_replay_gate"] is True
    assert ct["perp_specific_frictions_reserved_for_replay"]


def test_oos_required_mechanical_neutrality_low_turnover_no_optimization():
    oos = _R["oos_validation"]
    assert oos["forward_oos_required"] is True
    assert oos["neutrality_is_mechanical_so_cannot_fail_oos"] is True
    assert oos["forward_oos_must_hold_low_turnover"] is True
    assert oos["no_parameter_optimization"] is True


def test_gate_sequence_downstream_locked_no_c22():
    assert _R["gate_sequence"] == [
        "family_proposal", "candidate_spec", "detector_spec_dry_run",
        "real_candle_labels_review", "fee_honest_replay_review",
        "rejection_or_promote_decision"]
    assert _R["does_not_start_c22"] is True
    assert _R["c22_candidate_id"] is None
    for gate in ("spec_gate_locked", "detector_gate_locked", "labels_gate_locked",
                 "replay_gate_locked", "paper_trading_gate_locked",
                 "live_gate_locked"):
        assert _R[gate] is True, gate
        bad = {**_R, gate: False}
        assert c21p.validate_c21_proposal(bad)["valid"] is False, gate


def test_next_action_is_spec_gate():
    nra = c21p.get_candidate_21_proposal_next_action()
    assert nra == _R["next_required_action"]
    assert nra == "HUMAN_DECISION_C21_ADVANCE_TO_CANDIDATE_SPEC_OR_REJECT"


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in c21p._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert c21p.validate_c21_proposal(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_build", "no_detector", "no_labels", "no_replay",
                 "no_optimization", "no_tuning", "no_rescue", "no_rescue_c20",
                 "no_retune_c20", "no_data_fetch", "no_new_instrument_class",
                 "no_xauusd", "no_net_market_beta", "no_estimated_cross_asset_hedge",
                 "no_paper_trading", "no_live_trading", "no_start_c22"):
        assert _R["scope_locks"][must] is True, must


def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(c21p.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch(", "open(", "subprocess", "Popen"):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
              "subprocess", "websockets", "aiohttp", "schedule", "threading",
              "asyncio", "telegram", "csv", "hashlib", "os", "io", "shutil",
              "ssl", "ftplib", "pathlib", "datetime", "random", "numpy", "pandas"}
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
