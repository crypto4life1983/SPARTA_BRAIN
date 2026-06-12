"""SPARTA NY-Session FVG+CHOCH V3 RESULT + FORMAL CANDIDATE REJECTION
RECORD (READ-ONLY, EVIDENCE FREEZE, RUNS NOTHING).

The honest end of the first auto-research candidate. V3's structural stops
widened risk units 2-4x (max 39.68 bps) yet every one of the 7 detector-
accepted setups still fell short of the 81 bps floor -- across 21 sessions,
377 eligible fresh zones, two stop models, and a fee-honest replay that
netted -21.04R. The candidate is REJECTED_KEPT_ON_RECORD:
COST_NON_VIABLE_RISK_GEOMETRY. Nothing is deleted, nothing is hidden,
nothing is promoted, nothing ever touched paper or live. Any future revival
needs a NEW candidate family or a separately approved lower-cost research
lane -- maker execution is never assumed retroactively.
"""

from __future__ import annotations

import hashlib as _hashlib
import json as _json
import pathlib as _pathlib
from typing import Any

from sparta_commander.ny_session_fvg_choch_additional_session_days_staged_candles_review import (
    BASELINE_PROTECTED_FILES,
)
from sparta_commander.ny_session_fvg_choch_expanded_sample_redetection_review_contract import (
    EXPECTED_ACCEPTED_SETUP_IDS,
    EXPECTED_LABELS_SHA256 as EXPANDED_LABELS_SHA256,
    LABELS_PATH as EXPANDED_LABELS_PATH,
)
from sparta_commander.ny_session_fvg_choch_fee_honest_replay_results_review_contract import (
    EXPECTED_RESULTS_SHA256 as REPLAY_RESULTS_SHA256,
    EXPECTED_TOTAL_NET_R,
    RESULTS_PATH as REPLAY_RESULTS_PATH,
)
from sparta_commander.ny_session_fvg_choch_mutable_candidate_edit_v3_wider_structural_stop import (
    EDIT_V3_ID,
    VERDICT_M3_READY,
    build_mutable_candidate_edit_v3,
)
from sparta_commander.ny_session_fvg_choch_strategy_spec_contract import (
    CANDIDATE_FAMILY,
    CANDIDATE_ID,
)
from sparta_commander.ny_session_fvg_choch_v2_cost_viability_result_review_contract import (
    ARTIFACT_PATH as V2_ARTIFACT_PATH,
    EXPECTED_ARTIFACT_SHA256 as V2_ARTIFACT_SHA256,
)

RJ_SCHEMA_VERSION = (
    "ny_session_fvg_choch_v3_result_and_candidate_rejection_record.v1")
RJ_LABEL = ("SPARTA NY-Session FVG+CHOCH V3 Result + Candidate Rejection "
            "Record (READ-ONLY, EVIDENCE FREEZE, REJECTED KEPT ON RECORD)")
RJ_MODE = "RESEARCH_ONLY"
VERDICT_RJ_RECORDED = (
    "V3_RESULT_FROZEN_AND_CANDIDATE_REJECTED_KEPT_ON_RECORD")
VERDICT_RJ_REVIEW_REJECTED = "REJECTION_RECORD_REVIEW_REJECTED"
VERDICT_RJ_BLOCKED = "REJECTION_RECORD_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_DECISION_ON_NEXT_CANDIDATE_FAMILY"

V3_ARTIFACT_PATH = ("data/ny_fvg_choch/detector_labels/"
                    "v3_structural_stop_eligibility_2026-05-12"
                    "_2026-06-10.json")
EXPECTED_V3_ARTIFACT_SHA256 = (
    "31cf3393245d99657b06bf88a6e049798c4d8f544052038c211de20b5a270293")

EXPECTED_TOTAL_LABELS = 619
EXPECTED_ELIGIBLE_FRESH_ZONES = 377
EXPECTED_DETECTOR_ACCEPTED = 7
EXPECTED_REJECTED_BY_FLOOR = 7
EXPECTED_SURVIVORS = 0
EXPECTED_V3_STOP_GEOMETRY = "choch_leg_structural_extreme"

# Full-precision frozen V3 risk distances (rounded display in parentheses).
EXPECTED_V3_RISK_DISTANCES_BPS = {
    "ETHUSD_20260513_editv1exp_setup01_touch2": 11.285438,   # short 11.3
    "AVAXUSD_20260529_editv1exp_setup04_touch2": 12.345679,  # long  12.3
    "SOLUSD_20260526_editv1exp_setup01_touch1": 13.449506,   # long  13.4
    "ETHUSD_20260515_editv1exp_setup02_touch2": 13.846892,   # short 13.8
    "BTCUSD_20260609_editv1exp_setup05_touch1": 18.11269,    # long  18.1
    "SOLUSD_20260520_editv1exp_setup02_touch1": 24.624765,   # long  24.6
    "SOLUSD_20260513_editv1exp_setup02_touch1": 39.680383,   # short 39.7
}
EXPECTED_V3_MAX_RISK_BPS = 39.680383
EXPECTED_V1V2_MAX_RISK_BPS = 33.15758
EXPECTED_FLOOR_BPS = 81

REJECTION_STATUS = "REJECTED_KEPT_ON_RECORD"
REJECTION_REASON = "COST_NON_VIABLE_RISK_GEOMETRY"
REJECTION_CONCLUSION = (
    "the 1m NY-session FVG/CHOCH geometry does not produce risk units "
    "large enough to survive 27 bps taker execution under either "
    "impulse-candle stops or CHOCH-leg structural stops")

EVIDENCE_BASIS = (
    "v1_v2_impulse_stop_max_33_158_bps_vs_81_bps_required",
    "v3_structural_stop_max_39_680_bps_vs_81_bps_required",
    "21_sessions_377_eligible_fresh_zones_7_detector_accepted_0_cost_viable"
    "_survivors",
    "fee_honest_replay_of_the_7_v1_labels_netted_minus_21_040902_r_at_27bps",
)

FUTURE_RULE = (
    "do_not_promote_paper_trade_or_live_trade_this_candidate",
    "any_future_revival_requires_a_new_candidate_family_or_a_separately"
    "_approved_lower_cost_maker_execution_research_lane",
    "maker_execution_must_not_be_assumed_retroactively",
    "all_v1_v2_v3_evidence_stays_on_record_never_deleted_or_hidden",
)

FORBIDDEN = (
    "replay_runs", "scorer_runs", "optimizer_runs",
    "paper_live_micro_live_authorization", "order_placement",
    "broker_exchange_private_api_access",
    "credentials_api_keys_login_account_wallet",
    "deleting_or_hiding_rejected_evidence",
    "modifying_v1_v2_v3_artifacts",
    "lowering_costs_to_rescue_the_candidate",
    "assuming_maker_execution_retroactively", "gate_unlocks",
    "mission_flow_registration_unless_separately_approved",
)

REVIEW_CHECKLIST = (
    "v3_artifact_present_and_sha_pinned",
    "v3_edit_pushed_and_ready",
    "detection_chain_unchanged_619_377_7",
    "same_7_setup_ids_as_v1_v2",
    "v3_structural_stop_applied",
    "v3_risk_distances_match_frozen_table",
    "rejected_by_81bps_floor_7_of_7",
    "survivors_zero_and_replay_ready_false",
    "no_replay_pnl_scorer_or_optimizer_execution",
    "no_maker_assumption_and_no_cost_lowering",
    "prior_v1_v2_evidence_byte_identical",
    "artifacts_untracked_and_gates_locked",
)


def get_rejection_record_label() -> str:
    return RJ_LABEL


def observe_v3_result(repo_root: Any,
                      tracked_paths: Any = ()) -> dict[str, Any]:
    """READ-ONLY observation of the V3 artifact and full evidence state."""
    root = _pathlib.Path(str(repo_root))
    artifact_file = root / V3_ARTIFACT_PATH
    observation: dict[str, Any] = {
        "artifact_present": artifact_file.is_file(),
        "artifact": None, "artifact_sha256": None,
        "v3_edit_verdict": None,
        "tracked_output_paths": [str(p) for p in (tracked_paths or ())],
        "baseline_files_sha256": {},
        "v2_artifact_sha256": None, "expanded_labels_sha256": None,
        "replay_results_sha256": None,
    }
    if observation["artifact_present"]:
        raw = artifact_file.read_bytes()
        observation["artifact_sha256"] = _hashlib.sha256(raw).hexdigest()
        observation["artifact"] = _json.loads(raw.decode("utf-8"))
    observation["v3_edit_verdict"] = build_mutable_candidate_edit_v3(
        repo_root).get("verdict")
    for rel_path in BASELINE_PROTECTED_FILES:
        target = root / rel_path
        observation["baseline_files_sha256"][rel_path] = (
            _hashlib.sha256(target.read_bytes()).hexdigest()
            if target.is_file() else None)
    for key, rel_path in (("v2_artifact_sha256", V2_ARTIFACT_PATH),
                          ("expanded_labels_sha256", EXPANDED_LABELS_PATH),
                          ("replay_results_sha256", REPLAY_RESULTS_PATH)):
        target = root / rel_path
        if target.is_file():
            observation[key] = _hashlib.sha256(
                target.read_bytes()).hexdigest()
    return observation


def certify_rejection_record(observation: Any) -> dict[str, Any]:
    """DETERMINISTIC certification of the V3 result + formal rejection."""
    record: dict[str, Any] = {
        "schema_version": RJ_SCHEMA_VERSION, "label": RJ_LABEL,
        "mode": RJ_MODE, "lane": "crypto_d1_auto_research",
        "candidate_id": CANDIDATE_ID,
        "candidate_family": CANDIDATE_FAMILY,
        "edit_id": EDIT_V3_ID,
        "verdict": None, "blockers": [],
        "checklist": list(REVIEW_CHECKLIST), "checklist_results": {},
        "rejection_status": REJECTION_STATUS,
        "rejection_reason": REJECTION_REASON,
        "rejection_conclusion": REJECTION_CONCLUSION,
        "evidence_basis": list(EVIDENCE_BASIS),
        "future_rule": list(FUTURE_RULE),
        "expected_v3_risk_distances_bps": dict(
            EXPECTED_V3_RISK_DISTANCES_BPS),
        "v3_max_risk_bps": EXPECTED_V3_MAX_RISK_BPS,
        "v1v2_max_risk_bps": EXPECTED_V1V2_MAX_RISK_BPS,
        "floor_bps": EXPECTED_FLOOR_BPS,
        "replay_net_r_evidence": EXPECTED_TOTAL_NET_R,
        "forbidden": list(FORBIDDEN),
        "replay_ready": False, "replay_authorized": False,
        "candidate_approved_for_paper_or_live": False,
        "profitability_claim_permitted": False,
        "promotion_claim_permitted": False,
        "maker_execution_assumed": False,
        "cost_floor_lowered": False,
        "evidence_deleted_or_hidden": False,
        "rejected_evidence_kept_on_record": True,
        "outputs_remain_untracked_operational_evidence": True,
        "this_record_changes_no_rules": True,
        "modifies_mission_flow": False, "modifies_pm_lane": False,
        "human_review_required": True,
        "executes": False, "writes_files": False, "writes_reports": False,
        "modifies_labels": False, "deletes_labels": False,
        "modifies_staged_files": False,
        "runs_detector_now": False, "runs_replay_now": False,
        "scores_now": False, "fetches_data": False, "calls_api": False,
        "uses_network": False, "uses_credentials": False, "uses_wallet": False,
        "connects_broker": False, "connects_exchange": False,
        "uses_real_money": False, "contains_order_logic": False,
        "starts_scheduler": False, "sends_notifications": False,
        "authorizes_paper_execution": False, "authorizes_micro_live": False,
        "authorizes_live_trading": False, "promotes_gate": False,
        "unlocks_downstream_gate": False,
        "paper_trading_gate_locked": True, "micro_live_gate_locked": True,
        "live_gate_locked": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    if not isinstance(observation, dict):
        record["verdict"] = VERDICT_RJ_BLOCKED
        record["blockers"].append("observation_missing")
        return record
    o = observation
    if not o.get("artifact_present"):
        record["verdict"] = VERDICT_RJ_BLOCKED
        record["blockers"].append("v3_artifact_missing")
        return record

    artifact = o.get("artifact") or {}
    controls = artifact.get("stale_fvg_controls") or {}
    eligibility = artifact.get("per_accepted_label_v3_eligibility") or []
    cost_floor = artifact.get("v2_cost_floor_active") or {}
    r: dict[str, bool] = {}
    r["v3_artifact_present_and_sha_pinned"] = (
        o.get("artifact_sha256") == EXPECTED_V3_ARTIFACT_SHA256)
    r["v3_edit_pushed_and_ready"] = (
        o.get("v3_edit_verdict") == VERDICT_M3_READY
        and artifact.get("edit_id") == EDIT_V3_ID)
    r["detection_chain_unchanged_619_377_7"] = (
        artifact.get("labels_total") == EXPECTED_TOTAL_LABELS
        and controls.get("zones_eligible_fresh")
        == EXPECTED_ELIGIBLE_FRESH_ZONES
        and artifact.get("detector_accepted")
        == EXPECTED_DETECTOR_ACCEPTED)
    observed_ids = tuple(sorted(entry.get("setup_id")
                                for entry in eligibility))
    r["same_7_setup_ids_as_v1_v2"] = (
        observed_ids == tuple(sorted(EXPECTED_ACCEPTED_SETUP_IDS)))
    r["v3_structural_stop_applied"] = (
        artifact.get("v3_stop_geometry") == EXPECTED_V3_STOP_GEOMETRY
        and all(entry.get("v3_structural_stop") is not None
                and entry.get("v3_structural_stop")
                != entry.get("v1_impulse_stop") for entry in eligibility))
    observed_distances = {entry.get("setup_id"):
                          entry.get("v3_risk_distance_bps")
                          for entry in eligibility}
    r["v3_risk_distances_match_frozen_table"] = (
        observed_distances == EXPECTED_V3_RISK_DISTANCES_BPS
        and len(eligibility) == 7
        and max(EXPECTED_V3_RISK_DISTANCES_BPS.values())
        == EXPECTED_V3_MAX_RISK_BPS < EXPECTED_FLOOR_BPS)
    r["rejected_by_81bps_floor_7_of_7"] = (
        artifact.get("rejected_by_81bps_floor")
        == EXPECTED_REJECTED_BY_FLOOR
        and all(entry.get("v3_replay_eligible") is False
                and entry.get("minimum_required_bps") == EXPECTED_FLOOR_BPS
                for entry in eligibility))
    r["survivors_zero_and_replay_ready_false"] = (
        artifact.get("surviving_v3") == EXPECTED_SURVIVORS
        and artifact.get("surviving_setup_ids") == []
        and artifact.get("replay_ready") is False)
    r["no_replay_pnl_scorer_or_optimizer_execution"] = (
        artifact.get("no_pnl_no_scoring_no_replay") is True
        and artifact.get("labels_authorize_nothing") is True
        and not any("pnl" in str(key).lower() or "profit" in str(key).lower()
                    for entry in eligibility for key in entry))
    r["no_maker_assumption_and_no_cost_lowering"] = (
        cost_floor.get("maker_execution_assumed") is False
        and cost_floor.get("costs_lowered") is False
        and cost_floor.get("minimum_risk_distance_bps")
        == EXPECTED_FLOOR_BPS
        and cost_floor.get("round_trip_cost_bps") == 27)
    r["prior_v1_v2_evidence_byte_identical"] = (
        o.get("baseline_files_sha256") == BASELINE_PROTECTED_FILES
        and o.get("v2_artifact_sha256") == V2_ARTIFACT_SHA256
        and o.get("expanded_labels_sha256") == EXPANDED_LABELS_SHA256
        and o.get("replay_results_sha256") == REPLAY_RESULTS_SHA256)
    r["artifacts_untracked_and_gates_locked"] = not o.get(
        "tracked_output_paths")
    record["checklist_results"] = r
    failed = [name for name, ok in r.items() if not ok]
    if failed:
        record["verdict"] = VERDICT_RJ_REVIEW_REJECTED
        record["blockers"].extend("check_failed:" + n for n in failed)
        return record
    record["verdict"] = VERDICT_RJ_RECORDED
    return record


def build_rejection_record(repo_root: Any,
                           tracked_paths: Any = ()) -> dict[str, Any]:
    """Observe the V3 result read-only and certify the rejection record."""
    return certify_rejection_record(
        observe_v3_result(repo_root, tracked_paths))


def validate_rejection_record(record: Any) -> dict[str, Any]:
    """Validate the record's shape and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    v = record
    if v.get("verdict") not in (VERDICT_RJ_RECORDED,
                                VERDICT_RJ_REVIEW_REJECTED,
                                VERDICT_RJ_BLOCKED):
        errors.append("bad_verdict")
    if v.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if v.get("candidate_family") != CANDIDATE_FAMILY:
        errors.append("candidate_family_tampered")
    if tuple(v.get("checklist") or ()) != REVIEW_CHECKLIST:
        errors.append("checklist_tampered")
    if v.get("rejection_status") != REJECTION_STATUS:
        errors.append("rejection_status_tampered")
    if v.get("rejection_reason") != REJECTION_REASON:
        errors.append("rejection_reason_tampered")
    if v.get("rejection_conclusion") != REJECTION_CONCLUSION:
        errors.append("rejection_conclusion_tampered")
    if tuple(v.get("evidence_basis") or ()) != EVIDENCE_BASIS:
        errors.append("evidence_basis_tampered")
    if tuple(v.get("future_rule") or ()) != FUTURE_RULE:
        errors.append("future_rule_tampered")
    if v.get("expected_v3_risk_distances_bps") != (
            EXPECTED_V3_RISK_DISTANCES_BPS):
        errors.append("risk_distance_evidence_tampered")
    if v.get("v3_max_risk_bps") != EXPECTED_V3_MAX_RISK_BPS:
        errors.append("v3_max_tampered")
    if v.get("v1v2_max_risk_bps") != EXPECTED_V1V2_MAX_RISK_BPS:
        errors.append("v1v2_max_tampered")
    if v.get("floor_bps") != EXPECTED_FLOOR_BPS:
        errors.append("floor_tampered")
    if v.get("replay_net_r_evidence") != EXPECTED_TOTAL_NET_R:
        errors.append("replay_evidence_tampered")
    if tuple(v.get("forbidden") or ()) != FORBIDDEN:
        errors.append("forbidden_list_weakened")
    for key in ("replay_ready", "replay_authorized",
                "candidate_approved_for_paper_or_live",
                "profitability_claim_permitted",
                "promotion_claim_permitted", "maker_execution_assumed",
                "cost_floor_lowered", "evidence_deleted_or_hidden"):
        if v.get(key) is not False:
            errors.append("must_be_false_forever:" + key)
    results = v.get("checklist_results") or {}
    if v.get("verdict") == VERDICT_RJ_RECORDED:
        if v.get("blockers"):
            errors.append("recorded_with_blockers")
        if set(results) != set(REVIEW_CHECKLIST) or not all(
                results.get(n) is True for n in REVIEW_CHECKLIST):
            errors.append("recorded_without_full_passing_checklist")
    if v.get("verdict") in (VERDICT_RJ_REVIEW_REJECTED,
                            VERDICT_RJ_BLOCKED) and not v.get("blockers"):
        errors.append("non_recorded_without_blockers")
    for key, want in (
        ("rejected_evidence_kept_on_record", True),
        ("outputs_remain_untracked_operational_evidence", True),
        ("this_record_changes_no_rules", True),
        ("modifies_mission_flow", False), ("modifies_pm_lane", False),
        ("human_review_required", True),
        ("paper_trading_gate_locked", True),
        ("micro_live_gate_locked", True), ("live_gate_locked", True),
    ):
        if v.get(key) is not want:
            errors.append("constitution_flag_wrong:" + key)
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
        if v.get(key) is not False:
            errors.append("capability_not_false:" + key)
    return {"valid": not errors, "errors": errors}
