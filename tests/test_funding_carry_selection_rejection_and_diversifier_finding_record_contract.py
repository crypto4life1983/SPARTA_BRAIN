"""Tests for the funding-carry selection rejection + diversifier finding record.

Proves the record is PURE / DECISION-RECORD-ONLY: a sleeve-lane REJECT of the cross-sectional
funding-carry SELECTION as a return engine (does not beat its always-on null; 2021-concentrated)
and a KEEP of the always-on broad funding carry as a (non-engine) USEFUL_DIVERSIFIER finding;
anchored to the pushed evidence commit; preserves the decisive facts (cannot be flipped);
discloses exploratory + survivorship + funding-cashflow-only caveats with no deployment/
return-engine/survivorship-free claim; keeps C22 at 3/20 HOLD, C23/C24 not reactivated, official
ledger/lifecycle/lane-status unchanged, activates/promotes nothing; pins every capability flag
False."""
from __future__ import annotations

import ast
from pathlib import Path

import sparta_commander.funding_carry_selection_rejection_and_diversifier_finding_record_contract as rj

_R = rj.build_funding_carry_decision_record()


def test_builds_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_decision_record_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"] == (
        "REJECT_FUNDING_CARRY_SELECTION_AS_RETURN_ENGINE__"
        "KEEP_ALWAYS_ON_BROAD_FUNDING_NULL_AS_DIVERSIFIER_FINDING")
    assert rj.validate_funding_carry_decision_record(_R)["valid"] is True


def test_anchored_to_evidence():
    assert _R["anchored_to_evidence_commit"] == "6939826b09c117d392f5791a9f5520a1f39090e3"


def test_selection_rejected():
    assert _R["selection_family"] == "cross_sectional_crypto_funding_carry_market_neutral"
    assert _R["selection_rejected_as_return_engine"] is True
    sm = _R["selection_metrics"]
    assert sm["net_74bps_cagr"] == 0.070 and sm["sharpe"] == 2.66
    assert sm["ex_2021_compounded"] < 0.05  # 2021-concentrated
    assert sm["net_74bps_cagr"] < _R["always_on_metrics"]["cagr"]  # loses to always-on null


def test_diversifier_kept_not_engine():
    assert _R["always_on_finding_family"] == "always_on_broad_multi_asset_neutral_funding_carry"
    assert _R["always_on_is_useful_diversifier"] is True
    assert _R["always_on_is_return_engine"] is False
    am = _R["always_on_metrics"]
    assert am["cagr"] == 0.087 and am["sharpe"] == 5.23
    assert am["ex_2021"] > 0 and am["y2024_2026"] > 0       # durable
    assert abs(am["corr_to_btc"]) < 0.2                     # uncorrelated
    assert _R["evidence_headline"]["always_on_is_a_dampener_not_an_engine"] is True
    assert _R["return_engine_gap_unresolved"] is True


def test_caveats_disclosed():
    cav = " ".join(_R["caveats"]).lower()
    assert "survivorship" in cav and "funding-cashflow-only" in cav and "exploratory" in cav
    assert _R["is_exploratory_only"] is True
    assert _R["is_survivorship_biased"] is True
    assert _R["is_funding_cashflow_only_approximation"] is True
    assert _R["is_survivorship_free"] is False
    assert _R["is_deployment_grade"] is False


def test_preservation_no_official_status_change():
    assert _R["c22_progress_unchanged"] == "3/20"
    assert _R["c22_state_unchanged"] == "HOLD_FOR_MORE_FROZEN_DATA_WINDOWS"
    for k in ("does_not_advance_c22", "does_not_reactivate_c23", "does_not_reactivate_c24",
              "activates_no_candidate", "promotes_no_candidate",
              "does_not_modify_official_ledger", "does_not_modify_lifecycle",
              "does_not_modify_lane_status", "kept_on_record"):
        assert _R[k] is True, k


def test_capabilities_false_and_tamper_rejected():
    for flag in rj._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        assert rj.validate_funding_carry_decision_record({**_R, flag: True})["valid"] is False
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    # cannot flip: selection to beat the null, always-on to an engine, or claim deployment-grade
    assert rj.validate_funding_carry_decision_record(
        {**_R, "always_on_is_return_engine": True})["valid"] is False
    assert rj.validate_funding_carry_decision_record(
        {**_R, "is_deployment_grade": True})["valid"] is False
    assert rj.validate_funding_carry_decision_record(
        {**_R, "does_not_advance_c22": False})["valid"] is False


def test_module_purity():
    src = Path(rj.__file__).read_text(encoding="utf-8")
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "open(",
                 "subprocess", "urlopen", "requests.", "json.load", "read_text"):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "subprocess",
              "os", "io", "shutil", "json", "hashlib", "pathlib", "numpy", "pandas"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned), imported & banned
