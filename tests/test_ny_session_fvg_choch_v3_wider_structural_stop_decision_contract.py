"""Tests for the SPARTA NY FVG+CHOCH V3 Wider Structural Stop Decision.

Proves the V3 decision is gated on the frozen V2 rejection evidence, scoped
to exactly one stop-geometry experiment, preserves V1/V2 controls and the
81 bps cost floor, never assumes maker execution, keeps the locked scorer
and instructions immutable, runs nothing, and records the failure rule:
fail again and the candidate is rejected, kept on record.
"""

from __future__ import annotations

import ast
import os.path

import pytest

import sparta_commander.ny_session_fvg_choch_v3_wider_structural_stop_decision_contract as v3


def _observation(**overrides):
    observation = {
        "v2_review_verdict": "V2_COST_VIABILITY_REJECTED_ALL_LABELS",
        "v2_artifact_sha256": v3.V2_ARTIFACT_SHA256,
        "tracked_output_paths": [],
    }
    observation.update(overrides)
    return observation


def test_valid_decision_records_one_experiment():
    record = v3.certify_v3_decision(_observation())
    assert record["verdict"] == v3.VERDICT_V3D_RECORDED
    assert record["blockers"] == []
    assert record["decision_is_one_experiment_only"] is True
    assert record["rejection_not_marked_final"] is True
    assert all(record["checklist_results"][n] is True
               for n in v3.REVIEW_CHECKLIST)
    assert len(v3.REVIEW_CHECKLIST) == 10
    assert v3.validate_v3_decision(record)["valid"] is True


def test_real_v2_evidence_gates_decision_when_present():
    if not os.path.isfile("C:/SPARTA_BRAIN/" + v3.V2_ARTIFACT_PATH):
        pytest.skip("real V2 artifact absent on this machine")
    record = v3.build_v3_decision("C:/SPARTA_BRAIN", tracked_paths=[])
    assert record["verdict"] == v3.VERDICT_V3D_RECORDED
    assert v3.validate_v3_decision(record)["valid"] is True


def test_v2_evidence_required_before_v3_decision():
    missing = v3.certify_v3_decision(_observation(v2_artifact_sha256=None))
    assert missing["verdict"] == v3.VERDICT_V3D_BLOCKED
    assert "v2_evidence_missing" in missing["blockers"]
    assert v3.certify_v3_decision(None)["verdict"] == v3.VERDICT_V3D_BLOCKED


def test_tampered_v2_evidence_rejects():
    tampered_sha = v3.certify_v3_decision(_observation(
        v2_artifact_sha256="0" * 64))
    assert tampered_sha["verdict"] == v3.VERDICT_V3D_REJECTED
    assert ("check_failed:v2_artifact_sha_pinned_and_untampered"
            in tampered_sha["blockers"])
    wrong_verdict = v3.certify_v3_decision(_observation(
        v2_review_verdict="V2_RESULT_REVIEW_REJECTED"))
    assert wrong_verdict["verdict"] == v3.VERDICT_V3D_REJECTED
    assert ("check_failed:v2_rejection_evidence_certified_before_v3_decision"
            in wrong_verdict["blockers"])


def test_v3_changes_stop_geometry_only():
    record = v3.certify_v3_decision(_observation())
    assert record["checklist_results"]["v3_changes_stop_geometry_only"] is True
    assert "v3_may_change_stop_geometry_only" in v3.V3_CONSTRAINTS
    model = v3.V3_PROPOSED_STOP_MODEL
    assert ("replace_stop_outside_the_1m_fvg_impulse_candle_with_stop_beyond"
            "_the_choch_leg_structural_extreme" in model)
    assert ("long_setups_stop_below_the_choch_leg_low_structural_swing_low"
            in model)
    assert ("short_setups_stop_above_the_choch_leg_high_structural_swing"
            "_high" in model)
    assert "cost_viability_floor_applies_to_v3_setups_unchanged" in model
    # the stop model must not touch scorer, costs, or live capability
    for rule in model:
        for token in ("scorer", "instruction", "live", "paper", "maker",
                      "lower_cost"):
            assert token not in rule, rule
    tampered = v3.certify_v3_decision(_observation())
    tampered["v3_proposed_stop_model"] = ["also_lower_the_cost_floor"]
    assert v3.validate_v3_decision(tampered)["valid"] is False


def test_v1_and_v2_controls_preserved():
    record = v3.certify_v3_decision(_observation())
    assert record["preserved_v1_controls"] == {
        "max_fvg_age_bars": 24,
        "require_fresh_unmitigated_15m_fvg": True,
        "max_zone_touches_before_invalidation": 2}
    assert record["preserved_v2_cost_filter"]["round_trip_cost_bps"] == 27
    assert record["preserved_v2_cost_filter"][
        "minimum_risk_to_round_trip_cost_multiple"] == 3
    assert record["preserved_v2_cost_filter"][
        "minimum_risk_distance_bps"] == 81
    assert record["preserved_v2_cost_filter"][
        "reject_cost_dominated_setups"] is True
    # values match the PUSHED edit modules exactly (no ad-hoc copies)
    from sparta_commander.ny_session_fvg_choch_mutable_candidate_edit_v1 import (
        NEW_PARAMETERS)
    from sparta_commander.ny_session_fvg_choch_mutable_candidate_edit_v2_cost_viability import (
        V2_NEW_PARAMETERS)
    assert record["preserved_v1_controls"] == NEW_PARAMETERS
    assert record["preserved_v2_cost_filter"] == V2_NEW_PARAMETERS
    tampered = v3.certify_v3_decision(_observation())
    tampered["preserved_v2_cost_filter"] = dict(
        tampered["preserved_v2_cost_filter"], minimum_risk_distance_bps=10)
    assert v3.validate_v3_decision(tampered)["valid"] is False


def test_cost_floor_never_lowered_and_maker_not_assumed():
    record = v3.certify_v3_decision(_observation())
    assert record["cost_floor_lowered"] is False
    assert record["maker_execution_assumed"] is False
    assert "the_cost_floor_is_never_lowered_to_rescue_the_strategy" in (
        v3.V3_CONSTRAINTS)
    assert "maker_execution_is_not_assumed" in v3.V3_CONSTRAINTS
    assert "lowering_costs_to_rescue_the_strategy" in v3.FORBIDDEN
    tampered = v3.certify_v3_decision(_observation())
    tampered["cost_floor_lowered"] = True
    assert v3.validate_v3_decision(tampered)["valid"] is False
    tampered2 = v3.certify_v3_decision(_observation())
    tampered2["maker_execution_assumed"] = True
    assert v3.validate_v3_decision(tampered2)["valid"] is False


def test_locked_scorer_and_instructions_immutable():
    from sparta_commander.crypto_d1_auto_research_strategy_optimizer_contract import (
        FORBIDDEN_FOREVER, LOCKED_HUMAN_INSTRUCTIONS, LOCKED_SCORING_RULES)
    assert len(LOCKED_HUMAN_INSTRUCTIONS) == 7
    assert len(LOCKED_SCORING_RULES) == 9
    assert len(FORBIDDEN_FOREVER) == 12
    record = v3.certify_v3_decision(_observation())
    assert record["modifies_locked_scorer"] is False
    assert record["modifies_locked_instructions"] is False
    assert ("locked_scorer_and_locked_instructions_remain_immutable"
            in v3.V3_CONSTRAINTS)


def test_failure_rule_recorded():
    record = v3.certify_v3_decision(_observation())
    assert record["failure_rule"] == (
        "if V3 also fails cost viability or fee-honest replay, the "
        "candidate is rejected and kept on record")
    assert record["rejection_not_marked_final"] is True
    tampered = v3.certify_v3_decision(_observation())
    tampered["failure_rule"] = "keep trying forever"
    assert v3.validate_v3_decision(tampered)["valid"] is False
    tampered2 = v3.certify_v3_decision(_observation())
    tampered2["rejection_not_marked_final"] = False
    assert v3.validate_v3_decision(tampered2)["valid"] is False


def test_allowed_next_step_and_forbidden_list():
    record = v3.certify_v3_decision(_observation())
    assert record["allowed_next_step"] == (
        "HUMAN_APPROVED_V3_WIDER_STRUCTURAL_STOP_MUTABLE_CANDIDATE_EDIT")
    assert record["next_required_action"] == record["allowed_next_step"]
    for item in ("live_trading", "paper_trading", "order_placement",
                 "broker_exchange_private_api_access",
                 "credentials_api_keys_login_account_wallet",
                 "replay_scorer_or_optimizer_runs_in_this_block",
                 "lowering_costs_to_rescue_the_strategy",
                 "deleting_v2_evidence", "hiding_rejected_setups",
                 "auto_promotion", "gate_unlocks"):
        assert item in v3.FORBIDDEN, item
    tampered = v3.certify_v3_decision(_observation())
    tampered["forbidden"] = tampered["forbidden"][:3]
    assert v3.validate_v3_decision(tampered)["valid"] is False


def test_nothing_runs_and_gates_locked():
    record = v3.certify_v3_decision(_observation())
    for key in ("executes", "writes_files", "writes_reports",
                "modifies_labels", "deletes_labels", "modifies_staged_files",
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
    tracked = v3.certify_v3_decision(_observation(
        tracked_output_paths=["data/ny_fvg_choch/x"]))
    assert tracked["verdict"] == v3.VERDICT_V3D_REJECTED
    tampered = v3.certify_v3_decision(_observation())
    tampered["live_gate_locked"] = False
    assert v3.validate_v3_decision(tampered)["valid"] is False
    assert (v3.certify_v3_decision(_observation())
            == v3.certify_v3_decision(_observation()))


def test_upstream_stack_and_pm_lane_untouched():
    import sparta_commander.ny_session_fvg_choch_v2_cost_viability_result_review_contract as v2r
    assert v2r.EXPECTED_SURVIVING == 0
    assert max(v2r.EXPECTED_RISK_DISTANCES_BPS.values()) == 33.15758
    import sparta_commander.ny_session_fvg_choch_fee_honest_replay_results_review_contract as rr
    assert rr.EXPECTED_TOTAL_NET_R == -21.040902
    import sparta_commander.ny_session_fvg_choch_additional_session_days_staged_candles_review as ad
    assert len(ad.BASELINE_PROTECTED_FILES) == 5
    from sparta_commander.ny_session_fvg_choch_strategy_spec_contract import (
        FIB_LEVEL, RISK_REWARD_TARGET)
    assert FIB_LEVEL == 0.618 and RISK_REWARD_TARGET == 4.0
    from sparta_commander.strategy_factory_mission_flow_status import (
        LATEST_COMPLETED_PM_LANE_CHAIN)
    assert "Research Only" in LATEST_COMPLETED_PM_LANE_CHAIN


def test_label_action_read_only_and_imports_clean():
    assert v3.get_v3_decision_label() == v3.V3D_LABEL
    assert "READ-ONLY" in v3.V3D_LABEL and v3.V3D_MODE == "RESEARCH_ONLY"
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in v3.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(v3.__file__, encoding="utf-8").read()
    assert "__main__" not in src
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
                   "email", "csv", "pandas", "os", "io", "json", "shutil",
                   "databento", "ssl", "ftplib", "datetime"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
    assert not any(call.func.attr == "open" if isinstance(call.func, ast.Attribute)
                   else getattr(call.func, "id", "") == "open"
                   for call in ast.walk(tree) if isinstance(call, ast.Call))