"""Tests for the Candidate #11 real-candle labels review contract
(cross_asset_dispersion_reversion_v1).

Verifies: chain-gate on the READY C11 detector dry-run; verdict FROZEN; SHA pins
of the 3 sources + the two untracked label artifacts; the labels-stage facts
(742 labels; per-asset/per-regime minimums met); the EARLY GENERALIZATION
BATTERY passes at labels (cross-asset, cross-regime, no weekday dependence,
forward-OOS prepared); relative/not-long-drift; no replay/PnL in this gate; no
structural rejection pressure; all downstream gates locked; no profitability /
paper-live readiness claim; the artifacts remain untracked; AST/purity green.

The shared chain is memoized once at import."""
from __future__ import annotations

import ast
import copy
import inspect
import subprocess
import sys

import sparta_commander.cross_asset_dispersion_reversion_v1_real_candle_labels_review_contract as c11l  # noqa: E501


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
    _R = c11l.build_c11_labels_review(".", _tracked_paths())
finally:
    for _mod, _attr, _orig in _memo_restore:
        setattr(_mod, _attr, _orig)


# ---- chain gate + verdict --------------------------------------------------

def test_review_frozen_and_validates():
    assert _R["verdict"] == c11l.VERDICT_C11L_FROZEN
    assert _R["blockers"] == []
    assert _R["detector_dry_run_verdict"] == c11l.VERDICT_C11DD_READY
    assert c11l.validate_c11_labels_review(_R)["valid"] is True


def test_sha_pins_frozen():
    assert _R["expected_labels_sha256"] == c11l.EXPECTED_LABELS_SHA256
    assert _R["expected_summary_sha256"] == c11l.EXPECTED_SUMMARY_SHA256
    for s in ("BTCUSD", "ETHUSD", "SOLUSD"):
        assert _R["expected_source_sha256"][s] == c11l.EXPECTED_SOURCE_SHA256[s]
    assert _R["head_at_detector_dry_run"] == (
        "6e1efd2bb6082aef038b6d0de5578e0f0bdd4519")
    bad = copy.deepcopy(_R)
    bad["expected_labels_sha256"] = "0" * 64
    assert c11l.validate_c11_labels_review(bad)["valid"] is False


# ---- 1-7 label checks: counts, sample size --------------------------------

def test_label_counts_and_sample_size():
    assert _R["accepted_label_count"] == 742
    assert _R["sample_size_passed"] is True
    for s in ("BTCUSD", "ETHUSD", "SOLUSD"):
        assert _R["per_asset"][s] >= 20
    for r in ("bull", "bear", "chop"):
        assert _R["per_regime"][r] >= 20
    bad = copy.deepcopy(_R)
    bad["per_asset"]["ETHUSD"] = 5
    assert c11l.validate_c11_labels_review(bad)["valid"] is False
    bad2 = copy.deepcopy(_R)
    bad2["accepted_label_count"] = 50
    assert c11l.validate_c11_labels_review(bad2)["valid"] is False


def test_relative_not_long_drift():
    assert _R["relative_not_long_drift"] is True
    bad = copy.deepcopy(_R)
    bad["relative_not_long_drift"] = False
    assert c11l.validate_c11_labels_review(bad)["valid"] is False


# ---- 8. early generalization battery passes at labels ----------------------

def test_early_generalization_battery_passes_at_labels():
    b = _R["early_generalization_battery"]
    assert b["cross_asset_coverage_ok"] is True
    assert b["cross_regime_coverage_ok"] is True
    assert b["no_weekday_dependence_ok"] is True
    assert b["forward_oos_window_prepared"] is True
    assert b["passed"] is True
    assert _R["max_weekday_share"] <= 0.25
    assert len(_R["weekday_distribution"]) == 7
    bad = copy.deepcopy(_R)
    bad["early_generalization_battery"]["no_weekday_dependence_ok"] = False
    assert c11l.validate_c11_labels_review(bad)["valid"] is False


def test_forward_oos_reserved_and_still_required_at_replay():
    assert _R["forward_oos_start"] == "2026-01-01"
    assert "forward_oos_still_required_at_replay" in _R["claim_locks"]


# ---- 9. no structural rejection pressure -----------------------------------

def test_no_structural_rejection_pressure():
    assert _R["structural_rejection_pressure"] is False
    bad = copy.deepcopy(_R)
    bad["structural_rejection_pressure"] = True
    assert c11l.validate_c11_labels_review(bad)["valid"] is False


# ---- 10. no replay / PnL in this gate --------------------------------------

def test_no_replay_or_pnl_in_this_gate():
    assert _R["no_replay_or_pnl_in_this_gate"] is True
    assert _R["replay_gate_locked"] is True
    assert _R["pnl_gate_locked"] is True
    assert _R["scope_locks"]["no_replay"] is True
    assert _R["scope_locks"]["no_pnl"] is True


# ---- locks + capability flags + claim locks --------------------------------

def test_all_downstream_gates_locked():
    assert _R["is_labels_review_only"] is True
    for gate in ("replay_gate_locked", "pnl_gate_locked", "robustness_gate_locked",
                 "data_fetch_gate_locked", "paper_trading_gate_locked",
                 "live_gate_locked", "human_review_required"):
        assert _R[gate] is True, gate
    for key, val in _R["scope_locks"].items():
        assert val is True, key


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in c11l._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = copy.deepcopy(_R)
        bad[flag] = True
        assert c11l.validate_c11_labels_review(bad)["valid"] is False, flag


def test_claim_locks_and_label_no_readiness():
    for required in ("no_profitability_claim", "no_replay_in_this_gate",
                     "relative_not_long_drift", "no_best_asset_selection",
                     "forward_oos_still_required_at_replay"):
        assert required in _R["claim_locks"], required
    label = c11l.get_candidate_11_labels_review_label()
    assert "RESEARCH ONLY" in label
    assert "NOT A PROFITABILITY CLAIM" in label
    assert "NO REPLAY" in label.upper()
    for banned in ("APPROVED FOR PAPER", "APPROVED FOR LIVE", "PROFITABLE",
                   "EDGE CONFIRMED", "GUARANTEE", "READY FOR LIVE"):
        assert banned not in label.upper(), banned


def test_honest_caveats_present():
    joined = " || ".join(_R["honest_caveats"]).lower()
    assert "not long-drift" in joined or "not a calendar" in joined
    assert "no replay and no pnl" in joined
    assert "forward-oos" in joined


# ---- artifacts remain untracked --------------------------------------------

def test_label_artifacts_remain_untracked():
    tracked = _tracked_paths()
    assert c11l.LABELS_PATH not in tracked
    assert c11l.SUMMARY_PATH not in tracked
    for p in tracked:
        assert not p.startswith("data/cross_asset_dispersion_reversion_c11/"), p


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(c11l.__file__, encoding="utf-8").read()
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
