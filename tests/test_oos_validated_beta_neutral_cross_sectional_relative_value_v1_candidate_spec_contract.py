"""Tests for the Candidate #19 candidate-spec contract
(oos_validated_beta_neutral_cross_sectional_relative_value_v1).

Verifies: research-only, pure-spec-only, executes nothing; chain-gated on the frozen
C19 proposal for this exact family; a MARKET-NEUTRAL, return-space, dollar+beta-neutral
relative-value strategy carrying no buy-and-hold beta and not using a price-level
hedge; OOS neutrality validation is GATE ZERO; defines all seven exact rules (residual
/ gate-zero neutrality / entry / exit / stop & invalidation / turnover / non-overlap);
cached BTC/ETH/SOL D1-only universe (no fetch, no XAUUSD / new instrument class);
explains the difference from C16 / C17 / C18; market-neutral + risk-adjusted +
forward-OOS evaluation judged vs random/null (NOT buy-and-hold) with 37 bps reserved
for replay; preserves the gate sequence; downstream gates locked; does NOT start C20;
capability flags + scope locks; validator anti-tamper; module purity."""
from __future__ import annotations

import ast

import sparta_commander.oos_validated_beta_neutral_cross_sectional_relative_value_v1_candidate_spec_contract as c19s  # noqa: E501


_R = c19s.build_c19_spec(".", [])


def test_spec_frozen_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_pure_spec_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"] == "C19_SPEC_FROZEN_FOR_HUMAN_REVIEW"
    assert c19s.validate_c19_spec(_R)["valid"] is True


def test_candidate_identity():
    assert _R["candidate_id"] == "C19"
    assert _R["candidate_family"] == (
        "oos_validated_beta_neutral_cross_sectional_relative_value")
    assert _R["candidate_name"].endswith("_v1")


def test_chain_gated_on_frozen_c19_proposal():
    assert _R["source_proposal_valid"] is True
    assert _R["source_proposal_verdict"] == "C19_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW"
    assert _R["source_proposal_family"] == _R["candidate_family"]
    bad = {**_R, "source_proposal_verdict": "SOMETHING_ELSE"}
    assert c19s.validate_c19_spec(bad)["valid"] is False


def test_market_neutral_return_space_no_buy_and_hold_beta():
    assert _R["is_market_neutral"] is True
    assert _R["is_return_space"] is True
    assert _R["is_dollar_neutral"] is True
    assert _R["is_beta_neutral"] is True
    assert _R["carries_buy_and_hold_beta"] is False
    assert _R["uses_price_level_hedge"] is False
    for bad_flag, bad_val in (("carries_buy_and_hold_beta", True),
                              ("uses_price_level_hedge", True),
                              ("is_market_neutral", False)):
        bad = {**_R, bad_flag: bad_val}
        assert c19s.validate_c19_spec(bad)["valid"] is False, bad_flag


def test_all_seven_exact_rules_present():
    for rule in ("residual_calculation_rule", "oos_neutrality_gate_zero_rule",
                 "entry_rule", "exit_rule", "stop_invalidation_rule",
                 "turnover_constraint_rule", "non_overlap_rule"):
        assert _R[rule], rule
        bad = {**_R, rule: ""}
        assert c19s.validate_c19_spec(bad)["valid"] is False, rule
    # the gate-zero rule really is gate zero (before trading logic)
    assert "GATE ZERO" in _R["oos_neutrality_gate_zero_rule"]
    assert "before" in _R["oos_neutrality_gate_zero_rule"].lower()
    # the residual rule explicitly avoids the C16 level-OLS hedge
    assert "level" in _R["residual_calculation_rule"].lower()


def test_spec_params_declared_not_optimized():
    sp = _R["spec_params"]
    assert sp["return_space"] is True
    assert sp["dollar_neutral"] is True and sp["beta_neutral"] is True
    assert sp["net_residual_beta_tolerance"] == 0.10
    assert sp["max_gross_exposure"] == 1.0
    assert sp["no_parameter_optimization"] is True
    assert sp["no_parameter_tuning"] is True
    assert sp["no_rescue_variant"] is True
    bad = {**_R, "spec_params": {**sp, "net_residual_beta_tolerance": 0.9}}
    assert c19s.validate_c19_spec(bad)["valid"] is False


def test_universe_cached_d1_no_fetch_no_new_instrument():
    assert _R["universe"] == ["BTCUSD", "ETHUSD", "SOLUSD"]
    assert _R["timeframe"] == "D1"
    assert _R["no_new_data_fetch"] is True
    assert _R["no_new_instrument_class"] is True
    dr = _R["data_requirements"]
    assert dr["btc_eth_sol_d1_spot"]["available_locally"] is True
    assert dr["no_data_fetched_here"] is True
    assert dr["no_xauusd_or_new_instrument_class"] is True


def test_difference_from_c16_c17_c18_explained():
    diff = _R["difference_from_rejected"]
    assert "level" in diff["vs_c16_level_ols_hedge"].lower()
    assert "long-only" in diff["vs_c17_long_only_allocation"].lower() or (
        "long only" in diff["vs_c17_long_only_allocation"].lower())
    assert "beta" in diff["vs_c18_long_biased_timing"].lower()


def test_evaluation_market_neutral_not_vs_buy_and_hold():
    em = _R["evaluation_metrics"]
    assert "net_residual_beta" in em["primary_market_neutral"]
    for m in ("sharpe_ratio", "calmar_ratio", "max_drawdown"):
        assert m in em["risk_adjusted"]
    assert "random" in em["win_condition"].lower()
    assert em["neutrality_is_precondition"] is True
    assert em["judged_against_buy_and_hold"] is False
    assert _R["cost_reserved"]["all_in_round_trip_bps"] == 37.0
    assert _R["cost_reserved"]["applied_here"] is False


def test_rejection_criteria_gate_zero_and_market_neutral():
    rc = _R["rejection_criteria"]
    assert rc["reject_if_oos_neutrality_fails"] is True
    assert rc["reject_if_not_net_positive_vs_random_null"] is True
    assert rc["reject_if_forward_oos_edge_fails"] is True
    assert rc["raw_return_alone_is_not_sufficient"] is True
    assert rc["not_judged_against_buy_and_hold"] is True


def test_oos_validation_neutrality_first_no_optimization():
    oos = _R["oos_validation"]
    assert oos["forward_oos_required"] is True
    assert oos["neutrality_validated_oos_first"] is True
    assert oos["no_parameter_optimization"] is True


def test_gate_sequence_downstream_locked_no_c20():
    assert _R["gate_sequence"] == [
        "family_proposal", "candidate_spec", "detector_spec_dry_run",
        "real_candle_labels_review", "fee_honest_replay_review",
        "rejection_or_promote_decision"]
    assert _R["does_not_start_c20"] is True
    assert _R["c20_candidate_id"] is None
    for gate in ("detector_gate_locked", "labels_gate_locked", "replay_gate_locked",
                 "paper_trading_gate_locked", "live_gate_locked"):
        assert _R[gate] is True, gate
        bad = {**_R, gate: False}
        assert c19s.validate_c19_spec(bad)["valid"] is False, gate


def test_next_action_is_detector_gate():
    nra = c19s.get_candidate_19_spec_next_action()
    assert nra == _R["next_required_action"]
    assert nra == "HUMAN_DECISION_C19_ADVANCE_TO_DETECTOR_SPEC_DRY_RUN_OR_REJECT"


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in c19s._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert c19s.validate_c19_spec(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_build", "no_detector", "no_labels", "no_replay",
                 "no_optimization", "no_tuning", "no_rescue", "no_data_fetch",
                 "no_new_instrument_class", "no_xauusd", "no_net_market_beta",
                 "no_trade_before_neutrality_validated", "no_price_level_hedge",
                 "no_overlapping_positions", "no_paper_trading", "no_live_trading",
                 "no_start_c20"):
        assert _R["scope_locks"][must] is True, must


def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(c19s.__file__, encoding="utf-8").read()
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
