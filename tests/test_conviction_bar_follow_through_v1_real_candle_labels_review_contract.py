"""Tests for the Candidate #14 real-candle labels review contract
(conviction_bar_follow_through_v1).

Verifies: chain-gate on the READY C14 detector dry-run; verdict FROZEN; SHA pins
of the 3 sources + the two untracked label artifacts; the labels-stage facts (347
labels; per-asset/per-regime minimums met); the STRUCTURAL SAMPLE-SIZE GATE (the
C13 lesson) passes incl. a POPULATED forward-OOS 2026 window; single-asset-event-
not-drift; NO replay/PnL/baseline in this gate; no structural rejection pressure;
baselines + horizon cap + forward-OOS still required at replay; all downstream
gates locked; no profitability / paper-live readiness claim; the artifacts remain
untracked; AST/purity green.

The shared chain is memoized once at import."""
from __future__ import annotations

import ast
import copy
import inspect
import subprocess
import sys

import sparta_commander.conviction_bar_follow_through_v1_real_candle_labels_review_contract as c14l  # noqa: E501


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
    _R = c14l.build_c14_labels_review(".", _tracked_paths())
finally:
    for _mod, _attr, _orig in _memo_restore:
        setattr(_mod, _attr, _orig)


# ---- chain gate + verdict --------------------------------------------------

def test_review_frozen_and_validates():
    assert _R["verdict"] == c14l.VERDICT_C14L_FROZEN
    assert _R["blockers"] == []
    assert _R["detector_dry_run_verdict"] == c14l.VERDICT_C14DD_READY
    assert c14l.validate_c14_labels_review(_R)["valid"] is True


def test_sha_pins_frozen():
    assert _R["expected_labels_sha256"] == c14l.EXPECTED_LABELS_SHA256
    assert _R["expected_summary_sha256"] == c14l.EXPECTED_SUMMARY_SHA256
    for s in ("BTCUSD", "ETHUSD", "SOLUSD"):
        assert _R["expected_source_sha256"][s] == c14l.EXPECTED_SOURCE_SHA256[s]
    assert _R["head_at_detector_dry_run"] == (
        "989f2ead937d368061b879c599edd4faf5110bba")
    bad = copy.deepcopy(_R)
    bad["expected_labels_sha256"] = "0" * 64
    assert c14l.validate_c14_labels_review(bad)["valid"] is False


# ---- the STRUCTURAL sample-size gate (the C13 lesson) ----------------------

def test_structural_sample_size_gate_passes():
    assert _R["accepted_label_count"] == 347
    assert _R["accepted_pre_overlap_count"] == 402
    assert _R["dropped_labels_stage_non_overlap"] == 55
    assert _R["sample_size_passed"] is True
    for s in ("BTCUSD", "ETHUSD", "SOLUSD"):
        assert _R["per_asset"][s] >= 20
    for r in ("bull", "bear", "chop"):
        assert _R["per_regime"][r] >= 20
    bad = copy.deepcopy(_R)
    bad["per_asset"]["SOLUSD"] = 5
    assert c14l.validate_c14_labels_review(bad)["valid"] is False
    bad2 = copy.deepcopy(_R)
    bad2["accepted_label_count"] = 50
    assert c14l.validate_c14_labels_review(bad2)["valid"] is False


def test_forward_oos_window_populated():
    assert _R["forward_oos_populated"] is True
    assert _R["forward_oos_label_count"] == 23
    assert _R["structural_checks_battery"]["forward_oos_populated"] is True
    bad = copy.deepcopy(_R)
    bad["forward_oos_populated"] = False
    assert c14l.validate_c14_labels_review(bad)["valid"] is False
    bad2 = copy.deepcopy(_R)
    bad2["forward_oos_label_count"] = 0
    assert c14l.validate_c14_labels_review(bad2)["valid"] is False


def test_single_asset_event_not_drift():
    assert _R["single_asset_event_not_long_drift"] is True
    assert _R["relies_on_long_drift_or_bull_carry"] is False
    bad = copy.deepcopy(_R)
    bad["single_asset_event_not_long_drift"] = False
    assert c14l.validate_c14_labels_review(bad)["valid"] is False


def test_structural_battery_passes_and_no_rejection_pressure():
    b = _R["structural_checks_battery"]
    for key in ("sample_size_gate_passed", "cross_asset_coverage_ok",
                "cross_regime_coverage_ok", "no_weekday_dependence_ok",
                "passed"):
        assert b[key] is True, key
    assert _R["max_weekday_share"] <= 0.25
    assert len(_R["weekday_distribution"]) == 7
    assert _R["structural_rejection_pressure"] is False
    bad = copy.deepcopy(_R)
    bad["structural_rejection_pressure"] = True
    assert c14l.validate_c14_labels_review(bad)["valid"] is False


def test_forward_oos_reserved_and_still_required_at_replay():
    assert _R["forward_oos_start"] == "2026-01-01"
    assert "forward_oos_still_required_at_replay" in _R["claim_locks"]
    assert "baselines_and_horizon_cap_still_required_at_replay" in _R["claim_locks"]


# ---- no replay / PnL / baseline in this gate -------------------------------

def test_no_replay_pnl_baseline_in_this_gate():
    assert _R["no_replay_or_pnl_or_baseline_in_this_gate"] is True
    assert _R["replay_gate_locked"] is True
    assert _R["pnl_gate_locked"] is True
    assert _R["baseline_gate_locked"] is True
    assert _R["scope_locks"]["no_replay"] is True
    assert _R["scope_locks"]["no_baseline_comparison"] is True


# ---- locks + capability flags + claim locks --------------------------------

def test_all_downstream_gates_locked():
    assert _R["is_labels_review_only"] is True
    for gate in ("replay_gate_locked", "pnl_gate_locked", "baseline_gate_locked",
                 "robustness_gate_locked", "data_fetch_gate_locked",
                 "paper_trading_gate_locked", "live_gate_locked",
                 "human_review_required"):
        assert _R[gate] is True, gate
    for key, val in _R["scope_locks"].items():
        assert val is True, key


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in c14l._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = copy.deepcopy(_R)
        bad[flag] = True
        assert c14l.validate_c14_labels_review(bad)["valid"] is False, flag


def test_claim_locks_and_label_no_readiness():
    for required in ("no_profitability_claim", "no_replay_in_this_gate",
                     "no_baseline_comparison_in_this_gate",
                     "single_asset_event_not_long_drift",
                     "structural_sample_size_gate_passed_at_labels",
                     "forward_oos_still_required_at_replay"):
        assert required in _R["claim_locks"], required
    label = c14l.get_candidate_14_labels_review_label()
    assert "RESEARCH ONLY" in label
    assert "NOT A PROFITABILITY CLAIM" in label
    assert "NO REPLAY" in label.upper()
    for banned in ("APPROVED FOR PAPER", "APPROVED FOR LIVE", "PROFITABLE",
                   "EDGE CONFIRMED", "GUARANTEE", "READY FOR LIVE"):
        assert banned not in label.upper(), banned


def test_honest_caveats_present():
    joined = " || ".join(_R["honest_caveats"]).lower()
    assert "not long-drift" in joined
    assert "no replay" in joined
    assert "buy-and-hold" in joined or "random-entry" in joined
    assert "forward-oos" in joined
    assert "sample-size gate" in joined


# ---- artifacts remain untracked --------------------------------------------

def test_label_artifacts_remain_untracked():
    tracked = _tracked_paths()
    assert c14l.LABELS_PATH not in tracked
    assert c14l.SUMMARY_PATH not in tracked
    for p in tracked:
        assert not p.startswith(
            "data/conviction_bar_follow_through_c14/"), p


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(c14l.__file__, encoding="utf-8").read()
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
