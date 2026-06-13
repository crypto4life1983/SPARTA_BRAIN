"""Tests for the Candidate #8 detector-spec + synthetic dry-run
contract (LIQUIDITY_SWEEP_MEAN_REVERSION_V1).

Verifies: chain-gate on the seven-record ledger + C8 family proposal
+ C8 spec review + V3 blacklist + V2 + Recommendation V1 + Autopilot
V1; every frozen numeric (universe/timeframe/direction, ATR 14,
range-swing-low 96, sweep penetration 0.25 ATR, reclaim window 4,
upper-third 2/3, structure-stop buffer 0.20 ATR, 2R/3R/4R targets,
27/81 bps fee/floor, anti-cluster 8-bar gap proposal-locked NOT edit
token, sample-size adequacy 20 proposal-locked NOT edit token, sample
window); pure detector functions correct on synthetic fixtures;
synthetic-only / no I/O; strict-above + upper-third + 4-bar window +
stop geometry + floor + anti-cluster + context (BTCUSD/15m/long-only)
all enforced; AST/purity green; downstream execution gates remain
locked."""

from __future__ import annotations

import ast

import sparta_commander.liquidity_sweep_mean_reversion_v1_detector_spec_dry_run_contract as c8d
import sparta_commander.liquidity_sweep_mean_reversion_v1_family_proposal_contract as c8p
import sparta_commander.liquidity_sweep_mean_reversion_v1_spec_review_contract as c8s
import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as ap
import sparta_commander.strategy_factory_candidate_recommendation_v1_contract as rec
import sparta_commander.strategy_factory_overnight_research_autopilot_v2_contract as oap2
import sparta_commander.strategy_factory_rejected_family_blacklist_v3_contract as bl3


def _record():
    return c8d.build_candidate_8_detector_spec_dry_run()


# ---- chain-gate + verdicts --------------------------------------------------

def test_spec_ready_and_dry_run_passed_and_combined_ready():
    record = _record()
    assert record["verdict"] == c8d.VERDICT_C8D_READY
    assert record["blockers"] == []
    assert record["dry_run"]["verdict"] == (
        c8d.VERDICT_C8D_DRY_RUN_PASSED)
    assert record["dry_run"]["failures"] == []
    assert record["combined_verdict"] == (
        c8d.VERDICT_C8D_SPEC_DRY_RUN_READY)
    assert c8d.validate_candidate_8_detector_spec_dry_run(
        record)["valid"] is True
    assert _record() == record  # determinism


def test_full_chain_gates_certify():
    assert c8p.build_candidate_8_family_proposal()["verdict"] == (
        c8p.VERDICT_C8P_READY)
    assert c8s.build_candidate_8_spec_review()["verdict"] == (
        c8s.VERDICT_C8S_READY)
    assert bl3.build_rejected_family_blacklist_v3()["verdict"] == (
        bl3.VERDICT_BL3_READY)
    assert oap2.build_overnight_research_autopilot_v2_contract()[
        "verdict"] == oap2.VERDICT_OAP2_READY
    assert rec.build_candidate_recommendation()["verdict"] == (
        rec.VERDICT_CR_READY)
    assert ap.build_autopilot_loop_contract()["verdict"] == (
        ap.VERDICT_AP_READY)


def test_seven_record_ledger_status():
    from sparta_commander.btc_sol_long_trend_continuation_v1_result_and_rejection_record_contract import (  # noqa: E501
        REJECTION_STATUS as C3)
    from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (  # noqa: E501
        REJECTION_STATUS as C2)
    from sparta_commander.eth_sol_relative_strength_rejection_record_contract import (  # noqa: E501
        REJECTION_STATUS as C5)
    from sparta_commander.multi_symbol_relative_strength_rotation_filter_rejection_record_contract import (  # noqa: E501
        REJECTION_STATUS as C6)
    from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (  # noqa: E501
        REJECTION_STATUS as C1)
    from sparta_commander.sol_btc_long_1h_swing_structure_rejection_record_contract import (  # noqa: E501
        REJECTION_STATUS as C4)
    from sparta_commander.volatility_compression_expansion_v1_rejection_record import (  # noqa: E501
        REJECTION_STATUS as C7)
    assert C1 == C2 == C3 == C4 == C5 == C6 == C7 == (
        "REJECTED_KEPT_ON_RECORD")
    record = _record()
    assert record["ledger_status_seven_records"] == [
        "REJECTED_KEPT_ON_RECORD"] * 7
    assert record["ledger_all_rejected_kept_on_record"] is True


def test_chain_blocks_when_ledger_breaks():
    import sparta_commander.liquidity_sweep_mean_reversion_v1_detector_spec_dry_run_contract as mod
    originals = {key: getattr(mod, key) for key in
                 ("C1_STATUS", "C2_STATUS", "C3_STATUS", "C4_STATUS",
                  "C5_STATUS", "C6_STATUS", "C7_STATUS")}
    try:
        for key in originals:
            setattr(mod, key, "APPROVED_FOR_TRADING")
            spec = mod.build_candidate_8_detector_spec_contract()
            assert spec["verdict"] == c8d.VERDICT_C8D_BLOCKED, key
            assert "seven_record_ledger_broken" in spec["blockers"], (
                key)
            setattr(mod, key, originals[key])
    finally:
        for key, value in originals.items():
            setattr(mod, key, value)
    assert mod.build_candidate_8_detector_spec_contract()[
        "verdict"] == c8d.VERDICT_C8D_READY


# ---- frozen numerics ------------------------------------------------------

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
        assert c8d.validate_candidate_8_detector_spec_dry_run(
            tampered)["valid"] is False, (field, value)


def test_atr_and_lookback_frozen():
    record = _record()
    assert record["atr_length"] == 14
    assert record["range_swing_low_lookback_bars"] == 96
    for value in (7, 21, 30, 100):
        tampered = _record()
        tampered["atr_length"] = value
        assert c8d.validate_candidate_8_detector_spec_dry_run(
            tampered)["valid"] is False, value
    for value in (50, 100, 200):
        tampered = _record()
        tampered["range_swing_low_lookback_bars"] = value
        assert c8d.validate_candidate_8_detector_spec_dry_run(
            tampered)["valid"] is False, value


def test_sweep_rule_frozen():
    record = _record()
    assert record["sweep_penetration_atr_multiplier"] == 0.25
    assert record[
        "sweep_rule_strict_below_reference_minus_penetration"
    ] is True
    for value in (0.10, 0.30, 0.50, 1.0):
        tampered = _record()
        tampered["sweep_penetration_atr_multiplier"] = value
        assert c8d.validate_candidate_8_detector_spec_dry_run(
            tampered)["valid"] is False, value
    tampered = _record()
    tampered["sweep_rule_strict_below_reference_minus_penetration"] = (
        False)
    assert c8d.validate_candidate_8_detector_spec_dry_run(
        tampered)["valid"] is False


def test_reclaim_rule_frozen():
    record = _record()
    assert record["reclaim_window_bars"] == 4
    assert record[
        "reclaim_close_strictly_above_swept_reference"] is True
    assert abs(record["close_in_upper_third_fraction"]
               - (2.0 / 3.0)) < 1e-12
    for value in (1, 2, 3, 5, 8):
        tampered = _record()
        tampered["reclaim_window_bars"] = value
        assert c8d.validate_candidate_8_detector_spec_dry_run(
            tampered)["valid"] is False, value
    tampered = _record()
    tampered["reclaim_close_strictly_above_swept_reference"] = False
    assert c8d.validate_candidate_8_detector_spec_dry_run(
        tampered)["valid"] is False
    tampered = _record()
    tampered["close_in_upper_third_fraction"] = 0.5
    assert c8d.validate_candidate_8_detector_spec_dry_run(
        tampered)["valid"] is False


def test_structure_stop_rule_frozen():
    record = _record()
    assert record["structure_stop_buffer_atr_multiplier"] == 0.20
    assert record["stop_distance_formula"] == (
        "entry_price - (sweep_low - "
        "STRUCTURE_STOP_BUFFER_ATR_MULTIPLIER * ATR14)")
    assert record["stop_never_tightened_after_entry"] is True
    for value in (0.0, 0.10, 0.30, 0.50, 1.0):
        tampered = _record()
        tampered["structure_stop_buffer_atr_multiplier"] = value
        assert c8d.validate_candidate_8_detector_spec_dry_run(
            tampered)["valid"] is False, value
    tampered = _record()
    tampered["stop_distance_formula"] = "fixed_1_percent"
    assert c8d.validate_candidate_8_detector_spec_dry_run(
        tampered)["valid"] is False
    tampered = _record()
    tampered["stop_never_tightened_after_entry"] = False
    assert c8d.validate_candidate_8_detector_spec_dry_run(
        tampered)["valid"] is False


def test_target_variants_and_price_formula_frozen():
    record = _record()
    assert record["target_variants"] == ["2r", "3r", "4r"]
    assert record["target_price_formula"] == (
        "entry_price + r_multiple * stop_distance")
    for value in (["1r"], ["5r"], ["2r", "3r"], ["2r", "3r", "4r",
                                                  "5r"]):
        tampered = _record()
        tampered["target_variants"] = value
        assert c8d.validate_candidate_8_detector_spec_dry_run(
            tampered)["valid"] is False, value


def test_fee_27_and_floor_81_frozen():
    record = _record()
    assert record["fee_round_trip_bps"] == 27.0
    assert record["target_distance_floor_bps"] == 81.0
    assert record["no_maker_rebate_assumption"] is True
    assert record["no_zero_fee_assumption"] is True
    for value in (0.0, 5.0, 13.0, 26.0, 28.0, 50.0, 100.0):
        tampered = _record()
        tampered["fee_round_trip_bps"] = value
        assert c8d.validate_candidate_8_detector_spec_dry_run(
            tampered)["valid"] is False, value
    for value in (0.0, 27.0, 54.0, 80.0, 82.0, 162.0):
        tampered = _record()
        tampered["target_distance_floor_bps"] = value
        assert c8d.validate_candidate_8_detector_spec_dry_run(
            tampered)["valid"] is False, value
    for key in ("no_maker_rebate_assumption", "no_zero_fee_assumption"):
        tampered = _record()
        tampered[key] = False
        assert c8d.validate_candidate_8_detector_spec_dry_run(
            tampered)["valid"] is False, key


def test_anti_cluster_8_bar_gap_proposal_locked_not_edit_token():
    record = _record()
    assert record["anti_cluster_min_bar_gap"] == 8
    assert record["anti_cluster_tie_breaker"] == (
        "keep_the_earlier_event_drop_the_later_one")
    assert record["anti_cluster_applied_at"] == (
        "label_emission_time_before_replay_non_overlap")
    assert record["anti_cluster_does_not_consume_edit_token"] is True
    for value in (0, 1, 2, 4, 6, 10, 16):
        tampered = _record()
        tampered["anti_cluster_min_bar_gap"] = value
        assert c8d.validate_candidate_8_detector_spec_dry_run(
            tampered)["valid"] is False, value
    tampered = _record()
    tampered["anti_cluster_does_not_consume_edit_token"] = False
    assert c8d.validate_candidate_8_detector_spec_dry_run(
        tampered)["valid"] is False
    tampered = _record()
    tampered["anti_cluster_tie_breaker"] = "keep_the_later_drop_earlier"
    assert c8d.validate_candidate_8_detector_spec_dry_run(
        tampered)["valid"] is False
    tampered = _record()
    tampered["anti_cluster_applied_at"] = "after_replay_evaluation"
    assert c8d.validate_candidate_8_detector_spec_dry_run(
        tampered)["valid"] is False


def test_sample_size_threshold_20_proposal_locked_not_edit_token():
    record = _record()
    assert record["sample_size_adequacy_threshold_min_accepted"] == 20
    assert record[
        "sample_size_adequacy_does_not_consume_edit_token"] is True
    assert record[
        "sample_size_adequacy_enforced_at_labels_review_gate_only"
    ] is True
    for value in (0, 1, 5, 10, 15, 19, 21, 50, 100):
        tampered = _record()
        tampered["sample_size_adequacy_threshold_min_accepted"] = (
            value)
        assert c8d.validate_candidate_8_detector_spec_dry_run(
            tampered)["valid"] is False, value
    for key in (
            "sample_size_adequacy_does_not_consume_edit_token",
            "sample_size_adequacy_enforced_at_labels_review_gate_only"
    ):
        tampered = _record()
        tampered[key] = False
        assert c8d.validate_candidate_8_detector_spec_dry_run(
            tampered)["valid"] is False, key


def test_data_boundary_frozen():
    record = _record()
    assert record["no_fetch_ever"] is True
    assert record["no_real_time_data"] is True
    assert record["staged_data_never_modified"] is True
    for key in ("no_fetch_ever", "no_real_time_data",
                "staged_data_never_modified"):
        tampered = _record()
        tampered[key] = False
        assert c8d.validate_candidate_8_detector_spec_dry_run(
            tampered)["valid"] is False, key


def test_detector_required_fields_and_statuses_frozen():
    record = _record()
    assert tuple(record["detector_required_fields"]) == (
        c8d.C8_SETUP_REQUIRED_FIELDS)
    assert tuple(record["detector_statuses"]) == (
        c8d.C8_DETECTOR_STATUSES)
    tampered = _record()
    tampered["detector_required_fields"] = ["setup_id"]
    assert c8d.validate_candidate_8_detector_spec_dry_run(
        tampered)["valid"] is False
    tampered = _record()
    tampered["detector_statuses"] = ["accepted_for_replay_review"]
    assert c8d.validate_candidate_8_detector_spec_dry_run(
        tampered)["valid"] is False


def test_claim_locks_present():
    record = _record()
    locks = record["claim_locks"]
    for required in (
            "no_profitability_claim", "no_paper_approval",
            "no_live_approval", "no_execution_approval",
            "no_winner_wording",
            "promotion_can_only_produce_a_human_review_record",
            "anti_cluster_gap_is_proposal_level_locked_not_edit_token",
            "sample_size_threshold_is_proposal_level_locked_not_edit"
            "_token",
            "real_candle_detection_gate_locked",
            "labels_gate_locked", "replay_gate_locked",
            "relabel_gate_locked"):
        assert required in locks, required
    tampered = _record()
    tampered["claim_locks"] = []
    assert c8d.validate_candidate_8_detector_spec_dry_run(
        tampered)["valid"] is False


# ---- pure detector function behavior ---------------------------------------

def test_reference_low_no_same_bar_lookahead():
    bars = c8d.fixture_happy_path_sweep_and_reclaim()
    sweep_index = 100
    # The reference at the sweep bar must NOT include the sweep bar's
    # own low.
    ref = c8d.compute_reference_low(bars, sweep_index)
    assert ref is not None
    assert ref == min(float(b["low"])
                      for b in bars[sweep_index - 96:sweep_index])
    # Same-bar lookahead would have changed the reference.
    sweep_low = float(bars[sweep_index]["low"])
    assert ref != sweep_low
    # Insufficient history returns None.
    assert c8d.compute_reference_low(bars, 50) is None


def test_compute_stop_invalid_when_distance_not_positive():
    # Pathological case: entry below sweep_low - buffer (impossible
    # from real reclaim, but the function must defensively reject).
    stop = c8d.compute_stop(entry_price=49500.0, sweep_low=49600.0,
                            atr_at_sweep=50.0)
    assert stop["valid"] is False
    # Real case from the happy path: valid.
    stop_ok = c8d.compute_stop(entry_price=50030.0, sweep_low=49600.0,
                               atr_at_sweep=76.785714)
    assert stop_ok["valid"] is True
    assert stop_ok["stop_distance"] > 0.0
    assert stop_ok["stop_below_entry"] is True
    assert stop_ok["stop_below_sweep_low"] is True


def test_geometry_floor_27_bps_fees_and_81_bps_floor():
    # Distance such that 2r ~ 80 bps (under floor), 3r ~ 120 bps,
    # 4r ~ 160 bps. With entry=50000 and stop_distance=200 ->
    # 2r distance = 400 -> 80 bps; 3r = 600 -> 120 bps.
    out = c8d.geometry_floor_by_variant(entry_price=50000.0,
                                        stop_distance=200.0)
    assert out["floor_pass"]["2r"] is False
    assert out["floor_pass"]["3r"] is True
    assert out["floor_pass"]["4r"] is True
    assert out["any_variant_passes"] is True
    # All-fail case
    out_fail = c8d.geometry_floor_by_variant(entry_price=50000.0,
                                             stop_distance=50.0)
    assert out_fail["floor_pass"] == {"2r": False, "3r": False,
                                      "4r": False}
    assert out_fail["any_variant_passes"] is False


def test_validate_detection_context_raises_off_universe():
    # Inside universe -> no exception.
    c8d.validate_detection_context("BTCUSD", "15m", "long_only")
    # Off-universe symbol.
    try:
        c8d.validate_detection_context("ETHUSD", "15m", "long_only")
        assert False, "must raise on non-BTCUSD"
    except ValueError:
        pass
    # Off-universe timeframe.
    try:
        c8d.validate_detection_context("BTCUSD", "1h", "long_only")
        assert False, "must raise on non-15m"
    except ValueError:
        pass
    # Off-universe direction.
    try:
        c8d.validate_detection_context("BTCUSD", "15m", "short_only")
        assert False, "must raise on non-long_only"
    except ValueError:
        pass


# ---- synthetic-fixture dry-run summary ------------------------------------

def test_dry_run_fixtures_all_pass_and_summary_shape():
    record = _record()
    fixtures = record["dry_run"]["fixtures"]
    assert record["dry_run"]["failures"] == []
    assert record["dry_run"]["uses_synthetic_fixtures_only"] is True
    assert record["dry_run"]["reads_real_candles"] is False
    assert record["dry_run"]["reads_staged_data"] is False
    assert record["dry_run"]["reads_any_files"] is False
    for name in ("valid_sweep_and_reclaim", "insufficient_history",
                 "equality_at_sweep_threshold", "reclaim_too_late",
                 "reclaim_close_equals_reference",
                 "close_not_in_upper_third",
                 "geometry_floor_all_variants_fail",
                 "anti_cluster", "sample_size_adequacy",
                 "context_enforcement"):
        assert name in fixtures, name


def test_valid_sweep_and_reclaim_produces_one_accepted_setup():
    fx = _record()["dry_run"]["fixtures"]["valid_sweep_and_reclaim"]
    assert fx["attempts"] == 1
    assert fx["accepted"] == 1
    assert fx["first_accepted_floor_pass"] == {
        "2r": True, "3r": True, "4r": True}


def test_insufficient_history_emits_zero_attempts():
    fx = _record()["dry_run"]["fixtures"]["insufficient_history"]
    assert fx["attempts"] == 0


def test_equality_at_sweep_threshold_does_not_trigger():
    fx = _record()["dry_run"]["fixtures"][
        "equality_at_sweep_threshold"]
    assert fx["attempts"] == 0


def test_reclaim_too_late_rejects_with_window_failure():
    fx = _record()["dry_run"]["fixtures"]["reclaim_too_late"]
    assert fx["attempts"] == 1
    assert fx["accepted"] == 0
    assert fx["rejected_no_qualifying_reclaim"] == 1


def test_reclaim_close_equals_reference_rejects_strict_above():
    fx = _record()["dry_run"]["fixtures"][
        "reclaim_close_equals_reference"]
    assert fx["attempts"] == 1
    assert fx["accepted"] == 0
    assert fx["rejected_no_qualifying_reclaim"] == 1
    assert ("no_bar_within_window_closed_strictly_above_swept"
            "_reference") in fx["rejection_reasons"]


def test_close_not_in_upper_third_rejects_upper_third():
    fx = _record()["dry_run"]["fixtures"][
        "close_not_in_upper_third"]
    assert fx["attempts"] == 1
    assert fx["accepted"] == 0
    assert fx["rejected_no_qualifying_reclaim"] == 1
    assert ("no_bar_within_window_closed_in_upper_third_of_its_range"
            in fx["rejection_reasons"])


def test_geometry_floor_all_variants_fail_rejects_floor():
    fx = _record()["dry_run"]["fixtures"][
        "geometry_floor_all_variants_fail"]
    assert fx["attempts"] == 1
    assert fx["accepted"] == 0
    assert fx["rejected_geometry_floor"] == 1
    assert fx["floor_pass_by_variant"] == {
        "2r": False, "3r": False, "4r": False}


def test_anti_cluster_keeps_earlier_drops_within_gap_keeps_outside():
    fx = _record()["dry_run"]["fixtures"]["anti_cluster"]
    assert fx["anti_cluster_min_bar_gap"] == 8
    assert fx["anti_cluster_does_not_consume_edit_token"] is True
    assert "synthetic_b_inside" in fx["dropped_ids"]
    assert "synthetic_c_outside" in fx["kept_ids"]
    # at least one earlier kept event (the seed)
    assert len(fx["kept_ids"]) == 2
    assert len(fx["dropped_ids"]) == 1


def test_anti_cluster_filter_direct_invocation_8_bar_gap_boundary():
    # exact 8-bar gap is KEPT (>= 8 is the strict cutoff)
    seed = {"setup_id": "A", "symbol": "BTCUSD",
            "status": "accepted_for_replay_review",
            "event_index": 100, "rejection_reasons": []}
    at_gap = dict(seed); at_gap["setup_id"] = "B"
    at_gap["event_index"] = 108  # exactly +8
    inside = dict(seed); inside["setup_id"] = "C"
    inside["event_index"] = 107  # +7 (within gap)
    result = c8d.apply_anti_cluster_filter([seed, at_gap])
    assert [s["setup_id"] for s in result["kept"]] == ["A", "B"]
    assert result["dropped"] == []
    result2 = c8d.apply_anti_cluster_filter([seed, inside])
    assert [s["setup_id"] for s in result2["kept"]] == ["A"]
    assert [s["setup_id"] for s in result2["dropped"]] == ["C"]
    assert result2["anti_cluster_does_not_consume_edit_token"] is True


def test_sample_size_adequacy_flag_below_and_at_threshold():
    fx = _record()["dry_run"]["fixtures"]["sample_size_adequacy"]
    assert fx["below_minimum_at_dry_run"] is True
    assert fx["at_threshold_below_flag"] is False
    assert fx["enforced_at_labels_review_gate_only"] is True
    assert fx["does_not_consume_edit_token"] is True


def test_context_enforcement_blocks_off_universe_calls():
    fx = _record()["dry_run"]["fixtures"]["context_enforcement"]
    assert fx["symbol_eth"] is True
    assert fx["timeframe_1h"] is True
    assert fx["direction_short"] is True


# ---- spec record safety / capability flags --------------------------------

def test_spec_review_only_flag_is_false_but_synthetic_dry_run_only():
    record = _record()
    # this gate is DETECTOR + dry-run, not spec-review only
    assert record["is_spec_review_only"] is False
    assert record["is_synthetic_fixture_dry_run_only"] is True
    assert record["current_loop_stage"] == "detector_and_label_review"
    assert record["human_review_required"] is True


def test_no_downstream_unlocks_or_capability():
    record = _record()
    for key in ("runs_real_candle_detection",
                "runs_real_detection_now", "labels_now",
                "runs_relabel", "runs_replay",
                "runs_replay_now", "scores_now", "stages_data_now",
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
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate",
                "unlocks_real_candle_detection",
                "unlocks_detector_now",
                "unlocks_labels_now", "unlocks_replay_now",
                "unlocks_relabel_now", "claims_profitability",
                "executes", "writes_files"):
        assert record[key] is False, key
        tampered = _record()
        tampered[key] = True
        assert c8d.validate_candidate_8_detector_spec_dry_run(
            tampered)["valid"] is False, key
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True


def test_label_next_stage_and_label_text():
    record = _record()
    assert record["current_loop_stage"] == "detector_and_label_review"
    assert c8d.VERDICT_C8D_SPEC_DRY_RUN_READY == (
        "CANDIDATE_8_DETECTOR_SPEC_DRY_RUN_READY")
    assert c8d.NEXT_REQUIRED_ACTION == (
        "HUMAN_APPROVED_CANDIDATE_8_DRY_RUN_REVIEW")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER",
                   "LIVE", "BROKER", "EXCHANGE", "AUTOMATION",
                   "ORDER", "TRACK"):
        assert banned not in c8d.NEXT_REQUIRED_ACTION.upper(), banned
    assert c8d.get_candidate_8_detector_label() == c8d.C8D_LABEL
    assert c8d.C8D_MODE == "RESEARCH_ONLY"
    for phrase in ("READ-ONLY", "RESEARCH ONLY", "NOT A RESCUE",
                   "NOT A CLAIM"):
        assert phrase in c8d.C8D_LABEL, phrase
    for banned_phrase in ("WINNER", "PROFITABLE", "EDGE CONFIRMED",
                          "APPROVED FOR PAPER",
                          "APPROVED FOR LIVE"):
        assert banned_phrase not in c8d.C8D_LABEL.upper(), banned_phrase


# ---- module purity --------------------------------------------------------

def test_module_purity_no_banned_imports_no_io_no_main():
    src = open(c8d.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir",
                 "rmdir", "rename", "touch("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt",
                   "smtplib", "subprocess", "websockets", "aiohttp",
                   "schedule", "apscheduler", "threading", "asyncio",
                   "time", "sched", "telegram", "email", "csv",
                   "pandas", "pathlib", "os", "io", "json", "shutil",
                   "databento", "ssl", "ftplib", "hashlib",
                   "statistics", "random"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods), imported & banned_mods
    # No open() / no exec() / no eval() invocations
    for call in ast.walk(tree):
        if not isinstance(call, ast.Call):
            continue
        name = (call.func.attr if isinstance(call.func, ast.Attribute)
                else getattr(call.func, "id", ""))
        assert name not in ("open", "exec", "eval", "compile"), name
