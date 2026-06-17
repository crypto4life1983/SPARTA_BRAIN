"""Tests for the Candidate #12 formal rejection / closeout record contract
(failed_breakdown_reclaim_reversal_v1).

Verifies: chain-gate on the pushed FROZEN replay review carrying
structural_rejection_pressure=True and any_variant_passes_all_decisive_gates=
False; verdict RECORDED = REJECTED_KEPT_ON_RECORD; not active and not
parked-as-active; the full pushed evidence trail (proposal -> spec -> detector ->
labels -> replay) with 40-hex commits for ALL FIVE pushed gates; the rejection
reasons cite the negative edge + worse-than-random + all-regimes-negative +
forward-OOS failure + target-capture failure; anti-tamper (cannot flip to active
/ cannot clear the negative findings); all downstream gates locked; no
profitability / paper-live readiness claim; AST/purity green.

The shared chain is memoized once at import."""
from __future__ import annotations

import ast
import copy
import inspect
import subprocess
import sys

import sparta_commander.failed_breakdown_reclaim_reversal_v1_rejection_record_contract as rj12  # noqa: E501


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
    _R = rj12.build_c12_rejection_record(".", _tracked_paths())
finally:
    for _mod, _attr, _orig in _memo_restore:
        setattr(_mod, _attr, _orig)


# ---- verdict + rejection status --------------------------------------------

def test_record_recorded_and_validates():
    assert _R["verdict"] == rj12.VERDICT_RJ12_RECORDED
    assert _R["verdict"] == "C12_REJECTED_KEPT_ON_RECORD_FAILED_FEE_HONEST_REPLAY"
    assert _R["blockers"] == []
    assert _R["rejection_status"] == "REJECTED_KEPT_ON_RECORD"
    assert rj12.validate_c12_rejection_record(_R)["valid"] is True


def test_not_active_not_parked_kept_on_record():
    assert _R["is_active_candidate"] is False
    assert _R["parked_as_active"] is False
    assert _R["kept_on_record"] is True
    assert _R["original_frozen_c12_result_unchanged"] is True
    for bad_key in ("is_active_candidate", "parked_as_active"):
        bad = copy.deepcopy(_R)
        bad[bad_key] = True
        assert rj12.validate_c12_rejection_record(bad)["valid"] is False, bad_key


# ---- chain gate: replay negative-edge is the basis -------------------------

def test_chain_gate_on_replay_structural_rejection():
    assert _R["replay_review_verdict"] == rj12.VERDICT_C12RR_FROZEN
    assert _R["replay_structural_rejection_pressure"] is True
    assert _R["replay_any_variant_passes_all_decisive_gates"] is False
    bad = copy.deepcopy(_R)
    bad["replay_structural_rejection_pressure"] = False
    assert rj12.validate_c12_rejection_record(bad)["valid"] is False
    bad2 = copy.deepcopy(_R)
    bad2["replay_any_variant_passes_all_decisive_gates"] = True
    assert rj12.validate_c12_rejection_record(bad2)["valid"] is False


# ---- evidence trail (all 5 pushed gates) -----------------------------------

def test_pushed_evidence_chain_cites_five_gates_with_commits():
    chain = _R["pushed_evidence_chain"]
    stages = {e["stage"]: e for e in chain}
    for required, commit in (
            ("family_proposal", "710429b7a71b7ba4d23567b64e16062f55bf3bc4"),
            ("candidate_spec", "6ad2c1b97edb8985ab9d671130bdbc26afcec55c"),
            ("detector_spec_and_synthetic_dry_run",
             "c29c165cf0fc95dabf2da828c16977b4866df994"),
            ("real_candle_labels_review",
             "f9b510d9d8a4cb50bfb17bad5e5fa47f8e7b4038"),
            ("fee_slippage_honest_replay_review",
             "70116e70e7770d6b9ef4ecb38d7106613e52861e")):
        assert required in stages, required
        assert stages[required]["commit"] == commit, required
        assert len(stages[required]["commit"]) == 40
    assert _R["head_at_replay_review"] == (
        "70116e70e7770d6b9ef4ecb38d7106613e52861e")


def test_evidence_headline_records_the_failure():
    eh = _R["evidence_headline"]
    assert eh["accepted_labels"] == 206
    assert eh["labels_battery_passed"] is True
    assert eh["net_negative_all_variants"] is True
    assert eh["worse_than_random_entry"] is True
    assert eh["all_regimes_negative"] is True
    assert eh["forward_oos_2026_positive"] is False
    assert eh["net_r_all_in_3r"] < 0
    assert eh["regime_net_all_in_3r"]["bear"] < 0
    bad = copy.deepcopy(_R)
    bad["evidence_headline"]["worse_than_random_entry"] = False
    assert rj12.validate_c12_rejection_record(bad)["valid"] is False


def test_rejection_reasons_and_kept_on_record_lesson():
    reasons = " || ".join(_R["rejection_reasons"]).lower()
    assert "random-entry" in reasons or "random entry" in reasons
    assert "forward-oos" in reasons
    assert "regime" in reasons
    assert "net-negative" in reasons or "net negative" in reasons
    lesson = " || ".join(_R["kept_on_record_as"]).lower()
    assert "necessary but not sufficient" in lesson
    assert "random-entry" in lesson or "random entry" in lesson


# ---- locks + capability flags + claim locks --------------------------------

def test_all_gates_locked():
    for gate in ("robustness_gate_locked", "relabel_gate_locked",
                 "replay_gate_locked", "paper_trading_gate_locked",
                 "micro_live_gate_locked", "live_gate_locked"):
        assert _R[gate] is True, gate
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_new_replay", "no_robustness_run", "no_optimization",
                 "no_relabel", "no_portfolio_compute"):
        assert _R["scope_locks"][must] is True, must


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in rj12._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = copy.deepcopy(_R)
        bad[flag] = True
        assert rj12.validate_c12_rejection_record(bad)["valid"] is False, flag


def test_claim_locks_and_label_no_readiness():
    for required in ("no_profitability_claim",
                     "kept_on_record_not_active_candidate",
                     "not_parked_as_active",
                     "no_relabel_of_original_result", "no_new_replay",
                     "worse_than_random_entry_disclosed"):
        assert required in _R["claim_locks"], required
    label = rj12.get_candidate_12_rejection_record_label()
    assert "RESEARCH ONLY" in label
    assert "REJECTED_KEPT_ON_RECORD" in label
    assert "NOT AN ACTIVE CANDIDATE" in label
    for banned in ("APPROVED FOR PAPER", "APPROVED FOR LIVE", "PROFITABLE",
                   "EDGE CONFIRMED", "READY FOR LIVE"):
        assert banned not in label.upper(), banned


def test_next_action_is_closed_no_execution_token():
    nra = rj12.get_candidate_12_rejection_record_next_action()
    assert nra.startswith("NONE__C12_CLOSED")
    for banned in ("APPROVE", "PAPER", "LIVE", "EXECUTE", "BROKER", "ORDER",
                   "PROMOTE", "UNLOCK"):
        assert banned not in nra.upper(), banned


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(rj12.__file__, encoding="utf-8").read()
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
