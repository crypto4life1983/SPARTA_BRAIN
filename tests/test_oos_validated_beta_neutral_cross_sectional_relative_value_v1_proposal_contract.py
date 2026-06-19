"""Tests for the Candidate #19 family-proposal contract
(oos_validated_beta_neutral_cross_sectional_relative_value_v1).

Verifies: research-only, pure-proposal-only, executes nothing; chain-gated on the
valid C19 recommendation (its preferred direction is exactly this family); a
MARKET-NEUTRAL, return-space, dollar+beta-neutral relative-value family NOT in the
C1-C18 (23) ledger; OOS neutrality validation is GATE ZERO before any trading logic;
cached BTC/ETH/SOL D1-only universe (no fetch, no XAUUSD / new instrument class);
materially different from C1-C18 (esp. C16/C17/C18); six sub-approaches; market-neutral
+ risk-adjusted + forward-OOS evaluation with 37 bps reserved for replay; preserves the
gate sequence; downstream gates locked; does NOT start C20; capability flags + scope
locks; validator anti-tamper; module purity."""
from __future__ import annotations

import ast

import sparta_commander.oos_validated_beta_neutral_cross_sectional_relative_value_v1_proposal_contract as c19p  # noqa: E501
import sparta_commander.research_expansion_plan_v1_contract as rep


_R = c19p.build_c19_proposal(".", [])


def test_proposal_frozen_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_pure_proposal_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"] == "C19_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW"
    assert c19p.validate_c19_proposal(_R)["valid"] is True


def test_candidate_identity():
    assert _R["candidate_id"] == "C19"
    assert _R["candidate_family"] == (
        "oos_validated_beta_neutral_cross_sectional_relative_value")
    assert _R["candidate_name"].endswith("_v1")


def test_chain_gated_on_c19_recommendation():
    assert _R["recommendation_valid"] is True
    assert _R["recommendation_preferred_key"] == _R["candidate_family"]
    assert _R["promoted_from_recommendation"] == (
        "c19_research_direction_recommendation_v1")
    bad = {**_R, "recommendation_preferred_key": "something_else"}
    assert c19p.validate_c19_proposal(bad)["valid"] is False


def test_market_neutral_return_space_no_buy_and_hold_beta():
    assert _R["is_market_neutral"] is True
    assert _R["is_return_space"] is True
    assert _R["is_dollar_neutral"] is True
    assert _R["is_beta_neutral"] is True
    assert _R["carries_buy_and_hold_beta"] is False
    assert _R["is_directional_timing_signal"] is False
    bad = {**_R, "carries_buy_and_hold_beta": True}
    assert c19p.validate_c19_proposal(bad)["valid"] is False


def test_oos_neutrality_is_gate_zero():
    assert _R["oos_neutrality_validation_is_gate_zero"] is True
    gz = _R["oos_neutrality_gate_zero"]
    assert gz["is_gate_zero"] is True
    assert gz["no_trading_logic_until_neutrality_validated_oos"] is True
    assert gz["fixes_c16_failure"] is True
    bad = {**_R, "oos_neutrality_gate_zero": {
        **gz, "no_trading_logic_until_neutrality_validated_oos": False}}
    assert c19p.validate_c19_proposal(bad)["valid"] is False


def test_universe_cached_btc_eth_sol_d1_no_fetch_no_new_instrument():
    assert _R["universe"] == ["BTCUSD", "ETHUSD", "SOLUSD"]
    assert _R["timeframe"] == "D1"
    assert _R["no_new_data_fetch"] is True
    assert _R["no_new_instrument_class"] is True
    dr = _R["data_requirements"]
    assert dr["btc_eth_sol_d1_spot"]["available_locally"] is True
    assert dr["no_data_fetched_here"] is True
    assert dr["no_xauusd_or_new_instrument_class"] is True


def test_not_in_rejected_ledger_and_materially_different():
    assert _R["candidate_family"] not in set(rep.REJECTED_FAMILIES_C1_TO_C18)
    assert _R["candidate_not_in_rejected_ledger"] is True
    assert _R["rejected_families_count"] == 23
    diffs = " ".join(_R["why_different_from_c1_c18"])
    for must in ("C16", "C17", "C18"):
        assert must in diffs, must
    assert len(_R["why_different_from_c1_c18"]) >= 5


def test_six_sub_approaches_incl_gate_zero_estimation():
    subs = {s["key"] for s in _R["sub_approaches"]}
    assert len(_R["sub_approaches"]) == 6
    for must in ("oos_validated_return_beta_hedge_estimation",
                 "pairwise_beta_neutral_residual_reversion",
                 "cross_sectional_rank_residual_reversion",
                 "asset_vs_basket_beta_neutral_residual_reversion",
                 "rolling_neutrality_recalibration",
                 "neutral_residual_zscore_entry_exit"):
        assert must in subs, must


def test_evaluation_market_neutral_and_cost_reserved():
    em = _R["evaluation_metrics"]
    assert "net_residual_beta" in em["primary_market_neutral"]
    for m in ("sharpe_ratio", "calmar_ratio", "max_drawdown"):
        assert m in em["risk_adjusted"]
    assert "random" in em["win_condition"].lower()
    assert em["neutrality_is_precondition"] is True
    assert _R["cost_assumptions"]["all_in_round_trip_bps"] == 37.0
    assert _R["cost_assumptions"]["cost_applied_only_at_replay_gate"] is True


def test_oos_required_no_optimization():
    oos = _R["oos_validation"]
    assert oos["forward_oos_required"] is True
    assert oos["neutrality_validated_oos_first"] is True
    assert oos["no_parameter_optimization"] is True


def test_gate_sequence_preserved_downstream_locked_no_c20():
    assert _R["gate_sequence"] == [
        "family_proposal", "candidate_spec", "detector_spec_dry_run",
        "real_candle_labels_review", "fee_honest_replay_review",
        "rejection_or_promote_decision"]
    assert _R["does_not_start_c20"] is True
    assert _R["c20_candidate_id"] is None
    for gate in ("spec_gate_locked", "detector_gate_locked", "labels_gate_locked",
                 "replay_gate_locked", "paper_trading_gate_locked",
                 "live_gate_locked"):
        assert _R[gate] is True, gate
        bad = {**_R, gate: False}
        assert c19p.validate_c19_proposal(bad)["valid"] is False, gate


def test_next_action_is_spec_gate():
    nra = c19p.get_candidate_19_proposal_next_action()
    assert nra == _R["next_required_action"]
    assert nra == "HUMAN_DECISION_C19_ADVANCE_TO_CANDIDATE_SPEC_OR_REJECT"


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in c19p._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert c19p.validate_c19_proposal(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_build", "no_detector", "no_labels", "no_replay",
                 "no_optimization", "no_tuning", "no_rescue", "no_data_fetch",
                 "no_new_instrument_class", "no_xauusd", "no_net_market_beta",
                 "no_trade_before_neutrality_validated", "no_paper_trading",
                 "no_live_trading", "no_start_c20"):
        assert _R["scope_locks"][must] is True, must


def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(c19p.__file__, encoding="utf-8").read()
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
