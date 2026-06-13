"""Tests for the Candidate #6 informational replay results review.

Certify logic proven on synthetic observations for every failure mode;
real-artifact certification; tamper tests on every frozen block;
edit/rejection/paper/live/profitability locks; commander safety suite
runs alongside."""

from __future__ import annotations

import ast
import copy

import pytest

import sparta_commander.multi_symbol_relative_strength_rotation_filter_replay_results_review_contract as c6rr

REPO_ROOT = "C:/SPARTA_BRAIN"


def _good_observation():
    return {
        "results_exists": True, "summary_exists": True,
        "results_sha256": c6rr.EXPECTED_RESULTS_SHA256,
        "summary_sha256": c6rr.EXPECTED_SUMMARY_SHA256,
        "row_count": 135,
        "setup_ids": tuple(sorted(
            __import__(
                "sparta_commander.multi_symbol_relative_strength_rotation"
                "_filter_real_candle_labels_review_contract",
                fromlist=["EXPECTED_ACCEPTED_SETUP_IDS"]
            ).EXPECTED_ACCEPTED_SETUP_IDS)),
        "skipped_count": 0,
        "variants": copy.deepcopy(c6rr.EXPECTED_VARIANTS),
        "per_symbol": copy.deepcopy(c6rr.EXPECTED_PER_SYMBOL),
        "overlap_skipped_total":
            c6rr.EXPECTED_OVERLAP_SKIPPED_TOTAL,
        "all_variants_net_negative": True,
        "all_variants_gross_negative": True,
        "all_hit_rates_below_breakeven": True,
        "max_drawdown_exceeds_net_loss_per_variant": True,
        "summary_honest_verdict": c6rr.HONEST_VERDICT,
        "artifacts_tracked_in_git": [],
    }


def test_1_certify_passes_on_expected_observation():
    result = c6rr.certify_c6_replay_results(_good_observation())
    assert result["certified"] is True
    assert result["failures"] == []


def test_2_input_label_summary_shas_validated():
    inputs = c6rr.EXPECTED_INPUTS
    assert inputs["labels_sha256"] == (
        "bc8471fc78bbfe409b5cb0efa951608cddd73f3485d66dbd8d711bb1f4307"
        "d7a")
    assert inputs["summary_sha256"] == (
        "110b84b2ad96de5136d1a89da4ef26f2fbd1b4a0f45527f5e0f1a0c612fc"
        "18c7")
    assert inputs["accepted_count_BTCUSD"] == 32
    assert inputs["accepted_count_ETHUSD"] == 32
    assert inputs["accepted_count_SOLUSD"] == 71
    assert inputs["accepted_count_total"] == 135
    assert (inputs["accepted_count_BTCUSD"]
            + inputs["accepted_count_ETHUSD"]
            + inputs["accepted_count_SOLUSD"]) == 135


def test_3_replay_artifact_shas_validated():
    assert c6rr.EXPECTED_RESULTS_SHA256 == (
        "587da03b6351084fe33ea5c9ba17456feca8049eb5d135ca19eede26df911"
        "415")
    assert c6rr.EXPECTED_SUMMARY_SHA256 == (
        "8014bc3086310f14007ae8c10898ea7d06af9fbcfb6d287b6b315651f6721"
        "28a")
    bad = _good_observation()
    bad["results_sha256"] = "00" * 32
    assert "results_sha_mismatch" in c6rr.certify_c6_replay_results(
        bad)["failures"]
    bad2 = _good_observation()
    bad2["summary_sha256"] = "00" * 32
    assert "summary_sha_mismatch" in c6rr.certify_c6_replay_results(
        bad2)["failures"]


def test_4_5_6_per_variant_arithmetic_exact():
    table = c6rr.EXPECTED_VARIANTS
    assert table["2r"] == {
        "eligible_setups": 135, "skipped_overlap": 109, "kept": 26,
        "hits": 6, "stops": 18, "timeouts": 2,
        "hit_rate_pct": 23.1, "gross_breakeven_rate_pct": 33.3,
        "gross_r_total": -6.666284, "fee_r_total": 4.419006,
        "net_r_total": -11.085290, "avg_net_r": -0.426357,
        "max_drawdown_r": -17.407087}
    assert table["3r"] == {
        "eligible_setups": 135, "skipped_overlap": 111, "kept": 24,
        "hits": 4, "stops": 18, "timeouts": 2,
        "hit_rate_pct": 16.7, "gross_breakeven_rate_pct": 25.0,
        "gross_r_total": -6.666284, "fee_r_total": 4.179845,
        "net_r_total": -10.846129, "avg_net_r": -0.451922,
        "max_drawdown_r": -16.246386}
    assert table["4r"] == {
        "eligible_setups": 135, "skipped_overlap": 114, "kept": 21,
        "hits": 3, "stops": 16, "timeouts": 2,
        "hit_rate_pct": 14.3, "gross_breakeven_rate_pct": 20.0,
        "gross_r_total": -4.666284, "fee_r_total": 3.674705,
        "net_r_total": -8.340989, "avg_net_r": -0.39719,
        "max_drawdown_r": -16.246386}
    # internal consistency
    for name, row in table.items():
        assert row["hits"] + row["stops"] + row["timeouts"] == (
            row["kept"]), name
        assert row["eligible_setups"] == row["skipped_overlap"] + row[
            "kept"], name
        assert row["net_r_total"] < 0, name
        assert row["gross_r_total"] < 0, name
        assert row["hit_rate_pct"] < row["gross_breakeven_rate_pct"], (
            name)
        assert row["max_drawdown_r"] < row["net_r_total"], name
    # per-variant tampers
    for variant, key, value, expected in (
            ("2r", "net_r_total", 0.0,
             "variant_fact_mismatch:2r:net_r_total"),
            ("3r", "gross_r_total", 1.0,
             "variant_fact_mismatch:3r:gross_r_total"),
            ("4r", "hits", 5, "variant_fact_mismatch:4r:hits"),
            ("2r", "skipped_overlap", 100,
             "variant_fact_mismatch:2r:skipped_overlap"),
            ("3r", "max_drawdown_r", 0.0,
             "variant_fact_mismatch:3r:max_drawdown_r")):
        observation = _good_observation()
        observation["variants"][variant][key] = value
        result = c6rr.certify_c6_replay_results(observation)
        assert expected in result["failures"], expected


def test_7_per_symbol_breakdown_exact():
    split = c6rr.EXPECTED_PER_SYMBOL
    assert split["BTCUSD"] == {
        "2r_trades": 5, "2r_net": -5.409106,
        "3r_trades": 5, "3r_net": -5.409106,
        "4r_trades": 5, "4r_net": -5.409106}
    assert split["ETHUSD"] == {
        "2r_trades": 12, "2r_net": -2.447441,
        "3r_trades": 10, "3r_net": -4.122745,
        "4r_trades": 9, "4r_net": -0.946154}
    assert split["SOLUSD"] == {
        "2r_trades": 9, "2r_net": -3.228743,
        "3r_trades": 9, "3r_net": -1.314278,
        "4r_trades": 7, "4r_net": -1.985729}
    # trade-count reconciliation against the kept totals
    for name in ("2r", "3r", "4r"):
        assert (split["BTCUSD"][name + "_trades"]
                + split["ETHUSD"][name + "_trades"]
                + split["SOLUSD"][name + "_trades"]
                ) == c6rr.EXPECTED_VARIANTS[name]["kept"], name
        assert round(split["BTCUSD"][name + "_net"]
                     + split["ETHUSD"][name + "_net"]
                     + split["SOLUSD"][name + "_net"], 6) == (
            c6rr.EXPECTED_VARIANTS[name]["net_r_total"]), name
    bad = _good_observation()
    bad["per_symbol"]["BTCUSD"]["2r_net"] = 5.0
    assert "per_symbol_mismatch" in c6rr.certify_c6_replay_results(
        bad)["failures"]


def test_8_9_10_negativity_and_hit_rates():
    for name, row in c6rr.EXPECTED_VARIANTS.items():
        assert row["net_r_total"] < 0, name
        assert row["gross_r_total"] < 0, name
        assert row["hit_rate_pct"] < row["gross_breakeven_rate_pct"], (
            name)
    bad_net = _good_observation()
    bad_net["all_variants_net_negative"] = False
    assert "net_negative_fact_broken" in c6rr.certify_c6_replay_results(
        bad_net)["failures"]
    bad_gross = _good_observation()
    bad_gross["all_variants_gross_negative"] = False
    assert "gross_negative_fact_broken" in (
        c6rr.certify_c6_replay_results(bad_gross)["failures"])
    bad_be = _good_observation()
    bad_be["all_hit_rates_below_breakeven"] = False
    assert "hit_rates_below_breakeven_fact_broken" in (
        c6rr.certify_c6_replay_results(bad_be)["failures"])


def test_11_12_overlap_skipped_counts_and_total():
    assert c6rr.EXPECTED_VARIANTS["2r"]["skipped_overlap"] == 109
    assert c6rr.EXPECTED_VARIANTS["3r"]["skipped_overlap"] == 111
    assert c6rr.EXPECTED_VARIANTS["4r"]["skipped_overlap"] == 114
    assert c6rr.EXPECTED_OVERLAP_SKIPPED_TOTAL == 109 + 111 + 114
    assert c6rr.EXPECTED_OVERLAP_SKIPPED_TOTAL == 334
    bad = _good_observation()
    bad["overlap_skipped_total"] = 333
    assert "overlap_skipped_total_mismatch" in (
        c6rr.certify_c6_replay_results(bad)["failures"])


def test_13_max_drawdown_values_exact_and_exceed_loss():
    table = c6rr.EXPECTED_VARIANTS
    assert table["2r"]["max_drawdown_r"] == -17.407087
    assert table["3r"]["max_drawdown_r"] == -16.246386
    assert table["4r"]["max_drawdown_r"] == -16.246386
    # mdd EXCEEDS net loss (both negative, mdd is deeper)
    for name in ("2r", "3r", "4r"):
        assert table[name]["max_drawdown_r"] < table[name][
            "net_r_total"], name
    bad = _good_observation()
    bad["max_drawdown_exceeds_net_loss_per_variant"] = False
    assert "max_drawdown_exceeds_net_loss_fact_broken" in (
        c6rr.certify_c6_replay_results(bad)["failures"])


def test_14_honest_verdict_exact():
    assert c6rr.HONEST_VERDICT == (
        "edge_failed_all_variants_net_negative")
    bad = _good_observation()
    bad["summary_honest_verdict"] = "edge_confirmed"
    assert "summary_honest_verdict_mismatch" in (
        c6rr.certify_c6_replay_results(bad)["failures"])


def test_15_review_fails_on_any_record_change():
    record = c6rr.build_c6_replay_results_review(
        REPO_ROOT, tracked_paths=[])
    for field, value in (
            ("honest_verdict", "edge_confirmed"),
            ("head_at_replay", "00" * 20),
            ("expected_results_sha256", "00" * 32),
            ("expected_summary_sha256", "00" * 32),
            ("expected_inputs", {}),
            ("expected_variants", {}),
            ("expected_per_symbol", {}),
            ("expected_overlap_skipped_total", 0),
            ("frozen_replay_rules", []),
            ("frozen_review_findings", []),
            ("claim_locks", []),
            ("edit_authorized_by_this_gate", True),
            ("rejection_decision_by_this_gate", True),
            ("structure_filter_modified_by_this_gate", True),
            ("detector_changed_by_this_gate", True),
            ("labels_changed_by_this_gate", True),
            ("replay_rerun_by_this_gate", True),
            ("claims_profitability", True),
            ("authorizes_paper_execution", True),
            ("authorizes_live_trading", True),
            ("live_gate_locked", False),
            ("verdict", "C6_APPROVED_FOR_TRADING")):
        tampered = c6rr.build_c6_replay_results_review(
            REPO_ROOT, tracked_paths=[])
        tampered[field] = value
        assert c6rr.validate_c6_replay_results_review(
            tampered)["valid"] is False, field
    frozen_with_failures = c6rr.build_c6_replay_results_review(
        REPO_ROOT, tracked_paths=[])
    frozen_with_failures["failures"] = ["fake"]
    assert c6rr.validate_c6_replay_results_review(
        frozen_with_failures)["valid"] is False


def test_16_edit_rejection_paper_live_profitability_locked():
    record = c6rr.build_c6_replay_results_review(
        REPO_ROOT, tracked_paths=[])
    assert record["edit_authorized_by_this_gate"] is False
    assert record["rejection_decision_by_this_gate"] is False
    assert record["structure_filter_modified_by_this_gate"] is False
    assert record["detector_changed_by_this_gate"] is False
    assert record["labels_changed_by_this_gate"] is False
    assert record["replay_rerun_by_this_gate"] is False
    locks = record["claim_locks"]
    for lock in ("no_edit_authorized_by_this_gate",
                 "no_rejection_decision_made_by_this_gate",
                 "no_paper_approval", "no_live_approval",
                 "no_execution_approval", "no_profitability_claim",
                 "no_winner_wording"):
        assert lock in locks, lock


def test_17_no_trading_adjacent_capability():
    record = c6rr.build_c6_replay_results_review(
        REPO_ROOT, tracked_paths=[])
    for key in ("executes", "writes_files", "labels_now",
                "runs_real_detection_now", "runs_replay_now",
                "scores_now", "stages_data_now", "fetches_data",
                "calls_api", "uses_network", "uses_credentials",
                "uses_wallet", "uses_account", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic",
                "contains_portfolio_allocation_logic",
                "starts_scheduler", "sends_notifications",
                "auto_commits", "auto_pushes", "creates_runners_now",
                "creates_data_artifacts_now",
                "modifies_staged_market_data",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate", "claims_profitability"):
        assert record[key] is False, key
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True


def test_real_artifacts_certify_when_present():
    import pathlib
    if not (pathlib.Path(REPO_ROOT) / c6rr.RESULTS_PATH).is_file():
        pytest.skip("candidate #6 replay artifacts not present")
    record = c6rr.build_c6_replay_results_review(
        REPO_ROOT, tracked_paths=[])
    assert record["verdict"] == c6rr.VERDICT_C6RR_FROZEN
    assert record["failures"] == []
    assert c6rr.validate_c6_replay_results_review(record)["valid"] is True


def test_chain_gate_and_runner_untracked():
    import sparta_commander.multi_symbol_relative_strength_rotation_filter_real_candle_labels_review_contract as c6l
    review = c6l.build_c6_labels_review(REPO_ROOT, tracked_paths=[])
    assert review["verdict"] == (
        "CANDIDATE_6_REAL_CANDLE_LABELS_FROZEN_READY_FOR_HUMAN_REVIEW")
    # certification fails if the runner becomes tracked
    bad = _good_observation()
    bad["artifacts_tracked_in_git"] = [c6rr.RUNNER_PATH]
    assert "runner_and_artifacts_must_stay_untracked" in (
        c6rr.certify_c6_replay_results(bad)["failures"])


def test_18_ast_purity_and_no_writers_or_runners():
    assert c6rr.get_c6_replay_review_label() == c6rr.C6RR_LABEL
    assert "READ-ONLY" in c6rr.C6RR_LABEL
    assert "ALL VARIANTS NET NEGATIVE" in c6rr.C6RR_LABEL
    assert "NOT A PROFITABILITY CLAIM" in c6rr.C6RR_LABEL
    assert c6rr.C6RR_MODE == "RESEARCH_ONLY"
    assert c6rr.VERDICT_C6RR_FROZEN == (
        "C6_REPLAY_RESULTS_REVIEW_INFORMATION_ONLY_FROZEN")
    assert c6rr.NEXT_REQUIRED_ACTION == (
        "HUMAN_DECISION_C6_EDIT_OR_REJECT_OR_CLOSE_WITHOUT_EDIT")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in c6rr.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(c6rr.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    assert "random" not in src
    assert "now(" not in src
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
