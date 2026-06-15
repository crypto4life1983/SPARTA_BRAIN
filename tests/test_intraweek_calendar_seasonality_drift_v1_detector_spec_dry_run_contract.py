"""Tests for the Candidate #10 detector spec + synthetic dry-run
contract (INTRAWEEK_CALENDAR_SEASONALITY_DRIFT_V1).

Verifies: chain-gate on the nine-record ledger + the pushed C10 family
proposal + C10 spec review + V5 + V4 + V3 + V2 + Recommendation V1 +
Autopilot V1; every frozen numeric (universe/timeframe/direction,
cardinality 1, in-sample and out-of-sample windows, holding horizon 5,
ATR 14, structure-stop multiplier 1.5, 2R/3R/4R targets, 27/81 bps
fee/floor, anti-cluster 5-bar gap proposal-locked NOT edit token,
sample-size adequacy 100 proposal-locked NOT edit token, explicit-edge-
argument field proposal-locked NOT edit token, single-trigger design
proposal-locked NOT edit token); DATA-DETERMINED single deterministic
ISO-weekday calendar trigger (bucket value never hard-coded); purity of
the trigger (no price/volume/excursion condition); in-sample vs out-of-
sample separation; entry at the triggering bar close with no intrabar
entry; ATR/stop/target/floor geometry; anti-cluster 5-bar behavior;
sample-size adequacy flag; context enforcement rejects off-symbol/off-
timeframe/non-long/off-bucket; the synthetic dry-run passes; AST/purity
green; downstream execution gates locked.

PERFORMANCE: build_candidate_10_detector_spec_dry_run() chain-builds
the C10 spec review (whose own chain includes the C10 proposal +
drafter, ~9 min per build). The whole suite therefore builds the deep
chain only TWICE: once for the shared module-level record _R, and once
in the ledger-break test. The scanner/selector/anti-cluster/sample-size
fixtures are PURE and fast -- those tests call them directly without
any chain rebuild."""

from __future__ import annotations

import ast
import copy

import sparta_commander.intraweek_calendar_seasonality_drift_v1_detector_spec_dry_run_contract as c10d
import sparta_commander.intraweek_calendar_seasonality_drift_v1_family_proposal_contract as c10p
import sparta_commander.intraweek_calendar_seasonality_drift_v1_spec_review_contract as c10s

_R = c10d.build_candidate_10_detector_spec_dry_run()


def _record():
    return copy.deepcopy(_R)


# ---- chain gate + combined ready verdict ---------------------------------

def test_spec_dry_run_ready_and_gated_on_full_chain():
    assert _R["verdict"] == c10d.VERDICT_C10D_READY
    assert _R["blockers"] == []
    assert _R["combined_verdict"] == c10d.VERDICT_C10D_SPEC_DRY_RUN_READY
    assert _R["dry_run"]["verdict"] == c10d.VERDICT_C10D_DRY_RUN_PASSED
    assert _R["dry_run"]["failures"] == []
    assert c10d.validate_candidate_10_detector_spec_dry_run(
        _R)["valid"] is True
    assert _R["ledger_status_nine_records"] == [
        "REJECTED_KEPT_ON_RECORD"] * 9
    assert _R["ledger_all_rejected_kept_on_record"] is True
    # determinism of the pure validator on a fresh copy
    assert c10d.validate_candidate_10_detector_spec_dry_run(
        _record())["valid"] is True


def test_dry_run_does_not_touch_real_data():
    dr = _R["dry_run"]
    assert dr["uses_synthetic_fixtures_only"] is True
    assert dr["reads_real_candles"] is False
    assert dr["reads_staged_data"] is False
    assert dr["reads_any_files"] is False


def test_chain_blocks_when_ledger_breaks():
    mod = c10d
    original = mod.C1_STATUS
    try:
        mod.C1_STATUS = "APPROVED_FOR_TRADING"
        broken = mod.build_candidate_10_detector_spec_contract()
        assert broken["verdict"] == mod.VERDICT_C10D_BLOCKED
        assert "nine_record_ledger_broken" in broken["blockers"]
    finally:
        mod.C1_STATUS = original
    assert mod.C1_STATUS == "REJECTED_KEPT_ON_RECORD"
    # chain heals after restore
    assert mod.build_candidate_10_detector_spec_contract()[
        "verdict"] == mod.VERDICT_C10D_READY


# ---- frozen numerics ------------------------------------------------------

def test_universe_timeframe_direction_cardinality_windows():
    assert c10d.UNIVERSE == ("BTCUSD",)
    assert c10d.TIMEFRAME == "1d"
    assert c10d.DIRECTION == "long_only"
    assert c10d.FAVORABLE_WEEKDAY_BUCKET_CARDINALITY == 1
    assert c10d.IN_SAMPLE_SELECTION_WINDOW == ("2019-01-01",
                                               "2022-12-31")
    assert c10d.OUT_OF_SAMPLE_WINDOW == ("2023-01-01", "2025-12-31")
    assert _R["universe"] == ["BTCUSD"]
    assert _R["timeframe"] == "1d"
    assert _R["direction"] == "long_only"
    assert _R["favorable_weekday_bucket_cardinality"] == 1
    assert _R["in_sample_selection_window"] == ["2019-01-01",
                                                "2022-12-31"]
    assert _R["out_of_sample_window"] == ["2023-01-01", "2025-12-31"]


def test_holding_horizon_5_and_atr_14_and_stop_1_5():
    assert c10d.HOLDING_HORIZON_BARS == 5
    assert c10d.ATR_LENGTH == 14
    assert c10d.STRUCTURE_STOP_ATR_MULTIPLIER == 1.5
    assert _R["holding_horizon_bars"] == 5
    assert _R["fixed_horizon_exit_at_close"] is True
    assert _R["atr_length"] == 14
    assert _R["atr_is_risk_control_only_never_entry_trigger"] is True
    assert _R["structure_stop_atr_multiplier"] == 1.5
    assert _R["stop_price_formula"] == (
        "entry_price - STRUCTURE_STOP_ATR_MULTIPLIER * "
        "ATR14_at_entry_bar")
    assert _R["stop_never_tightened_after_entry"] is True


def test_fee_27_floor_81_targets_and_formula_locked():
    assert c10d.FEE_ROUND_TRIP_BPS == 27.0
    assert c10d.TARGET_DISTANCE_FLOOR_BPS == 81.0
    assert c10d.TARGET_VARIANTS == (("2r", 2.0), ("3r", 3.0),
                                    ("4r", 4.0))
    assert _R["fee_round_trip_bps"] == 27.0
    assert _R["target_distance_floor_bps"] == 81.0
    assert _R["no_maker_rebate_assumption"] is True
    assert _R["no_zero_fee_assumption"] is True
    assert _R["target_variants"] == ["2r", "3r", "4r"]
    assert _R["target_price_formula"] == (
        "entry_price + r_multiple * stop_distance")


# ---- the single data-determined calendar trigger -------------------------

def test_calendar_trigger_single_data_determined_bucket():
    bars = c10d.fixture_bucket_selection_data_determined()
    sel = c10d.select_favorable_weekday_bucket(bars)
    # weekday 3 is the unique in-sample winner that clears 81 bps
    assert sel["favorable_weekday_bucket"] == 3
    assert sel["favorable_weekday_bucket_cardinality"] == 1
    assert sel["cleared_81_bps_floor"] is True
    assert sel["bucket_value_is_data_determined_not_hardcoded"] is True
    assert sel["selected_on_in_sample_window_only"] is True
    cleared = [w for w, bps in sel["per_weekday_mean_bps"].items()
               if bps >= c10d.TARGET_DISTANCE_FLOOR_BPS]
    assert cleared == [3]
    # the spec record advertises data-determined, not hard-coded
    assert _R["favorable_weekday_bucket_value_is_data_determined"] is \
        True
    assert _R["favorable_weekday_bucket_value_is_hardcoded"] is False
    assert _R["trigger_is_single_iso_weekday_calendar_condition"] is \
        True


def test_no_price_volume_excursion_condition_in_trigger():
    bars = c10d.fixture_no_price_condition()
    setups = c10d.scan_c10_setups(bars, 3, "BTCUSD")
    # only the weekday-3 calendar bar triggers; the wild weekday-4
    # crash bar does NOT trigger -- price is never read
    triggered_weekdays = sorted(
        set(s["trigger_iso_weekday"] for s in setups))
    assert triggered_weekdays == [3]
    accepted = [s for s in setups
                if s["status"] == "accepted_for_replay_review"]
    assert len(accepted) == 1
    for s in setups:
        assert s["uses_no_price_condition"] is True
        assert s["uses_no_volume_condition"] is True
        assert s["uses_no_excursion_condition"] is True
    assert _R["uses_no_price_condition"] is True
    assert _R["uses_no_volume_condition"] is True
    assert _R["uses_no_excursion_condition"] is True


def test_in_sample_out_of_sample_separation():
    bars = c10d.fixture_bucket_selection_data_determined()
    in_sample = c10d.select_favorable_weekday_bucket(
        bars, in_sample_window=c10d.IN_SAMPLE_SELECTION_WINDOW)
    out_of_sample = c10d.select_favorable_weekday_bucket(
        bars, in_sample_window=c10d.OUT_OF_SAMPLE_WINDOW)
    # the OOS poison would crown a different weekday -- selection on the
    # in-sample window must ignore it entirely
    assert in_sample["favorable_weekday_bucket"] == 3
    assert out_of_sample["favorable_weekday_bucket"] != 3
    assert _R["bucket_selected_on_in_sample_window_only"] is True
    assert _R["bucket_held_fixed_for_out_of_sample"] is True


def test_entry_at_triggering_bar_close_no_intrabar():
    bars = c10d.fixture_geometry_happy_path()
    setups = c10d.scan_c10_setups(bars, 3, "BTCUSD")
    accepted = [s for s in setups
                if s["status"] == "accepted_for_replay_review"]
    assert len(accepted) == 1
    a = accepted[0]
    assert a["entry_index"] == a["trigger_index"]
    assert a["entry_price"] == float(bars[a["trigger_index"]]["close"])
    assert a["entry_is_at_triggering_bar_close"] is True
    assert a["entry_is_intrabar"] is False
    assert a["exit_index"] == a["entry_index"] + c10d.HOLDING_HORIZON_BARS
    assert _R["entry_rule_close_of_triggering_completed_daily_bar"] is \
        True
    assert _R["entry_index_equals_trigger_index"] is True
    assert _R["no_intrabar_entry"] is True


# ---- ATR / stop / target / floor geometry --------------------------------

def test_atr_stop_target_floor_geometry_happy_path():
    bars = c10d.fixture_geometry_happy_path()
    setups = c10d.scan_c10_setups(bars, 3, "BTCUSD")
    accepted = [s for s in setups
                if s["status"] == "accepted_for_replay_review"]
    assert len(accepted) == 1
    a = accepted[0]
    # flat bars half-range 80 -> ATR(14)=160 -> stop_distance=240
    assert a["atr_at_entry_bar"] == 160.0
    assert a["stop_distance"] == 240.0
    assert a["stop_below_entry"] is True
    assert a["geometry_floor_pass_by_variant"] == {
        "2r": True, "3r": True, "4r": True}
    # 2r = 480/50000 = 96 bps, 3r = 144, 4r = 192
    assert a["target_distance_bps_2r"] == 96.0
    assert a["target_distance_bps_3r"] == 144.0
    assert a["target_distance_bps_4r"] == 192.0


def test_geometry_floor_all_variants_fail_rejected():
    bars = c10d.fixture_geometry_floor_all_variants_fail()
    setups = c10d.scan_c10_setups(bars, 3, "BTCUSD")
    accepted = [s for s in setups
                if s["status"] == "accepted_for_replay_review"]
    rejected = [s for s in setups
                if s["status"] == "rejected_geometry_floor"]
    assert accepted == []
    assert len(rejected) == 1
    assert rejected[0]["geometry_floor_pass_by_variant"] == {
        "2r": False, "3r": False, "4r": False}


def test_no_evaluation_bar_rejection():
    # 18 flat bars: weekday-3 trigger at index 16 has ATR but 16+5 >= 18
    bars = [c10d._flat_bar(2020, i, 50000.0, 80.0) for i in range(18)]
    setups = c10d.scan_c10_setups(bars, 3, "BTCUSD")
    accepted = [s for s in setups
                if s["status"] == "accepted_for_replay_review"]
    rejected = [s for s in setups
                if s["status"] == "rejected_no_evaluation_bar"]
    assert accepted == []
    assert len(rejected) == 1


# ---- anti-cluster (proposal-locked, not edit token) ----------------------

def test_anti_cluster_5_bar_gap_behavior():
    base = {"setup_id": "a", "symbol": "BTCUSD",
            "status": "accepted_for_replay_review",
            "entry_index": 200, "rejection_reasons": []}
    inside = dict(base, setup_id="b_inside",
                  entry_index=base["entry_index"] + 3)
    outside = dict(base, setup_id="c_outside",
                   entry_index=base["entry_index"] + 5)
    result = c10d.apply_anti_cluster_filter([base, inside, outside])
    kept = set(s["setup_id"] for s in result["kept"])
    dropped = set(s["setup_id"] for s in result["dropped"])
    assert kept == {"a", "c_outside"}
    assert dropped == {"b_inside"}
    assert result["anti_cluster_min_bar_gap"] == 5
    assert result["tie_breaker"] == (
        "keep_the_earlier_event_drop_the_later_one")
    assert result["anti_cluster_does_not_consume_edit_token"] is True


def test_anti_cluster_proposal_locked_not_edit_token():
    assert c10d.ANTI_CLUSTER_MIN_BAR_GAP == 5
    assert _R["anti_cluster_min_bar_gap"] == 5
    assert _R["anti_cluster_does_not_consume_edit_token"] is True
    assert _R["anti_cluster_applied_at"] == (
        "label_emission_time_before_replay_non_overlap")
    assert _R["one_fire_per_iso_week_by_construction"] is True


# ---- sample-size adequacy (proposal-locked, not edit token) --------------

def test_sample_size_100_flag_behavior():
    below = c10d.check_sample_size_adequacy(
        [{"entry_index": i} for i in range(3)])
    at = c10d.check_sample_size_adequacy(
        [{"entry_index": i}
         for i in range(
             c10d.SAMPLE_SIZE_ADEQUACY_THRESHOLD_MIN_ACCEPTED)])
    assert below["below_minimum_at_dry_run"] is True
    assert at["below_minimum_at_dry_run"] is False
    assert below["minimum_required_at_labels_review_gate"] == 100
    assert below["enforced_at_labels_review_gate_only"] is True
    assert below["does_not_consume_edit_token"] is True


def test_sample_size_proposal_locked_not_edit_token():
    assert c10d.SAMPLE_SIZE_ADEQUACY_THRESHOLD_MIN_ACCEPTED == 100
    assert _R["sample_size_adequacy_threshold_min_accepted"] == 100
    assert _R["sample_size_adequacy_does_not_consume_edit_token"] is \
        True
    assert _R[
        "sample_size_adequacy_enforced_at_labels_review_gate_only"] is \
        True


# ---- explicit edge argument + single-trigger design ----------------------

def test_explicit_edge_argument_carried_forward_and_locked():
    assert _R["explicit_edge_argument_beyond_pattern_geometry"] == (
        c10p.EXPLICIT_EDGE_ARGUMENT_BEYOND_PATTERN_GEOMETRY)
    assert _R["explicit_edge_argument_does_not_consume_edit_token"] is \
        True


def test_single_trigger_design_proposal_locked_not_edit_token():
    assert _R["single_trigger_design_does_not_consume_edit_token"] is \
        True
    assert _R["selection_metric"] == c10d.SELECTION_METRIC


# ---- context enforcement -------------------------------------------------

def test_context_enforcement_off_universe_and_bucket():
    import pytest
    bars = c10d.fixture_geometry_happy_path()
    with pytest.raises(ValueError):
        c10d.scan_c10_setups(bars, 3, "ETHUSD")
    with pytest.raises(ValueError):
        c10d.scan_c10_setups(bars, 3, "BTCUSD", timeframe="1h")
    with pytest.raises(ValueError):
        c10d.scan_c10_setups(bars, 3, "BTCUSD", direction="short_only")
    with pytest.raises(ValueError):
        c10d.scan_c10_setups("not a list", 3, "BTCUSD")
    with pytest.raises(ValueError):
        c10d.scan_c10_setups(bars, 0, "BTCUSD")
    with pytest.raises(ValueError):
        c10d.scan_c10_setups(bars, 8, "BTCUSD")
    with pytest.raises(ValueError):
        c10d.scan_c10_setups(bars, True, "BTCUSD")


# ---- dry run end-to-end --------------------------------------------------

def test_dry_run_passes_all_fixtures():
    dr = c10d.run_c10_detector_dry_run()
    assert dr["verdict"] == c10d.VERDICT_C10D_DRY_RUN_PASSED
    assert dr["failures"] == []
    fx = dr["fixtures"]
    assert fx["bucket_selection_data_determined"][
        "favorable_weekday_bucket"] == 3
    assert fx["geometry_happy_path"]["accepted"] == 1
    assert fx["geometry_floor_all_variants_fail"][
        "rejected_geometry_floor"] == 1
    assert fx["no_price_condition"]["triggered_weekdays"] == [3]
    assert fx["no_evaluation_bar"]["rejected_no_evaluation_bar"] == 1
    assert all(fx["context_enforcement"].values())


# ---- spec-only: no downstream unlocks, no capability ---------------------

def test_detector_spec_only_no_downstream_unlocks_or_capability():
    assert _R["is_synthetic_fixture_dry_run_only"] is True
    assert _R["is_spec_review_only"] is False
    assert _R["is_a_rescue_attempt"] is False
    assert _R["human_review_required"] is True
    for key in ("paper_trading_gate_locked", "micro_live_gate_locked",
                "live_gate_locked"):
        assert _R[key] is True
    for key in ("executes", "writes_files", "labels_now",
                "runs_real_candle_detection", "runs_relabel",
                "runs_replay", "runs_real_detection_now",
                "runs_replay_now", "scores_now", "stages_data_now",
                "fetches_data", "calls_api", "uses_network",
                "uses_credentials", "uses_wallet", "uses_account",
                "connects_broker", "connects_exchange",
                "uses_real_money", "contains_order_logic",
                "contains_portfolio_allocation_logic",
                "starts_scheduler", "sends_notifications",
                "auto_commits", "auto_pushes", "creates_runners_now",
                "creates_data_artifacts_now",
                "creates_detector_implementation_now",
                "computes_pnl_now", "modifies_staged_market_data",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate",
                "unlocks_real_candle_detection",
                "unlocks_detector_now", "unlocks_labels_now",
                "unlocks_replay_now", "unlocks_relabel_now",
                "claims_profitability"):
        assert _R[key] is False, key


def test_claim_locks_and_label_and_next_action():
    assert _R["claim_locks"] == list(c10d.CLAIM_LOCKS)
    assert "no_profitability_claim" in c10d.CLAIM_LOCKS
    assert ("single_trigger_design_is_proposal_level_locked_not_edit"
            "_token") in c10d.CLAIM_LOCKS
    assert ("favorable_weekday_bucket_value_is_data_determined_not"
            "_hardcoded") in c10d.CLAIM_LOCKS
    assert "RESEARCH ONLY" in c10d.C10D_LABEL
    assert "NOT A CLAIM" in c10d.C10D_LABEL
    assert c10d.C10D_MODE == "RESEARCH_ONLY"
    assert _R["next_required_action"] == (
        "HUMAN_APPROVED_CANDIDATE_10_DRY_RUN_REVIEW")
    assert _R["current_loop_stage"] == "detector_and_label_review"


# ---- validator catches tampering -----------------------------------------

def test_validator_catches_tampering():
    bad_floor = _record()
    bad_floor["target_distance_floor_bps"] = 40.0
    assert c10d.validate_candidate_10_detector_spec_dry_run(
        bad_floor)["valid"] is False
    bad_stop = _record()
    bad_stop["structure_stop_atr_multiplier"] = 2.0
    assert c10d.validate_candidate_10_detector_spec_dry_run(
        bad_stop)["valid"] is False
    bad_card = _record()
    bad_card["favorable_weekday_bucket_cardinality"] = 2
    assert c10d.validate_candidate_10_detector_spec_dry_run(
        bad_card)["valid"] is False
    hardcoded = _record()
    hardcoded["favorable_weekday_bucket_value_is_hardcoded"] = True
    assert c10d.validate_candidate_10_detector_spec_dry_run(
        hardcoded)["valid"] is False
    price_leak = _record()
    price_leak["uses_no_price_condition"] = False
    assert c10d.validate_candidate_10_detector_spec_dry_run(
        price_leak)["valid"] is False
    capability_leak = _record()
    capability_leak["executes"] = True
    assert c10d.validate_candidate_10_detector_spec_dry_run(
        capability_leak)["valid"] is False
    not_dict = c10d.validate_candidate_10_detector_spec_dry_run("x")
    assert not_dict["valid"] is False


# ---- AST purity ----------------------------------------------------------

def test_module_purity_no_banned_imports_no_open_no_main():
    src = open(c10d.__file__, encoding="utf-8").read()
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
                   "databento", "ssl", "ftplib", "datetime",
                   "hashlib", "statistics", "random"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods), imported & banned_mods
    for call in ast.walk(tree):
        if not isinstance(call, ast.Call):
            continue
        name = (call.func.attr if isinstance(call.func, ast.Attribute)
                else getattr(call.func, "id", ""))
        assert name not in ("open", "exec", "eval", "compile"), name
