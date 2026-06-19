"""Tests for the Candidate #20 detector spec + synthetic dry-run contract
(mechanically_neutral_spot_perp_basis_funding_carry_v1).

Verifies: research-only, synthetic-dry-run-only, executes nothing on real data;
chain-gated on the frozen C20 spec; implements the exact same-asset basis/funding-carry
params (60-bar basis z, 30-bar funding lookback, 2.0/0.25/4.0 thresholds, 50 bps carry
floor, gross 1.0, 5-bar spacing) with MECHANICAL (not estimated) neutrality as gate
zero; the detector behaves correctly on all ten deterministic synthetic fixtures (no
real data, no fetch, no XAUUSD, no labels, no replay, no cost applied); the 37 bps +
perp frictions stay reserved for replay; downstream gates locked; does NOT start C21;
capability flags + scope locks; validator anti-tamper; module purity."""
from __future__ import annotations

import ast

import sparta_commander.mechanically_neutral_spot_perp_basis_funding_carry_v1_detector_spec_dry_run_contract as d20  # noqa: E501


_R = d20.build_c20_detector_dry_run(".", [])
_DRY = d20.run_synthetic_dry_run()


def test_dry_run_frozen_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_synthetic_dry_run_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"] == "C20_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW"
    assert d20.validate_c20_detector_dry_run(_R)["valid"] is True


def test_candidate_identity():
    assert _R["candidate_id"] == "C20"
    assert _R["candidate_family"] == (
        "mechanically_neutral_spot_perp_basis_funding_carry")
    assert _R["candidate_name"].endswith("_v1")


def test_chain_gated_on_frozen_c20_spec():
    assert _R["spec_valid"] is True
    assert _R["spec_verdict"] == "C20_SPEC_FROZEN_FOR_HUMAN_REVIEW"
    bad = {**_R, "spec_verdict": "SOMETHING_ELSE"}
    assert d20.validate_c20_detector_dry_run(bad)["valid"] is False


def test_exact_params_implemented():
    assert _R["basis_zscore_window_bars"] == 60
    assert _R["funding_lookback_bars"] == 30
    assert _R["entry_basis_zscore_threshold"] == 2.0
    assert _R["entry_min_annualized_carry_bps"] == 50.0
    assert _R["exit_basis_zscore_threshold"] == 0.25
    assert _R["stop_basis_zscore_threshold"] == 4.0
    assert _R["max_gross_exposure"] == 1.0
    assert _R["min_bars_between_rebalances"] == 5
    assert _R["basis_formula"] == "(perp_close - spot_close) / spot_close"
    bad = {**_R, "entry_min_annualized_carry_bps": 5.0}
    assert d20.validate_c20_detector_dry_run(bad)["valid"] is False


def test_mechanical_neutral_identity_not_estimated_carry_not_timing():
    assert _R["is_market_neutral"] is True
    assert _R["is_mechanically_neutral_same_asset"] is True
    assert _R["is_estimated_cross_asset_neutral"] is False
    assert _R["return_source_is_carry_not_timing"] is True
    assert _R["mechanical_neutrality_is_gate_zero"] is True
    for bad_flag, bad_val in (("is_estimated_cross_asset_neutral", True),
                              ("is_mechanically_neutral_same_asset", False),
                              ("mechanical_neutrality_is_gate_zero", False)):
        bad = {**_R, bad_flag: bad_val}
        assert d20.validate_c20_detector_dry_run(bad)["valid"] is False, bad_flag


# ---- the ten synthetic proof checks ----------------------------------------

def test_all_ten_dry_run_checks_pass():
    assert _DRY["all_checks_pass"] is True
    assert _R["dry_run_all_checks_pass"] is True
    for c in ("funding_carry_creates_valid_neutral_setup",
              "basis_premium_creates_valid_convergence_setup",
              "negative_carry_regime_blocks_entry", "weak_basis_and_carry_no_trade",
              "convergence_exit_works", "divergence_stop_works",
              "gross_exposure_capped", "rebalance_spacing_prevents_overtrading",
              "one_live_position_per_asset_no_overlap",
              "mechanical_neutrality_uses_identical_asset_only"):
        assert _R["dry_run_checks"][c] is True, c
        bad_checks = {**_R["dry_run_checks"], c: False}
        bad = {**_R, "dry_run_checks": bad_checks}
        assert d20.validate_c20_detector_dry_run(bad)["valid"] is False, c


def test_funding_carry_creates_valid_setup():
    r = _DRY["results"]["funding_carry_valid"]
    assert r["mechanical_neutrality_ok"] is True
    assert len(r["trades"]) >= 1
    assert r["trades"][0]["entry_reason"] == "funding_carry"


def test_basis_premium_creates_convergence_setup():
    r = _DRY["results"]["basis_premium_valid"]
    assert r["mechanical_neutrality_ok"] is True
    assert len(r["trades"]) >= 1
    assert r["trades"][0]["entry_reason"] == "basis_convergence"


def test_negative_carry_and_weak_block_entry():
    assert len(_DRY["results"]["negative_carry_blocks"]["trades"]) == 0
    assert len(_DRY["results"]["weak_no_trade"]["trades"]) == 0


def test_convergence_exit_and_divergence_stop():
    cv = _DRY["results"]["convergence_exit"]["trades"]
    assert len(cv) == 1 and cv[0]["exit_reason"] == "convergence"
    dv = _DRY["results"]["divergence_stop"]["trades"]
    assert len(dv) == 1 and dv[0]["exit_reason"] == "divergence_stop"


def test_spacing_and_gross_and_non_overlap():
    sp = _DRY["results"]["spacing"]["trades"]
    assert len(sp) >= 2
    assert all((sp[i + 1]["entry_bar"] - sp[i]["entry_bar"]) >= 5
               for i in range(len(sp) - 1))
    for r in _DRY["results"].values():
        assert r["gross"] <= 1.0 + 1e-9
        assert r["max_concurrent_positions"] <= 1


def test_mechanical_neutrality_gate_zero_blocks_non_same_asset():
    na = _DRY["results"]["non_same_asset_blocked"]
    assert na["mechanical_neutrality_ok"] is False
    assert na["blocked_before_entry"] is True
    assert na["entry_logic_reached"] is False
    assert len(na["trades"]) == 0
    # the constructed (same-asset) fixtures are all mechanically neutral
    for name, r in _DRY["results"].items():
        if name == "non_same_asset_blocked":
            continue
        assert r["mechanical_neutrality_ok"] is True
        assert r["same_asset"] is True


def test_basis_formula_is_same_asset_relative():
    # (perp - spot) / spot computed on the IDENTICAL asset's series
    spot = [100.0, 100.0, 100.0]
    perp = [101.0, 100.0, 99.0]
    basis = d20._basis_series(spot, perp)
    assert basis == [0.01, 0.0, -0.01]


def test_funding_carry_short_perp_receives_when_positive():
    # annualized carry over the lookback window; positive funding -> positive carry
    funding = [0.0002] * 40
    carry = d20._annualized_carry_bps(funding, 40)
    assert carry > 0
    # 0.0002/day * 365 * 10000 bps
    assert abs(carry - 0.0002 * 365 * 10000) < 1e-6
    neg = d20._annualized_carry_bps([-0.0002] * 40, 40)
    assert neg < 0


# ---- determinism + synthetic-only + cost reserved --------------------------

def test_deterministic_synthetic_only_no_real_data():
    assert _DRY["checks"]["deterministic"] is True
    assert _R["uses_synthetic_fixtures_only"] is True
    assert _R["uses_real_data"] is False
    assert _R["uses_xauusd"] is False
    assert _R["no_new_data_fetch"] is True
    assert len(_R["synthetic_fixtures"]) == 8
    assert _R["dry_run_scenario_count"] == 8


def test_cost_reserved_for_replay_not_applied():
    assert _R["cost_model_applied_here"] is False
    assert _R["cost_model_reserved_for_replay"] is True
    assert _R["all_in_round_trip_bps_reserved"] == 37.0
    assert _R["perp_frictions_reserved_for_replay"] is True
    assert _DRY["checks"]["cost_model_not_applied"] is True
    bad = {**_R, "cost_model_applied_here": True}
    assert d20.validate_c20_detector_dry_run(bad)["valid"] is False


# ---- gate sequence + downstream locks + no C21 -----------------------------

def test_next_action_is_labels_gate_and_no_c21():
    nra = d20.get_candidate_20_detector_dry_run_next_action()
    assert nra == _R["next_required_action"]
    assert nra == "HUMAN_DECISION_C20_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT"
    assert _R["does_not_start_c21"] is True
    assert _R["c21_candidate_id"] is None
    for gate in ("labels_gate_locked", "replay_gate_locked",
                 "paper_trading_gate_locked", "live_gate_locked"):
        assert _R[gate] is True, gate
        bad = {**_R, gate: False}
        assert d20.validate_c20_detector_dry_run(bad)["valid"] is False, gate


def test_anti_loop_not_in_rejected_ledger():
    assert _R["rejected_families_count"] == 24
    assert _R["candidate_not_in_rejected_ledger"] is True


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in d20._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert d20.validate_c20_detector_dry_run(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_build", "no_data_fetch", "no_real_candles", "no_xauusd",
                 "no_labels", "no_replay", "no_cost_application", "no_optimization",
                 "no_tuning", "no_rescue", "no_estimated_cross_asset_hedge",
                 "no_net_market_beta", "no_trade_before_neutrality_validated",
                 "no_overlapping_positions", "no_paper_trading", "no_live_trading",
                 "no_start_c21"):
        assert _R["scope_locks"][must] is True, must


def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(d20.__file__, encoding="utf-8").read()
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
