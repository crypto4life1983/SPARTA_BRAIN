"""Tests for the Candidate #11 family proposal contract
(cross_asset_dispersion_reversion_v1).

Verifies: chain-gate on the closed C10 rejection record (REJECTED_KEPT_ON_RECORD);
verdict CANDIDATE_11_FAMILY_PROPOSAL_READY; the proposed family is materially NEW
(not in the C1-C10 rejected ledger) and differentiates from EVERY rejected
family; the C10 lesson is applied; the HARD early-generalization rule + the four
early-generalization checks are present; proposal-only posture (no detector /
labels / replay / data fetch / trading / portfolio compute); all execution +
downstream gates locked; AST/purity green.

The shared C10 build chain is memoized once at import."""
from __future__ import annotations

import ast
import copy
import inspect
import subprocess
import sys

import sparta_commander.cross_asset_dispersion_reversion_v1_family_proposal_contract as c11p  # noqa: E501


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
    _R = c11p.build_candidate_11_family_proposal(".", _tracked_paths())
finally:
    for _mod, _attr, _orig in _memo_restore:
        setattr(_mod, _attr, _orig)


# ---- chain gate + verdict --------------------------------------------------

def test_proposal_ready_and_validates():
    assert _R["verdict"] == c11p.VERDICT_C11P_READY
    assert _R["blockers"] == []
    assert _R["c10_rejection_status"] == "REJECTED_KEPT_ON_RECORD"
    assert c11p.validate_candidate_11_family_proposal(_R)["valid"] is True


def test_candidate_identity():
    assert _R["candidate_number"] == 11
    assert _R["candidate_family"] == "cross_asset_dispersion_reversion"
    assert _R["mode"] == "RESEARCH_ONLY"


# ---- materially new + differentiation from all C1-C10 ----------------------

def test_proposed_family_is_not_a_rejected_family():
    assert _R["candidate_family"] not in _R["rejected_families_c1_to_c10"]
    assert _R["is_materially_new_family"] is True


def test_differentiates_from_every_rejected_family():
    rejected = _R["rejected_families_c1_to_c10"]
    diff = _R["material_difference_from_each_rejected"]
    assert len(rejected) >= 15
    for f in rejected:
        assert diff.get(f), f
    # C10 specifically is addressed
    assert "intraweek_calendar_seasonality_drift" in rejected
    assert diff["intraweek_calendar_seasonality_drift"]
    bad = copy.deepcopy(_R)
    del bad["material_difference_from_each_rejected"][
        "intraweek_calendar_seasonality_drift"]
    assert c11p.validate_candidate_11_family_proposal(bad)["valid"] is False


def test_relative_not_long_drift_edge():
    # opposite of the rejected relative-strength CONTINUATION families
    d = _R["material_difference_from_each_rejected"]
    assert "OPPOSITE" in d["eth_sol_relative_strength_pullback_continuation"]
    assert "laggard" in _R["clean_hypothesis"].lower()
    assert "not a directional bet" in _R["clean_hypothesis"].lower() or \
        "not undifferentiated long-drift" in _R["edge_source_hypothesis"].lower() \
        or "not" in _R["edge_source_hypothesis"].lower()


# ---- C10 lesson + hard early-generalization rule ---------------------------

def test_c10_lesson_applied():
    lesson = " || ".join(_R["c10_lesson_applied"]).lower()
    assert "long-drift" in lesson
    assert "generalization" in lesson
    assert "early" in lesson


def test_hard_early_generalization_rule_present():
    rule = _R["hard_rule_early_generalization"].lower()
    assert "early" in rule
    assert "before" in rule and ("robustness" in rule or "promotion" in rule)
    assert "structural rejection" in rule
    for chk in ("cross_weekday_neutrality_required_early",
                "cross_asset_multiple_laggards_required_early",
                "forward_oos_continuation_required_early",
                "cross_regime_bull_bear_chop_stability_required_early"):
        assert chk in _R["early_generalization_checks"], chk
    bad = copy.deepcopy(_R)
    bad["early_generalization_checks"] = [
        c for c in bad["early_generalization_checks"]
        if c != "forward_oos_continuation_required_early"]
    assert c11p.validate_candidate_11_family_proposal(bad)["valid"] is False


def test_anti_trap_filters_cover_c10_traps():
    joined = " || ".join(_R["anti_trap_filters"]).lower()
    assert "long-drift" in joined
    assert "single asset or a single weekday" in joined or "single-weekday" in joined
    assert "calendar" in joined
    assert "forward-oos" in joined


# ---- research plan content -------------------------------------------------

def test_data_needs_and_no_fetch_for_initial():
    dn = _R["data_needs"]
    assert dn["new_fetch_needed_for_initial_research"] is False
    assert dn["timeframe"] == "1d"
    assert dn["market_type"] == "spot"
    assert "BTC" in dn["assets_required_minimum"]
    assert len(dn["assets_required_minimum"]) >= 3


def test_entry_exit_and_risk_geometry_present():
    assert "laggard" in _R["entry_concept"].lower()
    assert "weekday is irrelevant" in _R["entry_concept"].lower()
    assert _R["exit_concept"]
    rg = _R["risk_geometry"]
    for key in ("stop", "targets", "costs", "sizing"):
        assert rg[key], key
    assert "no shorting" in rg["sizing"].lower() or "no leverage" in rg["sizing"].lower()


def test_symbols_cross_asset_long_only():
    assert set(_R["symbols"]) == {"BTCUSD", "ETHUSD", "SOLUSD"}
    assert _R["direction"] == "long_only"


# ---- proposal-only posture + locks -----------------------------------------

def test_proposal_only_no_detector_labels_replay():
    assert _R["is_proposal_only"] is True
    for lock in ("no_detector", "no_labels", "no_replay", "no_robustness_run",
                 "no_generalization_run", "no_data_fetch", "no_paper_trading",
                 "no_live_trading", "no_portfolio_compute", "no_calendar_trigger",
                 "no_weekday_trigger", "no_rescue_of_rejected_geometry"):
        assert _R["scope_locks"][lock] is True
    for gate in ("detector_gate_locked", "labels_gate_locked",
                 "replay_gate_locked", "paper_trading_gate_locked",
                 "live_gate_locked"):
        assert _R[gate] is True, gate


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in c11p._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = copy.deepcopy(_R)
        bad[flag] = True
        assert c11p.validate_candidate_11_family_proposal(bad)["valid"] is False, flag


def test_next_action_and_label():
    assert _R["next_required_action"] == (
        "HUMAN_DECISION_C11_ADVANCE_TO_SPEC_OR_REJECT_PROPOSAL")
    label = c11p.get_candidate_11_family_proposal_label()
    assert "PROPOSAL ONLY" in label
    assert "MATERIALLY DIFFERENT FROM C1-C10" in label
    assert "EARLY GENERALIZATION" in label
    for banned in ("APPROVED FOR PAPER", "APPROVED FOR LIVE", "PROFITABLE",
                   "EDGE CONFIRMED", "GUARANTEE"):
        assert banned not in label.upper(), banned


# ---- chain blocks when C10 not closed --------------------------------------

def test_chain_blocks_when_c10_not_closed(monkeypatch):
    monkeypatch.setattr(
        c11p, "build_c10_rejection_record",
        lambda repo_root, tracked: {"rejection_status": "NOT_CLOSED"})
    blocked = c11p.build_candidate_11_family_proposal(".", [])
    assert blocked["verdict"] == c11p.VERDICT_C11P_BLOCKED
    assert "c10_not_closed_on_record" in blocked["blockers"]


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(c11p.__file__, encoding="utf-8").read()
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
