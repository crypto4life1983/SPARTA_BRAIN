"""Tests for the SPARTA NY FVG+CHOCH Mutable Candidate Edit V2 - Cost
Viability Filter.

Proves V2 adds ONLY the five cost-viability parameters to the mutable
candidate asset, that sub-81bps setups (including every cost-broken V1
replay) are rejected, that 2x/4x variants are noted but inactive, and that
everything locked stays locked with human approval still required before
any V2 re-detection or replay.
"""

from __future__ import annotations

import ast

import sparta_commander.ny_session_fvg_choch_mutable_candidate_edit_v2_cost_viability as m2
from sparta_commander.ny_session_fvg_choch_fee_honest_replay_results_review_contract import (
    EXPECTED_PER_LABEL,
)
from sparta_commander.ny_session_fvg_choch_mutable_candidate_edit_v1 import (
    build_edited_candidate_asset as build_v1_asset,
)


def test_edit_v2_is_ready_and_asset_accepted():
    record = m2.build_mutable_candidate_edit_v2()
    assert record["verdict"] == m2.VERDICT_M2_READY
    assert record["blockers"] == []
    assert record["edited_asset_verdict"] == (
        "CANDIDATE_ASSET_ACCEPTED_FOR_RESEARCH")
    assert record["candidate_id"] == (
        "NY_SESSION_FVG_CHOCH_STRATEGY_CANDIDATE_V1")
    assert m2.validate_mutable_candidate_edit_v2(record)["valid"] is True


def test_exactly_five_v2_parameters_with_approved_values():
    assert m2.V2_NEW_PARAMETERS == {
        "reject_cost_dominated_setups": True,
        "round_trip_cost_bps": 27,
        "minimum_risk_to_round_trip_cost_multiple": 3,
        "minimum_risk_distance_bps": 81,
        "require_entry_to_stop_distance_bps_gte_minimum": True}
    assert m2.MINIMUM_RISK_DISTANCE_BPS == 27 * 3 == 81
    edited = m2.build_edited_candidate_asset_v2()
    parameters = edited["fields"]["parameters"]
    for key, value in m2.V2_NEW_PARAMETERS.items():
        assert parameters[key] == value, key


def test_only_mutable_candidate_rules_changed():
    v1 = build_v1_asset()
    v2 = m2.build_edited_candidate_asset_v2()
    # V1 builder output is NOT mutated by V2
    assert "minimum_risk_distance_bps" not in v1["fields"]["parameters"]
    # outer research flags identical
    for key in ("research_only", "live_trading_authorized",
                "paper_trading_authorized", "human_review_required",
                "optimizer_may_edit", "locked_instructions_may_edit",
                "locked_scorer_may_edit"):
        assert v2[key] == v1[key], key
    changed = {name for name in v1["fields"]
               if v2["fields"][name] != v1["fields"][name]}
    assert changed == {"parameters", "constraints", "lineage",
                       "audit_notes", "rationale"}
    # every V1 parameter is preserved inside V2
    for key, value in v1["fields"]["parameters"].items():
        assert v2["fields"]["parameters"][key] == value, key
    assert v2["fields"]["parameters"]["max_fvg_age_bars"] == 24
    assert v2["fields"]["parameters"][
        "require_fresh_unmitigated_15m_fvg"] is True
    assert v2["fields"]["parameters"][
        "max_zone_touches_before_invalidation"] == 2
    assert v2["fields"]["status"] == "proposed"


def test_locked_scorer_instructions_and_detector_unchanged():
    from sparta_commander.crypto_d1_auto_research_strategy_optimizer_contract import (
        FORBIDDEN_FOREVER, LOCKED_HUMAN_INSTRUCTIONS, LOCKED_SCORING_RULES)
    assert len(LOCKED_HUMAN_INSTRUCTIONS) == 7
    assert len(LOCKED_SCORING_RULES) == 9
    assert len(FORBIDDEN_FOREVER) == 12
    from sparta_commander.ny_session_fvg_choch_detector_spec import (
        DETECTOR_STATUSES, LABEL_REQUIRED_FIELDS)
    assert len(LABEL_REQUIRED_FIELDS) == 29
    assert len(DETECTOR_STATUSES) == 9
    from sparta_commander.ny_session_fvg_choch_strategy_spec_contract import (
        DETERMINISTIC_RULES, FIB_LEVEL, FIB_TOLERANCE, RISK_REWARD_TARGET)
    assert FIB_LEVEL == 0.618 and FIB_TOLERANCE == 0.05
    assert RISK_REWARD_TARGET == 4.0
    assert "trigger_1m_bullish_choch" in DETERMINISTIC_RULES
    assert "htf_15m_bullish_fvg" in DETERMINISTIC_RULES
    record = m2.build_mutable_candidate_edit_v2()
    for key in ("modifies_locked_scorer", "modifies_locked_instructions",
                "modifies_detector_rules",
                "modifies_detector_label_schema"):
        assert record[key] is False, key
    for guarantee in ("locked_scorer_unchanged",
                      "locked_instructions_unchanged",
                      "choch_rule_unchanged",
                      "fib_0618_plus_minus_5pct_unchanged",
                      "4r_target_definition_unchanged",
                      "v1_freshness_controls_unchanged_24_true_2"):
        assert guarantee in record["unchanged_guarantees"], guarantee


def test_no_replay_pnl_scoring_or_paper_live_added():
    edited = m2.build_edited_candidate_asset_v2()
    for name in list(edited["fields"]) + list(
            edited["fields"]["parameters"]):
        lowered = str(name).lower()
        for token in ("pnl", "profit", "replay", "win_rate", "net_r",
                      "gross_r", "paper", "live_trading"):
            assert token not in lowered, name
    assert edited["live_trading_authorized"] is False
    assert edited["paper_trading_authorized"] is False
    record = m2.build_mutable_candidate_edit_v2()
    for key in ("runs_replay_now", "scores_now", "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading"):
        assert record[key] is False, key
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True


def test_setups_below_81_bps_are_rejected():
    # 50 bps risk distance: cost-dominated, rejected
    fifty = m2.evaluate_setup_cost_viability(100.0, 99.50)
    assert fifty["viable"] is False
    assert fifty["entry_to_stop_distance_bps"] == 50.0
    assert "cost_dominated_setup_rejected" in fifty["reason"]
    # 80.9 bps: still below the floor, rejected
    edge = m2.evaluate_setup_cost_viability(100.0, 99.1910)
    assert edge["viable"] is False
    # 81 bps exactly: viable
    exact = m2.evaluate_setup_cost_viability(100.0, 99.19)
    assert exact["entry_to_stop_distance_bps"] == 81.0
    assert exact["viable"] is True
    # 120 bps: viable
    wide = m2.evaluate_setup_cost_viability(100.0, 98.80)
    assert wide["viable"] is True
    # shorts mirror (stop above entry)
    short = m2.evaluate_setup_cost_viability(100.0, 101.0)
    assert short["viable"] is True
    tight_short = m2.evaluate_setup_cost_viability(100.0, 100.05)
    assert tight_short["viable"] is False
    # invalid prices never pass
    assert m2.evaluate_setup_cost_viability(None, 99.0)["viable"] is False
    assert m2.evaluate_setup_cost_viability(0.0, 99.0)["viable"] is False
    assert m2.evaluate_setup_cost_viability(100.0, -1.0)["viable"] is False


def test_cost_broken_v1_replays_would_not_pass_v2():
    # implied risk distance from the FROZEN replay evidence (27bps / cost_R)
    eth_0513 = EXPECTED_PER_LABEL[
        "ETHUSD_20260513_editv1exp_setup01_touch2"]
    avax_0529 = EXPECTED_PER_LABEL[
        "AVAXUSD_20260529_editv1exp_setup04_touch2"]
    eth_bps = m2.implied_risk_distance_bps(eth_0513[2], eth_0513[3])
    avax_bps = m2.implied_risk_distance_bps(avax_0529[2], avax_0529[3])
    assert eth_bps is not None and eth_bps < 3  # ~2.6 bps
    assert avax_bps is not None and avax_bps < 5  # ~4.5 bps
    assert eth_bps < m2.MINIMUM_RISK_DISTANCE_BPS
    assert avax_bps < m2.MINIMUM_RISK_DISTANCE_BPS
    # EVERY completed V1 replay was below the 81 bps floor
    for setup_id, (status, _exit, gross, net) in EXPECTED_PER_LABEL.items():
        if status == "REPLAY_READY_FOR_LOCKED_SCORER_REVIEW":
            implied = m2.implied_risk_distance_bps(gross, net)
            assert implied is not None and implied < 81, setup_id
            synthetic = m2.evaluate_setup_cost_viability(
                100.0, 100.0 - implied / 100.0)
            assert synthetic["viable"] is False, setup_id


def test_2x_and_4x_variants_noted_only_not_active():
    assert m2.FUTURE_RESEARCH_VARIANTS_NOTED_ONLY == {
        "softer_2x_round_trip": 54, "harder_4x_round_trip": 108}
    parameters = m2.build_edited_candidate_asset_v2()["fields"]["parameters"]
    assert parameters["minimum_risk_distance_bps"] == 81
    assert 54 not in (parameters["minimum_risk_distance_bps"],)
    assert 108 not in (parameters["minimum_risk_distance_bps"],)
    record = m2.build_mutable_candidate_edit_v2()
    assert record["future_research_variants_noted_only"] == {
        "softer_2x_round_trip": 54, "harder_4x_round_trip": 108}
    tampered = m2.build_mutable_candidate_edit_v2()
    tampered["edited_asset"]["fields"]["parameters"][
        "minimum_risk_distance_bps"] = 54
    assert m2.validate_mutable_candidate_edit_v2(tampered)["valid"] is False


def test_based_on_frozen_replay_evidence():
    record = m2.build_mutable_candidate_edit_v2()
    assert record["based_on_replay_evidence"] == {
        "net_r_after_costs": -21.040902,
        "round_trip_cost_bps": 27.0,
        "labels_replayed": 7}
    tampered = m2.build_mutable_candidate_edit_v2()
    tampered["based_on_replay_evidence"] = {"net_r_after_costs": 10.0}
    assert m2.validate_mutable_candidate_edit_v2(tampered)["valid"] is False


def test_no_credential_order_access_and_asset_screen_holds():
    record = m2.build_mutable_candidate_edit_v2()
    for key in ("fetches_data", "calls_api", "uses_network",
                "uses_credentials", "uses_wallet", "connects_broker",
                "connects_exchange", "contains_order_logic"):
        assert record[key] is False, key
    from sparta_commander.crypto_d1_auto_research_mutable_candidate_asset_spec import (
        validate_candidate_asset)
    smuggled = m2.build_edited_candidate_asset_v2()
    smuggled["fields"] = dict(smuggled["fields"], api_key_env="X")
    assert validate_candidate_asset(smuggled)["verdict"] == (
        "CANDIDATE_ASSET_REJECTED")
    smuggled2 = m2.build_edited_candidate_asset_v2()
    smuggled2["fields"] = dict(smuggled2["fields"], order_endpoint="X")
    assert validate_candidate_asset(smuggled2)["verdict"] == (
        "CANDIDATE_ASSET_REJECTED")


def test_no_detector_or_replay_run_and_no_mutation():
    record = m2.build_mutable_candidate_edit_v2()
    assert record["runs_detector_now"] is False
    assert record["runs_replay_now"] is False
    assert record["redetection_not_run_here"] is True
    assert record["modifies_staged_candles"] is False
    assert record["modifies_previous_labels"] is False
    src = open(m2.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    assert "detector_run_once" not in src
    assert "redetection_run_once" not in src
    assert "replay_7_accepted_once" not in src
    assert "automatic_redetection" in m2.FORBIDDEN
    assert "replay_runs" in m2.FORBIDDEN


def test_human_approval_required_before_v2_redetection_or_replay():
    record = m2.build_mutable_candidate_edit_v2()
    assert record["redetection_requires_separate_human_approval"] is True
    assert record["replay_requires_separate_human_approval"] is True
    assert record["next_required_action"] == (
        "HUMAN_APPROVED_REDETECTION_WITH_COST_VIABILITY_EDIT_V2")
    tampered = m2.build_mutable_candidate_edit_v2()
    tampered["redetection_requires_separate_human_approval"] = False
    assert m2.validate_mutable_candidate_edit_v2(tampered)["valid"] is False
    tampered2 = m2.build_mutable_candidate_edit_v2()
    tampered2["live_gate_locked"] = False
    assert m2.validate_mutable_candidate_edit_v2(tampered2)["valid"] is False


def test_validator_strict_and_deterministic():
    assert (m2.build_mutable_candidate_edit_v2()
            == m2.build_mutable_candidate_edit_v2())
    tampered = m2.build_mutable_candidate_edit_v2()
    tampered["v2_new_parameters"] = dict(tampered["v2_new_parameters"],
                                         minimum_risk_distance_bps=1)
    assert m2.validate_mutable_candidate_edit_v2(tampered)["valid"] is False
    tampered2 = m2.build_mutable_candidate_edit_v2()
    tampered2["forbidden"] = tampered2["forbidden"][:3]
    assert m2.validate_mutable_candidate_edit_v2(tampered2)["valid"] is False
    tampered3 = m2.build_mutable_candidate_edit_v2()
    tampered3["edited_asset"]["fields"]["parameters"][
        "max_fvg_age_bars"] = 999
    assert m2.validate_mutable_candidate_edit_v2(tampered3)["valid"] is False


def test_upstream_stack_and_pm_lane_untouched():
    import sparta_commander.ny_session_fvg_choch_fee_honest_replay_results_review_contract as rr
    assert rr.EXPECTED_TOTAL_NET_R == -21.040902
    import sparta_commander.ny_session_fvg_choch_accepted_labels_human_review_contract as al
    assert len(al.FROZEN_ACCEPTED_SETUP_IDS) == 7
    import sparta_commander.ny_session_fvg_choch_mutable_candidate_edit_v1 as me
    assert me.build_mutable_candidate_edit_v1()["verdict"] == (
        "NY_FVG_CHOCH_MUTABLE_CANDIDATE_EDIT_V1_READY")
    import sparta_commander.ny_session_fvg_choch_additional_session_days_staged_candles_review as ad
    assert len(ad.BASELINE_PROTECTED_FILES) == 5
    from sparta_commander.strategy_factory_mission_flow_status import (
        LATEST_COMPLETED_PM_LANE_CHAIN)
    assert "Research Only" in LATEST_COMPLETED_PM_LANE_CHAIN


def test_label_action_and_imports_clean():
    assert m2.get_mutable_candidate_edit_v2_label() == m2.M2_LABEL
    assert "READ-ONLY" in m2.M2_LABEL and m2.M2_MODE == "RESEARCH_ONLY"
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in m2.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(m2.__file__, encoding="utf-8").read()
    assert "while true" not in src.lower() and "sleep(" not in src.lower()
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
                   "subprocess", "websockets", "aiohttp", "schedule",
                   "apscheduler", "threading", "asyncio", "time", "telegram",
                   "email", "csv", "pandas", "pathlib", "os", "io", "json",
                   "shutil", "databento", "ssl", "ftplib", "datetime",
                   "hashlib"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
    assert not any(call.func.attr == "open" if isinstance(call.func, ast.Attribute)
                   else getattr(call.func, "id", "") == "open"
                   for call in ast.walk(tree) if isinstance(call, ast.Call))