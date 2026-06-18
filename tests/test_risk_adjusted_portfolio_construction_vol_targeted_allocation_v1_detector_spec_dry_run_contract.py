"""Tests for the Candidate #17 detector-spec + synthetic dry-run contract
(risk_adjusted_portfolio_construction_vol_targeted_allocation_v1).

Verifies: research-only, synthetic-only (NO real data / NO cost application),
executes nothing; chain-gated on the frozen C17 candidate spec; the allocator is a
long/flat vol-targeted risk-parity allocator (NOT a directional timing signal);
the synthetic dry-run proves inverse-vol weights ordered BTC>ETH>SOL, long-only (no
shorting), gross capped at 1.0 (no leverage), vol-target scaling down in high vol
and capped in calm, weekly rebalance with a no-trade band, turnover within cap,
near-equal risk contributions, the BTC/ETH/SOL universe only, and the 37 bps cost
RESERVED (not applied); downstream gates locked; capability flags + scope locks;
validator anti-tamper; module purity; determinism."""
from __future__ import annotations

import ast

import sparta_commander.risk_adjusted_portfolio_construction_vol_targeted_allocation_v1_detector_spec_dry_run_contract as d17  # noqa: E501


_R = d17.build_c17_detector_dry_run(".", [])


# ---- core: research-only, synthetic-only, frozen, validates ----------------

def test_dry_run_frozen_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_synthetic_dry_run_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"] == "C17_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW"
    assert d17.validate_c17_detector_dry_run(_R)["valid"] is True


def test_candidate_identity():
    assert _R["candidate_id"] == "C17"
    assert _R["candidate_family"] == (
        "risk_adjusted_portfolio_construction_vol_targeted_allocation")


# ---- chain gate on the frozen C17 spec -------------------------------------

def test_chain_gated_on_frozen_c17_spec():
    assert _R["spec_verdict"] == "C17_SPEC_FROZEN_FOR_HUMAN_REVIEW"
    assert _R["spec_valid"] is True
    bad = {**_R, "spec_verdict": "C17_SPEC_BLOCKED"}
    assert d17.validate_c17_detector_dry_run(bad)["valid"] is False


# ---- synthetic-only, no real data, no cost ---------------------------------

def test_synthetic_only_no_real_data_no_cost():
    assert _R["uses_synthetic_fixtures_only"] is True
    assert _R["uses_real_data"] is False
    assert _R["cost_model_applied_here"] is False
    assert _R["cost_model_reserved_for_replay"] is True
    assert _R["all_in_round_trip_bps_reserved"] == 37.0
    assert _R["runs_replay"] is False
    assert _R["computes_pnl"] is False
    assert _R["fetches_data"] is False
    assert _R["uses_real_candles"] is False


# ---- identity: long/flat vol-targeted risk-parity allocator ----------------

def test_allocator_identity_not_directional():
    assert _R["is_portfolio_allocator"] is True
    assert _R["is_volatility_targeted"] is True
    assert _R["is_risk_parity"] is True
    assert _R["is_long_or_flat"] is True
    assert _R["allows_shorting"] is False
    assert _R["allows_leverage_above_cap"] is False
    assert _R["is_directional_timing_signal"] is False
    for bad_key in ("allows_shorting", "allows_leverage_above_cap",
                    "is_directional_timing_signal"):
        bad = {**_R, bad_key: True}
        assert d17.validate_c17_detector_dry_run(bad)["valid"] is False, bad_key


# ---- the synthetic behaviour checks (the whole point) ----------------------

def test_all_synthetic_checks_pass():
    checks = _R["dry_run_checks"]
    for k in ("deterministic", "inverse_vol_orders_weights",
              "weights_nonnegative_no_shorting", "gross_exposure_le_cap",
              "gross_capped_at_one_in_calm", "vol_target_scales_down_in_high_vol",
              "weekly_rebalance_cadence", "no_trade_band_suppresses_churn",
              "avg_weekly_turnover_within_cap", "risk_contributions_near_equal",
              "universe_only_btc_eth_sol", "cost_model_not_applied",
              "no_entry_exit_signal_continuous_allocation"):
        assert checks[k] is True, k
    assert _R["dry_run_all_checks_pass"] is True
    # tamper: flipping any check to False invalidates
    bad = {**_R, "dry_run_checks": {**checks, "gross_capped_at_one_in_calm": False}}
    assert d17.validate_c17_detector_dry_run(bad)["valid"] is False


def test_inverse_vol_weights_order_btc_eth_sol():
    rep = _R["dry_run_representative_checkpoint"]
    iw = rep["inverse_vol_weights"]
    # lower-vol asset gets MORE weight: BTC > ETH > SOL
    assert iw["BTCUSD"] > iw["ETHUSD"] > iw["SOLUSD"]
    vols = rep["vols"]
    assert vols["BTCUSD"] < vols["ETHUSD"] < vols["SOLUSD"]


def test_gross_exposure_capped_and_long_only():
    cps = _R["dry_run_representative_checkpoint"]
    # representative is calm: uncapped scale would exceed 1.0 but gross capped at 1
    assert cps["uncapped_scale"] > 1.0
    assert cps["gross_exposure"] == 1.0
    for w in cps["weights"].values():
        assert w >= 0.0          # long-only / no shorting


def test_turnover_within_cap():
    assert _R["dry_run_avg_weekly_turnover"] <= 0.20
    assert _R["dry_run_n_skipped_by_band"] >= 1     # band suppressed churn
    bad = {**_R, "dry_run_avg_weekly_turnover": 0.9}
    assert d17.validate_c17_detector_dry_run(bad)["valid"] is False


# ---- universe / timeframe / params -----------------------------------------

def test_universe_timeframe_params():
    assert _R["assets"] == ["BTCUSD", "ETHUSD", "SOLUSD"]
    assert _R["timeframe"] == "D1"
    assert _R["max_gross_exposure"] == 1.0
    assert _R["target_portfolio_vol_annualized"] == 0.20
    assert _R["vol_lookback_days"] == 30
    assert _R["rebalance_every_days"] == 7
    bad = {**_R, "assets": ["BTCUSD", "ETHUSD"]}
    assert d17.validate_c17_detector_dry_run(bad)["valid"] is False


# ---- determinism -----------------------------------------------------------

def test_determinism():
    a = d17.run_synthetic_dry_run()
    b = d17.run_synthetic_dry_run()
    assert ([c["weights"] for c in a["checkpoints"]]
            == [c["weights"] for c in b["checkpoints"]])
    assert a["checks"]["deterministic"] is True


# ---- anti-loop + next gate -------------------------------------------------

def test_anti_loop_and_next_gate():
    assert _R["candidate_not_in_rejected_ledger"] is True
    assert _R["rejected_families_count"] == 21
    assert _R["next_required_action"] == (
        "HUMAN_DECISION_C17_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT")
    nra = d17.get_candidate_17_detector_dry_run_next_action()
    for banned in ("PAPER", "LIVE", "BROKER", "ORDER", "REPLAY", "PNL", "FETCH"):
        assert banned not in nra.upper(), banned
    bad = {**_R, "rejected_families_count": 20}
    assert d17.validate_c17_detector_dry_run(bad)["valid"] is False


# ---- downstream gates locked + flags + scope locks -------------------------

def test_downstream_gates_locked():
    for gate in ("labels_gate_locked", "replay_gate_locked",
                 "paper_trading_gate_locked", "live_gate_locked"):
        assert _R[gate] is True, gate
        bad = {**_R, gate: False}
        assert d17.validate_c17_detector_dry_run(bad)["valid"] is False, gate


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in d17._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert d17.validate_c17_detector_dry_run(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_data_fetch", "no_real_candles", "no_labels", "no_replay",
                 "no_pnl", "no_cost_application", "no_optimization", "no_commit",
                 "no_push", "no_broker", "no_order_logic", "no_shorting",
                 "no_leverage_above_cap", "no_paper_trading", "no_live_trading"):
        assert _R["scope_locks"][must] is True, must


def test_label_no_profitability_claim():
    label = d17.get_candidate_17_detector_dry_run_label()
    assert "RESEARCH ONLY" in label
    assert "SYNTHETIC" in label
    assert "NOT a profitability claim" in label or (
        "NOT A PROFITABILITY" in label.upper())
    for banned in ("PROFITABLE", "EDGE CONFIRMED", "READY FOR LIVE"):
        assert banned not in label.upper(), banned


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(d17.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch(", "open("):
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
