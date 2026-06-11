"""SPARTA NY-Session FVG+CHOCH RE-DETECTION WITH EDITED CANDIDATE V1
(READ-ONLY REVIEW OF THE ONE APPROVED RE-DETECTION PASS).

Certifies the re-detection run that applied the pushed mutable candidate
edit V1 (max_fvg_age_bars=24, require_fresh_unmitigated_15m_fvg=True,
max_zone_touches_before_invalidation=2) to the SAME staged candles:
259 -> 20 labels (239 junk attempts eliminated), still 0 accepted, prior
labels and staged candles byte-identical. replay_ready stays False -- with
zero accepted labels there is nothing to replay, and any replay would need
its own human approval anyway. Changes no rules, runs nothing.
"""

from __future__ import annotations

import hashlib as _hashlib
import json as _json
import pathlib as _pathlib
from typing import Any

from sparta_commander.ny_session_fvg_choch_detector_spec import (
    DETECTOR_STATUSES,
    LABEL_REQUIRED_FIELDS,
)
from sparta_commander.ny_session_fvg_choch_mutable_candidate_edit_v1 import (
    EDIT_ID,
    NEW_PARAMETERS,
)
from sparta_commander.ny_session_fvg_choch_strategy_spec_contract import (
    CANDIDATE_ID,
)

RD_SCHEMA_VERSION = (
    "ny_session_fvg_choch_redetection_with_edited_candidate.v1")
RD_LABEL = ("SPARTA NY-Session FVG+CHOCH Re-Detection With Edited Candidate "
            "V1 Review (READ-ONLY, REVIEW ONLY, RUNS NOTHING)")
RD_MODE = "RESEARCH_ONLY"
VERDICT_RD_ACCEPTED = "REDETECTION_V1_ACCEPTED_NO_REPLAY_READY"
VERDICT_RD_REJECTED = "REDETECTION_V1_REJECTED"
VERDICT_RD_BLOCKED = "REDETECTION_V1_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_DECISION_ON_NEXT_RESEARCH_STEP"

NEW_LABELS_PATH = ("data/ny_fvg_choch/detector_labels/"
                   "detector_labels_2026-06-10_edit_v1.jsonl")
SUMMARY_PATH = ("data/ny_fvg_choch/detector_labels/"
                "redetection_summary_2026-06-10_edit_v1.json")
PRIOR_LABELS_PATH = ("data/ny_fvg_choch/detector_labels/"
                     "detector_labels_2026-06-10.jsonl")
MANIFEST_PATH = "data/ny_fvg_choch/staged/manifest.txt"

EXPECTED_PREVIOUS = {"labels_total": 259, "accepted_total": 0}
EXPECTED_NEW_TOTAL = 20
EXPECTED_NEW_ACCEPTED = 0
EXPECTED_JUNK_REDUCTION = 239
EXPECTED_BY_SYMBOL = {"BTCUSD": 2, "ETHUSD": 2, "SOLUSD": 4,
                      "AVAXUSD": 4, "ARBUSD": 2, "XRPUSD": 6}
EXPECTED_REJECTIONS = {"SETUP_REJECTED_MISSING_CHOCH": 15,
                       "SETUP_REJECTED_FIB_MISALIGNMENT": 4,
                       "SETUP_REJECTED_MISSING_LTF_FVG": 1}
EXPECTED_CONTROLS = {"zones_with_session_touch": 259,
                     "zones_filtered_stale_age": 237,
                     "zones_filtered_mitigated": 11,
                     "zones_eligible_fresh": 11,
                     "touches_capped_beyond_limit": 52}
EXPECTED_MANIFEST_SHA256 = (
    "cbe83729cea90f233c257078063f0bd342baac64bef1a9a4ef64a6f9539de82e")
EXPECTED_PRIOR_LABELS_SHA256 = (
    "bd4241d8235cab57c013fd51661846fd583d871c4c33e0575c7768ea457795c5")

_PNL_REPLAY_FORBIDDEN_TOKENS = ("pnl", "profit", "replay_status", "score",
                                "net_r", "gross_r", "win_rate", "order",
                                "api_key", "wallet", "account", "login")

REVIEW_CHECKLIST = (
    "new_labels_and_summary_present",
    "outputs_untracked_not_in_git_index",
    "edited_candidate_asset_used",
    "stale_fvg_controls_active_and_accounted",
    "every_label_has_29_field_schema_plus_authorizes_nothing",
    "every_status_in_closed_9_set",
    "new_totals_match_observed_run",
    "comparison_to_previous_run_recorded",
    "no_replay_pnl_or_scoring_fields",
    "staged_manifest_sha_preserved",
    "prior_labels_sha_preserved",
    "replay_ready_false_with_zero_accepted",
)

RESEARCH_INTERPRETATION = (
    "stale_fvg_filtering_eliminated_239_of_259_attempts_92_percent_junk_reduction",
    "controls_accounted_for_every_zone_237_stale_11_mitigated_11_fresh",
    "still_zero_accepted_labels_so_nothing_is_replayable_yet",
    "one_session_day_is_a_small_sample_more_session_days_are_the_honest_next_lever",
)

FORBIDDEN = (
    "replay_runs", "scorer_runs", "optimizer_runs",
    "report_artifact_creation", "modifying_labels", "deleting_labels",
    "modifying_staged_candles", "network_retrieval",
    "broker_exchange_private_api_access", "credentials_or_api_keys",
    "account_wallet_login_access", "trading_endpoints_of_any_kind",
    "paper_live_micro_live_authorization", "gate_unlocks",
)


def get_redetection_review_label() -> str:
    return RD_LABEL


def observe_redetection(repo_root: Any,
                        tracked_paths: Any = ()) -> dict[str, Any]:
    """READ-ONLY observation of the re-detection outputs and data state."""
    root = _pathlib.Path(str(repo_root))
    labels_file = root / NEW_LABELS_PATH
    summary_file = root / SUMMARY_PATH
    observation: dict[str, Any] = {
        "labels_present": labels_file.is_file(),
        "summary_present": summary_file.is_file(),
        "labels": [], "summary": None,
        "tracked_output_paths": [str(p) for p in (tracked_paths or ())],
        "staged_manifest_sha256": None, "prior_labels_sha256": None,
    }
    if observation["labels_present"]:
        for line in labels_file.read_text(encoding="utf-8").splitlines():
            if line.strip():
                observation["labels"].append(_json.loads(line))
    if observation["summary_present"]:
        observation["summary"] = _json.loads(
            summary_file.read_text(encoding="utf-8"))
    manifest = root / MANIFEST_PATH
    if manifest.is_file():
        observation["staged_manifest_sha256"] = _hashlib.sha256(
            manifest.read_bytes()).hexdigest()
    prior = root / PRIOR_LABELS_PATH
    if prior.is_file():
        observation["prior_labels_sha256"] = _hashlib.sha256(
            prior.read_bytes()).hexdigest()
    return observation


def certify_redetection(observation: Any) -> dict[str, Any]:
    """DETERMINISTIC certification of the observed re-detection. Pure."""
    review: dict[str, Any] = {
        "schema_version": RD_SCHEMA_VERSION, "label": RD_LABEL,
        "mode": RD_MODE, "lane": "crypto_d1_auto_research",
        "candidate_id": CANDIDATE_ID, "edit_id": EDIT_ID,
        "verdict": None, "blockers": [],
        "checklist": list(REVIEW_CHECKLIST), "checklist_results": {},
        "labels_total": 0, "accepted_total": 0,
        "research_interpretation": list(RESEARCH_INTERPRETATION),
        "forbidden": list(FORBIDDEN),
        "replay_ready": False,
        "replay_requires_separate_human_approval": True,
        "previous_labels_kept_on_record": True,
        "outputs_remain_untracked_operational_data": True,
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
        review["verdict"] = VERDICT_RD_BLOCKED
        review["blockers"].append("observation_missing")
        return review
    o = observation
    if not o.get("labels_present") or not o.get("summary_present"):
        review["verdict"] = VERDICT_RD_BLOCKED
        review["blockers"].append("labels_or_summary_file_missing")
        return review

    labels = o.get("labels") or []
    summary = o.get("summary") or {}
    expected_keys = set(LABEL_REQUIRED_FIELDS) | {"label_authorizes_nothing"}
    r: dict[str, bool] = {}
    r["new_labels_and_summary_present"] = True
    r["outputs_untracked_not_in_git_index"] = not o.get(
        "tracked_output_paths")
    r["edited_candidate_asset_used"] = (
        summary.get("edit_id") == EDIT_ID
        and summary.get("edited_candidate_parameters_active")
        == NEW_PARAMETERS)
    controls = summary.get("stale_fvg_controls") or {}
    r["stale_fvg_controls_active_and_accounted"] = (
        controls == EXPECTED_CONTROLS
        and controls.get("zones_filtered_stale_age", 0)
        + controls.get("zones_filtered_mitigated", 0)
        + controls.get("zones_eligible_fresh", 0)
        == controls.get("zones_with_session_touch", -1))
    r["every_label_has_29_field_schema_plus_authorizes_nothing"] = bool(
        labels) and all(
        isinstance(x, dict) and set(x) == expected_keys
        and x.get("label_authorizes_nothing") is True
        and x.get("candidate_id") == CANDIDATE_ID for x in labels)
    r["every_status_in_closed_9_set"] = bool(labels) and all(
        x.get("detector_status") in DETECTOR_STATUSES for x in labels)
    review["labels_total"] = len(labels)
    by_symbol: dict[str, int] = {}
    rejections: dict[str, int] = {}
    accepted = 0
    for x in labels:
        by_symbol[x.get("symbol")] = by_symbol.get(x.get("symbol"), 0) + 1
        status = x.get("detector_status")
        if status == "SETUP_LABEL_ACCEPTED_FOR_REPLAY_REVIEW":
            accepted += 1
        else:
            rejections[status] = rejections.get(status, 0) + 1
    review["accepted_total"] = accepted
    r["new_totals_match_observed_run"] = (
        len(labels) == EXPECTED_NEW_TOTAL
        and accepted == EXPECTED_NEW_ACCEPTED
        and by_symbol == EXPECTED_BY_SYMBOL
        and rejections == EXPECTED_REJECTIONS)
    comparison = summary.get("comparison_to_previous_run") or {}
    r["comparison_to_previous_run_recorded"] = (
        comparison.get("previous_labels_total")
        == EXPECTED_PREVIOUS["labels_total"]
        and comparison.get("previous_accepted_total")
        == EXPECTED_PREVIOUS["accepted_total"]
        and comparison.get("new_labels_total") == EXPECTED_NEW_TOTAL
        and comparison.get("new_accepted_total") == EXPECTED_NEW_ACCEPTED
        and comparison.get("junk_label_reduction")
        == EXPECTED_JUNK_REDUCTION)
    clean = True
    for x in labels:
        for key in x:
            lowered = str(key).lower()
            if any(token in lowered
                   for token in _PNL_REPLAY_FORBIDDEN_TOKENS):
                clean = False
    r["no_replay_pnl_or_scoring_fields"] = (
        bool(labels) and clean
        and summary.get("no_pnl_no_scoring_no_replay") is True
        and summary.get("labels_authorize_nothing") is True)
    r["staged_manifest_sha_preserved"] = (
        o.get("staged_manifest_sha256") == EXPECTED_MANIFEST_SHA256
        and summary.get("staged_manifest_sha256")
        == EXPECTED_MANIFEST_SHA256)
    r["prior_labels_sha_preserved"] = (
        o.get("prior_labels_sha256") == EXPECTED_PRIOR_LABELS_SHA256
        and summary.get("prior_labels_sha256_after_run")
        == EXPECTED_PRIOR_LABELS_SHA256)
    r["replay_ready_false_with_zero_accepted"] = (
        summary.get("replay_ready") is False and accepted == 0
        and summary.get("replay_requires_separate_human_approval") is True)
    review["checklist_results"] = r
    failed = [name for name, ok in r.items() if not ok]
    if failed:
        review["verdict"] = VERDICT_RD_REJECTED
        review["blockers"].extend("check_failed:" + n for n in failed)
        return review
    review["replay_ready"] = False
    review["verdict"] = VERDICT_RD_ACCEPTED
    return review


def build_redetection_review(repo_root: Any,
                             tracked_paths: Any = ()) -> dict[str, Any]:
    """Observe the re-detection outputs read-only and certify them."""
    return certify_redetection(observe_redetection(repo_root, tracked_paths))


def validate_redetection_review(review: Any) -> dict[str, Any]:
    """Validate the review's shape and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(review, dict):
        return {"valid": False, "errors": ["review_not_a_dict"]}
    v = review
    if v.get("verdict") not in (VERDICT_RD_ACCEPTED, VERDICT_RD_REJECTED,
                                VERDICT_RD_BLOCKED):
        errors.append("bad_verdict")
    if v.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if v.get("edit_id") != EDIT_ID:
        errors.append("edit_id_tampered")
    if tuple(v.get("checklist") or ()) != REVIEW_CHECKLIST:
        errors.append("checklist_tampered")
    if tuple(v.get("research_interpretation") or ()) != (
            RESEARCH_INTERPRETATION):
        errors.append("research_interpretation_tampered")
    if tuple(v.get("forbidden") or ()) != FORBIDDEN:
        errors.append("forbidden_list_weakened")
    if v.get("replay_ready") is not False:
        errors.append("replay_ready_must_be_false_with_zero_accepted")
    results = v.get("checklist_results") or {}
    if v.get("verdict") == VERDICT_RD_ACCEPTED:
        if v.get("blockers"):
            errors.append("accepted_with_blockers")
        if set(results) != set(REVIEW_CHECKLIST) or not all(
                results.get(n) is True for n in REVIEW_CHECKLIST):
            errors.append("accepted_without_full_passing_checklist")
    if v.get("verdict") in (VERDICT_RD_REJECTED, VERDICT_RD_BLOCKED) \
            and not v.get("blockers"):
        errors.append("non_accepted_without_blockers")
    for key, want in (
        ("replay_requires_separate_human_approval", True),
        ("previous_labels_kept_on_record", True),
        ("outputs_remain_untracked_operational_data", True),
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
