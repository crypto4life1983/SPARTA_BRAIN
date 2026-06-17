"""Tests for the Candidate #11 formal rejection / closeout record contract
(cross_asset_dispersion_reversion_v1).

Verifies: chain-gate on the pushed FROZEN replay review carrying
structural_rejection_pressure=True and forward_oos_continuation_passed=False;
verdict RECORDED = REJECTED_KEPT_ON_RECORD; not active and not parked-as-active;
the full pushed evidence trail (proposal -> spec -> detector -> labels -> replay)
with 40-hex commits for the four pushed gates; the originating proposal stage
honestly marked not-separately-pushed; the rejection reasons cite the forward-OOS
failure + regime asymmetry + horizon-drift dominance; anti-tamper (cannot flip to
active / cannot clear the forward-OOS failure); all downstream gates locked; no
profitability / paper-live readiness claim; AST/purity green.

The shared chain is memoized once at import."""
from __future__ import annotations

import ast
import copy
import inspect
import subprocess
import sys

import sparta_commander.cross_asset_dispersion_reversion_v1_rejection_record_contract as rj11  # noqa: E501


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
    _R = rj11.build_c11_rejection_record(".", _tracked_paths())
finally:
    for _mod, _attr, _orig in _memo_restore:
        setattr(_mod, _attr, _orig)


# ---- verdict + rejection status --------------------------------------------

def test_record_recorded_and_validates():
    assert _R["verdict"] == rj11.VERDICT_RJ11_RECORDED
    assert _R["verdict"] == "C11_REJECTED_KEPT_ON_RECORD_FAILED_FEE_HONEST_REPLAY"
    assert _R["blockers"] == []
    assert _R["rejection_status"] == "REJECTED_KEPT_ON_RECORD"
    assert rj11.validate_c11_rejection_record(_R)["valid"] is True


def test_not_active_not_parked_kept_on_record():
    assert _R["is_active_candidate"] is False
    assert _R["parked_as_active"] is False
    assert _R["kept_on_record"] is True
    assert _R["original_frozen_c11_result_unchanged"] is True
    for bad_key in ("is_active_candidate", "parked_as_active"):
        bad = copy.deepcopy(_R)
        bad[bad_key] = True
        assert rj11.validate_c11_rejection_record(bad)["valid"] is False, bad_key


# ---- chain gate: replay forward-OOS failure is the basis -------------------

def test_chain_gate_on_replay_forward_oos_failure():
    assert _R["replay_review_verdict"] == rj11.VERDICT_C11RR_FROZEN
    assert _R["replay_structural_rejection_pressure"] is True
    assert _R["replay_forward_oos_continuation_passed"] is False
    bad = copy.deepcopy(_R)
    bad["replay_forward_oos_continuation_passed"] = True
    assert rj11.validate_c11_rejection_record(bad)["valid"] is False
    bad2 = copy.deepcopy(_R)
    bad2["replay_structural_rejection_pressure"] = False
    assert rj11.validate_c11_rejection_record(bad2)["valid"] is False


# ---- evidence trail --------------------------------------------------------

def test_pushed_evidence_chain_cites_four_gates_with_commits():
    chain = _R["pushed_evidence_chain"]
    stages = {e["stage"]: e for e in chain}
    for required, commit in (
            ("candidate_spec", "748414f57eafc7dff543b7bbc5294e39fc074089"),
            ("detector_spec_and_synthetic_dry_run",
             "6e1efd2bb6082aef038b6d0de5578e0f0bdd4519"),
            ("real_candle_labels_review",
             "8e69956ba10ea1c5dd80c2860b71142e2e9f512a"),
            ("fee_slippage_honest_replay_review",
             "cf39a55392e50582b3ee2ea84b7d043459ca3afd")):
        assert required in stages, required
        assert stages[required]["commit"] == commit, required
        assert len(stages[required]["commit"]) == 40
    assert _R["head_at_replay_review"] == (
        "cf39a55392e50582b3ee2ea84b7d043459ca3afd")


def test_originating_proposal_stage_marked_not_pushed():
    fp = _R["family_proposal_stage"]
    assert fp["stage"] == "family_proposal"
    assert fp["pushed_separately_on_origin"] is False
    assert len(fp["earliest_pushed_ancestor_commit"]) == 40
    bad = copy.deepcopy(_R)
    bad["family_proposal_stage"]["pushed_separately_on_origin"] = True
    assert rj11.validate_c11_rejection_record(bad)["valid"] is False


def test_evidence_headline_records_the_failure():
    eh = _R["evidence_headline"]
    assert eh["accepted_labels"] == 742
    assert eh["labels_battery_passed"] is True
    assert eh["forward_oos_2026_positive_any_variant"] is False
    assert eh["regime_symmetry_passed"] is False
    assert eh["replay_forward_oos_2026_net_r_3r"] < 0
    assert eh["bear_regime_net_r_3r"] < 0
    bad = copy.deepcopy(_R)
    bad["evidence_headline"]["regime_symmetry_passed"] = True
    assert rj11.validate_c11_rejection_record(bad)["valid"] is False


def test_rejection_reasons_and_kept_on_record_lesson():
    reasons = " || ".join(_R["rejection_reasons"]).lower()
    assert "forward-oos" in reasons
    assert "bear" in reasons
    assert "horizon" in reasons
    lesson = " || ".join(_R["kept_on_record_as"]).lower()
    assert "necessary but not sufficient" in lesson
    assert "forward-oos" in lesson


# ---- locks + capability flags + claim locks --------------------------------

def test_all_gates_locked():
    for gate in ("robustness_gate_locked", "relabel_gate_locked",
                 "paper_trading_gate_locked", "micro_live_gate_locked",
                 "live_gate_locked"):
        assert _R[gate] is True, gate
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_robustness_run", "no_optimization", "no_regime_filter",
                 "no_horizon_reselection", "no_asset_reselection",
                 "no_regime_reselection", "no_portfolio_compute"):
        assert _R["scope_locks"][must] is True, must


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in rj11._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = copy.deepcopy(_R)
        bad[flag] = True
        assert rj11.validate_c11_rejection_record(bad)["valid"] is False, flag


def test_claim_locks_and_label_no_readiness():
    for required in ("no_profitability_claim",
                     "kept_on_record_not_active_candidate",
                     "not_parked_as_active",
                     "no_relabel_of_original_result",
                     "no_optimization_or_horizon_asset_regime_reselection",
                     "no_regime_filter_attempt"):
        assert required in _R["claim_locks"], required
    label = rj11.get_candidate_11_rejection_record_label()
    assert "RESEARCH ONLY" in label
    assert "REJECTED_KEPT_ON_RECORD" in label
    assert "NOT AN ACTIVE CANDIDATE" in label
    for banned in ("APPROVED FOR PAPER", "APPROVED FOR LIVE", "PROFITABLE",
                   "EDGE CONFIRMED", "READY FOR LIVE"):
        assert banned not in label.upper(), banned


def test_next_action_is_closed_no_execution_token():
    nra = rj11.get_candidate_11_rejection_record_next_action()
    assert nra.startswith("NONE__C11_CLOSED")
    for banned in ("APPROVE", "PAPER", "LIVE", "EXECUTE", "BROKER", "ORDER",
                   "PROMOTE", "UNLOCK"):
        assert banned not in nra.upper(), banned


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(rj11.__file__, encoding="utf-8").read()
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
