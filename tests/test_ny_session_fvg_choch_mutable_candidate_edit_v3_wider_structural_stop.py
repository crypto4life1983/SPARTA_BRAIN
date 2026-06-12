"""Tests for the SPARTA NY FVG+CHOCH Mutable Candidate Edit V3 - Wider
Structural Stop.

Proves V3 changes ONLY the stop geometry (impulse-candle -> CHOCH leg
structural extreme), is blocked without the recorded V3 decision, preserves
V1/V2 controls and the 81 bps floor, never assumes maker execution, keeps
locked scorer/instructions immutable, runs nothing, and keeps all gates
LOCKED.
"""

from __future__ import annotations

import ast
import os.path

import pytest

import sparta_commander.ny_session_fvg_choch_mutable_candidate_edit_v3_wider_structural_stop as m3
from sparta_commander.ny_session_fvg_choch_mutable_candidate_edit_v2_cost_viability import (
    build_edited_candidate_asset_v2,
)

_RECORDED = "V3_DECISION_RECORDED_PROCEED_WITH_ONE_WIDER_STOP_EXPERIMENT"


def test_v3_edit_ready_when_decision_recorded():
    record = m3.record_mutable_candidate_edit_v3(_RECORDED)
    assert record["verdict"] == m3.VERDICT_M3_READY
    assert record["blockers"] == []
    assert record["edited_asset_verdict"] == (
        "CANDIDATE_ASSET_ACCEPTED_FOR_RESEARCH")
    assert record["candidate_id"] == (
        "NY_SESSION_FVG_CHOCH_STRATEGY_CANDIDATE_V1")
    assert record["candidate_family"] == "intraday_fvg_choch"
    assert m3.validate_mutable_candidate_edit_v3(record)["valid"] is True


def test_v3_edit_blocked_without_recorded_decision():
    for bad in (None, "V3_DECISION_REJECTED", "V3_DECISION_BLOCKED",
                "anything_else"):
        record = m3.record_mutable_candidate_edit_v3(bad)
        assert record["verdict"] == m3.VERDICT_M3_BLOCKED, bad
        assert "v3_decision_not_recorded" in record["blockers"]
        assert record["edited_asset"] is None


def test_real_repo_build_gates_on_live_v3_decision():
    if not os.path.isfile("C:/SPARTA_BRAIN/data/ny_fvg_choch/"
                          "detector_labels/v2_cost_viability_eligibility"
                          "_2026-05-12_2026-06-10.json"):
        pytest.skip("real V2 evidence absent on this machine")
    record = m3.build_mutable_candidate_edit_v3("C:/SPARTA_BRAIN")
    assert record["verdict"] == m3.VERDICT_M3_READY
    assert m3.validate_mutable_candidate_edit_v3(record)["valid"] is True


def test_only_stop_geometry_changes():
    v2 = build_edited_candidate_asset_v2()
    v3 = m3.build_edited_candidate_asset_v3()
    # V2 builder output is NOT mutated by V3
    assert "stop_geometry" not in v2["fields"]["parameters"]
    # outer research flags identical
    for key in ("research_only", "live_trading_authorized",
                "paper_trading_authorized", "human_review_required",
                "optimizer_may_edit", "locked_instructions_may_edit",
                "locked_scorer_may_edit"):
        assert v3[key] == v2[key], key
    changed = {name for name in v2["fields"]
               if v3["fields"][name] != v2["fields"][name]}
    assert changed == {"parameters", "risk_rules_text", "constraints",
                       "lineage", "audit_notes", "rationale"}
    # entry/exit/HTF logic untouched
    assert v3["fields"]["entry_rules_text"] == v2["fields"]["entry_rules_text"]
    assert v3["fields"]["exit_rules_text"] == v2["fields"]["exit_rules_text"]
    assert v3["fields"]["session_filter"] == v2["fields"]["session_filter"]
    assert v3["fields"]["risk_rules_text"] == m3.V3_STOP_RULE_TEXT
    assert "choch_leg_structural_swing_low" in str(
        v3["fields"]["parameters"]["stop_rule_long"])
    assert "choch_leg_structural_swing_high" in str(
        v3["fields"]["parameters"]["stop_rule_short"])
    assert v3["fields"]["parameters"][
        "risk_unit_recomputed_from_entry_to_structural_stop"] is True
    assert v3["fields"]["status"] == "proposed"


def test_v1_controls_preserved():
    parameters = m3.build_edited_candidate_asset_v3()["fields"]["parameters"]
    assert parameters["max_fvg_age_bars"] == 24
    assert parameters["require_fresh_unmitigated_15m_fvg"] is True
    assert parameters["max_zone_touches_before_invalidation"] == 2
    record = m3.record_mutable_candidate_edit_v3(_RECORDED)
    assert ("v1_freshness_controls_unchanged_24_true_2"
            in record["unchanged_guarantees"])
    tampered = m3.record_mutable_candidate_edit_v3(_RECORDED)
    tampered["edited_asset"]["fields"]["parameters"]["max_fvg_age_bars"] = 99
    assert m3.validate_mutable_candidate_edit_v3(tampered)["valid"] is False


def test_v2_cost_floor_preserved_and_not_bypassable():
    parameters = m3.build_edited_candidate_asset_v3()["fields"]["parameters"]
    assert parameters["round_trip_cost_bps"] == 27
    assert parameters["minimum_risk_to_round_trip_cost_multiple"] == 3
    assert parameters["minimum_risk_distance_bps"] == 81
    assert parameters["reject_cost_dominated_setups"] is True
    assert parameters["accepted_labels_must_pass_81bps_floor"] is True
    record = m3.record_mutable_candidate_edit_v3(_RECORDED)
    assert record["accepted_labels_may_bypass_floor"] is False
    tampered = m3.record_mutable_candidate_edit_v3(_RECORDED)
    tampered["edited_asset"]["fields"]["parameters"][
        "minimum_risk_distance_bps"] = 10
    assert m3.validate_mutable_candidate_edit_v3(tampered)["valid"] is False
    tampered2 = m3.record_mutable_candidate_edit_v3(_RECORDED)
    tampered2["accepted_labels_may_bypass_floor"] = True
    assert m3.validate_mutable_candidate_edit_v3(tampered2)["valid"] is False


def test_maker_not_assumed_and_cost_floor_not_lowered():
    record = m3.record_mutable_candidate_edit_v3(_RECORDED)
    assert record["maker_execution_assumed"] is False
    assert record["cost_floor_lowered"] is False
    assert "assuming_maker_execution" in m3.FORBIDDEN
    assert "lowering_costs" in m3.FORBIDDEN
    tampered = m3.record_mutable_candidate_edit_v3(_RECORDED)
    tampered["maker_execution_assumed"] = True
    assert m3.validate_mutable_candidate_edit_v3(tampered)["valid"] is False
    tampered2 = m3.record_mutable_candidate_edit_v3(_RECORDED)
    tampered2["cost_floor_lowered"] = True
    assert m3.validate_mutable_candidate_edit_v3(tampered2)["valid"] is False


def test_locked_scorer_and_instructions_immutable():
    from sparta_commander.crypto_d1_auto_research_strategy_optimizer_contract import (
        FORBIDDEN_FOREVER, LOCKED_HUMAN_INSTRUCTIONS, LOCKED_SCORING_RULES)
    assert len(LOCKED_HUMAN_INSTRUCTIONS) == 7
    assert len(LOCKED_SCORING_RULES) == 9
    assert len(FORBIDDEN_FOREVER) == 12
    record = m3.record_mutable_candidate_edit_v3(_RECORDED)
    assert record["modifies_locked_scorer"] is False
    assert record["modifies_locked_instructions"] is False
    edited = m3.build_edited_candidate_asset_v3()
    assert edited["locked_scorer_may_edit"] is False
    assert edited["locked_instructions_may_edit"] is False
    # detection logic text untouched in the strategy spec
    from sparta_commander.ny_session_fvg_choch_strategy_spec_contract import (
        DETERMINISTIC_RULES, FIB_LEVEL, FIB_TOLERANCE, RISK_REWARD_TARGET)
    assert FIB_LEVEL == 0.618 and FIB_TOLERANCE == 0.05
    assert RISK_REWARD_TARGET == 4.0
    assert "trigger_1m_bullish_choch" in DETERMINISTIC_RULES


def test_live_paper_order_api_credential_fields_reject():
    edited = m3.build_edited_candidate_asset_v3()
    assert edited["research_only"] is True
    assert edited["live_trading_authorized"] is False
    assert edited["paper_trading_authorized"] is False
    from sparta_commander.crypto_d1_auto_research_mutable_candidate_asset_spec import (
        validate_candidate_asset)
    for bad in ("api_key_env", "order_endpoint", "wallet_address",
                "broker_account", "login_token"):
        smuggled = m3.build_edited_candidate_asset_v3()
        smuggled["fields"] = dict(smuggled["fields"], **{bad: "x"})
        assert validate_candidate_asset(smuggled)["verdict"] == (
            "CANDIDATE_ASSET_REJECTED"), bad
    flipped = m3.build_edited_candidate_asset_v3()
    flipped["live_trading_authorized"] = True
    assert validate_candidate_asset(flipped)["verdict"] == (
        "CANDIDATE_ASSET_REJECTED")


def test_nothing_runs_and_artifacts_untouched():
    record = m3.record_mutable_candidate_edit_v3(_RECORDED)
    for key in ("executes", "writes_files", "writes_reports",
                "runs_detector_now", "runs_replay_now", "scores_now",
                "fetches_data", "calls_api", "uses_network",
                "uses_credentials", "uses_wallet", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate"):
        assert record[key] is False, key
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True
    assert record["modifies_staged_candles"] is False
    assert record["modifies_previous_labels"] is False
    assert record["previous_evidence_kept_on_record"] is True
    src = open(m3.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    # never imports the run tools (the words may appear in prose only)
    for tool in ("detector_run_once", "redetection_run_once",
                 "redetection_expanded_sample_once",
                 "redetection_v2_cost_viability_once",
                 "replay_7_accepted_once"):
        assert tool not in src, tool
    tampered = m3.record_mutable_candidate_edit_v3(_RECORDED)
    tampered["live_gate_locked"] = False
    assert m3.validate_mutable_candidate_edit_v3(tampered)["valid"] is False
    tampered2 = m3.record_mutable_candidate_edit_v3(_RECORDED)
    tampered2["forbidden"] = tampered2["forbidden"][:3]
    assert m3.validate_mutable_candidate_edit_v3(tampered2)["valid"] is False


def test_one_experiment_and_human_gates():
    record = m3.record_mutable_candidate_edit_v3(_RECORDED)
    assert record["one_experiment_only"] is True
    assert record["redetection_requires_separate_human_approval"] is True
    assert record["replay_requires_separate_human_approval"] is True
    assert record["next_required_action"] == (
        "HUMAN_APPROVED_V3_REDETECTION_ON_EXPANDED_SAMPLE")
    tampered = m3.record_mutable_candidate_edit_v3(_RECORDED)
    tampered["redetection_requires_separate_human_approval"] = False
    assert m3.validate_mutable_candidate_edit_v3(tampered)["valid"] is False


def test_deterministic_and_validator_strict():
    assert (m3.record_mutable_candidate_edit_v3(_RECORDED)
            == m3.record_mutable_candidate_edit_v3(_RECORDED))
    tampered = m3.record_mutable_candidate_edit_v3(_RECORDED)
    tampered["v3_new_parameters"] = dict(tampered["v3_new_parameters"],
                                         stop_geometry="back_to_impulse")
    assert m3.validate_mutable_candidate_edit_v3(tampered)["valid"] is False
    tampered2 = m3.record_mutable_candidate_edit_v3(_RECORDED)
    tampered2["v3_stop_rule_text"] = "whatever stop"
    assert m3.validate_mutable_candidate_edit_v3(tampered2)["valid"] is False
    tampered3 = m3.record_mutable_candidate_edit_v3(_RECORDED)
    tampered3["edited_asset"]["fields"]["risk_rules_text"] = "old stop rule"
    assert m3.validate_mutable_candidate_edit_v3(tampered3)["valid"] is False


def test_upstream_stack_and_pm_lane_untouched():
    import sparta_commander.ny_session_fvg_choch_v3_wider_structural_stop_decision_contract as v3d
    assert v3d.VERDICT_V3D_RECORDED == _RECORDED
    import sparta_commander.ny_session_fvg_choch_v2_cost_viability_result_review_contract as v2r
    assert v2r.EXPECTED_SURVIVING == 0
    import sparta_commander.ny_session_fvg_choch_fee_honest_replay_results_review_contract as rr
    assert rr.EXPECTED_TOTAL_NET_R == -21.040902
    import sparta_commander.ny_session_fvg_choch_additional_session_days_staged_candles_review as ad
    assert len(ad.BASELINE_PROTECTED_FILES) == 5
    from sparta_commander.strategy_factory_mission_flow_status import (
        LATEST_COMPLETED_PM_LANE_CHAIN)
    assert "Research Only" in LATEST_COMPLETED_PM_LANE_CHAIN


def test_label_action_and_imports_clean():
    assert m3.get_mutable_candidate_edit_v3_label() == m3.M3_LABEL
    assert "READ-ONLY" in m3.M3_LABEL and m3.M3_MODE == "RESEARCH_ONLY"
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in m3.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(m3.__file__, encoding="utf-8").read()
    assert "while true" not in src.lower() and "sleep(" not in src.lower()
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch("):
        assert verb not in src, verb
    tree = ast.parse(src)
    sparta_imports = {node.module for node in ast.walk(tree)
                      if isinstance(node, ast.ImportFrom) and node.module
                      and node.module.startswith("sparta_commander")}
    for module in sparta_imports:
        for fragment in ("replay_runner", "replay_spec", "optimizer"):
            assert fragment not in module, module
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