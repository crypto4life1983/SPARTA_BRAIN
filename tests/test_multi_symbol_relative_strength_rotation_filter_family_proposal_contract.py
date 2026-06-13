"""Tests for the Candidate #6 family proposal contract
(MULTI_SYMBOL_RELATIVE_STRENGTH_ROTATION_FILTER_V1).

Proves: Recommendation V1 + Autopilot V1 + five-record ledger gate the
build; the proposal passes the loop's own proposal gate AND the
recommendation's hard rules; the selected candidate equals the frozen
preferred pick; material differences from all five rejected families;
inspiration-only seeds with no C5 rescue path; zero execution; no
claims; next stage is candidate_spec review. Tamper tests on every
frozen block. Commander safety suite runs alongside."""

from __future__ import annotations

import ast

import sparta_commander.multi_symbol_relative_strength_rotation_filter_family_proposal_contract as c6p
import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as ap
import sparta_commander.strategy_factory_candidate_recommendation_v1_contract as cr


def test_proposal_ready_and_gated_on_all_three_layers():
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
    record = c6p.build_candidate_6_family_proposal()
    assert record["verdict"] == c6p.VERDICT_C6P_READY
    assert record["blockers"] == []
    assert c6p.validate_candidate_6_family_proposal(
        record)["valid"] is True
    # both pushed gate layers validated the proposal inside the build
    assert record["loop_proposal_check"]["acceptable"] is True
    assert record["loop_proposal_check"]["errors"] == []
    assert record["hypothesis_language_check"]["acceptable"] is True
    assert record["recommendation_hard_rules_check"][
        "acceptable"] is True
    assert record["recommendation_hard_rules_check"][
        "rejections"] == []
    assert c6p.build_candidate_6_family_proposal() == record


def test_selected_candidate_is_the_recommendation_preferred():
    record = c6p.build_candidate_6_family_proposal()
    assert record["selected_candidate_id"] == (
        "MULTI_SYMBOL_RELATIVE_STRENGTH_ROTATION_FILTER_V1")
    assert record["candidate_id"] == record["selected_candidate_id"]
    assert record["recommendation_preferred_matches"] is True
    recommendation = cr.build_candidate_recommendation()
    assert recommendation["preferred_candidate_6"] == (
        record["selected_candidate_id"])
    assert recommendation[
        "preferred_is_proposal_recommendation_only"] is True


def test_proposal_passes_loop_gate_and_hard_rules_directly():
    check = ap.validate_candidate_family_proposal(
        dict(c6p.LOOP_PROPOSAL))
    assert check["acceptable"] is True
    assert check["errors"] == []
    assert c6p.LOOP_PROPOSAL["uses_seeds_as_rescue"] is False
    assert c6p.CANDIDATE_FAMILY not in ap.REJECTED_FAMILIES
    assert c6p.CANDIDATE_FAMILY not in cr.ALL_REJECTED_FAMILIES
    rescue = dict(c6p.LOOP_PROPOSAL, uses_seeds_as_rescue=True)
    assert ap.validate_candidate_family_proposal(
        rescue)["acceptable"] is False


def test_material_differences_from_all_five():
    diff = c6p.DIFFERENCE_FROM_REJECTED_FAMILIES
    assert "not ny-session fvg/choch" in diff
    assert "not generic breakout-pullback rescue logic" in diff
    assert "not long-biased trend continuation" in diff
    assert "not generic sol/btc long swing structure" in diff
    assert "not eth/sol shallow pullback continuation" in diff
    assert "cross-sectional symbol ranking before any entry logic" \
        in diff
    assert "core filter, not a post-failure edit" in diff
    assert "no single-symbol setup can qualify without ranking context" \
        in diff


def test_seed_usage_inspiration_only_no_c5_rescue():
    seeds = c6p.SEED_USAGE
    assert ("sol_side_relative_strength_recurrence_is_inspiration_only"
            in seeds)
    assert ("c5_gross_positive_2r_observation_is_not_promotion"
            "_evidence" in seeds)
    assert ("thin_risk_fee_sensitivity_is_a_risk_control_lesson_only"
            in seeds)
    assert any("avoid_delayed_pullback_rescue_entries" in seed
               for seed in seeds)
    assert ("same_symbol_non_overlap_remains_a_risk_control_lesson"
            in seeds)
    assert ("eth_c5_negative_contribution_is_not_edge_evidence"
            in seeds)
    assert any("no_c1_c5_setup_ids_replay_rows_or_labels" in seed
               for seed in seeds)
    assert c6p.SEEDS_ARE_NEVER_RESCUE_PATHS is True
    continuation = c6p.CONTINUATION_CONDITION
    assert continuation[
        "avoids_delayed_pullback_resumption_scarcity_from_c5"] is True
    assert continuation[
        "does_not_reuse_c5_shallow_pullback_as_is"] is True


def test_definitions_frozen():
    record = c6p.build_candidate_6_family_proposal()
    assert record["symbols"] == ["BTCUSD", "ETHUSD", "SOLUSD"]
    assert record["timeframe"] == "1h"
    assert record["direction"] == "long_only"
    assert "research labels" in record["direction_note"]
    ranking = record["ranking_condition"]
    assert ranking["symbols_compared_simultaneously"] is True
    assert ranking["no_future_bars"] is True
    assert ranking["no_same_bar_lookahead"] is True
    assert ranking[
        "rs_metric_and_lookback_frozen_numerically_at_spec_review"] \
        is True
    assert "rank #1 at trigger time" in ranking["definition"]
    fee = record["fee_aware_geometry_policy"]
    assert fee["fee_model_round_trip_bps"] == 27
    assert fee["minimum_gross_target_distance_floor_bps"] == 81
    assert fee["floor_checked_before_replay_eligibility"] is True
    assert fee["no_maker_rebate_assumption"] is True
    assert fee["no_zero_fee_assumption"] is True
    overlap = record["non_overlap_policy"]
    assert overlap["built_in_at_label_replay_policy_time"] is True
    assert overlap["reduce_or_keep_only_never_add_trades"] is True
    stops = record["stop_logic_policy"]
    assert "WIDER" in stops["rule"]
    assert stops["never_tightened_after_entry"] is True
    assert "ONE pre-committed edit" in record["edit_allowance_policy"]
    assert record["required_evidence_stages"] == list(ap.LOOP_STAGES)
    assert record["rejection_conditions"] == list(
        ap.AUTO_REJECTION_RULES)
    promo = record["promotion_to_human_review_conditions"]
    assert any("human-review record only: no claim" in item
               for item in promo)
    assert any("sample size not near-zero" in item for item in promo)


def test_next_stage_is_candidate_spec_review_not_detector():
    record = c6p.build_candidate_6_family_proposal()
    assert record["next_loop_stage"] == "candidate_spec"
    assert record["next_loop_stage"] == ap.LOOP_STAGES[0]
    assert c6p.NEXT_REQUIRED_ACTION == (
        "HUMAN_APPROVED_CANDIDATE_6_SPEC_REVIEW")
    assert "DETECTOR" not in c6p.NEXT_REQUIRED_ACTION
    assert record["runs_real_detection_now"] is False
    assert record["creates_detector_label_replay_files_now"] is False
    tampered = c6p.build_candidate_6_family_proposal()
    tampered["next_loop_stage"] = "fee_honest_replay"
    assert c6p.validate_candidate_6_family_proposal(
        tampered)["valid"] is False


def test_record_tampering_invalidates():
    for field, value in (
            ("selected_candidate_id", "SOMETHING_ELSE"),
            ("candidate_id", "SOMETHING_ELSE"),
            ("candidate_family", "long_1h_swing_structure"),
            ("clean_hypothesis", "different"),
            ("difference_from_rejected_families", "none"),
            ("loop_proposal", {"uses_seeds_as_rescue": True}),
            ("symbols", ["BTCUSD", "ETHUSD", "SOLUSD", "DOGEUSD"]),
            ("direction", "both"),
            ("ranking_condition", {}),
            ("continuation_condition", {}),
            ("fee_aware_geometry_policy", {}),
            ("non_overlap_policy", {}),
            ("seed_usage", []),
            ("seeds_are_never_rescue_paths", False),
            ("required_evidence_stages", []),
            ("rejection_conditions", []),
            ("safety_and_no_claim", []),
            ("claims_profitability", True),
            ("auto_pushes", True),
            ("contains_portfolio_allocation_logic", True),
            ("live_gate_locked", False),
            ("verdict", "CANDIDATE_6_APPROVED_FOR_TRADING")):
        tampered = c6p.build_candidate_6_family_proposal()
        tampered[field] = value
        assert c6p.validate_candidate_6_family_proposal(
            tampered)["valid"] is False, field


def test_zero_capability_and_gates_locked():
    record = c6p.build_candidate_6_family_proposal()
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
                "creates_detector_label_replay_files_now",
                "modifies_staged_market_data",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate", "claims_profitability"):
        assert record[key] is False, key
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True
    assert ap.screen_output_language(
        c6p.CLEAN_HYPOTHESIS)["acceptable"] is True
    assert ap.screen_output_language(
        c6p.DIFFERENCE_FROM_REJECTED_FAMILIES)["acceptable"] is True


def test_label_action_and_module_purity():
    assert c6p.get_candidate_6_proposal_label() == c6p.C6P_LABEL
    assert "READ-ONLY" in c6p.C6P_LABEL
    assert "NOT A RESCUE" in c6p.C6P_LABEL
    assert c6p.C6P_MODE == "RESEARCH_ONLY"
    assert c6p.VERDICT_C6P_READY == "CANDIDATE_6_FAMILY_PROPOSAL_READY"
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in c6p.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(c6p.__file__, encoding="utf-8").read()
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
