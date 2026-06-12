"""Tests for the SPARTA NY FVG+CHOCH V3 Result + Candidate Rejection Record.

Proves the formal rejection freezes the complete V3 evidence (619/377/7,
structural stops, max 39.68 bps vs the 81 bps floor, 0 survivors), requires
the pushed V3 edit and an untampered artifact, rejects any survivor or
profitability/promotion/maker/cost-lowering claim, keeps every piece of
evidence on record, and leaves all gates LOCKED forever for this candidate.
"""

from __future__ import annotations

import ast
import os.path

import pytest

import sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract as rj


def _eligibility():
    rows = []
    for setup_id, bps in sorted(rj.EXPECTED_V3_RISK_DISTANCES_BPS.items()):
        rows.append({"setup_id": setup_id,
                     "symbol": setup_id.split("_")[0],
                     "session_date": "2026-05-13",
                     "direction": "long",
                     "entry_price": 100.0,
                     "v1_impulse_stop": 99.99,
                     "v3_structural_stop": 99.90,
                     "v3_risk_distance_bps": bps,
                     "minimum_required_bps": 81,
                     "v3_replay_eligible": False,
                     "reason": ("cost_dominated_setup_rejected:"
                                "distance_below_81_bps")})
    return rows


def _artifact(**overrides):
    artifact = {
        "edit_id": ("NY_SESSION_FVG_CHOCH_MUTABLE_CANDIDATE_EDIT_V3_WIDER"
                    "_STRUCTURAL_STOP"),
        "v3_stop_geometry": "choch_leg_structural_extreme",
        "labels_total": 619,
        "stale_fvg_controls": {"zones_with_session_touch": 5573,
                               "zones_filtered_stale_age": 4824,
                               "zones_filtered_mitigated": 372,
                               "zones_eligible_fresh": 377,
                               "touches_capped_beyond_limit": 715},
        "detector_accepted": 7,
        "per_accepted_label_v3_eligibility": _eligibility(),
        "rejected_by_81bps_floor": 7,
        "surviving_v3": 0,
        "surviving_setup_ids": [],
        "replay_ready": False,
        "replay_requires_separate_human_approval": True,
        "v2_cost_floor_active": {"round_trip_cost_bps": 27,
                                 "minimum_risk_to_round_trip_cost_multiple":
                                     3,
                                 "minimum_risk_distance_bps": 81,
                                 "maker_execution_assumed": False,
                                 "costs_lowered": False},
        "no_pnl_no_scoring_no_replay": True,
        "labels_authorize_nothing": True,
    }
    artifact.update(overrides)
    return artifact


def _observation(**overrides):
    observation = {
        "artifact_present": True,
        "artifact": overrides.pop("artifact", None) or _artifact(),
        "artifact_sha256": rj.EXPECTED_V3_ARTIFACT_SHA256,
        "v3_edit_verdict": "NY_FVG_CHOCH_MUTABLE_CANDIDATE_EDIT_V3_READY",
        "tracked_output_paths": [],
        "baseline_files_sha256": dict(rj.BASELINE_PROTECTED_FILES),
        "v2_artifact_sha256": rj.V2_ARTIFACT_SHA256,
        "expanded_labels_sha256": rj.EXPANDED_LABELS_SHA256,
        "replay_results_sha256": rj.REPLAY_RESULTS_SHA256,
    }
    observation.update(overrides)
    return observation


def test_valid_v3_result_records_formal_rejection():
    record = rj.certify_rejection_record(_observation())
    assert record["verdict"] == rj.VERDICT_RJ_RECORDED
    assert record["blockers"] == []
    assert record["rejection_status"] == "REJECTED_KEPT_ON_RECORD"
    assert record["rejection_reason"] == "COST_NON_VIABLE_RISK_GEOMETRY"
    assert all(record["checklist_results"][n] is True
               for n in rj.REVIEW_CHECKLIST)
    assert len(rj.REVIEW_CHECKLIST) == 12
    assert rj.validate_rejection_record(record)["valid"] is True


def test_real_v3_artifact_records_rejection_when_present():
    if not os.path.isfile("C:/SPARTA_BRAIN/" + rj.V3_ARTIFACT_PATH):
        pytest.skip("real V3 artifact absent on this machine")
    record = rj.build_rejection_record("C:/SPARTA_BRAIN", tracked_paths=[])
    assert record["verdict"] == rj.VERDICT_RJ_RECORDED
    assert rj.validate_rejection_record(record)["valid"] is True


def test_rejection_requires_pushed_v3_edit_and_valid_artifact():
    not_ready = rj.certify_rejection_record(_observation(
        v3_edit_verdict="NY_FVG_CHOCH_MUTABLE_CANDIDATE_EDIT_V3_BLOCKED"))
    assert not_ready["verdict"] == rj.VERDICT_RJ_REVIEW_REJECTED
    assert "check_failed:v3_edit_pushed_and_ready" in not_ready["blockers"]
    wrong_edit = rj.certify_rejection_record(_observation(
        artifact=_artifact(edit_id="SOME_OTHER_EDIT")))
    assert "check_failed:v3_edit_pushed_and_ready" in wrong_edit["blockers"]


def test_missing_or_tampered_v3_artifact_blocks_or_rejects():
    missing = rj.certify_rejection_record(_observation(
        artifact_present=False))
    assert missing["verdict"] == rj.VERDICT_RJ_BLOCKED
    assert "v3_artifact_missing" in missing["blockers"]
    tampered = rj.certify_rejection_record(_observation(
        artifact_sha256="0" * 64))
    assert tampered["verdict"] == rj.VERDICT_RJ_REVIEW_REJECTED
    assert ("check_failed:v3_artifact_present_and_sha_pinned"
            in tampered["blockers"])
    assert rj.certify_rejection_record(None)["verdict"] == (
        rj.VERDICT_RJ_BLOCKED)


def test_any_survivor_rejects_this_rejection_record():
    survivor = rj.certify_rejection_record(_observation(artifact=_artifact(
        surviving_v3=1,
        surviving_setup_ids=["SOLUSD_20260513_editv1exp_setup02_touch1"])))
    assert survivor["verdict"] == rj.VERDICT_RJ_REVIEW_REJECTED
    assert ("check_failed:survivors_zero_and_replay_ready_false"
            in survivor["blockers"])
    eligibility = _eligibility()
    eligibility[0]["v3_replay_eligible"] = True
    sneaky = rj.certify_rejection_record(_observation(artifact=_artifact(
        per_accepted_label_v3_eligibility=eligibility)))
    assert ("check_failed:rejected_by_81bps_floor_7_of_7"
            in sneaky["blockers"])


def test_replay_ready_true_rejects_this_rejection_record():
    ready = rj.certify_rejection_record(_observation(
        artifact=_artifact(replay_ready=True)))
    assert ready["verdict"] == rj.VERDICT_RJ_REVIEW_REJECTED
    assert ("check_failed:survivors_zero_and_replay_ready_false"
            in ready["blockers"])
    tampered = rj.certify_rejection_record(_observation())
    tampered["replay_ready"] = True
    assert rj.validate_rejection_record(tampered)["valid"] is False


def test_missing_or_changed_risk_distance_table_rejects():
    missing_rows = rj.certify_rejection_record(_observation(
        artifact=_artifact(per_accepted_label_v3_eligibility=
                           _eligibility()[:-1])))
    assert ("check_failed:v3_risk_distances_match_frozen_table"
            in missing_rows["blockers"])
    eligibility = _eligibility()
    for row in eligibility:
        if row["setup_id"] == "SOLUSD_20260513_editv1exp_setup02_touch1":
            row["v3_risk_distance_bps"] = 95.0  # fake floor-clearing max
    widened = rj.certify_rejection_record(_observation(artifact=_artifact(
        per_accepted_label_v3_eligibility=eligibility)))
    assert widened["verdict"] == rj.VERDICT_RJ_REVIEW_REJECTED
    assert rj.EXPECTED_V3_MAX_RISK_BPS == 39.680383 < 81
    assert rj.EXPECTED_V1V2_MAX_RISK_BPS == 33.15758 < 81
    tampered = rj.certify_rejection_record(_observation())
    tampered["expected_v3_risk_distances_bps"] = {}
    assert rj.validate_rejection_record(tampered)["valid"] is False
    tampered2 = rj.certify_rejection_record(_observation())
    tampered2["v3_max_risk_bps"] = 100.0
    assert rj.validate_rejection_record(tampered2)["valid"] is False


def test_pnl_profitability_or_promotion_claims_reject():
    eligibility = _eligibility()
    eligibility[2]["net_pnl"] = 9.0
    leak = rj.certify_rejection_record(_observation(artifact=_artifact(
        per_accepted_label_v3_eligibility=eligibility)))
    assert ("check_failed:no_replay_pnl_scorer_or_optimizer_execution"
            in leak["blockers"])
    no_flag = rj.certify_rejection_record(_observation(
        artifact=_artifact(no_pnl_no_scoring_no_replay=False)))
    assert no_flag["verdict"] == rj.VERDICT_RJ_REVIEW_REJECTED
    for flag in ("profitability_claim_permitted",
                 "promotion_claim_permitted",
                 "candidate_approved_for_paper_or_live",
                 "replay_authorized"):
        tampered = rj.certify_rejection_record(_observation())
        tampered[flag] = True
        assert rj.validate_rejection_record(tampered)["valid"] is False, flag


def test_maker_assumption_and_cost_lowering_reject():
    maker = rj.certify_rejection_record(_observation(artifact=_artifact(
        v2_cost_floor_active={"round_trip_cost_bps": 27,
                              "minimum_risk_to_round_trip_cost_multiple": 3,
                              "minimum_risk_distance_bps": 81,
                              "maker_execution_assumed": True,
                              "costs_lowered": False})))
    assert ("check_failed:no_maker_assumption_and_no_cost_lowering"
            in maker["blockers"])
    lowered = rj.certify_rejection_record(_observation(artifact=_artifact(
        v2_cost_floor_active={"round_trip_cost_bps": 2,
                              "minimum_risk_to_round_trip_cost_multiple": 3,
                              "minimum_risk_distance_bps": 6,
                              "maker_execution_assumed": False,
                              "costs_lowered": True})))
    assert lowered["verdict"] == rj.VERDICT_RJ_REVIEW_REJECTED
    tampered = rj.certify_rejection_record(_observation())
    tampered["maker_execution_assumed"] = True
    assert rj.validate_rejection_record(tampered)["valid"] is False
    tampered2 = rj.certify_rejection_record(_observation())
    tampered2["cost_floor_lowered"] = True
    assert rj.validate_rejection_record(tampered2)["valid"] is False
    assert "assuming_maker_execution_retroactively" in rj.FORBIDDEN
    assert "lowering_costs_to_rescue_the_candidate" in rj.FORBIDDEN


def test_evidence_deletion_or_hiding_rejects():
    mutated = dict(rj.BASELINE_PROTECTED_FILES)
    mutated[next(iter(mutated))] = None  # a protected file deleted
    deleted = rj.certify_rejection_record(_observation(
        baseline_files_sha256=mutated))
    assert ("check_failed:prior_v1_v2_evidence_byte_identical"
            in deleted["blockers"])
    wrong_v2 = rj.certify_rejection_record(_observation(
        v2_artifact_sha256="0" * 64))
    assert ("check_failed:prior_v1_v2_evidence_byte_identical"
            in wrong_v2["blockers"])
    tampered = rj.certify_rejection_record(_observation())
    tampered["evidence_deleted_or_hidden"] = True
    assert rj.validate_rejection_record(tampered)["valid"] is False
    tampered2 = rj.certify_rejection_record(_observation())
    tampered2["rejected_evidence_kept_on_record"] = False
    assert rj.validate_rejection_record(tampered2)["valid"] is False
    assert "deleting_or_hiding_rejected_evidence" in rj.FORBIDDEN
    assert ("all_v1_v2_v3_evidence_stays_on_record_never_deleted_or_hidden"
            in rj.FUTURE_RULE)


def test_formal_rejection_content_frozen():
    record = rj.certify_rejection_record(_observation())
    assert record["candidate_id"] == (
        "NY_SESSION_FVG_CHOCH_STRATEGY_CANDIDATE_V1")
    assert record["candidate_family"] == "intraday_fvg_choch"
    assert "does not produce risk units" in record["rejection_conclusion"]
    assert ("v1_v2_impulse_stop_max_33_158_bps_vs_81_bps_required"
            in record["evidence_basis"])
    assert ("v3_structural_stop_max_39_680_bps_vs_81_bps_required"
            in record["evidence_basis"])
    assert ("fee_honest_replay_of_the_7_v1_labels_netted_minus_21_040902_r"
            "_at_27bps" in record["evidence_basis"])
    assert ("do_not_promote_paper_trade_or_live_trade_this_candidate"
            in record["future_rule"])
    assert ("maker_execution_must_not_be_assumed_retroactively"
            in record["future_rule"])
    assert record["replay_net_r_evidence"] == -21.040902
    for field, value in (("rejection_status", "APPROVED"),
                         ("rejection_reason", "CHANGED_MY_MIND"),
                         ("rejection_conclusion", "it works actually")):
        tampered = rj.certify_rejection_record(_observation())
        tampered[field] = value
        assert rj.validate_rejection_record(tampered)["valid"] is False, field
    tampered2 = rj.certify_rejection_record(_observation())
    tampered2["future_rule"] = ["promote_it"]
    assert rj.validate_rejection_record(tampered2)["valid"] is False


def test_artifacts_untracked_and_gates_locked():
    tracked = rj.certify_rejection_record(_observation(
        tracked_output_paths=["data/ny_fvg_choch/x.json"]))
    assert tracked["verdict"] == rj.VERDICT_RJ_REVIEW_REJECTED
    record = rj.certify_rejection_record(_observation())
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
    tampered = rj.certify_rejection_record(_observation())
    tampered["forbidden"] = tampered["forbidden"][:3]
    assert rj.validate_rejection_record(tampered)["valid"] is False
    assert (rj.certify_rejection_record(_observation())
            == rj.certify_rejection_record(_observation()))


def test_upstream_stack_and_pm_lane_untouched():
    import sparta_commander.ny_session_fvg_choch_mutable_candidate_edit_v3_wider_structural_stop as m3
    assert m3.VERDICT_M3_READY == "NY_FVG_CHOCH_MUTABLE_CANDIDATE_EDIT_V3_READY"
    import sparta_commander.ny_session_fvg_choch_v2_cost_viability_result_review_contract as v2r
    assert v2r.EXPECTED_SURVIVING == 0
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
    assert rj.get_rejection_record_label() == rj.RJ_LABEL
    assert "READ-ONLY" in rj.RJ_LABEL and rj.RJ_MODE == "RESEARCH_ONLY"
    assert rj.NEXT_REQUIRED_ACTION == (
        "HUMAN_DECISION_ON_NEXT_CANDIDATE_FAMILY")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in rj.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(rj.__file__, encoding="utf-8").read()
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
                   "email", "csv", "pandas", "os", "io", "shutil",
                   "databento", "ssl", "ftplib", "datetime"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
    assert not any(call.func.attr == "open" if isinstance(call.func, ast.Attribute)
                   else getattr(call.func, "id", "") == "open"
                   for call in ast.walk(tree) if isinstance(call, ast.Call))