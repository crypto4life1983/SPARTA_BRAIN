"""Tests for the Candidate #20 family-proposal contract
(mechanically_neutral_spot_perp_basis_funding_carry_v1).

Verifies: research-only, pure-proposal-only, executes nothing; chain-gated on the
FROZEN_AND_READY data-readiness review; a MECHANICALLY-neutral same-asset spot/perp
basis-funding-carry family NOT in the C1-C19 (24) ledger; mechanical (not estimated)
neutrality is gate zero; carry (not buy-and-hold beta, not OHLCV timing) return source;
frozen public spot/perp/funding-only universe (no fetch, no XAUUSD/new instrument);
materially different from C1-C19 (esp. C16/C17/C18/C19); six sub-families; market-neutral
+ risk-adjusted + forward-OOS evaluation judged vs random/null (NOT buy-and-hold) with 37
bps + perp frictions reserved for replay; preserves the gate sequence; downstream gates
locked; does NOT start C21; capability flags + scope locks; validator anti-tamper;
module purity."""
from __future__ import annotations

import ast

import sparta_commander.mechanically_neutral_spot_perp_basis_funding_carry_v1_proposal_contract as c20p  # noqa: E501
import sparta_commander.research_expansion_plan_v1_contract as rep


_R = c20p.build_c20_proposal(".", [])


def test_proposal_frozen_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_pure_proposal_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"] == "C20_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW"
    assert c20p.validate_c20_proposal(_R)["valid"] is True


def test_candidate_identity():
    assert _R["candidate_id"] == "C20"
    assert _R["candidate_family"] == (
        "mechanically_neutral_spot_perp_basis_funding_carry")
    assert _R["candidate_name"].endswith("_v1")


def test_chain_gated_on_frozen_dataset():
    assert _R["data_readiness_valid"] is True
    assert _R["data_readiness_verdict"] == (
        "FROZEN_AND_READY_FOR_RESEARCH_ONLY_BASIS_FUNDING_STUDY")
    assert _R["promoted_from_data_readiness_review"] == (
        "crypto_basis_funding_data_readiness_review_v1")
    bad = {**_R, "data_readiness_verdict": "SOMETHING_ELSE"}
    assert c20p.validate_c20_proposal(bad)["valid"] is False


def test_mechanically_neutral_same_asset_carry_not_beta():
    assert _R["is_market_neutral"] is True
    assert _R["is_mechanically_neutral_same_asset"] is True
    assert _R["is_estimated_cross_asset_neutral"] is False
    assert _R["return_source_is_carry_not_timing"] is True
    assert _R["carries_buy_and_hold_beta"] is False
    assert _R["is_directional_timing_signal"] is False
    gz = _R["mechanical_neutrality_gate_zero"]
    assert gz["is_gate_zero"] is True
    assert gz["neutrality_is_mechanical_not_estimated"] is True
    assert gz["fixes_c16_c19_estimated_neutrality_failure"] is True
    for bad_flag, val in (("carries_buy_and_hold_beta", True),
                          ("is_estimated_cross_asset_neutral", True),
                          ("is_mechanically_neutral_same_asset", False)):
        bad = {**_R, bad_flag: val}
        assert c20p.validate_c20_proposal(bad)["valid"] is False, bad_flag


def test_materially_different_from_c1_c19():
    assert _R["candidate_family"] not in set(rep.REJECTED_FAMILIES_C1_TO_C19)
    assert _R["candidate_not_in_rejected_ledger"] is True
    assert _R["rejected_families_count"] == 24
    diffs = " ".join(_R["why_different_from_c1_c19"])
    for must in ("buy-and-hold", "ESTIMATED", "CARRY", "MECHANICAL"):
        assert must in diffs, must


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


def test_six_sub_families():
    subs = {s["key"] for s in _R["sub_families"]}
    assert len(_R["sub_families"]) == 6
    for must in ("funding_carry_directional", "basis_zscore_mean_reversion",
                 "funding_extreme_fade", "basis_term_structure_regime",
                 "cross_symbol_basis_relative_value",
                 "funding_carry_with_basis_divergence_stop"):
        assert must in subs, must


def test_evaluation_vs_random_null_not_buy_and_hold_cost_reserved():
    em = _R["evaluation_metrics"]
    assert "net_price_beta_mechanical" in em["primary_market_neutral"]
    for m in ("sharpe_ratio", "calmar_ratio", "max_drawdown"):
        assert m in em["risk_adjusted"]
    assert "random" in em["win_condition"].lower()
    assert em["judged_against_buy_and_hold"] is False
    ct = _R["cost_assumptions"]
    assert ct["all_in_round_trip_bps"] == 37.0
    assert ct["applied_here"] is False
    assert ct["cost_applied_only_at_replay_gate"] is True
    assert ct["perp_specific_frictions_reserved_for_replay"]


def test_oos_required_mechanical_neutrality_no_optimization():
    oos = _R["oos_validation"]
    assert oos["forward_oos_required"] is True
    assert oos["neutrality_is_mechanical_so_cannot_fail_oos"] is True
    assert oos["no_parameter_optimization"] is True


def test_gate_sequence_downstream_locked_no_c21():
    assert _R["gate_sequence"] == [
        "family_proposal", "candidate_spec", "detector_spec_dry_run",
        "real_candle_labels_review", "fee_honest_replay_review",
        "rejection_or_promote_decision"]
    assert _R["does_not_start_c21"] is True
    assert _R["c21_candidate_id"] is None
    for gate in ("spec_gate_locked", "detector_gate_locked", "labels_gate_locked",
                 "replay_gate_locked", "paper_trading_gate_locked",
                 "live_gate_locked"):
        assert _R[gate] is True, gate
        bad = {**_R, gate: False}
        assert c20p.validate_c20_proposal(bad)["valid"] is False, gate


def test_next_action_is_spec_gate():
    nra = c20p.get_candidate_20_proposal_next_action()
    assert nra == _R["next_required_action"]
    assert nra == "HUMAN_DECISION_C20_ADVANCE_TO_CANDIDATE_SPEC_OR_REJECT"


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in c20p._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert c20p.validate_c20_proposal(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_build", "no_detector", "no_labels", "no_replay",
                 "no_optimization", "no_tuning", "no_rescue", "no_data_fetch",
                 "no_new_instrument_class", "no_xauusd", "no_net_market_beta",
                 "no_estimated_cross_asset_hedge", "no_paper_trading",
                 "no_live_trading", "no_start_c21"):
        assert _R["scope_locks"][must] is True, must


def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(c20p.__file__, encoding="utf-8").read()
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
