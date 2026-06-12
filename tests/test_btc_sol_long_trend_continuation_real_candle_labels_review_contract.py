"""Tests for the Candidate #3 real-candle labels review / evidence
freeze. Certify logic is proven on synthetic observations for every
failure mode; one real-artifact test certifies the live files when
present (skipped otherwise)."""

from __future__ import annotations

import ast

import pytest

import sparta_commander.btc_sol_long_trend_continuation_real_candle_labels_review_contract as tcl

REPO_ROOT = "C:/SPARTA_BRAIN"


def _good_observation():
    return {
        "labels_exists": True, "summary_exists": True,
        "labels_sha256": tcl.EXPECTED_LABELS_SHA256,
        "summary_sha256": tcl.EXPECTED_SUMMARY_SHA256,
        "labels_line_count": 711,
        "status_breakdown": dict(tcl.EXPECTED_STATUS_BREAKDOWN),
        "accepted_count": 0,
        "per_symbol_counts": {
            "BTCUSD": {"attempts": 334, "accepted": 0, "rejected": 334},
            "SOLUSD": {"attempts": 377, "accepted": 0, "rejected": 377}},
        "floor_near_misses_bps": [35.76, 37.44, 51.38, 70.58, 72.6,
                                  77.92],
        "candidate_id_in_labels": True,
        "statuses_in_closed_set": True,
        "artifacts_tracked_in_git": [],
    }


def test_certify_passes_on_expected_observation():
    result = tcl.certify_tc3_labels_review(_good_observation())
    assert result["certified"] is True
    assert result["failures"] == []


def test_certify_failure_modes():
    cases = (
        ({"labels_exists": False}, "labels_artifact_missing"),
        ({"summary_exists": False}, "summary_artifact_missing"),
        ({"labels_sha256": "00" * 32}, "labels_sha_mismatch"),
        ({"summary_sha256": "00" * 32}, "summary_sha_mismatch"),
        ({"labels_line_count": 710}, "label_count_mismatch"),
        ({"accepted_count": 1}, "expected_zero_accepts"),
        ({"status_breakdown": {"rejected_pullback_too_short": 627}},
         "status_breakdown_mismatch"),
        ({"floor_near_misses_bps": [35.76]},
         "floor_near_misses_mismatch"),
        ({"candidate_id_in_labels": False},
         "candidate_id_mismatch_in_labels"),
        ({"statuses_in_closed_set": False},
         "status_outside_closed_set"),
        ({"artifacts_tracked_in_git": [tcl.LABELS_PATH]},
         "artifacts_must_stay_untracked"),
    )
    for override, expected_failure in cases:
        observation = _good_observation()
        observation.update(override)
        result = tcl.certify_tc3_labels_review(observation)
        assert result["certified"] is False, expected_failure
        assert expected_failure in result["failures"], expected_failure
    bad_symbol = _good_observation()
    bad_symbol["per_symbol_counts"]["BTCUSD"]["accepted"] = 1
    assert tcl.certify_tc3_labels_review(bad_symbol)["certified"] is False
    extra_symbol = _good_observation()
    extra_symbol["per_symbol_counts"]["ETHUSD"] = {
        "attempts": 1, "accepted": 0, "rejected": 1}
    result = tcl.certify_tc3_labels_review(extra_symbol)
    assert "unexpected_symbols_in_labels" in result["failures"]
    assert tcl.certify_tc3_labels_review(None)["certified"] is False


def test_frozen_counts_and_breakdown_and_near_misses():
    assert tcl.EXPECTED_COUNTS["BTCUSD"] == {
        "attempts": 334, "accepted": 0, "rejected": 334}
    assert tcl.EXPECTED_COUNTS["SOLUSD"] == {
        "attempts": 377, "accepted": 0, "rejected": 377}
    assert tcl.EXPECTED_COUNTS["total"] == {
        "attempts": 711, "accepted": 0, "rejected": 711}
    assert sum(tcl.EXPECTED_STATUS_BREAKDOWN.values()) == 711
    assert tcl.EXPECTED_STATUS_BREAKDOWN == {
        "rejected_pullback_too_short": 627,
        "rejected_no_resumption_close": 40,
        "rejected_retrace_too_deep": 15,
        "rejected_trend_not_qualified": 15,
        "rejected_pullback_broke_swing_low": 7,
        "rejected_cost_floor_risk_too_small": 6,
        "rejected_pullback_too_long": 1}
    assert "accepted_for_replay_review" not in (
        tcl.EXPECTED_STATUS_BREAKDOWN)
    assert tcl.EXPECTED_FLOOR_NEAR_MISSES_BPS == (
        35.76, 37.44, 51.38, 70.58, 72.6, 77.92)
    assert all(bps < 81 for bps in tcl.EXPECTED_FLOOR_NEAR_MISSES_BPS)
    assert tcl.EXPECTED_LABELS_SHA256 == (
        "ad7fb2813804d01c8e0e31014651eb4c459b32ac8cdc26e62c61a7ee"
        "4074c2cc")
    assert tcl.EXPECTED_SUMMARY_SHA256 == (
        "dda0766e7880d9fef1c7a451a09b183095df0e46d4c41cf4f45e9eee"
        "57853af9")


def test_frozen_decision_facts_and_authorizations():
    facts = tcl.FROZEN_DECISION_FACTS
    assert any("valid honest outcome" in fact for fact in facts)
    assert any("no replay is authorized" in fact for fact in facts)
    assert any("no profitability claim" in fact for fact in facts)
    assert any("no mutable edit is authorized" in fact for fact in facts)
    record = tcl.build_tc3_labels_review(REPO_ROOT, tracked_paths=[])
    assert record["replay_authorized"] is False
    assert record["mutable_edit_authorized"] is False
    for field, value in (("replay_authorized", True),
                         ("mutable_edit_authorized", True),
                         ("expected_labels_sha256", "00" * 32),
                         ("expected_counts", {}),
                         ("expected_status_breakdown", {}),
                         ("expected_floor_near_misses_bps", [1.0]),
                         ("frozen_decision_facts", []),
                         ("claims_profitability", True),
                         ("live_gate_locked", False)):
        tampered = tcl.build_tc3_labels_review(REPO_ROOT,
                                               tracked_paths=[])
        tampered[field] = value
        assert tcl.validate_tc3_labels_review(
            tampered)["valid"] is False, field


def test_real_artifacts_certify_when_present():
    import pathlib
    if not (pathlib.Path(REPO_ROOT) / tcl.LABELS_PATH).is_file():
        pytest.skip("candidate #3 label artifacts not present")
    record = tcl.build_tc3_labels_review(REPO_ROOT, tracked_paths=[])
    assert record["verdict"] == tcl.VERDICT_TCL_FROZEN
    assert record["failures"] == []
    assert tcl.validate_tc3_labels_review(record)["valid"] is True


def test_ledger_gate_and_capabilities():
    record = tcl.build_tc3_labels_review(REPO_ROOT, tracked_paths=[])
    assert record["verdict"] != tcl.VERDICT_TCL_BLOCKED
    from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
        REJECTION_STATUS as C1)
    from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (
        REJECTION_STATUS as C2)
    assert C1 == C2 == "REJECTED_KEPT_ON_RECORD"
    for key in ("executes", "writes_files", "runs_real_detection_now",
                "runs_replay_now", "scores_now", "stages_data_now",
                "fetches_data", "calls_api", "uses_network",
                "uses_credentials", "uses_wallet", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate",
                "claims_profitability", "revives_candidate_2"):
        assert record[key] is False, key
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True


def test_label_action_and_module_purity():
    assert tcl.get_tc3_labels_review_label() == tcl.TCL_LABEL
    assert "READ-ONLY" in tcl.TCL_LABEL
    assert "ZERO ACCEPTS FROZEN" in tcl.TCL_LABEL
    assert tcl.TCL_MODE == "RESEARCH_ONLY"
    assert tcl.NEXT_REQUIRED_ACTION == (
        "HUMAN_DECISION_ON_CANDIDATE_3_OUTCOME")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in tcl.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(tcl.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt",
                   "smtplib", "subprocess", "websockets", "aiohttp",
                   "schedule", "apscheduler", "threading", "asyncio",
                   "time", "sched", "telegram", "email", "csv", "pandas",
                   "os", "io", "shutil", "databento", "ssl", "ftplib",
                   "datetime"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
    assert not any(
        call.func.attr == "open" if isinstance(call.func, ast.Attribute)
        else getattr(call.func, "id", "") == "open"
        for call in ast.walk(tree) if isinstance(call, ast.Call))
