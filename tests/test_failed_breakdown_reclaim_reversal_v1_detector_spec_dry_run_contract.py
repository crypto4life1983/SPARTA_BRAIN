"""Tests for the Candidate #12 detector-spec + synthetic dry-run contract
(failed_breakdown_reclaim_reversal_v1).

Verifies the pure detector primitives + synthetic fixtures + the chain-gated
dry-run record: close-confirmed failed-breakdown reclaim of a K=20 low; ATR(14)
stop = reclaim_low - 0.25*ATR with an invalid-stop guard; 81 bps gross floor;
1.5R/2R/3R; <=3-bar hold with stop-first straddle and horizon exit; per-asset
reduce-or-keep non-overlap; no date/weekday in the bar shape; the early
generalization + anti-drift battery stays LOCKED for labels/replay; all execution
gates locked; ~42 capability flags False; anti-tamper; AST/purity green.

The shared chain is memoized once at import."""
from __future__ import annotations

import ast
import copy
import inspect
import subprocess
import sys

import sparta_commander.failed_breakdown_reclaim_reversal_v1_detector_spec_dry_run_contract as c12d  # noqa: E501


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
    _R = c12d.build_candidate_12_detector_spec_dry_run(".", _tracked_paths())
finally:
    for _mod, _attr, _orig in _memo_restore:
        setattr(_mod, _attr, _orig)


# ---- detector primitives (direct, no chain) --------------------------------

def test_prior_k_low_and_reclaim_detection():
    bars = c12d.fixture_valid_reclaim_accepted()
    t = c12d._T
    lk = c12d.prior_k_low(bars, t)
    assert abs(lk - 99.0) < 1e-6           # flat prior-20-low at 100*(1-0.01)
    assert bars[t]["low"] < lk             # pierce
    assert bars[t]["close"] > lk           # close-confirmed reclaim
    assert c12d.is_failed_breakdown_reclaim(bars, t) is True


def test_compute_stop_guard_rejects_non_positive_distance():
    assert c12d.compute_stop(100.0, 100.0, 0.0)["valid"] is False   # zero
    assert c12d.compute_stop(100.0, 101.0, 0.0)["valid"] is False   # above entry
    good = c12d.compute_stop(100.0, 98.0, 1.0)
    assert good["valid"] is True and good["stop_distance"] > 0


def test_scan_locked_to_1d_long_only():
    try:
        c12d.scan_c12_setups(c12d.fixture_valid_reclaim_accepted(),
                             timeframe="1h")
        assert False, "expected ValueError"
    except ValueError:
        pass


# ---- chain gate + verdict --------------------------------------------------

def test_dry_run_ready_and_validates():
    assert _R["verdict"] == c12d.VERDICT_C12DD_READY
    assert _R["blockers"] == []
    assert _R["spec_verdict"] == c12d.VERDICT_C12S_READY
    assert c12d.validate_candidate_12_detector_spec_dry_run(_R)["valid"] is True


def test_all_dry_run_proofs_true():
    proofs = _R["dry_run_proofs"]
    for key in ("valid_reclaim_setup_accepted", "no_setup_when_no_pierce",
                "no_setup_when_close_does_not_reclaim",
                "invalid_stop_guard_rejects", "below_floor_rejected",
                "target_hit_outcome", "stop_hit_outcome",
                "same_bar_straddle_is_stop_first", "horizon_exit_when_neither",
                "per_asset_non_overlap_drops_later",
                "no_calendar_or_weekday_trigger",
                "no_labels_replay_data_fetch_trading", "deterministic"):
        assert proofs[key] is True, key


# ---- the dry-run outcomes themselves ---------------------------------------

def test_accept_reject_outcomes():
    dry = _R["dry_run"]
    assert dry["valid_reclaim_status"] == "accepted_for_replay_review"
    assert dry["no_pierce_setup_count"] == 0
    assert dry["no_reclaim_setup_count"] == 0
    assert dry["below_floor_status"] == "rejected_geometry_floor"
    assert dry["invalid_stop_guard_valid"] is False


def test_exit_handling_outcomes():
    dry = _R["dry_run"]
    assert dry["target_outcome"] == "hit" and dry["target_gross_r"] == 1.5
    assert dry["stop_outcome"] == "miss" and dry["stop_gross_r"] == -1.0
    assert dry["straddle_outcome"] == "miss_same_bar_straddle"
    assert dry["straddle_gross_r"] == -1.0
    assert dry["horizon_outcome"] == "horizon"


def test_non_overlap_drops_later_same_asset_setup():
    dry = _R["dry_run"]
    assert dry["non_overlap_accepted_setups"] >= 2
    assert dry["non_overlap_kept"] == 1
    assert dry["non_overlap_dropped"] >= 1


# ---- frozen detector geometry ----------------------------------------------

def test_frozen_geometry_constants():
    assert _R["k_day_low_lookback"] == 20
    assert _R["atr_length"] == 14
    assert _R["stop_atr_buffer_multiplier"] == 0.25
    assert _R["target_variants"] == ["1.5r", "2r", "3r"]
    assert _R["target_distance_floor_bps"] == 81.0
    assert _R["all_in_round_trip_bps"] == 37.0
    assert _R["max_hold_bars"] == 3
    assert _R["same_bar_straddle_policy"] == "stop_first_conservative_miss"
    assert _R["non_overlap_policy"] == "per_asset_reduce_or_keep_only_never_add"
    for tamper, val in (("k_day_low_lookback", 5), ("max_hold_bars", 9),
                        ("target_distance_floor_bps", 1.0),
                        ("all_in_round_trip_bps", 5.0)):
        bad = copy.deepcopy(_R)
        bad[tamper] = val
        assert c12d.validate_candidate_12_detector_spec_dry_run(
            bad)["valid"] is False, tamper


def test_no_calendar_single_asset_or_drift():
    assert _R["uses_no_weekday_or_calendar_trigger"] is True
    assert _R["is_single_asset_edge"] is False
    assert _R["relies_on_long_drift_or_bull_carry"] is False
    # bars carry only OHLC (no date / no weekday)
    bar = c12d.fixture_valid_reclaim_accepted()[0]
    assert set(bar.keys()) == {"open", "high", "low", "close"}


def test_early_battery_locked_for_labels_replay():
    locked = _R["early_generalization_battery_locked_for_labels_replay"]
    for chk in ("forward_oos_continuation_required_early",
                "beats_matched_buy_and_hold_baseline_required_early",
                "beats_matched_random_entry_baseline_required_early",
                "target_capture_dominates_horizon_exit_share_capped_required_early"):
        assert chk in locked, chk
    assert _R["max_horizon_exit_share"] == 0.50


# ---- locks + capability flags ----------------------------------------------

def test_all_gates_locked():
    for gate in ("labels_gate_locked", "replay_gate_locked",
                 "data_fetch_gate_locked", "robustness_gate_locked",
                 "paper_trading_gate_locked", "live_gate_locked",
                 "human_review_required"):
        assert _R[gate] is True, gate
    for key, val in _R["scope_locks"].items():
        assert val is True, key


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in c12d._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = copy.deepcopy(_R)
        bad[flag] = True
        assert c12d.validate_candidate_12_detector_spec_dry_run(
            bad)["valid"] is False, flag


def test_next_action_and_label():
    nra = c12d.get_candidate_12_detector_dry_run_next_action()
    assert nra == "HUMAN_DECISION_C12_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT"
    label = c12d.get_candidate_12_detector_dry_run_label()
    assert "SYNTHETIC FIXTURES ONLY" in label and "RESEARCH ONLY" in label


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(c12d.__file__, encoding="utf-8").read()
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
