"""Tests for the Strategy Factory Candidate Family Recommendation V1.

Proves: the five-candidate ledger and Autopilot V1 gate the build; all
safety locks; future-family-only seed inventory; all three
recommendations are materially different from C1-C5 and pass the loop's
own proposal gate plus the hard rejection rules; rescue-path wording is
rejected; the preferred Candidate #6 is selected deterministically; zero
execution of any kind; no claims. Tamper tests on every frozen block.
Commander safety suite runs alongside."""

from __future__ import annotations

import ast

import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as ap
import sparta_commander.strategy_factory_candidate_recommendation_v1_contract as cr


def test_recommendation_ready_and_gated_on_five_record_ledger():
    record = cr.build_candidate_recommendation()
    assert record["verdict"] == cr.VERDICT_CR_READY
    assert record["blockers"] == []
    assert cr.validate_candidate_recommendation(record)["valid"] is True
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
    assert ap.build_autopilot_loop_contract()["verdict"] == (
        ap.VERDICT_AP_READY)
    ledger = record["five_candidate_ledger"]
    assert len([key for key in ledger
                if key.startswith("candidate_")]) == 5
    assert ledger["candidate_5"]["reason"] == (
        "SMALL_SAMPLE_NET_NEGATIVE_AND_EDIT_ADDED_NOTHING")
    assert ledger[
        "zero_trades_zero_claims_zero_deleted_evidence"] is True
    assert cr.build_candidate_recommendation() == record  # determinism


def test_all_three_recommendations_pass_loop_gate_and_hard_rules():
    record = cr.build_candidate_recommendation()
    assert set(record["recommendations"]) == {
        "SOL_RELATIVE_STRENGTH_BREAKOUT_CONTINUATION_V1",
        "MULTI_SYMBOL_RELATIVE_STRENGTH_ROTATION_FILTER_V1",
        "VOLATILITY_EXPANSION_AFTER_RS_COMPRESSION_V1"}
    for key, checks in record["recommendation_checks"].items():
        assert checks["loop_gate"]["acceptable"] is True, key
        assert checks["loop_gate"]["errors"] == [], key
        assert checks["hard_rules"]["acceptable"] is True, key
        assert checks["hard_rules"]["rejections"] == [], key
    for key, rec in record["recommendations"].items():
        for field in ("family_id", "hypothesis", "symbols", "timeframe",
                      "direction", "materially_different_because",
                      "seeds_inspiring_it", "why_not_rescue",
                      "expected_failure_risks", "required_spec_gates",
                      "no_claim"):
            assert rec.get(field), (key, field)
        assert rec["direction"] == "long_only", key
        assert rec["timeframe"] == "1h", key
        assert rec["family"] not in cr.ALL_REJECTED_FAMILIES, key
        assert "81_bps_floor_at_label_time" in rec[
            "required_spec_gates"], key
        assert "27_bps_fee_model" in rec["required_spec_gates"], key
        assert "no profitability claim" in rec["no_claim"], key
        assert ap.screen_output_language(
            rec["hypothesis"])["acceptable"] is True, key


def test_materially_different_from_all_five():
    for key, rec in cr.RECOMMENDATIONS.items():
        diff = rec["materially_different_because"]
        # each recommendation must address every prior failure family
        assert "c1" in diff or "session" in diff or "fvg" in diff, key
        assert "c2" in diff or "breakout-retest" in diff \
            or "retest" in diff, key
        assert "c3" in diff or "micro-pattern" in diff, key
        assert "c4" in diff or "swing" in diff, key
        assert "c5" in diff or "pullback" in diff \
            or "resumption" in diff, key


def test_hard_rejection_rules_work():
    # same as prior family
    reused = dict(cr.RECOMMENDATIONS[
        "SOL_RELATIVE_STRENGTH_BREAKOUT_CONTINUATION_V1"])
    reused["family"] = "long_1h_swing_structure"
    check = cr.apply_hard_rejection_rules(reused)
    assert check["acceptable"] is False
    assert "reject_if_same_as_any_prior_family" in check["rejections"]
    # winner language
    bragging = dict(cr.RECOMMENDATIONS[
        "VOLATILITY_EXPANSION_AFTER_RS_COMPRESSION_V1"])
    bragging["hypothesis"] = "this winner strategy is clearly profitable"
    check = cr.apply_hard_rejection_rules(bragging)
    assert check["acceptable"] is False
    assert ("reject_if_it_uses_winner_or_profitability_language"
            in check["rejections"])
    # fee removal via missing gates
    feeless = dict(cr.RECOMMENDATIONS[
        "MULTI_SYMBOL_RELATIVE_STRENGTH_ROTATION_FILTER_V1"])
    feeless["required_spec_gates"] = ("wider_stop_rule",)
    check = cr.apply_hard_rejection_rules(feeless)
    assert check["acceptable"] is False
    assert ("reject_if_it_removes_fees_or_lowers_fee_floor"
            in check["rejections"])
    # fee removal via wording
    feeless2 = dict(cr.RECOMMENDATIONS[
        "MULTI_SYMBOL_RELATIVE_STRENGTH_ROTATION_FILTER_V1"])
    feeless2["hypothesis"] = "evaluate zero-fee performance"
    assert ("reject_if_it_removes_fees_or_lowers_fee_floor"
            in cr.apply_hard_rejection_rules(feeless2)["rejections"])
    # c5 continuation dependence
    rescue = dict(cr.RECOMMENDATIONS[
        "SOL_RELATIVE_STRENGTH_BREAKOUT_CONTINUATION_V1"])
    rescue["why_not_rescue"] = "we just continue c5 as-is with a tweak"
    assert ("reject_if_it_depends_on_c5_continuation_as_is"
            in cr.apply_hard_rejection_rules(rescue)["rejections"])
    # rs gate weakening
    weakened = dict(cr.RECOMMENDATIONS[
        "SOL_RELATIVE_STRENGTH_BREAKOUT_CONTINUATION_V1"])
    weakened["hypothesis"] = "use a weaker rs gate to add trades"
    assert ("reject_if_it_weakens_rs_gate_just_to_add_trades"
            in cr.apply_hard_rejection_rules(weakened)["rejections"])
    # tiny sample promotion
    tiny = dict(cr.RECOMMENDATIONS[
        "VOLATILITY_EXPANSION_AFTER_RS_COMPRESSION_V1"])
    tiny["hypothesis"] = "promote on the small sample we already have"
    assert ("reject_if_it_depends_on_tiny_sample_promotion"
            in cr.apply_hard_rejection_rules(tiny)["rejections"])
    # direction outside long_only research scope
    directional = dict(cr.RECOMMENDATIONS[
        "VOLATILITY_EXPANSION_AFTER_RS_COMPRESSION_V1"])
    directional["direction"] = "live_both_ways"
    assert ("reject_if_it_has_paper_live_trading_capability"
            in cr.apply_hard_rejection_rules(directional)["rejections"])
    assert cr.apply_hard_rejection_rules(None)["acceptable"] is False
    # loop gate rejects rescue-path wording end to end
    rescue_proposal = {
        "family": "a_new_family",
        "hypothesis": "a clean test",
        "difference_from_rejected_families": "different",
        "uses_seeds_as_rescue": True}
    assert ap.validate_candidate_family_proposal(
        rescue_proposal)["acceptable"] is False


def test_seed_inventory_future_family_only():
    seeds = cr.SEED_INVENTORY_FUTURE_FAMILY_ONLY
    assert len(seeds) == 10
    for seed in (
            "cost_geometry_can_kill_an_otherwise_plausible_idea",
            "breakout_pullback_edge_failure_must_not_be_rescued_by"
            "_weaker_filters",
            "near_zero_setup_count_after_structure_edit_is_a_kill"
            "_condition",
            "same_symbol_overlap_correlation_must_be_penalized",
            "sol_side_relative_strength_recurrence_across_c4_c5_is"
            "_inspiration_only",
            "thin_risk_fee_sensitivity_must_be_filtered_before_replay",
            "trigger_resumption_scarcity_is_a_structural_lesson",
            "same_symbol_non_overlap_can_remove_winners",
            "eth_side_negative_contribution_in_c5_is_not_edge_evidence",
            "btc_weakness_in_c4_is_not_edge_evidence"):
        assert seed in seeds, seed
    rules = cr.PROPOSAL_RULES
    assert any("only as inspiration" in rule for rule in rules)
    assert any("never use seeds as rescue paths" in rule
               for rule in rules)
    assert any("never reuse rejected geometry unchanged" in rule
               for rule in rules)
    assert any("validate_candidate_family_proposal" in rule
               for rule in rules)
    assert any("evidence language only" in rule for rule in rules)


def test_preferred_candidate_6_selected_deterministically():
    record = cr.build_candidate_recommendation()
    assert record["preferred_candidate_6"] == (
        "MULTI_SYMBOL_RELATIVE_STRENGTH_ROTATION_FILTER_V1")
    assert record["preferred_candidate_6"] in record["recommendations"]
    assert record["preferred_is_proposal_recommendation_only"] is True
    rationale = record["preferred_rationale"]
    assert any("most structurally different" in item
               for item in rationale)
    assert any("most likely to avoid the five known failure modes"
               in item for item in rationale)
    assert any("proposal recommendation only, not execution" in item
               for item in rationale)
    # deterministic across builds
    assert cr.build_candidate_recommendation()[
        "preferred_candidate_6"] == record["preferred_candidate_6"]


def test_record_tampering_invalidates():
    record = cr.build_candidate_recommendation()
    for field, value in (
            ("five_candidate_ledger", {}),
            ("all_rejected_families", []),
            ("proposal_rules", []),
            ("seed_inventory_future_family_only", []),
            ("hard_rejection_rules", []),
            ("recommendations", {}),
            ("preferred_candidate_6", "SOMETHING_ELSE"),
            ("preferred_rationale", []),
            ("preferred_is_proposal_recommendation_only", False),
            ("claims_profitability", True),
            ("auto_pushes", True),
            ("auto_commits", True),
            ("creates_candidate_6_execution_files", True),
            ("live_gate_locked", False),
            ("verdict", "CANDIDATE_6_APPROVED")):
        tampered = cr.build_candidate_recommendation()
        tampered[field] = value
        assert cr.validate_candidate_recommendation(
            tampered)["valid"] is False, field
    four_ledger = cr.build_candidate_recommendation()
    del four_ledger["five_candidate_ledger"]["candidate_5"]
    assert cr.validate_candidate_recommendation(
        four_ledger)["valid"] is False
    renamed = cr.build_candidate_recommendation()
    renamed["five_candidate_ledger"]["candidate_4"]["family"] = "other"
    assert cr.validate_candidate_recommendation(
        renamed)["valid"] is False


def test_zero_capability_and_no_claims():
    record = cr.build_candidate_recommendation()
    for key in ("executes", "writes_files", "labels_now",
                "runs_real_detection_now", "runs_replay_now",
                "scores_now", "stages_data_now", "fetches_data",
                "calls_api", "uses_network", "uses_credentials",
                "uses_wallet", "uses_account", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "auto_commits", "auto_pushes",
                "creates_runners_now", "creates_data_artifacts_now",
                "creates_candidate_6_execution_files",
                "modifies_staged_market_data",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate", "claims_profitability"):
        assert record[key] is False, key
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True
    for key, rec in record["recommendations"].items():
        assert ap.screen_output_language(
            " ".join(str(v) for v in rec.values()
                     if isinstance(v, str)))["acceptable"] is True, key


def test_label_verdict_and_module_purity():
    assert cr.get_candidate_recommendation_label() == cr.CR_LABEL
    assert "READ-ONLY" in cr.CR_LABEL
    assert "NEVER EXECUTION" in cr.CR_LABEL
    assert cr.CR_MODE == "RESEARCH_ONLY"
    assert cr.VERDICT_CR_READY == (
        "STRATEGY_FACTORY_CANDIDATE_RECOMMENDATION_V1_READY")
    assert cr.NEXT_REQUIRED_ACTION == (
        "HUMAN_APPROVED_CANDIDATE_6_FAMILY_PROPOSAL_VIA_AUTOPILOT_LOOP")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in cr.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(cr.__file__, encoding="utf-8").read()
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
