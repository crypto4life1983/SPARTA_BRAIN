"""Tests for the Candidate #21 detector spec + synthetic dry-run contract
(low_turnover_same_asset_spot_perp_funding_carry_v1).

Verifies: research-only, synthetic-dry-run-only, executes nothing on real data;
chain-gated on the frozen C21 spec; implements the exact LOW-TURNOVER carry-regime
params (30-bar carry window, 100 bps enter, 7-bar durable breakdown, 20-bar min hold,
30-bar cadence, 6/yr round-trip ceiling) with MECHANICAL (not estimated) neutrality as
gate zero and NO basis-z / NO drawdown stop; the detector behaves correctly on all ten
deterministic synthetic fixtures (no real data, fetch, XAUUSD, labels, replay, cost);
NOT a rescue/retune of C20 (C20 stays rejected); the 37/74 bps cost stays reserved for
replay; downstream gates locked; the next gate is real-candle labels approval/rejection
only; does NOT start C22; capability flags + scope locks; validator anti-tamper; module
purity. Deterministic."""
from __future__ import annotations

import ast

import sparta_commander.low_turnover_same_asset_spot_perp_funding_carry_v1_detector_spec_dry_run_contract as d21  # noqa: E501


_R = d21.build_c21_detector_dry_run(".", [])
_DRY = d21.run_synthetic_dry_run()


def test_dry_run_frozen_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_synthetic_dry_run_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"] == "C21_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW"
    assert d21.validate_c21_detector_dry_run(_R)["valid"] is True


def test_candidate_identity_and_chain_gate():
    assert _R["candidate_id"] == "C21"
    assert _R["candidate_family"] == (
        "low_turnover_same_asset_spot_perp_funding_carry")
    assert _R["spec_valid"] is True
    assert _R["spec_verdict"] == "C21_SPEC_FROZEN_FOR_HUMAN_REVIEW"
    bad = {**_R, "spec_verdict": "X"}
    assert d21.validate_c21_detector_dry_run(bad)["valid"] is False


def test_exact_low_turnover_params_implemented():
    assert _R["carry_regime_window_bars"] == 30
    assert _R["annualized_carry_enter_bps"] == 100.0
    assert _R["carry_regime_breakdown_bars"] == 7
    assert _R["min_hold_bars"] == 20
    assert _R["rebalance_cadence_bars"] == 30
    assert _R["max_round_trips_per_year_per_asset"] == 6
    assert _R["max_gross_exposure"] == 1.0
    assert _R["basis_formula"] == "(perp_close - spot_close) / spot_close"
    bad = {**_R, "min_hold_bars": 1}
    assert d21.validate_c21_detector_dry_run(bad)["valid"] is False


def test_mechanical_neutral_low_turnover_no_basis_z_no_drawdown_stop():
    assert _R["is_market_neutral"] is True
    assert _R["is_mechanically_neutral_same_asset"] is True
    assert _R["is_estimated_cross_asset_neutral"] is False
    assert _R["return_source_is_carry_not_timing"] is True
    assert _R["is_low_turnover"] is True
    assert _R["is_high_turnover"] is False
    assert _R["uses_basis_z_stop"] is False
    assert _R["uses_drawdown_stop"] is False
    assert _R["mechanical_neutrality_is_gate_zero"] is True
    for bad_flag, val in (("is_high_turnover", True),
                          ("uses_basis_z_stop", True),
                          ("uses_drawdown_stop", True),
                          ("is_estimated_cross_asset_neutral", True)):
        bad = {**_R, bad_flag: val}
        assert d21.validate_c21_detector_dry_run(bad)["valid"] is False, bad_flag


def test_not_a_rescue_of_c20():
    assert _R["is_rescue_or_retune_of_c20"] is False
    assert _R["c20_remains_rejected"] is True
    bad = {**_R, "is_rescue_or_retune_of_c20": True}
    assert d21.validate_c21_detector_dry_run(bad)["valid"] is False


# ---- the ten synthetic proof checks ----------------------------------------

def test_all_ten_dry_run_checks_pass():
    assert _DRY["all_checks_pass"] is True
    assert _R["dry_run_all_checks_pass"] is True
    for c in ("persistent_carry_creates_long_hold", "carry_below_threshold_no_entry",
              "negative_carry_regime_no_entry", "durable_breakdown_exit_works",
              "transient_dip_does_not_exit", "min_hold_blocks_early_exit",
              "cadence_respected_between_trades",
              "low_turnover_round_trips_under_ceiling",
              "mechanical_neutrality_gate_zero_blocks_non_same_asset",
              "no_basis_z_or_drawdown_stop_used"):
        assert _R["dry_run_checks"][c] is True, c
        bad_checks = {**_R["dry_run_checks"], c: False}
        bad = {**_R, "dry_run_checks": bad_checks}
        assert d21.validate_c21_detector_dry_run(bad)["valid"] is False, c


def test_persistent_carry_creates_a_long_hold():
    r = _DRY["results"]["persistent_carry_hold"]
    assert len(r["trades"]) == 1
    t = r["trades"][0]
    assert t["entry_reason"] == "carry_regime"
    assert t["exit_reason"] == "end_of_data"
    assert t["hold_bars"] >= 20    # a genuinely long hold (low turnover)


def test_below_threshold_and_negative_regime_no_entry():
    assert len(_DRY["results"]["carry_below_threshold"]["trades"]) == 0
    assert len(_DRY["results"]["negative_carry_regime"]["trades"]) == 0


def test_durable_breakdown_exits_transient_dip_holds():
    db = _DRY["results"]["durable_breakdown_exit"]["trades"]
    assert len(db) == 1 and db[0]["exit_reason"] == "durable_carry_regime_breakdown"
    td = _DRY["results"]["transient_dip_no_exit"]["trades"]
    # a < 7-bar dip never triggers a breakdown exit -> the position is held to the end
    assert len(td) == 1 and td[0]["exit_reason"] == "end_of_data"


def test_min_hold_blocks_early_exit():
    # the breakdown counter reaches 7 bars after entry, but the exit is held off until
    # the minimum hold (>= 20 bars) -- proving persistence, not churn.
    mh = _DRY["results"]["min_hold_blocks_early_exit"]["trades"]
    assert len(mh) == 1
    assert mh[0]["exit_reason"] == "durable_carry_regime_breakdown"
    assert mh[0]["hold_bars"] >= 20


def test_cadence_respected_and_blocks_premature_reentry():
    cb = _DRY["results"]["cadence_blocks_reentry"]
    assert len(cb["trades"]) >= 2
    # the cadence rule prevented premature churn: blocked re-entry attempts were
    # recorded, and every re-entry is spaced >= the 30-bar cadence after the exit
    assert cb["blocked_by_cadence"] > 0
    for i in range(len(cb["trades"]) - 1):
        assert (cb["trades"][i + 1]["entry_bar"]
                - cb["trades"][i]["exit_bar"]) >= 30


def test_low_turnover_round_trips_under_ceiling():
    for r in _DRY["results"].values():
        assert r["round_trips_per_year"] <= 6 + 1e-9


def test_no_basis_z_or_drawdown_stop_ever_used():
    # the only exit reasons are durable carry-regime breakdown or end-of-data -- never
    # a basis-z divergence stop or a drawdown stop (those are explicitly forbidden)
    for r in _DRY["results"].values():
        for er in r["exit_reasons"]:
            assert er in ("durable_carry_regime_breakdown", "end_of_data"), er


def test_mechanical_neutrality_gate_zero_blocks_non_same_asset():
    na = _DRY["results"]["non_same_asset_blocked"]
    assert na["mechanical_neutrality_ok"] is False
    assert na["blocked_before_entry"] is True
    assert len(na["trades"]) == 0
    for name, r in _DRY["results"].items():
        if name == "non_same_asset_blocked":
            continue
        assert r["mechanical_neutrality_ok"] is True
        assert r["gross"] <= 1.0 + 1e-9
        assert r["max_concurrent_positions"] <= 1


def test_basis_is_diagnostic_same_asset_formula():
    spot = [100.0, 100.0, 100.0]
    perp = [101.0, 100.0, 99.0]
    assert d21._basis_series(spot, perp) == [0.01, 0.0, -0.01]


def test_carry_regime_gate_threshold():
    # 30 bars of +0.0002 funding -> annualized carry well above the 100 bps gate
    carry = d21._annualized_carry_bps([0.0002] * 40, 40)
    assert carry > 100.0
    # weak funding -> below the 100 bps gate
    weak = d21._annualized_carry_bps([0.00001] * 40, 40)
    assert weak < 100.0


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
    assert _R["round_trip_cost_per_trade_bps_reserved"] == 74.0
    assert _R["perp_frictions_reserved_for_replay"] is True
    bad = {**_R, "cost_model_applied_here": True}
    assert d21.validate_c21_detector_dry_run(bad)["valid"] is False


# ---- gate sequence + downstream locks + no C22 -----------------------------

def test_next_action_is_labels_gate_and_no_c22():
    nra = d21.get_candidate_21_detector_dry_run_next_action()
    assert nra == _R["next_required_action"]
    assert nra == "HUMAN_DECISION_C21_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT"
    assert _R["does_not_start_c22"] is True
    assert _R["c22_candidate_id"] is None
    for gate in ("labels_gate_locked", "replay_gate_locked",
                 "paper_trading_gate_locked", "live_gate_locked"):
        assert _R[gate] is True, gate
        bad = {**_R, gate: False}
        assert d21.validate_c21_detector_dry_run(bad)["valid"] is False, gate


def test_anti_loop_not_in_rejected_ledger():
    assert _R["rejected_families_count"] == 25
    assert _R["candidate_not_in_rejected_ledger"] is True


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in d21._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert d21.validate_c21_detector_dry_run(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_build", "no_data_fetch", "no_real_candles", "no_xauusd",
                 "no_labels", "no_replay", "no_cost_application", "no_optimization",
                 "no_tuning", "no_rescue", "no_rescue_c20", "no_high_turnover",
                 "no_basis_z_stop", "no_drawdown_stop",
                 "no_estimated_cross_asset_hedge", "no_overlapping_positions",
                 "no_paper_trading", "no_live_trading", "no_start_c22"):
        assert _R["scope_locks"][must] is True, must


def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(d21.__file__, encoding="utf-8").read()
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
