"""Tests for the Candidate #14 family proposal contract
(conviction_bar_follow_through_v1).

Verifies: chain-gate on the closed C13 rejection record (REJECTED_KEPT_ON_RECORD);
verdict READY; materially-new family; full differentiation from every rejected
family C1-C13 (18 incl. C10/C11/C12/C13); the C10+C11+C12+C13 lessons applied; the
hard early-generalization + anti-drift battery present (incl. the NEW structural
labels sample-size gate before replay, must-beat-random-entry/buy-and-hold, and
the target-capture / horizon cap); single-bar conviction trigger (range outlier +
top-quartile close), not a squeeze-release/breakout/trend/reversion; proposal-only
posture; no calendar/weekday trigger; no long-drift/bull-carry reliance; all
execution + downstream gates locked; ~38 capability flags False; anti-tamper;
AST/purity green.

The shared chain is memoized once at import."""
from __future__ import annotations

import ast
import copy
import inspect
import subprocess
import sys

import sparta_commander.conviction_bar_follow_through_v1_family_proposal_contract as c14p  # noqa: E501


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
    _R = c14p.build_candidate_14_family_proposal(".", _tracked_paths())
finally:
    for _mod, _attr, _orig in _memo_restore:
        setattr(_mod, _attr, _orig)


# ---- chain gate + verdict --------------------------------------------------

def test_proposal_ready_and_validates():
    assert _R["verdict"] == c14p.VERDICT_C14P_READY
    assert _R["blockers"] == []
    assert _R["c13_rejection_status"] == "REJECTED_KEPT_ON_RECORD"
    assert c14p.validate_candidate_14_family_proposal(_R)["valid"] is True


def test_chain_gate_requires_c13_closed():
    assert _R["head_at_c13_rejection"] == (
        "2d287bb2d6feb31a35286e2080e821bac5419612")


def test_identity_number_14_new_family():
    assert _R["candidate_number"] == 14
    assert _R["candidate_family"] == "conviction_bar_follow_through"
    assert _R["candidate_id"] == "CONVICTION_BAR_FOLLOW_THROUGH_V1"
    assert _R["is_materially_new_family"] is True
    assert _R["candidate_family"] not in _R["rejected_families_c1_to_c13"]


# ---- differentiation from EVERY rejected family C1-C13 ---------------------

def test_rejected_ledger_includes_c10_c11_c12_c13():
    led = _R["rejected_families_c1_to_c13"]
    for fam in ("intraweek_calendar_seasonality_drift",       # C10
                "cross_asset_dispersion_reversion",           # C11
                "failed_breakdown_reclaim_reversal",          # C12
                "lead_lag_propagation_continuation"):         # C13
        assert fam in led, fam
    assert len(led) == 18


def test_differentiation_present_for_every_rejected_family():
    diff = _R["material_difference_from_each_rejected"]
    for f in _R["rejected_families_c1_to_c13"]:
        assert diff.get(f), f
        assert len(diff[f]) > 20, f
    # tamper: drop the C-vol differentiation (closest cousin) -> invalid
    bad = copy.deepcopy(_R)
    bad["material_difference_from_each_rejected"].pop(
        "volatility_compression_expansion")
    assert c14p.validate_candidate_14_family_proposal(bad)["valid"] is False


# ---- C10-C13 lessons + the hard anti-drift battery -------------------------

def test_lessons_applied():
    joined = " || ".join(_R["c10_c11_c12_c13_lessons_applied"]).lower()
    assert "necessary but not sufficient" in joined
    assert "random-entry" in joined or "random entry" in joined
    assert "structural rejection at the labels stage" in joined


def test_hard_early_generalization_and_anti_drift_checks():
    checks = _R["early_generalization_checks"]
    for required in (
            "structural_labels_sample_size_gate_before_replay_required_early",
            "forward_oos_continuation_required_early",
            "cross_regime_bull_bear_chop_symmetry_required_early",
            "cross_asset_multiple_assets_required_early",
            "beats_buy_and_hold_and_random_entry_baseline_required_early",
            "target_capture_dominates_horizon_exit_share_capped_required_early"):
        assert required in checks, required
    assert _R["hard_rule_early_generalization_and_anti_drift"]
    # tamper: drop the structural labels sample-size gate -> invalid
    bad = copy.deepcopy(_R)
    bad["early_generalization_checks"] = [
        c for c in checks
        if c != "structural_labels_sample_size_gate_before_replay_required_early"]
    assert c14p.validate_candidate_14_family_proposal(bad)["valid"] is False


def test_anti_trap_filters_cover_random_drift_rare_forward_oos():
    joined = " || ".join(_R["anti_trap_filters"]).lower()
    assert "random-entry" in joined
    assert "buy-and-hold" in joined or "carry" in joined
    assert "horizon" in joined
    assert "forward-oos" in joined
    assert "too rare" in joined or "sample-size" in joined


# ---- entry: conviction-bar event, not calendar/single-asset/carry ----------

def test_entry_is_conviction_bar_not_calendar_not_carry():
    entry = _R["entry_concept"].lower()
    assert "true_range" in entry and "atr" in entry
    assert "top quartile" in entry or "0.75" in entry
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
    for flag in c14p._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = copy.deepcopy(_R)
        bad[flag] = True
        assert c14p.validate_candidate_14_family_proposal(bad)["valid"] is False, flag


def test_next_action_is_human_decision_proposal_only():
    nra = c14p.get_candidate_14_family_proposal_next_action()
    assert nra == "HUMAN_DECISION_C14_ADVANCE_TO_SPEC_OR_REJECT_PROPOSAL"
    label = c14p.get_candidate_14_family_proposal_label()
    assert "PROPOSAL ONLY" in label
    assert "RESEARCH ONLY" in label
    for banned in ("APPROVED FOR PAPER", "APPROVED FOR LIVE", "PROFITABLE",
                   "EDGE CONFIRMED", "READY FOR LIVE"):
        assert banned not in label.upper(), banned


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(c14p.__file__, encoding="utf-8").read()
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
