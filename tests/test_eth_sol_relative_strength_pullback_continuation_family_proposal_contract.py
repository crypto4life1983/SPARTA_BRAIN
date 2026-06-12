"""Tests for the Candidate #5 family proposal contract
(ETH_SOL_RELATIVE_STRENGTH_PULLBACK_CONTINUATION_V1).

Proves: the pushed Autopilot Loop V1 certifies live and validates this
exact proposal through its own gates; material differences from all four
rejected families; seeds inspiration-only with no C4 evidence reuse; no
detector/fetch/replay/labels/artifacts/runners executed; zero trading
capability; no winner/profitability language; non-overlap built in at
policy time; fee-aware geometry before replay; the next stage is
candidate_spec review, not detector execution."""

from __future__ import annotations

import ast

import sparta_commander.eth_sol_relative_strength_pullback_continuation_family_proposal_contract as c5p
import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as ap


def test_autopilot_loop_certifies_live_and_gates_the_proposal():
    loop = ap.build_autopilot_loop_contract()
    assert loop["verdict"] == ap.VERDICT_AP_READY
    assert ap.validate_autopilot_loop_contract(loop)["valid"] is True
    record = c5p.build_candidate_5_family_proposal()
    assert record["verdict"] == c5p.VERDICT_C5P_READY
    assert record["blockers"] == []
    assert c5p.validate_candidate_5_family_proposal(
        record)["valid"] is True
    # the loop's OWN gate validated the proposal inside the build
    assert record["loop_proposal_check"]["acceptable"] is True
    assert record["loop_proposal_check"]["errors"] == []
    assert record["hypothesis_language_check"]["acceptable"] is True
    # determinism
    assert c5p.build_candidate_5_family_proposal() == record


def test_proposal_passes_loop_gate_directly():
    check = ap.validate_candidate_family_proposal(
        dict(c5p.LOOP_PROPOSAL))
    assert check["acceptable"] is True
    assert check["errors"] == []
    assert c5p.LOOP_PROPOSAL["uses_seeds_as_rescue"] is False
    assert c5p.LOOP_PROPOSAL["family"] == (
        "eth_sol_relative_strength_pullback_continuation")
    assert c5p.LOOP_PROPOSAL["family"] not in ap.REJECTED_FAMILIES


def test_material_differences_from_all_four_rejected_families():
    diff = c5p.DIFFERENCE_FROM_REJECTED_FAMILIES
    assert "not ny-session fvg/choch" in diff
    assert "not generic crypto intraday breakout-pullback" in diff
    assert "not long-biased trend continuation" in diff
    assert "not c4 long 1h swing structure" in diff
    assert "required gate, not a post-failure rescue" in diff
    assert "not as a rescue edit" in diff
    assert "fee-aware risk geometry before replay approval" in diff
    # the family id itself is none of the rejected families
    for family in ap.REJECTED_FAMILIES:
        assert c5p.CANDIDATE_FAMILY != family


def test_seed_usage_is_inspiration_only_no_c4_rescue():
    seeds = c5p.SEED_USAGE
    assert ("same_symbol_non_overlap_cooldown_inherited_as_built_in"
            "_machinery") in seeds
    assert ("sol_c4_clue_is_inspiration_only_not_evidence_of_edge"
            in seeds)
    assert ("btc_weakness_from_c4_is_not_reused_as_edge_evidence"
            in seeds)
    assert ("structural_stop_and_clustering_lessons_used_as_risk"
            "_controls_only") in seeds
    assert ("no_c4_setup_ids_replay_rows_or_labels_may_be_reused_as"
            "_evidence") in seeds
    record = c5p.build_candidate_5_family_proposal()
    assert record["reuses_c4_evidence"] is False
    rescue = dict(c5p.LOOP_PROPOSAL, uses_seeds_as_rescue=True)
    assert ap.validate_candidate_family_proposal(
        rescue)["acceptable"] is False
    tampered = c5p.build_candidate_5_family_proposal()
    tampered["loop_proposal"] = rescue
    assert c5p.validate_candidate_5_family_proposal(
        tampered)["valid"] is False


def test_hypothesis_definitions_frozen():
    record = c5p.build_candidate_5_family_proposal()
    assert record["candidate_id"] == (
        "ETH_SOL_RELATIVE_STRENGTH_PULLBACK_CONTINUATION_V1")
    assert record["symbols"] == ["ETHUSD", "SOLUSD"]
    assert record["timeframe"] == "1h"
    assert record["direction"] == "long_only"
    rs = record["relative_strength_condition"]
    assert rs["lookback_bars_1h"] == 20
    assert rs["uses_completed_bars_only_no_lookahead"] is True
    assert rs["is_a_required_gate_not_a_rescue"] is True
    pullback = record["pullback_condition"]
    assert pullback["min_bars"] == 2
    assert pullback["max_bars"] == 6
    assert pullback["max_retrace_pct_of_leg"] == 38.2
    assert pullback["must_hold_above_leg_low"] is True
    trigger = record["continuation_trigger"]
    assert trigger["entry_price"] == "close_of_the_trigger_bar"
    assert "next 1h bar" in trigger["anti_lookahead"]
    assert trigger["one_setup_per_pullback"] is True
    stops = record["stop_logic_policy"]
    assert stops["selection"] == (
        "WIDER_of_structural_and_volatility_stop_always")
    assert stops["never_tightened_after_entry"] is True
    assert "ONE pre-committed edit" in record["edit_allowance_policy"]
    assert "REJECTED_KEPT_ON_RECORD" in record["edit_allowance_policy"]
    for field, value in (("symbols", ["ETHUSD", "SOLUSD", "BTCUSD"]),
                         ("direction", "both"),
                         ("clean_hypothesis", "different"),
                         ("candidate_family", "long_1h_swing_structure")):
        tampered = c5p.build_candidate_5_family_proposal()
        tampered[field] = value
        assert c5p.validate_candidate_5_family_proposal(
            tampered)["valid"] is False, field


def test_non_overlap_built_in_and_fee_geometry_before_replay():
    record = c5p.build_candidate_5_family_proposal()
    overlap = record["non_overlap_policy"]
    assert "BUILT-IN" in overlap["definition"]
    assert "label/replay policy time" in overlap["definition"]
    assert overlap["inherited_from_c4_as_machinery_not_rescue"] is True
    assert overlap[
        "applied_at_label_replay_time_not_as_rescue_edit"] is True
    fee = record["fee_aware_geometry_policy"]
    assert fee["minimum_risk_distance_bps"] == 81
    assert fee["checked_at_label_time"] is True
    assert fee["assumed_round_trip_cost_bps"] == 27
    assert fee["maker_execution_assumed"] is False
    assert fee["floor_may_be_lowered"] is False
    assert fee[
        "fee_aware_geometry_required_before_replay_approval"] is True
    for field in ("non_overlap_policy", "fee_aware_geometry_policy"):
        tampered = c5p.build_candidate_5_family_proposal()
        tampered[field] = {}
        assert c5p.validate_candidate_5_family_proposal(
            tampered)["valid"] is False, field


def test_evidence_stages_rejections_and_promotion_conditions():
    record = c5p.build_candidate_5_family_proposal()
    assert record["required_evidence_stages"] == list(ap.LOOP_STAGES)
    assert record["rejection_conditions"] == list(
        ap.AUTO_REJECTION_RULES)
    promo = record["promotion_to_human_review_conditions"]
    assert any("overlap-adjusted independent sample" in item
               for item in promo)
    assert any("human-review record only: no claim" in item
               for item in promo)
    safety = record["safety_and_no_claim"]
    assert any("no trading, no paper trading, no live" in item
               for item in safety)
    assert any("no wallet, account, api, or order" in item
               for item in safety)
    assert any("no auto-push, no auto-commit" in item for item in safety)
    assert any("no profitability claim and no winner wording" in item
               for item in safety)
    assert any("evidence language only" in item for item in safety)


def test_no_winner_or_profitability_language():
    assert ap.screen_output_language(
        c5p.CLEAN_HYPOTHESIS)["acceptable"] is True
    assert ap.screen_output_language(
        c5p.DIFFERENCE_FROM_REJECTED_FAMILIES)["acceptable"] is True
    for token in ("winner", "profitable", "ready for live",
                  "ready for paper", "edge confirmed", "guaranteed"):
        assert token not in c5p.CLEAN_HYPOTHESIS.lower()
        assert token not in c5p.C5P_LABEL.lower()


def test_next_stage_is_candidate_spec_review_not_detector():
    record = c5p.build_candidate_5_family_proposal()
    assert record["next_loop_stage"] == "candidate_spec"
    assert record["next_loop_stage"] == ap.LOOP_STAGES[0]
    assert c5p.NEXT_REQUIRED_ACTION == (
        "HUMAN_APPROVED_CANDIDATE_5_SPEC_REVIEW")
    assert "DETECTOR" not in c5p.NEXT_REQUIRED_ACTION
    assert record["runs_real_detection_now"] is False
    tampered = c5p.build_candidate_5_family_proposal()
    tampered["next_loop_stage"] = "fee_honest_replay"
    assert c5p.validate_candidate_5_family_proposal(
        tampered)["valid"] is False


def test_zero_capability_and_gates_locked():
    record = c5p.build_candidate_5_family_proposal()
    for key in ("executes", "writes_files", "labels_now",
                "runs_real_detection_now", "runs_replay_now",
                "scores_now", "stages_data_now", "fetches_data",
                "calls_api", "uses_network", "uses_credentials",
                "uses_wallet", "uses_account", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "auto_commits", "auto_pushes",
                "creates_runners_now", "creates_data_artifacts_now",
                "reuses_c4_evidence",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate", "claims_profitability"):
        assert record[key] is False, key
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True
    for field, value in (("claims_profitability", True),
                         ("auto_pushes", True),
                         ("creates_data_artifacts_now", True),
                         ("reuses_c4_evidence", True),
                         ("live_gate_locked", False),
                         ("seed_usage", []),
                         ("safety_and_no_claim", []),
                         ("rejection_conditions", []),
                         ("required_evidence_stages", [])):
        tampered = c5p.build_candidate_5_family_proposal()
        tampered[field] = value
        assert c5p.validate_candidate_5_family_proposal(
            tampered)["valid"] is False, field


def test_ledger_intact_and_module_purity():
    from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
        REJECTION_STATUS as C1)
    from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (
        REJECTION_STATUS as C2)
    from sparta_commander.btc_sol_long_trend_continuation_v1_result_and_rejection_record_contract import (
        REJECTION_STATUS as C3)
    from sparta_commander.sol_btc_long_1h_swing_structure_rejection_record_contract import (
        REJECTION_STATUS as C4)
    assert C1 == C2 == C3 == C4 == "REJECTED_KEPT_ON_RECORD"
    assert c5p.get_candidate_5_proposal_label() == c5p.C5P_LABEL
    assert "READ-ONLY" in c5p.C5P_LABEL
    assert "NOT A RESCUE" in c5p.C5P_LABEL
    assert c5p.C5P_MODE == "RESEARCH_ONLY"
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in c5p.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(c5p.__file__, encoding="utf-8").read()
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
                   "ssl", "ftplib", "datetime", "hashlib", "statistics"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
    assert not any(
        call.func.attr == "open" if isinstance(call.func, ast.Attribute)
        else getattr(call.func, "id", "") == "open"
        for call in ast.walk(tree) if isinstance(call, ast.Call))
