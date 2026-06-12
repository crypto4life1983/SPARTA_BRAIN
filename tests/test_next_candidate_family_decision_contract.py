"""Tests for the SPARTA Next Candidate Family Decision contract.

Proves the next-family decision requires the intact rejection record of
candidate #1, selects a family genuinely different from the rejected 1m
FVG/CHOCH scalp geometry, keeps the 81 bps floor and fee-honest discipline,
never assumes maker execution, builds nothing, and keeps all gates LOCKED.
"""

from __future__ import annotations

import ast
import os.path

import pytest

import sparta_commander.next_candidate_family_decision_contract as nf


def _observation(**overrides):
    observation = {
        "rejection_record_verdict":
            "V3_RESULT_FROZEN_AND_CANDIDATE_REJECTED_KEPT_ON_RECORD",
        "v3_artifact_sha256": nf.EXPECTED_V3_ARTIFACT_SHA256,
        "tracked_output_paths": [],
    }
    observation.update(overrides)
    return observation


def test_valid_decision_records_next_family():
    record = nf.certify_next_family_decision(_observation())
    assert record["verdict"] == nf.VERDICT_NF_RECORDED
    assert record["blockers"] == []
    assert record["next_family_id"] == (
        "CRYPTO_INTRADAY_BREAKOUT_PULLBACK_STRUCTURE_V1")
    assert record["next_family_name"] == (
        "intraday_breakout_pullback_structure")
    assert all(record["checklist_results"][n] is True
               for n in nf.REVIEW_CHECKLIST)
    assert len(nf.REVIEW_CHECKLIST) == 8
    assert nf.validate_next_family_decision(record)["valid"] is True


def test_real_rejection_evidence_gates_decision_when_present():
    if not os.path.isfile("C:/SPARTA_BRAIN/" + nf.V3_ARTIFACT_PATH):
        pytest.skip("real rejection evidence absent on this machine")
    record = nf.build_next_family_decision("C:/SPARTA_BRAIN",
                                           tracked_paths=[])
    assert record["verdict"] == nf.VERDICT_NF_RECORDED
    assert nf.validate_next_family_decision(record)["valid"] is True


def test_rejection_evidence_required_and_intact():
    missing = nf.certify_next_family_decision(_observation(
        v3_artifact_sha256=None))
    assert missing["verdict"] == nf.VERDICT_NF_BLOCKED
    assert "rejection_evidence_missing" in missing["blockers"]
    tampered = nf.certify_next_family_decision(_observation(
        v3_artifact_sha256="0" * 64))
    assert tampered["verdict"] == nf.VERDICT_NF_REJECTED
    assert ("check_failed:rejection_evidence_artifact_sha_pinned"
            in tampered["blockers"])
    wrong_verdict = nf.certify_next_family_decision(_observation(
        rejection_record_verdict="REJECTION_RECORD_REVIEW_REJECTED"))
    assert wrong_verdict["verdict"] == nf.VERDICT_NF_REJECTED
    assert ("check_failed:rejection_record_certified_and_intact"
            in wrong_verdict["blockers"])
    assert nf.certify_next_family_decision(None)["verdict"] == (
        nf.VERDICT_NF_BLOCKED)


def test_next_family_differs_from_rejected_scalp_geometry():
    record = nf.certify_next_family_decision(_observation())
    assert record["checklist_results"][
        "next_family_differs_from_rejected_scalp_geometry"] is True
    assert nf.NEXT_FAMILY_ID != "NY_SESSION_FVG_CHOCH_STRATEGY_CANDIDATE_V1"
    assert nf.NEXT_FAMILY_NAME != "intraday_fvg_choch"
    assert "fvg_choch" not in nf.NEXT_FAMILY_NAME
    assert ("use_15m_and_1h_context_instead_of_1m_scalp_geometry"
            in nf.CANDIDATE_CONCEPT)
    summary = record["rejected_evidence_summary"]
    assert summary["rejected_candidate_id"] == (
        "NY_SESSION_FVG_CHOCH_STRATEGY_CANDIDATE_V1")
    assert summary["rejection_status"] == "REJECTED_KEPT_ON_RECORD"
    assert summary["rejection_reason"] == "COST_NON_VIABLE_RISK_GEOMETRY"
    assert summary["v1v2_max_risk_bps"] == 33.15758
    assert summary["v3_max_risk_bps"] == 39.680383
    assert summary["floor_bps"] == 81
    assert summary["cost_viable_survivors"] == 0
    assert summary["fee_honest_replay_net_r"] == -21.040902
    tampered = nf.certify_next_family_decision(_observation())
    tampered["next_family_id"] = "NY_SESSION_FVG_CHOCH_STRATEGY_CANDIDATE_V1"
    assert nf.validate_next_family_decision(tampered)["valid"] is False
    tampered2 = nf.certify_next_family_decision(_observation())
    tampered2["rejected_evidence_summary"] = {}
    assert nf.validate_next_family_decision(tampered2)["valid"] is False


def test_concept_and_rationale_frozen():
    record = nf.certify_next_family_decision(_observation())
    for item in ("look_for_directional_momentum_expansion_or_range_breakout",
                 "wait_for_pullback_or_retest_into_structure",
                 "enter_only_if_continuation_confirms",
                 "stop_at_structural_swing_or_atr_based_invalidation",
                 "require_minimum_risk_distance_gte_81_bps_before_replay"
                 "_eligibility",
                 "preserve_fee_honest_cost_discipline_27bps_taker_round"
                 "_trip"):
        assert item in record["candidate_concept"], item
    for item in ("wider_stop_geometry_is_more_likely_to_survive_27bps_taker"
                 "_execution",
                 "avoids_sub_40_bps_1m_impulse_candle_risk_units",
                 "still_deterministic_and_testable",
                 "suitable_for_staged_historical_candle_replay",
                 "compatible_with_the_existing_auto_research_machinery"):
        assert item in record["preference_rationale"], item
    tampered = nf.certify_next_family_decision(_observation())
    tampered["candidate_concept"] = ["whatever"]
    assert nf.validate_next_family_decision(tampered)["valid"] is False
    tampered2 = nf.certify_next_family_decision(_observation())
    tampered2["preference_rationale"] = ["it_feels_good"]
    assert nf.validate_next_family_decision(tampered2)["valid"] is False


def test_no_maker_assumption_or_cost_lowering_allowed():
    record = nf.certify_next_family_decision(_observation())
    assert record["maker_execution_assumed"] is False
    assert record["cost_floor_lowered"] is False
    assert "assuming_maker_execution" in nf.FORBIDDEN
    assert "lowering_the_81_bps_cost_floor" in nf.FORBIDDEN
    for flag in ("maker_execution_assumed", "cost_floor_lowered",
                 "rejected_candidate_revived", "strategy_spec_built_here"):
        tampered = nf.certify_next_family_decision(_observation())
        tampered[flag] = True
        assert nf.validate_next_family_decision(tampered)["valid"] is False, flag


def test_rejected_candidate_never_revived_and_evidence_preserved():
    record = nf.certify_next_family_decision(_observation())
    assert record["rejected_candidate_revived"] is False
    assert record["rejected_evidence_kept_on_record"] is True
    assert ("reviving_the_rejected_fvg_choch_candidate_without_a_new_family"
            "_or_separate_lower_cost_lane" in nf.FORBIDDEN)
    assert "deleting_or_hiding_rejected_evidence" in nf.FORBIDDEN
    tampered = nf.certify_next_family_decision(_observation())
    tampered["rejected_evidence_kept_on_record"] = False
    assert nf.validate_next_family_decision(tampered)["valid"] is False


def test_nothing_built_or_run_in_this_block():
    record = nf.certify_next_family_decision(_observation())
    assert record["strategy_spec_built_here"] is False
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
    tracked = nf.certify_next_family_decision(_observation(
        tracked_output_paths=["data/x"]))
    assert tracked["verdict"] == nf.VERDICT_NF_REJECTED
    tampered = nf.certify_next_family_decision(_observation())
    tampered["live_gate_locked"] = False
    assert nf.validate_next_family_decision(tampered)["valid"] is False
    tampered2 = nf.certify_next_family_decision(_observation())
    tampered2["forbidden"] = tampered2["forbidden"][:3]
    assert nf.validate_next_family_decision(tampered2)["valid"] is False
    assert (nf.certify_next_family_decision(_observation())
            == nf.certify_next_family_decision(_observation()))


def test_upstream_stack_and_pm_lane_untouched():
    import sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract as rj
    assert rj.REJECTION_STATUS == "REJECTED_KEPT_ON_RECORD"
    assert rj.EXPECTED_V3_MAX_RISK_BPS == 39.680383
    import sparta_commander.ny_session_fvg_choch_additional_session_days_staged_candles_review as ad
    assert len(ad.BASELINE_PROTECTED_FILES) == 5
    from sparta_commander.crypto_d1_auto_research_strategy_optimizer_contract import (
        build_optimizer_contract)
    assert build_optimizer_contract()["verdict"] == (
        "CRYPTO_D1_AUTO_RESEARCH_OPTIMIZER_CONTRACT_READY")
    from sparta_commander.crypto_d1_auto_research_mutable_candidate_asset_spec import (
        ALLOWED_EDITABLE_FIELDS)
    assert len(ALLOWED_EDITABLE_FIELDS) == 16
    from sparta_commander.strategy_factory_mission_flow_status import (
        LATEST_COMPLETED_PM_LANE_CHAIN)
    assert "Research Only" in LATEST_COMPLETED_PM_LANE_CHAIN


def test_label_action_read_only_and_imports_clean():
    assert nf.get_next_family_decision_label() == nf.NF_LABEL
    assert "READ-ONLY" in nf.NF_LABEL and nf.NF_MODE == "RESEARCH_ONLY"
    assert nf.NEXT_REQUIRED_ACTION == (
        "HUMAN_APPROVED_BREAKOUT_PULLBACK_STRATEGY_SPEC_CONTRACT")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in nf.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(nf.__file__, encoding="utf-8").read()
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
        for fragment in ("replay_runner", "replay_spec", "optimizer",
                         "detector_spec"):
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