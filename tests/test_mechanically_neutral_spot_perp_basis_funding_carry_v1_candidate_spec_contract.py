"""Tests for the Candidate #20 candidate-spec contract
(mechanically_neutral_spot_perp_basis_funding_carry_v1).

Verifies: research-only, pure-spec-only, executes nothing; chain-gated on the frozen
C20 proposal for this exact family; a MARKET-NEUTRAL, SAME-ASSET basis/funding-carry
strategy whose neutrality is MECHANICAL (not estimated) carrying no buy-and-hold beta
and no estimated cross-asset hedge, with a CARRY (not OHLCV-timing) return source;
mechanical neutrality is GATE ZERO; defines all nine exact rules (basis / funding /
gate-zero mechanical neutrality / entry / exit / stop & invalidation / turnover /
non-overlap / replay win criteria); frozen BTC/ETH/SOL D1 spot+perp+funding-only
universe (no fetch, no XAUUSD / new instrument class); explains the difference from
C16 / C17 / C18 / C19; market-neutral + risk-adjusted + forward-OOS evaluation judged
vs random/null (NOT buy-and-hold) with 37 bps + perp-specific frictions reserved for
replay; preserves the gate sequence; downstream gates locked; does NOT start C21;
capability flags + scope locks; validator anti-tamper; module purity."""
from __future__ import annotations

import ast

import sparta_commander.mechanically_neutral_spot_perp_basis_funding_carry_v1_candidate_spec_contract as c20s  # noqa: E501


_R = c20s.build_c20_spec(".", [])


def test_spec_frozen_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_pure_spec_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"] == "C20_SPEC_FROZEN_FOR_HUMAN_REVIEW"
    assert c20s.validate_c20_spec(_R)["valid"] is True


def test_candidate_identity():
    assert _R["candidate_id"] == "C20"
    assert _R["candidate_family"] == (
        "mechanically_neutral_spot_perp_basis_funding_carry")
    assert _R["candidate_name"].endswith("_v1")


def test_chain_gated_on_frozen_c20_proposal():
    assert _R["source_proposal_valid"] is True
    assert _R["source_proposal_verdict"] == "C20_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW"
    assert _R["source_proposal_family"] == _R["candidate_family"]
    bad = {**_R, "source_proposal_verdict": "SOMETHING_ELSE"}
    assert c20s.validate_c20_spec(bad)["valid"] is False


def test_mechanically_neutral_same_asset_carry_not_beta():
    assert _R["is_market_neutral"] is True
    assert _R["is_mechanically_neutral_same_asset"] is True
    assert _R["is_estimated_cross_asset_neutral"] is False
    assert _R["return_source_is_carry_not_timing"] is True
    assert _R["carries_buy_and_hold_beta"] is False
    assert _R["is_directional_timing_signal"] is False
    for bad_flag, bad_val in (("carries_buy_and_hold_beta", True),
                              ("is_estimated_cross_asset_neutral", True),
                              ("is_mechanically_neutral_same_asset", False),
                              ("is_directional_timing_signal", True)):
        bad = {**_R, bad_flag: bad_val}
        assert c20s.validate_c20_spec(bad)["valid"] is False, bad_flag


def test_all_nine_exact_rules_present():
    for rule in ("basis_calculation_rule", "funding_calculation_rule",
                 "mechanical_neutrality_gate_zero_rule", "entry_rule", "exit_rule",
                 "stop_invalidation_rule", "turnover_constraint_rule",
                 "non_overlap_rule", "replay_win_criteria"):
        assert _R[rule], rule
        bad = {**_R, rule: ""}
        assert c20s.validate_c20_spec(bad)["valid"] is False, rule
    # the gate-zero rule really is gate zero (before trading logic)
    assert "GATE ZERO" in _R["mechanical_neutrality_gate_zero_rule"]
    assert "before" in _R["mechanical_neutrality_gate_zero_rule"].lower()
    # the basis rule is a SAME-ASSET relative basis (spot vs perp of the same asset)
    assert "basis" in _R["basis_calculation_rule"].lower()
    assert "perp" in _R["basis_calculation_rule"].lower()
    assert "spot" in _R["basis_calculation_rule"].lower()
    # the funding rule is about the short-perp leg earning/paying funding
    assert "funding" in _R["funding_calculation_rule"].lower()
    assert "short" in _R["funding_calculation_rule"].lower()
    # the replay win criteria are cost-honest and vs random/null, not buy-and-hold
    assert "random" in _R["replay_win_criteria"].lower()
    assert "buy-and-hold" in _R["replay_win_criteria"].lower()


def test_spec_params_declared_not_optimized():
    sp = _R["spec_params"]
    assert sp["same_asset_legs"] is True
    assert sp["equal_notional_legs"] is True
    assert sp["net_price_beta_target"] == 0.0
    assert sp["max_gross_exposure"] == 1.0
    assert sp["no_parameter_optimization"] is True
    assert sp["no_parameter_tuning"] is True
    assert sp["no_rescue_variant"] is True
    bad = {**_R, "spec_params": {**sp, "net_price_beta_target": 0.9}}
    assert c20s.validate_c20_spec(bad)["valid"] is False


def test_universe_frozen_d1_no_fetch_no_new_instrument():
    assert _R["universe"] == ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    assert _R["timeframe"] == "D1"
    assert _R["no_new_data_fetch"] is True
    assert _R["no_new_instrument_class"] is True
    dr = _R["data_requirements"]
    assert dr["spot_perp_funding_d1"]["available_locally"] is True
    assert dr["no_data_fetched_here"] is True
    assert dr["no_xauusd_or_new_instrument_class"] is True


def test_difference_from_c16_c17_c18_c19_explained():
    diff = _R["difference_from_rejected"]
    assert "mechanical" in diff["vs_c16_level_ols_estimated_neutrality"].lower()
    assert "estimate" in diff["vs_c19_return_beta_estimated_neutrality"].lower() or (
        "mechanical" in diff["vs_c19_return_beta_estimated_neutrality"].lower())
    assert "long-only" in diff["vs_c17_long_only_allocation"].lower() or (
        "long only" in diff["vs_c17_long_only_allocation"].lower())
    assert "carry" in diff["vs_c18_long_biased_timing"].lower()


def test_evaluation_market_neutral_not_vs_buy_and_hold():
    em = _R["evaluation_metrics"]
    assert "net_price_beta_mechanical" in em["primary_market_neutral"]
    for m in ("sharpe_ratio", "calmar_ratio", "max_drawdown"):
        assert m in em["risk_adjusted"]
    assert "random" in em["win_condition"].lower()
    assert em["neutrality_is_mechanical_precondition"] is True
    assert em["judged_against_buy_and_hold"] is False
    ct = _R["cost_reserved"]
    assert ct["all_in_round_trip_bps"] == 37.0
    assert ct["applied_here"] is False
    assert ct["applied_at_replay_gate_only"] is True
    assert ct["perp_specific_frictions_reserved_for_replay"]
    assert ct["two_legs_spot_and_perp_so_cost_counts_double_per_rebalance"] is True


def test_rejection_criteria_gate_zero_and_market_neutral():
    rc = _R["rejection_criteria"]
    assert rc["reject_if_not_mechanically_neutral"] is True
    assert rc["reject_if_not_net_positive_vs_random_null"] is True
    assert rc["reject_if_forward_oos_edge_fails"] is True
    assert rc["reject_if_carry_does_not_cover_two_leg_and_perp_costs"] is True
    assert rc["raw_carry_alone_is_not_sufficient"] is True
    assert rc["not_judged_against_buy_and_hold"] is True


def test_oos_validation_mechanical_neutrality_no_optimization():
    oos = _R["oos_validation"]
    assert oos["forward_oos_required"] is True
    assert oos["neutrality_is_mechanical_so_cannot_fail_oos"] is True
    assert oos["no_parameter_optimization"] is True


def test_six_sub_families_carried():
    subs = set(_R["sub_families"])
    assert len(_R["sub_families"]) == 6
    for must in ("funding_carry_directional", "basis_zscore_mean_reversion",
                 "funding_extreme_fade", "basis_term_structure_regime",
                 "cross_symbol_basis_relative_value",
                 "funding_carry_with_basis_divergence_stop"):
        assert must in subs, must


def test_gate_sequence_downstream_locked_no_c21():
    assert _R["gate_sequence"] == [
        "family_proposal", "candidate_spec", "detector_spec_dry_run",
        "real_candle_labels_review", "fee_honest_replay_review",
        "rejection_or_promote_decision"]
    assert _R["does_not_start_c21"] is True
    assert _R["c21_candidate_id"] is None
    for gate in ("detector_gate_locked", "labels_gate_locked", "replay_gate_locked",
                 "paper_trading_gate_locked", "live_gate_locked"):
        assert _R[gate] is True, gate
        bad = {**_R, gate: False}
        assert c20s.validate_c20_spec(bad)["valid"] is False, gate


def test_next_action_is_detector_gate():
    nra = c20s.get_candidate_20_spec_next_action()
    assert nra == _R["next_required_action"]
    assert nra == "HUMAN_DECISION_C20_ADVANCE_TO_DETECTOR_SPEC_DRY_RUN_OR_REJECT"


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in c20s._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert c20s.validate_c20_spec(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_build", "no_detector", "no_labels", "no_replay",
                 "no_optimization", "no_tuning", "no_rescue", "no_data_fetch",
                 "no_new_instrument_class", "no_xauusd", "no_net_market_beta",
                 "no_estimated_cross_asset_hedge",
                 "no_trade_before_neutrality_validated",
                 "no_overlapping_positions", "no_paper_trading", "no_live_trading",
                 "no_start_c21"):
        assert _R["scope_locks"][must] is True, must


def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(c20s.__file__, encoding="utf-8").read()
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
