"""Tests for the Candidate #6 strategy spec review contract.

Verifies: the pushed proposal + Recommendation V1 + Autopilot V1 +
five-record ledger gate the build; every frozen numeric (RS metric,
lookback, rank-#1 trigger, continuation event, WIDER stop, universe,
floor/fee, data boundary); missing-or-altered mutations reject; claim
locks and research-only boundaries are permanent; zero
trading-adjacent capability. Commander safety suite runs alongside."""

from __future__ import annotations

import ast

import sparta_commander.multi_symbol_relative_strength_rotation_filter_spec_review_contract as c6s
import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as ap


def test_spec_ready_and_gated_on_full_chain():
    import sparta_commander.multi_symbol_relative_strength_rotation_filter_family_proposal_contract as c6p
    import sparta_commander.strategy_factory_candidate_recommendation_v1_contract as cr
    assert c6p.build_candidate_6_family_proposal()["verdict"] == (
        c6p.VERDICT_C6P_READY)
    assert cr.build_candidate_recommendation()["verdict"] == (
        cr.VERDICT_CR_READY)
    assert ap.build_autopilot_loop_contract()["verdict"] == (
        ap.VERDICT_AP_READY)
    from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
        REJECTION_STATUS as C1)
    from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (
        REJECTION_STATUS as C2)
    from sparta_commander.btc_sol_long_trend_continuation_v1_result_and_rejection_record_contract import (
        REJECTION_STATUS as C3)
    from sparta_commander.sol_btc_long_1h_swing_structure_rejection_record_contract import (
        REJECTION_STATUS as C4)
    from sparta_commander.eth_sol_relative_strength_rejection_record_contract import (
        REJECTION_STATUS as C5)
    assert C1 == C2 == C3 == C4 == C5 == "REJECTED_KEPT_ON_RECORD"
    record = c6s.build_candidate_6_spec_review()
    assert record["verdict"] == c6s.VERDICT_C6S_READY
    assert record["blockers"] == []
    assert c6s.validate_candidate_6_spec_review(record)["valid"] is True
    assert c6s.build_candidate_6_spec_review() == record  # determinism


def test_rs_metric_and_lookback_frozen_and_rejecting_mutations():
    rs = c6s.RS_METRIC
    assert rs["metric"] == "close_to_close_return"
    assert rs["formula"] == "return_20 = close[t] / close[t-20] - 1"
    assert rs["lookback_bars_1h"] == 20
    assert rs["computed_simultaneously_for_all_three_symbols"] is True
    assert rs["uses_completed_1h_bars_only"] is True
    assert rs["no_future_bars"] is True
    assert rs["no_same_bar_lookahead"] is True
    # missing RS metric
    missing = c6s.build_candidate_6_spec_review()
    missing["rs_metric"] = {}
    check = c6s.validate_candidate_6_spec_review(missing)
    assert check["valid"] is False
    assert "rs_metric_definition_missing_or_altered" in check["errors"]
    # altered metric
    altered = c6s.build_candidate_6_spec_review()
    altered["rs_metric"] = dict(c6s.RS_METRIC, metric="volume_ratio")
    check = c6s.validate_candidate_6_spec_review(altered)
    assert check["valid"] is False
    assert "rs_metric_definition_missing_or_altered" in check["errors"]
    # altered lookback
    lookback = c6s.build_candidate_6_spec_review()
    lookback["rs_metric"] = dict(c6s.RS_METRIC, lookback_bars_1h=5)
    check = c6s.validate_candidate_6_spec_review(lookback)
    assert check["valid"] is False
    assert "rs_lookback_missing_or_altered" in check["errors"]


def test_rank_1_trigger_frozen_and_rejecting_mutations():
    rank = c6s.RANK_RULE
    assert "strict rank #1" in rank["rule"]
    assert "STRICTLY greater than both other symbols" in rank["rule"]
    assert rank["additional_rule"] == "return_20(candidate) > 0"
    assert rank["ties_fail"] is True
    assert rank["no_lookahead"] is True
    missing = c6s.build_candidate_6_spec_review()
    missing["rank_rule"] = {}
    check = c6s.validate_candidate_6_spec_review(missing)
    assert check["valid"] is False
    assert "rank_1_trigger_missing_or_altered" in check["errors"]
    altered = c6s.build_candidate_6_spec_review()
    altered["rank_rule"] = dict(c6s.RANK_RULE, ties_fail=False)
    check = c6s.validate_candidate_6_spec_review(altered)
    assert check["valid"] is False
    assert "rank_1_trigger_missing_or_altered" in check["errors"]


def test_continuation_event_frozen_and_rejecting_mutations():
    continuation = c6s.CONTINUATION_EVENT
    assert "fresh 10-bar closing high" in continuation["rule"]
    assert continuation["closing_high_lookback_bars"] == 10
    assert continuation["entry_price"] == "close_of_the_event_bar"
    assert continuation["evaluation_starts"] == (
        "next_1h_bar_after_event_close")
    assert continuation["one_setup_per_event_bar"] is True
    assert continuation["no_intrabar_entry"] is True
    assert continuation["not_a_delayed_pullback_resumption"] is True
    missing = c6s.build_candidate_6_spec_review()
    missing["continuation_event"] = {}
    check = c6s.validate_candidate_6_spec_review(missing)
    assert check["valid"] is False
    assert "continuation_event_missing_or_altered" in check["errors"]
    altered = c6s.build_candidate_6_spec_review()
    altered["continuation_event"] = dict(
        c6s.CONTINUATION_EVENT, evaluation_starts="same_bar")
    check = c6s.validate_candidate_6_spec_review(altered)
    assert check["valid"] is False
    assert "continuation_event_missing_or_altered" in check["errors"]
    rescue = c6s.build_candidate_6_spec_review()
    rescue["continuation_event"] = dict(
        c6s.CONTINUATION_EVENT, not_a_delayed_pullback_resumption=False)
    check = c6s.validate_candidate_6_spec_review(rescue)
    assert check["valid"] is False
    assert "c5_rescue_protection_weakened" in check["errors"]


def test_wider_stop_rule_frozen_and_rejecting_mutations():
    stop = c6s.STOP_RULE
    assert stop["atr_length"] == 14
    assert stop["atr_multiplier"] == 1.5
    assert stop["structure_lookback_bars"] == 10
    assert stop["stop_distance"] == (
        "max(1.5 * atr14, structure_stop_distance)")
    assert stop["stop_must_be_below_entry"] is True
    assert stop["invalid_if_stop_distance_not_positive"] is True
    assert stop["wider_stop_rule_mandatory_no_tightening"] is True
    missing = c6s.build_candidate_6_spec_review()
    missing["stop_rule"] = {}
    check = c6s.validate_candidate_6_spec_review(missing)
    assert check["valid"] is False
    assert "wider_stop_rule_missing_or_altered" in check["errors"]
    altered = c6s.build_candidate_6_spec_review()
    altered["stop_rule"] = dict(
        c6s.STOP_RULE,
        stop_distance="min(1.5 * atr14, structure_stop_distance)")
    check = c6s.validate_candidate_6_spec_review(altered)
    assert check["valid"] is False
    assert "wider_stop_rule_missing_or_altered" in check["errors"]
    numbers = c6s.build_candidate_6_spec_review()
    numbers["stop_rule"] = dict(c6s.STOP_RULE, atr_length=7)
    check = c6s.validate_candidate_6_spec_review(numbers)
    assert check["valid"] is False
    assert "stop_numbers_missing_or_altered" in check["errors"]


def test_universe_enforced():
    record = c6s.build_candidate_6_spec_review()
    assert record["universe"] == ["BTCUSD", "ETHUSD", "SOLUSD"]
    assert record["timeframe"] == "1h"
    assert record["direction"] == "long_only"
    for value in (["BTCUSD", "ETHUSD"],
                  ["BTCUSD", "ETHUSD", "SOLUSD", "DOGEUSD"],
                  []):
        tampered = c6s.build_candidate_6_spec_review()
        tampered["universe"] = value
        check = c6s.validate_candidate_6_spec_review(tampered)
        assert check["valid"] is False, value
        assert "universe_tampered" in check["errors"], value


def test_floor_and_fee_enforced():
    fee = c6s.FEE_GEOMETRY
    assert fee["fee_model_round_trip_bps"] == 27
    assert fee["minimum_gross_target_distance_floor_bps"] == 81
    assert 27 * 3 == 81
    assert fee["floor_is_3x_round_trip_fees"] is True
    assert fee["checked_before_replay_eligibility"] is True
    assert fee["no_maker_rebate_assumption"] is True
    assert fee["no_zero_fee_assumption"] is True
    for mutated, expected in (
            (dict(fee, fee_model_round_trip_bps=10),
             "fee_bps_missing_or_altered"),
            (dict(fee, minimum_gross_target_distance_floor_bps=54),
             "floor_81bps_missing_or_altered"),
            ({}, "fee_bps_missing_or_altered")):
        tampered = c6s.build_candidate_6_spec_review()
        tampered["fee_geometry"] = mutated
        check = c6s.validate_candidate_6_spec_review(tampered)
        assert check["valid"] is False
        assert expected in check["errors"]
    record = c6s.build_candidate_6_spec_review()
    assert record["target_rules"]["variants"] == ["2r", "3r", "4r"]
    tampered = c6s.build_candidate_6_spec_review()
    tampered["target_rules"] = dict(tampered["target_rules"],
                                    variants=["2r", "8r"])
    assert c6s.validate_candidate_6_spec_review(
        tampered)["valid"] is False


def test_data_boundary_and_ledger_gate_enforced():
    boundary = c6s.DATA_BOUNDARY
    assert "existing append-only staged 15m candles only" in (
        boundary["source"])
    assert "pushed aggregator" in boundary["aggregation"]
    assert boundary["sample_tag"] == "2026-05-02_2026-06-10"
    assert boundary["no_fetch_ever"] is True
    assert boundary["no_real_time_data"] is True
    assert boundary["staged_data_never_modified"] is True
    weakened = c6s.build_candidate_6_spec_review()
    weakened["data_boundary"] = dict(c6s.DATA_BOUNDARY,
                                     no_fetch_ever=False)
    check = c6s.validate_candidate_6_spec_review(weakened)
    assert check["valid"] is False
    assert "data_boundary_weakened" in check["errors"]
    # the five-record ledger gate is structural: the build routes
    # through the pushed proposal, which goes BLOCKED on ledger break;
    # here we assert the live chain holds and the verdict is gated
    record = c6s.build_candidate_6_spec_review()
    assert record["verdict"] == c6s.VERDICT_C6S_READY
    assert record["rejection_conditions"] == list(
        ap.AUTO_REJECTION_RULES)
    tampered = c6s.build_candidate_6_spec_review()
    tampered["rejection_conditions"] = []
    assert c6s.validate_candidate_6_spec_review(
        tampered)["valid"] is False


def test_research_only_boundaries_permanent():
    record = c6s.build_candidate_6_spec_review()
    locks = record["claim_locks"]
    for lock in ("no_profitability_claim", "no_paper_approval",
                 "no_live_approval", "no_execution_approval",
                 "no_winner_wording",
                 "promotion_can_only_produce_a_human_review_record"):
        assert lock in locks, lock
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
                "creates_detector_implementation_now",
                "modifies_staged_market_data",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate", "claims_profitability"):
        assert record[key] is False, key
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True
    for field, value in (("claim_locks", []),
                         ("claims_profitability", True),
                         ("authorizes_paper_execution", True),
                         ("authorizes_live_trading", True),
                         ("creates_detector_implementation_now", True),
                         ("fetches_data", True),
                         ("live_gate_locked", False),
                         ("verdict", "CANDIDATE_6_APPROVED")):
        tampered = c6s.build_candidate_6_spec_review()
        tampered[field] = value
        assert c6s.validate_candidate_6_spec_review(
            tampered)["valid"] is False, field


def test_label_next_stage_and_module_purity():
    record = c6s.build_candidate_6_spec_review()
    assert record["current_loop_stage"] == "candidate_spec"
    assert record["next_loop_stage"] == "detector_and_label_review"
    assert record["next_loop_stage"] == ap.LOOP_STAGES[1]
    assert c6s.VERDICT_C6S_READY == "CANDIDATE_6_SPEC_REVIEW_READY"
    assert c6s.NEXT_REQUIRED_ACTION == (
        "HUMAN_APPROVED_CANDIDATE_6_DETECTOR_SPEC_AND_DRY_RUN_PATH")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in c6s.NEXT_REQUIRED_ACTION.upper(), banned
    assert c6s.get_candidate_6_spec_review_label() == c6s.C6S_LABEL
    assert "READ-ONLY" in c6s.C6S_LABEL
    assert c6s.C6S_MODE == "RESEARCH_ONLY"
    src = open(c6s.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt",
                   "smtplib", "subprocess", "websockets", "aiohttp",
                   "schedule", "apscheduler", "threading", "asyncio",
                   "time", "sched", "telegram", "email", "csv", "pandas",
                   "pathlib", "os", "io", "json", "shutil", "databento",
                   "ssl", "ftplib", "datetime", "hashlib", "statistics",
                   "random"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
    assert not any(
        call.func.attr == "open" if isinstance(call.func, ast.Attribute)
        else getattr(call.func, "id", "") == "open"
        for call in ast.walk(tree) if isinstance(call, ast.Call))
