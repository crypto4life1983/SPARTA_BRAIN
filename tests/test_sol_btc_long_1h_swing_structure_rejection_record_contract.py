"""Tests for the Candidate #4 formal rejection record.

Verifies: live replay-review gate; filter artifact sha; all filtered
variant arithmetic; gross+net negative everywhere; reduce-or-equal trade
counts; zero overlaps after filter; edit allowance spent; rejection
verdict string; no paper/live/profitability; untracked runner/artifact;
seeds preserved for future families only. Tamper tests on every frozen
block. Commander safety suite runs alongside per repo pattern."""

from __future__ import annotations

import ast
import copy

import pytest

import sparta_commander.sol_btc_long_1h_swing_structure_rejection_record_contract as rj4

REPO_ROOT = "C:/SPARTA_BRAIN"


def _good_observation():
    return {
        "eval_exists": True,
        "eval_sha256": rj4.EXPECTED_FILTER_EVAL_SHA256,
        "classification": "C4_FILTER_ONLY_EDIT_FAILED_REJECT_NEXT",
        "variants": copy.deepcopy(rj4.EXPECTED_FILTERED_VARIANTS),
        "accounting_ok": True,
        "all_gross_negative": True,
        "all_net_negative": True,
        "all_overlaps_zero": True,
        "all_counts_reduce_or_equal": True,
        "artifacts_tracked_in_git": [],
    }


def test_certify_passes_on_expected_observation():
    result = rj4.certify_c4_rejection(_good_observation())
    assert result["certified"] is True
    assert result["failures"] == []


def test_certify_failure_modes():
    cases = (
        ({"eval_exists": False}, "filter_eval_artifact_missing"),
        ({"eval_sha256": "00" * 32}, "filter_eval_sha_mismatch"),
        ({"classification": "C4_FILTER_ONLY_EDIT_POSITIVE"},
         "classification_mismatch"),
        ({"accounting_ok": False}, "kept_removed_accounting_broken"),
        ({"all_gross_negative": False}, "gross_negative_fact_broken"),
        ({"all_net_negative": False}, "net_negative_fact_broken"),
        ({"all_overlaps_zero": False}, "overlaps_not_zero_after_filter"),
        ({"all_counts_reduce_or_equal": False},
         "filter_increased_trades_invalid"),
        ({"artifacts_tracked_in_git": [rj4.FILTER_RUNNER_PATH]},
         "runner_and_artifact_must_stay_untracked"),
    )
    for override, expected_failure in cases:
        observation = _good_observation()
        observation.update(override)
        result = rj4.certify_c4_rejection(observation)
        assert result["certified"] is False, expected_failure
        assert expected_failure in result["failures"], expected_failure
    # arithmetic tampers: net R, gross R, hits/stops/timeouts, overlaps
    for variant, key, value, expected in (
            ("2r", "net_r", -1.0, "filtered_fact_mismatch:2r:net_r"),
            ("3r", "gross_r", 1.0, "filtered_fact_mismatch:3r:gross_r"),
            ("4r", "hits", 3, "filtered_fact_mismatch:4r:hits"),
            ("2r", "stops", 5, "filtered_fact_mismatch:2r:stops"),
            ("3r", "timeouts", 1, "filtered_fact_mismatch:3r:timeouts"),
            ("4r", "overlaps_after", 2,
             "filtered_fact_mismatch:4r:overlaps_after"),
            ("2r", "filtered_trades", 9,
             "filtered_fact_mismatch:2r:filtered_trades")):
        observation = _good_observation()
        observation["variants"][variant][key] = value
        result = rj4.certify_c4_rejection(observation)
        assert expected in result["failures"], expected
    assert rj4.certify_c4_rejection(None)["certified"] is False


def test_frozen_filtered_variant_table_exact():
    table = rj4.EXPECTED_FILTERED_VARIANTS
    assert table["2r"] == {
        "original_trades": 22, "filtered_trades": 8,
        "removed_trades": 14, "hits": 2, "stops": 6, "timeouts": 0,
        "hit_rate_pct": 25.0, "gross_breakeven_rate_pct": 33.3,
        "gross_r": -2.0, "fee_r": 1.29908, "net_r": -3.29908,
        "overlaps_after": 0}
    assert table["3r"] == {
        "original_trades": 22, "filtered_trades": 7,
        "removed_trades": 15, "hits": 1, "stops": 6, "timeouts": 0,
        "hit_rate_pct": 14.3, "gross_breakeven_rate_pct": 25.0,
        "gross_r": -3.0, "fee_r": 1.232028, "net_r": -4.232028,
        "overlaps_after": 0}
    assert table["4r"] == {
        "original_trades": 22, "filtered_trades": 7,
        "removed_trades": 15, "hits": 1, "stops": 6, "timeouts": 0,
        "hit_rate_pct": 14.3, "gross_breakeven_rate_pct": 20.0,
        "gross_r": -2.0, "fee_r": 1.232028, "net_r": -3.232028,
        "overlaps_after": 0}
    for name, row in table.items():
        assert row["filtered_trades"] <= row["original_trades"], name
        assert (row["filtered_trades"] + row["removed_trades"]
                == row["original_trades"]), name
        assert row["hits"] + row["stops"] + row["timeouts"] == (
            row["filtered_trades"]), name
        assert row["gross_r"] < 0, name
        assert row["net_r"] < 0, name
        assert row["net_r"] == round(
            row["gross_r"] - row["fee_r"], 6), name
        assert row["hit_rate_pct"] < row["gross_breakeven_rate_pct"], name
        assert row["overlaps_after"] == 0, name


def test_comparison_to_unfiltered_frozen():
    comparison = rj4.COMPARISON_TO_UNFILTERED
    assert comparison["2r"] == {"unfiltered_net_r": -11.666507,
                                "filtered_net_r": -3.29908}
    assert comparison["3r"] == {"unfiltered_net_r": -18.666507,
                                "filtered_net_r": -4.232028}
    assert comparison["4r"] == {"unfiltered_net_r": -16.666507,
                                "filtered_net_r": -3.232028}
    for name in ("2r", "3r", "4r"):
        pair = comparison[name]
        assert pair["filtered_net_r"] > pair["unfiltered_net_r"], name
        assert pair["filtered_net_r"] < 0, name
    statements = comparison["statements"]
    assert any("did not turn the candidate positive" in s
               for s in statements)
    assert any("amplifying the failure, not causing it" in s
               for s in statements)
    assert any("below gross breakeven" in s for s in statements)


def test_rejection_constants_and_facts():
    assert rj4.REJECTION_STATUS == "REJECTED_KEPT_ON_RECORD"
    assert rj4.REJECTION_REASON == (
        "EDGE_FAILURE_SURVIVED_ONE_AUTHORIZED_FILTER_ONLY_EDIT")
    assert rj4.FILTER_CLASSIFICATION == (
        "C4_FILTER_ONLY_EDIT_FAILED_REJECT_NEXT")
    assert rj4.VERDICT_RJ4_RECORDED == (
        "C4_REJECTED_KEPT_ON_RECORD_EDGE_FAILURE_SURVIVED_ONE"
        "_AUTHORIZED_FILTER_ONLY_EDIT")
    facts = rj4.REJECTION_FACTS
    assert "candidate #4 is rejected" in facts
    assert "rejection is kept on record" in facts
    assert "reason: edge failure, not cost failure" in facts
    assert any("gross-negative before filter" in f for f in facts)
    assert any("gross-negative after filter" in f for f in facts)
    assert any("net-negative before and after" in f for f in facts)
    assert any("spent and failed" in f for f in facts)
    assert "no paper approval" in facts
    assert "no live approval" in facts
    assert "no profitability claim permitted" in facts
    validity = rj4.FILTER_VALIDITY_FACTS
    assert any("same-symbol no-overlap/cooldown" in f for f in validity)
    assert any("reduced-or-equal" in f for f in validity)
    assert any("no new trades" in f for f in validity)
    assert any("entries not weakened" in f for f in validity)
    assert any("union removed equals the original 22" in f
               for f in validity)
    symbol_facts = rj4.FROZEN_SYMBOL_FACTS
    assert any("btc kept 3 trades, 0 hits" in f for f in symbol_facts)
    assert any("noise-level" in f for f in symbol_facts)


def test_seeds_for_future_families_only():
    seeds = rj4.SEEDS_FOR_FUTURE_FAMILIES_ONLY
    assert len(seeds) == 5
    assert seeds[0].startswith("same_symbol_no_overlap_cooldown")
    assert "not_as_rescue_after_failure" in seeds[1]
    assert "cannot_be_promoted" in seeds[2]
    assert "not_evidence_of_edge" in seeds[3]
    assert "failure_mode_lessons" in seeds[4]
    assert rj4.SEEDS_ARE_NEVER_RESCUE_PATHS is True


def test_record_tampering_invalidates():
    record = rj4.build_c4_rejection_record(REPO_ROOT, tracked_paths=[])
    for field, value in (
            ("rejection_status", "ACCEPTED"),
            ("rejection_reason", "NONE"),
            ("filter_classification", "C4_FILTER_ONLY_EDIT_POSITIVE"),
            ("expected_filter_eval_sha256", "00" * 32),
            ("expected_filtered_variants", {}),
            ("comparison_to_unfiltered", {}),
            ("upstream_frozen_facts", {}),
            ("filter_validity_facts", []),
            ("frozen_symbol_facts", []),
            ("rejection_facts", []),
            ("seeds_for_future_families_only", []),
            ("seeds_are_never_rescue_paths", False),
            ("edit_allowance_spent", False),
            ("candidate_4_may_continue_as_is", True),
            ("candidate_4_may_receive_another_edit", True),
            ("further_replays_authorized", True),
            ("claims_profitability", True),
            ("authorizes_paper_execution", True),
            ("authorizes_live_trading", True),
            ("live_gate_locked", False)):
        tampered = rj4.build_c4_rejection_record(REPO_ROOT,
                                                 tracked_paths=[])
        tampered[field] = value
        assert rj4.validate_c4_rejection_record(
            tampered)["valid"] is False, field


def test_real_artifact_certifies_when_present():
    import pathlib
    if not (pathlib.Path(REPO_ROOT) / rj4.FILTER_EVAL_PATH).is_file():
        pytest.skip("candidate #4 filter eval artifact not present")
    record = rj4.build_c4_rejection_record(REPO_ROOT, tracked_paths=[])
    assert record["verdict"] == rj4.VERDICT_RJ4_RECORDED
    assert record["failures"] == []
    assert rj4.validate_c4_rejection_record(record)["valid"] is True


def test_replay_review_live_and_ledger_intact():
    import sparta_commander.sol_btc_long_1h_swing_structure_replay_results_review_contract as c4rr
    review = c4rr.build_c4_replay_results_review(REPO_ROOT,
                                                 tracked_paths=[])
    assert review["verdict"] == c4rr.VERDICT_C4RR_FROZEN
    from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
        REJECTION_STATUS as C1)
    from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (
        REJECTION_STATUS as C2)
    from sparta_commander.btc_sol_long_trend_continuation_v1_result_and_rejection_record_contract import (
        REJECTION_STATUS as C3)
    assert C1 == C2 == C3 == "REJECTED_KEPT_ON_RECORD"
    record = rj4.build_c4_rejection_record(REPO_ROOT, tracked_paths=[])
    assert record["verdict"] != rj4.VERDICT_RJ4_BLOCKED
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
    assert record["edit_allowance_spent"] is True


def test_label_action_and_module_purity():
    assert rj4.get_c4_rejection_record_label() == rj4.RJ4_LABEL
    assert "READ-ONLY" in rj4.RJ4_LABEL
    assert "REJECTED KEPT ON RECORD" in rj4.RJ4_LABEL
    assert rj4.RJ4_MODE == "RESEARCH_ONLY"
    assert rj4.NEXT_REQUIRED_ACTION == (
        "HUMAN_DECISION_ON_NEXT_CANDIDATE_FAMILY")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in rj4.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(rj4.__file__, encoding="utf-8").read()
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
                   "datetime", "statistics"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
    assert not any(
        call.func.attr == "open" if isinstance(call.func, ast.Attribute)
        else getattr(call.func, "id", "") == "open"
        for call in ast.walk(tree) if isinstance(call, ast.Call))
