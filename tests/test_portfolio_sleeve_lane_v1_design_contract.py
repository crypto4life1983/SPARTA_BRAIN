"""Tests for the SPARTA Portfolio Sleeve Lane v1 DESIGN contract.

Proves the design is PURE / DESIGN-ONLY / ADDITIVE: it declares two clearly-separated tracks
(Standalone -- must beat its benchmark, unchanged; Portfolio Sleeve -- need NOT beat BTC/SOL
standalone) and the seven rigour-preserving sleeve criteria; the pure classifier maps the
three initial targets to the right advisory buckets (carry null -> WATCHLIST, C15 ->
WATCHLIST_PENDING_MEASUREMENT, C13 -> HOLD_FOR_MORE_DATA) using ONLY declared committed
evidence; the correlation measurement is DECLARED-NOT-RUN with no fetch and no portfolio
compute; it changes no rule/gate/status, promotes/reclassifies nothing, leaves
C13/C15/C17/C20/C21 and the C22 replay lock untouched, and does not activate C23/C24; and
every capability flag is False."""
from __future__ import annotations

import ast
from pathlib import Path

import sparta_commander.portfolio_sleeve_lane_v1_design_contract as psl

_D = psl.build_portfolio_sleeve_lane_design()


# ---- builds + validates ----------------------------------------------------

def test_design_builds_and_validates():
    assert _D["mode"] == "RESEARCH_ONLY"
    assert _D["is_pure_design_only"] is True
    assert _D["is_additive"] is True
    assert _D["verdict"] == "PORTFOLIO_SLEEVE_LANE_V1_DESIGN_FROZEN_FOR_HUMAN_REVIEW"
    assert psl.validate_portfolio_sleeve_lane_design(_D)["valid"] is True


# ---- two clearly-separated tracks ------------------------------------------

def test_two_tracks_separated():
    st = _D["tracks"]["standalone_strategy_candidate"]
    sl = _D["tracks"]["portfolio_sleeve_candidate"]
    assert st["must_beat_benchmark"] is True
    assert st["this_lane_changes_it"] is False           # standalone gate UNCHANGED
    assert sl["must_beat_btc_sol_standalone"] is False   # sleeve need NOT beat BTC/SOL alone
    assert _D["sleeve_track_does_not_require_beating_btc_sol_standalone"] is True


# ---- all seven rigour-preserving criteria present --------------------------

def test_seven_sleeve_criteria():
    keys = {c["key"] for c in _D["sleeve_criteria"]}
    assert keys == {
        "positive_after_realistic_costs", "not_obviously_overfit", "not_outlier_dependent",
        "not_structurally_broken", "acceptable_or_positive_forward_oos_or_hold",
        "plausibly_diversifying_vs_btc_sol", "expected_portfolio_level_improvement"}


# ---- pure classifier: the three initial targets ----------------------------

def test_classifier_buckets_for_initial_targets():
    by = {t["target"]: t for t in _D["initial_targets"]}
    assert by["always_on_neutral_carry_null"]["classifier_bucket"] == "PORTFOLIO_SLEEVE_WATCHLIST"
    assert by["c15_time_series_momentum"]["classifier_bucket"] == (
        "PORTFOLIO_SLEEVE_WATCHLIST_PENDING_MEASUREMENT")
    assert by["c13_cross_asset_lead_lag"]["classifier_bucket"] == "HOLD_FOR_MORE_DATA"
    for t in _D["initial_targets"]:
        assert t["classifier_consistent"] is True


# ---- classifier discriminates: REJECT cases (C17-like, C20-like) -----------

def test_classifier_rejects_correlated_and_net_negative():
    # C17-like: high correlation + negative OOS -> REJECT (not diversifying)
    c17_like = psl.classify_sleeve_candidate({
        "positive_after_cost": True, "forward_oos_state": "NEGATIVE",
        "outlier_dependent": False, "overfit": False, "structurally_broken": False,
        "diversification": "HIGH_MEASURED", "sample_sufficient": True})
    assert c17_like["bucket"] == "REJECT"
    # C20-like: net-negative after cost -> REJECT
    c20_like = psl.classify_sleeve_candidate({
        "positive_after_cost": False, "forward_oos_state": "NEGATIVE",
        "outlier_dependent": False, "overfit": False, "structurally_broken": False,
        "diversification": "NEUTRAL_BY_CONSTRUCTION", "sample_sufficient": True})
    assert c20_like["bucket"] == "REJECT"
    # outlier-dependent (C18-like) -> REJECT
    c18_like = psl.classify_sleeve_candidate({
        "positive_after_cost": True, "forward_oos_state": "NEGATIVE",
        "outlier_dependent": True, "overfit": False, "structurally_broken": False,
        "diversification": "UNMEASURED", "sample_sufficient": True})
    assert c18_like["bucket"] == "REJECT"


def test_classifier_never_changes_status():
    for t in _D["initial_targets"]:
        out = psl.classify_sleeve_candidate(t["evidence"])
        assert out["is_official_status_change"] is False
        assert out["advisory_only"] is True


# ---- measurement declared, NOT run; no fetch; no portfolio compute ----------

def test_measurement_declared_not_run():
    cmp_ = _D["correlation_measurement_plan"]
    assert cmp_["status"] == "DECLARED_NOT_RUN"
    assert cmp_["no_data_fetch"] is True
    assert cmp_["requires_separate_human_token"] is True
    assert _D["measurement_run_here"] is False
    assert _D["portfolio_results_computed_here"] is False
    # C13 explicitly not computable yet (never replayed)
    assert "c13_cross_asset_lead_lag" in cmp_["not_computable_yet"]


# ---- preservation: changes no rule/gate/status; nothing promoted/reclassified

def test_preservation_guarantees():
    for k in ("changes_no_existing_rule", "changes_no_existing_gate",
              "changes_no_candidate_status", "promotes_nothing", "reclassifies_nothing",
              "c13_c15_c17_c20_c21_unchanged", "c22_replay_lock_untouched",
              "does_not_advance_c22", "does_not_activate_c23", "does_not_activate_c24",
              "watchlist_is_advisory_not_promotion"):
        assert _D[k] is True, k
    assert _D["next_human_gate"] == (
        "HUMAN_APPROVED_RUN_PORTFOLIO_SLEEVE_CORRELATION_MEASUREMENT_FROM_EXISTING_ARTIFACTS_ONLY")


# ---- capability flags + anti-tamper ----------------------------------------

def test_capabilities_false_and_tamper_rejected():
    for flag in psl._CAPABILITY_FLAGS_FALSE:
        assert _D[flag] is False, flag
        assert psl.validate_portfolio_sleeve_lane_design({**_D, flag: True})["valid"] is False
    for key, val in _D["scope_locks"].items():
        assert val is True, key
    # cannot flip the sleeve track to require beating BTC/SOL, nor run the measurement
    assert psl.validate_portfolio_sleeve_lane_design(
        {**_D, "measurement_run_here": True})["valid"] is False
    assert psl.validate_portfolio_sleeve_lane_design(
        {**_D, "changes_no_candidate_status": False})["valid"] is False


# ---- module purity ---------------------------------------------------------

def test_module_purity():
    src = Path(psl.__file__).read_text(encoding="utf-8")
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "open(",
                 "subprocess", "Popen", "urlopen", "requests.", "socket.connect",
                 "json.load", "read_text", "glob("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
              "subprocess", "websockets", "aiohttp", "schedule", "threading",
              "asyncio", "telegram", "os", "io", "shutil", "ssl", "ftplib",
              "json", "hashlib", "pathlib", "numpy", "pandas"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned), imported & banned
