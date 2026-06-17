"""Tests for the Candidate #11 fee-honest replay-results review contract
(cross_asset_dispersion_reversion_v1).

Verifies: chain-gate on the FROZEN C11 labels review; verdict FROZEN; SHA pins of
the labels + the two untracked replay artifacts + the 3 sources; the human-fixed
5-bar horizon disclosure (spec did NOT pre-declare it); the honest headline --
full-sample net positive after 37 bps costs BUT forward-OOS 2026 negative for
every variant, bear-regime negative, horizon-dominated -> structural rejection
pressure; the six pre-registered rejection warnings evaluated; anti-tamper
(negative findings cannot be flipped); all downstream gates locked; no
profitability / paper-live readiness claim; the artifacts remain untracked;
AST/purity green.

The shared chain is memoized once at import."""
from __future__ import annotations

import ast
import copy
import inspect
import subprocess
import sys

import sparta_commander.cross_asset_dispersion_reversion_v1_replay_results_review_contract as c11rr  # noqa: E501


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
    _R = c11rr.build_c11_replay_review(".", _tracked_paths())
finally:
    for _mod, _attr, _orig in _memo_restore:
        setattr(_mod, _attr, _orig)


# ---- chain gate + verdict --------------------------------------------------

def test_review_frozen_and_validates():
    assert _R["verdict"] == c11rr.VERDICT_C11RR_FROZEN
    assert _R["blockers"] == []
    assert _R["labels_review_verdict"] == c11rr.VERDICT_C11L_FROZEN
    assert c11rr.validate_c11_replay_review(_R)["valid"] is True


def test_sha_pins_frozen():
    assert _R["expected_labels_sha256"] == c11rr.EXPECTED_LABELS_SHA256
    assert _R["expected_replay_ledger_sha256"] == c11rr.EXPECTED_REPLAY_LEDGER_SHA256
    assert _R["expected_replay_summary_sha256"] == c11rr.EXPECTED_REPLAY_SUMMARY_SHA256
    for s in ("BTCUSD", "ETHUSD", "SOLUSD"):
        assert _R["expected_source_sha256"][s] == c11rr.EXPECTED_SOURCE_SHA256[s]
    assert _R["head_at_labels_review"] == (
        "8e69956ba10ea1c5dd80c2860b71142e2e9f512a")
    bad = copy.deepcopy(_R)
    bad["expected_replay_ledger_sha256"] = "0" * 64
    assert c11rr.validate_c11_replay_review(bad)["valid"] is False


# ---- cost basis + human-fixed horizon --------------------------------------

def test_cost_basis_intact():
    assert _R["all_in_round_trip_bps"] == 37.0
    assert _R["fee_round_trip_bps"] + _R["slippage_round_trip_bps"] == 37.0
    bad = copy.deepcopy(_R)
    bad["all_in_round_trip_bps"] = 5.0
    assert c11rr.validate_c11_replay_review(bad)["valid"] is False


def test_human_fixed_horizon_disclosed():
    assert _R["holding_horizon_bars"] == 5
    assert _R["spec_predeclared_horizon"] is False
    assert "human_fixed_horizon_disclosed" in _R["claim_locks"]
    bad = copy.deepcopy(_R)
    bad["spec_predeclared_horizon"] = True
    assert c11rr.validate_c11_replay_review(bad)["valid"] is False


# ---- the honest headline: forward-OOS fails -> structural rejection pressure -

def test_full_sample_positive_after_costs():
    for name in ("2r", "3r", "4r"):
        v = _R["replay_aggregates"][name]
        assert v["net_all_in_positive_full_sample"] is True
        assert v["net_r_total_all_in"] > 0
    assert _R["all_variants_net_positive_after_costs_full_sample"] is True
    assert _R["full_sample_sign_survives_costs"] is True


def test_forward_oos_negative_every_variant():
    assert _R["forward_oos_continuation_passed"] is False
    assert _R["any_variant_net_positive_forward_oos_2026"] is False
    for name in ("2r", "3r", "4r"):
        foos = _R["replay_aggregates"][name]["forward_oos_net_all_in"]
        assert foos["forward_oos"] < 0, name
    bad = copy.deepcopy(_R)
    bad["forward_oos_continuation_passed"] = True
    assert c11rr.validate_c11_replay_review(bad)["valid"] is False


def test_forward_oos_sign_cannot_be_flipped():
    bad = copy.deepcopy(_R)
    bad["replay_aggregates"]["3r"]["forward_oos_net_all_in"]["forward_oos"] = 5.0
    assert c11rr.validate_c11_replay_review(bad)["valid"] is False


def test_regime_asymmetry_and_structural_rejection_pressure():
    assert _R["regime_symmetry_passed"] is False
    assert _R["structural_rejection_pressure"] is True
    # bear-regime negative for 2R/3R.
    assert _R["replay_aggregates"]["2r"]["per_regime_net_all_in"]["bear"] < 0
    assert _R["replay_aggregates"]["3r"]["per_regime_net_all_in"]["bear"] < 0
    bad = copy.deepcopy(_R)
    bad["structural_rejection_pressure"] = False
    assert c11rr.validate_c11_replay_review(bad)["valid"] is False


def test_rejection_warnings_evaluated():
    rw = _R["rejection_warnings"]
    assert rw["negative_forward_oos_2026"] is True
    assert rw["explained_by_long_drift"] is True
    assert rw["negative_all_in_net_full_sample"] is False
    assert "negative_forward_oos_2026" in _R["rejection_warnings_triggered"]
    assert "explained_by_long_drift" in _R["rejection_warnings_triggered"]
    bad = copy.deepcopy(_R)
    bad["rejection_warnings"]["negative_forward_oos_2026"] = False
    assert c11rr.validate_c11_replay_review(bad)["valid"] is False


def test_horizon_dominated_and_thin_mean_disclosed():
    for name in ("2r", "3r", "4r"):
        assert _R["replay_aggregates"][name]["horizon_exit_share"] >= 0.6
    assert _R["disclosures"]["horizon_dominated_holding_drift"] is True
    assert _R["disclosures"]["btc_negative_all_variants"] is True


def test_per_variant_structure_and_worst_streak():
    for name in ("2r", "3r", "4r"):
        v = _R["replay_aggregates"][name]
        assert v["trade_count"] == v["kept_count"]
        assert v["worst_losing_streak"] == 15
        assert set(v["per_asset_net_all_in"]) == {"BTCUSD", "ETHUSD", "SOLUSD"}
        assert set(v["per_regime_net_all_in"]) == {"bull", "bear", "chop"}
        assert "2026" in v["per_year_net_all_in"]


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
    for flag in c11rr._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = copy.deepcopy(_R)
        bad[flag] = True
        assert c11rr.validate_c11_replay_review(bad)["valid"] is False, flag


def test_claim_locks_and_label_no_readiness():
    for required in ("no_profitability_claim",
                     "forward_oos_continuation_failed_disclosed",
                     "regime_asymmetry_disclosed",
                     "structural_rejection_pressure_disclosed",
                     "human_fixed_horizon_disclosed"):
        assert required in _R["claim_locks"], required
    label = c11rr.get_candidate_11_replay_review_label()
    assert "RESEARCH ONLY" in label
    assert "NOT A PROFITABILITY CLAIM" in label
    for banned in ("APPROVED FOR PAPER", "APPROVED FOR LIVE", "PROFITABLE",
                   "EDGE CONFIRMED", "GUARANTEE", "READY FOR LIVE"):
        assert banned not in label.upper(), banned


def test_next_action_is_human_decision_no_execution_token():
    nra = c11rr.get_candidate_11_replay_review_next_action()
    assert nra == "HUMAN_DECISION_C11_PROMOTE_TO_ROBUSTNESS_OR_REJECT"
    for banned in ("APPROVE", "PAPER", "LIVE", "EXECUTE", "BROKER", "ORDER",
                   "FETCH", "UNLOCK"):
        assert banned not in nra.upper(), banned


# ---- replay artifacts remain untracked -------------------------------------

def test_replay_artifacts_remain_untracked():
    tracked = _tracked_paths()
    assert c11rr.LEDGER_PATH not in tracked
    assert c11rr.SUMMARY_PATH not in tracked
    for p in tracked:
        assert not p.startswith(
            "data/cross_asset_dispersion_reversion_c11/"), p


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(c11rr.__file__, encoding="utf-8").read()
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
