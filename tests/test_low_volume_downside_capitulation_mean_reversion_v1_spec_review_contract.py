"""Tests for the Candidate #9 strategy spec review contract
(LOW_VOLUME_DOWNSIDE_CAPITULATION_MEAN_REVERSION_V1).

Verifies: chain-gate on the pushed C9 family proposal + V4 + V3 + V2
+ Recommendation V1 + Autopilot V1 + 8-record ledger; every frozen
numeric (universe/timeframe/direction, rolling-window 96, ATR 14,
downside z-score -2.0, below-median volume threshold 50, joint
trigger, entry on next-bar-close, structure-stop buffer 0.20 ATR,
2R/3R/4R targets, 96-bar timeout, 27/81 bps fee/floor, anti-cluster
8-bar gap proposal-locked NOT edit token, sample-size adequacy 20
proposal-locked NOT edit token, explicit-edge-argument field
proposal-locked NOT edit token, sample tag); explicit edge argument
carried forward verbatim from C9 family proposal; edit-token
eligible parameters; material differences from C1-C8; AST/purity
green; downstream execution gates locked."""

from __future__ import annotations

import ast

import sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_family_proposal_contract as c9p
import sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_spec_review_contract as c9s
import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as ap
import sparta_commander.strategy_factory_candidate_recommendation_v1_contract as rec
import sparta_commander.strategy_factory_overnight_research_autopilot_v2_contract as oap2
import sparta_commander.strategy_factory_rejected_family_blacklist_v3_contract as bl3
import sparta_commander.strategy_factory_rejected_family_blacklist_v4_contract as bl4


def _record():
    return c9s.build_candidate_9_spec_review()


# ---- chain gate + ready verdict -------------------------------------------

def test_spec_ready_and_gated_on_full_chain():
    assert c9p.build_candidate_9_family_proposal()["verdict"] == (
        c9p.VERDICT_C9P_READY)
    assert bl4.build_rejected_family_blacklist_v4()["verdict"] == (
        bl4.VERDICT_BL4_READY)
    assert bl3.build_rejected_family_blacklist_v3()["verdict"] == (
        bl3.VERDICT_BL3_READY)
    assert oap2.build_overnight_research_autopilot_v2_contract()[
        "verdict"] == oap2.VERDICT_OAP2_READY
    assert rec.build_candidate_recommendation()["verdict"] == (
        rec.VERDICT_CR_READY)
    assert ap.build_autopilot_loop_contract()["verdict"] == (
        ap.VERDICT_AP_READY)
    record = _record()
    assert record["verdict"] == c9s.VERDICT_C9S_READY
    assert record["blockers"] == []
    assert c9s.validate_candidate_9_spec_review(
        record)["valid"] is True
    assert _record() == record  # determinism
    assert record["ledger_status_eight_records"] == [
        "REJECTED_KEPT_ON_RECORD"] * 8
    assert record["ledger_all_rejected_kept_on_record"] is True


def test_chain_blocks_when_ledger_breaks():
    import sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_spec_review_contract as mod
    originals = {key: getattr(mod, key) for key in
                 ("C1_STATUS", "C2_STATUS", "C3_STATUS", "C4_STATUS",
                  "C5_STATUS", "C6_STATUS", "C7_STATUS",
                  "C8_STATUS")}
    try:
        for key in originals:
            setattr(mod, key, "APPROVED_FOR_TRADING")
            record = mod.build_candidate_9_spec_review()
            assert record["verdict"] == c9s.VERDICT_C9S_BLOCKED, key
            assert "eight_record_ledger_broken" in record[
                "blockers"], key
            setattr(mod, key, originals[key])
    finally:
        for key, value in originals.items():
            setattr(mod, key, value)
    assert mod.build_candidate_9_spec_review()["verdict"] == (
        c9s.VERDICT_C9S_READY)


# ---- frozen universe + timeframe + direction + rolling window ----------

def test_universe_timeframe_direction_and_rolling_window():
    record = _record()
    assert record["universe"] == ["BTCUSD"]
    assert record["timeframe"] == "15m"
    assert record["direction"] == "long_only"
    assert record["rolling_window_bars"] == 96
    assert record[
        "rolling_window_uses_prior_bars_only_no_same_bar_lookahead"
    ] is True
    for field, value in (("universe", ["BTCUSD", "ETHUSD"]),
                         ("universe", []),
                         ("timeframe", "1h"),
                         ("timeframe", "4h"),
                         ("direction", "short_only"),
                         ("rolling_window_bars", 48),
                         ("rolling_window_bars", 192)):
        tampered = _record()
        tampered[field] = value
        assert c9s.validate_candidate_9_spec_review(
            tampered)["valid"] is False, (field, value)


def test_atr_length_14_frozen():
    record = _record()
    assert record["atr_length"] == 14
    assert record[
        "atr_uses_completed_15m_bars_only_standard_true_range"
    ] is True
    for value in (7, 21, 30):
        tampered = _record()
        tampered["atr_length"] = value
        assert c9s.validate_candidate_9_spec_review(
            tampered)["valid"] is False, value


# ---- frozen joint trigger (z-score + volume) ---------------------------

def test_downside_z_score_threshold_minus_2_0_frozen():
    record = _record()
    assert record["downside_z_score_threshold"] == -2.0
    rule = record["downside_z_score_rule"]
    assert rule["downside_z_score_threshold"] == -2.0
    assert rule["rolling_window_bars"] == 96
    assert rule["strict_inequality_below_threshold"] is True
    assert rule["no_same_bar_lookahead_in_stats"] is True
    assert rule["log_return_definition"] == (
        "log(close[i] / close[i-1]) for each completed 15m bar i")
    assert rule["stats_use_population_or_sample_std"] == (
        "sample_std_n_minus_1")
    for value in (-1.0, -1.5, -2.5, -3.0, 0.0, 2.0):
        tampered = _record()
        tampered["downside_z_score_threshold"] = value
        assert c9s.validate_candidate_9_spec_review(
            tampered)["valid"] is False, value


def test_volume_below_median_rule_50_percentile_strict_below():
    record = _record()
    vr = record["volume_below_median_rule"]
    assert vr["volume_percentile_threshold"] == 50.0
    assert vr["strict_inequality_below_median"] is True
    assert vr["rolling_window_bars"] == 96
    assert vr["no_same_bar_lookahead_in_median"] is True
    for value in (25.0, 40.0, 49.0, 51.0, 60.0, 75.0):
        tampered = _record()
        tampered["volume_below_median_rule"]["volume_percentile"
                                             "_threshold"] = value
        assert c9s.validate_candidate_9_spec_review(
            tampered)["valid"] is False, value
    tampered = _record()
    tampered["volume_below_median_rule"][
        "strict_inequality_below_median"] = False
    assert c9s.validate_candidate_9_spec_review(
        tampered)["valid"] is False


def test_joint_trigger_both_required_on_same_bar():
    jt = _record()["joint_trigger_rule"]
    assert jt["both_conditions_required_on_same_bar"] is True
    assert jt[
        "is_a_joint_microstructure_trigger_not_a_chart_pattern"
    ] is True
    tampered = _record()
    tampered["joint_trigger_rule"][
        "both_conditions_required_on_same_bar"] = False
    assert c9s.validate_candidate_9_spec_review(
        tampered)["valid"] is False


# ---- frozen entry rule -------------------------------------------------

def test_entry_rule_next_bar_close_no_intrabar():
    er = _record()["entry_rule"]
    assert er["entry_price"] == (
        "close_of_the_next_completed_15m_bar_after_trigger_bar")
    assert er["no_intrabar_entry"] is True
    assert er["no_same_bar_entry"] is True
    assert er["invalidate_if_entry_bar_close_le_trigger_bar_low"
              ] is True
    assert er["evaluation_starts"] == (
        "next_15m_bar_after_entry_bar_close")
    for key in ("no_intrabar_entry", "no_same_bar_entry",
                "invalidate_if_entry_bar_close_le_trigger_bar_low"):
        tampered = _record()
        tampered["entry_rule"][key] = False
        assert c9s.validate_candidate_9_spec_review(
            tampered)["valid"] is False, key


# ---- frozen structure-stop rule ---------------------------------------

def test_structure_stop_buffer_0_20_atr_frozen():
    stop = _record()["stop_rule"]
    assert stop["structure_stop_buffer_atr_multiplier"] == 0.20
    assert stop["atr_length"] == 14
    assert stop["stop_price_formula"] == (
        "trigger_bar_low - STRUCTURE_STOP_BUFFER_ATR_MULTIPLIER * "
        "ATR14_at_trigger_bar")
    assert stop["stop_must_be_below_entry"] is True
    assert stop["stop_must_be_below_trigger_bar_low"] is True
    assert stop["never_tightened_after_entry"] is True
    assert stop["invalid_if_stop_distance_not_positive"] is True
    for value in (0.0, 0.10, 0.30, 0.50, 1.0):
        tampered = _record()
        tampered["stop_rule"]["structure_stop_buffer_atr_multiplier"
                              ] = value
        assert c9s.validate_candidate_9_spec_review(
            tampered)["valid"] is False, value


# ---- frozen targets + timeout + fee geometry --------------------------

def test_target_variants_2r_3r_4r_and_formula_locked():
    targets = _record()["target_rules"]
    assert targets["variants"] == ["2r", "3r", "4r"]
    assert targets["no_new_variants_after_label_freeze"] is True
    assert targets["target_price_formula"] == (
        "entry_price + r_multiple * stop_distance")
    for value in (["1r"], ["5r"], ["2r", "3r"], ["2r", "3r", "4r",
                                                  "5r"]):
        tampered = _record()
        tampered["target_rules"]["variants"] = value
        assert c9s.validate_candidate_9_spec_review(
            tampered)["valid"] is False, value


def test_timeout_96_bars_locked():
    timeout = _record()["timeout_rule"]
    assert timeout["timeout_bars"] == 96
    assert timeout["horizon_hours_at_15m"] == 24.0
    assert timeout["applied_at_replay_time"] is True
    assert timeout["is_not_an_entry_gate_rule"] is True
    for value in (48, 60, 100, 192):
        tampered = _record()
        tampered["timeout_rule"]["timeout_bars"] = value
        assert c9s.validate_candidate_9_spec_review(
            tampered)["valid"] is False, value


def test_fee_27_and_floor_81_locked():
    fee = _record()["fee_geometry"]
    assert fee["fee_model_round_trip_bps"] == 27
    assert fee["minimum_gross_target_distance_floor_bps"] == 81
    assert fee["floor_is_3x_round_trip_fees"] is True
    assert fee["no_maker_rebate_assumption"] is True
    assert fee["no_zero_fee_assumption"] is True
    for value in (0, 5, 13, 26, 28, 50):
        tampered = _record()
        tampered["fee_geometry"]["fee_model_round_trip_bps"] = value
        assert c9s.validate_candidate_9_spec_review(
            tampered)["valid"] is False, value
    for value in (0, 27, 54, 80, 82, 162):
        tampered = _record()
        tampered["fee_geometry"][
            "minimum_gross_target_distance_floor_bps"] = value
        assert c9s.validate_candidate_9_spec_review(
            tampered)["valid"] is False, value


# ---- anti-cluster + sample-size + explicit-edge-argument all locked ---

def test_anti_cluster_8_bars_proposal_locked_not_edit_token():
    anti = _record()["anti_cluster_policy"]
    assert anti[
        "min_bars_between_same_symbol_accepted_events_15m"] == 8
    assert anti["is_not_the_single_allowed_c9_edit_token"] is True
    assert anti["applies_before_replay_time_non_overlap"] is True
    assert anti["replay_time_non_overlap_unchanged"] is True
    assert anti["tie_breaker"] == (
        "keep_the_earlier_event_drop_the_later_one")
    for value in (0, 4, 6, 10, 16):
        tampered = _record()
        tampered["anti_cluster_policy"][
            "min_bars_between_same_symbol_accepted_events_15m"
        ] = value
        assert c9s.validate_candidate_9_spec_review(
            tampered)["valid"] is False, value
    tampered = _record()
    tampered["anti_cluster_policy"][
        "is_not_the_single_allowed_c9_edit_token"] = False
    assert c9s.validate_candidate_9_spec_review(
        tampered)["valid"] is False


def test_sample_size_20_proposal_locked_not_edit_token():
    sa = _record()["sample_size_adequacy_policy"]
    assert sa[
        "minimum_accepted_setups_required_at_labels_review_gate"
    ] == 20
    assert sa[
        "below_threshold_triggers_structural_rejection_without_edit"
        "_token"] is True
    assert sa["is_not_the_single_allowed_c9_edit_token"] is True
    for value in (0, 5, 10, 19, 21, 50):
        tampered = _record()
        tampered["sample_size_adequacy_policy"][
            "minimum_accepted_setups_required_at_labels_review_gate"
        ] = value
        assert c9s.validate_candidate_9_spec_review(
            tampered)["valid"] is False, value


def test_explicit_edge_argument_carried_forward_and_locked():
    record = _record()
    # The full 6-paragraph argument carries through unchanged
    carried = record[
        "explicit_edge_argument_beyond_pattern_geometry_carried"
        "_forward"]
    assert carried == c9p.EXPLICIT_EDGE_ARGUMENT_BEYOND_PATTERN_GEOMETRY
    assert "MICROSTRUCTURAL, NOT VISUAL" in carried
    assert "WHY THIS IS NOT C8" in carried
    # Policy
    eep = record["explicit_edge_argument_policy"]
    assert eep["carried_forward_from_c9_family_proposal"] is True
    assert eep["v4_required_field"] is True
    assert eep["argument_is_microstructural_not_visual"] is True
    assert eep[
        "argument_is_falsifiable_by_per_variant_net_r_sums"] is True
    assert eep["is_not_the_single_allowed_c9_edit_token"] is True
    tampered = _record()
    tampered["explicit_edge_argument_beyond_pattern_geometry_carried"
             "_forward"] = "tampered argument"
    assert c9s.validate_candidate_9_spec_review(
        tampered)["valid"] is False
    tampered = _record()
    tampered["explicit_edge_argument_policy"][
        "v4_required_field"] = False
    assert c9s.validate_candidate_9_spec_review(
        tampered)["valid"] is False


# ---- edit-token policy locks ------------------------------------------

def test_edit_policy_one_token_targets_only_structural_numerics():
    edit = _record()["edit_policy"]
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
    assert edit["edit_must_target_a_different_structural_parameter"
                ] is True
    eligible = tuple(edit["edit_token_eligible_parameters"])
    assert eligible == ("DOWNSIDE_Z_SCORE_THRESHOLD",
                        "VOLUME_PERCENTILE_THRESHOLD_50",
                        "ROLLING_WINDOW_BARS",
                        "STRUCTURE_STOP_BUFFER_ATR_MULTIPLIER")
    # tampering on any lock breaks validation
    for key in ("anti_cluster_gap_is_proposal_level_locked_not_the"
                "_edit_token",
                "sample_size_threshold_is_proposal_level_locked_not"
                "_the_edit_token",
                "explicit_edge_argument_field_is_proposal_level"
                "_locked_not_the_edit_token"):
        tampered = _record()
        tampered["edit_policy"][key] = False
        assert c9s.validate_candidate_9_spec_review(
            tampered)["valid"] is False, key


# ---- data boundary + sample tag --------------------------------------

def test_data_boundary_and_sample_window_frozen():
    boundary = _record()["data_boundary"]
    assert boundary["sample_tag"] == "2026-05-02_2026-06-10"
    assert boundary["no_fetch_ever"] is True
    assert boundary["no_real_time_data"] is True
    assert boundary["staged_data_never_modified"] is True
    assert boundary[
        "consumes_volume_column_structurally_for_first_time_in_lane"
    ] is True


# ---- material differences from C1-C8 ----------------------------------

def test_material_differences_from_c1_c8_frozen():
    diffs = _record()["material_differences_from_rejected_families"]
    joined = " || ".join(diffs)
    for marker, phrase in (
            ("NOT_c1", "no_ny_fvg_choch_dependency"),
            ("NOT_c2", "breakout_pullback"),
            ("NOT_c3", "trend_continuation"),
            ("NOT_c4", "btc_sol_or_sol_btc_swing"),
            ("NOT_c5", "no_relative_strength_comparison"),
            ("NOT_c6", "multi_symbol_rank"),
            ("NOT_c7", "atr_compression"),
            ("NOT_c8", "sweep_below_prior_low")):
        assert marker in joined, marker
        assert phrase in joined, phrase


def test_inherited_lessons_c6_c7_c8_frozen():
    lessons = _record()["inherited_lessons"]
    joined = " || ".join(lessons)
    assert "c6_lesson_anti_cluster" in joined
    assert "c7_lesson_sample_size_adequacy" in joined
    assert "c8_lesson_explicit_edge_argument_beyond_pattern_geometry" \
        in joined
    assert "not_consuming_edit_token" in joined


# ---- spec-review-only safety + claim locks ----------------------------

def test_spec_review_only_no_downstream_unlocks_or_capability():
    record = _record()
    assert record["is_spec_review_only"] is True
    assert record["current_loop_stage"] == "candidate_spec"
    assert record["next_loop_stage"] == "detector_and_label_review"
    for key in ("runs_detector", "runs_real_candle_detection",
                "runs_relabel", "runs_replay",
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
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate", "unlocks_detector_now",
                "unlocks_labels_now", "unlocks_replay_now",
                "unlocks_relabel_now", "claims_profitability",
                "executes", "writes_files"):
        assert record[key] is False, key
        tampered = _record()
        tampered[key] = True
        assert c9s.validate_candidate_9_spec_review(
            tampered)["valid"] is False, key
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True


def test_claim_locks_and_label():
    record = _record()
    locks = record["claim_locks"]
    for required in (
            "no_profitability_claim", "no_paper_approval",
            "no_live_approval", "no_execution_approval",
            "no_winner_wording",
            "promotion_can_only_produce_a_human_review_record",
            "anti_cluster_gap_is_proposal_level_locked_not_edit"
            "_token",
            "sample_size_threshold_is_proposal_level_locked_not_edit"
            "_token",
            "explicit_edge_argument_field_is_proposal_level_locked"
            "_not_edit_token"):
        assert required in locks, required
    assert c9s.NEXT_REQUIRED_ACTION == (
        "HUMAN_APPROVED_CANDIDATE_9_DETECTOR_SPEC_AND_DRY_RUN_PATH")
    for banned in ("PROMOTE", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER",
                   "LIVE", "BROKER", "EXCHANGE", "AUTOMATION",
                   "ORDER", "TRACK"):
        assert banned not in c9s.NEXT_REQUIRED_ACTION.upper(), banned
    assert c9s.get_candidate_9_spec_review_label() == c9s.C9S_LABEL
    assert c9s.C9S_MODE == "RESEARCH_ONLY"
    for phrase in ("READ-ONLY", "RESEARCH ONLY",
                   "RULES DEFINITION",
                   "EXPLICIT EDGE ARGUMENT BEYOND PATTERN GEOMETRY",
                   "NOT A RESCUE", "NOT A CLAIM"):
        assert phrase in c9s.C9S_LABEL, phrase
    for banned_phrase in ("WINNER", "PROFITABLE",
                          "EDGE CONFIRMED",
                          "APPROVED FOR PAPER",
                          "APPROVED FOR LIVE"):
        assert banned_phrase not in c9s.C9S_LABEL.upper(), (
            banned_phrase)


# ---- module purity --------------------------------------------------------

def test_module_purity_no_banned_imports_no_open_no_main():
    src = open(c9s.__file__, encoding="utf-8").read()
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
