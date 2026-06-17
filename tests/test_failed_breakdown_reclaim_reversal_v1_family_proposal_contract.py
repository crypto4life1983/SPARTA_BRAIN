"""Tests for the Candidate #12 family proposal contract
(failed_breakdown_reclaim_reversal_v1).

Verifies: chain-gate on the closed C11 rejection record (REJECTED_KEPT_ON_RECORD);
verdict READY; materially-new family; full differentiation from every rejected
family C1-C11 (incl. the C11 cross_asset_dispersion_reversion entry); the C10+C11
lessons applied; the hard early-generalization + anti-drift battery present (incl.
the NEW must-beat-buy-and-hold/random-entry gate and the target-capture-dominance
/ horizon-exit-share cap); proposal-only posture; no calendar/weekday trigger; no
long-drift/bull-carry reliance; all execution + downstream gates locked; ~40
capability flags False; anti-tamper; AST/purity green.

The shared chain is memoized once at import."""
from __future__ import annotations

import ast
import copy
import inspect
import subprocess
import sys

import sparta_commander.failed_breakdown_reclaim_reversal_v1_family_proposal_contract as c12p  # noqa: E501


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
    _R = c12p.build_candidate_12_family_proposal(".", _tracked_paths())
finally:
    for _mod, _attr, _orig in _memo_restore:
        setattr(_mod, _attr, _orig)


# ---- chain gate + verdict --------------------------------------------------

def test_proposal_ready_and_validates():
    assert _R["verdict"] == c12p.VERDICT_C12P_READY
    assert _R["blockers"] == []
    assert _R["c11_rejection_status"] == "REJECTED_KEPT_ON_RECORD"
    assert c12p.validate_candidate_12_family_proposal(_R)["valid"] is True


def test_chain_gate_requires_c11_closed():
    assert _R["head_at_c11_rejection"] == (
        "0fa49663de9307d90bd2f6b60456811fc78097d9")


def test_identity_number_12_new_family():
    assert _R["candidate_number"] == 12
    assert _R["candidate_family"] == "failed_breakdown_reclaim_reversal"
    assert _R["candidate_id"] == "FAILED_BREAKDOWN_RECLAIM_REVERSAL_V1"
    assert _R["is_materially_new_family"] is True
    assert _R["candidate_family"] not in _R["rejected_families_c1_to_c11"]


# ---- differentiation from EVERY rejected family C1-C11 ---------------------

def test_rejected_ledger_includes_c10_and_c11():
    led = _R["rejected_families_c1_to_c11"]
    assert "intraweek_calendar_seasonality_drift" in led      # C10
    assert "cross_asset_dispersion_reversion" in led          # C11
    assert len(led) == 16


def test_differentiation_present_for_every_rejected_family():
    diff = _R["material_difference_from_each_rejected"]
    for f in _R["rejected_families_c1_to_c11"]:
        assert diff.get(f), f
        assert len(diff[f]) > 20, f
    # tamper: drop the C11 differentiation -> invalid
    bad = copy.deepcopy(_R)
    bad["material_difference_from_each_rejected"].pop(
        "cross_asset_dispersion_reversion")
    assert c12p.validate_candidate_12_family_proposal(bad)["valid"] is False


# ---- C10 + C11 lessons + the hard anti-drift battery -----------------------

def test_c10_c11_lessons_applied():
    joined = " || ".join(_R["c10_c11_lessons_applied"]).lower()
    assert "necessary but not sufficient" in joined
    assert "forward-oos" in joined
    assert "buy-and-hold" in joined or "buy and hold" in joined


def test_hard_early_generalization_and_anti_drift_checks():
    checks = _R["early_generalization_checks"]
    for required in (
            "forward_oos_continuation_required_early",
            "cross_regime_bull_bear_chop_symmetry_required_early",
            "cross_asset_multiple_assets_required_early",
            "beats_buy_and_hold_and_random_entry_baseline_required_early",
            "target_capture_dominates_horizon_exit_share_capped_required_early"):
        assert required in checks, required
    assert _R["hard_rule_early_generalization_and_anti_drift"]
    # tamper: drop the must-beat-buy-and-hold gate -> invalid
    bad = copy.deepcopy(_R)
    bad["early_generalization_checks"] = [
        c for c in checks
        if c != "beats_buy_and_hold_and_random_entry_baseline_required_early"]
    assert c12p.validate_candidate_12_family_proposal(bad)["valid"] is False


def test_anti_trap_filters_cover_drift_and_forward_oos():
    joined = " || ".join(_R["anti_trap_filters"]).lower()
    assert "buy-and-hold" in joined or "carry" in joined
    assert "horizon" in joined
    assert "forward-oos" in joined


# ---- entry/exit/risk/data --------------------------------------------------

def test_entry_is_reclaim_event_not_calendar_not_single_asset_carry():
    entry = _R["entry_concept"].lower()
    assert "reclaim" in entry or "closes back above" in entry
    assert "weekday" not in entry or "no date" in entry
    assert _R["uses_weekday_or_calendar_trigger"] is False
    assert _R["is_single_asset_edge"] is False
    assert _R["relies_on_long_drift_or_bull_carry"] is False


def test_exit_horizon_is_human_fixed_not_optimized():
    exit_c = _R["exit_concept"].lower()
    assert "horizon" in exit_c
    assert "not optimized" in exit_c or "never" in exit_c


def test_data_needs_no_fetch_required():
    dn = _R["data_needs"]
    assert dn["new_fetch_needed_for_initial_research"] is False
    assert dn["timeframe"] == "1d" and dn["market_type"] == "spot"
    for s in ("BTC", "ETH", "SOL"):
        assert s in dn["assets_required_minimum"]


# ---- locks + capability flags ----------------------------------------------

def test_all_gates_locked():
    for gate in ("detector_gate_locked", "labels_gate_locked",
                 "replay_gate_locked", "paper_trading_gate_locked",
                 "live_gate_locked", "human_review_required"):
        assert _R[gate] is True, gate
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_calendar_trigger", "no_weekday_trigger",
                 "no_long_drift_or_bull_carry_reliance", "no_portfolio_compute",
                 "no_data_fetch"):
        assert _R["scope_locks"][must] is True, must


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in c12p._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = copy.deepcopy(_R)
        bad[flag] = True
        assert c12p.validate_candidate_12_family_proposal(bad)["valid"] is False, flag


def test_next_action_is_human_decision_proposal_only():
    nra = c12p.get_candidate_12_family_proposal_next_action()
    assert nra == "HUMAN_DECISION_C12_ADVANCE_TO_SPEC_OR_REJECT_PROPOSAL"
    label = c12p.get_candidate_12_family_proposal_label()
    assert "PROPOSAL ONLY" in label
    assert "RESEARCH ONLY" in label
    for banned in ("APPROVED FOR PAPER", "APPROVED FOR LIVE", "PROFITABLE",
                   "EDGE CONFIRMED", "READY FOR LIVE"):
        assert banned not in label.upper(), banned


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(c12p.__file__, encoding="utf-8").read()
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
