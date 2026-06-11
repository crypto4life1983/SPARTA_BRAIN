"""SPARTA NY-Session FVG+CHOCH EXPANDED SAMPLE RE-DETECTION REVIEW
(READ-ONLY, REVIEW ONLY, RUNS NOTHING).

Certifies the one approved re-detection over the expanded 21-session sample
(2026-05-12 .. 2026-06-10) with edit V1 active: 619 labels, 377 eligible
fresh zones (past the 100+ target), and the lane's FIRST 7 ACCEPTED labels.
The 2026-06-10 day reproduced its edit-V1 result exactly (20 labels),
proving zero rule drift. replay_ready is True for the first time -- but
replay is NOT authorized: it remains behind its own separate human approval,
and nothing here computes PnL, scores, or optimizes.
"""

from __future__ import annotations

import hashlib as _hashlib
import json as _json
import pathlib as _pathlib
from typing import Any

from sparta_commander.ny_session_fvg_choch_additional_session_days_staged_candles_review import (
    BASELINE_PROTECTED_FILES,
)
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

EX_SCHEMA_VERSION = (
    "ny_session_fvg_choch_expanded_sample_redetection_review.v1")
EX_LABEL = ("SPARTA NY-Session FVG+CHOCH Expanded Sample Re-Detection "
            "Review (READ-ONLY, REVIEW ONLY, REPLAY STILL HUMAN-GATED)")
EX_MODE = "RESEARCH_ONLY"
VERDICT_EX_ACCEPTED = (
    "EXPANDED_REDETECTION_ACCEPTED_AWAITING_HUMAN_REPLAY_DECISION")
VERDICT_EX_REJECTED = "EXPANDED_REDETECTION_REJECTED"
VERDICT_EX_BLOCKED = "EXPANDED_REDETECTION_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_REVIEW_OF_EXPANDED_SAMPLE_ACCEPTED_LABELS"

LABELS_PATH = ("data/ny_fvg_choch/detector_labels/"
               "detector_labels_expanded_2026-05-12_2026-06-10.jsonl")
SUMMARY_PATH = ("data/ny_fvg_choch/detector_labels/"
                "redetection_summary_expanded_2026-05-12_2026-06-10.json")

EXPECTED_TOTAL_LABELS = 619
EXPECTED_ACCEPTED = 7
EXPECTED_ACCEPTED_SETUP_IDS = (
    "BTCUSD_20260609_editv1exp_setup05_touch1",
    "ETHUSD_20260513_editv1exp_setup01_touch2",
    "ETHUSD_20260515_editv1exp_setup02_touch2",
    "SOLUSD_20260513_editv1exp_setup02_touch1",
    "SOLUSD_20260520_editv1exp_setup02_touch1",
    "SOLUSD_20260526_editv1exp_setup01_touch1",
    "AVAXUSD_20260529_editv1exp_setup04_touch2",
)
EXPECTED_ACCEPTED_BY_SYMBOL = {"BTCUSD": 1, "ETHUSD": 2, "SOLUSD": 3,
                               "AVAXUSD": 1, "ARBUSD": 0, "XRPUSD": 0}
EXPECTED_BY_SYMBOL_TOTALS = {"BTCUSD": 111, "ETHUSD": 102, "SOLUSD": 101,
                             "AVAXUSD": 101, "ARBUSD": 111, "XRPUSD": 93}
EXPECTED_REJECTIONS = {"SETUP_REJECTED_MISSING_CHOCH": 388,
                       "SETUP_REJECTED_FIB_MISALIGNMENT": 211,
                       "SETUP_REJECTED_MISSING_LTF_FVG": 12,
                       "SETUP_REJECTED_MISSING_HTF_FVG": 1}
EXPECTED_CONTROLS = {"zones_with_session_touch": 5573,
                     "zones_filtered_stale_age": 4824,
                     "zones_filtered_mitigated": 372,
                     "zones_eligible_fresh": 377,
                     "touches_capped_beyond_limit": 715}
EXPECTED_SESSION_COUNT = 21
EXPECTED_2026_06_10_TOTAL = 20  # exact reproduction of the edit-V1 run
EXPECTED_COMPARISON = {
    "first_run_2026_06_10": {"labels": 259, "accepted": 0},
    "edit_v1_run_2026_06_10": {"labels": 20, "accepted": 0},
    "expanded_21_sessions": {"labels": 619, "accepted": 7}}
EXPECTED_LABELS_SHA256 = (
    "8283e72fed6d724670583d1906b089f337ab8718ac35cd154c743decb3472a79")

_PNL_FORBIDDEN_TOKENS = ("pnl", "profit", "replay_status", "score", "net_r",
                         "gross_r", "win_rate", "order", "api_key", "wallet",
                         "login")

REVIEW_CHECKLIST = (
    "labels_and_summary_present",
    "outputs_untracked_not_in_git_index",
    "edited_candidate_v1_active_no_drift",
    "stale_fvg_controls_active_and_fully_accounted",
    "every_label_has_29_field_schema_plus_authorizes_nothing",
    "every_status_in_closed_9_set",
    "totals_match_observed_run_619_and_7_accepted",
    "accepted_setup_ids_match_exactly",
    "session_day_2026_06_10_reproduced_edit_v1_result",
    "comparison_across_all_three_runs_recorded",
    "no_replay_pnl_or_scoring_fields",
    "baseline_and_prior_outputs_byte_identical",
    "labels_file_sha_pinned",
    "replay_gated_on_separate_human_approval",
)

RESEARCH_INTERPRETATION = (
    "first_7_accepted_labels_in_lane_history_replay_candidates_exist",
    "377_eligible_fresh_zones_exceeds_the_100_plus_target",
    "acceptance_rate_is_low_7_of_619_attempts_about_1_percent_consistent_with_a_strict_gate",
    "sol_and_eth_produced_the_cleanest_candidates_arb_and_xrp_produced_none",
    "2026_06_10_was_indeed_a_zero_day_zero_accepted_was_normal_variance_not_a_broken_detector",
    "next_honest_step_is_human_review_of_the_7_accepted_labels_then_a_separately_approved_fee_honest_replay",
)

FORBIDDEN = (
    "replay_runs", "pnl_calculation", "scoring_fields", "optimizer_runs",
    "rule_changes", "candidate_asset_changes",
    "locked_scorer_or_instruction_changes",
    "modifying_staged_candles", "modifying_prior_labels",
    "deleting_prior_outputs", "broker_exchange_credential_access",
    "order_endpoints", "paper_live_micro_live_authorization",
    "gate_unlocks",
)


def get_expanded_sample_review_label() -> str:
    return EX_LABEL


def observe_expanded_redetection(repo_root: Any,
                                 tracked_paths: Any = ()) -> dict[str, Any]:
    """READ-ONLY observation of the expanded-run outputs and data state."""
    root = _pathlib.Path(str(repo_root))
    labels_file = root / LABELS_PATH
    summary_file = root / SUMMARY_PATH
    observation: dict[str, Any] = {
        "labels_present": labels_file.is_file(),
        "summary_present": summary_file.is_file(),
        "labels": [], "summary": None, "labels_sha256": None,
        "tracked_output_paths": [str(p) for p in (tracked_paths or ())],
        "baseline_files_sha256": {},
    }
    if observation["labels_present"]:
        raw = labels_file.read_bytes()
        observation["labels_sha256"] = _hashlib.sha256(raw).hexdigest()
        for line in raw.decode("utf-8").splitlines():
            if line.strip():
                observation["labels"].append(_json.loads(line))
    if observation["summary_present"]:
        observation["summary"] = _json.loads(
            summary_file.read_text(encoding="utf-8"))
    for rel_path in BASELINE_PROTECTED_FILES:
        target = root / rel_path
        observation["baseline_files_sha256"][rel_path] = (
            _hashlib.sha256(target.read_bytes()).hexdigest()
            if target.is_file() else None)
    return observation


def certify_expanded_redetection(observation: Any) -> dict[str, Any]:
    """DETERMINISTIC certification of the expanded run. Pure."""
    review: dict[str, Any] = {
        "schema_version": EX_SCHEMA_VERSION, "label": EX_LABEL,
        "mode": EX_MODE, "lane": "crypto_d1_auto_research",
        "candidate_id": CANDIDATE_ID, "edit_id": EDIT_ID,
        "verdict": None, "blockers": [],
        "checklist": list(REVIEW_CHECKLIST), "checklist_results": {},
        "labels_total": 0, "accepted_total": 0,
        "accepted_setup_ids": [],
        "research_interpretation": list(RESEARCH_INTERPRETATION),
        "forbidden": list(FORBIDDEN),
        "replay_ready": False, "replay_authorized": False,
        "replay_requires_separate_human_approval": True,
        "previous_outputs_kept_on_record": True,
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
        review["verdict"] = VERDICT_EX_BLOCKED
        review["blockers"].append("observation_missing")
        return review
    o = observation
    if not o.get("labels_present") or not o.get("summary_present"):
        review["verdict"] = VERDICT_EX_BLOCKED
        review["blockers"].append("labels_or_summary_file_missing")
        return review

    labels = o.get("labels") or []
    summary = o.get("summary") or {}
    expected_keys = set(LABEL_REQUIRED_FIELDS) | {"label_authorizes_nothing"}
    r: dict[str, bool] = {}
    r["labels_and_summary_present"] = True
    r["outputs_untracked_not_in_git_index"] = not o.get(
        "tracked_output_paths")
    r["edited_candidate_v1_active_no_drift"] = (
        summary.get("edit_id") == EDIT_ID
        and summary.get("edited_candidate_parameters_active")
        == NEW_PARAMETERS
        and len(summary.get("session_dates") or ())
        == EXPECTED_SESSION_COUNT)
    controls = summary.get("stale_fvg_controls") or {}
    r["stale_fvg_controls_active_and_fully_accounted"] = (
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
    accepted_ids = []
    day_2026_06_10 = 0
    accepted_by_symbol = {s: 0 for s in EXPECTED_ACCEPTED_BY_SYMBOL}
    for x in labels:
        by_symbol[x.get("symbol")] = by_symbol.get(x.get("symbol"), 0) + 1
        if x.get("session_date") == "2026-06-10":
            day_2026_06_10 += 1
        status = x.get("detector_status")
        if status == "SETUP_LABEL_ACCEPTED_FOR_REPLAY_REVIEW":
            accepted_ids.append(x.get("setup_id"))
            if x.get("symbol") in accepted_by_symbol:
                accepted_by_symbol[x.get("symbol")] += 1
        else:
            rejections[status] = rejections.get(status, 0) + 1
    review["accepted_total"] = len(accepted_ids)
    review["accepted_setup_ids"] = sorted(accepted_ids)
    r["totals_match_observed_run_619_and_7_accepted"] = (
        len(labels) == EXPECTED_TOTAL_LABELS
        and len(accepted_ids) == EXPECTED_ACCEPTED
        and by_symbol == EXPECTED_BY_SYMBOL_TOTALS
        and rejections == EXPECTED_REJECTIONS
        and accepted_by_symbol == EXPECTED_ACCEPTED_BY_SYMBOL)
    r["accepted_setup_ids_match_exactly"] = (
        sorted(accepted_ids) == sorted(EXPECTED_ACCEPTED_SETUP_IDS))
    r["session_day_2026_06_10_reproduced_edit_v1_result"] = (
        day_2026_06_10 == EXPECTED_2026_06_10_TOTAL)
    r["comparison_across_all_three_runs_recorded"] = (
        summary.get("comparison") == EXPECTED_COMPARISON)
    clean = True
    for x in labels:
        for key in x:
            lowered = str(key).lower()
            if any(token in lowered for token in _PNL_FORBIDDEN_TOKENS):
                clean = False
    r["no_replay_pnl_or_scoring_fields"] = (
        bool(labels) and clean
        and summary.get("no_pnl_no_scoring_no_replay") is True
        and summary.get("labels_authorize_nothing") is True)
    r["baseline_and_prior_outputs_byte_identical"] = (
        o.get("baseline_files_sha256") == BASELINE_PROTECTED_FILES)
    r["labels_file_sha_pinned"] = (
        o.get("labels_sha256") == EXPECTED_LABELS_SHA256)
    r["replay_gated_on_separate_human_approval"] = (
        summary.get("replay_requires_separate_human_approval") is True
        and summary.get("replay_ready") is True)
    review["checklist_results"] = r
    failed = [name for name, ok in r.items() if not ok]
    if failed:
        review["verdict"] = VERDICT_EX_REJECTED
        review["blockers"].extend("check_failed:" + n for n in failed)
        return review
    # Accepted labels exist: replay_ready True, but NEVER authorized here.
    review["replay_ready"] = True
    review["verdict"] = VERDICT_EX_ACCEPTED
    return review


def build_expanded_redetection_review(repo_root: Any,
                                      tracked_paths: Any = ()) -> dict[str, Any]:
    """Observe the expanded-run outputs read-only and certify them."""
    return certify_expanded_redetection(
        observe_expanded_redetection(repo_root, tracked_paths))


def validate_expanded_redetection_review(review: Any) -> dict[str, Any]:
    """Validate the review's shape and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(review, dict):
        return {"valid": False, "errors": ["review_not_a_dict"]}
    v = review
    if v.get("verdict") not in (VERDICT_EX_ACCEPTED, VERDICT_EX_REJECTED,
                                VERDICT_EX_BLOCKED):
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
    if v.get("replay_authorized") is not False:
        errors.append("replay_can_never_be_authorized_by_this_review")
    results = v.get("checklist_results") or {}
    if v.get("verdict") == VERDICT_EX_ACCEPTED:
        if v.get("blockers"):
            errors.append("accepted_with_blockers")
        if set(results) != set(REVIEW_CHECKLIST) or not all(
                results.get(n) is True for n in REVIEW_CHECKLIST):
            errors.append("accepted_without_full_passing_checklist")
        if v.get("replay_ready") is not True:
            errors.append("accepted_run_must_report_replay_ready_true")
        if tuple(v.get("accepted_setup_ids") or ()) != tuple(
                sorted(EXPECTED_ACCEPTED_SETUP_IDS)):
            errors.append("accepted_setup_ids_tampered")
    else:
        if v.get("replay_ready") is not False:
            errors.append("non_accepted_run_cannot_be_replay_ready")
    if v.get("verdict") in (VERDICT_EX_REJECTED, VERDICT_EX_BLOCKED) \
            and not v.get("blockers"):
        errors.append("non_accepted_without_blockers")
    for key, want in (
        ("replay_requires_separate_human_approval", True),
        ("previous_outputs_kept_on_record", True),
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
