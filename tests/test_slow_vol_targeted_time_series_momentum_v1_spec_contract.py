"""Tests for the Candidate #15 family-spec contract
(slow_vol_targeted_time_series_momentum_v1).

Verifies: research-only, pure-spec-only, executes nothing; chain-gated on the
tournament proposal with winner == trend_following; the candidate is materially
different from C1-C14 (slow / vol-targeted / time-series momentum / regime-aware /
NOT fixed-horizon); symbols+timeframe, entry/exit/risk logic, the 37 bps cost
model, buy-and-hold + random-entry baselines, forward-OOS requirement, and BOTH
the 3-year durability and 3-6 month relevance windows are present; downstream gates
locked; capability flags + scope locks; validator anti-tamper; module purity."""
from __future__ import annotations

import ast

import sparta_commander.slow_vol_targeted_time_series_momentum_v1_spec_contract as c15  # noqa: E501


_R = c15.build_c15_spec(".", [])


# ---- core: research-only, pure, frozen, validates --------------------------

def test_spec_frozen_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_pure_spec_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"] == "C15_SPEC_FROZEN_FOR_HUMAN_REVIEW"
    assert c15.validate_c15_spec(_R)["valid"] is True


def test_candidate_identity():
    assert _R["candidate_id"] == "C15"
    assert _R["candidate_family"] == "slow_vol_targeted_time_series_momentum"
    assert _R["candidate_name"] == "slow_vol_targeted_time_series_momentum_v1"


# ---- chain gate on the tournament winner -----------------------------------

def test_chain_gated_on_trend_following_winner():
    assert _R["source_tournament_winner"] == "trend_following"
    assert _R["tournament_proposal_valid"] is True
    assert _R["tournament_recommended_score"] is not None


def test_gate_sequence_preserved():
    assert _R["gate_sequence"] == [
        "family_proposal", "candidate_spec", "detector_spec_dry_run",
        "real_candle_labels_review", "fee_honest_replay_review",
        "rejection_or_promote_decision"]


# ---- material difference from C1-C14 (the whole point) ---------------------

def test_materially_different_from_c1_c14():
    assert _R["is_fixed_horizon"] is False
    assert _R["is_volatility_targeted"] is True
    assert _R["is_time_series_momentum"] is True
    assert _R["is_regime_aware"] is True
    md = " || ".join(_R["material_difference_from_c1_c14"]).lower()
    assert "slow" in md
    assert "volatility-targeted" in md or "vol-targeted" in md or "atr-scaled" in md
    assert "long/short" in md or "symmetric" in md
    assert "regime" in md
    assert "not a fixed max-hold" in md or "not fixed" in md or "signal-driven" in md
    assert _R["candidate_not_in_rejected_ledger"] is True
    for bad_key in ("is_fixed_horizon",):  # flipping to fixed-horizon is invalid
        bad = {**_R, bad_key: True}
        assert c15.validate_c15_spec(bad)["valid"] is False


# ---- symbols / timeframe / logic -------------------------------------------

def test_symbols_timeframe_and_logic_present():
    assert _R["symbols"] == ["BTCUSD", "ETHUSD", "SOLUSD"]
    assert _R["timeframe"] == "D1"
    assert _R["entry_logic"] and _R["exit_logic"] and _R["risk_logic"]
    sp = _R["spec_params"]
    assert sp["fixed_horizon"] is None          # signal-driven, not fixed-horizon
    assert sp["allow_short"] is True and sp["allow_flat"] is True
    assert sp["one_edit_allowance_used"] is False


# ---- cost model (37 bps) ----------------------------------------------------

def test_cost_model_intact():
    assert _R["all_in_round_trip_bps"] == 37.0
    assert _R["fee_round_trip_bps"] + _R["slippage_round_trip_bps"] == 37.0
    bad = {**_R, "all_in_round_trip_bps": 5.0}
    assert c15.validate_c15_spec(bad)["valid"] is False


# ---- baselines + forward-OOS (the C14 trap) --------------------------------

def test_baselines_and_forward_oos_required():
    br = _R["baselines_required"]
    assert br["buy_and_hold"]["required"] is True
    assert br["random_entry"]["required"] is True
    dg = _R["decisive_replay_gates"]
    assert dg["must_beat_buy_and_hold"] is True
    assert dg["must_beat_random_entry"] is True
    assert dg["forward_oos_must_be_net_positive"] is True
    assert dg["regime_net_symmetry_required"] is True
    assert dg["horizon_exit_cap_applicable"] is False   # signal-driven exits
    assert _R["forward_oos"]["required"] is True
    assert _R["forward_oos"]["must_be_net_positive"] is True
    for bad_key in ("must_beat_buy_and_hold", "must_beat_random_entry",
                    "forward_oos_must_be_net_positive"):
        bad = {**_R, "decisive_replay_gates": {**dg, bad_key: False}}
        assert c15.validate_c15_spec(bad)["valid"] is False, bad_key


# ---- both windows (requirement 5) ------------------------------------------

def test_durability_and_recent_relevance_windows():
    w = _R["evaluation_windows"]
    assert w["durability_window_days"] == 1095            # 3 years
    assert w["recent_relevance_window_days_min"] == 90    # 3 months
    assert w["recent_relevance_window_days_max"] == 180   # 6 months
    assert w["forward_oos_required"] is True
    assert w["regime_specific_tagging_required"] is True
    bad = {**_R, "evaluation_windows": {**w, "durability_window_days": 30}}
    assert c15.validate_c15_spec(bad)["valid"] is False


# ---- downstream gates locked + capability flags + scope locks --------------

def test_downstream_gates_locked():
    for gate in ("detector_gate_locked", "labels_gate_locked",
                 "replay_gate_locked", "paper_trading_gate_locked",
                 "live_gate_locked"):
        assert _R[gate] is True, gate
        bad = {**_R, gate: False}
        assert c15.validate_c15_spec(bad)["valid"] is False, gate


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in c15._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert c15.validate_c15_spec(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_build", "no_data_fetch", "no_detector_run", "no_labels",
                 "no_replay", "no_backtest", "no_commit", "no_push",
                 "no_paper_trading", "no_live_trading", "no_broker",
                 "no_one_edit_invocation"):
        assert _R["scope_locks"][must] is True, must


def test_label_and_next_action_no_readiness():
    label = c15.get_candidate_15_spec_label()
    assert "RESEARCH ONLY" in label
    assert "NOT a profitability claim" in label or "NOT A PROFITABILITY" in label.upper()
    for banned in ("PROFITABLE", "EDGE CONFIRMED", "READY FOR LIVE",
                   "APPROVED FOR PAPER", "APPROVED FOR LIVE"):
        assert banned not in label.upper(), banned
    nra = c15.get_candidate_15_spec_next_action()
    assert nra == _R["next_required_action"]
    assert nra == "HUMAN_DECISION_C15_ADVANCE_TO_DETECTOR_SPEC_DRY_RUN_OR_REJECT"
    for banned in ("PAPER", "LIVE", "EXECUTE", "BROKER", "ORDER", "FETCH",
                   "REPLAY", "LABELS"):
        assert banned not in nra.upper(), banned


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(c15.__file__, encoding="utf-8").read()
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
