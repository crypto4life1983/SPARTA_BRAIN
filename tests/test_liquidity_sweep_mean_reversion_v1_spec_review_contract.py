"""Tests for the Candidate #8 strategy spec review contract
(LIQUIDITY_SWEEP_MEAN_REVERSION_V1).

Verifies: the pushed C8 proposal + V3 blacklist + V2 + Recommendation
V1 + Autopilot V1 + seven-record ledger gate the build; every frozen
numeric (universe/timeframe/direction, ATR 14, range-swing-low 96,
sweep penetration 0.25 ATR, reclaim window 4, close-in-upper-third,
structure-stop buffer 0.20 ATR, 2R/3R/4R targets, 27/81 bps fee/
floor, anti-cluster 8-bar gap proposal-locked NOT edit token,
sample-size adequacy threshold 20 proposal-locked NOT edit token,
sample tag); missing-or-altered mutations reject; claim locks and
research-only boundaries permanent; zero downstream unlocks; zero
trading-adjacent capability; AST/purity green. Commander safety
suite runs alongside."""

from __future__ import annotations

import ast

import sparta_commander.liquidity_sweep_mean_reversion_v1_family_proposal_contract as c8p
import sparta_commander.liquidity_sweep_mean_reversion_v1_spec_review_contract as c8s
import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as ap
import sparta_commander.strategy_factory_candidate_recommendation_v1_contract as rec
import sparta_commander.strategy_factory_overnight_research_autopilot_v2_contract as oap2
import sparta_commander.strategy_factory_rejected_family_blacklist_v3_contract as bl3


def _record():
    return c8s.build_candidate_8_spec_review()


def test_spec_ready_and_gated_on_full_chain():
    assert c8p.build_candidate_8_family_proposal()["verdict"] == (
        c8p.VERDICT_C8P_READY)
    assert bl3.build_rejected_family_blacklist_v3()["verdict"] == (
        bl3.VERDICT_BL3_READY)
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
    from sparta_commander.volatility_compression_expansion_v1_rejection_record import (  # noqa: E501
        REJECTION_STATUS as C7)
    assert C1 == C2 == C3 == C4 == C5 == C6 == C7 == (
        "REJECTED_KEPT_ON_RECORD")
    record = _record()
    assert record["verdict"] == c8s.VERDICT_C8S_READY
    assert record["blockers"] == []
    assert c8s.validate_candidate_8_spec_review(
        record)["valid"] is True
    assert _record() == record  # determinism
    assert record["ledger_status_seven_records"] == [
        "REJECTED_KEPT_ON_RECORD"] * 7
    assert record["ledger_all_rejected_kept_on_record"] is True


def test_universe_timeframe_direction_frozen():
    record = _record()
    assert record["universe"] == ["BTCUSD"]
    assert record["timeframe"] == "15m"
    assert record["direction"] == "long_only"
    for field, value in (("universe", ["BTCUSD", "ETHUSD"]),
                         ("universe", []),
                         ("timeframe", "1h"),
                         ("timeframe", "4h"),
                         ("direction", "long_or_short"),
                         ("direction", "short_only")):
        tampered = _record()
        tampered[field] = value
        assert c8s.validate_candidate_8_spec_review(
            tampered)["valid"] is False, (field, value)


def test_atr_and_range_swing_low_lookback_frozen():
    record = _record()
    assert record["atr_length"] == 14
    assert record["range_swing_low_lookback_bars"] == 96
    for value in (7, 21, 30, 100):
        tampered = _record()
        tampered["atr_length"] = value
        assert c8s.validate_candidate_8_spec_review(
            tampered)["valid"] is False, value
    for value in (50, 60, 100, 200):
        tampered = _record()
        tampered["range_swing_low_lookback_bars"] = value
        assert c8s.validate_candidate_8_spec_review(
            tampered)["valid"] is False, value


def test_sweep_rule_frozen():
    rule = c8s.SWEEP_RULE
    assert rule["sweep_penetration_atr_multiplier"] == 0.25
    assert rule["range_swing_low_lookback_bars"] == 96
    assert rule["uses_completed_15m_bars_only"] is True
    assert rule["no_future_bars"] is True
    assert rule["no_same_bar_lookahead"] is True
    assert rule["strict_inequality_below_reference_minus_penetration"] \
        is True
    for mutation in ({"sweep_penetration_atr_multiplier": 0.10},
                     {"sweep_penetration_atr_multiplier": 0.50},
                     {"range_swing_low_lookback_bars": 50},
                     {"strict_inequality_below_reference_minus_penetration":
                          False}):
        tampered = _record()
        tampered["sweep_rule"] = dict(c8s.SWEEP_RULE, **mutation)
        assert c8s.validate_candidate_8_spec_review(
            tampered)["valid"] is False, mutation


def test_reclaim_event_frozen():
    rec_ev = c8s.RECLAIM_EVENT
    assert rec_ev["reclaim_window_bars"] == 4
    assert rec_ev["reclaim_close_strictly_above_swept_reference"] is (
        True)
    assert rec_ev["close_in_upper_third_required"] is True
    assert abs(rec_ev["upper_third_fraction"] - (2.0 / 3.0)) < 1e-12
    assert rec_ev["entry_price"] == (
        "close_of_the_reclaim_confirmation_bar")
    assert rec_ev["evaluation_starts"] == (
        "next_15m_bar_after_reclaim_close")
    assert rec_ev["no_intrabar_entry"] is True
    for mutation in ({"reclaim_window_bars": 2},
                     {"reclaim_window_bars": 8},
                     {"reclaim_close_strictly_above_swept_reference":
                          False},
                     {"close_in_upper_third_required": False},
                     {"entry_price": "midprice"},
                     {"entry_price": "next_bar_open"},
                     {"evaluation_starts": "same_bar_as_reclaim_close"},
                     {"no_intrabar_entry": False}):
        tampered = _record()
        tampered["reclaim_event"] = dict(c8s.RECLAIM_EVENT, **mutation)
        assert c8s.validate_candidate_8_spec_review(
            tampered)["valid"] is False, mutation


def test_stop_rule_frozen():
    stop = c8s.STOP_RULE
    assert stop["atr_length"] == 14
    assert stop["structure_stop_buffer_atr_multiplier"] == 0.20
    assert stop["stop_distance_formula"] == (
        "entry_price - (sweep_low - "
        "STRUCTURE_STOP_BUFFER_ATR_MULTIPLIER * ATR14)")
    assert stop["stop_must_be_below_entry"] is True
    assert stop["stop_must_be_below_sweep_low"] is True
    assert stop["never_tightened_after_entry"] is True
    assert stop["invalid_if_stop_distance_not_positive"] is True
    for mutation in ({"atr_length": 7}, {"atr_length": 30},
                     {"structure_stop_buffer_atr_multiplier": 0.0},
                     {"structure_stop_buffer_atr_multiplier": 0.10},
                     {"structure_stop_buffer_atr_multiplier": 0.50},
                     {"stop_distance_formula": "fixed_1_percent"},
                     {"stop_must_be_below_entry": False},
                     {"stop_must_be_below_sweep_low": False},
                     {"never_tightened_after_entry": False}):
        tampered = _record()
        tampered["stop_rule"] = dict(c8s.STOP_RULE, **mutation)
        assert c8s.validate_candidate_8_spec_review(
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
        assert c8s.validate_candidate_8_spec_review(
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
        tampered["fee_geometry"] = dict(c8s.FEE_GEOMETRY,
                                        fee_model_round_trip_bps=value)
        assert c8s.validate_candidate_8_spec_review(
            tampered)["valid"] is False, value
    for value in (0, 27, 54, 80, 82, 100, 162):
        tampered = _record()
        tampered["fee_geometry"] = dict(
            c8s.FEE_GEOMETRY,
            minimum_gross_target_distance_floor_bps=value)
        assert c8s.validate_candidate_8_spec_review(
            tampered)["valid"] is False, value


def test_anti_cluster_is_proposal_locked_8_bar_gap_not_edit_token():
    anti = _record()["anti_cluster_policy"]
    assert anti["min_bars_between_same_symbol_accepted_events_15m"] \
        == 8
    assert anti["is_not_the_single_allowed_c8_edit_token"] is True
    assert anti["applies_before_replay_time_non_overlap"] is True
    assert anti["replay_time_non_overlap_unchanged"] is True
    assert anti["scope"] == "per_symbol"
    assert anti["applied_at"] == (
        "label_emission_time_before_replay_non_overlap")
    assert anti["tie_breaker"] == (
        "keep_the_earlier_event_drop_the_later_one")
    for value in (0, 1, 2, 4, 6, 10, 16, 24):
        tampered = _record()
        tampered["anti_cluster_policy"] = dict(
            c8s.ANTI_CLUSTER_POLICY,
            min_bars_between_same_symbol_accepted_events_15m=value)
        assert c8s.validate_candidate_8_spec_review(
            tampered)["valid"] is False, value
    tampered = _record()
    tampered["anti_cluster_policy"] = dict(
        c8s.ANTI_CLUSTER_POLICY,
        is_not_the_single_allowed_c8_edit_token=False)
    assert c8s.validate_candidate_8_spec_review(
        tampered)["valid"] is False
    edit = _record()["edit_policy"]
    assert edit["maximum_pre_committed_edits"] == 1
    assert edit[
        "anti_cluster_gap_is_proposal_level_locked_not_the_edit_token"
    ] is True
    tampered = _record()
    tampered["edit_policy"] = dict(
        c8s.EDIT_POLICY,
        anti_cluster_gap_is_proposal_level_locked_not_the_edit_token=
        False)
    assert c8s.validate_candidate_8_spec_review(
        tampered)["valid"] is False


def test_sample_size_adequacy_is_proposal_locked_min_20_not_edit_token():
    sa = _record()["sample_size_adequacy_policy"]
    assert sa[
        "minimum_accepted_setups_required_at_labels_review_gate"] == 20
    assert sa[
        "below_threshold_triggers_structural_rejection_without_edit_token"
    ] is True
    assert sa["is_not_the_single_allowed_c8_edit_token"] is True
    assert sa["applies_at_labels_review_gate"] is True
    assert sa["applies_before_any_edit_token_decision"] is True
    for value in (0, 1, 5, 10, 15, 19, 21, 50, 100):
        tampered = _record()
        tampered["sample_size_adequacy_policy"] = dict(
            c8s.SAMPLE_SIZE_ADEQUACY_POLICY,
            minimum_accepted_setups_required_at_labels_review_gate=
            value)
        assert c8s.validate_candidate_8_spec_review(
            tampered)["valid"] is False, value
    tampered = _record()
    tampered["sample_size_adequacy_policy"] = dict(
        c8s.SAMPLE_SIZE_ADEQUACY_POLICY,
        below_threshold_triggers_structural_rejection_without_edit_token=
        False)
    assert c8s.validate_candidate_8_spec_review(
        tampered)["valid"] is False
    tampered = _record()
    tampered["sample_size_adequacy_policy"] = dict(
        c8s.SAMPLE_SIZE_ADEQUACY_POLICY,
        is_not_the_single_allowed_c8_edit_token=False)
    assert c8s.validate_candidate_8_spec_review(
        tampered)["valid"] is False
    edit = _record()["edit_policy"]
    assert edit[
        "sample_size_threshold_is_proposal_level_locked_not_the_edit"
        "_token"] is True
    tampered = _record()
    tampered["edit_policy"] = dict(
        c8s.EDIT_POLICY,
        sample_size_threshold_is_proposal_level_locked_not_the_edit_token=
        False)
    assert c8s.validate_candidate_8_spec_review(
        tampered)["valid"] is False


def test_data_boundary_and_sample_window_frozen():
    boundary = _record()["data_boundary"]
    assert boundary["sample_tag"] == "2026-05-02_2026-06-10"
    assert boundary["no_fetch_ever"] is True
    assert boundary["no_real_time_data"] is True
    assert boundary["staged_data_never_modified"] is True
    for mutation in ({"sample_tag": "2026-01-01_2026-04-01"},
                     {"no_fetch_ever": False},
                     {"staged_data_never_modified": False}):
        tampered = _record()
        tampered["data_boundary"] = dict(c8s.DATA_BOUNDARY, **mutation)
        assert c8s.validate_candidate_8_spec_review(
            tampered)["valid"] is False, mutation


def test_material_differences_from_c1_c7_frozen():
    diffs = _record()["material_differences_from_rejected_families"]
    expected_substrings = (
        ("NOT_c1", "no_ny_fvg_choch_dependency"),
        ("NOT_c2", "breakout_pullback"),
        ("NOT_c3", "trend_continuation"),
        ("NOT_c4", "btc_sol_or_sol_btc_swing"),
        ("NOT_c5", "no_relative_strength_comparison"),
        ("NOT_c6", "multi_symbol_rank"),
        ("NOT_c7", "atr_compression"))
    joined = " || ".join(diffs)
    for marker, phrase in expected_substrings:
        assert marker in joined, marker
        assert phrase in joined, phrase


def test_inherited_lessons_c6_and_c7_frozen():
    lessons = _record()["inherited_lessons"]
    joined = " || ".join(lessons)
    assert "c6_lesson_anti_cluster" in joined
    assert "c7_lesson_sample_size_adequacy" in joined
    assert "not_consuming_edit_token" in joined


def test_chain_blocks_when_ledger_breaks():
    import sparta_commander.liquidity_sweep_mean_reversion_v1_spec_review_contract as mod
    originals = {key: getattr(mod, key) for key in
                 ("C1_STATUS", "C2_STATUS", "C3_STATUS", "C4_STATUS",
                  "C5_STATUS", "C6_STATUS", "C7_STATUS")}
    try:
        for key in originals:
            setattr(mod, key, "APPROVED_FOR_TRADING")
            record = mod.build_candidate_8_spec_review()
            assert record["verdict"] == c8s.VERDICT_C8S_BLOCKED, key
            assert "seven_record_ledger_broken" in record[
                "blockers"], key
            setattr(mod, key, originals[key])
    finally:
        for key, value in originals.items():
            setattr(mod, key, value)
    assert mod.build_candidate_8_spec_review()["verdict"] == (
        c8s.VERDICT_C8S_READY)


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
                "computes_pnl_now",
                "modifies_staged_market_data",
                "authorizes_paper_execution",
                "authorizes_micro_live",
                "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate",
                "unlocks_detector_now", "unlocks_labels_now",
                "unlocks_replay_now", "unlocks_relabel_now",
                "claims_profitability",
                "executes", "writes_files"):
        assert record[key] is False, key
        tampered = _record()
        tampered[key] = True
        assert c8s.validate_candidate_8_spec_review(
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
                 "_edit_token",
                 "sample_size_threshold_is_proposal_level_locked_not"
                 "_edit_token"):
        assert lock in locks, lock
    tampered = _record()
    tampered["claim_locks"] = []
    assert c8s.validate_candidate_8_spec_review(
        tampered)["valid"] is False
    label = c8s.C8S_LABEL
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
    assert c8s.VERDICT_C8S_READY == "CANDIDATE_8_SPEC_REVIEW_READY"
    assert c8s.NEXT_REQUIRED_ACTION == (
        "HUMAN_APPROVED_CANDIDATE_8_DETECTOR_SPEC_AND_DRY_RUN_PATH")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in c8s.NEXT_REQUIRED_ACTION.upper(), banned
    assert c8s.get_candidate_8_spec_review_label() == c8s.C8S_LABEL
    assert c8s.C8S_MODE == "RESEARCH_ONLY"
    src = open(c8s.__file__, encoding="utf-8").read()
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
