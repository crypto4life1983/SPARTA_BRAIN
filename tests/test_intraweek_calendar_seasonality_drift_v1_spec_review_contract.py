"""Tests for the Candidate #10 strategy spec review contract
(INTRAWEEK_CALENDAR_SEASONALITY_DRIFT_V1).

Verifies: chain-gate on the nine-record ledger + the pushed C10 family
proposal + V5 + V4 + V3 + V2 + Recommendation V1 + Autopilot V1; every
frozen numeric (universe/timeframe/direction, cardinality 1, in-sample
and out-of-sample windows, holding horizon 5, ATR 14, structure-stop
multiplier 1.5, 2R/3R/4R targets, 27/81 bps fee/floor, anti-cluster
5-bar gap proposal-locked NOT edit token, sample-size adequacy 100
proposal-locked NOT edit token, explicit-edge-argument field
proposal-locked NOT edit token, single-trigger design proposal-locked
NOT edit token, sample tag); single deterministic calendar trigger
purity (no price/volume/excursion condition); explicit edge argument
carried forward verbatim from the C10 family proposal; edit-token
eligible parameters; material differences from C1-C9; AST/purity
green; downstream execution gates locked.

PERFORMANCE: build_candidate_10_spec_review() chain-builds the C10
family proposal (whose own chain includes the drafter, ~9 min per
build). The whole suite therefore builds the deep chain only TWICE:
once for the shared module-level record _R, and once in the
ledger-break test. Every other test mutates copy.deepcopy(_R) and
calls the pure validator -- no rebuild."""

from __future__ import annotations

import ast
import copy

import sparta_commander.intraweek_calendar_seasonality_drift_v1_family_proposal_contract as c10p
import sparta_commander.intraweek_calendar_seasonality_drift_v1_spec_review_contract as c10s
import sparta_commander.strategy_factory_rejected_family_blacklist_v5_contract as bl5

_R = c10s.build_candidate_10_spec_review()


def _record():
    return copy.deepcopy(_R)


# ---- chain gate + ready verdict -------------------------------------------

def test_spec_ready_and_gated_on_full_chain():
    # Assert on the verdicts the shared record already embedded, rather
    # than rebuilding each upstream contract (every rebuild is minutes).
    assert _R["verdict"] == c10s.VERDICT_C10S_READY
    assert _R["blockers"] == []
    assert c10s.validate_candidate_10_spec_review(_R)["valid"] is True
    assert _R["candidate_10_proposal_verdict"] == c10p.VERDICT_C10P_READY
    assert _R["v5_blacklist_verdict"] == bl5.VERDICT_BL5_READY
    assert _R["v4_blacklist_verdict"] is not None
    assert _R["v3_blacklist_verdict"] is not None
    assert _R["v2_verdict"] is not None
    assert _R["recommendation_verdict"] is not None
    assert _R["autopilot_loop_verdict"] is not None
    assert _R["ledger_status_nine_records"] == [
        "REJECTED_KEPT_ON_RECORD"] * 9
    assert _R["ledger_all_rejected_kept_on_record"] is True
    # determinism of the pure validator on a fresh copy
    assert c10s.validate_candidate_10_spec_review(
        _record())["valid"] is True


def test_chain_blocks_when_ledger_breaks():
    # ONE rebuild only: flip a single ledger status, rebuild once,
    # assert BLOCKED, restore in finally, witness restoration via _R.
    import sparta_commander.intraweek_calendar_seasonality_drift_v1_spec_review_contract as mod
    original = mod.C1_STATUS
    try:
        mod.C1_STATUS = "APPROVED_FOR_TRADING"
        record = mod.build_candidate_10_spec_review()
        assert record["verdict"] == c10s.VERDICT_C10S_BLOCKED
        assert "nine_record_ledger_broken" in record["blockers"]
        assert record["ledger_all_rejected_kept_on_record"] is False
    finally:
        mod.C1_STATUS = original
    # the shared record stays READY; restoration is real
    assert _R["verdict"] == c10s.VERDICT_C10S_READY
    assert mod.C1_STATUS == "REJECTED_KEPT_ON_RECORD"


# ---- frozen universe + timeframe + direction + cardinality + windows ---

def test_universe_timeframe_direction_cardinality_windows():
    assert _R["universe"] == ["BTCUSD"]
    assert _R["timeframe"] == "1d"
    assert _R["direction"] == "long_only"
    assert _R["favorable_weekday_bucket_cardinality"] == 1
    assert _R["in_sample_selection_window"] == "2019-01-01_2022-12-31"
    assert _R["out_of_sample_window"] == "2023-01-01_2025-12-31"
    for field, value in (("universe", ["BTCUSD", "ETHUSD"]),
                         ("universe", []),
                         ("timeframe", "1h"),
                         ("timeframe", "4h"),
                         ("direction", "short_only"),
                         ("favorable_weekday_bucket_cardinality", 2),
                         ("favorable_weekday_bucket_cardinality", 0),
                         ("in_sample_selection_window",
                          "2019-01-01_2025-12-31"),
                         ("out_of_sample_window",
                          "2019-01-01_2022-12-31")):
        tampered = _record()
        tampered[field] = value
        assert c10s.validate_candidate_10_spec_review(
            tampered)["valid"] is False, (field, value)


# ---- single deterministic calendar trigger purity ----------------------

def test_calendar_trigger_is_single_deterministic_and_pure():
    ct = _R["calendar_trigger_rule"]
    assert ct["is_a_single_deterministic_calendar_trigger"] is True
    assert ct["favorable_weekday_bucket_cardinality"] == 1
    assert ct["bucket_value_is_data_determined_not_hardcoded"] is True
    assert ct["uses_completed_daily_bars_only"] is True
    assert ct["no_future_bars"] is True
    assert ct["no_same_bar_lookahead"] is True
    assert ct["uses_no_price_pattern_condition"] is True
    assert ct["uses_no_volume_condition"] is True
    assert ct["uses_no_statistical_excursion_condition"] is True
    assert ct["in_sample_selection_window"] == "2019-01-01_2022-12-31"
    assert ct["out_of_sample_window"] == "2023-01-01_2025-12-31"
    for key in ("is_a_single_deterministic_calendar_trigger",
                "uses_no_price_pattern_condition",
                "uses_no_volume_condition",
                "uses_no_statistical_excursion_condition",
                "no_same_bar_lookahead", "no_future_bars",
                "bucket_value_is_data_determined_not_hardcoded"):
        tampered = _record()
        tampered["calendar_trigger_rule"][key] = False
        assert c10s.validate_candidate_10_spec_review(
            tampered)["valid"] is False, key


# ---- frozen entry rule -------------------------------------------------

def test_entry_rule_close_of_triggering_bar_no_intrabar():
    er = _R["entry_rule"]
    assert er["entry_price"] == (
        "close_of_the_triggering_completed_daily_bar")
    assert er["no_intrabar_entry"] is True
    assert er["no_same_bar_lookahead"] is True
    assert er["evaluation_starts"] == (
        "next_daily_bar_after_entry_bar_close")
    for key in ("no_intrabar_entry", "no_same_bar_lookahead"):
        tampered = _record()
        tampered["entry_rule"][key] = False
        assert c10s.validate_candidate_10_spec_review(
            tampered)["valid"] is False, key


# ---- frozen fixed-horizon exit -----------------------------------------

def test_holding_horizon_5_bars_frozen():
    assert _R["holding_horizon_bars"] == 5
    xr = _R["exit_rule"]
    assert xr["holding_horizon_bars"] == 5
    assert xr["applied_at_replay_time"] is True
    assert xr["is_not_an_entry_gate_rule"] is True
    for value in (1, 3, 4, 6, 10, 96):
        tampered = _record()
        tampered["holding_horizon_bars"] = value
        assert c10s.validate_candidate_10_spec_review(
            tampered)["valid"] is False, value
        tampered = _record()
        tampered["exit_rule"]["holding_horizon_bars"] = value
        assert c10s.validate_candidate_10_spec_review(
            tampered)["valid"] is False, value


# ---- frozen ATR + structure-stop rule ----------------------------------

def test_atr_14_and_structure_stop_multiplier_1_5_frozen():
    assert _R["atr_length"] == 14
    assert _R[
        "atr_uses_completed_daily_bars_only_standard_true_range"
    ] is True
    assert _R["structure_stop_atr_multiplier"] == 1.5
    stop = _R["stop_rule"]
    assert stop["atr_length"] == 14
    assert stop["structure_stop_atr_multiplier"] == 1.5
    assert stop["stop_price_formula"] == (
        "entry_price - STRUCTURE_STOP_ATR_MULTIPLIER * "
        "ATR14_at_entry_bar")
    assert stop["stop_distance_formula"] == "entry_price - stop_price"
    assert stop["stop_is_risk_control_only_not_an_entry_trigger"] is (
        True)
    assert stop["stop_must_be_below_entry"] is True
    assert stop["invalid_if_stop_distance_not_positive"] is True
    assert stop["never_tightened_after_entry"] is True
    for value in (7, 21, 30):
        tampered = _record()
        tampered["atr_length"] = value
        assert c10s.validate_candidate_10_spec_review(
            tampered)["valid"] is False, value
    for value in (0.0, 1.0, 1.25, 2.0, 3.0):
        tampered = _record()
        tampered["structure_stop_atr_multiplier"] = value
        assert c10s.validate_candidate_10_spec_review(
            tampered)["valid"] is False, value
        tampered = _record()
        tampered["stop_rule"]["structure_stop_atr_multiplier"] = value
        assert c10s.validate_candidate_10_spec_review(
            tampered)["valid"] is False, value
    for key in ("stop_must_be_below_entry",
                "invalid_if_stop_distance_not_positive",
                "never_tightened_after_entry",
                "stop_is_risk_control_only_not_an_entry_trigger"):
        tampered = _record()
        tampered["stop_rule"][key] = False
        assert c10s.validate_candidate_10_spec_review(
            tampered)["valid"] is False, key


# ---- frozen targets + fee geometry -------------------------------------

def test_target_variants_2r_3r_4r_and_formula_locked():
    targets = _R["target_rules"]
    assert targets["variants"] == ["2r", "3r", "4r"]
    assert targets["no_new_variants_after_label_freeze"] is True
    assert targets["target_price_formula"] == (
        "entry_price + r_multiple * stop_distance")
    for value in (["1r"], ["5r"], ["2r", "3r"],
                  ["2r", "3r", "4r", "5r"]):
        tampered = _record()
        tampered["target_rules"]["variants"] = value
        assert c10s.validate_candidate_10_spec_review(
            tampered)["valid"] is False, value
    tampered = _record()
    tampered["target_rules"]["target_price_formula"] = "tampered"
    assert c10s.validate_candidate_10_spec_review(
        tampered)["valid"] is False


def test_fee_27_and_floor_81_locked():
    fee = _R["fee_geometry"]
    assert fee["fee_model_round_trip_bps"] == 27
    assert fee["minimum_gross_target_distance_floor_bps"] == 81
    assert fee["floor_is_3x_round_trip_fees"] is True
    assert fee["no_maker_rebate_assumption"] is True
    assert fee["no_zero_fee_assumption"] is True
    for value in (0, 5, 13, 26, 28, 50):
        tampered = _record()
        tampered["fee_geometry"]["fee_model_round_trip_bps"] = value
        assert c10s.validate_candidate_10_spec_review(
            tampered)["valid"] is False, value
    for value in (0, 27, 54, 80, 82, 162):
        tampered = _record()
        tampered["fee_geometry"][
            "minimum_gross_target_distance_floor_bps"] = value
        assert c10s.validate_candidate_10_spec_review(
            tampered)["valid"] is False, value
    for key in ("no_maker_rebate_assumption", "no_zero_fee_assumption"):
        tampered = _record()
        tampered["fee_geometry"][key] = False
        assert c10s.validate_candidate_10_spec_review(
            tampered)["valid"] is False, key


# ---- anti-cluster + sample-size + edge + single-trigger all locked -----

def test_anti_cluster_5_bars_proposal_locked_not_edit_token():
    anti = _R["anti_cluster_policy"]
    assert anti[
        "min_bars_between_same_symbol_accepted_events_1d"] == 5
    assert anti["one_fire_per_iso_week_by_construction"] is True
    assert anti["calendar_is_the_primary_anti_cluster_constraint"] is (
        True)
    assert anti["is_not_the_single_allowed_c10_edit_token"] is True
    assert anti["applies_before_replay_time_non_overlap"] is True
    assert anti["replay_time_non_overlap_unchanged"] is True
    assert anti["tie_breaker"] == (
        "keep_the_earlier_event_drop_the_later_one")
    for value in (0, 3, 4, 6, 10):
        tampered = _record()
        tampered["anti_cluster_policy"][
            "min_bars_between_same_symbol_accepted_events_1d"] = value
        assert c10s.validate_candidate_10_spec_review(
            tampered)["valid"] is False, value
    for key in ("is_not_the_single_allowed_c10_edit_token",
                "one_fire_per_iso_week_by_construction",
                "calendar_is_the_primary_anti_cluster_constraint",
                "applies_before_replay_time_non_overlap",
                "replay_time_non_overlap_unchanged"):
        tampered = _record()
        tampered["anti_cluster_policy"][key] = False
        assert c10s.validate_candidate_10_spec_review(
            tampered)["valid"] is False, key


def test_sample_size_100_proposal_locked_not_edit_token():
    sa = _R["sample_size_adequacy_policy"]
    assert sa[
        "minimum_accepted_setups_required_at_labels_review_gate"
    ] == 100
    assert sa[
        "below_threshold_triggers_structural_rejection_without_edit"
        "_token"] is True
    assert sa["is_not_the_single_allowed_c10_edit_token"] is True
    for value in (0, 20, 50, 99, 101, 200):
        tampered = _record()
        tampered["sample_size_adequacy_policy"][
            "minimum_accepted_setups_required_at_labels_review_gate"
        ] = value
        assert c10s.validate_candidate_10_spec_review(
            tampered)["valid"] is False, value
    for key in ("below_threshold_triggers_structural_rejection_without"
                "_edit_token",
                "is_not_the_single_allowed_c10_edit_token"):
        tampered = _record()
        tampered["sample_size_adequacy_policy"][key] = False
        assert c10s.validate_candidate_10_spec_review(
            tampered)["valid"] is False, key


def test_explicit_edge_argument_carried_forward_and_locked():
    carried = _R[
        "explicit_edge_argument_beyond_pattern_geometry_carried"
        "_forward"]
    assert carried == c10p.EXPLICIT_EDGE_ARGUMENT_BEYOND_PATTERN_GEOMETRY
    assert "CALENDAR RISK PREMIUM, NOT A VISUAL PATTERN" in carried
    assert "WHY THIS IS ORTHOGONAL TO C1-C9" in carried
    eep = _R["explicit_edge_argument_policy"]
    assert eep["carried_forward_from_c10_family_proposal"] is True
    assert eep["v5_required_field"] is True
    assert eep["argument_is_a_calendar_risk_premium_not_visual"] is True
    assert eep[
        "argument_is_orthogonal_to_all_price_and_volume_conditions"
    ] is True
    assert eep[
        "argument_is_falsifiable_by_per_bucket_per_variant_net_r_sums"
    ] is True
    assert eep["is_not_the_single_allowed_c10_edit_token"] is True
    tampered = _record()
    tampered["explicit_edge_argument_beyond_pattern_geometry_carried"
             "_forward"] = "tampered argument"
    assert c10s.validate_candidate_10_spec_review(
        tampered)["valid"] is False
    for key in ("v5_required_field",
                "is_not_the_single_allowed_c10_edit_token"):
        tampered = _record()
        tampered["explicit_edge_argument_policy"][key] = False
        assert c10s.validate_candidate_10_spec_review(
            tampered)["valid"] is False, key


def test_single_trigger_design_proposal_locked_not_edit_token():
    stp = _R["single_trigger_policy"]
    assert stp["design_is_single_deterministic_trigger"] is True
    assert stp["no_intersection_of_trigger_conditions"] is True
    assert stp["intersection_sparsity_failure_cannot_occur"] is True
    assert stp["is_not_the_single_allowed_c10_edit_token"] is True
    for key in ("design_is_single_deterministic_trigger",
                "no_intersection_of_trigger_conditions",
                "is_not_the_single_allowed_c10_edit_token"):
        tampered = _record()
        tampered["single_trigger_policy"][key] = False
        assert c10s.validate_candidate_10_spec_review(
            tampered)["valid"] is False, key


# ---- edit-token policy locks ------------------------------------------

def test_edit_policy_one_token_targets_only_structural_numerics():
    edit = _R["edit_policy"]
    assert edit["maximum_pre_committed_edits"] == 1
    assert edit["edit_requires_separate_human_approval"] is True
    assert edit[
        "anti_cluster_gap_is_proposal_level_locked_not_the_edit"
        "_token"] is True
    assert edit[
        "sample_size_threshold_is_proposal_level_locked_not_the"
        "_edit_token"] is True
    assert edit[
        "explicit_edge_argument_field_is_proposal_level_locked"
        "_not_the_edit_token"] is True
    assert edit[
        "single_trigger_design_is_proposal_level_locked_not_the"
        "_edit_token"] is True
    assert edit["edit_must_target_a_different_structural_parameter"
                ] is True
    eligible = tuple(edit["edit_token_eligible_parameters"])
    assert eligible == ("FAVORABLE_WEEKDAY_BUCKET_SELECTION_WINDOW",
                        "HOLDING_HORIZON_BARS",
                        "FAVORABLE_WEEKDAY_BUCKET_CARDINALITY",
                        "STRUCTURE_STOP_ATR_MULTIPLIER")
    for value in (0, 2, 3):
        tampered = _record()
        tampered["edit_policy"]["maximum_pre_committed_edits"] = value
        assert c10s.validate_candidate_10_spec_review(
            tampered)["valid"] is False, value
    for key in ("anti_cluster_gap_is_proposal_level_locked_not_the"
                "_edit_token",
                "sample_size_threshold_is_proposal_level_locked_not"
                "_the_edit_token",
                "explicit_edge_argument_field_is_proposal_level"
                "_locked_not_the_edit_token",
                "single_trigger_design_is_proposal_level_locked_not"
                "_the_edit_token"):
        tampered = _record()
        tampered["edit_policy"][key] = False
        assert c10s.validate_candidate_10_spec_review(
            tampered)["valid"] is False, key
    tampered = _record()
    tampered["edit_policy"]["edit_token_eligible_parameters"] = [
        "FEE_BPS"]
    assert c10s.validate_candidate_10_spec_review(
        tampered)["valid"] is False


# ---- data boundary + sample tag --------------------------------------

def test_data_boundary_and_sample_window_frozen():
    boundary = _R["data_boundary"]
    assert boundary["sample_tag"] == "2019-01-01_2025-12-31"
    assert boundary["no_fetch_ever"] is True
    assert boundary["no_real_time_data"] is True
    assert boundary["staged_data_never_modified"] is True
    assert boundary[
        "consumes_calendar_weekday_index_as_a_new_exogenous_input_for"
        "_the_first_time_in_lane"] is True
    for value in ("2019-01-01_2024-12-31", "2020-01-01_2025-12-31"):
        tampered = _record()
        tampered["data_boundary"]["sample_tag"] = value
        assert c10s.validate_candidate_10_spec_review(
            tampered)["valid"] is False, value
    for key in ("no_fetch_ever", "staged_data_never_modified"):
        tampered = _record()
        tampered["data_boundary"][key] = False
        assert c10s.validate_candidate_10_spec_review(
            tampered)["valid"] is False, key


# ---- material differences from C1-C9 ----------------------------------

def test_material_differences_from_c1_c9_frozen():
    diffs = _R["material_differences_from_rejected_families"]
    joined = " || ".join(diffs)
    for marker, phrase in (
            ("NOT_c1", "not_session_anchored"),
            ("NOT_c2", "breakout_pullback"),
            ("NOT_c3", "trend_continuation"),
            ("NOT_c4", "btc_sol_or_sol_btc_swing"),
            ("NOT_c5", "relative_strength_pullback"),
            ("NOT_c6", "multi_symbol_rank"),
            ("NOT_c7", "atr_compression"),
            ("NOT_c8", "sweep_below_prior_low"),
            ("NOT_c9", "no_volume_condition")):
        assert marker in joined, marker
        assert phrase in joined, phrase
    tampered = _record()
    tampered["material_differences_from_rejected_families"] = list(
        diffs[:-1])
    assert c10s.validate_candidate_10_spec_review(
        tampered)["valid"] is False


def test_inherited_lessons_c6_c7_c8_c9_frozen():
    lessons = _R["inherited_lessons"]
    joined = " || ".join(lessons)
    assert "c6_lesson_anti_cluster" in joined
    assert "c7_lesson_sample_size_adequacy" in joined
    assert "c8_lesson_explicit_edge_argument_beyond_pattern_geometry" \
        in joined
    assert "c9_lesson_single_deterministic_trigger_design" in joined
    assert "not_consuming_edit_token" in joined


# ---- spec-review-only safety + claim locks ----------------------------

def test_spec_review_only_no_downstream_unlocks_or_capability():
    assert _R["is_spec_review_only"] is True
    assert _R["current_loop_stage"] == "candidate_spec"
    assert _R["next_loop_stage"] == "detector_and_label_review"
    for key in ("runs_detector", "runs_real_candle_detection",
                "runs_dry_run", "runs_relabel", "runs_replay",
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
                "uses_external_data_source",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate", "unlocks_detector_now",
                "unlocks_labels_now", "unlocks_replay_now",
                "unlocks_relabel_now", "claims_profitability",
                "executes", "writes_files"):
        assert _R[key] is False, key
        tampered = _record()
        tampered[key] = True
        assert c10s.validate_candidate_10_spec_review(
            tampered)["valid"] is False, key
    assert _R["paper_trading_gate_locked"] is True
    assert _R["micro_live_gate_locked"] is True
    assert _R["live_gate_locked"] is True
    assert _R["human_review_required"] is True
    assert _R["is_a_rescue_attempt"] is False


def test_claim_locks_and_label():
    locks = _R["claim_locks"]
    for required in (
            "no_profitability_claim", "no_paper_approval",
            "no_live_approval", "no_execution_approval",
            "no_winner_wording",
            "promotion_can_only_produce_a_human_review_record",
            "anti_cluster_gap_is_proposal_level_locked_not_edit_token",
            "sample_size_threshold_is_proposal_level_locked_not_edit"
            "_token",
            "explicit_edge_argument_field_is_proposal_level_locked"
            "_not_edit_token",
            "single_trigger_design_is_proposal_level_locked_not_edit"
            "_token"):
        assert required in locks, required
    assert c10s.NEXT_REQUIRED_ACTION == (
        "HUMAN_APPROVED_CANDIDATE_10_DETECTOR_SPEC_AND_DRY_RUN_PATH")
    for banned in ("PROMOTE", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER",
                   "LIVE", "BROKER", "EXCHANGE", "AUTOMATION",
                   "ORDER", "TRACK"):
        assert banned not in c10s.NEXT_REQUIRED_ACTION.upper(), banned
    assert c10s.get_candidate_10_spec_review_label() == c10s.C10S_LABEL
    assert c10s.C10S_MODE == "RESEARCH_ONLY"
    for phrase in ("READ-ONLY", "RESEARCH ONLY",
                   "RULES DEFINITION",
                   "EXPLICIT EDGE ARGUMENT BEYOND PATTERN GEOMETRY",
                   "SINGLE-TRIGGER", "NOT A RESCUE", "NOT A CLAIM"):
        assert phrase in c10s.C10S_LABEL, phrase
    for banned_phrase in ("WINNER", "PROFITABLE",
                          "EDGE CONFIRMED",
                          "APPROVED FOR PAPER",
                          "APPROVED FOR LIVE"):
        assert banned_phrase not in c10s.C10S_LABEL.upper(), (
            banned_phrase)


# ---- module purity --------------------------------------------------------

def test_module_purity_no_banned_imports_no_open_no_main():
    src = open(c10s.__file__, encoding="utf-8").read()
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
