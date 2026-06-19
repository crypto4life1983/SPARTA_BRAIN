"""Tests for the Candidate #19 detector spec + synthetic dry-run contract
(oos_validated_beta_neutral_cross_sectional_relative_value_v1).

Verifies: research-only, synthetic-dry-run-only, executes nothing; chain-gated on the
frozen C19 candidate spec; the detector implements the EXACT return-space market-neutral
params (90D beta window, 60D OOS neutrality gate zero at |net beta| <= 0.10, z-window 60,
enter |z| >= 2.0, exit |z| <= 0.25, stop |z| >= 4.0, gross <= 1.0, >= 5-bar spacing, one
live position) with NO price-level hedge; runs on DETERMINISTIC SYNTHETIC fixtures only
(no real data / fetch / XAUUSD / labels / replay / cost); the eight required proof
scenarios hold; 37 bps reserved for replay; downstream gates locked; does NOT start C20;
capability flags + scope locks; validator anti-tamper; module purity."""
from __future__ import annotations

import ast

import sparta_commander.oos_validated_beta_neutral_cross_sectional_relative_value_v1_detector_spec_dry_run_contract as d19  # noqa: E501


_R = d19.build_c19_detector_dry_run(".", [])
_DRY = d19.run_synthetic_dry_run()


def test_dry_run_frozen_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_synthetic_dry_run_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"] == "C19_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW"
    assert d19.validate_c19_detector_dry_run(_R)["valid"] is True


def test_candidate_identity_and_chain_gate():
    assert _R["candidate_id"] == "C19"
    assert _R["candidate_family"] == (
        "oos_validated_beta_neutral_cross_sectional_relative_value")
    assert _R["spec_valid"] is True
    assert _R["spec_verdict"] == "C19_SPEC_FROZEN_FOR_HUMAN_REVIEW"


def test_exact_params_implemented():
    assert _R["beta_estimation_window_bars"] == 90
    assert _R["oos_neutrality_window_bars"] == 60
    assert _R["net_residual_beta_tolerance"] == 0.10
    assert _R["residual_zscore_window_bars"] == 60
    assert _R["entry_zscore_threshold"] == 2.0
    assert _R["exit_zscore_threshold"] == 0.25
    assert _R["stop_zscore_threshold"] == 4.0
    assert _R["max_gross_exposure"] == 1.0
    assert _R["min_bars_between_rebalances"] == 5
    assert _R["is_market_neutral"] is True
    assert _R["is_return_space"] is True
    assert _R["uses_price_level_hedge"] is False
    assert _R["oos_neutrality_is_gate_zero"] is True


def test_synthetic_only_no_real_data():
    assert _R["uses_synthetic_fixtures_only"] is True
    assert _R["uses_real_data"] is False
    assert _R["uses_xauusd"] is False
    assert _R["no_new_data_fetch"] is True
    assert set(_R["synthetic_fixtures"]) == {
        "valid_trade", "neutrality_fail", "weak", "enter_exit", "divergence_stop",
        "spacing"}


# ---- the eight required synthetic proof scenarios --------------------------

def test_all_eight_proof_checks_pass():
    assert _DRY["all_checks_pass"] is True
    for c in ("valid_neutral_passes_and_trades",
              "neutrality_failure_blocks_all_trading", "weak_residual_no_trade",
              "extreme_enters_then_exits_on_reversion", "divergence_stop_invalidates",
              "rebalance_spacing_prevents_overtrading", "gross_exposure_capped",
              "one_live_position_no_overlap"):
        assert _DRY["checks"][c] is True, c


def test_1_valid_neutral_passes_and_trades():
    r = _DRY["results"]["valid_trade"]
    assert r["neutrality_passed"] is True
    assert abs(r["net_beta_oos"]) <= 0.10
    assert len(r["trades"]) >= 1


def test_2_neutrality_failure_blocks_all_trading_before_entry():
    r = _DRY["results"]["neutrality_fail"]
    assert r["neutrality_passed"] is False
    assert abs(r["net_beta_oos"]) > 0.10
    assert r["blocked_before_entry"] is True
    assert r["entry_logic_reached"] is False
    assert r["trades"] == []


def test_3_weak_residual_creates_no_trade():
    r = _DRY["results"]["weak"]
    assert r["neutrality_passed"] is True
    assert r["trades"] == []


def test_4_extreme_enters_then_exits_on_mean_reversion():
    r = _DRY["results"]["enter_exit"]
    assert len(r["trades"]) == 1
    assert r["trades"][0]["exit_reason"] == "mean_reversion"
    assert abs(r["trades"][0]["entry_z"]) >= 2.0


def test_5_divergence_stop_invalidates_position():
    r = _DRY["results"]["divergence_stop"]
    assert len(r["trades"]) == 1
    assert r["trades"][0]["exit_reason"] == "divergence_stop"
    assert abs(r["trades"][0]["exit_z"]) >= 4.0


def test_6_rebalance_spacing_prevents_overtrading():
    r = _DRY["results"]["spacing"]
    bars = sorted(t["entry_bar"] for t in r["trades"])
    assert len(bars) >= 1
    for a, b in zip(bars[:-1], bars[1:]):
        assert b - a >= 5, (a, b)


def test_7_gross_exposure_cap_respected():
    for name, r in _DRY["results"].items():
        assert r["gross"] <= 1.0 + 1e-9, name


def test_8_one_live_position_no_overlap():
    for name, r in _DRY["results"].items():
        assert r["max_concurrent_positions"] <= 1, name


def test_detector_is_deterministic():
    a = d19.run_detector(*[d19.build_synthetic_fixtures()["enter_exit"][k]
                           for k in ("rb", "re", "rs")])
    b = d19.run_detector(*[d19.build_synthetic_fixtures()["enter_exit"][k]
                           for k in ("rb", "re", "rs")])
    assert a["b1"] == b["b1"] and a["b2"] == b["b2"]
    assert len(a["trades"]) == len(b["trades"])


# ---- cost reserved + locks + no C20 ----------------------------------------

def test_cost_reserved_not_applied():
    assert _R["cost_model_reserved_for_replay"] is True
    assert _R["cost_model_applied_here"] is False
    assert _R["all_in_round_trip_bps_reserved"] == 37.0


def test_next_action_and_downstream_locked_no_c20():
    assert _R["next_required_action"] == (
        "HUMAN_DECISION_C19_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT")
    assert _R["does_not_start_c20"] is True
    assert _R["c20_candidate_id"] is None
    for gate in ("labels_gate_locked", "replay_gate_locked",
                 "paper_trading_gate_locked", "live_gate_locked"):
        assert _R[gate] is True, gate
        bad = {**_R, gate: False}
        assert d19.validate_c19_detector_dry_run(bad)["valid"] is False, gate


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in d19._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert d19.validate_c19_detector_dry_run(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_data_fetch", "no_real_candles", "no_xauusd", "no_labels",
                 "no_replay", "no_cost_application", "no_optimization", "no_tuning",
                 "no_rescue", "no_price_level_hedge",
                 "no_trade_before_neutrality_validated", "no_overlapping_positions",
                 "no_paper_trading", "no_live_trading", "no_start_c20"):
        assert _R["scope_locks"][must] is True, must


def test_validator_rejects_dry_run_check_tamper():
    bad_checks = {**_R["dry_run_checks"],
                  "neutrality_failure_blocks_all_trading": False}
    bad = {**_R, "dry_run_checks": bad_checks}
    assert d19.validate_c19_detector_dry_run(bad)["valid"] is False


def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(d19.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch(", "open(", "subprocess", "Popen"):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
              "subprocess", "websockets", "aiohttp", "schedule", "threading",
              "asyncio", "telegram", "csv", "hashlib", "os", "io", "shutil",
              "ssl", "ftplib", "pathlib", "datetime", "numpy", "pandas"}
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
