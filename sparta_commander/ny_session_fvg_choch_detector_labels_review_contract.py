"""SPARTA NY-Session FVG+CHOCH DETECTOR LABELS REVIEW (READ-ONLY).

The human-review contract over the one detector run on real staged candles:
it READS the label JSONL and run summary, re-validates every label against
the pushed 29-field schema and closed 9-status set, checks the exact
observed distribution (259 labels, 0 accepted), re-confirms the staged
candles are byte-identical and still accepted, and surfaces the research
interpretation -- zero accepted labels means NO replay yet, and the high
rejection count points at a mutable-candidate edit, not a detector bug.
This review changes no rules: any rule change goes through the mutable
candidate asset path under its own human approval, never the locked
scorer/instructions.
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
from sparta_commander.ny_session_fvg_choch_real_candle_staged_files_review_contract import (
    VERDICT_SR_ACCEPTED as STAGED_FILES_ACCEPTED,
    build_staged_files_review,
)
from sparta_commander.ny_session_fvg_choch_strategy_spec_contract import (
    CANDIDATE_ID,
)

DL_SCHEMA_VERSION = "ny_session_fvg_choch_detector_labels_review.v1"
DL_LABEL = ("SPARTA NY-Session FVG+CHOCH Detector Labels Review "
            "(READ-ONLY, REVIEW ONLY, CHANGES NO RULES)")
DL_MODE = "RESEARCH_ONLY"
VERDICT_DL_NO_REPLAY = "DETECTOR_LABELS_ACCEPTED_NO_REPLAY_READY"
VERDICT_DL_EDIT_RECOMMENDED = (
    "DETECTOR_LABELS_ACCEPTED_WITH_MUTABLE_CANDIDATE_EDIT_RECOMMENDED")
VERDICT_DL_REJECTED = "DETECTOR_LABELS_REJECTED"
VERDICT_DL_BLOCKED = "DETECTOR_LABELS_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_DECISION_ON_MUTABLE_CANDIDATE_EDIT"

LABELS_PATH = "data/ny_fvg_choch/detector_labels/detector_labels_2026-06-10.jsonl"
SUMMARY_PATH = ("data/ny_fvg_choch/detector_labels/"
                "detector_run_summary_2026-06-10.json")
EXPECTED_TOTAL_LABELS = 259
EXPECTED_ACCEPTED = 0
EXPECTED_BY_SYMBOL = {"BTCUSD": 52, "ETHUSD": 23, "SOLUSD": 41,
                      "AVAXUSD": 43, "ARBUSD": 60, "XRPUSD": 40}
EXPECTED_REJECTIONS = {"SETUP_REJECTED_MISSING_CHOCH": 255,
                       "SETUP_REJECTED_FIB_MISALIGNMENT": 3,
                       "SETUP_REJECTED_MISSING_LTF_FVG": 1}
EXPECTED_STAGED_MANIFEST_SHA256 = (
    "cbe83729cea90f233c257078063f0bd342baac64bef1a9a4ef64a6f9539de82e")

_PNL_REPLAY_FORBIDDEN_TOKENS = ("pnl", "profit", "replay", "score", "net_r",
                                "gross_r", "win_rate", "order", "api_key",
                                "wallet", "account", "login")

REVIEW_CHECKLIST = (
    "labels_and_summary_present",
    "outputs_untracked_not_in_git_index",
    "every_label_has_29_field_schema_plus_authorizes_nothing",
    "every_label_candidate_id_correct",
    "every_status_in_closed_9_set",
    "total_labels_259",
    "labels_by_symbol_match_observed_run",
    "accepted_labels_zero",
    "rejection_counts_match_observed_run",
    "no_replay_pnl_or_scoring_fields_in_labels",
    "summary_records_no_pnl_no_scoring_no_replay",
    "staged_candles_byte_identical_and_still_accepted",
)

RESEARCH_INTERPRETATION = (
    "zero_accepted_labels_means_no_replay_should_run_yet",
    "detector_appears_spec_faithful_but_may_over_trigger_stale_15m_fvg_zones",
    "high_rejection_count_suggests_candidate_asset_edit_not_detector_bug_by_default",
)

RECOMMENDED_MUTABLE_CANDIDATE_EDITS = (
    "add_max_fvg_age_bars",
    "require_fresh_unmitigated_15m_fvg",
    "tighten_or_revise_htf_context_touch_logic",
    "revise_choch_watch_window",
    "review_fib_0618_tolerance",
    "add_max_zone_touches_before_invalidation",
)

EDIT_PATH_RULE = ("any_rule_change_goes_through_the_mutable_candidate_asset_"
                  "path_with_human_approval_never_locked_scorer_or_"
                  "locked_instructions")

FORBIDDEN = (
    "replay_runs", "scorer_runs", "optimizer_runs",
    "report_artifact_creation", "modifying_labels", "deleting_labels",
    "modifying_staged_candles", "network_retrieval",
    "broker_exchange_private_api_access", "credentials_or_api_keys",
    "account_wallet_login_access", "trading_endpoints_of_any_kind",
    "paper_live_micro_live_authorization", "gate_unlocks",
)


def get_detector_labels_review_label() -> str:
    return DL_LABEL


def observe_detector_labels(repo_root: Any,
                            tracked_paths: Any = ()) -> dict[str, Any]:
    """READ-ONLY observation of the detector outputs and staged-set state.
    tracked_paths = git index listing for the detector_labels folder."""
    root = _pathlib.Path(str(repo_root))
    labels_file = root / LABELS_PATH
    summary_file = root / SUMMARY_PATH
    observation: dict[str, Any] = {
        "labels_present": labels_file.is_file(),
        "summary_present": summary_file.is_file(),
        "labels": [], "summary": None,
        "tracked_label_paths": [str(p) for p in (tracked_paths or ())],
        "staged_review_verdict": None, "staged_manifest_sha256": None,
    }
    if observation["labels_present"]:
        for line in labels_file.read_text(encoding="utf-8").splitlines():
            if line.strip():
                observation["labels"].append(_json.loads(line))
    if observation["summary_present"]:
        observation["summary"] = _json.loads(
            summary_file.read_text(encoding="utf-8"))
    staged_review = build_staged_files_review(repo_root, tracked_paths=[])
    observation["staged_review_verdict"] = staged_review.get("verdict")
    manifest = root / "data/ny_fvg_choch/staged/manifest.txt"
    if manifest.is_file():
        observation["staged_manifest_sha256"] = _hashlib.sha256(
            manifest.read_bytes()).hexdigest()
    return observation


def certify_detector_labels(observation: Any) -> dict[str, Any]:
    """DETERMINISTIC certification of observed detector outputs. Pure."""
    review: dict[str, Any] = {
        "schema_version": DL_SCHEMA_VERSION, "label": DL_LABEL,
        "mode": DL_MODE, "lane": "crypto_d1_auto_research",
        "candidate_id": CANDIDATE_ID, "verdict": None, "blockers": [],
        "checklist": list(REVIEW_CHECKLIST), "checklist_results": {},
        "labels_total": 0, "accepted_total": 0,
        "research_interpretation": list(RESEARCH_INTERPRETATION),
        "recommended_mutable_candidate_edits": [],
        "edit_path_rule": EDIT_PATH_RULE,
        "this_review_changes_no_rules": True,
        "replay_ready": False,
        "forbidden": list(FORBIDDEN),
        "label_outputs_remain_untracked_operational_data": True,
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
        review["verdict"] = VERDICT_DL_BLOCKED
        review["blockers"].append("observation_missing")
        return review
    o = observation
    if not o.get("labels_present") or not o.get("summary_present"):
        review["verdict"] = VERDICT_DL_BLOCKED
        review["blockers"].append("labels_or_summary_file_missing")
        return review

    labels = o.get("labels") or []
    summary = o.get("summary") or {}
    expected_keys = set(LABEL_REQUIRED_FIELDS) | {"label_authorizes_nothing"}
    r: dict[str, bool] = {}
    r["labels_and_summary_present"] = True
    r["outputs_untracked_not_in_git_index"] = not o.get(
        "tracked_label_paths")
    r["every_label_has_29_field_schema_plus_authorizes_nothing"] = bool(
        labels) and all(
        isinstance(x, dict) and set(x) == expected_keys
        and x.get("label_authorizes_nothing") is True for x in labels)
    r["every_label_candidate_id_correct"] = bool(labels) and all(
        x.get("candidate_id") == CANDIDATE_ID for x in labels)
    r["every_status_in_closed_9_set"] = bool(labels) and all(
        x.get("detector_status") in DETECTOR_STATUSES for x in labels)
    review["labels_total"] = len(labels)
    r["total_labels_259"] = len(labels) == EXPECTED_TOTAL_LABELS
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
    r["labels_by_symbol_match_observed_run"] = by_symbol == EXPECTED_BY_SYMBOL
    r["accepted_labels_zero"] = accepted == EXPECTED_ACCEPTED
    r["rejection_counts_match_observed_run"] = (
        rejections == EXPECTED_REJECTIONS)
    clean = True
    for x in labels:
        for key in x:
            lowered = str(key).lower()
            if any(token in lowered
                   for token in _PNL_REPLAY_FORBIDDEN_TOKENS):
                clean = False
    r["no_replay_pnl_or_scoring_fields_in_labels"] = bool(labels) and clean
    r["summary_records_no_pnl_no_scoring_no_replay"] = (
        summary.get("no_pnl_no_scoring_no_replay") is True
        and summary.get("labels_authorize_nothing") is True
        and summary.get("labels_total") == len(labels)
        and summary.get("accepted_total") == accepted)
    r["staged_candles_byte_identical_and_still_accepted"] = (
        o.get("staged_review_verdict") == STAGED_FILES_ACCEPTED
        and o.get("staged_manifest_sha256")
        == EXPECTED_STAGED_MANIFEST_SHA256)
    review["checklist_results"] = r
    failed = [name for name, ok in r.items() if not ok]
    if failed:
        review["verdict"] = VERDICT_DL_REJECTED
        review["blockers"].extend("check_failed:" + n for n in failed)
        return review
    # All checks pass. Zero accepted labels => replay must NOT run yet.
    review["replay_ready"] = False
    missing_choch = rejections.get("SETUP_REJECTED_MISSING_CHOCH", 0)
    if accepted == 0 and missing_choch * 2 >= len(labels):
        review["recommended_mutable_candidate_edits"] = list(
            RECOMMENDED_MUTABLE_CANDIDATE_EDITS)
        review["verdict"] = VERDICT_DL_EDIT_RECOMMENDED
    else:
        review["verdict"] = VERDICT_DL_NO_REPLAY
    return review


def build_detector_labels_review(repo_root: Any,
                                 tracked_paths: Any = ()) -> dict[str, Any]:
    """Observe the detector outputs read-only and certify them."""
    return certify_detector_labels(
        observe_detector_labels(repo_root, tracked_paths))


def validate_detector_labels_review(review: Any) -> dict[str, Any]:
    """Validate the review's shape and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(review, dict):
        return {"valid": False, "errors": ["review_not_a_dict"]}
    v = review
    if v.get("verdict") not in (VERDICT_DL_NO_REPLAY,
                                VERDICT_DL_EDIT_RECOMMENDED,
                                VERDICT_DL_REJECTED, VERDICT_DL_BLOCKED):
        errors.append("bad_verdict")
    if v.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if tuple(v.get("checklist") or ()) != REVIEW_CHECKLIST:
        errors.append("checklist_tampered")
    if tuple(v.get("research_interpretation") or ()) != (
            RESEARCH_INTERPRETATION):
        errors.append("research_interpretation_tampered")
    if v.get("edit_path_rule") != EDIT_PATH_RULE:
        errors.append("edit_path_rule_tampered")
    if tuple(v.get("forbidden") or ()) != FORBIDDEN:
        errors.append("forbidden_list_weakened")
    if v.get("replay_ready") is not False:
        errors.append("replay_ready_must_be_false_with_zero_accepted")
    results = v.get("checklist_results") or {}
    if v.get("verdict") in (VERDICT_DL_NO_REPLAY,
                            VERDICT_DL_EDIT_RECOMMENDED):
        if v.get("blockers"):
            errors.append("accepted_with_blockers")
        if set(results) != set(REVIEW_CHECKLIST) or not all(
                results.get(n) is True for n in REVIEW_CHECKLIST):
            errors.append("accepted_without_full_passing_checklist")
    if v.get("verdict") == VERDICT_DL_EDIT_RECOMMENDED and tuple(
            v.get("recommended_mutable_candidate_edits") or ()) != (
            RECOMMENDED_MUTABLE_CANDIDATE_EDITS):
        errors.append("edit_recommendations_tampered")
    if v.get("verdict") in (VERDICT_DL_REJECTED, VERDICT_DL_BLOCKED) \
            and not v.get("blockers"):
        errors.append("non_accepted_without_blockers")
    for key, want in (
        ("this_review_changes_no_rules", True),
        ("label_outputs_remain_untracked_operational_data", True),
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
