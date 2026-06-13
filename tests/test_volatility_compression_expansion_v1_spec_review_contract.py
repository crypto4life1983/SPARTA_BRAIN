"""Tests for the Candidate #7 strategy spec review contract
(VOLATILITY_COMPRESSION_EXPANSION_V1).

Verifies: the pushed C7 proposal + V2 + Recommendation V1 + Autopilot
V1 + six-record ledger gate the build; every frozen numeric and
binary (ATR length, rolling-average window, contraction fraction +
window, expansion multiplier + close-in-upper-third, structure-stop
lookback, WIDER stop ATR multiplier, anti-cluster 6-bar gap, sample
window, 27/81 bps); the anti-cluster gap is proposal-level locked
and NOT the edit token; missing-or-altered mutations reject; claim
locks and research-only boundaries are permanent; zero downstream
unlocks; zero trading-adjacent capability. Commander safety suite
runs alongside."""

from __future__ import annotations

import ast

import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as ap
import sparta_commander.strategy_factory_candidate_recommendation_v1_contract as rec
import sparta_commander.strategy_factory_overnight_research_autopilot_v2_contract as oap2
import sparta_commander.volatility_compression_expansion_v1_family_proposal_contract as c7p
import sparta_commander.volatility_compression_expansion_v1_spec_review_contract as c7s


def _record():
    return c7s.build_candidate_7_spec_review()


def test_spec_ready_and_gated_on_full_chain():
    assert c7p.build_candidate_7_family_proposal()["verdict"] == (
        c7p.VERDICT_C7P_READY)
    assert oap2.build_overnight_research_autopilot_v2_contract()[
        "verdict"] == oap2.VERDICT_OAP2_READY
    assert rec.build_candidate_recommendation()["verdict"] == (
        rec.VERDICT_CR_READY)
    assert ap.build_autopilot_loop_contract()["verdict"] == (
        ap.VERDICT_AP_READY)
    from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (  # noqa: E501
        REJECTION_STATUS as C1)
    from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (  # noqa: E501
        REJECTION_STATUS as C2)
    from sparta_commander.btc_sol_long_trend_continuation_v1_result_and_rejection_record_contract import (  # noqa: E501
        REJECTION_STATUS as C3)
    from sparta_commander.sol_btc_long_1h_swing_structure_rejection_record_contract import (  # noqa: E501
        REJECTION_STATUS as C4)
    from sparta_commander.eth_sol_relative_strength_rejection_record_contract import (  # noqa: E501
        REJECTION_STATUS as C5)
    from sparta_commander.multi_symbol_relative_strength_rotation_filter_rejection_record_contract import (  # noqa: E501
        REJECTION_STATUS as C6)
    assert C1 == C2 == C3 == C4 == C5 == C6 == "REJECTED_KEPT_ON_RECORD"
    record = _record()
    assert record["verdict"] == c7s.VERDICT_C7S_READY
    assert record["blockers"] == []
    assert c7s.validate_candidate_7_spec_review(record)["valid"] is True
    assert _record() == record  # determinism
    assert record["ledger_status_six_records"] == [
        "REJECTED_KEPT_ON_RECORD"] * 6
    assert record["ledger_all_rejected_kept_on_record"] is True


def test_universe_timeframe_direction_frozen():
    record = _record()
    assert record["universe"] == ["BTCUSD"]
    assert record["timeframe"] == "4h"
    assert record["direction"] == "long_only"
    for field, value in (("universe", ["BTCUSD", "ETHUSD"]),
                         ("universe", []),
                         ("timeframe", "1h"),
                         ("timeframe", "15m"),
                         ("direction", "long_or_short"),
                         ("direction", "short_only")):
        tampered = _record()
        tampered[field] = value
        assert c7s.validate_candidate_7_spec_review(
            tampered)["valid"] is False, (field, value)


def test_atr_and_rolling_average_window_frozen():
    record = _record()
    assert record["atr_length"] == 14
    assert record["atr_rolling_average_window_4h_bars"] == 100
    assert record[
        "atr_uses_completed_4h_bars_only_standard_true_range"] is True
    for value in (7, 21, 30, 100):
        tampered = _record()
        tampered["atr_length"] = value
        assert c7s.validate_candidate_7_spec_review(
            tampered)["valid"] is False, value
    for value in (50, 200, 500, 1000):
        tampered = _record()
        tampered["atr_rolling_average_window_4h_bars"] = value
        assert c7s.validate_candidate_7_spec_review(
            tampered)["valid"] is False, value


def test_contraction_rule_frozen():
    rule = c7s.CONTRACTION_RULE
    assert rule["contraction_fraction"] == 0.6
    assert rule["contraction_window_bars"] == 5
    assert rule["rolling_average_window_4h_bars"] == 100
    assert rule["uses_completed_4h_bars_only"] is True
    assert rule["no_future_bars"] is True
    assert rule["no_same_bar_lookahead"] is True
    assert rule["strict_inequality"] is True
    for mutation in ({"contraction_fraction": 0.5},
                     {"contraction_fraction": 1.0},
                     {"contraction_window_bars": 0},
                     {"contraction_window_bars": 3},
                     {"contraction_window_bars": 20},
                     {"rolling_average_window_4h_bars": 50}):
        tampered = _record()
        tampered["contraction_rule"] = dict(c7s.CONTRACTION_RULE,
                                            **mutation)
        assert c7s.validate_candidate_7_spec_review(
            tampered)["valid"] is False, mutation


def test_expansion_event_frozen():
    expansion = c7s.EXPANSION_EVENT
    assert expansion["expansion_true_range_multiplier"] == 1.8
    assert expansion["close_in_upper_third_required"] is True
    assert expansion["entry_price"] == "close_of_the_event_bar"
    assert expansion["evaluation_starts"] == (
        "next_4h_bar_after_event_close")
    assert expansion["one_setup_per_event_bar"] is True
    assert expansion["no_intrabar_entry"] is True
    for mutation in ({"expansion_true_range_multiplier": 1.0},
                     {"expansion_true_range_multiplier": 2.5},
                     {"close_in_upper_third_required": False},
                     {"entry_price": "midprice"},
                     {"entry_price": "next_bar_open"},
                     {"evaluation_starts": "same_bar_as_event_close"},
                     {"no_intrabar_entry": False}):
        tampered = _record()
        tampered["expansion_event"] = dict(c7s.EXPANSION_EVENT,
                                           **mutation)
        assert c7s.validate_candidate_7_spec_review(
            tampered)["valid"] is False, mutation


def test_stop_rule_frozen():
    stop = c7s.STOP_RULE
    assert stop["atr_length"] == 14
    assert stop["atr_multiplier"] == 1.5
    assert stop["structure_lookback_bars"] == 10
    assert stop["stop_distance"] == (
        "max(WIDER_STOP_ATR_MULTIPLIER * atr14, "
        "structure_stop_distance)")
    assert stop["wider_stop_rule_mandatory_no_tightening"] is True
    for mutation in ({"atr_length": 7}, {"atr_length": 30},
                     {"atr_multiplier": 0.5},
                     {"atr_multiplier": 1.0},
                     {"atr_multiplier": 2.0},
                     {"structure_lookback_bars": 3},
                     {"structure_lookback_bars": 20},
                     {"stop_distance": "fixed_2_percent"},
                     {"wider_stop_rule_mandatory_no_tightening":
                          False}):
        tampered = _record()
        tampered["stop_rule"] = dict(c7s.STOP_RULE, **mutation)
        assert c7s.validate_candidate_7_spec_review(
            tampered)["valid"] is False, mutation


def test_target_rules_frozen():
    targets = _record()["target_rules"]
    assert targets["variants"] == ["2r", "3r", "4r"]
    assert targets["no_new_variants_after_label_freeze"] is True
    assert targets["target_price_formula"] == (
        "entry_price + r_multiple * stop_distance")
    for value in (["1r"], ["5r"], ["2r", "3r"],
                  ["2r", "3r", "4r", "5r"]):
        tampered = _record()
        tampered["target_rules"] = dict(tampered["target_rules"],
                                        variants=value)
        assert c7s.validate_candidate_7_spec_review(
            tampered)["valid"] is False, value


def test_fee_geometry_frozen_27_and_81():
    fee = _record()["fee_geometry"]
    assert fee["fee_model_round_trip_bps"] == 27
    assert fee["minimum_gross_target_distance_floor_bps"] == 81
    assert fee["floor_is_3x_round_trip_fees"] is True
    assert fee["no_maker_rebate_assumption"] is True
    assert fee["no_zero_fee_assumption"] is True
    for value in (0, 5, 13, 20, 26, 28, 50, 100):
        tampered = _record()
        tampered["fee_geometry"] = dict(c7s.FEE_GEOMETRY,
                                        fee_model_round_trip_bps=value)
        assert c7s.validate_candidate_7_spec_review(
            tampered)["valid"] is False, value
    for value in (0, 27, 54, 80, 82, 100, 162):
        tampered = _record()
        tampered["fee_geometry"] = dict(
            c7s.FEE_GEOMETRY,
            minimum_gross_target_distance_floor_bps=value)
        assert c7s.validate_candidate_7_spec_review(
            tampered)["valid"] is False, value


def test_anti_cluster_is_proposal_locked_not_edit_token():
    anti = _record()["anti_cluster_policy"]
    assert anti["min_bars_between_same_symbol_accepted_events_4h"] == 6
    assert anti["is_not_the_single_allowed_c7_edit_token"] is True
    assert anti["applies_before_replay_time_non_overlap"] is True
    assert anti["replay_time_non_overlap_unchanged"] is True
    assert anti["scope"] == "per_symbol"
    assert anti["applied_at"] == (
        "label_emission_time_before_replay_non_overlap")
    assert anti["tie_breaker"] == (
        "keep_the_earlier_event_drop_the_later_one")
    # mutating min_bars rejects
    for value in (0, 1, 2, 5, 7, 12, 24, 48):
        tampered = _record()
        tampered["anti_cluster_policy"] = dict(
            c7s.ANTI_CLUSTER_POLICY,
            min_bars_between_same_symbol_accepted_events_4h=value)
        assert c7s.validate_candidate_7_spec_review(
            tampered)["valid"] is False, value
    # weakening the "not the edit token" lock rejects
    tampered = _record()
    tampered["anti_cluster_policy"] = dict(
        c7s.ANTI_CLUSTER_POLICY,
        is_not_the_single_allowed_c7_edit_token=False)
    assert c7s.validate_candidate_7_spec_review(
        tampered)["valid"] is False
    # the edit_policy block also asserts this
    edit = _record()["edit_policy"]
    assert edit["maximum_pre_committed_edits"] == 1
    assert edit["edit_requires_separate_human_approval"] is True
    assert edit[
        "anti_cluster_gap_is_proposal_level_locked_not_the_edit_token"
    ] is True
    tampered = _record()
    tampered["edit_policy"] = dict(
        c7s.EDIT_POLICY,
        anti_cluster_gap_is_proposal_level_locked_not_the_edit_token=
        False)
    assert c7s.validate_candidate_7_spec_review(
        tampered)["valid"] is False


def test_data_boundary_and_sample_window_frozen():
    boundary = _record()["data_boundary"]
    assert boundary["sample_tag"] == "2026-05-02_2026-06-10"
    assert boundary["no_fetch_ever"] is True
    assert boundary["no_real_time_data"] is True
    assert boundary["staged_data_never_modified"] is True
    for mutation in ({"sample_tag": "2026-04-01_2026-05-01"},
                     {"no_fetch_ever": False},
                     {"staged_data_never_modified": False}):
        tampered = _record()
        tampered["data_boundary"] = dict(c7s.DATA_BOUNDARY, **mutation)
        assert c7s.validate_candidate_7_spec_review(
            tampered)["valid"] is False, mutation


def test_chain_blocks_when_ledger_breaks():
    import sparta_commander.volatility_compression_expansion_v1_spec_review_contract as mod
    originals = {key: getattr(mod, key) for key in
                 ("C1_STATUS", "C2_STATUS", "C3_STATUS", "C4_STATUS",
                  "C5_STATUS", "C6_STATUS")}
    try:
        for key in originals:
            setattr(mod, key, "APPROVED_FOR_TRADING")
            record = mod.build_candidate_7_spec_review()
            assert record["verdict"] == c7s.VERDICT_C7S_BLOCKED, key
            assert "six_record_ledger_broken" in record[
                "blockers"], key
            setattr(mod, key, originals[key])
    finally:
        for key, value in originals.items():
            setattr(mod, key, value)
    assert mod.build_candidate_7_spec_review()["verdict"] == (
        c7s.VERDICT_C7S_READY)


def test_spec_review_only_no_downstream_unlocks_or_capability():
    record = _record()
    assert record["is_spec_review_only"] is True
    assert record["current_loop_stage"] == "candidate_spec"
    assert record["next_loop_stage"] == "detector_and_label_review"
    for key in ("runs_detector", "runs_real_candle_detection",
                "runs_relabel", "runs_replay", "labels_now",
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
                "creates_detector_implementation_now",
                "modifies_staged_market_data",
                "authorizes_paper_execution",
                "authorizes_micro_live",
                "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate",
                "unlocks_detector_now", "unlocks_labels_now",
                "unlocks_replay_now",
                "claims_profitability",
                "executes", "writes_files"):
        assert record[key] is False, key
        tampered = _record()
        tampered[key] = True
        assert c7s.validate_candidate_7_spec_review(
            tampered)["valid"] is False, key
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True


def test_research_only_boundaries_and_claim_locks():
    record = _record()
    locks = record["claim_locks"]
    for lock in ("no_profitability_claim", "no_paper_approval",
                 "no_live_approval", "no_execution_approval",
                 "no_winner_wording",
                 "promotion_can_only_produce_a_human_review_record",
                 "anti_cluster_gap_is_proposal_level_locked_not"
                 "_edit_token"):
        assert lock in locks, lock
    tampered = _record()
    tampered["claim_locks"] = []
    assert c7s.validate_candidate_7_spec_review(
        tampered)["valid"] is False
    # label must include research-only / not-a-rescue / not-a-claim
    label = c7s.C7S_LABEL
    assert "READ-ONLY" in label
    assert "RESEARCH ONLY" in label
    assert "NOT A RESCUE" in label
    assert "NOT A CLAIM" in label
    for banned_phrase in ("WINNER", "PROFITABLE", "EDGE CONFIRMED",
                          "APPROVED FOR PAPER", "APPROVED FOR LIVE"):
        assert banned_phrase not in label.upper(), banned_phrase


def test_label_next_stage_and_module_purity():
    record = _record()
    assert record["current_loop_stage"] == "candidate_spec"
    assert record["next_loop_stage"] == "detector_and_label_review"
    assert record["next_loop_stage"] == ap.LOOP_STAGES[1]
    assert c7s.VERDICT_C7S_READY == "CANDIDATE_7_SPEC_REVIEW_READY"
    assert c7s.NEXT_REQUIRED_ACTION == (
        "HUMAN_APPROVED_CANDIDATE_7_DETECTOR_SPEC_AND_DRY_RUN_PATH")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in c7s.NEXT_REQUIRED_ACTION.upper(), banned
    assert c7s.get_candidate_7_spec_review_label() == c7s.C7S_LABEL
    assert c7s.C7S_MODE == "RESEARCH_ONLY"
    src = open(c7s.__file__, encoding="utf-8").read()
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
