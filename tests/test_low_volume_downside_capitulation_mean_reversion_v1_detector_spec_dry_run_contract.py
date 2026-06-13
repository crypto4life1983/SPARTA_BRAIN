"""Tests for the Candidate #9 detector-spec + synthetic dry-run
contract (LOW_VOLUME_DOWNSIDE_CAPITULATION_MEAN_REVERSION_V1).

Verifies: chain-gate on the 8-record ledger + C9 family proposal +
C9 spec review + V4 + V3 + V2 + Recommendation V1 + Autopilot V1;
every frozen numeric (universe/timeframe/direction, rolling-window
96, ATR 14, downside z-score |2.0|, below-median volume 50,
structure-stop buffer 0.20 ATR, 2R/3R/4R targets, 96-bar timeout,
27/81 bps fee/floor, anti-cluster 8-bar gap proposal-locked NOT
edit token, sample-size adequacy 20 proposal-locked NOT edit token,
explicit-edge-argument field proposal-locked NOT edit token); 11
synthetic fixtures all certify (happy path, insufficient history,
equality at z, equality at volume median, z-only, volume-only,
entry-bar invalidation, floor fail, anti-cluster boundary,
sample-size adequacy, context enforcement); pure detector function
behavior; downstream execution gates locked; AST/purity green."""

from __future__ import annotations

import ast

import sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_detector_spec_dry_run_contract as c9d
import sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_family_proposal_contract as c9p
import sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_spec_review_contract as c9s
import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as ap
import sparta_commander.strategy_factory_candidate_recommendation_v1_contract as rec
import sparta_commander.strategy_factory_overnight_research_autopilot_v2_contract as oap2
import sparta_commander.strategy_factory_rejected_family_blacklist_v3_contract as bl3
import sparta_commander.strategy_factory_rejected_family_blacklist_v4_contract as bl4


def _record():
    return c9d.build_candidate_9_detector_spec_dry_run()


# ---- chain gate + verdicts --------------------------------------------------

def test_spec_ready_and_dry_run_passed_and_combined_ready():
    record = _record()
    assert record["verdict"] == c9d.VERDICT_C9D_READY
    assert record["blockers"] == []
    assert record["dry_run"]["verdict"] == (
        c9d.VERDICT_C9D_DRY_RUN_PASSED)
    assert record["dry_run"]["failures"] == []
    assert record["combined_verdict"] == (
        c9d.VERDICT_C9D_SPEC_DRY_RUN_READY)
    assert c9d.validate_candidate_9_detector_spec_dry_run(
        record)["valid"] is True


def test_full_chain_gates_certify():
    assert c9p.build_candidate_9_family_proposal()["verdict"] == (
        c9p.VERDICT_C9P_READY)
    assert c9s.build_candidate_9_spec_review()["verdict"] == (
        c9s.VERDICT_C9S_READY)
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


def test_eight_record_ledger_intact():
    record = _record()
    assert record["ledger_status_eight_records"] == [
        "REJECTED_KEPT_ON_RECORD"] * 8
    assert record["ledger_all_rejected_kept_on_record"] is True


def test_chain_blocks_when_ledger_breaks():
    import sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_detector_spec_dry_run_contract as mod
    originals = {key: getattr(mod, key) for key in
                 ("C1_STATUS", "C2_STATUS", "C3_STATUS", "C4_STATUS",
                  "C5_STATUS", "C6_STATUS", "C7_STATUS",
                  "C8_STATUS")}
    try:
        for key in originals:
            setattr(mod, key, "APPROVED_FOR_TRADING")
            spec = mod.build_candidate_9_detector_spec_contract()
            assert spec["verdict"] == c9d.VERDICT_C9D_BLOCKED, key
            assert "eight_record_ledger_broken" in spec[
                "blockers"], key
            setattr(mod, key, originals[key])
    finally:
        for key, value in originals.items():
            setattr(mod, key, value)
    assert mod.build_candidate_9_detector_spec_contract()[
        "verdict"] == c9d.VERDICT_C9D_READY


# ---- frozen numerics ------------------------------------------------------

def test_universe_timeframe_direction_frozen():
    record = _record()
    assert record["universe"] == ["BTCUSD"]
    assert record["timeframe"] == "15m"
    assert record["direction"] == "long_only"
    for field, value in (("universe", ["BTCUSD", "ETHUSD"]),
                         ("universe", []),
                         ("timeframe", "1h"),
                         ("direction", "short_only")):
        tampered = _record()
        tampered[field] = value
        assert c9d.validate_candidate_9_detector_spec_dry_run(
            tampered)["valid"] is False, (field, value)


def test_rolling_window_atr_z_volume_frozen():
    record = _record()
    assert record["rolling_window_bars"] == 96
    assert record["atr_length"] == 14
    assert record["downside_z_score_threshold_abs"] == 2.0
    assert record["downside_z_score_threshold_signed"] == -2.0
    assert record["volume_percentile_threshold"] == 50.0
    assert record["volume_strict_below_median"] is True
    assert record[
        "joint_trigger_both_conditions_required_on_same_bar"] is True
    for field, bad in (
            ("rolling_window_bars", 48),
            ("rolling_window_bars", 192),
            ("atr_length", 7),
            ("downside_z_score_threshold_abs", 1.5),
            ("downside_z_score_threshold_signed", -1.5),
            ("volume_percentile_threshold", 25.0),
            ("volume_strict_below_median", False),
            ("joint_trigger_both_conditions_required_on_same_bar",
             False)):
        tampered = _record()
        tampered[field] = bad
        assert c9d.validate_candidate_9_detector_spec_dry_run(
            tampered)["valid"] is False, (field, bad)


def test_entry_rule_and_invalidation_frozen():
    record = _record()
    assert record[
        "entry_rule_close_of_next_completed_bar_after_trigger_bar"
    ] is True
    assert record[
        "entry_bar_close_must_be_strictly_above_trigger_bar_low"
    ] is True
    for key in ("entry_rule_close_of_next_completed_bar_after"
                "_trigger_bar",
                "entry_bar_close_must_be_strictly_above_trigger_bar"
                "_low"):
        tampered = _record()
        tampered[key] = False
        assert c9d.validate_candidate_9_detector_spec_dry_run(
            tampered)["valid"] is False, key


def test_stop_rule_frozen():
    record = _record()
    assert record["structure_stop_buffer_atr_multiplier"] == 0.20
    assert record["stop_price_formula"] == (
        "trigger_bar_low - STRUCTURE_STOP_BUFFER_ATR_MULTIPLIER * "
        "ATR14_at_trigger_bar")
    assert record["stop_never_tightened_after_entry"] is True
    for value in (0.0, 0.10, 0.30, 0.50, 1.0):
        tampered = _record()
        tampered["structure_stop_buffer_atr_multiplier"] = value
        assert c9d.validate_candidate_9_detector_spec_dry_run(
            tampered)["valid"] is False, value
    tampered = _record()
    tampered["stop_price_formula"] = "fixed_1_percent"
    assert c9d.validate_candidate_9_detector_spec_dry_run(
        tampered)["valid"] is False


def test_target_variants_and_floor_frozen():
    record = _record()
    assert record["target_variants"] == ["2r", "3r", "4r"]
    assert record["target_price_formula"] == (
        "entry_price + r_multiple * stop_distance")
    assert record["timeout_bars"] == 96
    assert record["fee_round_trip_bps"] == 27.0
    assert record["target_distance_floor_bps"] == 81.0
    assert record["no_maker_rebate_assumption"] is True
    assert record["no_zero_fee_assumption"] is True
    for value in (0.0, 5.0, 26.0, 28.0, 100.0):
        tampered = _record()
        tampered["fee_round_trip_bps"] = value
        assert c9d.validate_candidate_9_detector_spec_dry_run(
            tampered)["valid"] is False, value
    for value in (0.0, 27.0, 80.0, 82.0, 162.0):
        tampered = _record()
        tampered["target_distance_floor_bps"] = value
        assert c9d.validate_candidate_9_detector_spec_dry_run(
            tampered)["valid"] is False, value


def test_anti_cluster_8_bar_gap_proposal_locked_not_edit_token():
    record = _record()
    assert record["anti_cluster_min_bar_gap"] == 8
    assert record["anti_cluster_tie_breaker"] == (
        "keep_the_earlier_event_drop_the_later_one")
    assert record["anti_cluster_applied_at"] == (
        "label_emission_time_before_replay_non_overlap")
    assert record["anti_cluster_does_not_consume_edit_token"] is True
    for value in (0, 4, 6, 10, 16):
        tampered = _record()
        tampered["anti_cluster_min_bar_gap"] = value
        assert c9d.validate_candidate_9_detector_spec_dry_run(
            tampered)["valid"] is False, value
    tampered = _record()
    tampered["anti_cluster_does_not_consume_edit_token"] = False
    assert c9d.validate_candidate_9_detector_spec_dry_run(
        tampered)["valid"] is False


def test_sample_size_threshold_20_proposal_locked_not_edit_token():
    record = _record()
    assert record["sample_size_adequacy_threshold_min_accepted"] == 20
    assert record[
        "sample_size_adequacy_does_not_consume_edit_token"] is True
    assert record[
        "sample_size_adequacy_enforced_at_labels_review_gate_only"
    ] is True
    for value in (0, 5, 19, 21, 50):
        tampered = _record()
        tampered["sample_size_adequacy_threshold_min_accepted"] = (
            value)
        assert c9d.validate_candidate_9_detector_spec_dry_run(
            tampered)["valid"] is False, value


def test_explicit_edge_argument_proposal_locked_not_edit_token():
    record = _record()
    assert record[
        "explicit_edge_argument_does_not_consume_edit_token"] is True
    tampered = _record()
    tampered["explicit_edge_argument_does_not_consume_edit_token"] = (
        False)
    assert c9d.validate_candidate_9_detector_spec_dry_run(
        tampered)["valid"] is False


def test_data_boundary_frozen():
    record = _record()
    assert record["no_fetch_ever"] is True
    assert record["no_real_time_data"] is True
    assert record["staged_data_never_modified"] is True
    for key in ("no_fetch_ever", "no_real_time_data",
                "staged_data_never_modified"):
        tampered = _record()
        tampered[key] = False
        assert c9d.validate_candidate_9_detector_spec_dry_run(
            tampered)["valid"] is False, key


def test_detector_required_fields_and_statuses_frozen():
    record = _record()
    assert tuple(record["detector_required_fields"]) == (
        c9d.C9_SETUP_REQUIRED_FIELDS)
    assert tuple(record["detector_statuses"]) == (
        c9d.C9_DETECTOR_STATUSES)
    tampered = _record()
    tampered["detector_required_fields"] = ["setup_id"]
    assert c9d.validate_candidate_9_detector_spec_dry_run(
        tampered)["valid"] is False


def test_claim_locks_present_including_proposal_locks():
    record = _record()
    locks = record["claim_locks"]
    for required in (
            "no_profitability_claim", "no_paper_approval",
            "no_live_approval", "no_execution_approval",
            "no_winner_wording",
            "promotion_can_only_produce_a_human_review_record",
            "anti_cluster_gap_is_proposal_level_locked_not_edit"
            "_token",
            "sample_size_threshold_is_proposal_level_locked_not"
            "_edit_token",
            "explicit_edge_argument_field_is_proposal_level_locked"
            "_not_edit_token",
            "real_candle_detection_gate_locked",
            "labels_gate_locked", "replay_gate_locked",
            "relabel_gate_locked"):
        assert required in locks, required
    tampered = _record()
    tampered["claim_locks"] = []
    assert c9d.validate_candidate_9_detector_spec_dry_run(
        tampered)["valid"] is False


# ---- pure detector function behavior ---------------------------------------

def test_median_of_helper_correctness():
    assert c9d._median_of([1.0, 2.0, 3.0]) == 2.0
    assert c9d._median_of([1.0, 2.0, 3.0, 4.0]) == 2.5
    assert c9d._median_of([100.0]) == 100.0
    try:
        c9d._median_of([])
        assert False, "must raise on empty"
    except ValueError:
        pass


def test_validate_detection_context_raises_off_universe():
    c9d.validate_detection_context("BTCUSD", "15m", "long_only")
    for symbol, tf, dirn in (("ETHUSD", "15m", "long_only"),
                             ("BTCUSD", "1h", "long_only"),
                             ("BTCUSD", "15m", "short_only")):
        try:
            c9d.validate_detection_context(symbol, tf, dirn)
            assert False, "must raise on " + str((symbol, tf, dirn))
        except ValueError:
            pass


def test_compute_stop_invalid_when_distance_not_positive():
    # Pathological case where entry <= trigger_low - buffer.
    stop = c9d.compute_stop(entry_price=49000.0, trigger_low=49100.0,
                            atr_at_trigger=50.0)
    assert stop["valid"] is False
    # Real case: entry above trigger_low, with buffer subtraction:
    stop_ok = c9d.compute_stop(entry_price=49200.0,
                               trigger_low=49000.0,
                               atr_at_trigger=126.07)
    assert stop_ok["valid"] is True
    assert stop_ok["stop_distance"] > 0.0
    assert stop_ok["stop_below_entry"] is True
    assert stop_ok["stop_below_trigger_low"] is True


def test_geometry_floor_27_bps_fees_and_81_bps_floor():
    # 2R bps = 80 (under 81) -> 2R fails; 3R/4R pass.
    out = c9d.geometry_floor_by_variant(entry_price=50000.0,
                                        stop_distance=200.0)
    assert out["floor_pass"]["2r"] is False
    assert out["floor_pass"]["3r"] is True
    assert out["floor_pass"]["4r"] is True
    assert out["any_variant_passes"] is True
    # All-fail
    out_fail = c9d.geometry_floor_by_variant(entry_price=50000.0,
                                             stop_distance=50.0)
    assert out_fail["floor_pass"] == {"2r": False, "3r": False,
                                      "4r": False}
    assert out_fail["any_variant_passes"] is False


# ---- synthetic-fixture dry-run summary ------------------------------------

def test_dry_run_fixtures_all_pass_and_summary_shape():
    record = _record()
    fixtures = record["dry_run"]["fixtures"]
    assert record["dry_run"]["failures"] == []
    assert record["dry_run"]["uses_synthetic_fixtures_only"] is True
    assert record["dry_run"]["reads_real_candles"] is False
    assert record["dry_run"]["reads_staged_data"] is False
    assert record["dry_run"]["reads_any_files"] is False
    for name in ("happy_path_joint_trigger", "insufficient_history",
                 "equality_at_z_threshold",
                 "equality_at_volume_median",
                 "z_only_no_volume", "volume_only_no_z",
                 "entry_bar_invalidation",
                 "geometry_floor_all_variants_fail",
                 "anti_cluster", "sample_size_adequacy",
                 "context_enforcement"):
        assert name in fixtures, name


def test_happy_path_joint_trigger_produces_one_accepted_setup():
    fx = _record()["dry_run"]["fixtures"]["happy_path_joint_trigger"]
    assert fx["attempts"] == 1
    assert fx["accepted"] == 1
    assert fx["first_accepted_floor_pass"] == {
        "2r": True, "3r": True, "4r": True}


def test_insufficient_history_emits_zero_attempts():
    fx = _record()["dry_run"]["fixtures"]["insufficient_history"]
    assert fx["attempts"] == 0


def test_equality_at_z_threshold_does_not_trigger():
    fx = _record()["dry_run"]["fixtures"]["equality_at_z_threshold"]
    assert fx["attempts"] == 0


def test_equality_at_volume_median_does_not_trigger():
    fx = _record()["dry_run"]["fixtures"][
        "equality_at_volume_median"]
    assert fx["attempts"] == 0


def test_z_only_no_volume_does_not_trigger():
    fx = _record()["dry_run"]["fixtures"]["z_only_no_volume"]
    assert fx["attempts"] == 0


def test_volume_only_no_z_does_not_trigger():
    fx = _record()["dry_run"]["fixtures"]["volume_only_no_z"]
    assert fx["attempts"] == 0


def test_entry_bar_invalidation_rejects():
    fx = _record()["dry_run"]["fixtures"]["entry_bar_invalidation"]
    assert fx["attempts"] == 1
    assert fx["accepted"] == 0
    assert fx["rejected_entry_invalidation"] == 1


def test_geometry_floor_all_variants_fail_rejects():
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
    assert len(fx["kept_ids"]) == 2
    assert len(fx["dropped_ids"]) == 1


def test_anti_cluster_boundary_at_exactly_8_is_kept():
    seed = {"setup_id": "A", "symbol": "BTCUSD",
            "status": "accepted_for_replay_review",
            "entry_index": 200, "rejection_reasons": []}
    at_gap = dict(seed); at_gap["setup_id"] = "B"
    at_gap["entry_index"] = 208  # exactly +8
    inside = dict(seed); inside["setup_id"] = "C"
    inside["entry_index"] = 207  # +7 (within gap)
    result = c9d.apply_anti_cluster_filter([seed, at_gap])
    assert [s["setup_id"] for s in result["kept"]] == ["A", "B"]
    assert result["dropped"] == []
    result2 = c9d.apply_anti_cluster_filter([seed, inside])
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
    assert fx["non_list_bars"] is True


# ---- safety / capability flags ------------------------------------------

def test_synthetic_dry_run_only_with_all_downstream_gates_locked():
    record = _record()
    assert record["is_synthetic_fixture_dry_run_only"] is True
    assert record["is_spec_review_only"] is False
    assert record["current_loop_stage"] == "detector_and_label_review"
    assert record["human_review_required"] is True
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True
    for key in ("runs_real_candle_detection",
                "runs_real_detection_now", "labels_now",
                "runs_replay", "runs_replay_now", "runs_relabel",
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
        assert c9d.validate_candidate_9_detector_spec_dry_run(
            tampered)["valid"] is False, key


def test_label_next_required_action_and_label_text():
    record = _record()
    assert record["current_loop_stage"] == "detector_and_label_review"
    assert c9d.VERDICT_C9D_SPEC_DRY_RUN_READY == (
        "CANDIDATE_9_DETECTOR_SPEC_DRY_RUN_READY")
    assert c9d.NEXT_REQUIRED_ACTION == (
        "HUMAN_APPROVED_CANDIDATE_9_DRY_RUN_REVIEW")
    for banned in ("PROMOTE", "ACQUIRE", "FETCH",
                   "EXECUTE", "EXECUTION", "BACKTEST", "BASELINE",
                   "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in c9d.NEXT_REQUIRED_ACTION.upper(), banned
    assert c9d.get_candidate_9_detector_label() == c9d.C9D_LABEL
    assert c9d.C9D_MODE == "RESEARCH_ONLY"
    for phrase in ("READ-ONLY", "RESEARCH ONLY",
                   "SYNTHETIC FIXTURES ONLY",
                   "NOT A RESCUE", "NOT A CLAIM"):
        assert phrase in c9d.C9D_LABEL, phrase
    for banned_phrase in ("WINNER", "PROFITABLE",
                          "EDGE CONFIRMED",
                          "APPROVED FOR PAPER",
                          "APPROVED FOR LIVE"):
        assert banned_phrase not in c9d.C9D_LABEL.upper(), (
            banned_phrase)


# ---- module purity --------------------------------------------------------

def test_module_purity_no_banned_imports_no_io_no_main():
    src = open(c9d.__file__, encoding="utf-8").read()
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
    for call in ast.walk(tree):
        if not isinstance(call, ast.Call):
            continue
        name = (call.func.attr if isinstance(call.func, ast.Attribute)
                else getattr(call.func, "id", ""))
        assert name not in ("open", "exec", "eval", "compile"), name
