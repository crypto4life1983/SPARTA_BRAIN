"""Tests for the Candidate #5 informational replay results review.

Certify logic proven on synthetic observations for every failure mode;
real-artifact certification; tamper tests on every frozen block;
information-only and edit-unspent locks; commander safety suite runs
alongside."""

from __future__ import annotations

import ast
import copy

import pytest

import sparta_commander.eth_sol_relative_strength_replay_results_review_contract as c5rr

REPO_ROOT = "C:/SPARTA_BRAIN"


def _good_observation():
    return {
        "results_exists": True, "summary_exists": True,
        "results_sha256": c5rr.EXPECTED_RESULTS_SHA256,
        "summary_sha256": c5rr.EXPECTED_SUMMARY_SHA256,
        "row_count": 6,
        "setup_ids": tuple(sorted(c5rr.EXPECTED_SETUP_IDS)),
        "skipped_count": 0,
        "variants": copy.deepcopy(c5rr.EXPECTED_VARIANTS),
        "per_symbol": copy.deepcopy(c5rr.EXPECTED_PER_SYMBOL),
        "best_worst": copy.deepcopy(c5rr.EXPECTED_BEST_WORST),
        "removed_ids_by_variant": {
            "2r": [c5rr.EXPECTED_REMOVED_SETUP_ID],
            "3r": [c5rr.EXPECTED_REMOVED_SETUP_ID],
            "4r": [c5rr.EXPECTED_REMOVED_SETUP_ID]},
        "all_variants_net_negative": True,
        "gross_positive_2r": True,
        "gross_flat_4r": True,
        "artifacts_tracked_in_git": [],
    }


def test_certify_passes_on_expected_observation():
    result = c5rr.certify_c5_replay_results(_good_observation())
    assert result["certified"] is True
    assert result["failures"] == []


def test_certify_failure_modes():
    cases = (
        ({"results_exists": False}, "results_artifact_missing"),
        ({"summary_exists": False}, "summary_artifact_missing"),
        ({"results_sha256": "00" * 32}, "results_sha_mismatch"),
        ({"summary_sha256": "00" * 32}, "summary_sha_mismatch"),
        ({"row_count": 5}, "row_count_not_6"),
        ({"setup_ids": ("X",)}, "setup_ids_mismatch"),
        ({"skipped_count": 1}, "skipped_count_not_zero"),
        ({"all_variants_net_negative": False},
         "net_negative_fact_broken"),
        ({"gross_positive_2r": False}, "gross_positive_2r_fact_broken"),
        ({"gross_flat_4r": False}, "gross_flat_4r_fact_broken"),
        ({"artifacts_tracked_in_git": [c5rr.RUNNER_PATH]},
         "runner_and_artifacts_must_stay_untracked"),
    )
    for override, expected_failure in cases:
        observation = _good_observation()
        observation.update(override)
        result = c5rr.certify_c5_replay_results(observation)
        assert result["certified"] is False, expected_failure
        assert expected_failure in result["failures"], expected_failure
    # arithmetic tampers: net/gross/fee/hits/stops/timeouts per variant
    for variant, key, value, expected in (
            ("2r", "net_r", 0.5, "variant_fact_mismatch:2r:net_r"),
            ("3r", "gross_r", 1.0, "variant_fact_mismatch:3r:gross_r"),
            ("4r", "fee_r", 0.1, "variant_fact_mismatch:4r:fee_r"),
            ("2r", "hits", 3, "variant_fact_mismatch:2r:hits"),
            ("3r", "stops", 3, "variant_fact_mismatch:3r:stops"),
            ("4r", "timeouts", 1, "variant_fact_mismatch:4r:timeouts"),
            ("2r", "kept", 6, "variant_fact_mismatch:2r:kept")):
        observation = _good_observation()
        observation["variants"][variant][key] = value
        result = c5rr.certify_c5_replay_results(observation)
        assert expected in result["failures"], expected
    bad_removed = _good_observation()
    bad_removed["removed_ids_by_variant"]["3r"] = []
    assert "non_overlap_removal_mismatch:3r" in (
        c5rr.certify_c5_replay_results(bad_removed)["failures"])
    bad_split = _good_observation()
    bad_split["per_symbol"]["SOLUSD"]["net_r"]["2r"] = 0.0
    assert "per_symbol_mismatch" in c5rr.certify_c5_replay_results(
        bad_split)["failures"]
    bad_bw = _good_observation()
    bad_bw["best_worst"]["2r"]["best"]["net_r"] = 9.9
    assert "best_worst_mismatch" in c5rr.certify_c5_replay_results(
        bad_bw)["failures"]
    assert c5rr.certify_c5_replay_results(None)["certified"] is False


def test_frozen_variant_table_exact_and_consistent():
    table = c5rr.EXPECTED_VARIANTS
    assert table["2r"]["gross_r"] == 1.000001      # gross-positive
    assert table["2r"]["net_r"] == -0.269641       # net-negative
    assert table["3r"]["gross_r"] == -0.999999
    assert table["3r"]["net_r"] == -2.269641
    assert table["4r"]["gross_r"] == 0.000001      # gross-flat
    assert table["4r"]["net_r"] == -1.269641
    for name, row in table.items():
        assert row["frozen_labels"] == 6, name
        assert row["replayed"] == 6, name
        assert row["kept"] == 5, name
        assert row["removed"] == 1, name
        assert row["hits"] + row["stops"] + row["timeouts"] == 5, name
        assert row["net_r"] < 0, name              # all net-negative
        assert row["net_r"] == round(
            row["gross_r"] - row["fee_r"], 6), name
        assert row["fee_r"] == 1.269642, name
    assert table["2r"]["hit_rate_pct"] == 40.0
    assert table["2r"]["hit_rate_pct"] > (
        table["2r"]["gross_breakeven_rate_pct"])   # above breakeven
    assert table["3r"]["hit_rate_pct"] < (
        table["3r"]["gross_breakeven_rate_pct"])
    assert table["4r"]["hit_rate_pct"] == (
        table["4r"]["gross_breakeven_rate_pct"])


def test_frozen_setup_ids_and_non_overlap_removal():
    assert c5rr.EXPECTED_SETUP_IDS == (
        "ETHUSD_2026-05-13T08:00:00Z",
        "ETHUSD_2026-05-24T01:00:00Z",
        "ETHUSD_2026-05-25T14:00:00Z",
        "SOLUSD_2026-05-06T01:00:00Z",
        "SOLUSD_2026-05-06T06:00:00Z",
        "SOLUSD_2026-05-09T01:00:00Z")
    assert c5rr.EXPECTED_REMOVED_SETUP_ID == (
        "SOLUSD_2026-05-06T06:00:00Z")
    assert c5rr.EXPECTED_REMOVED_SETUP_ID in c5rr.EXPECTED_SETUP_IDS
    facts = c5rr.FROZEN_REPLAY_FACTS
    assert any("zero skipped" in fact for fact in facts)
    assert any("removed in all variants" in fact for fact in facts)
    assert any("removed a winner" in fact
               and "honest cost" in fact for fact in facts)
    assert any("kept set size 5 and removed set size 1" in fact
               for fact in facts)
    assert any("thinnest 75.6 bps risk" in fact for fact in facts)


def test_frozen_per_symbol_and_best_worst():
    split = c5rr.EXPECTED_PER_SYMBOL
    assert split["ETHUSD"]["trades"] == 3
    assert split["SOLUSD"]["trades"] == 2
    assert split["ETHUSD"]["net_r"] == {
        "2r": -3.861515, "3r": -3.861515, "4r": -3.861515}
    assert split["ETHUSD"]["hits"] == {"2r": 0, "3r": 0, "4r": 0}
    assert split["SOLUSD"]["net_r"] == {
        "2r": 3.591874, "3r": 1.591874, "4r": 2.591874}
    assert split["SOLUSD"]["hits"] == {"2r": 2, "3r": 1, "4r": 1}
    for name in ("2r", "3r", "4r"):
        assert round(split["ETHUSD"]["net_r"][name]
                     + split["SOLUSD"]["net_r"][name], 6) == (
            c5rr.EXPECTED_VARIANTS[name]["net_r"])
        assert (split["ETHUSD"]["hits"][name]
                + split["SOLUSD"]["hits"][name]) == (
            c5rr.EXPECTED_VARIANTS[name]["hits"])
    bw = c5rr.EXPECTED_BEST_WORST
    assert bw["2r"]["best"] == {
        "setup_id": "SOLUSD_2026-05-09T01:00:00Z", "net_r": 1.858159}
    assert bw["3r"]["best"] == {
        "setup_id": "SOLUSD_2026-05-06T01:00:00Z", "net_r": 2.733715}
    assert bw["4r"]["best"]["net_r"] == 3.733715
    for name in ("2r", "3r", "4r"):
        assert bw[name]["worst"] == {
            "setup_id": "ETHUSD_2026-05-25T14:00:00Z",
            "net_r": -1.357148}


def test_classification_facts_and_seeds():
    assert c5rr.CLASSIFICATION == (
        "C5_REPLAY_SMALL_SAMPLE_NEGATIVE_REJECT_OR_EDIT_DECISION")
    facts = c5rr.FROZEN_CLASSIFICATION_FACTS
    assert "all variants net-negative" in facts
    assert "2r is gross-positive but net-negative" in facts
    assert "4r is gross-flat but net-negative" in facts
    assert any("only 5 kept trades" in fact for fact in facts)
    assert any("noise-level" in fact for fact in facts)
    assert any("cannot promote" in fact and "profitability claim" in fact
               for fact in facts)
    assert any("single pre-committed edit remains unspent" in fact
               for fact in facts)
    assert any("human decision" in fact for fact in facts)
    assert any("372/411" in fact and "pullback_too_long" in fact
               for fact in facts)
    assert any("2 sol trades from one week" in fact
               and "eth contributed only stops" in fact
               for fact in facts)
    seeds = c5rr.SEED_OBSERVATIONS_NOT_CLAIMS
    assert "sol_side_rs_strength_recurs_across_c4_and_c5" in seeds
    assert "thin_risk_fee_sensitivity_matters" in seeds
    assert "dedup_can_remove_winners" in seeds
    assert ("eth_side_contribution_was_negative_in_this_sample"
            in seeds)


def test_real_artifacts_certify_when_present():
    import pathlib
    if not (pathlib.Path(REPO_ROOT) / c5rr.RESULTS_PATH).is_file():
        pytest.skip("candidate #5 replay artifacts not present")
    record = c5rr.build_c5_replay_results_review(REPO_ROOT,
                                                 tracked_paths=[])
    assert record["verdict"] == c5rr.VERDICT_C5RR_FROZEN
    assert record["failures"] == []
    assert c5rr.validate_c5_replay_results_review(record)["valid"] is True


def test_record_tampering_invalidates():
    record = c5rr.build_c5_replay_results_review(REPO_ROOT,
                                                 tracked_paths=[])
    for field, value in (
            ("classification", "C5_REPLAY_POSITIVE"),
            ("head_at_replay", "00" * 20),
            ("expected_results_sha256", "00" * 32),
            ("expected_summary_sha256", "00" * 32),
            ("labels_artifact_sha256", "00" * 32),
            ("labels_summary_sha256", "00" * 32),
            ("expected_setup_ids", ["X"]),
            ("expected_removed_setup_id", "NONE"),
            ("expected_variants", {}),
            ("expected_per_symbol", {}),
            ("expected_best_worst", {}),
            ("frozen_replay_facts", []),
            ("frozen_classification_facts", []),
            ("seed_observations_not_claims", []),
            ("information_only_no_promotion_possible", False),
            ("edit_allowance_unspent", False),
            ("edit_or_reject_is_human_decision", False),
            ("claims_profitability", True),
            ("authorizes_paper_execution", True),
            ("live_gate_locked", False),
            ("verdict", "C5_APPROVED_FOR_TRADING")):
        tampered = c5rr.build_c5_replay_results_review(
            REPO_ROOT, tracked_paths=[])
        tampered[field] = value
        assert c5rr.validate_c5_replay_results_review(
            tampered)["valid"] is False, field
    frozen_with_failures = c5rr.build_c5_replay_results_review(
        REPO_ROOT, tracked_paths=[])
    frozen_with_failures["failures"] = ["fake"]
    assert c5rr.validate_c5_replay_results_review(
        frozen_with_failures)["valid"] is False


def test_chain_gate_information_only_and_capabilities():
    import sparta_commander.eth_sol_relative_strength_real_candle_labels_review_contract as c5l
    import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as ap
    assert c5l.build_c5_labels_review(REPO_ROOT, tracked_paths=[])[
        "verdict"] == (
        "CANDIDATE_5_REAL_CANDLE_LABELS_FROZEN_READY_FOR_HUMAN_REVIEW")
    assert ap.build_autopilot_loop_contract()["verdict"] == (
        "STRATEGY_FACTORY_AUTOPILOT_RESEARCH_LOOP_V1_READY")
    from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
        REJECTION_STATUS as C1)
    from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (
        REJECTION_STATUS as C2)
    from sparta_commander.btc_sol_long_trend_continuation_v1_result_and_rejection_record_contract import (
        REJECTION_STATUS as C3)
    from sparta_commander.sol_btc_long_1h_swing_structure_rejection_record_contract import (
        REJECTION_STATUS as C4)
    assert C1 == C2 == C3 == C4 == "REJECTED_KEPT_ON_RECORD"
    record = c5rr.build_c5_replay_results_review(REPO_ROOT,
                                                 tracked_paths=[])
    assert record["verdict"] != c5rr.VERDICT_C5RR_BLOCKED
    assert record["information_only_no_promotion_possible"] is True
    assert record["edit_allowance_unspent"] is True
    assert record["edit_or_reject_is_human_decision"] is True
    for key in ("executes", "writes_files", "labels_now",
                "runs_real_detection_now", "runs_replay_now",
                "scores_now", "stages_data_now", "fetches_data",
                "calls_api", "uses_network", "uses_credentials",
                "uses_wallet", "uses_account", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "auto_commits", "auto_pushes",
                "creates_runners_now", "creates_data_artifacts_now",
                "modifies_staged_market_data",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate", "claims_profitability"):
        assert record[key] is False, key
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True


def test_label_action_and_module_purity():
    assert c5rr.get_c5_replay_review_label() == c5rr.C5RR_LABEL
    assert "READ-ONLY" in c5rr.C5RR_LABEL
    assert "SMALL SAMPLE" in c5rr.C5RR_LABEL
    assert "NOT A PROFITABILITY CLAIM" in c5rr.C5RR_LABEL
    assert c5rr.C5RR_MODE == "RESEARCH_ONLY"
    assert c5rr.VERDICT_C5RR_FROZEN == (
        "C5_REPLAY_RESULTS_REVIEW_INFORMATION_ONLY_FROZEN")
    assert c5rr.NEXT_REQUIRED_ACTION == (
        "HUMAN_DECISION_C5_EDIT_OR_REJECT_AFTER_REPLAY")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in c5rr.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(c5rr.__file__, encoding="utf-8").read()
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
