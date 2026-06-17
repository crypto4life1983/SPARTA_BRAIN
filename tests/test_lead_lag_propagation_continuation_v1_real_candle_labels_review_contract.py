"""Tests for the Candidate #13 real-candle labels review contract
(lead_lag_propagation_continuation_v1).

Verifies: chain-gate on the READY C13 detector dry-run; verdict STRUCTURAL
REJECTION (the labels FAIL the structural checks); SHA pins of the 3 sources +
the two untracked label artifacts; the failing labels-stage facts (41 < 100
total; ETH 18 < 20; all regimes < 20; ZERO forward-OOS 2026); NO replay/PnL/
baseline in this gate; anti-tamper (the failing findings cannot be flipped to a
pass); all downstream gates locked; no profitability / paper-live readiness
claim; the artifacts remain untracked; AST/purity green.

The shared chain is memoized once at import."""
from __future__ import annotations

import ast
import copy
import inspect
import subprocess
import sys

import sparta_commander.lead_lag_propagation_continuation_v1_real_candle_labels_review_contract as c13l  # noqa: E501


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
    _R = c13l.build_c13_labels_review(".", _tracked_paths())
finally:
    for _mod, _attr, _orig in _memo_restore:
        setattr(_mod, _attr, _orig)


# ---- chain gate + verdict (structural rejection) ---------------------------

def test_review_structural_rejection_and_validates():
    assert _R["verdict"] == c13l.VERDICT_C13L_STRUCTURAL_REJECTION
    assert _R["blockers"] == []
    assert _R["detector_dry_run_verdict"] == c13l.VERDICT_C13DD_READY
    assert c13l.validate_c13_labels_review(_R)["valid"] is True


def test_sha_pins_frozen():
    assert _R["expected_labels_sha256"] == c13l.EXPECTED_LABELS_SHA256
    assert _R["expected_summary_sha256"] == c13l.EXPECTED_SUMMARY_SHA256
    for s in ("BTCUSD", "ETHUSD", "SOLUSD"):
        assert _R["expected_source_sha256"][s] == c13l.EXPECTED_SOURCE_SHA256[s]
    assert _R["head_at_detector_dry_run"] == (
        "d32047c124168b3e478d7e181dfe6155d14d3604")
    bad = copy.deepcopy(_R)
    bad["expected_labels_sha256"] = "0" * 64
    assert c13l.validate_c13_labels_review(bad)["valid"] is False


# ---- the failing labels-stage facts ----------------------------------------

def test_under_powered_counts():
    assert _R["accepted_label_count"] == 41
    assert _R["accepted_label_count"] < _R["min_labels_total"]
    assert _R["per_follower"]["ETHUSD"] == 18
    assert _R["per_follower"]["ETHUSD"] < _R["min_per_follower"]
    for r in ("bull", "bear", "chop"):
        assert _R["per_regime"][r] < _R["min_per_regime"]
    assert _R["sample_size_passed"] is False
    # cannot be flipped
    bad = copy.deepcopy(_R)
    bad["sample_size_passed"] = True
    assert c13l.validate_c13_labels_review(bad)["valid"] is False
    bad2 = copy.deepcopy(_R)
    bad2["accepted_label_count"] = 500
    assert c13l.validate_c13_labels_review(bad2)["valid"] is False


def test_zero_forward_oos_labels():
    assert _R["forward_oos_label_count"] == 0
    assert _R["structural_checks_battery"]["forward_oos_window_reserved"] is False
    bad = copy.deepcopy(_R)
    bad["forward_oos_label_count"] = 22
    assert c13l.validate_c13_labels_review(bad)["valid"] is False


def test_structural_rejection_pressure_and_battery_failed():
    assert _R["structural_rejection_pressure"] is True
    assert _R["structural_checks_battery"]["passed"] is False
    assert _R["structural_checks_battery"]["both_followers_present_ok"] is False
    assert _R["structural_checks_battery"]["cross_regime_coverage_ok"] is False
    for bad_key, val in (("structural_rejection_pressure", False),):
        bad = copy.deepcopy(_R)
        bad[bad_key] = val
        assert c13l.validate_c13_labels_review(bad)["valid"] is False
    bad2 = copy.deepcopy(_R)
    bad2["structural_checks_battery"]["passed"] = True
    assert c13l.validate_c13_labels_review(bad2)["valid"] is False


def test_rejection_reasons_recorded():
    rr = _R["rejection_reasons"]
    for key in ("total_below_minimum", "per_follower_below_minimum",
                "per_regime_below_minimum", "zero_forward_oos_labels"):
        assert rr[key] is True, key
        bad = copy.deepcopy(_R)
        bad["rejection_reasons"][key] = False
        assert c13l.validate_c13_labels_review(bad)["valid"] is False, key


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
    for flag in c13l._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = copy.deepcopy(_R)
        bad[flag] = True
        assert c13l.validate_c13_labels_review(bad)["valid"] is False, flag


def test_claim_locks_and_label_no_readiness():
    for required in ("no_profitability_claim", "no_replay_in_this_gate",
                     "no_baseline_comparison_in_this_gate",
                     "structural_rejection_at_labels_stage",
                     "zero_forward_oos_labels_disclosed"):
        assert required in _R["claim_locks"], required
    label = c13l.get_candidate_13_labels_review_label()
    assert "RESEARCH ONLY" in label
    assert "NOT A PROFITABILITY CLAIM" in label
    assert "STRUCTURAL REJECTION" in label.upper()
    for banned in ("APPROVED FOR PAPER", "APPROVED FOR LIVE", "PROFITABLE",
                   "EDGE CONFIRMED", "GUARANTEE", "READY FOR LIVE"):
        assert banned not in label.upper(), banned


def test_next_action_is_human_decision():
    nra = c13l.get_candidate_13_labels_review_next_action()
    assert nra == "HUMAN_DECISION_C13_REJECT_OR_INVOKE_ONE_EDIT_ALLOWANCE"
    for banned in ("APPROVE", "PAPER", "LIVE", "EXECUTE", "BROKER", "ORDER"):
        assert banned not in nra.upper(), banned


# ---- artifacts remain untracked --------------------------------------------

def test_label_artifacts_remain_untracked():
    tracked = _tracked_paths()
    assert c13l.LABELS_PATH not in tracked
    assert c13l.SUMMARY_PATH not in tracked
    for p in tracked:
        assert not p.startswith(
            "data/lead_lag_propagation_continuation_c13/"), p


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(c13l.__file__, encoding="utf-8").read()
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
