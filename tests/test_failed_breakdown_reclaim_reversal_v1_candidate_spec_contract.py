"""Tests for the Candidate #12 candidate-spec contract
(failed_breakdown_reclaim_reversal_v1).

Verifies: chain-gate on the READY C12 family proposal; verdict READY; the frozen
spec rules (BTC/ETH/SOL daily spot, no fetch; close-confirmed failed-breakdown
reclaim of a deterministic K=20 low; ATR(14)-validated stop below the reclaim
low; 81 bps gross floor over the 37 bps cost model; 1.5R/2R/3R; <=3-bar hold;
conservative stop-first straddle; per-asset reduce-or-keep non-overlap); BOTH
baseline gates (buy-and-hold + random-entry); the full early battery incl. the
horizon-exit-share cap; the one-edit allowance; no calendar/weekday trigger; no
long-drift/bull-carry reliance; all execution gates locked; ~44 capability flags
False; anti-tamper; AST/purity green.

The shared chain is memoized once at import."""
from __future__ import annotations

import ast
import copy
import inspect
import subprocess
import sys

import sparta_commander.failed_breakdown_reclaim_reversal_v1_candidate_spec_contract as c12s  # noqa: E501


def _tracked_paths():
    return subprocess.check_output(
        ["git", "ls-files"]).decode("utf-8").splitlines()


def _install_pure_gate_memoization():
    cache: dict = {}
    wrappers: dict = {}
    restore: list = []

    def _make(orig):
        def _wrapped(*args, **kwargs):
            if args or kwargs:
                return orig(*args, **kwargs)
            oid = id(orig)
            if oid not in cache:
                cache[oid] = orig()
            return copy.deepcopy(cache[oid])
        return _wrapped

    def _is_target(fn) -> bool:
        return inspect.isfunction(fn) and (
            fn.__name__.startswith("build_")
            or fn.__name__ == "_recompute_live_dry_run")

    for _mname, _mod in list(sys.modules.items()):
        if _mod is None or not _mname.startswith("sparta_commander"):
            continue
        for _orig in list(vars(_mod).values()):
            if _is_target(_orig) and id(_orig) not in wrappers:
                wrappers[id(_orig)] = _make(_orig)
    for _mname, _mod in list(sys.modules.items()):
        if _mod is None or not _mname.startswith("sparta_commander"):
            continue
        for _attr, _val in list(vars(_mod).items()):
            if inspect.isfunction(_val) and id(_val) in wrappers:
                restore.append((_mod, _attr, _val))
                setattr(_mod, _attr, wrappers[id(_val)])
    return restore


_memo_restore = _install_pure_gate_memoization()
try:
    _R = c12s.build_candidate_12_spec(".", _tracked_paths())
finally:
    for _mod, _attr, _orig in _memo_restore:
        setattr(_mod, _attr, _orig)


# ---- chain gate + verdict --------------------------------------------------

def test_spec_ready_and_validates():
    assert _R["verdict"] == c12s.VERDICT_C12S_READY
    assert _R["blockers"] == []
    assert _R["proposal_verdict"] == c12s.VERDICT_C12P_READY
    assert c12s.validate_candidate_12_spec(_R)["valid"] is True


def test_chain_gate_on_pushed_proposal():
    assert _R["head_at_c12_proposal"] == (
        "710429b7a71b7ba4d23567b64e16062f55bf3bc4")
    assert _R["candidate_number"] == 12
    assert _R["candidate_family"] == "failed_breakdown_reclaim_reversal"


# ---- 1-2 universe + no fetch -----------------------------------------------

def test_symbols_daily_spot_no_fetch():
    assert _R["symbol_universe"] == ["BTCUSD", "ETHUSD", "SOLUSD"]
    assert _R["min_assets_required"] == 3
    assert _R["timeframe"] == "1d" and _R["market_type"] == "spot"
    assert _R["no_data_fetch"] is True
    bad = copy.deepcopy(_R)
    bad["no_data_fetch"] = False
    assert c12s.validate_candidate_12_spec(bad)["valid"] is False


# ---- 3 reclaim definition + deterministic lookback + close-confirmed --------

def test_reclaim_definition_and_deterministic_lookback():
    assert _R["k_day_low_lookback"] == 20
    ec = _R["entry_concept"]
    assert ec["condition_a_pierce"] == "low[t] < L_K"
    assert ec["condition_b_reclaim_on_close"] == "close[t] > L_K"
    assert "close" in ec["confirmation"]
    assert ec["weekday_or_calendar_trigger"] is False
    assert ec["relies_on_long_drift_or_bull_carry"] is False
    bad = copy.deepcopy(_R)
    bad["k_day_low_lookback"] = 5
    assert c12s.validate_candidate_12_spec(bad)["valid"] is False


# ---- 4-7 geometry / cost / floor / hold ------------------------------------

def test_stop_targets_floor_cost_hold():
    rg = _R["risk_geometry"]
    assert rg["atr_length"] == 14
    assert rg["stop_atr_buffer_multiplier"] == 0.25
    assert _R["target_policy"]["variants"] == ["1.5r", "2r", "3r"]
    assert _R["target_distance_floor_bps"] == 81.0
    cm = _R["cost_model"]
    assert cm["all_in_round_trip_bps"] == 37.0
    assert cm["fee_round_trip_bps"] + cm["slippage_round_trip_bps"] == 37.0
    assert _R["max_hold_bars"] == 3
    assert "STOP FIRST" in _R["exit_policy"]["same_bar_straddle"]
    for tamper in ("target_distance_floor_bps", "max_hold_bars"):
        bad = copy.deepcopy(_R)
        bad[tamper] = 999
        assert c12s.validate_candidate_12_spec(bad)["valid"] is False, tamper


def test_cost_model_tamper_rejected():
    bad = copy.deepcopy(_R)
    bad["cost_model"]["all_in_round_trip_bps"] = 5.0
    assert c12s.validate_candidate_12_spec(bad)["valid"] is False


# ---- 8 non-overlap ---------------------------------------------------------

def test_non_overlap_per_asset():
    assert _R["non_overlap_policy"]["rule"] == (
        "per_asset_reduce_or_keep_only_never_add")


# ---- 9 BOTH baseline gates -------------------------------------------------

def test_baseline_comparisons_both_required():
    bc = _R["baseline_comparisons"]
    assert bc["matched_buy_and_hold"] and bc["matched_random_entry"]
    assert bc["both_required"] is True
    assert bc["failing_either_is_structural_rejection"] is True
    bad = copy.deepcopy(_R)
    bad["baseline_comparisons"]["both_required"] = False
    assert c12s.validate_candidate_12_spec(bad)["valid"] is False


# ---- 10 early battery + horizon cap + sample size --------------------------

def test_early_battery_and_horizon_cap():
    gates = _R["early_structural_rejection_gates"]
    for required in (
            "forward_oos_continuation_required_early",
            "cross_regime_bull_bear_chop_symmetry_required_early",
            "cross_asset_multiple_assets_required_early",
            "beats_matched_buy_and_hold_baseline_required_early",
            "beats_matched_random_entry_baseline_required_early",
            "target_capture_dominates_horizon_exit_share_capped_required_early",
            "no_weekday_or_calendar_dependence_required_early",
            "sample_size_minimums_required_early"):
        assert required in gates, required
    assert _R["max_horizon_exit_share"] == 0.50
    aog = _R["anti_overfit_generalization_rules"]
    assert aog["must_beat_buy_and_hold_and_random_entry"] is True
    assert aog["target_capture_must_dominate_horizon_capped"] is True
    assert aog["regime_symmetry_required_not_long_drift"] is True
    bad = copy.deepcopy(_R)
    bad["max_horizon_exit_share"] = 0.95
    assert c12s.validate_candidate_12_spec(bad)["valid"] is False


def test_sample_size_minimums():
    ss = _R["sample_size_requirements"]
    assert ss["min_accepted_total"] == 100
    assert ss["min_accepted_per_asset"] == 20
    assert ss["min_accepted_per_regime"] == 20
    assert ss["below_minimum_is_structural_rejection"] is True


# ---- one-edit allowance ----------------------------------------------------

def test_one_edit_allowance():
    oe = _R["one_edit_allowance"]
    assert oe["exactly_one_documented_parameter_edit_permitted"] is True
    assert oe["second_edit_is_structural_rejection"] is True
    assert oe["never_to_rescue_after_seeing_forward_oos"] is True
    bad = copy.deepcopy(_R)
    bad["one_edit_allowance"]["second_edit_is_structural_rejection"] = False
    assert c12s.validate_candidate_12_spec(bad)["valid"] is False


# ---- locks + capability flags ----------------------------------------------

def test_all_gates_locked_and_no_drift_reliance():
    assert _R["is_spec_only"] is True
    assert _R["relies_on_long_drift_or_bull_carry"] is False
    for gate in ("detector_gate_locked", "labels_gate_locked",
                 "replay_gate_locked", "data_fetch_gate_locked",
                 "paper_trading_gate_locked", "live_gate_locked",
                 "human_review_required"):
        assert _R[gate] is True, gate
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_calendar_trigger", "no_weekday_trigger",
                 "no_long_drift_or_bull_carry_reliance", "no_data_fetch",
                 "no_parameter_fitting_beyond_one_edit"):
        assert _R["scope_locks"][must] is True, must


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in c12s._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = copy.deepcopy(_R)
        bad[flag] = True
        assert c12s.validate_candidate_12_spec(bad)["valid"] is False, flag


def test_next_action_and_label():
    nra = c12s.get_candidate_12_spec_next_action()
    assert nra == "HUMAN_DECISION_C12_ADVANCE_TO_DETECTOR_SPEC_OR_REJECT"
    label = c12s.get_candidate_12_spec_label()
    assert "SPEC ONLY" in label and "RESEARCH ONLY" in label
    for banned in ("APPROVED FOR PAPER", "APPROVED FOR LIVE", "PROFITABLE",
                   "EDGE CONFIRMED", "READY FOR LIVE"):
        assert banned not in label.upper(), banned


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(c12s.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch(", "open("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
              "subprocess", "websockets", "aiohttp", "schedule", "threading",
              "asyncio", "telegram", "csv", "hashlib", "os", "io", "shutil",
              "ssl", "ftplib", "pathlib", "datetime"}
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
