"""Tests for the Candidate #11 candidate spec contract
(cross_asset_dispersion_reversion_v1).

Verifies: chain-gate on the READY C11 family proposal; verdict
CANDIDATE_11_SPEC_READY; all ten spec sections pinned (symbol universe,
timeframe, entry, stop/risk, targets, cost model, sample size, invalidation,
anti-overfit/generalization, next gate); the C10 lesson is enforced (early
generalization battery is MANDATORY before robustness/promotion; no
calendar/weekday trigger; no single-asset trap; regime-symmetry required);
materially different from C1-C10; spec-only posture with all execution gates
locked; no paper/live readiness claim; AST/purity green.

The shared chain is memoized once at import."""
from __future__ import annotations

import ast
import copy
import inspect
import subprocess
import sys

import sparta_commander.cross_asset_dispersion_reversion_v1_candidate_spec_contract as c11s  # noqa: E501


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
    _R = c11s.build_candidate_11_spec(".", _tracked_paths())
finally:
    for _mod, _attr, _orig in _memo_restore:
        setattr(_mod, _attr, _orig)


# ---- chain gate + verdict --------------------------------------------------

def test_spec_ready_and_validates():
    assert _R["verdict"] == c11s.VERDICT_C11S_READY
    assert _R["blockers"] == []
    assert _R["proposal_verdict"] == c11s.VERDICT_C11P_READY
    assert c11s.validate_candidate_11_spec(_R)["valid"] is True


def test_identity_and_materially_new():
    assert _R["candidate_number"] == 11
    assert _R["candidate_family"] == "cross_asset_dispersion_reversion"
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_materially_new_family"] is True
    assert _R["candidate_family"] not in _R["rejected_families_c1_to_c10"]


# ---- 1. symbol universe (cross-asset; not single-asset) --------------------

def test_symbol_universe_cross_asset():
    assert set(_R["symbol_universe"]) == {"BTCUSD", "ETHUSD", "SOLUSD"}
    assert len(_R["symbol_universe"]) >= 3
    assert _R["market_type"] == "spot"
    assert _R["direction"] == "long_only"
    assert _R["is_single_asset"] is False
    bad = copy.deepcopy(_R)
    bad["symbol_universe"] = ["BTCUSD"]
    assert c11s.validate_candidate_11_spec(bad)["valid"] is False


# ---- 2. timeframe ----------------------------------------------------------

def test_timeframe_daily():
    assert _R["timeframe"] == "1d"


# ---- 3. entry concept (relative, not calendar/weekday/single-asset) --------

def test_entry_concept_relative_not_calendar():
    ec = _R["entry_concept"]
    assert ec["trigger"] == (
        "cross_sectional_dispersion_reversion_of_the_relative_laggard")
    assert ec["weekday_or_calendar_trigger"] is False
    assert ec["single_asset_or_single_weekday"] is False
    assert ec["z_score_entry_threshold"] == -1.0
    assert "regime_filter" in ec
    bad = copy.deepcopy(_R)
    bad["entry_concept"]["weekday_or_calendar_trigger"] = True
    assert c11s.validate_candidate_11_spec(bad)["valid"] is False


# ---- 4-5. stop geometry + targets ------------------------------------------

def test_stop_geometry_and_targets():
    rg = _R["risk_geometry"]
    assert rg["atr_length"] == 14
    assert "1.5" in rg["structure_stop"]
    assert "no leverage" in rg["sizing"].lower() or "no shorting" in rg["sizing"].lower()
    tp = _R["target_policy"]
    assert tuple(tp["variants"]) == ("2r", "3r", "4r")
    assert tp["no_new_variants_after_label_freeze"] is True
    assert _R["target_distance_floor_bps"] == 81.0


# ---- 6. cost model ---------------------------------------------------------

def test_cost_model_fee_plus_slippage():
    cm = _R["cost_model"]
    assert cm["fee_round_trip_bps"] == 27.0
    assert cm["slippage_round_trip_bps"] == 10.0
    assert cm["all_in_round_trip_bps"] == 37.0
    bad = copy.deepcopy(_R)
    bad["cost_model"]["all_in_round_trip_bps"] = 0.0
    assert c11s.validate_candidate_11_spec(bad)["valid"] is False


# ---- 7. sample-size (cross-asset + cross-regime coverage) ------------------

def test_sample_size_cross_asset_cross_regime():
    ss = _R["sample_size_requirements"]
    assert ss["min_accepted_total"] >= 100
    assert ss["min_accepted_per_asset"] >= 1
    assert ss["min_accepted_per_regime"] >= 1
    assert ss["below_minimum_is_structural_rejection"] is True
    bad = copy.deepcopy(_R)
    bad["sample_size_requirements"]["min_accepted_per_regime"] = 0
    assert c11s.validate_candidate_11_spec(bad)["valid"] is False


# ---- 8. invalidation / rejection rules -------------------------------------

def test_invalidation_rules_cover_traps():
    joined = " || ".join(_R["invalidation_rejection_rules"]).lower()
    assert "long-drift" in joined
    assert "weekday" in joined
    assert "forward-oos" in joined
    assert "81 bps" in joined or "floor" in joined


# ---- 9. anti-overfit / generalization (the C10 lesson) ---------------------

def test_early_generalization_battery_mandatory_before_promotion():
    aog = _R["anti_overfit_generalization_rules"]
    assert aog["battery_runs_before_robustness_and_before_promotion"] is True
    assert aog["failing_any_battery_check_is_structural_rejection"] is True
    assert aog["no_weekday_or_calendar_trigger"] is True
    assert aog["regime_symmetry_required_not_long_drift"] is True
    for chk in ("cross_weekday_neutrality_required_early",
                "cross_asset_multiple_laggards_required_early",
                "forward_oos_continuation_required_early",
                "cross_regime_bull_bear_chop_stability_required_early"):
        assert chk in _R["early_generalization_battery"], chk
    bad = copy.deepcopy(_R)
    bad["early_generalization_battery"] = [
        c for c in bad["early_generalization_battery"]
        if c != "forward_oos_continuation_required_early"]
    assert c11s.validate_candidate_11_spec(bad)["valid"] is False
    bad2 = copy.deepcopy(_R)
    bad2["anti_overfit_generalization_rules"][
        "battery_runs_before_robustness_and_before_promotion"] = False
    assert c11s.validate_candidate_11_spec(bad2)["valid"] is False


# ---- 10. next gate ---------------------------------------------------------

def test_next_gate_after_spec():
    assert _R["next_required_action"] == (
        "HUMAN_DECISION_C11_ADVANCE_TO_DETECTOR_SPEC_OR_REJECT")
    assert _R["next_gate_after_spec"]["action"] == _R["next_required_action"]


# ---- spec-only posture + locks ---------------------------------------------

def test_spec_only_all_execution_gates_locked():
    assert _R["is_spec_only"] is True
    for lock in ("no_detector", "no_labels", "no_replay", "no_data_fetch",
                 "no_paper_trading", "no_live_trading", "no_portfolio_compute",
                 "no_calendar_trigger", "no_weekday_trigger",
                 "no_parameter_fitting", "no_paper_live_readiness_claim"):
        assert _R["scope_locks"][lock] is True
    for gate in ("detector_gate_locked", "labels_gate_locked",
                 "replay_gate_locked", "data_fetch_gate_locked",
                 "paper_trading_gate_locked", "live_gate_locked"):
        assert _R[gate] is True, gate


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in c11s._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = copy.deepcopy(_R)
        bad[flag] = True
        assert c11s.validate_candidate_11_spec(bad)["valid"] is False, flag


def test_label_no_readiness_claim():
    label = c11s.get_candidate_11_spec_label()
    assert "SPEC ONLY" in label
    assert "MATERIALLY DIFFERENT FROM C1-C10" in label
    assert "EARLY GENERALIZATION" in label
    for banned in ("APPROVED FOR PAPER", "APPROVED FOR LIVE", "PROFITABLE",
                   "EDGE CONFIRMED", "GUARANTEE", "READY FOR LIVE"):
        assert banned not in label.upper(), banned


# ---- chain blocks when proposal not ready ----------------------------------

def test_chain_blocks_when_proposal_not_ready(monkeypatch):
    monkeypatch.setattr(
        c11s, "build_candidate_11_family_proposal",
        lambda repo_root, tracked: {"verdict": "SOMETHING_ELSE"})
    blocked = c11s.build_candidate_11_spec(".", [])
    assert blocked["verdict"] == c11s.VERDICT_C11S_BLOCKED
    assert "proposal_not_ready" in blocked["blockers"]


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(c11s.__file__, encoding="utf-8").read()
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
