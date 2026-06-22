"""Tests for the combined C23/C24 portfolio-sleeve rejection record.

Proves the record is PURE / REJECTION-RECORD-ONLY: a sleeve-lane REJECT of BOTH C23 (net-
negative low-vol neutral sleeve) and C24 (non-stationary 2021-only illiquidity sleeve that
fails forward-OOS robustness and does not beat BTC risk-adjusted); anchored to the pushed
evidence commit + frozen data manifest hash; preserves the decisive failure facts (cannot be
flipped); keeps C22 unchanged at 3/20 HOLD and C23/C24 not-active/not-promoted; does NOT modify
the official ledger / lifecycle / lane status; discloses exploratory + survivorship bias; and
pins every capability flag False."""
from __future__ import annotations

import ast
from pathlib import Path

import sparta_commander.c23_c24_combined_sleeve_rejection_record_contract as rj

_R = rj.build_c23_c24_sleeve_rejection_record()


def test_builds_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_rejection_record_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"] == "REJECT_C23_AND_C24_AS_CROSS_SECTIONAL_PORTFOLIO_SLEEVES"
    assert _R["combined_decision"] == "REJECT"
    assert rj.validate_c23_c24_sleeve_rejection_record(_R)["valid"] is True


def test_anchored_to_pushed_evidence():
    assert _R["anchored_to_evidence_commit"] == "816547254692b83b6c66993f656bc75498532368"
    assert len(_R["data_manifest_sha256"]) == 64
    assert _R["data_manifest_sha256"] == (
        "6dde40284e089a1a8b59ee6a06a801818a44f44d617930cf4cb1e3284a000f99")


def test_decisive_failure_facts():
    eh = _R["evidence_headline"]
    assert eh["c23_net_negative_after_cost"] is True
    assert eh["c24_return_is_2021_artifact"] is True
    assert eh["c24_negative_recent_years"] is True
    assert eh["c24_does_not_beat_btc_risk_adjusted"] is True
    assert eh["neither_is_a_return_engine"] is True
    assert _R["c23_metrics"]["net_cagr"] < 0 and _R["c23_metrics"]["sharpe"] < 0
    assert _R["c24_metrics"]["ex_2021_compounded"] < 0
    assert _R["c24_metrics"]["sharpe"] < _R["btc_bench_sharpe"]
    assert _R["return_engine_gap_unresolved"] is True


def test_exploratory_survivorship_disclosed():
    assert _R["is_exploratory_only"] is True
    assert _R["is_survivorship_biased"] is True
    assert _R["is_survivorship_free"] is False
    assert _R["is_deployment_grade"] is False


def test_preservation_no_official_status_change():
    assert _R["c22_progress_unchanged"] == "3/20"
    assert _R["c22_state_unchanged"] == "HOLD_FOR_MORE_FROZEN_DATA_WINDOWS"
    assert _R["c23_is_active"] is False and _R["c24_is_active"] is False
    for k in ("does_not_advance_c22", "does_not_activate_c23", "does_not_activate_c24",
              "does_not_promote_c23", "does_not_promote_c24",
              "does_not_modify_official_rejected_family_ledger", "does_not_modify_lifecycle",
              "does_not_modify_lane_status", "kept_on_record"):
        assert _R[k] is True, k


def test_capabilities_false_and_tamper_rejected():
    for flag in rj._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        assert rj.validate_c23_c24_sleeve_rejection_record({**_R, flag: True})["valid"] is False
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    # cannot flip C24 to durable, nor mark either active, nor claim survivorship-free
    assert rj.validate_c23_c24_sleeve_rejection_record(
        {**_R, "evidence_headline": {**_R["evidence_headline"],
                                     "c24_return_is_2021_artifact": False}})["valid"] is False
    assert rj.validate_c23_c24_sleeve_rejection_record(
        {**_R, "c23_is_active": True})["valid"] is False
    assert rj.validate_c23_c24_sleeve_rejection_record(
        {**_R, "is_survivorship_free": True})["valid"] is False
    assert rj.validate_c23_c24_sleeve_rejection_record(
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
