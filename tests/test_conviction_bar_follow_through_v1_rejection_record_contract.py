"""Tests for the Candidate #14 formal rejection / closeout record contract
(conviction_bar_follow_through_v1).

Verifies: chain-gate on the FROZEN replay review carrying
structural_rejection_pressure=True and any_variant_passes_all_decisive_gates=
False; verdict RECORDED = REJECTED_KEPT_ON_RECORD; not active / not parked; the
KEY POSITIVES preserved (first to beat random, net+ at 1.5R/2R, 2R regime-
symmetric, bear+ all variants); the DECISIVE rejection reasons preserved (loses
to B&H all, forward-OOS neg all, target-capture fails, structural rejection
pressure); the verbatim CONCLUSION; the 4 pushed-gate commits + the SHA-anchored
replay stage; the added-to-rejected-ledger flag; anti-tamper; all gates locked;
no profitability/paper-live claim; AST/purity green.

The shared chain is memoized once at import."""
from __future__ import annotations

import ast
import copy
import inspect
import subprocess
import sys

import sparta_commander.conviction_bar_follow_through_v1_rejection_record_contract as rj14  # noqa: E501


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
    _R = rj14.build_c14_rejection_record(".", _tracked_paths())
finally:
    for _mod, _attr, _orig in _memo_restore:
        setattr(_mod, _attr, _orig)


# ---- verdict + rejection status --------------------------------------------

def test_record_recorded_and_validates():
    assert _R["verdict"] == rj14.VERDICT_RJ14_RECORDED
    assert _R["verdict"] == "C14_REJECTED_KEPT_ON_RECORD_FAILED_FEE_HONEST_REPLAY"
    assert _R["blockers"] == []
    assert _R["rejection_status"] == "REJECTED_KEPT_ON_RECORD"
    assert rj14.validate_c14_rejection_record(_R)["valid"] is True


def test_not_active_not_parked_kept_on_record_and_ledger():
    assert _R["is_active_candidate"] is False
    assert _R["parked_as_active"] is False
    assert _R["kept_on_record"] is True
    assert _R["original_frozen_c14_result_unchanged"] is True
    assert _R["added_to_rejected_family_ledger"] is True
    for bad_key in ("is_active_candidate", "parked_as_active"):
        bad = copy.deepcopy(_R)
        bad[bad_key] = True
        assert rj14.validate_c14_rejection_record(bad)["valid"] is False, bad_key


# ---- verbatim conclusion ---------------------------------------------------

def test_verbatim_conclusion_recorded():
    assert _R["conclusion"] == (
        "Conviction-bar follow-through appears to contain timing information, "
        "but the timing advantage was insufficient to produce a durable "
        "tradeable edge after fees and forward validation.")
    bad = copy.deepcopy(_R)
    bad["conclusion"] = "edge confirmed"
    assert rj14.validate_c14_rejection_record(bad)["valid"] is False


# ---- chain gate: replay structural rejection -------------------------------

def test_chain_gate_on_replay_structural_rejection():
    assert _R["replay_review_verdict"] == rj14.VERDICT_C14RR_FROZEN
    assert _R["replay_structural_rejection_pressure"] is True
    assert _R["replay_any_variant_passes_all_decisive_gates"] is False
    assert _R["replay_beats_random_entry_any_variant"] is True
    bad = copy.deepcopy(_R)
    bad["replay_structural_rejection_pressure"] = False
    assert rj14.validate_c14_rejection_record(bad)["valid"] is False
    bad2 = copy.deepcopy(_R)
    bad2["replay_any_variant_passes_all_decisive_gates"] = True
    assert rj14.validate_c14_rejection_record(bad2)["valid"] is False


# ---- preserved KEY POSITIVES -----------------------------------------------

def test_key_positive_findings_preserved():
    joined = " || ".join(_R["key_positive_findings"]).lower()
    assert "first sparta candidate to beat" in joined
    assert "random-entry" in joined
    assert "net-positive after 37 bps" in joined
    assert "regime-symmetric at 2r" in joined or "bull" in joined
    assert "bear regime is net-positive in all variants" in joined
    eh = _R["evidence_headline"]
    assert eh["beats_random_entry_all_variants"] is True
    assert eh["regime_symmetric_at_2r"] is True
    assert eh["bear_regime_net_positive_all_variants"] is True
    bad = copy.deepcopy(_R)
    bad["evidence_headline"]["beats_random_entry_all_variants"] = False
    assert rj14.validate_c14_rejection_record(bad)["valid"] is False


# ---- preserved DECISIVE REJECTION REASONS ----------------------------------

def test_rejection_reasons_preserved():
    joined = " || ".join(_R["rejection_reasons"]).lower()
    assert "buy-and-hold comparison in every variant" in joined
    assert "forward-oos 2026 is net-negative in every variant" in joined
    assert "target-capture dominance failed" in joined
    assert "structural rejection pressure remains true" in joined
    eh = _R["evidence_headline"]
    assert eh["loses_to_buy_and_hold_all_variants"] is True
    assert eh["forward_oos_2026_positive_any_variant"] is False
    assert eh["target_capture_dominates_any_variant"] is False
    for bad_key, val in (("loses_to_buy_and_hold_all_variants", False),
                         ("forward_oos_2026_positive_any_variant", True)):
        bad = copy.deepcopy(_R)
        bad["evidence_headline"][bad_key] = val
        assert rj14.validate_c14_rejection_record(bad)["valid"] is False, bad_key


# ---- evidence trail (4 pushed gates + SHA-anchored replay stage) -----------

def test_pushed_evidence_chain_cites_four_gates_with_commits():
    chain = _R["pushed_evidence_chain"]
    stages = {e["stage"]: e for e in chain}
    for required, commit in (
            ("family_proposal", "127d959a0aea695ba42993a1fb046a4c2c96823a"),
            ("candidate_spec", "563b9c320ba12977c7b0112f07341ecd41b9b8af"),
            ("detector_spec_and_synthetic_dry_run",
             "989f2ead937d368061b879c599edd4faf5110bba"),
            ("real_candle_labels_review",
             "bc69e4f0b0cf1e63ed00d6cb02b991f3d9d22ac6")):
        assert required in stages, required
        assert stages[required]["commit"] == commit, required
        assert len(stages[required]["commit"]) == 40


def test_replay_stage_sha_anchored_commit_pending():
    rs = _R["replay_results_review_stage"]
    assert rs["stage"] == "fee_slippage_honest_replay_review"
    assert rs["pushed_separately_on_origin"] is False
    assert rs["replay_ledger_sha256"] == rj14.EXPECTED_REPLAY_LEDGER_SHA256
    assert rs["replay_summary_sha256"] == rj14.EXPECTED_REPLAY_SUMMARY_SHA256
    bad = copy.deepcopy(_R)
    bad["replay_results_review_stage"]["replay_ledger_sha256"] = "0" * 64
    assert rj14.validate_c14_rejection_record(bad)["valid"] is False


def test_kept_on_record_lesson():
    lesson = " || ".join(_R["kept_on_record_as"]).lower()
    assert "entry-timing information" in lesson
    assert "buy-and-hold" in lesson
    assert "beats random" in lesson or "random" in lesson


# ---- locks + capability flags + claim locks --------------------------------

def test_all_gates_locked():
    for gate in ("robustness_gate_locked", "relabel_gate_locked",
                 "replay_gate_locked", "one_edit_gate_locked",
                 "paper_trading_gate_locked", "micro_live_gate_locked",
                 "live_gate_locked"):
        assert _R[gate] is True, gate
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_new_replay", "no_one_edit", "no_robustness_run",
                 "no_optimization", "no_portfolio_compute"):
        assert _R["scope_locks"][must] is True, must


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in rj14._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = copy.deepcopy(_R)
        bad[flag] = True
        assert rj14.validate_c14_rejection_record(bad)["valid"] is False, flag


def test_claim_locks_and_label_no_readiness():
    for required in ("no_profitability_claim",
                     "kept_on_record_not_active_candidate",
                     "not_parked_as_active", "no_new_replay",
                     "beats_random_entry_positive_preserved",
                     "loses_to_buy_and_hold_disclosed",
                     "conclusion_recorded_precisely"):
        assert required in _R["claim_locks"], required
    label = rj14.get_candidate_14_rejection_record_label()
    assert "RESEARCH ONLY" in label
    assert "REJECTED_KEPT_ON_RECORD" in label
    assert "NOT AN ACTIVE CANDIDATE" in label
    for banned in ("APPROVED FOR PAPER", "APPROVED FOR LIVE", "PROFITABLE",
                   "EDGE CONFIRMED", "READY FOR LIVE"):
        assert banned not in label.upper(), banned


def test_next_action_is_closed_no_execution_token():
    nra = rj14.get_candidate_14_rejection_record_next_action()
    assert nra.startswith("NONE__C14_CLOSED")
    for banned in ("APPROVE", "PAPER", "LIVE", "EXECUTE", "BROKER", "ORDER",
                   "PROMOTE", "UNLOCK"):
        assert banned not in nra.upper(), banned


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(rj14.__file__, encoding="utf-8").read()
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
