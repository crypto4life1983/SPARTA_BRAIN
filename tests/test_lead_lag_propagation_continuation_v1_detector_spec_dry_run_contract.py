"""Tests for the Candidate #13 detector-spec + synthetic dry-run contract
(lead_lag_propagation_continuation_v1).

Verifies the pure detector primitives + synthetic aligned fixtures + the
chain-gated dry-run record: confirmed leader move (r_L>0, z_L>=1.5) + follower lag
(r_F<0.5*r_L); ATR(14) stop = follower_close-1.0*ATR with an invalid-stop guard;
81 bps gross floor; 1R/1.5R/2R; <=2-bar hold with stop-first straddle and horizon
exit; per-follower reduce-or-keep non-overlap; leader != follower (raises); no
date/weekday in the bar shape; the early generalization + anti-drift battery stays
LOCKED for labels/replay; all execution gates locked; ~42 capability flags False;
anti-tamper; AST/purity green.

The shared chain is memoized once at import."""
from __future__ import annotations

import ast
import copy
import inspect
import subprocess
import sys

import sparta_commander.lead_lag_propagation_continuation_v1_detector_spec_dry_run_contract as c13d  # noqa: E501


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
    _R = c13d.build_candidate_13_detector_spec_dry_run(".", _tracked_paths())
finally:
    for _mod, _attr, _orig in _memo_restore:
        setattr(_mod, _attr, _orig)


# ---- detector primitives (direct) ------------------------------------------

def test_leader_zscore_and_lag_detection():
    d = c13d.fixture_valid_propagation_accepted()
    t = c13d._T
    z = c13d.leader_zscore(d["BTCUSD"], t)
    assert z is not None and z >= 1.5
    r_l = c13d.daily_return(d["BTCUSD"], t)
    r_f = c13d.daily_return(d["ETHUSD"], t)
    assert r_l > 0
    assert r_f < 0.5 * r_l            # ETH lags


def test_compute_stop_guard_rejects_zero_atr():
    assert c13d.compute_stop(100.0, 0.0)["valid"] is False
    good = c13d.compute_stop(100.0, 2.0)
    assert good["valid"] is True and good["stop_distance"] == 2.0


def test_scan_requires_distinct_followers_and_1d_long():
    try:
        c13d.scan_c13_setups(c13d.fixture_valid_propagation_accepted(),
                             followers=("BTCUSD", "ETHUSD"))
        assert False, "expected ValueError leader==follower"
    except ValueError:
        pass
    try:
        c13d.scan_c13_setups(c13d.fixture_valid_propagation_accepted(),
                             timeframe="1h")
        assert False, "expected ValueError timeframe"
    except ValueError:
        pass


# ---- chain gate + verdict --------------------------------------------------

def test_dry_run_ready_and_validates():
    assert _R["verdict"] == c13d.VERDICT_C13DD_READY
    assert _R["blockers"] == []
    assert _R["spec_verdict"] == c13d.VERDICT_C13S_READY
    assert c13d.validate_candidate_13_detector_spec_dry_run(_R)["valid"] is True


def test_all_dry_run_proofs_true():
    proofs = _R["dry_run_proofs"]
    for key in ("valid_propagation_setup_accepted",
                "no_setup_when_leader_move_not_confirmed",
                "no_setup_when_follower_already_matched",
                "invalid_stop_guard_rejects", "below_floor_rejected",
                "target_hit_outcome", "stop_hit_outcome",
                "same_bar_straddle_is_stop_first", "horizon_exit_when_neither",
                "per_follower_non_overlap_drops_later",
                "leader_must_not_equal_follower",
                "no_calendar_or_weekday_trigger",
                "no_labels_replay_baseline_data_fetch_trading", "deterministic"):
        assert proofs[key] is True, key


def test_accept_reject_outcomes():
    dry = _R["dry_run"]
    assert dry["valid_status"] == "accepted_for_replay_review"
    assert dry["not_confirmed_count"] == 0
    assert dry["no_lag_count"] == 0
    assert dry["below_floor_status"] == "rejected_geometry_floor"
    assert dry["invalid_stop_guard_valid"] is False
    assert dry["leader_eq_follower_raises"] is True


def test_exit_handling_outcomes():
    dry = _R["dry_run"]
    assert dry["target_outcome"] == "hit" and dry["target_gross_r"] == 1.0
    assert dry["stop_outcome"] == "miss" and dry["stop_gross_r"] == -1.0
    assert dry["straddle_outcome"] == "miss_same_bar_straddle"
    assert dry["straddle_gross_r"] == -1.0
    assert dry["horizon_outcome"] == "horizon"


def test_non_overlap_drops_later_same_follower():
    dry = _R["dry_run"]
    assert dry["non_overlap_accepted_setups"] >= 2
    assert dry["non_overlap_kept"] == 1
    assert dry["non_overlap_dropped"] >= 1


# ---- frozen geometry + leader!=follower ------------------------------------

def test_frozen_geometry_constants():
    assert _R["leader"] == "BTCUSD"
    assert _R["followers"] == ["ETHUSD", "SOLUSD"]
    assert _R["leader"] not in _R["followers"]
    assert _R["leader_z_entry_threshold"] == 1.5
    assert _R["lag_margin_fraction"] == 0.5
    assert _R["stop_atr_multiplier"] == 1.0
    assert _R["target_variants"] == ["1r", "1.5r", "2r"]
    assert _R["target_distance_floor_bps"] == 81.0
    assert _R["all_in_round_trip_bps"] == 37.0
    assert _R["max_hold_bars"] == 2
    for tamper, val in (("max_hold_bars", 9), ("leader_z_entry_threshold", 0.0),
                        ("all_in_round_trip_bps", 5.0)):
        bad = copy.deepcopy(_R)
        bad[tamper] = val
        assert c13d.validate_candidate_13_detector_spec_dry_run(
            bad)["valid"] is False, tamper


def test_no_calendar_single_asset_or_drift():
    assert _R["uses_no_weekday_or_calendar_trigger"] is True
    assert _R["is_single_asset_edge"] is False
    assert _R["relies_on_long_drift_or_bull_carry"] is False
    assert _R["leader_distinct_from_follower"] is True
    bar = c13d.fixture_valid_propagation_accepted()["ETHUSD"][0]
    assert set(bar.keys()) == {"open", "high", "low", "close"}


def test_early_battery_locked_for_labels_replay():
    locked = _R["early_generalization_battery_locked_for_labels_replay"]
    for chk in ("forward_oos_continuation_required_early",
                "beats_matched_buy_and_hold_baseline_required_early",
                "beats_matched_random_entry_baseline_required_early",
                "beats_buy_the_leader_baseline_required_early",
                "target_capture_dominates_horizon_exit_share_capped_required_early"):
        assert chk in locked, chk
    assert _R["max_horizon_exit_share"] == 0.50


# ---- locks + capability flags ----------------------------------------------

def test_all_gates_locked():
    for gate in ("labels_gate_locked", "replay_gate_locked",
                 "baseline_gate_locked", "data_fetch_gate_locked",
                 "robustness_gate_locked", "paper_trading_gate_locked",
                 "live_gate_locked", "human_review_required"):
        assert _R[gate] is True, gate
    for key, val in _R["scope_locks"].items():
        assert val is True, key


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in c13d._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = copy.deepcopy(_R)
        bad[flag] = True
        assert c13d.validate_candidate_13_detector_spec_dry_run(
            bad)["valid"] is False, flag


def test_next_action_and_label():
    nra = c13d.get_candidate_13_detector_dry_run_next_action()
    assert nra == "HUMAN_DECISION_C13_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT"
    label = c13d.get_candidate_13_detector_dry_run_label()
    assert "SYNTHETIC FIXTURES ONLY" in label and "RESEARCH ONLY" in label


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(c13d.__file__, encoding="utf-8").read()
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
