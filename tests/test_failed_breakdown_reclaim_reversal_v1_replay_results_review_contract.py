"""Tests for the Candidate #12 fee-honest replay-results review contract
(failed_breakdown_reclaim_reversal_v1).

Verifies: chain-gate on the FROZEN C12 labels review; verdict FROZEN; SHA pins of
the labels + the two untracked replay artifacts + the 3 sources; the honest
DECISIVE outcome -- net negative every variant, worse than random entry, all
regimes negative, forward-OOS 2026 negative, target capture does not dominate ->
structural rejection pressure; anti-tamper (negative findings cannot be flipped);
all downstream gates locked; no profitability / paper-live readiness claim; the
artifacts remain untracked; AST/purity green.

The shared chain is memoized once at import."""
from __future__ import annotations

import ast
import copy
import inspect
import subprocess
import sys

import sparta_commander.failed_breakdown_reclaim_reversal_v1_replay_results_review_contract as c12rr  # noqa: E501


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
    _R = c12rr.build_c12_replay_review(".", _tracked_paths())
finally:
    for _mod, _attr, _orig in _memo_restore:
        setattr(_mod, _attr, _orig)


# ---- chain gate + verdict --------------------------------------------------

def test_review_frozen_and_validates():
    assert _R["verdict"] == c12rr.VERDICT_C12RR_FROZEN
    assert _R["blockers"] == []
    assert _R["labels_review_verdict"] == c12rr.VERDICT_C12L_FROZEN
    assert c12rr.validate_c12_replay_review(_R)["valid"] is True


def test_sha_pins_frozen():
    assert _R["expected_labels_sha256"] == c12rr.EXPECTED_LABELS_SHA256
    assert _R["expected_replay_ledger_sha256"] == c12rr.EXPECTED_REPLAY_LEDGER_SHA256
    assert _R["expected_replay_summary_sha256"] == c12rr.EXPECTED_REPLAY_SUMMARY_SHA256
    for s in ("BTCUSD", "ETHUSD", "SOLUSD"):
        assert _R["expected_source_sha256"][s] == c12rr.EXPECTED_SOURCE_SHA256[s]
    assert _R["head_at_labels_review"] == (
        "f9b510d9d8a4cb50bfb17bad5e5fa47f8e7b4038")
    bad = copy.deepcopy(_R)
    bad["expected_replay_ledger_sha256"] = "0" * 64
    assert c12rr.validate_c12_replay_review(bad)["valid"] is False


# ---- cost basis ------------------------------------------------------------

def test_cost_basis_intact():
    assert _R["all_in_round_trip_bps"] == 37.0
    assert _R["fee_round_trip_bps"] + _R["slippage_round_trip_bps"] == 37.0
    bad = copy.deepcopy(_R)
    bad["all_in_round_trip_bps"] = 5.0
    assert c12rr.validate_c12_replay_review(bad)["valid"] is False


# ---- the honest decisive failure -------------------------------------------

def test_no_variant_passes_structural_rejection_pressure():
    assert _R["any_variant_passes_all_decisive_gates"] is False
    assert _R["structural_rejection_pressure"] is True
    for bad_key in ("any_variant_passes_all_decisive_gates",):
        bad = copy.deepcopy(_R)
        bad[bad_key] = True
        assert c12rr.validate_c12_replay_review(bad)["valid"] is False
    bad2 = copy.deepcopy(_R)
    bad2["structural_rejection_pressure"] = False
    assert c12rr.validate_c12_replay_review(bad2)["valid"] is False


def test_net_negative_every_variant():
    for name in ("1.5r", "2r", "3r"):
        v = _R["replay_aggregates"][name]
        assert v["net_r_total_all_in"] < 0, name
        assert v["net_all_in_positive"] is False
        assert v["beats_random_entry_mean"] is False
        bad = copy.deepcopy(_R)
        bad["replay_aggregates"][name]["net_r_total_all_in"] = 10.0
        assert c12rr.validate_c12_replay_review(bad)["valid"] is False, name


def test_worse_than_random_entry():
    dg = _R["decisive_gate_results"]
    assert dg["beats_random_entry_any_variant"] is False
    for name in ("1.5r", "2r", "3r"):
        v = _R["replay_aggregates"][name]
        assert v["random_entry_percentile"] <= 0.05
        assert v["net_r_total_all_in"] < v["random_entry_mean_net_all_in"]
    assert _R["rejection_warnings"]["worse_than_random_entry_baseline"] is True


def test_all_regimes_negative_and_forward_oos_negative():
    for name in ("1.5r", "2r", "3r"):
        v = _R["replay_aggregates"][name]
        pr = v["per_regime_net_all_in"]
        assert pr["bull"] < 0 and pr["bear"] < 0 and pr["chop"] < 0, name
        assert v["forward_oos_net_all_in"] < 0, name
    assert _R["rejection_warnings"]["all_regimes_net_negative"] is True
    assert _R["rejection_warnings"]["negative_forward_oos_2026"] is True
    bad = copy.deepcopy(_R)
    bad["replay_aggregates"]["2r"]["per_regime_net_all_in"]["bear"] = 5.0
    assert c12rr.validate_c12_replay_review(bad)["valid"] is False


def test_target_capture_does_not_dominate():
    dg = _R["decisive_gate_results"]
    assert dg["target_capture_dominates_any_variant"] is False
    for name in ("1.5r", "2r", "3r"):
        v = _R["replay_aggregates"][name]
        assert v["target_capture_dominates"] is False
        assert v["hit"] < v["horizon"]
    assert _R["rejection_warnings"]["target_capture_does_not_dominate"] is True


def test_beats_buy_and_hold_is_meaningless():
    # B&H is beaten only because passive hold of the same windows is more negative
    assert _R["decisive_gate_results"]["beats_buy_and_hold_any_variant"] is True
    assert _R["buy_and_hold_net_all_in_total"] < 0
    for name in ("1.5r", "2r", "3r"):
        v = _R["replay_aggregates"][name]
        assert v["net_r_total_all_in"] > _R["buy_and_hold_net_all_in_total"]
        assert v["net_r_total_all_in"] < 0
    assert _R["rejection_warnings"][
        "buy_and_hold_only_beaten_because_it_is_more_negative"] is True


def test_rejection_warnings_triggered_list():
    trg = _R["rejection_warnings_triggered"]
    for w in ("negative_all_in_net_all_variants",
              "worse_than_random_entry_baseline", "all_regimes_net_negative",
              "negative_forward_oos_2026", "target_capture_does_not_dominate"):
        assert w in trg, w


# ---- locks + capability flags + claim locks --------------------------------

def test_all_downstream_gates_locked():
    assert _R["is_replay_review_only"] is True
    for gate in ("robustness_gate_locked", "relabel_gate_locked",
                 "data_fetch_gate_locked", "portfolio_compute_gate_locked",
                 "paper_trading_gate_locked", "micro_live_gate_locked",
                 "live_gate_locked", "human_review_required"):
        assert _R[gate] is True, gate
    for key, val in _R["scope_locks"].items():
        assert val is True, key


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in c12rr._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = copy.deepcopy(_R)
        bad[flag] = True
        assert c12rr.validate_c12_replay_review(bad)["valid"] is False, flag


def test_claim_locks_and_label_no_readiness():
    for required in ("no_profitability_claim",
                     "fails_must_beat_random_entry_disclosed",
                     "all_regimes_negative_disclosed",
                     "negative_forward_oos_disclosed",
                     "structural_rejection_pressure_disclosed"):
        assert required in _R["claim_locks"], required
    label = c12rr.get_candidate_12_replay_review_label()
    assert "RESEARCH ONLY" in label
    assert "NOT A PROFITABILITY CLAIM" in label
    for banned in ("APPROVED FOR PAPER", "APPROVED FOR LIVE", "PROFITABLE",
                   "EDGE CONFIRMED", "READY FOR LIVE"):
        assert banned not in label.upper(), banned


def test_next_action_is_human_decision_no_execution_token():
    nra = c12rr.get_candidate_12_replay_review_next_action()
    assert nra == "HUMAN_DECISION_C12_PROMOTE_TO_ROBUSTNESS_OR_REJECT"
    for banned in ("APPROVE", "PAPER", "LIVE", "EXECUTE", "BROKER", "ORDER",
                   "FETCH", "UNLOCK"):
        assert banned not in nra.upper(), banned


# ---- replay artifacts remain untracked -------------------------------------

def test_replay_artifacts_remain_untracked():
    tracked = _tracked_paths()
    assert c12rr.LEDGER_PATH not in tracked
    assert c12rr.SUMMARY_PATH not in tracked
    for p in tracked:
        assert not p.startswith(
            "data/failed_breakdown_reclaim_reversal_c12/"), p


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(c12rr.__file__, encoding="utf-8").read()
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
