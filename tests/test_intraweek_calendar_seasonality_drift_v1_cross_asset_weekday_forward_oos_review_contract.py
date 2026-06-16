"""Tests for the Candidate #10 cross-asset / cross-weekday / forward-OOS
generalization review / evidence-freeze contract.

Verifies: chain-gate on the pushed FROZEN robustness review; frozen SHA pins of
the 3 sources + the untracked generalization artifact; self-validation (156
BTC-Friday OOS); the honest finding that the Friday edge DOES NOT GENERALIZE
(general long-drift, 6/7 weekdays positive; weak ETH/SOL; forward-OOS negative
on all 3 assets); original frozen C10 result unchanged; promotion barred; all
gates locked; AST/purity green.

The shared C10 build chain is memoized once at import."""
from __future__ import annotations

import ast
import copy
import inspect
import subprocess
import sys

import sparta_commander.intraweek_calendar_seasonality_drift_v1_cross_asset_weekday_forward_oos_review_contract as c10gen  # noqa: E501


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
    _R = c10gen.build_c10_generalization_review(".", _tracked_paths())
finally:
    for _mod, _attr, _orig in _memo_restore:
        setattr(_mod, _attr, _orig)


# ---- chain gate + verdict --------------------------------------------------

def test_review_does_not_generalize_and_validates():
    assert _R["verdict"] == c10gen.VERDICT_C10GEN_DOES_NOT_GENERALIZE
    assert _R["blockers"] == []
    assert _R["robustness_review_verdict"] == c10gen.VERDICT_C10ROB_FROZEN
    assert c10gen.validate_c10_generalization_review(_R)["valid"] is True


def test_verdict_in_allowed_set():
    for v in ("C10_GENERALIZATION_FROZEN_FOR_HUMAN_REVIEW",
              "C10_GENERALIZES_WEAK_OR_STRONG", "C10_DOES_NOT_GENERALIZE",
              "C10_GENERALIZATION_INCONCLUSIVE"):
        assert hasattr(c10gen, "VERDICT_C10GEN_" + {
            "C10_GENERALIZATION_FROZEN_FOR_HUMAN_REVIEW": "FROZEN",
            "C10_GENERALIZES_WEAK_OR_STRONG": "GENERALIZES",
            "C10_DOES_NOT_GENERALIZE": "DOES_NOT_GENERALIZE",
            "C10_GENERALIZATION_INCONCLUSIVE": "INCONCLUSIVE"}[v])
    assert _R["verdict"] in (
        c10gen.VERDICT_C10GEN_FROZEN, c10gen.VERDICT_C10GEN_GENERALIZES,
        c10gen.VERDICT_C10GEN_DOES_NOT_GENERALIZE,
        c10gen.VERDICT_C10GEN_INCONCLUSIVE)


def test_sha_pins_frozen():
    assert _R["expected_generalization_sha256"] == (
        c10gen.EXPECTED_GENERALIZATION_SHA256)
    for k in ("BTC", "ETH", "SOL"):
        assert _R["expected_source_sha256"][k] == (
            c10gen.EXPECTED_SOURCE_SHA256[k])
    assert _R["head_at_robustness_review"] == (
        "85e2cd6a4b49ec6e07f74ee920caab23516a14ca")
    bad = copy.deepcopy(_R)
    bad["expected_generalization_sha256"] = "0" * 64
    assert c10gen.validate_c10_generalization_review(bad)["valid"] is False


# ---- self-validation -------------------------------------------------------

def test_self_validation_reproduces_156_btc_friday():
    assert _R["self_validation_passed"] is True
    assert _R["self_validation_btc_friday_oos_accepted"] == 156
    bad = copy.deepcopy(_R)
    bad["self_validation_btc_friday_oos_accepted"] = 200
    assert c10gen.validate_c10_generalization_review(bad)["valid"] is False


# ---- 1. cross-asset --------------------------------------------------------

def test_cross_asset_eth_sol_weak_positive_but_decaying():
    ca = _R["cross_asset_friday_oos_net_r"]
    # BTC reference matches the frozen replay headline
    assert ca["BTC_reference"]["3r"] == 22.48
    # ETH/SOL net-positive on every variant but far weaker than BTC
    for asset in ("ETH", "SOL"):
        assert ca[asset]["all_variants_positive"] is True
        assert ca[asset]["3r"] < ca["BTC_reference"]["3r"]
        assert ca[asset]["net_2025_negative"] is True
    assert _R["cross_asset_independent_confirmation"] is False


# ---- 2. cross-weekday: NOT friday-specific ---------------------------------

def test_cross_weekday_friday_not_unique_general_drift():
    cw3 = _R["cross_weekday_btc_oos_net_3r"]
    # Friday is the strongest...
    assert cw3["5_fri"] == max(cw3.values())
    # ...but most weekdays are positive (general drift, not friday-specific)
    positive = sum(1 for v in cw3.values() if v > 0)
    assert positive >= 6
    cw = _R["cross_weekday_summary"]
    assert cw["friday_is_unique_positive_weekday"] is False
    assert cw["positive_weekdays_count_3r"] == 6
    assert _R["friday_specificity_holds"] is False
    assert _R["friday_is_general_long_drift"] is True
    bad = copy.deepcopy(_R)
    bad["cross_weekday_summary"]["friday_is_unique_positive_weekday"] = True
    assert c10gen.validate_c10_generalization_review(bad)["valid"] is False


# ---- 3. forward-OOS negative on all assets ---------------------------------

def test_forward_oos_negative_all_assets():
    fwd = _R["forward_oos_friday_2026_net_r"]
    for asset in ("BTC", "ETH", "SOL"):
        assert fwd[asset]["all_variants_positive"] is False
        assert fwd[asset]["3r"] < 0
    assert _R["forward_oos_positive_any_asset"] is False
    bad = copy.deepcopy(_R)
    bad["forward_oos_friday_2026_net_r"]["BTC"]["all_variants_positive"] = True
    assert c10gen.validate_c10_generalization_review(bad)["valid"] is False


# ---- disposition + original-result protection ------------------------------

def test_disposition_reject_or_park_and_promotion_barred():
    assert _R["recommended_disposition"].startswith("REJECT_OR_PARK")
    assert _R["promotion_to_paper_or_live_barred"] is True
    assert _R["next_required_action"] == "HUMAN_DECISION_C10_REJECT_OR_PARK"
    bad = copy.deepcopy(_R)
    bad["promotion_to_paper_or_live_barred"] = False
    assert c10gen.validate_c10_generalization_review(bad)["valid"] is False


def test_original_frozen_result_unchanged_no_relabel():
    assert _R["original_frozen_c10_result_unchanged"] is True
    assert _R["relabels_original_result"] is False
    assert _R["reselects_weekday"] is False
    assert _R["fits_parameters"] is False
    assert _R["optimizes"] is False
    assert _R["selects_best_cell_as_promotion"] is False
    for lock in ("no_relabel", "no_weekday_reselection", "no_parameter_fitting",
                 "no_optimization", "no_best_cell_selected_as_promotion"):
        assert _R["scope_locks"][lock] is True


# ---- locks + capability flags ----------------------------------------------

def test_all_downstream_gates_locked():
    assert _R["is_generalization_review_only"] is True
    assert _R["current_loop_stage"] == "cross_asset_weekday_forward_oos_review"
    for key in ("relabel_gate_locked", "paper_trading_gate_locked",
                "micro_live_gate_locked", "live_gate_locked",
                "human_review_required"):
        assert _R[key] is True, key
    for key, val in _R["scope_locks"].items():
        assert val is True, key


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in c10gen._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = copy.deepcopy(_R)
        bad[flag] = True
        assert c10gen.validate_c10_generalization_review(bad)["valid"] is False, flag


def test_claim_locks_and_label():
    for required in ("no_profitability_claim", "no_relabel_of_original_result",
                     "friday_specificity_failed_disclosed",
                     "forward_oos_negative_disclosed",
                     "promotion_to_paper_or_live_barred"):
        assert required in _R["claim_locks"], required
    label = c10gen.get_candidate_10_generalization_review_label()
    assert "RESEARCH ONLY" in label
    assert "DOES NOT GENERALIZE" in label
    assert "NOT A PROFITABILITY CLAIM" in label
    for banned in ("APPROVED FOR PAPER", "APPROVED FOR LIVE", "EDGE CONFIRMED",
                   "PROFITABLE", "GUARANTEE"):
        assert banned not in label.upper(), banned


def test_honest_caveats_present():
    joined = " || ".join(_R["honest_caveats"]).lower()
    assert "general bullish long-drift" in joined or "general long-drift" in joined
    assert "forward-oos" in joined and "negative" in joined
    assert "self-validation passed" in joined
    assert "not changed or relabeled" in joined


# ---- artifact untracked ----------------------------------------------------

def test_generalization_artifact_remains_untracked():
    tracked = _tracked_paths()
    assert c10gen.GENERALIZATION_PATH not in tracked
    for p in tracked:
        assert not p.startswith(
            "data/intraweek_calendar_seasonality_c10/"
            "cross_asset_weekday_forward_oos/"), p


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(c10gen.__file__, encoding="utf-8").read()
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
