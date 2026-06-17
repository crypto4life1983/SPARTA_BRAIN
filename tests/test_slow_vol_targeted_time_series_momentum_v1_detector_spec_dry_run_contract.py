"""Tests for the Candidate #15 detector spec + SYNTHETIC dry-run contract
(slow_vol_targeted_time_series_momentum_v1).

Verifies: research-only, synthetic-only, executes nothing on real data; chain-
gated on the frozen C15 spec; the detector behaves per the C15 logic on
deterministic synthetic fixtures (long-in-uptrend, short-in-downtrend, flat-in-
chop, vol-targeted sizing, non-fixed-horizon holding, W1 regime context); the
37 bps cost model is RESERVED for replay and NOT applied; downstream gates locked;
capability flags + scope locks; validator anti-tamper; module purity."""
from __future__ import annotations

import ast

import sparta_commander.slow_vol_targeted_time_series_momentum_v1_detector_spec_dry_run_contract as d15  # noqa: E501


_R = d15.build_c15_detector_dry_run(".", [])


# ---- core: research-only, synthetic, frozen, validates ---------------------

def test_dry_run_frozen_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_synthetic_dry_run_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"] == "C15_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW"
    assert d15.validate_c15_detector_dry_run(_R)["valid"] is True


def test_chain_gated_on_frozen_c15_spec():
    assert _R["spec_valid"] is True
    assert _R["spec_verdict"] == "C15_SPEC_FROZEN_FOR_HUMAN_REVIEW"


# ---- synthetic only / no real data -----------------------------------------

def test_synthetic_only_no_real_data():
    assert _R["uses_synthetic_fixtures_only"] is True
    assert _R["uses_real_data"] is False
    assert _R["synthetic_bars_per_fixture"] == 160
    bad = {**_R, "uses_real_data": True}
    assert d15.validate_c15_detector_dry_run(bad)["valid"] is False


# ---- cost model reserved for replay, not applied ---------------------------

def test_cost_model_reserved_not_applied():
    assert _R["cost_model_reserved_for_replay"] is True
    assert _R["cost_model_applied_here"] is False
    assert _R["all_in_round_trip_bps_reserved"] == 37.0
    assert _R["applies_cost_model"] is False
    bad = {**_R, "cost_model_applied_here": True}
    assert d15.validate_c15_detector_dry_run(bad)["valid"] is False


# ---- preserved C15 logic ----------------------------------------------------

def test_preserved_c15_logic_identity():
    assert _R["symbols"] == ["BTCUSD", "ETHUSD", "SOLUSD"]
    assert _R["timeframe"] == "D1"
    assert _R["context_timeframe"] == "W1"
    assert _R["uses_w1_regime_context"] is True
    assert _R["is_time_series_momentum"] is True
    assert _R["is_volatility_targeted"] is True
    assert _R["is_regime_aware"] is True
    assert _R["is_fixed_horizon"] is False
    bad = {**_R, "is_fixed_horizon": True}
    assert d15.validate_c15_detector_dry_run(bad)["valid"] is False


# ---- the synthetic dry-run behaviour ---------------------------------------

def test_all_dry_run_checks_pass():
    assert _R["dry_run_all_checks_pass"] is True
    for k in ("uptrend_is_long", "uptrend_non_fixed_horizon_hold",
              "downtrend_is_short", "chop_mostly_flat",
              "vol_targeting_scales_down", "low_vol_scale_capped",
              "regime_context_bull_in_uptrend", "regime_context_bear_in_downtrend"):
        assert _R["dry_run_checks"][k] is True, k


def test_uptrend_long_and_non_fixed_horizon():
    up = _R["dry_run_summaries"]["uptrend_low_vol"]
    assert up["counts"]["long"] > 0
    assert up["counts"]["short"] == 0
    # a single long run spanning many bars -> not a fixed-horizon exit
    assert up["max_consecutive_long"] >= 20


def test_downtrend_short_symmetric_regime_aware():
    dn = _R["dry_run_summaries"]["downtrend"]
    assert dn["counts"]["short"] > 0
    assert dn["counts"]["long"] == 0
    assert dn["regime_counts"]["bear"] > dn["regime_counts"]["bull"]


def test_chop_mostly_flat():
    ch = _R["dry_run_summaries"]["chop"]
    assert ch["flat_share"] >= 0.70


def test_vol_targeting_scales_down_with_vol():
    lo = _R["dry_run_summaries"]["uptrend_low_vol"]["avg_active_position_scale"]
    hi = _R["dry_run_summaries"]["uptrend_high_vol"]["avg_active_position_scale"]
    assert hi < lo
    assert abs(lo - d15.SPEC_PARAMS["max_position_scale"]) < 1e-6  # capped


# ---- detector primitive sanity (pure, synthetic) ---------------------------

def test_scan_states_warmup_then_signal():
    candles = d15.build_synthetic_fixtures()["uptrend_low_vol"]
    states = d15.scan_c15_states(candles)
    assert states[0]["state"] == "warmup"
    assert any(s["state"] == "long" for s in states)
    # nothing in the per-bar output is a cost/pnl field
    for s in states:
        assert "pnl" not in s and "net_r" not in s


# ---- downstream gates locked + flags + scope locks -------------------------

def test_downstream_gates_locked():
    for gate in ("labels_gate_locked", "replay_gate_locked",
                 "paper_trading_gate_locked", "live_gate_locked"):
        assert _R[gate] is True, gate
        bad = {**_R, gate: False}
        assert d15.validate_c15_detector_dry_run(bad)["valid"] is False, gate


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in d15._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert d15.validate_c15_detector_dry_run(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_data_fetch", "no_real_candles", "no_labels", "no_replay",
                 "no_backtest", "no_pnl", "no_cost_application", "no_commit",
                 "no_push", "no_paper_trading", "no_live_trading", "no_broker"):
        assert _R["scope_locks"][must] is True, must


def test_label_and_next_action_no_readiness():
    label = d15.get_candidate_15_detector_dry_run_label()
    assert "RESEARCH ONLY" in label
    assert "SYNTHETIC" in label.upper()
    assert "NOT a profitability claim" in label or "NOT A PROFITABILITY" in label.upper()
    for banned in ("PROFITABLE", "EDGE CONFIRMED", "READY FOR LIVE"):
        assert banned not in label.upper(), banned
    nra = d15.get_candidate_15_detector_dry_run_next_action()
    assert nra == _R["next_required_action"]
    assert nra == "HUMAN_DECISION_C15_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT"
    for banned in ("PAPER", "LIVE", "EXECUTE", "BROKER", "ORDER", "FETCH",
                   "REPLAY"):
        assert banned not in nra.upper(), banned


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(d15.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch(", "open("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
              "subprocess", "websockets", "aiohttp", "schedule", "threading",
              "asyncio", "telegram", "csv", "hashlib", "os", "io", "shutil",
              "ssl", "ftplib", "pathlib", "datetime", "random"}
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
