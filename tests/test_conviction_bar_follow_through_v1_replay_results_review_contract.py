"""Tests for the Candidate #14 fee-honest replay-results review contract
(conviction_bar_follow_through_v1).

Verifies: chain-gate on the FROZEN C14 labels review; verdict FROZEN; SHA pins of
the labels + the two untracked replay artifacts + the 3 sources; the honest
decisive outcome -- BEATS random-entry (notable positive, first candidate) but
LOSES to buy-and-hold every variant, forward-OOS 2026 negative every variant,
target capture does not dominate -> structural rejection pressure; anti-tamper
(negative findings cannot be flipped, beats-random positive cannot be cleared);
all downstream gates locked; no profitability / paper-live readiness claim; the
artifacts remain untracked; AST/purity green.

The shared chain is memoized once at import."""
from __future__ import annotations

import ast
import copy
import inspect
import subprocess
import sys

import sparta_commander.conviction_bar_follow_through_v1_replay_results_review_contract as c14rr  # noqa: E501


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
    _R = c14rr.build_c14_replay_review(".", _tracked_paths())
finally:
    for _mod, _attr, _orig in _memo_restore:
        setattr(_mod, _attr, _orig)


# ---- chain gate + verdict --------------------------------------------------

def test_review_frozen_and_validates():
    assert _R["verdict"] == c14rr.VERDICT_C14RR_FROZEN
    assert _R["blockers"] == []
    assert _R["labels_review_verdict"] == c14rr.VERDICT_C14L_FROZEN
    assert c14rr.validate_c14_replay_review(_R)["valid"] is True


def test_sha_pins_frozen():
    assert _R["expected_labels_sha256"] == c14rr.EXPECTED_LABELS_SHA256
    assert _R["expected_replay_ledger_sha256"] == c14rr.EXPECTED_REPLAY_LEDGER_SHA256
    assert _R["expected_replay_summary_sha256"] == c14rr.EXPECTED_REPLAY_SUMMARY_SHA256
    for s in ("BTCUSD", "ETHUSD", "SOLUSD"):
        assert _R["expected_source_sha256"][s] == c14rr.EXPECTED_SOURCE_SHA256[s]
    assert _R["head_at_labels_review"] == (
        "bc69e4f0b0cf1e63ed00d6cb02b991f3d9d22ac6")
    bad = copy.deepcopy(_R)
    bad["expected_replay_ledger_sha256"] = "0" * 64
    assert c14rr.validate_c14_replay_review(bad)["valid"] is False


def test_cost_basis_intact():
    assert _R["all_in_round_trip_bps"] == 37.0
    assert _R["fee_round_trip_bps"] + _R["slippage_round_trip_bps"] == 37.0
    bad = copy.deepcopy(_R)
    bad["all_in_round_trip_bps"] = 5.0
    assert c14rr.validate_c14_replay_review(bad)["valid"] is False


# ---- the honest decisive failure -------------------------------------------

def test_no_variant_passes_structural_rejection_pressure():
    assert _R["any_variant_passes_all_decisive_gates"] is False
    assert _R["structural_rejection_pressure"] is True
    bad = copy.deepcopy(_R)
    bad["any_variant_passes_all_decisive_gates"] = True
    assert c14rr.validate_c14_replay_review(bad)["valid"] is False
    bad2 = copy.deepcopy(_R)
    bad2["structural_rejection_pressure"] = False
    assert c14rr.validate_c14_replay_review(bad2)["valid"] is False


def test_loses_to_buy_and_hold_every_variant():
    dg = _R["decisive_gate_results"]
    assert dg["beats_buy_and_hold_any_variant"] is False
    bh = _R["buy_and_hold_net_all_in_total"]
    assert bh > 0
    for name in ("1r", "1.5r", "2r"):
        v = _R["replay_aggregates"][name]
        assert v["beats_buy_and_hold"] is False
        assert v["net_r_total_all_in"] < bh
    assert _R["rejection_warnings"]["loses_to_buy_and_hold_all_variants"] is True
    bad = copy.deepcopy(_R)
    bad["replay_aggregates"]["2r"]["beats_buy_and_hold"] = True
    assert c14rr.validate_c14_replay_review(bad)["valid"] is False


def test_beats_random_entry_notable_positive():
    dg = _R["decisive_gate_results"]
    assert dg["beats_random_entry_any_variant"] is True
    for name in ("1r", "1.5r", "2r"):
        v = _R["replay_aggregates"][name]
        assert v["beats_random_entry_mean"] is True
        assert v["net_r_total_all_in"] > v["random_entry_mean_net_all_in"]
    assert _R["notable_positives"]["beats_random_entry_all_variants"] is True
    # the positive must remain disclosed (anti-tamper both ways)
    bad = copy.deepcopy(_R)
    bad["decisive_gate_results"]["beats_random_entry_any_variant"] = False
    assert c14rr.validate_c14_replay_review(bad)["valid"] is False


def test_forward_oos_negative_and_target_capture_fails():
    for name in ("1r", "1.5r", "2r"):
        v = _R["replay_aggregates"][name]
        assert v["forward_oos_net_all_in"] < 0, name
        assert v["target_capture_dominates"] is False, name
        assert v["hit"] < v["horizon"], name
    assert _R["rejection_warnings"]["negative_forward_oos_2026_all_variants"] is True
    assert _R["rejection_warnings"][
        "target_capture_does_not_dominate_all_variants"] is True
    bad = copy.deepcopy(_R)
    bad["replay_aggregates"]["1r"]["forward_oos_net_all_in"] = 5.0
    assert c14rr.validate_c14_replay_review(bad)["valid"] is False


def test_carry_signature_disclosed():
    assert _R["rejection_warnings"][
        "beats_random_but_loses_to_buy_and_hold_is_carry_signature"] is True
    assert "carry_signature_disclosed" in _R["claim_locks"]
    joined = " || ".join(_R["honest_caveats"]).lower()
    assert "carry signature" in joined
    assert "beats" in joined and "random" in joined


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
    for flag in c14rr._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = copy.deepcopy(_R)
        bad[flag] = True
        assert c14rr.validate_c14_replay_review(bad)["valid"] is False, flag


def test_claim_locks_and_label_no_readiness():
    for required in ("no_profitability_claim", "loses_to_buy_and_hold_disclosed",
                     "negative_forward_oos_disclosed", "carry_signature_disclosed",
                     "structural_rejection_pressure_disclosed"):
        assert required in _R["claim_locks"], required
    label = c14rr.get_candidate_14_replay_review_label()
    assert "RESEARCH ONLY" in label
    assert "NOT A PROFITABILITY CLAIM" in label
    for banned in ("APPROVED FOR PAPER", "APPROVED FOR LIVE", "PROFITABLE",
                   "EDGE CONFIRMED", "READY FOR LIVE"):
        assert banned not in label.upper(), banned


def test_next_action_is_human_decision_no_execution_token():
    nra = c14rr.get_candidate_14_replay_review_next_action()
    assert nra == "HUMAN_DECISION_C14_PROMOTE_TO_ROBUSTNESS_OR_REJECT"
    for banned in ("APPROVE", "PAPER", "LIVE", "EXECUTE", "BROKER", "ORDER",
                   "FETCH", "UNLOCK"):
        assert banned not in nra.upper(), banned


# ---- replay artifacts remain untracked -------------------------------------

def test_replay_artifacts_remain_untracked():
    tracked = _tracked_paths()
    assert c14rr.LEDGER_PATH not in tracked
    assert c14rr.SUMMARY_PATH not in tracked
    for p in tracked:
        assert not p.startswith(
            "data/conviction_bar_follow_through_c14/"), p


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(c14rr.__file__, encoding="utf-8").read()
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
