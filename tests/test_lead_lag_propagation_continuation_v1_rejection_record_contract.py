"""Tests for the Candidate #13 formal rejection / closeout record contract
(lead_lag_propagation_continuation_v1).

Verifies: chain-gate on the pushed STRUCTURAL_REJECTION labels review (carrying
structural_rejection_pressure=True and sample_size_passed=False); verdict
RECORDED = REJECTED_KEPT_ON_RECORD at the LABELS stage (never reached replay);
not active and not parked-as-active; the one-edit allowance was DECLINED; the full
pushed evidence trail (proposal -> spec -> detector -> labels) with 40-hex commits
for all FOUR pushed gates; the rejection reasons cite the under-powered sample +
zero forward-OOS + anti-curve-fit; anti-tamper (cannot flip to active / cannot
clear the failing facts / cannot mark one-edit invoked); all downstream gates
locked; no profitability / paper-live readiness claim; AST/purity green.

The shared chain is memoized once at import."""
from __future__ import annotations

import ast
import copy
import inspect
import subprocess
import sys

import sparta_commander.lead_lag_propagation_continuation_v1_rejection_record_contract as rj13  # noqa: E501


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
    _R = rj13.build_c13_rejection_record(".", _tracked_paths())
finally:
    for _mod, _attr, _orig in _memo_restore:
        setattr(_mod, _attr, _orig)


# ---- verdict + rejection status --------------------------------------------

def test_record_recorded_and_validates():
    assert _R["verdict"] == rj13.VERDICT_RJ13_RECORDED
    assert _R["verdict"] == (
        "C13_REJECTED_KEPT_ON_RECORD_FAILED_LABELS_STRUCTURAL_CHECKS")
    assert _R["blockers"] == []
    assert _R["rejection_status"] == "REJECTED_KEPT_ON_RECORD"
    assert rj13.validate_c13_rejection_record(_R)["valid"] is True


def test_rejected_at_labels_stage_never_reached_replay():
    assert _R["rejection_stage"] == "real_candle_labels_review"
    assert _R["reached_replay_stage"] is False
    bad = copy.deepcopy(_R)
    bad["reached_replay_stage"] = True
    assert rj13.validate_c13_rejection_record(bad)["valid"] is False


def test_one_edit_declined():
    assert _R["one_edit_allowance_invoked"] is False
    assert "no_one_edit_invoked" in _R["claim_locks"]
    assert _R["scope_locks"]["no_one_edit"] is True
    bad = copy.deepcopy(_R)
    bad["one_edit_allowance_invoked"] = True
    assert rj13.validate_c13_rejection_record(bad)["valid"] is False


def test_not_active_not_parked_kept_on_record():
    assert _R["is_active_candidate"] is False
    assert _R["parked_as_active"] is False
    assert _R["kept_on_record"] is True
    assert _R["original_frozen_c13_result_unchanged"] is True
    for bad_key in ("is_active_candidate", "parked_as_active"):
        bad = copy.deepcopy(_R)
        bad[bad_key] = True
        assert rj13.validate_c13_rejection_record(bad)["valid"] is False, bad_key


# ---- chain gate: labels structural rejection is the basis ------------------

def test_chain_gate_on_labels_structural_rejection():
    assert _R["labels_review_verdict"] == rj13.VERDICT_C13L_STRUCTURAL_REJECTION
    assert _R["labels_structural_rejection_pressure"] is True
    assert _R["labels_sample_size_passed"] is False
    bad = copy.deepcopy(_R)
    bad["labels_structural_rejection_pressure"] = False
    assert rj13.validate_c13_rejection_record(bad)["valid"] is False
    bad2 = copy.deepcopy(_R)
    bad2["labels_sample_size_passed"] = True
    assert rj13.validate_c13_rejection_record(bad2)["valid"] is False


# ---- evidence trail (4 pushed gates, no replay) ----------------------------

def test_pushed_evidence_chain_cites_four_gates_with_commits():
    chain = _R["pushed_evidence_chain"]
    stages = {e["stage"]: e for e in chain}
    for required, commit in (
            ("family_proposal", "ae97e896ba2fc924df82e97beafb2ecdbaa4c739"),
            ("candidate_spec", "74f4906a282756168ce4838383a18068d9d3591c"),
            ("detector_spec_and_synthetic_dry_run",
             "d32047c124168b3e478d7e181dfe6155d14d3604"),
            ("real_candle_labels_review",
             "c976ed87d1fc1bb97c3901883785ee87b5eccb4d")):
        assert required in stages, required
        assert stages[required]["commit"] == commit, required
        assert len(stages[required]["commit"]) == 40
    # no replay stage in the chain (C13 never reached replay)
    assert "fee_slippage_honest_replay_review" not in stages
    assert _R["head_at_labels_review"] == (
        "c976ed87d1fc1bb97c3901883785ee87b5eccb4d")


def test_evidence_headline_records_the_failure():
    eh = _R["evidence_headline"]
    assert eh["accepted_labels"] == 41
    assert eh["total_below_minimum"] is True
    assert eh["eth_below_per_follower_minimum"] is True
    assert eh["all_regimes_below_minimum"] is True
    assert eh["zero_forward_oos_labels"] is True
    assert eh["labels_stage_structural_battery_failed"] is True
    assert eh["reached_replay_stage"] is False
    assert eh["one_edit_allowance_invoked"] is False
    bad = copy.deepcopy(_R)
    bad["evidence_headline"]["zero_forward_oos_labels"] = False
    assert rj13.validate_c13_rejection_record(bad)["valid"] is False


def test_rejection_reasons_and_kept_on_record_lesson():
    reasons = " || ".join(_R["rejection_reasons"]).lower()
    assert "below the required 100" in reasons
    assert "forward-oos" in reasons
    assert "curve-fitting" in reasons or "curve fit" in reasons
    lesson = " || ".join(_R["kept_on_record_as"]).lower()
    assert "labels-stage" in lesson
    assert "before any replay" in lesson


# ---- locks + capability flags + claim locks --------------------------------

def test_all_gates_locked():
    for gate in ("one_edit_gate_locked", "labels_relabel_gate_locked",
                 "replay_gate_locked", "robustness_gate_locked",
                 "paper_trading_gate_locked", "micro_live_gate_locked",
                 "live_gate_locked"):
        assert _R[gate] is True, gate
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_one_edit", "no_replay", "no_robustness_run",
                 "no_z_threshold_reselection", "no_lag_margin_reselection",
                 "no_optimization", "no_portfolio_compute"):
        assert _R["scope_locks"][must] is True, must


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in rj13._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = copy.deepcopy(_R)
        bad[flag] = True
        assert rj13.validate_c13_rejection_record(bad)["valid"] is False, flag


def test_claim_locks_and_label_no_readiness():
    for required in ("no_profitability_claim",
                     "kept_on_record_not_active_candidate",
                     "not_parked_as_active", "no_one_edit_invoked",
                     "no_relabel_of_original_result", "no_replay",
                     "labels_stage_structural_rejection_is_the_rejection_basis"):
        assert required in _R["claim_locks"], required
    label = rj13.get_candidate_13_rejection_record_label()
    assert "RESEARCH ONLY" in label
    assert "REJECTED_KEPT_ON_RECORD" in label
    assert "NOT AN ACTIVE CANDIDATE" in label
    for banned in ("APPROVED FOR PAPER", "APPROVED FOR LIVE", "PROFITABLE",
                   "EDGE CONFIRMED", "READY FOR LIVE"):
        assert banned not in label.upper(), banned


def test_next_action_is_closed_no_execution_token():
    nra = rj13.get_candidate_13_rejection_record_next_action()
    assert nra.startswith("NONE__C13_CLOSED")
    for banned in ("APPROVE", "PAPER", "LIVE", "EXECUTE", "BROKER", "ORDER",
                   "PROMOTE", "UNLOCK"):
        assert banned not in nra.upper(), banned


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(rj13.__file__, encoding="utf-8").read()
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
