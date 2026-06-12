"""Tests for the Candidate #3 V1 result freeze + formal rejection record.

Proves: certification recounts the V1 artifacts and matches every frozen
fact; the near-zero rule trigger is re-derived, not trusted; the
rejection status/reason and permanence flags are tamper-locked; seeds are
never rescue paths; zero capability."""

from __future__ import annotations

import ast

import pytest

import sparta_commander.btc_sol_long_trend_continuation_v1_result_and_rejection_record_contract as rj3

REPO_ROOT = "C:/SPARTA_BRAIN"


def _good_observation():
    return {
        "labels_exists": True, "summary_exists": True,
        "labels_sha256": rj3.EXPECTED_V1_LABELS_SHA256,
        "summary_sha256": rj3.EXPECTED_V1_SUMMARY_SHA256,
        "labels_line_count": 711,
        "status_breakdown": dict(rj3.EXPECTED_V1_STATUS_BREAKDOWN),
        "accepted_count": 9,
        "per_symbol_counts": {
            "BTCUSD": {"attempts": 334, "accepted": 2, "rejected": 332},
            "SOLUSD": {"attempts": 377, "accepted": 7, "rejected": 370}},
        "sol_accepted_count": 7,
        "accepted_all_structural_stops": True,
        "accepted_risk_bps_min": 92.18,
        "accepted_risk_bps_max": 151.47,
        "near_zero_rule_triggered": True,
        "artifacts_tracked_in_git": [],
    }


def test_certify_passes_on_expected_observation():
    result = rj3.certify_v1_result(_good_observation())
    assert result["certified"] is True
    assert result["failures"] == []


def test_certify_failure_modes():
    cases = (
        ({"labels_exists": False}, "labels_artifact_missing"),
        ({"summary_exists": False}, "summary_artifact_missing"),
        ({"labels_sha256": "00" * 32}, "labels_sha_mismatch"),
        ({"summary_sha256": "00" * 32}, "summary_sha_mismatch"),
        ({"labels_line_count": 710}, "label_count_mismatch"),
        ({"accepted_count": 10}, "accepted_count_mismatch"),
        ({"status_breakdown": {"accepted_for_replay_review": 9}},
         "status_breakdown_mismatch"),
        ({"sol_accepted_count": 6}, "sol_seed_observation_mismatch"),
        ({"accepted_all_structural_stops": False},
         "structural_stop_seed_observation_mismatch"),
        ({"accepted_risk_bps_min": 80.0}, "risk_min_mismatch"),
        ({"accepted_risk_bps_max": 160.0}, "risk_max_mismatch"),
        ({"near_zero_rule_triggered": False},
         "near_zero_rule_must_have_triggered"),
        ({"artifacts_tracked_in_git": [rj3.V1_LABELS_PATH]},
         "artifacts_must_stay_untracked"),
    )
    for override, expected_failure in cases:
        observation = _good_observation()
        observation.update(override)
        result = rj3.certify_v1_result(observation)
        assert result["certified"] is False, expected_failure
        assert expected_failure in result["failures"], expected_failure
    bad_symbol = _good_observation()
    bad_symbol["per_symbol_counts"]["BTCUSD"]["accepted"] = 3
    assert rj3.certify_v1_result(bad_symbol)["certified"] is False
    assert rj3.certify_v1_result(None)["certified"] is False


def test_frozen_counts_breakdown_and_rule_consistency():
    assert rj3.EXPECTED_V1_COUNTS["BTCUSD"] == {
        "attempts": 334, "accepted": 2, "rejected": 332}
    assert rj3.EXPECTED_V1_COUNTS["SOLUSD"] == {
        "attempts": 377, "accepted": 7, "rejected": 370}
    assert rj3.EXPECTED_V1_COUNTS["total"] == {
        "attempts": 711, "accepted": 9, "rejected": 702}
    assert sum(rj3.EXPECTED_V1_STATUS_BREAKDOWN.values()) == 711
    assert rj3.EXPECTED_V1_STATUS_BREAKDOWN[
        "accepted_for_replay_review"] == 9
    assert rj3.EXPECTED_V1_STATUS_BREAKDOWN == {
        "accepted_for_replay_review": 9,
        "rejected_pullback_too_short": 399,
        "rejected_no_resumption_close": 147,
        "rejected_retrace_too_deep": 46,
        "rejected_trend_not_qualified": 46,
        "rejected_cost_floor_risk_too_small": 29,
        "rejected_pullback_broke_swing_low": 19,
        "rejected_pullback_too_long": 15,
        "rejected_insufficient_1h_history": 1}
    # the frozen counts themselves must satisfy the near-zero rule
    assert (rj3.EXPECTED_V1_COUNTS["total"]["accepted"]
            < rj3.NEAR_ZERO_THRESHOLD_ACCEPTED_LABELS)
    assert rj3.NEAR_ZERO_THRESHOLD_ACCEPTED_LABELS == 10
    assert rj3.EXPECTED_V1_LABELS_SHA256 == (
        "e02d58c184656b49731519d04a2101a05cc90874a9234b7647638d0a"
        "3656a69b")
    assert rj3.EXPECTED_V1_SUMMARY_SHA256 == (
        "99e1eee0ccb9c76a588bf065b44eff0df84d406fc1c50e33818df4fc"
        "3233f63f")


def test_rejection_status_reason_and_facts():
    assert rj3.REJECTION_STATUS == "REJECTED_KEPT_ON_RECORD"
    assert rj3.REJECTION_REASON == (
        "NEAR_ZERO_SETUPS_AFTER_ONE_AUTHORIZED_STRUCTURE_EDIT")
    facts = rj3.FROZEN_RESULT_FACTS
    assert any("one authorized edit" in fact for fact in facts)
    assert any("exactly once" in fact for fact in facts)
    assert any("below the pre-committed near-zero threshold" in fact
               for fact in facts)
    assert any("no replay is authorized" in fact for fact in facts)
    assert any("no second mutable edit" in fact for fact in facts)
    assert any("no profitability claim" in fact for fact in facts)


def test_seed_observations_never_rescue_paths():
    seeds = rj3.SEED_OBSERVATIONS_FOR_NEW_FAMILIES_ONLY
    assert seeds == (
        "sol_produced_7_of_9_accepted_labels",
        "all_9_accepted_labels_used_structural_stops",
        "accepted_risk_distances_were_healthy_92_to_151_bps")
    assert rj3.SEEDS_ARE_NEVER_RESCUE_PATHS is True
    record = rj3.build_tc3_rejection_record(REPO_ROOT, tracked_paths=[])
    assert record["seeds_are_never_rescue_paths"] is True
    assert record["candidate_3_may_continue_as_is"] is False
    assert record["candidate_3_may_receive_another_mutable_edit"] is False
    assert record["replay_authorized"] is False


def test_real_artifacts_certify_when_present():
    import pathlib
    if not (pathlib.Path(REPO_ROOT) / rj3.V1_LABELS_PATH).is_file():
        pytest.skip("candidate #3 v1 artifacts not present")
    record = rj3.build_tc3_rejection_record(REPO_ROOT, tracked_paths=[])
    assert record["verdict"] == rj3.VERDICT_RJ3_RECORDED
    assert record["failures"] == []
    assert rj3.validate_tc3_rejection_record(record)["valid"] is True


def test_tampering_invalidates():
    record = rj3.build_tc3_rejection_record(REPO_ROOT, tracked_paths=[])
    for field, value in (
            ("rejection_status", "ACCEPTED"),
            ("rejection_reason", "NONE"),
            ("expected_v1_labels_sha256", "00" * 32),
            ("expected_v1_counts", {}),
            ("expected_v1_status_breakdown", {}),
            ("near_zero_threshold_accepted_labels", 5),
            ("frozen_result_facts", []),
            ("seed_observations_for_new_families_only", []),
            ("seeds_are_never_rescue_paths", False),
            ("candidate_3_may_continue_as_is", True),
            ("candidate_3_may_receive_another_mutable_edit", True),
            ("replay_authorized", True),
            ("claims_profitability", True),
            ("revives_candidate_2", True),
            ("live_gate_locked", False)):
        tampered = rj3.build_tc3_rejection_record(REPO_ROOT,
                                                  tracked_paths=[])
        tampered[field] = value
        assert rj3.validate_tc3_rejection_record(
            tampered)["valid"] is False, field


def test_ledger_intact_and_capabilities_locked():
    from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
        REJECTION_STATUS as C1)
    from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (
        REJECTION_STATUS as C2)
    assert C1 == C2 == "REJECTED_KEPT_ON_RECORD"
    record = rj3.build_tc3_rejection_record(REPO_ROOT, tracked_paths=[])
    assert record["verdict"] != rj3.VERDICT_RJ3_BLOCKED
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
    assert rj3.get_tc3_rejection_record_label() == rj3.RJ3_LABEL
    assert "READ-ONLY" in rj3.RJ3_LABEL
    assert "REJECTED KEPT ON RECORD" in rj3.RJ3_LABEL
    assert rj3.RJ3_MODE == "RESEARCH_ONLY"
    assert rj3.NEXT_REQUIRED_ACTION == (
        "HUMAN_DECISION_ON_NEXT_CANDIDATE_FAMILY")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in rj3.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(rj3.__file__, encoding="utf-8").read()
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
