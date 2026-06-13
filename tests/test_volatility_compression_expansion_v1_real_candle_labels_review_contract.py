"""Tests for the Candidate #7 real-candle detector labels review
(VOLATILITY_COMPRESSION_EXPANSION_V1).

Verifies: chain gates live; both artifact shas; staged BTCUSD shas;
the aggregation rule (3840 15m -> 240 4h, complete 16-quarter-hour);
122 total attempts; 0 accepted before & after anti-cluster; 122
rejected by scanner on `rejected_contraction_window`; 0 dropped by
anti-cluster; zero floor pass at every variant; event_index range
[118, 239]; first/last sorted setup IDs; summary self-claims; review
flags downstream locks; AST/purity green; commander safety suite
alongside (12 tests)."""

from __future__ import annotations

import ast

import pytest

import sparta_commander.volatility_compression_expansion_v1_real_candle_labels_review_contract as c7l

REPO_ROOT = "C:/SPARTA_BRAIN"


def _good_observation():
    return {
        "labels_exists": True, "summary_exists": True,
        "labels_sha256": c7l.EXPECTED_LABELS_SHA256,
        "summary_sha256": c7l.EXPECTED_SUMMARY_SHA256,
        "labels_line_count": c7l.EXPECTED_TOTAL_ATTEMPTS,
        "status_breakdown": dict(c7l.EXPECTED_STATUS_BREAKDOWN),
        "all_symbols_btcusd": True,
        "all_timeframes_4h": True,
        "all_direction_long": True,
        "all_accepted_for_labeling_none_when_rejected_contraction":
            True,
        "min_event_index_seen": c7l.EXPECTED_MIN_EVENT_INDEX,
        "max_event_index_seen": c7l.EXPECTED_MAX_EVENT_INDEX,
        "first_three_sorted_setup_ids":
            c7l.EXPECTED_FIRST_THREE_SORTED_SETUP_IDS,
        "last_three_sorted_setup_ids":
            c7l.EXPECTED_LAST_THREE_SORTED_SETUP_IDS,
        "summary_candidate_id":
            "VOLATILITY_COMPRESSION_EXPANSION_V1",
        "summary_symbol": "BTCUSD",
        "summary_timeframe": "4h",
        "summary_direction": "long_only",
        "summary_sample_tag": "2026-05-02_2026-06-10",
        "summary_replay_executed_now": False,
        "summary_pnl_computed": False,
        "summary_labels_authorize_nothing": True,
        "summary_anti_cluster_does_not_consume_edit_token": True,
        "summary_statuses_closed_set_ok": True,
        "summary_git_head": c7l.HEAD_AT_DETECTION,
        "summary_total_attempts": 122,
        "summary_accepted_before_anti_cluster": 0,
        "summary_accepted_after_anti_cluster": 0,
        "summary_rejected_by_scanner": 122,
        "summary_dropped_by_anti_cluster": 0,
        "summary_status_breakdown":
            {"rejected_contraction_window": 122},
        "summary_floor_pass_pre": {"2r": 0, "3r": 0, "4r": 0},
        "summary_floor_pass_post": {"2r": 0, "3r": 0, "4r": 0},
        "summary_bars_15m": 3840,
        "summary_bars_4h": 240,
        "staged_shas_now": dict(c7l.EXPECTED_STAGED_SHAS),
        "staged_shas_match": True,
        "artifacts_tracked_in_git": [],
    }


def test_certify_passes_on_expected_observation():
    result = c7l.certify_c7_labels_review(_good_observation())
    assert result["certified"] is True
    assert result["failures"] == []


def test_artifact_shas_frozen_exact():
    assert c7l.EXPECTED_LABELS_SHA256 == (
        "dc242578436b00bd22b5352153e5b5226d3dce4449bf67db6ab9229d61f988"
        "61")
    assert c7l.EXPECTED_SUMMARY_SHA256 == (
        "b9d9d781d7557ad58d7bae3e796cf8d9cea582b7fd71f8e7ca8672c35ffec3"
        "2e")
    bad = _good_observation()
    bad["labels_sha256"] = "00" * 32
    assert "labels_sha_mismatch" in c7l.certify_c7_labels_review(
        bad)["failures"]
    bad2 = _good_observation()
    bad2["summary_sha256"] = "00" * 32
    assert "summary_sha_mismatch" in c7l.certify_c7_labels_review(
        bad2)["failures"]


def test_staged_btcusd_shas_pinned_and_required_unchanged():
    assert set(c7l.EXPECTED_STAGED_SHAS) == {
        "data/ny_fvg_choch/staged/BTCUSD_15m_2026-05-02_2026-06-09.csv",
        "data/ny_fvg_choch/staged/BTCUSD_15m_2026-06-01_2026-06-10.csv"}
    for sha in c7l.EXPECTED_STAGED_SHAS.values():
        assert len(sha) == 64
        # only hex chars
        int(sha, 16)
    bad = _good_observation()
    bad["staged_shas_match"] = False
    assert "staged_data_shas_changed" in (
        c7l.certify_c7_labels_review(bad)["failures"])


def test_aggregation_rule_frozen():
    rule = c7l.EXPECTED_AGGREGATION_RULE
    assert rule["method"] == "aggregate_4h_from_15m"
    assert rule["buckets_aligned_to_hours"] == (0, 4, 8, 12, 16, 20)
    assert rule["complete_bucket_rule"] == (
        "exactly_16_15m_bars_per_bucket")
    assert rule["incomplete_buckets_dropped"] is True
    assert rule["bars_15m_input"] == 3840
    assert rule["bars_4h_output"] == 240
    # 3840 / 16 = 240 with zero remainder
    assert rule["bars_15m_input"] % 16 == 0
    assert rule["bars_15m_input"] // 16 == rule["bars_4h_output"]


def test_frozen_counts_are_zero_accepted_zero_drops():
    assert c7l.EXPECTED_TOTAL_ATTEMPTS == 122
    assert c7l.EXPECTED_ACCEPTED_PRE_ANTI_CLUSTER == 0
    assert c7l.EXPECTED_ACCEPTED_POST_ANTI_CLUSTER == 0
    assert c7l.EXPECTED_REJECTED_BY_SCANNER == 122
    assert c7l.EXPECTED_DROPPED_BY_ANTI_CLUSTER == 0
    # the breakdown sums to total
    assert sum(c7l.EXPECTED_STATUS_BREAKDOWN.values()) == 122
    assert c7l.EXPECTED_STATUS_BREAKDOWN == {
        "rejected_contraction_window": 122}
    # tamper rejects
    for field, value in (
            ("labels_line_count", 121),
            ("summary_total_attempts", 121),
            ("summary_accepted_before_anti_cluster", 1),
            ("summary_accepted_after_anti_cluster", 1),
            ("summary_rejected_by_scanner", 100),
            ("summary_dropped_by_anti_cluster", 5),
            ("status_breakdown",
             {"accepted_for_replay_review": 122})):
        bad = _good_observation()
        bad[field] = value
        result = c7l.certify_c7_labels_review(bad)
        assert result["certified"] is False, field


def test_rejection_breakdown_is_all_contraction_window():
    assert "rejected_contraction_window" in (
        c7l.EXPECTED_STATUS_BREAKDOWN)
    assert c7l.EXPECTED_STATUS_BREAKDOWN[
        "rejected_contraction_window"] == 122
    # any other status would be a failure
    bad = _good_observation()
    bad["status_breakdown"] = {
        "rejected_contraction_window": 100,
        "rejected_expansion_multiplier": 22}
    assert "status_breakdown_mismatch" in (
        c7l.certify_c7_labels_review(bad)["failures"])


def test_floor_pass_is_zero_at_every_variant():
    assert c7l.EXPECTED_FLOOR_PASS_COUNTS == {
        "2r": 0, "3r": 0, "4r": 0}
    for key, value in (
            ("summary_floor_pass_pre", {"2r": 1, "3r": 0, "4r": 0}),
            ("summary_floor_pass_post", {"2r": 0, "3r": 5, "4r": 0})):
        bad = _good_observation()
        bad[key] = value
        result = c7l.certify_c7_labels_review(bad)
        assert result["certified"] is False, key


def test_event_index_range_and_first_last_setup_ids():
    assert c7l.EXPECTED_MIN_EVENT_INDEX == 118
    assert c7l.EXPECTED_MAX_EVENT_INDEX == 239
    assert (c7l.EXPECTED_MAX_EVENT_INDEX
            - c7l.EXPECTED_MIN_EVENT_INDEX + 1) == 122
    assert c7l.EXPECTED_FIRST_THREE_SORTED_SETUP_IDS == (
        "BTCUSD_2026-05-21T16:00:00Z",
        "BTCUSD_2026-05-21T20:00:00Z",
        "BTCUSD_2026-05-22T00:00:00Z")
    assert c7l.EXPECTED_LAST_THREE_SORTED_SETUP_IDS == (
        "BTCUSD_2026-06-10T12:00:00Z",
        "BTCUSD_2026-06-10T16:00:00Z",
        "BTCUSD_2026-06-10T20:00:00Z")
    for setup_id in (c7l.EXPECTED_FIRST_THREE_SORTED_SETUP_IDS
                     + c7l.EXPECTED_LAST_THREE_SORTED_SETUP_IDS):
        assert setup_id.startswith("BTCUSD_")
    bad = _good_observation()
    bad["min_event_index_seen"] = 200
    assert "min_event_index_must_equal_118" in (
        c7l.certify_c7_labels_review(bad)["failures"])
    bad2 = _good_observation()
    bad2["first_three_sorted_setup_ids"] = ("X", "Y", "Z")
    assert "first_three_setup_ids_mismatch" in (
        c7l.certify_c7_labels_review(bad2)["failures"])


def test_summary_self_claims_locked():
    claims = c7l.EXPECTED_SUMMARY_SELF_CLAIMS
    assert claims["replay_executed_now"] is False
    assert claims["pnl_computed"] is False
    assert claims["labels_authorize_nothing"] is True
    assert claims["anti_cluster_does_not_consume_edit_token"] is True
    assert claims["statuses_closed_set_ok"] is True
    assert claims["git_head"] == c7l.HEAD_AT_DETECTION
    for key in ("summary_replay_executed_now",
                "summary_pnl_computed",
                "summary_labels_authorize_nothing",
                "summary_anti_cluster_does_not_consume_edit_token",
                "summary_statuses_closed_set_ok"):
        bad = _good_observation()
        bad[key] = not bad[key]
        result = c7l.certify_c7_labels_review(bad)
        assert result["certified"] is False, key
    bad_head = _good_observation()
    bad_head["summary_git_head"] = "00" * 20
    assert "summary_claim_mismatch:git_head" in (
        c7l.certify_c7_labels_review(bad_head)["failures"])


def test_review_flags_downstream_locks_and_no_capability():
    record = c7l.build_c7_labels_review(REPO_ROOT, tracked_paths=[])
    assert record["is_labels_review_only"] is True
    assert record["edit_token_applied_by_this_gate"] is False
    assert record["rejection_decision_made_by_this_gate"] is False
    assert record["replay_authorized_by_this_gate"] is False
    assert record["relabel_authorized_by_this_gate"] is False
    locks = record["claim_locks"]
    for lock in ("no_profitability_claim", "no_paper_approval",
                 "no_live_approval", "no_execution_approval",
                 "no_winner_wording",
                 "no_replay_authorized_by_this_gate",
                 "no_relabel_authorized_by_this_gate",
                 "no_edit_token_applied_by_this_gate",
                 "no_rejection_decision_made_by_this_gate",
                 "anti_cluster_gap_remains_proposal_level_locked"):
        assert lock in locks, lock
    for key in ("executes", "writes_files", "labels_now",
                "runs_real_candle_detection",
                "runs_relabel", "runs_replay",
                "runs_real_detection_now", "runs_replay_now",
                "scores_now", "stages_data_now",
                "fetches_data", "calls_api", "uses_network",
                "uses_credentials", "uses_wallet", "uses_account",
                "connects_broker", "connects_exchange",
                "uses_real_money", "contains_order_logic",
                "contains_portfolio_allocation_logic",
                "starts_scheduler", "sends_notifications",
                "auto_commits", "auto_pushes",
                "creates_runners_now", "creates_data_artifacts_now",
                "modifies_staged_market_data",
                "authorizes_paper_execution",
                "authorizes_micro_live",
                "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate",
                "unlocks_replay_now", "unlocks_relabel_now",
                "unlocks_edit_token_now",
                "claims_profitability"):
        assert record[key] is False, key
        tampered = c7l.build_c7_labels_review(
            REPO_ROOT, tracked_paths=[])
        tampered[key] = True
        assert c7l.validate_c7_labels_review(
            tampered)["valid"] is False, key
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True


def test_real_artifacts_certify_when_present_and_chain_holds():
    import pathlib
    if not (pathlib.Path(REPO_ROOT) / c7l.LABELS_PATH).is_file():
        pytest.skip("candidate #7 detector labels not present")
    record = c7l.build_c7_labels_review(REPO_ROOT, tracked_paths=[])
    assert record["verdict"] == c7l.VERDICT_C7L_FROZEN
    assert record["blockers"] == []
    assert record["failures"] == []
    assert c7l.validate_c7_labels_review(record)["valid"] is True
    # determinism
    assert c7l.build_c7_labels_review(
        REPO_ROOT, tracked_paths=[]) == record
    # six-record ledger holds
    assert record["ledger_all_rejected_kept_on_record"] is True


def test_runner_and_artifacts_must_stay_untracked():
    bad = _good_observation()
    bad["artifacts_tracked_in_git"] = [c7l.RUNNER_PATH]
    assert "runner_and_artifacts_must_stay_untracked" in (
        c7l.certify_c7_labels_review(bad)["failures"])
    bad2 = _good_observation()
    bad2["artifacts_tracked_in_git"] = [c7l.LABELS_PATH]
    assert "runner_and_artifacts_must_stay_untracked" in (
        c7l.certify_c7_labels_review(bad2)["failures"])


def test_chain_blocks_when_ledger_breaks():
    import sparta_commander.volatility_compression_expansion_v1_real_candle_labels_review_contract as mod
    originals = {key: getattr(mod, key) for key in
                 ("C1_STATUS", "C2_STATUS", "C3_STATUS", "C4_STATUS",
                  "C5_STATUS", "C6_STATUS")}
    try:
        for key in originals:
            setattr(mod, key, "APPROVED_FOR_TRADING")
            rec = mod.build_c7_labels_review(
                REPO_ROOT, tracked_paths=[])
            assert rec["verdict"] == c7l.VERDICT_C7L_BLOCKED, key
            assert "six_record_ledger_broken" in rec["blockers"], key
            setattr(mod, key, originals[key])
    finally:
        for key, value in originals.items():
            setattr(mod, key, value)
    assert mod.build_c7_labels_review(
        REPO_ROOT, tracked_paths=[])["verdict"] == c7l.VERDICT_C7L_FROZEN


def test_label_next_action_and_module_purity():
    record = c7l.build_c7_labels_review(REPO_ROOT, tracked_paths=[])
    assert record["next_required_action"] == (
        "HUMAN_DECISION_C7_EDIT_OR_REJECT_ON_ZERO_ACCEPTED_REAL"
        "_CANDLE_SETUPS")
    assert c7l.VERDICT_C7L_FROZEN == (
        "CANDIDATE_7_REAL_CANDLE_LABELS_REVIEW_FROZEN")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in c7l.NEXT_REQUIRED_ACTION.upper(), banned
    assert c7l.get_candidate_7_labels_review_label() == c7l.C7L_LABEL
    assert "READ-ONLY" in c7l.C7L_LABEL
    assert "RESEARCH ONLY" in c7l.C7L_LABEL
    assert "ZERO ACCEPTED SETUPS" in c7l.C7L_LABEL
    assert "NOT A PROFITABILITY CLAIM" in c7l.C7L_LABEL
    src = open(c7l.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    assert "random" not in src
    assert "now(" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch(", "subprocess", "Popen", "system("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt",
                   "smtplib", "subprocess", "websockets", "aiohttp",
                   "schedule", "apscheduler", "threading", "asyncio",
                   "time", "sched", "telegram", "email", "csv", "pandas",
                   "os", "io", "shutil", "databento", "ssl", "ftplib",
                   "datetime", "statistics", "random"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
    assert not any(
        call.func.attr == "open" if isinstance(call.func, ast.Attribute)
        else getattr(call.func, "id", "") == "open"
        for call in ast.walk(tree) if isinstance(call, ast.Call))
