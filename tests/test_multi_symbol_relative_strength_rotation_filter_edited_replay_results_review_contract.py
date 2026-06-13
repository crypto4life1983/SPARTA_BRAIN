"""Tests for the Candidate #6 edited informational replay results
review.

Covers all 19 commanded requirements: artifact sha freezes; total
counts; per-variant arithmetic (2R/3R/4R); per-symbol breakdown;
all-variants-net-negative; gross-negative; hit rates below breakeven;
overlap skipped counts and total; max drawdown; honest verdict
`edited_edge_failed`; worsened-vs-original comparison; auto-rejection
trigger status; review fails on any frozen-fact mutation; downstream
locks held; no trading-adjacent capability; AST/purity. Commander
safety suite runs alongside (12 tests)."""

from __future__ import annotations

import ast
import copy

import pytest

import sparta_commander.multi_symbol_relative_strength_rotation_filter_edited_replay_results_review_contract as c6eer
import sparta_commander.multi_symbol_relative_strength_rotation_filter_replay_results_review_contract as c6rr
import sparta_commander.multi_symbol_relative_strength_rotation_filter_edited_real_candle_labels_review_contract as c6el

REPO_ROOT = "C:/SPARTA_BRAIN"


def _good_observation():
    return {
        "results_exists": True, "summary_exists": True,
        "results_sha256": c6eer.EXPECTED_RESULTS_SHA256,
        "summary_sha256": c6eer.EXPECTED_SUMMARY_SHA256,
        "row_count": 36,
        "setup_ids": tuple(sorted(
            c6el.EXPECTED_KEPT_ACCEPTED_SETUP_IDS)),
        "variants": copy.deepcopy(c6eer.EXPECTED_VARIANTS),
        "per_symbol": copy.deepcopy(c6eer.EXPECTED_PER_SYMBOL),
        "overlap_skipped_total":
            c6eer.EXPECTED_OVERLAP_SKIPPED_TOTAL,
        "all_variants_net_negative": True,
        "all_variants_gross_negative": True,
        "all_hit_rates_below_breakeven": True,
        "max_drawdown_exceeds_net_loss_per_variant": True,
        "summary_honest_verdict": c6eer.HONEST_VERDICT,
        "summary_auto_rejection_triggers": dict(
            c6eer.EXPECTED_AUTO_REJECTION_TRIGGERS),
        "summary_replayed_setup_ids": tuple(sorted(
            c6el.EXPECTED_KEPT_ACCEPTED_SETUP_IDS)),
        "summary_no_second_edit_attempted": True,
        "summary_no_detector_rerun": True,
        "summary_no_label_change": True,
        "summary_no_rejection_record_in_this_gate": True,
        "summary_no_paper_or_live_authorization": True,
        "summary_no_profitability_claim": True,
        "artifacts_tracked_in_git": [],
    }


# (1) Validate edited replay artifact shas exactly --------------------------

def test_1_edited_replay_artifact_shas_exact():
    assert c6eer.EXPECTED_RESULTS_SHA256 == (
        "b83a4d697219fe8c3635bac7f6ca7baf86e5ecb29b99a35693446bafa7f88"
        "4f0")
    assert c6eer.EXPECTED_SUMMARY_SHA256 == (
        "150cb5483107fd88474a8989798450209da696b148dd79b9fda1b55bd643"
        "4fc6")
    bad = _good_observation()
    bad["results_sha256"] = "00" * 32
    assert "edited_results_sha_mismatch" in (
        c6eer.certify_c6_edited_replay_results(bad)["failures"])
    bad2 = _good_observation()
    bad2["summary_sha256"] = "00" * 32
    assert "edited_summary_sha_mismatch" in (
        c6eer.certify_c6_edited_replay_results(bad2)["failures"])


# (2) Validate edited input artifact shas exactly ---------------------------

def test_2_edited_input_artifact_shas_exact():
    inputs = c6eer.EXPECTED_INPUTS
    assert inputs["edited_labels_sha256"] == (
        "a2c720be296914edc863835c02b71949cbf727ae67b0853018983f4a8ae9"
        "d987")
    assert inputs["edited_summary_sha256"] == (
        "92bdf76ec9474292a92ce687a5d830b5f1d66ad65cc4f49c86489219d044"
        "6f7a")
    # mirror the pushed edited-labels review's frozen shas
    assert inputs["edited_labels_sha256"] == (
        c6el.EXPECTED_LABELS_SHA256)
    assert inputs["edited_summary_sha256"] == (
        c6el.EXPECTED_SUMMARY_SHA256)


# (3) Validate edited accepted count = 36 -----------------------------------

def test_3_edited_accepted_count_equals_36():
    inputs = c6eer.EXPECTED_INPUTS
    assert inputs["edited_accepted_count_BTCUSD"] == 9
    assert inputs["edited_accepted_count_ETHUSD"] == 11
    assert inputs["edited_accepted_count_SOLUSD"] == 16
    assert inputs["edited_accepted_count_total"] == 36
    assert (inputs["edited_accepted_count_BTCUSD"]
            + inputs["edited_accepted_count_ETHUSD"]
            + inputs["edited_accepted_count_SOLUSD"]) == 36
    bad = _good_observation()
    bad["row_count"] = 35
    assert "row_count_not_36" in (
        c6eer.certify_c6_edited_replay_results(bad)["failures"])


# (4) Validate 2R edited replay arithmetic exactly --------------------------

def test_4_2r_edited_arithmetic_exact():
    table = c6eer.EXPECTED_VARIANTS["2r"]
    assert table == {
        "eligible_setups": 36, "skipped_overlap": 11, "kept": 25,
        "hits": 5, "stops": 18, "timeouts": 2,
        "hit_rate_pct": 20.0, "gross_breakeven_rate_pct": 33.3,
        "gross_r_total": -8.666284, "fee_r_total": 4.231551,
        "net_r_total": -12.897835, "avg_net_r": -0.515913,
        "max_drawdown_r": -17.464416}
    assert table["hits"] + table["stops"] + table["timeouts"] == (
        table["kept"])
    assert table["eligible_setups"] == (
        table["skipped_overlap"] + table["kept"])
    bad = _good_observation()
    bad["variants"]["2r"]["net_r_total"] = -1.0
    assert "variant_fact_mismatch:2r:net_r_total" in (
        c6eer.certify_c6_edited_replay_results(bad)["failures"])


# (5) Validate 3R edited replay arithmetic exactly --------------------------

def test_5_3r_edited_arithmetic_exact():
    table = c6eer.EXPECTED_VARIANTS["3r"]
    assert table == {
        "eligible_setups": 36, "skipped_overlap": 12, "kept": 24,
        "hits": 3, "stops": 19, "timeouts": 2,
        "hit_rate_pct": 12.5, "gross_breakeven_rate_pct": 25.0,
        "gross_r_total": -10.666284, "fee_r_total": 4.127007,
        "net_r_total": -14.793291, "avg_net_r": -0.616387,
        "max_drawdown_r": -17.448356}
    assert table["hits"] + table["stops"] + table["timeouts"] == (
        table["kept"])
    bad = _good_observation()
    bad["variants"]["3r"]["hits"] = 5
    assert "variant_fact_mismatch:3r:hits" in (
        c6eer.certify_c6_edited_replay_results(bad)["failures"])


# (6) Validate 4R edited replay arithmetic exactly --------------------------

def test_6_4r_edited_arithmetic_exact():
    table = c6eer.EXPECTED_VARIANTS["4r"]
    assert table == {
        "eligible_setups": 36, "skipped_overlap": 14, "kept": 22,
        "hits": 2, "stops": 18, "timeouts": 2,
        "hit_rate_pct": 9.1, "gross_breakeven_rate_pct": 20.0,
        "gross_r_total": -10.666284, "fee_r_total": 3.798458,
        "net_r_total": -14.464742, "avg_net_r": -0.657488,
        "max_drawdown_r": -17.448356}
    assert table["hits"] + table["stops"] + table["timeouts"] == (
        table["kept"])
    bad = _good_observation()
    bad["variants"]["4r"]["max_drawdown_r"] = 0.0
    assert "variant_fact_mismatch:4r:max_drawdown_r" in (
        c6eer.certify_c6_edited_replay_results(bad)["failures"])


# (7) Validate per-symbol breakdown exactly --------------------------------

def test_7_per_symbol_breakdown_exact():
    split = c6eer.EXPECTED_PER_SYMBOL
    assert split["BTCUSD"] == {
        "2r_trades": 5, "2r_net": -5.409106,
        "3r_trades": 5, "3r_net": -5.409106,
        "4r_trades": 5, "4r_net": -5.409106}
    assert split["ETHUSD"] == {
        "2r_trades": 9, "2r_net": -4.867937,
        "3r_trades": 9, "3r_net": -6.867937,
        "4r_trades": 9, "4r_net": -5.867937}
    assert split["SOLUSD"] == {
        "2r_trades": 11, "2r_net": -2.620792,
        "3r_trades": 10, "3r_net": -2.516248,
        "4r_trades": 8, "4r_net": -3.187699}
    # trade-count reconciliation against the kept totals per variant
    for name in ("2r", "3r", "4r"):
        assert (split["BTCUSD"][name + "_trades"]
                + split["ETHUSD"][name + "_trades"]
                + split["SOLUSD"][name + "_trades"]
                ) == c6eer.EXPECTED_VARIANTS[name]["kept"], name
        # net R reconciliation per variant
        assert round(split["BTCUSD"][name + "_net"]
                     + split["ETHUSD"][name + "_net"]
                     + split["SOLUSD"][name + "_net"], 6) == (
            c6eer.EXPECTED_VARIANTS[name]["net_r_total"]), name
    bad = _good_observation()
    bad["per_symbol"]["BTCUSD"]["2r_net"] = 5.0
    assert "per_symbol_mismatch" in (
        c6eer.certify_c6_edited_replay_results(bad)["failures"])


# (8) Validate all variants net-negative -----------------------------------

def test_8_all_variants_net_negative():
    for name, row in c6eer.EXPECTED_VARIANTS.items():
        assert row["net_r_total"] < 0, name
    bad = _good_observation()
    bad["all_variants_net_negative"] = False
    assert "net_negative_fact_broken" in (
        c6eer.certify_c6_edited_replay_results(bad)["failures"])


# (9) Validate all variants gross-negative ---------------------------------

def test_9_all_variants_gross_negative():
    for name, row in c6eer.EXPECTED_VARIANTS.items():
        assert row["gross_r_total"] < 0, name
    bad = _good_observation()
    bad["all_variants_gross_negative"] = False
    assert "gross_negative_fact_broken" in (
        c6eer.certify_c6_edited_replay_results(bad)["failures"])


# (10) Validate hit rates below breakeven ---------------------------------

def test_10_hit_rates_below_gross_breakeven():
    for name, row in c6eer.EXPECTED_VARIANTS.items():
        assert row["hit_rate_pct"] < row[
            "gross_breakeven_rate_pct"], name
    # explicit values
    assert c6eer.EXPECTED_VARIANTS["2r"]["hit_rate_pct"] == 20.0
    assert c6eer.EXPECTED_VARIANTS["3r"]["hit_rate_pct"] == 12.5
    assert c6eer.EXPECTED_VARIANTS["4r"]["hit_rate_pct"] == 9.1
    bad = _good_observation()
    bad["all_hit_rates_below_breakeven"] = False
    assert "hit_rates_below_breakeven_fact_broken" in (
        c6eer.certify_c6_edited_replay_results(bad)["failures"])


# (11) Validate overlap skipped counts exactly: 11/12/14 and total 37 ------

def test_11_overlap_skipped_counts_and_total():
    assert c6eer.EXPECTED_VARIANTS["2r"]["skipped_overlap"] == 11
    assert c6eer.EXPECTED_VARIANTS["3r"]["skipped_overlap"] == 12
    assert c6eer.EXPECTED_VARIANTS["4r"]["skipped_overlap"] == 14
    assert c6eer.EXPECTED_OVERLAP_SKIPPED_TOTAL == 11 + 12 + 14
    assert c6eer.EXPECTED_OVERLAP_SKIPPED_TOTAL == 37
    bad = _good_observation()
    bad["overlap_skipped_total"] = 38
    assert "overlap_skipped_total_mismatch" in (
        c6eer.certify_c6_edited_replay_results(bad)["failures"])


# (12) Validate max drawdown values exactly -------------------------------

def test_12_max_drawdown_values_exact_and_exceed_loss():
    table = c6eer.EXPECTED_VARIANTS
    assert table["2r"]["max_drawdown_r"] == -17.464416
    assert table["3r"]["max_drawdown_r"] == -17.448356
    assert table["4r"]["max_drawdown_r"] == -17.448356
    # max drawdown EXCEEDS net loss (both negative; mdd is deeper)
    for name in ("2r", "3r", "4r"):
        assert table[name]["max_drawdown_r"] < table[name][
            "net_r_total"], name
    bad = _good_observation()
    bad["max_drawdown_exceeds_net_loss_per_variant"] = False
    assert "max_drawdown_exceeds_net_loss_fact_broken" in (
        c6eer.certify_c6_edited_replay_results(bad)["failures"])


# (13) Validate honest verdict exactly: `edited_edge_failed` --------------

def test_13_honest_verdict_exact():
    assert c6eer.HONEST_VERDICT == "edited_edge_failed"
    bad = _good_observation()
    bad["summary_honest_verdict"] = (
        "edited_passed_research_threshold_for_human_review")
    assert "summary_honest_verdict_mismatch" in (
        c6eer.certify_c6_edited_replay_results(bad)["failures"])


# (14) Validate edited results worsened versus original ------------------

def test_14_edited_worsened_versus_original_replay():
    compare = c6eer.EXPECTED_WORSENED_VS_ORIGINAL
    # mirror originals exactly from the pushed original-replay review
    for name in ("2r", "3r", "4r"):
        original = c6rr.EXPECTED_VARIANTS[name]
        assert compare[name]["original_net_r"] == (
            original["net_r_total"]), name
        assert compare[name]["original_hit_rate_pct"] == (
            original["hit_rate_pct"]), name
        # net R deeper (more negative) under edited
        assert compare[name]["edited_net_r"] < compare[name][
            "original_net_r"], name
        assert compare[name]["net_r_delta_deeper"] is True, name
        # hit rate worsened (lower)
        assert compare[name]["edited_hit_rate_pct"] < compare[name][
            "original_hit_rate_pct"], name
        assert compare[name]["hit_rate_worsened"] is True, name
    # specific values check
    assert compare["2r"]["edited_net_r"] == -12.897835
    assert compare["3r"]["edited_net_r"] == -14.793291
    assert compare["4r"]["edited_net_r"] == -14.464742
    assert compare["2r"]["edited_hit_rate_pct"] == 20.0
    assert compare["3r"]["edited_hit_rate_pct"] == 12.5
    assert compare["4r"]["edited_hit_rate_pct"] == 9.1


# (15) Validate auto-rejection triggers fired exactly as reported -------

def test_15_auto_rejection_triggers_fired_as_reported():
    triggers = c6eer.EXPECTED_AUTO_REJECTION_TRIGGERS
    assert triggers["any_variant_net_negative"] is True
    assert triggers["any_variant_gross_negative"] is True
    assert triggers["any_variant_hit_rate_below_gross_breakeven"] is (
        True)
    assert triggers[
        "any_variant_kept_set_below_minimum_evaluable_count"] is False
    assert triggers["minimum_evaluable_kept_per_variant"] == 10
    assert triggers["edited_labels_sha_mismatch"] is False
    assert triggers["edited_summary_sha_mismatch"] is False
    assert triggers["staged_data_sha_mismatch"] is False
    assert triggers["any_inviolable_rule_changed"] is False
    assert triggers["any_second_edit_attempted"] is False
    # each trigger key must be present in the summary
    for key in ("any_variant_net_negative",
                "any_variant_gross_negative",
                "any_variant_hit_rate_below_gross_breakeven",
                "any_variant_kept_set_below_minimum_evaluable_count",
                "edited_labels_sha_mismatch",
                "edited_summary_sha_mismatch",
                "staged_data_sha_mismatch",
                "any_inviolable_rule_changed",
                "any_second_edit_attempted"):
        bad = _good_observation()
        bad["summary_auto_rejection_triggers"] = dict(
            bad["summary_auto_rejection_triggers"], **{
                key: not bad["summary_auto_rejection_triggers"][key]})
        assert "auto_rejection_trigger_mismatch:" + key in (
            c6eer.certify_c6_edited_replay_results(bad)["failures"]), \
            key


# (16) Review fails if any frozen-fact mutation -------------------------

def test_16_review_fails_on_any_record_change():
    record = c6eer.build_c6_edited_replay_results_review(
        REPO_ROOT, tracked_paths=[])
    for field, value in (
            ("honest_verdict",
             "edited_passed_research_threshold_for_human_review"),
            ("head_at_edited_replay", "00" * 20),
            ("expected_results_sha256", "00" * 32),
            ("expected_summary_sha256", "00" * 32),
            ("expected_inputs", {}),
            ("expected_variants", {}),
            ("expected_per_symbol", {}),
            ("expected_overlap_skipped_total", 0),
            ("expected_auto_rejection_triggers", {}),
            ("expected_worsened_vs_original", {}),
            ("frozen_replay_rules", []),
            ("frozen_review_findings", []),
            ("claim_locks", []),
            ("edit_authorized_by_this_gate", True),
            ("second_edit_possible", True),
            ("rejection_record_created_by_this_gate", True),
            ("structure_filter_modified_by_this_gate", True),
            ("detector_changed_by_this_gate", True),
            ("labels_changed_by_this_gate", True),
            ("replay_rerun_by_this_gate", True),
            ("claims_profitability", True),
            ("authorizes_paper_execution", True),
            ("authorizes_live_trading", True),
            ("live_gate_locked", False),
            ("verdict", "C6_APPROVED_FOR_TRADING")):
        tampered = c6eer.build_c6_edited_replay_results_review(
            REPO_ROOT, tracked_paths=[])
        tampered[field] = value
        assert c6eer.validate_c6_edited_replay_results_review(
            tampered)["valid"] is False, field
    frozen_with_failures = c6eer.build_c6_edited_replay_results_review(
        REPO_ROOT, tracked_paths=[])
    frozen_with_failures["failures"] = ["fake"]
    assert c6eer.validate_c6_edited_replay_results_review(
        frozen_with_failures)["valid"] is False


# (17) No second edit / rejection / paper / live / profitability ---------

def test_17_no_second_edit_rejection_paper_live_profitability():
    record = c6eer.build_c6_edited_replay_results_review(
        REPO_ROOT, tracked_paths=[])
    assert record["edit_authorized_by_this_gate"] is False
    assert record["second_edit_possible"] is False
    assert record["rejection_record_created_by_this_gate"] is False
    assert record["structure_filter_modified_by_this_gate"] is False
    assert record["detector_changed_by_this_gate"] is False
    assert record["labels_changed_by_this_gate"] is False
    assert record["replay_rerun_by_this_gate"] is False
    locks = record["claim_locks"]
    for lock in ("no_edit_authorized_by_this_gate",
                 "no_second_edit_possible",
                 "no_rejection_record_created_by_this_gate",
                 "no_paper_approval", "no_live_approval",
                 "no_execution_approval", "no_profitability_claim",
                 "no_winner_wording"):
        assert lock in locks, lock
    # the summary's own locks are re-verified by the certifier
    bad = _good_observation()
    bad["summary_no_second_edit_attempted"] = False
    assert "summary_must_record_no_second_edit_attempted" in (
        c6eer.certify_c6_edited_replay_results(bad)["failures"])
    bad2 = _good_observation()
    bad2["summary_no_rejection_record_in_this_gate"] = False
    assert "summary_must_record_no_rejection_record_in_this_gate" in (
        c6eer.certify_c6_edited_replay_results(bad2)["failures"])
    bad3 = _good_observation()
    bad3["summary_no_profitability_claim"] = False
    assert "summary_must_record_no_profitability_claim" in (
        c6eer.certify_c6_edited_replay_results(bad3)["failures"])


# (18) No trading-adjacent capability ------------------------------------

def test_18_no_trading_adjacent_capability():
    record = c6eer.build_c6_edited_replay_results_review(
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


# (19) AST/purity --------------------------------------------------------

def test_19_ast_purity_and_no_writers_or_runners():
    assert c6eer.get_c6_edited_replay_review_label() == c6eer.C6EER_LABEL
    assert "READ-ONLY" in c6eer.C6EER_LABEL
    assert "ALL VARIANTS NET NEGATIVE" in c6eer.C6EER_LABEL
    assert "NOT A PROFITABILITY CLAIM" in c6eer.C6EER_LABEL
    assert c6eer.C6EER_MODE == "RESEARCH_ONLY"
    assert c6eer.VERDICT_C6EER_FROZEN == (
        "C6_EDITED_REPLAY_RESULTS_REVIEW_INFORMATION_ONLY_FROZEN")
    assert c6eer.NEXT_REQUIRED_ACTION == (
        "HUMAN_DECISION_C6_REJECTION_RECORD_OR_CLOSE_FAMILY")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in c6eer.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(c6eer.__file__, encoding="utf-8").read()
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


# Real-artifact live certification ----------------------------------------

def test_real_artifacts_certify_when_present():
    import pathlib
    if not (pathlib.Path(REPO_ROOT) / c6eer.RESULTS_PATH).is_file():
        pytest.skip("candidate #6 edited replay artifacts not present")
    record = c6eer.build_c6_edited_replay_results_review(
        REPO_ROOT, tracked_paths=[])
    assert record["verdict"] == c6eer.VERDICT_C6EER_FROZEN
    assert record["failures"] == []
    assert c6eer.validate_c6_edited_replay_results_review(
        record)["valid"] is True
    # determinism
    assert c6eer.build_c6_edited_replay_results_review(
        REPO_ROOT, tracked_paths=[]) == record


def test_chain_gate_and_runner_untracked():
    bad = _good_observation()
    bad["artifacts_tracked_in_git"] = [c6eer.RUNNER_PATH]
    assert "edited_runner_and_artifacts_must_stay_untracked" in (
        c6eer.certify_c6_edited_replay_results(bad)["failures"])
