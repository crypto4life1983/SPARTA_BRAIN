"""SPARTA NY-Session FVG+CHOCH V2 COST-VIABILITY RESULT REVIEW
(READ-ONLY, REVIEW ONLY, FREEZES THE EVIDENCE).

The V2 verdict, frozen: detection reproduced the frozen expanded run
byte-for-byte (619 labels, 377 eligible fresh zones, 7 detector-accepted),
then the 81 bps cost-viability floor rejected ALL 7 -- the widest risk
distance the strategy produced over 21 sessions was 33.2 bps. The exact
1m-FVG impulse-candle stop geometry is not viable under 27 bps taker
execution, and more sessions are unlikely to fix a structural issue. The
clean options -- rejection kept on record, V3 wider-stop research, or
separate lower-cost-execution research -- are a HUMAN decision. This review
runs nothing, claims nothing, changes no rules.
"""

from __future__ import annotations

import hashlib as _hashlib
import json as _json
import pathlib as _pathlib
from typing import Any

from sparta_commander.ny_session_fvg_choch_additional_session_days_staged_candles_review import (
    BASELINE_PROTECTED_FILES,
)
from sparta_commander.ny_session_fvg_choch_accepted_labels_human_review_contract import (
    BATCH2_MANIFEST_PATH,
    BATCH2_MANIFEST_SHA256,
)
from sparta_commander.ny_session_fvg_choch_expanded_sample_redetection_review_contract import (
    EXPECTED_LABELS_SHA256 as EXPANDED_LABELS_SHA256,
    LABELS_PATH as EXPANDED_LABELS_PATH,
)
from sparta_commander.ny_session_fvg_choch_fee_honest_replay_results_review_contract import (
    EXPECTED_RESULTS_SHA256 as REPLAY_RESULTS_SHA256,
    RESULTS_PATH as REPLAY_RESULTS_PATH,
)
from sparta_commander.ny_session_fvg_choch_mutable_candidate_edit_v2_cost_viability import (
    EDIT_V2_ID,
    V2_NEW_PARAMETERS,
    VERDICT_M2_READY,
    build_mutable_candidate_edit_v2,
)
from sparta_commander.ny_session_fvg_choch_strategy_spec_contract import (
    CANDIDATE_ID,
)

V2R_SCHEMA_VERSION = (
    "ny_session_fvg_choch_v2_cost_viability_result_review.v1")
V2R_LABEL = ("SPARTA NY-Session FVG+CHOCH V2 Cost-Viability Result Review "
             "(READ-ONLY, REVIEW ONLY, NO CLAIMS, CHANGES NO RULES)")
V2R_MODE = "RESEARCH_ONLY"
VERDICT_V2R_REJECTED_ALL = "V2_COST_VIABILITY_REJECTED_ALL_LABELS"
VERDICT_V2R_REVIEW_REJECTED = "V2_RESULT_REVIEW_REJECTED"
VERDICT_V2R_BLOCKED = "V2_RESULT_REVIEW_BLOCKED"
NEXT_REQUIRED_ACTION = (
    "HUMAN_DECISION_ON_V3_WIDER_STOPS_OR_REJECTION_KEPT_ON_RECORD")

ARTIFACT_PATH = ("data/ny_fvg_choch/detector_labels/"
                 "v2_cost_viability_eligibility_2026-05-12_2026-06-10.json")
EXPECTED_ARTIFACT_SHA256 = (
    "f2ad5171e8f5afd8600a6e128ce9de0fd5892ff40c783e66d0d2a4696b797ff4")

EXPECTED_TOTAL_LABELS = 619
EXPECTED_ELIGIBLE_FRESH_ZONES = 377
EXPECTED_DETECTOR_ACCEPTED = 7
EXPECTED_REJECTED_BY_COST_FILTER = 7
EXPECTED_SURVIVING = 0
EXPECTED_V1_CONTROLS = {"max_fvg_age_bars": 24,
                        "require_fresh_unmitigated_15m_fvg": True,
                        "max_zone_touches_before_invalidation": 2}

# The seven frozen risk distances (bps of entry), the heart of the evidence.
EXPECTED_RISK_DISTANCES_BPS = {
    "ETHUSD_20260513_editv1exp_setup01_touch2": 2.645024,
    "AVAXUSD_20260529_editv1exp_setup04_touch2": 4.489338,
    "SOLUSD_20260526_editv1exp_setup01_touch1": 7.601895,
    "ETHUSD_20260515_editv1exp_setup02_touch2": 9.253776,
    "BTCUSD_20260609_editv1exp_setup05_touch1": 16.480916,
    "SOLUSD_20260520_editv1exp_setup02_touch1": 17.589118,
    "SOLUSD_20260513_editv1exp_setup02_touch1": 33.15758,
}
EXPECTED_MINIMUM_REQUIRED_BPS = 81

HONEST_RESEARCH_CONCLUSION = (
    "exact_1m_fvg_impulse_candle_stop_geometry_is_not_viable_under_27bps_taker_execution",
    "widest_risk_distance_over_21_sessions_was_33_2_bps_versus_the_81_bps_floor",
    "more_sessions_are_unlikely_to_fix_a_structural_issue_with_single_digit_to_low_30_bps_risk_units",
    "option_1_rejection_kept_on_record",
    "option_2_v3_wider_structural_stop_research",
    "option_3_separate_lower_cost_maker_execution_research_not_assumed_here",
    "the_choice_is_a_human_decision_nothing_is_promoted_or_authorized",
)

_FORBIDDEN_TOKENS = ("pnl", "profit", "replay_status", "score", "net_r",
                     "gross_r", "win_rate", "order", "api_key", "wallet",
                     "login", "private_endpoint")

REVIEW_CHECKLIST = (
    "v2_artifact_present_and_sha_pinned",
    "detection_reproduced_frozen_expanded_run_byte_for_byte",
    "expanded_labels_hash_matches_pinned_reference",
    "total_setup_attempts_619",
    "eligible_fresh_zones_377",
    "detector_accepted_before_v2_was_7",
    "v2_rejected_7_of_7_and_zero_survivors",
    "replay_ready_false",
    "no_replay_pnl_scorer_or_optimizer_execution",
    "v2_params_read_from_pushed_asset_not_hardcoded",
    "v1_controls_remained_intact",
    "risk_distance_table_matches_frozen_evidence",
    "prior_outputs_and_candles_byte_identical",
    "artifacts_untracked_and_no_trading_capability",
)

FORBIDDEN = (
    "replay_runs", "pnl_calculation", "profitability_claims",
    "scorer_or_optimizer_runs", "rule_changes", "candidate_asset_changes",
    "modifying_labels_candles_or_artifacts", "deleting_prior_outputs",
    "broker_exchange_credential_access", "order_endpoints",
    "paper_live_micro_live_authorization", "gate_unlocks",
)


def get_v2_result_review_label() -> str:
    return V2R_LABEL


def observe_v2_result(repo_root: Any,
                      tracked_paths: Any = ()) -> dict[str, Any]:
    """READ-ONLY observation of the V2 artifact and full integrity state."""
    root = _pathlib.Path(str(repo_root))
    artifact_file = root / ARTIFACT_PATH
    observation: dict[str, Any] = {
        "artifact_present": artifact_file.is_file(),
        "artifact": None, "artifact_sha256": None,
        "v2_edit_verdict": None,
        "tracked_output_paths": [str(p) for p in (tracked_paths or ())],
        "baseline_files_sha256": {}, "batch2_manifest_sha256": None,
        "expanded_labels_sha256": None, "replay_results_sha256": None,
    }
    if observation["artifact_present"]:
        raw = artifact_file.read_bytes()
        observation["artifact_sha256"] = _hashlib.sha256(raw).hexdigest()
        observation["artifact"] = _json.loads(raw.decode("utf-8"))
    observation["v2_edit_verdict"] = build_mutable_candidate_edit_v2().get(
        "verdict")
    for rel_path in BASELINE_PROTECTED_FILES:
        target = root / rel_path
        observation["baseline_files_sha256"][rel_path] = (
            _hashlib.sha256(target.read_bytes()).hexdigest()
            if target.is_file() else None)
    for key, rel_path in (("batch2_manifest_sha256", BATCH2_MANIFEST_PATH),
                          ("expanded_labels_sha256", EXPANDED_LABELS_PATH),
                          ("replay_results_sha256", REPLAY_RESULTS_PATH)):
        target = root / rel_path
        if target.is_file():
            observation[key] = _hashlib.sha256(
                target.read_bytes()).hexdigest()
    return observation


def certify_v2_result(observation: Any) -> dict[str, Any]:
    """DETERMINISTIC certification of the V2 result. Pure."""
    review: dict[str, Any] = {
        "schema_version": V2R_SCHEMA_VERSION, "label": V2R_LABEL,
        "mode": V2R_MODE, "lane": "crypto_d1_auto_research",
        "candidate_id": CANDIDATE_ID, "edit_id": EDIT_V2_ID,
        "verdict": None, "blockers": [],
        "checklist": list(REVIEW_CHECKLIST), "checklist_results": {},
        "expected_risk_distances_bps": dict(EXPECTED_RISK_DISTANCES_BPS),
        "minimum_required_bps": EXPECTED_MINIMUM_REQUIRED_BPS,
        "honest_research_conclusion": list(HONEST_RESEARCH_CONCLUSION),
        "forbidden": list(FORBIDDEN),
        "replay_ready": False, "replay_authorized": False,
        "candidate_approved_for_paper_or_live": False,
        "profitability_claim_permitted": False,
        "artifacts_remain_untracked_operational_evidence": True,
        "v3_or_rejection_is_a_human_decision": True,
        "this_review_changes_no_rules": True,
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
        review["verdict"] = VERDICT_V2R_BLOCKED
        review["blockers"].append("observation_missing")
        return review
    o = observation
    if not o.get("artifact_present"):
        review["verdict"] = VERDICT_V2R_BLOCKED
        review["blockers"].append("v2_artifact_missing")
        return review

    artifact = o.get("artifact") or {}
    controls = artifact.get("stale_fvg_controls") or {}
    comparison = artifact.get("comparison_vs_v1_expanded_run") or {}
    eligibility = artifact.get("per_accepted_label_eligibility") or []
    r: dict[str, bool] = {}
    r["v2_artifact_present_and_sha_pinned"] = (
        o.get("artifact_sha256") == EXPECTED_ARTIFACT_SHA256)
    r["detection_reproduced_frozen_expanded_run_byte_for_byte"] = (
        artifact.get("detection_reproduced_frozen_expanded_run_exactly")
        is True)
    r["expanded_labels_hash_matches_pinned_reference"] = (
        o.get("expanded_labels_sha256") == EXPANDED_LABELS_SHA256)
    r["total_setup_attempts_619"] = (
        artifact.get("labels_total") == EXPECTED_TOTAL_LABELS
        and comparison.get("v1_labels") == EXPECTED_TOTAL_LABELS)
    r["eligible_fresh_zones_377"] = (
        controls.get("zones_eligible_fresh")
        == EXPECTED_ELIGIBLE_FRESH_ZONES)
    r["detector_accepted_before_v2_was_7"] = (
        artifact.get("detector_accepted") == EXPECTED_DETECTOR_ACCEPTED)
    r["v2_rejected_7_of_7_and_zero_survivors"] = (
        artifact.get("rejected_by_cost_viability_filter")
        == EXPECTED_REJECTED_BY_COST_FILTER
        and artifact.get("accepted_surviving_v2") == EXPECTED_SURVIVING
        and artifact.get("surviving_setup_ids") == []
        and all(entry.get("v2_replay_eligible") is False
                for entry in eligibility))
    r["replay_ready_false"] = artifact.get("replay_ready") is False
    r["no_replay_pnl_scorer_or_optimizer_execution"] = (
        artifact.get("no_pnl_no_scoring_no_replay") is True
        and artifact.get("labels_authorize_nothing") is True
        and not any(any(token in str(key).lower()
                        for token in _FORBIDDEN_TOKENS)
                    for entry in eligibility for key in entry))
    r["v2_params_read_from_pushed_asset_not_hardcoded"] = (
        artifact.get("edit_id") == EDIT_V2_ID
        and artifact.get("v2_parameters_active") == V2_NEW_PARAMETERS
        and o.get("v2_edit_verdict") == VERDICT_M2_READY)
    r["v1_controls_remained_intact"] = (
        artifact.get("v1_freshness_controls_active")
        == EXPECTED_V1_CONTROLS)
    observed_distances = {entry.get("setup_id"):
                          entry.get("entry_to_stop_distance_bps")
                          for entry in eligibility}
    r["risk_distance_table_matches_frozen_evidence"] = (
        observed_distances == EXPECTED_RISK_DISTANCES_BPS
        and all(entry.get("minimum_required_bps")
                == EXPECTED_MINIMUM_REQUIRED_BPS for entry in eligibility)
        and len(eligibility) == 7)
    r["prior_outputs_and_candles_byte_identical"] = (
        o.get("baseline_files_sha256") == BASELINE_PROTECTED_FILES
        and o.get("batch2_manifest_sha256") == BATCH2_MANIFEST_SHA256
        and o.get("replay_results_sha256") == REPLAY_RESULTS_SHA256)
    r["artifacts_untracked_and_no_trading_capability"] = (
        not o.get("tracked_output_paths")
        and artifact.get("replay_requires_separate_human_approval") is True)
    review["checklist_results"] = r
    failed = [name for name, ok in r.items() if not ok]
    if failed:
        review["verdict"] = VERDICT_V2R_REVIEW_REJECTED
        review["blockers"].extend("check_failed:" + n for n in failed)
        return review
    review["verdict"] = VERDICT_V2R_REJECTED_ALL
    return review


def build_v2_result_review(repo_root: Any,
                           tracked_paths: Any = ()) -> dict[str, Any]:
    """Observe the V2 result read-only and certify it."""
    return certify_v2_result(observe_v2_result(repo_root, tracked_paths))


def validate_v2_result_review(review: Any) -> dict[str, Any]:
    """Validate the review's shape and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(review, dict):
        return {"valid": False, "errors": ["review_not_a_dict"]}
    v = review
    if v.get("verdict") not in (VERDICT_V2R_REJECTED_ALL,
                                VERDICT_V2R_REVIEW_REJECTED,
                                VERDICT_V2R_BLOCKED):
        errors.append("bad_verdict")
    if v.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if v.get("edit_id") != EDIT_V2_ID:
        errors.append("edit_id_tampered")
    if tuple(v.get("checklist") or ()) != REVIEW_CHECKLIST:
        errors.append("checklist_tampered")
    if v.get("expected_risk_distances_bps") != EXPECTED_RISK_DISTANCES_BPS:
        errors.append("risk_distance_evidence_tampered")
    if v.get("minimum_required_bps") != EXPECTED_MINIMUM_REQUIRED_BPS:
        errors.append("minimum_bps_tampered")
    if tuple(v.get("honest_research_conclusion") or ()) != (
            HONEST_RESEARCH_CONCLUSION):
        errors.append("honest_conclusion_tampered")
    if tuple(v.get("forbidden") or ()) != FORBIDDEN:
        errors.append("forbidden_list_weakened")
    if v.get("replay_ready") is not False:
        errors.append("replay_ready_must_be_false_with_zero_survivors")
    if v.get("replay_authorized") is not False:
        errors.append("replay_can_never_be_authorized_here")
    if v.get("candidate_approved_for_paper_or_live") is not False:
        errors.append("paper_live_can_never_be_approved_here")
    if v.get("profitability_claim_permitted") is not False:
        errors.append("profitability_claim_can_never_be_permitted_here")
    results = v.get("checklist_results") or {}
    if v.get("verdict") == VERDICT_V2R_REJECTED_ALL:
        if v.get("blockers"):
            errors.append("certified_with_blockers")
        if set(results) != set(REVIEW_CHECKLIST) or not all(
                results.get(n) is True for n in REVIEW_CHECKLIST):
            errors.append("certified_without_full_passing_checklist")
    if v.get("verdict") in (VERDICT_V2R_REVIEW_REJECTED,
                            VERDICT_V2R_BLOCKED) and not v.get("blockers"):
        errors.append("non_certified_without_blockers")
    for key, want in (
        ("artifacts_remain_untracked_operational_evidence", True),
        ("v3_or_rejection_is_a_human_decision", True),
        ("this_review_changes_no_rules", True),
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
