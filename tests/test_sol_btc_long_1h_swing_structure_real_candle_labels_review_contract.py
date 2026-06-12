"""Tests for the Candidate #4 real-candle labels review / evidence
freeze. Certify logic proven on synthetic observations for every failure
mode; one real-artifact test certifies the live files when present."""

from __future__ import annotations

import ast

import pytest

import sparta_commander.sol_btc_long_1h_swing_structure_real_candle_labels_review_contract as c4l

REPO_ROOT = "C:/SPARTA_BRAIN"


def _good_observation():
    return {
        "labels_exists": True, "summary_exists": True,
        "labels_sha256": c4l.EXPECTED_LABELS_SHA256,
        "summary_sha256": c4l.EXPECTED_SUMMARY_SHA256,
        "labels_line_count": 275,
        "status_breakdown": dict(c4l.EXPECTED_STATUS_BREAKDOWN),
        "accepted_count": 22,
        "per_symbol_counts": {
            "SOLUSD": {"attempts": 137, "accepted": 12, "rejected": 125},
            "BTCUSD": {"attempts": 138, "accepted": 10, "rejected": 128}},
        "accepted_all_at_or_above_floor": True,
        "accepted_risk_bps_min": 83.86,
        "accepted_risk_bps_median": 139.39,
        "accepted_risk_bps_max": 402.67,
        "structural_stop_count": 21,
        "atr_stop_count": 1,
        "sol_accepted_count": 12,
        "btc_accepted_count": 10,
        "near_zero_rule_triggered": False,
        "candidate_id_in_labels": True,
        "statuses_in_closed_set": True,
        "artifacts_tracked_in_git": [],
    }


def test_certify_passes_on_expected_observation():
    result = c4l.certify_c4_labels_review(_good_observation())
    assert result["certified"] is True
    assert result["failures"] == []


def test_certify_failure_modes():
    cases = (
        ({"labels_exists": False}, "labels_artifact_missing"),
        ({"summary_exists": False}, "summary_artifact_missing"),
        ({"labels_sha256": "00" * 32}, "labels_sha_mismatch"),
        ({"summary_sha256": "00" * 32}, "summary_sha_mismatch"),
        ({"labels_line_count": 274}, "label_count_mismatch"),
        ({"accepted_count": 23}, "accepted_count_mismatch"),
        ({"status_breakdown": {"accepted_for_replay_review": 22}},
         "status_breakdown_mismatch"),
        ({"accepted_all_at_or_above_floor": False},
         "accepted_label_below_floor"),
        ({"accepted_risk_bps_min": 80.0}, "risk_min_mismatch"),
        ({"accepted_risk_bps_median": 100.0}, "risk_median_mismatch"),
        ({"accepted_risk_bps_max": 500.0}, "risk_max_mismatch"),
        ({"structural_stop_count": 22}, "structural_stop_count_mismatch"),
        ({"atr_stop_count": 0}, "atr_stop_count_mismatch"),
        ({"sol_accepted_count": 11}, "sol_accepted_mismatch"),
        ({"btc_accepted_count": 11}, "btc_accepted_mismatch"),
        ({"near_zero_rule_triggered": True},
         "near_zero_rule_must_not_have_triggered"),
        ({"candidate_id_in_labels": False},
         "candidate_id_mismatch_in_labels"),
        ({"statuses_in_closed_set": False}, "status_outside_closed_set"),
        ({"artifacts_tracked_in_git": [c4l.LABELS_PATH]},
         "artifacts_must_stay_untracked"),
    )
    for override, expected_failure in cases:
        observation = _good_observation()
        observation.update(override)
        result = c4l.certify_c4_labels_review(observation)
        assert result["certified"] is False, expected_failure
        assert expected_failure in result["failures"], expected_failure
    extra_symbol = _good_observation()
    extra_symbol["per_symbol_counts"]["ETHUSD"] = {
        "attempts": 1, "accepted": 0, "rejected": 1}
    assert "unexpected_symbols_in_labels" in c4l.certify_c4_labels_review(
        extra_symbol)["failures"]
    assert c4l.certify_c4_labels_review(None)["certified"] is False


def test_frozen_counts_breakdown_and_consistency():
    assert c4l.EXPECTED_COUNTS["SOLUSD"] == {
        "attempts": 137, "accepted": 12, "rejected": 125}
    assert c4l.EXPECTED_COUNTS["BTCUSD"] == {
        "attempts": 138, "accepted": 10, "rejected": 128}
    assert c4l.EXPECTED_COUNTS["total"] == {
        "attempts": 275, "accepted": 22, "rejected": 253}
    assert sum(c4l.EXPECTED_STATUS_BREAKDOWN.values()) == 275
    assert c4l.EXPECTED_STATUS_BREAKDOWN == {
        "accepted_for_replay_review": 22,
        "rejected_not_higher_low": 137,
        "rejected_sl2_low_broken_before_entry": 78,
        "rejected_trend_not_qualified": 26,
        "rejected_cost_floor_risk_too_small": 6,
        "rejected_insufficient_4h_history": 4,
        "rejected_no_trigger_close_within_window": 2}
    # the frozen counts themselves must satisfy the near-zero outcome
    assert (c4l.EXPECTED_COUNTS["total"]["accepted"]
            >= c4l.NEAR_ZERO_THRESHOLD_ACCEPTED_LABELS)
    facts = c4l.EXPECTED_ACCEPTED_FACTS
    assert facts == {
        "all_cleared_81bps_floor": True,
        "risk_bps_min": 83.86, "risk_bps_median": 139.39,
        "risk_bps_max": 402.67,
        "structural_stop_count": 21, "atr_stop_count": 1,
        "sol_accepted": 12, "btc_accepted": 10}
    assert facts["structural_stop_count"] + facts["atr_stop_count"] == 22
    assert facts["sol_accepted"] + facts["btc_accepted"] == 22
    assert facts["risk_bps_min"] >= 81
    assert c4l.EXPECTED_LABELS_SHA256 == (
        "8b89b87dd615921405cf4e7a9f50ef908b6dfbcdc593f6781ff062a6"
        "a2dcc746")
    assert c4l.EXPECTED_SUMMARY_SHA256 == (
        "d70b6979f33186d4538897e4cf92e3fd2787d18793dddf7a0c0b1db5"
        "56336205")


def test_frozen_decision_facts_no_replay_no_claims():
    facts = c4l.FROZEN_DECISION_FACTS
    assert any("exactly once" in fact for fact in facts)
    assert any("did not trigger" in fact for fact in facts)
    assert any("replay has not yet run" in fact for fact in facts)
    assert any("no profitability claim" in fact for fact in facts)
    record = c4l.build_c4_labels_review(REPO_ROOT, tracked_paths=[])
    assert record["replay_has_run"] is False
    for field, value in (("replay_has_run", True),
                         ("expected_labels_sha256", "00" * 32),
                         ("expected_counts", {}),
                         ("expected_status_breakdown", {}),
                         ("expected_accepted_facts", {}),
                         ("near_zero_threshold_accepted_labels", 5),
                         ("frozen_decision_facts", []),
                         ("claims_profitability", True),
                         ("revives_candidate_3", True),
                         ("live_gate_locked", False)):
        tampered = c4l.build_c4_labels_review(REPO_ROOT,
                                              tracked_paths=[])
        tampered[field] = value
        assert c4l.validate_c4_labels_review(
            tampered)["valid"] is False, field


def test_real_artifacts_certify_when_present():
    import pathlib
    if not (pathlib.Path(REPO_ROOT) / c4l.LABELS_PATH).is_file():
        pytest.skip("candidate #4 label artifacts not present")
    record = c4l.build_c4_labels_review(REPO_ROOT, tracked_paths=[])
    assert record["verdict"] == c4l.VERDICT_C4L_FROZEN
    assert record["failures"] == []
    assert c4l.validate_c4_labels_review(record)["valid"] is True


def test_ledger_gate_and_capabilities():
    from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
        REJECTION_STATUS as C1)
    from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (
        REJECTION_STATUS as C2)
    from sparta_commander.btc_sol_long_trend_continuation_v1_result_and_rejection_record_contract import (
        REJECTION_STATUS as C3)
    assert C1 == C2 == C3 == "REJECTED_KEPT_ON_RECORD"
    record = c4l.build_c4_labels_review(REPO_ROOT, tracked_paths=[])
    assert record["verdict"] != c4l.VERDICT_C4L_BLOCKED
    for key in ("executes", "writes_files", "runs_real_detection_now",
                "runs_replay_now", "scores_now", "stages_data_now",
                "fetches_data", "calls_api", "uses_network",
                "uses_credentials", "uses_wallet", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate",
                "claims_profitability", "revives_candidate_3"):
        assert record[key] is False, key
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True


def test_label_action_and_module_purity():
    assert c4l.get_c4_labels_review_label() == c4l.C4L_LABEL
    assert "READ-ONLY" in c4l.C4L_LABEL
    assert "NOT A PROFITABILITY CLAIM" in c4l.C4L_LABEL
    assert c4l.C4L_MODE == "RESEARCH_ONLY"
    assert c4l.NEXT_REQUIRED_ACTION == (
        "HUMAN_APPROVED_C4_FEE_HONEST_REPLAY_OF_22_ACCEPTED_LABELS")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in c4l.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(c4l.__file__, encoding="utf-8").read()
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
