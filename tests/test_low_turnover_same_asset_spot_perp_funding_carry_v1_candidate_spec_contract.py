"""Tests for the Candidate #21 candidate-spec contract
(low_turnover_same_asset_spot_perp_funding_carry_v1).

Verifies: research-only, pure-spec-only, executes nothing; chain-gated on the frozen C21
proposal for this exact family; a MARKET-NEUTRAL, LOW-TURNOVER, same-asset funding-carry
strategy whose neutrality is MECHANICAL (not estimated) carrying no buy-and-hold beta and
no estimated cross-asset hedge; NOT a rescue/retune of C20 (C20 stays rejected); defines
all nine exact rules (basis / funding / gate-zero neutrality / carry-regime gate /
entry-exit hysteresis / hold-persistence / turnover limit / durable-breakdown exit /
replay win criteria); a FINITE FROZEN config family (no optimization); frozen BTC/ETH/SOL
D1 spot+perp+funding-only universe (no fetch, no XAUUSD/new instrument); explains the
difference from C20 + C16/C17/C18/C19; turnover-efficient evaluation vs random/null AND
the always-on carry (NOT buy-and-hold) with 37 bps / 74 bps two-leg + perp frictions
reserved for replay; cannot be called profitable before full validation; preserves the
gate sequence; downstream gates locked; does NOT start C22; capability flags + scope
locks; validator anti-tamper; module purity."""
from __future__ import annotations

import ast

import sparta_commander.low_turnover_same_asset_spot_perp_funding_carry_v1_candidate_spec_contract as c21s  # noqa: E501


_R = c21s.build_c21_spec(".", [])


def test_spec_frozen_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_pure_spec_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"] == "C21_SPEC_FROZEN_FOR_HUMAN_REVIEW"
    assert c21s.validate_c21_spec(_R)["valid"] is True


def test_candidate_identity():
    assert _R["candidate_id"] == "C21"
    assert _R["candidate_family"] == (
        "low_turnover_same_asset_spot_perp_funding_carry")
    assert _R["candidate_name"].endswith("_v1")


def test_chain_gated_on_frozen_c21_proposal():
    assert _R["source_proposal_valid"] is True
    assert _R["source_proposal_verdict"] == "C21_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW"
    assert _R["source_proposal_family"] == _R["candidate_family"]
    bad = {**_R, "source_proposal_verdict": "SOMETHING_ELSE"}
    assert c21s.validate_c21_spec(bad)["valid"] is False


def test_low_turnover_mechanical_carry_not_high_turnover_timing():
    assert _R["is_market_neutral"] is True
    assert _R["is_mechanically_neutral_same_asset"] is True
    assert _R["is_estimated_cross_asset_neutral"] is False
    assert _R["return_source_is_carry_not_timing"] is True
    assert _R["is_low_turnover"] is True
    assert _R["prioritizes_hold_persistence"] is True
    assert _R["is_high_turnover"] is False
    assert _R["carries_buy_and_hold_beta"] is False
    for bad_flag, val in (("is_high_turnover", True),
                          ("is_low_turnover", False),
                          ("is_estimated_cross_asset_neutral", True)):
        bad = {**_R, bad_flag: val}
        assert c21s.validate_c21_spec(bad)["valid"] is False, bad_flag


def test_not_a_rescue_of_c20_lesson_preserved():
    assert _R["is_rescue_or_retune_of_c20"] is False
    assert _R["c20_remains_rejected"] is True
    lp = _R["c20_lesson_preserved"]
    assert lp["carry_source_is_real"] is True
    assert lp["c20_failed_due_to_churn_cost_not_signal"] is True
    bad = {**_R, "is_rescue_or_retune_of_c20": True}
    assert c21s.validate_c21_spec(bad)["valid"] is False
    bad2 = {**_R, "c20_remains_rejected": False}
    assert c21s.validate_c21_spec(bad2)["valid"] is False


def test_all_nine_exact_rules_present():
    for rule in ("basis_calculation_rule", "funding_calculation_rule",
                 "mechanical_neutrality_gate_zero_rule", "carry_regime_gate_rule",
                 "entry_exit_hysteresis_rule", "hold_persistence_rule",
                 "turnover_limit_rule", "durable_breakdown_exit_rule",
                 "replay_win_criteria"):
        assert _R[rule], rule
        bad = {**_R, rule: ""}
        assert c21s.validate_c21_spec(bad)["valid"] is False, rule
    # the gate-zero rule really is gate zero (before any carry/regime logic)
    assert "GATE ZERO" in _R["mechanical_neutrality_gate_zero_rule"]
    # hysteresis is wide (enter high, exit low)
    assert "hysteresis" in _R["entry_exit_hysteresis_rule"].lower()
    # hold-persistence enforces a minimum hold
    assert "min_hold_bars" in _R["hold_persistence_rule"]
    # exits only on a durable breakdown (consecutive negative bars)
    assert "consecutive" in _R["durable_breakdown_exit_rule"].lower()
    # the replay win criteria must BEAT the always-on carry, vs random/null, not B&H
    assert "always-on" in _R["replay_win_criteria"].lower()
    assert "random" in _R["replay_win_criteria"].lower()
    assert "buy-and-hold" in _R["replay_win_criteria"].lower()


def test_spec_params_finite_frozen_low_turnover_not_optimized():
    sp = _R["spec_params"]
    assert sp["same_asset_legs"] is True
    assert sp["equal_notional_legs"] is True
    assert sp["net_price_beta_target"] == 0.0
    assert sp["max_gross_exposure"] == 1.0
    assert sp["min_hold_bars"] > 0
    assert sp["max_round_trips_per_year_per_asset"] > 0
    # wide hysteresis: enter threshold strictly above exit threshold
    assert sp["annualized_carry_enter_bps"] > sp["annualized_carry_exit_bps"]
    assert sp["finite_frozen_config_family"] is True
    assert sp["no_parameter_optimization"] is True
    assert sp["no_parameter_tuning"] is True
    assert sp["no_rescue_variant"] is True
    # tamper: a narrow/inverted hysteresis band fails
    bad = {**_R, "spec_params": {**sp, "annualized_carry_enter_bps": 0.0}}
    assert c21s.validate_c21_spec(bad)["valid"] is False


def test_universe_frozen_d1_no_fetch_no_new_instrument():
    assert _R["universe"] == ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    assert _R["timeframe"] == "D1"
    assert _R["no_new_data_fetch"] is True
    assert _R["no_new_instrument_class"] is True
    dr = _R["data_requirements"]
    assert dr["spot_perp_funding_d1"]["available_locally"] is True
    assert dr["no_data_fetched_here"] is True
    assert dr["no_xauusd_or_new_instrument_class"] is True


def test_difference_from_c20_and_c16_c17_c18_c19():
    diff = _R["difference_from_rejected"]
    assert "turnover" in diff["vs_c20_high_turnover_timing"].lower()
    assert "704" in diff["vs_c20_high_turnover_timing"]
    assert "mechanical" in diff["vs_c16_c19_estimated_neutrality"].lower()
    assert "buy-and-hold" in diff["vs_c17_c18_long_biased"].lower()


def test_evaluation_turnover_aware_vs_null_and_always_on():
    em = _R["evaluation_metrics"]
    assert "net_price_beta_mechanical" in em["primary_market_neutral"]
    assert "round_trips_per_year" in em["turnover_efficiency"]
    assert em["must_beat_always_on_carry_after_cost"] is True
    for m in ("sharpe_ratio", "calmar_ratio", "max_drawdown"):
        assert m in em["risk_adjusted"]
    assert "random" in em["win_condition"].lower()
    assert em["low_turnover_is_evaluation_dimension"] is True
    assert em["judged_against_buy_and_hold"] is False
    assert em["cannot_be_called_profitable_before_full_validation"] is True
    ct = _R["cost_reserved"]
    assert ct["all_in_round_trip_bps"] == 37.0
    assert ct["round_trip_cost_per_trade_bps"] == 74.0
    assert ct["applied_here"] is False
    assert ct["applied_at_replay_gate_only"] is True
    assert ct["perp_specific_frictions_reserved_for_replay"]


def test_rejection_criteria_and_no_early_profit_claim():
    rc = _R["rejection_criteria"]
    assert rc["reject_if_not_mechanically_neutral"] is True
    assert rc["reject_if_does_not_beat_always_on_carry_after_cost"] is True
    assert rc["reject_if_turnover_or_cost_drag_too_high"] is True
    assert rc["reject_if_forward_oos_edge_fails"] is True
    assert rc["not_judged_against_buy_and_hold"] is True
    assert _R["cannot_be_called_profitable_before_full_validation"] is True
    assert _R["claims_profitability"] is False
    assert _R["claims_edge"] is False


def test_oos_required_mechanical_neutrality_low_turnover_no_optimization():
    oos = _R["oos_validation"]
    assert oos["forward_oos_required"] is True
    assert oos["neutrality_is_mechanical_so_cannot_fail_oos"] is True
    assert oos["forward_oos_must_hold_low_turnover"] is True
    assert oos["no_parameter_optimization"] is True


def test_six_sub_families_carried():
    subs = set(_R["sub_families"])
    assert len(_R["sub_families"]) == 6
    for must in ("persistent_positive_carry_hold", "carry_regime_gated_hold",
                 "funding_threshold_hysteresis_hold", "slow_periodic_rebalanced_carry",
                 "top_carry_asset_concentration_hold",
                 "always_on_carry_with_breakdown_circuit_breaker"):
        assert must in subs, must


def test_gate_sequence_downstream_locked_no_c22():
    assert _R["gate_sequence"] == [
        "family_proposal", "candidate_spec", "detector_spec_dry_run",
        "real_candle_labels_review", "fee_honest_replay_review",
        "rejection_or_promote_decision"]
    assert _R["does_not_start_c22"] is True
    assert _R["c22_candidate_id"] is None
    for gate in ("detector_gate_locked", "labels_gate_locked", "replay_gate_locked",
                 "paper_trading_gate_locked", "live_gate_locked"):
        assert _R[gate] is True, gate
        bad = {**_R, gate: False}
        assert c21s.validate_c21_spec(bad)["valid"] is False, gate


def test_next_action_is_detector_gate():
    nra = c21s.get_candidate_21_spec_next_action()
    assert nra == _R["next_required_action"]
    assert nra == "HUMAN_DECISION_C21_ADVANCE_TO_DETECTOR_SPEC_DRY_RUN_OR_REJECT"


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in c21s._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert c21s.validate_c21_spec(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_build", "no_detector", "no_labels", "no_replay",
                 "no_optimization", "no_tuning", "no_rescue", "no_rescue_c20",
                 "no_data_fetch", "no_new_instrument_class", "no_xauusd",
                 "no_net_market_beta", "no_estimated_cross_asset_hedge",
                 "no_high_turnover", "no_paper_trading", "no_live_trading",
                 "no_start_c22"):
        assert _R["scope_locks"][must] is True, must


def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(c21s.__file__, encoding="utf-8").read()
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
