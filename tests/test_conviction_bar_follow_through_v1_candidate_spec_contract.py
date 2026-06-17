"""Tests for the Candidate #14 candidate-spec contract
(conviction_bar_follow_through_v1).

Verifies: chain-gate on the READY C14 family proposal; verdict READY; the frozen
spec rules (BTC/ETH/SOL daily spot, no fetch; conviction bar = true_range >=
1.5*ATR(14) AND close >= low+0.75*range, no compression precondition; ATR(14)
stop; 81 bps floor over 37 bps cost; 1R/1.5R/2R; <=2-bar hold; conservative
stop-first straddle; per-asset resolved-exit non-overlap); BOTH baseline gates;
the full early battery WITH the structural labels sample-size gate FIRST + the
horizon cap; the one-edit allowance; no calendar/weekday; no long-drift/bull-carry
reliance; no threshold fitting; all execution gates locked; ~44 capability flags
False; anti-tamper; AST/purity green.

The shared chain is memoized once at import."""
from __future__ import annotations

import ast
import copy
import inspect
import subprocess
import sys

import sparta_commander.conviction_bar_follow_through_v1_candidate_spec_contract as c14s  # noqa: E501


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
    _R = c14s.build_candidate_14_spec(".", _tracked_paths())
finally:
    for _mod, _attr, _orig in _memo_restore:
        setattr(_mod, _attr, _orig)


# ---- chain gate + verdict --------------------------------------------------

def test_spec_ready_and_validates():
    assert _R["verdict"] == c14s.VERDICT_C14S_READY
    assert _R["blockers"] == []
    assert _R["proposal_verdict"] == c14s.VERDICT_C14P_READY
    assert c14s.validate_candidate_14_spec(_R)["valid"] is True


def test_chain_gate_on_pushed_proposal():
    assert _R["head_at_c14_proposal"] == (
        "127d959a0aea695ba42993a1fb046a4c2c96823a")
    assert _R["candidate_number"] == 14
    assert _R["candidate_family"] == "conviction_bar_follow_through"


# ---- 1-2 universe + no fetch -----------------------------------------------

def test_symbols_daily_spot_no_fetch():
    assert _R["symbol_universe"] == ["BTCUSD", "ETHUSD", "SOLUSD"]
    assert _R["min_assets_required"] == 3
    assert _R["timeframe"] == "1d" and _R["market_type"] == "spot"
    assert _R["no_data_fetch"] is True
    bad = copy.deepcopy(_R)
    bad["no_data_fetch"] = False
    assert c14s.validate_candidate_14_spec(bad)["valid"] is False


# ---- 3 conviction-bar rule -------------------------------------------------

def test_conviction_bar_rule_frozen():
    assert _R["range_atr_multiple"] == 1.5
    assert _R["close_location_min"] == 0.75
    ec = _R["entry_concept"]
    assert ec["condition_a_range_outlier"] == "true_range >= 1.5 * ATR(14)"
    assert ec["condition_b_strong_close"] == "close >= low + 0.75 * (high - low)"
    assert ec["no_compression_precondition"] is True
    assert ec["weekday_or_calendar_trigger"] is False
    assert ec["relies_on_long_drift_or_bull_carry"] is False
    for tamper, val in (("range_atr_multiple", 5.0), ("close_location_min", 0.1)):
        bad = copy.deepcopy(_R)
        bad[tamper] = val
        assert c14s.validate_candidate_14_spec(bad)["valid"] is False, tamper


# ---- 4-7 geometry / cost / floor / hold ------------------------------------

def test_stop_targets_floor_cost_hold():
    rg = _R["risk_geometry"]
    assert rg["atr_length"] == 14 and rg["stop_atr_multiplier"] == 1.0
    assert _R["target_policy"]["variants"] == ["1r", "1.5r", "2r"]
    assert _R["target_distance_floor_bps"] == 81.0
    cm = _R["cost_model"]
    assert cm["all_in_round_trip_bps"] == 37.0
    assert cm["fee_round_trip_bps"] + cm["slippage_round_trip_bps"] == 37.0
    assert _R["max_hold_bars"] == 2
    assert "STOP FIRST" in _R["exit_policy"]["same_bar_straddle"]
    for tamper, val in (("target_distance_floor_bps", 1.0), ("max_hold_bars", 9)):
        bad = copy.deepcopy(_R)
        bad[tamper] = val
        assert c14s.validate_candidate_14_spec(bad)["valid"] is False, tamper


def test_cost_model_tamper_rejected():
    bad = copy.deepcopy(_R)
    bad["cost_model"]["all_in_round_trip_bps"] = 5.0
    assert c14s.validate_candidate_14_spec(bad)["valid"] is False


# ---- 8 non-overlap ---------------------------------------------------------

def test_non_overlap_per_asset():
    assert _R["non_overlap_policy"]["rule"] == (
        "per_asset_resolved_exit_reduce_or_keep_only_never_add")


# ---- 9 BOTH baseline gates -------------------------------------------------

def test_baseline_comparisons_both_required():
    bc = _R["baseline_comparisons"]
    assert bc["matched_buy_and_hold"] and bc["matched_random_entry"]
    assert bc["both_required"] is True
    assert bc["failing_either_is_structural_rejection"] is True
    bad = copy.deepcopy(_R)
    bad["baseline_comparisons"]["both_required"] = False
    assert c14s.validate_candidate_14_spec(bad)["valid"] is False


# ---- 10 early battery WITH the structural sample-size gate FIRST ------------

def test_structural_labels_sample_size_gate_first():
    gates = _R["early_structural_rejection_gates"]
    assert gates[0] == "structural_labels_sample_size_gate_required_first"
    for required in (
            "structural_labels_sample_size_gate_required_first",
            "forward_oos_continuation_required_early",
            "cross_regime_bull_bear_chop_symmetry_required_early",
            "cross_asset_multiple_assets_required_early",
            "beats_matched_buy_and_hold_baseline_required_early",
            "beats_matched_random_entry_baseline_required_early",
            "target_capture_dominates_horizon_exit_share_capped_required_early",
            "no_weekday_or_calendar_dependence_required_early"):
        assert required in gates, required
    ss = _R["sample_size_requirements"]
    assert ss["min_accepted_total"] == 100
    assert ss["min_accepted_per_asset"] == 20
    assert ss["min_accepted_per_regime"] == 20
    assert ss["forward_oos_window_must_be_populated"] is True
    assert ss["below_minimum_is_structural_rejection"] is True
    aog = _R["anti_overfit_generalization_rules"]
    assert aog["structural_labels_sample_size_gate_enforced_before_replay"] is True
    assert aog["threshold_not_fit_to_manufacture_samples"] is True
    assert _R["max_horizon_exit_share"] == 0.50
    # tamper: drop the sample-size gate -> invalid
    bad = copy.deepcopy(_R)
    bad["early_structural_rejection_gates"] = [
        g for g in gates
        if g != "structural_labels_sample_size_gate_required_first"]
    assert c14s.validate_candidate_14_spec(bad)["valid"] is False
    bad2 = copy.deepcopy(_R)
    bad2["sample_size_requirements"]["forward_oos_window_must_be_populated"] = False
    assert c14s.validate_candidate_14_spec(bad2)["valid"] is False


def test_must_beat_baselines_and_target_capture():
    aog = _R["anti_overfit_generalization_rules"]
    assert aog["must_beat_buy_and_hold_and_random_entry"] is True
    assert aog["target_capture_must_dominate_horizon_capped"] is True
    assert aog["regime_symmetry_required_not_long_drift"] is True


# ---- one-edit allowance ----------------------------------------------------

def test_one_edit_allowance():
    oe = _R["one_edit_allowance"]
    assert oe["exactly_one_documented_parameter_edit_permitted"] is True
    assert oe["second_edit_is_structural_rejection"] is True
    assert oe["never_to_rescue_after_seeing_forward_oos"] is True
    assert oe["never_to_manufacture_samples"] is True
    bad = copy.deepcopy(_R)
    bad["one_edit_allowance"]["never_to_manufacture_samples"] = False
    assert c14s.validate_candidate_14_spec(bad)["valid"] is False


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
                 "no_threshold_fit_to_manufacture_samples",
                 "no_parameter_fitting_beyond_one_edit"):
        assert _R["scope_locks"][must] is True, must


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in c14s._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = copy.deepcopy(_R)
        bad[flag] = True
        assert c14s.validate_candidate_14_spec(bad)["valid"] is False, flag


def test_next_action_and_label():
    nra = c14s.get_candidate_14_spec_next_action()
    assert nra == "HUMAN_DECISION_C14_ADVANCE_TO_DETECTOR_SPEC_OR_REJECT"
    label = c14s.get_candidate_14_spec_label()
    assert "SPEC ONLY" in label and "RESEARCH ONLY" in label
    for banned in ("APPROVED FOR PAPER", "APPROVED FOR LIVE", "PROFITABLE",
                   "EDGE CONFIRMED", "READY FOR LIVE"):
        assert banned not in label.upper(), banned


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(c14s.__file__, encoding="utf-8").read()
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
