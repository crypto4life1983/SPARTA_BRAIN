"""Tests for the Candidate #4 replay results review / evidence freeze.

Certify logic proven on synthetic observations for every failure mode
(sha, arithmetic, counts, symbol split, best/worst, overlap warning,
zero-skip set equality, tracked-artifact violation); tamper tests on the
record; one real-artifact test certifies the live files when present."""

from __future__ import annotations

import ast
import copy

import pytest

import sparta_commander.sol_btc_long_1h_swing_structure_replay_results_review_contract as c4rr

REPO_ROOT = "C:/SPARTA_BRAIN"


def _good_observation():
    return {
        "results_exists": True, "summary_exists": True,
        "results_sha256": c4rr.EXPECTED_RESULTS_SHA256,
        "summary_sha256": c4rr.EXPECTED_SUMMARY_SHA256,
        "row_count": 22,
        "setup_ids_unique": True,
        "setup_ids_match_frozen_accepted_set": True,
        "variants": {
            "2r": {"hits": 5, "stops": 17, "timeouts": 0,
                   "hit_rate_pct": 22.7, "gross_r": -7.0,
                   "fee_r": 4.666507, "net_r": -11.666507},
            "3r": {"hits": 2, "stops": 20, "timeouts": 0,
                   "hit_rate_pct": 9.1, "gross_r": -14.0,
                   "fee_r": 4.666507, "net_r": -18.666507},
            "4r": {"hits": 2, "stops": 20, "timeouts": 0,
                   "hit_rate_pct": 9.1, "gross_r": -12.0,
                   "fee_r": 4.666507, "net_r": -16.666507}},
        "symbol_split": copy.deepcopy(c4rr.EXPECTED_SYMBOL_SPLIT),
        "best_worst": copy.deepcopy(c4rr.EXPECTED_BEST_WORST),
        "overlaps_per_variant": {"2r": 14, "3r": 14, "4r": 14},
        "all_variants_gross_negative": True,
        "all_variants_net_negative": True,
        "artifacts_tracked_in_git": [],
    }


def test_certify_passes_on_expected_observation():
    result = c4rr.certify_c4_replay_results(_good_observation())
    assert result["certified"] is True
    assert result["failures"] == []


def test_certify_failure_modes():
    cases = (
        ({"results_exists": False}, "results_artifact_missing"),
        ({"summary_exists": False}, "summary_artifact_missing"),
        ({"results_sha256": "00" * 32}, "results_sha_mismatch"),
        ({"summary_sha256": "00" * 32}, "summary_sha_mismatch"),
        ({"row_count": 21}, "row_count_not_22"),
        ({"setup_ids_unique": False}, "setup_ids_not_unique"),
        ({"setup_ids_match_frozen_accepted_set": False},
         "setup_ids_do_not_match_frozen_accepted_set"),
        ({"all_variants_gross_negative": False},
         "gross_negative_fact_broken"),
        ({"all_variants_net_negative": False},
         "net_negative_fact_broken"),
        ({"artifacts_tracked_in_git": [c4rr.RUNNER_PATH]},
         "runner_and_artifacts_must_stay_untracked"),
    )
    for override, expected_failure in cases:
        observation = _good_observation()
        observation.update(override)
        result = c4rr.certify_c4_replay_results(observation)
        assert result["certified"] is False, expected_failure
        assert expected_failure in result["failures"], expected_failure
    # arithmetic tamper: net R, hit counts, fee model
    for variant, key, value, expected in (
            ("2r", "net_r", -10.0, "variant_fact_mismatch:2r:net_r"),
            ("3r", "hits", 3, "variant_fact_mismatch:3r:hits"),
            ("4r", "fee_r", 1.0, "variant_fact_mismatch:4r:fee_r"),
            ("2r", "stops", 16, "variant_fact_mismatch:2r:stops")):
        observation = _good_observation()
        observation["variants"][variant][key] = value
        result = c4rr.certify_c4_replay_results(observation)
        assert expected in result["failures"], expected
    bad_split = _good_observation()
    bad_split["symbol_split"]["SOLUSD"]["net_r"]["2r"] = 0.0
    assert "symbol_split_mismatch" in c4rr.certify_c4_replay_results(
        bad_split)["failures"]
    bad_bw = _good_observation()
    bad_bw["best_worst"]["2r"]["best"]["net_r"] = 5.0
    assert "best_worst_mismatch" in c4rr.certify_c4_replay_results(
        bad_bw)["failures"]
    bad_overlap = _good_observation()
    bad_overlap["overlaps_per_variant"]["3r"] = 0
    assert "overlap_count_mismatch:3r" in c4rr.certify_c4_replay_results(
        bad_overlap)["failures"]
    assert c4rr.certify_c4_replay_results(None)["certified"] is False


def test_frozen_variant_table_exact():
    table = c4rr.EXPECTED_VARIANTS
    assert table["2r"] == {
        "hits": 5, "stops": 17, "timeouts": 0, "hit_rate_pct": 22.7,
        "gross_breakeven_rate_pct": 33.3, "gross_r": -7.0,
        "fee_r": 4.666507, "net_r": -11.666507}
    assert table["3r"] == {
        "hits": 2, "stops": 20, "timeouts": 0, "hit_rate_pct": 9.1,
        "gross_breakeven_rate_pct": 25.0, "gross_r": -14.0,
        "fee_r": 4.666507, "net_r": -18.666507}
    assert table["4r"] == {
        "hits": 2, "stops": 20, "timeouts": 0, "hit_rate_pct": 9.1,
        "gross_breakeven_rate_pct": 20.0, "gross_r": -12.0,
        "fee_r": 4.666507, "net_r": -16.666507}
    for name, row in table.items():
        assert row["hits"] + row["stops"] + row["timeouts"] == 22, name
        assert row["gross_r"] < 0, name      # edge failure
        assert row["net_r"] < 0, name        # net failure
        assert row["net_r"] == round(
            row["gross_r"] - row["fee_r"], 6), name
        assert row["hit_rate_pct"] < row["gross_breakeven_rate_pct"], name


def test_frozen_symbol_split_and_best_worst():
    split = c4rr.EXPECTED_SYMBOL_SPLIT
    assert split["SOLUSD"]["trades"] == 12
    assert split["BTCUSD"]["trades"] == 10
    assert split["SOLUSD"]["trades"] + split["BTCUSD"]["trades"] == 22
    assert split["SOLUSD"]["net_r"] == {
        "2r": -2.396186, "3r": -6.396186, "4r": -4.396186}
    assert split["BTCUSD"]["net_r"] == {
        "2r": -9.270321, "3r": -12.270321, "4r": -12.270321}
    assert split["SOLUSD"]["hits"] == {"2r": 4, "3r": 2, "4r": 2}
    assert split["BTCUSD"]["hits"] == {"2r": 1, "3r": 0, "4r": 0}
    for name in ("2r", "3r", "4r"):
        per_variant = c4rr.EXPECTED_VARIANTS[name]
        assert (split["SOLUSD"]["hits"][name]
                + split["BTCUSD"]["hits"][name]) == per_variant["hits"]
        assert round(split["SOLUSD"]["net_r"][name]
                     + split["BTCUSD"]["net_r"][name], 6) == (
            per_variant["net_r"])
    bw = c4rr.EXPECTED_BEST_WORST
    assert bw["2r"]["best"] == {
        "setup_id": "SOLUSD_2026-05-08T23:00:00Z", "net_r": 1.858159}
    assert bw["3r"]["best"] == {
        "setup_id": "SOLUSD_2026-05-05T16:00:00Z", "net_r": 2.843273}
    assert bw["4r"]["best"]["net_r"] == 3.843273
    assert bw["2r"]["worst"]["setup_id"] == (
        "SOLUSD_2026-05-30T08:00:00Z")
    assert bw["3r"]["worst"]["setup_id"] == (
        "BTCUSD_2026-05-09T07:00:00Z")


def test_frozen_rules_warnings_and_upstream():
    rules = c4rr.FROZEN_REPLAY_RULES
    assert any("27 bps round-trip" in rule for rule in rules)
    assert any("trigger candle close" in rule for rule in rules)
    assert any("next 1h bar" in rule for rule in rules)
    assert any("stop-before-target" in rule for rule in rules)
    assert any("adverse gaps" in rule for rule in rules)
    assert any("capped at the target" in rule for rule in rules)
    assert any("last available close" in rule for rule in rules)
    assert any("pushed" in rule and "aggregator" in rule for rule in rules)
    assert any("zero skipped" in rule for rule in rules)
    warnings = c4rr.FROZEN_WARNINGS
    assert any("14 of 22" in warning for warning in warnings)
    assert any("EDGE FAILURE" in warning for warning in warnings)
    assert any("zero-fee replay would still be negative" in warning
               for warning in warnings)
    assert any("candidate #2" in warning for warning in warnings)
    assert any("no paper or live" in warning for warning in warnings)
    assert any("no profitability claim" in warning for warning in warnings)
    upstream = c4rr.UPSTREAM_FROZEN_FACTS
    assert upstream["labels_review_commit"] == (
        "8cf8136aef277b92cc780960aa6c20be3a581376")
    assert upstream["accepted_count"] == 22
    assert upstream["label_recount"] == 275
    assert upstream["replay_has_run_was_false_before_replay_gate"] is True
    assert upstream["zero_skips_in_replay"] is True
    assert c4rr.EXPECTED_OVERLAPS_PER_VARIANT == 14


def test_record_tampering_invalidates():
    record = c4rr.build_c4_replay_results_review(REPO_ROOT,
                                                 tracked_paths=[])
    for field, value in (
            ("expected_results_sha256", "00" * 32),
            ("expected_summary_sha256", "00" * 32),
            ("expected_variants", {}),
            ("expected_symbol_split", {}),
            ("expected_best_worst", {}),
            ("expected_overlaps_per_variant", 0),
            ("frozen_replay_rules", []),
            ("frozen_warnings", []),
            ("upstream_frozen_facts", {}),
            ("failure_classification", "COST_FAILURE"),
            ("single_filter_only_edit_allowance_unspent", False),
            ("edit_or_reject_is_human_decision", False),
            ("claims_profitability", True),
            ("revives_candidate_3", True),
            ("live_gate_locked", False)):
        tampered = c4rr.build_c4_replay_results_review(
            REPO_ROOT, tracked_paths=[])
        tampered[field] = value
        assert c4rr.validate_c4_replay_results_review(
            tampered)["valid"] is False, field
    fake_verdict = c4rr.build_c4_replay_results_review(
        REPO_ROOT, tracked_paths=[])
    fake_verdict["verdict"] = "SOMETHING_POSITIVE"
    assert c4rr.validate_c4_replay_results_review(
        fake_verdict)["valid"] is False


def test_real_artifacts_certify_when_present():
    import pathlib
    if not (pathlib.Path(REPO_ROOT) / c4rr.RESULTS_PATH).is_file():
        pytest.skip("candidate #4 replay artifacts not present")
    record = c4rr.build_c4_replay_results_review(REPO_ROOT,
                                                 tracked_paths=[])
    assert record["verdict"] == c4rr.VERDICT_C4RR_FROZEN
    assert record["failures"] == []
    assert c4rr.validate_c4_replay_results_review(record)["valid"] is True


def test_ledger_gate_and_capabilities():
    from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
        REJECTION_STATUS as C1)
    from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (
        REJECTION_STATUS as C2)
    from sparta_commander.btc_sol_long_trend_continuation_v1_result_and_rejection_record_contract import (
        REJECTION_STATUS as C3)
    assert C1 == C2 == C3 == "REJECTED_KEPT_ON_RECORD"
    record = c4rr.build_c4_replay_results_review(REPO_ROOT,
                                                 tracked_paths=[])
    assert record["verdict"] != c4rr.VERDICT_C4RR_BLOCKED
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
    assert record["single_filter_only_edit_allowance_unspent"] is True
    assert record["edit_or_reject_is_human_decision"] is True


def test_label_action_and_module_purity():
    assert c4rr.get_c4_replay_review_label() == c4rr.C4RR_LABEL
    assert "READ-ONLY" in c4rr.C4RR_LABEL
    assert "NOT A PROFITABILITY CLAIM" in c4rr.C4RR_LABEL
    assert c4rr.C4RR_MODE == "RESEARCH_ONLY"
    assert c4rr.VERDICT_C4RR_FROZEN == (
        "C4_REPLAY_RESULTS_REVIEW_CONTRACT_FROZEN_REJECTION_PRESSURE")
    assert c4rr.NEXT_REQUIRED_ACTION == (
        "HUMAN_DECISION_C4_FILTER_ONLY_EDIT_OR_REJECT")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in c4rr.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(c4rr.__file__, encoding="utf-8").read()
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
