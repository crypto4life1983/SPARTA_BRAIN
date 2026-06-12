"""SPARTA BREAKOUT-PULLBACK REAL-CANDLE DETECTOR LABELS REVIEW
(READ-ONLY, REVIEW ONLY, FREEZES THE EVIDENCE).

Candidate #2's first real-market result, frozen: 559 breakout attempts over
the staged 21-session sample, 105 ACCEPTED with every one clearing the
81 bps floor at label time (min 81.77 / median 114.48 / max 223.71 bps),
454 auditable rejections. The geometry thesis held on real data. replay
remains behind its own human gate; this review runs nothing, changes no
rules, and keeps candidate #1's rejection on record.
"""

from __future__ import annotations

import hashlib as _hashlib
import json as _json
import pathlib as _pathlib
from typing import Any

from sparta_commander.crypto_intraday_breakout_pullback_structure_detector_spec import (
    BP_DETECTOR_STATUSES,
    BP_LABEL_REQUIRED_FIELDS,
)
from sparta_commander.crypto_intraday_breakout_pullback_structure_strategy_spec_contract import (
    CANDIDATE_ID,
)
from sparta_commander.ny_session_fvg_choch_additional_session_days_staged_candles_review import (
    BASELINE_PROTECTED_FILES,
)

BPL_SCHEMA_VERSION = (
    "crypto_intraday_breakout_pullback_structure_real_candle_detector"
    "_labels_review.v1")
BPL_LABEL = ("SPARTA Breakout-Pullback Real-Candle Detector Labels Review "
             "(READ-ONLY, REVIEW ONLY, CHANGES NO RULES)")
BPL_MODE = "RESEARCH_ONLY"
VERDICT_BPL_ACCEPTED = (
    "BP_REAL_CANDLE_DETECTOR_LABELS_ACCEPTED_FOR_REPLAY_REVIEW")
VERDICT_BPL_REJECTED = "BP_REAL_CANDLE_DETECTOR_LABELS_REJECTED"
VERDICT_BPL_BLOCKED = "BP_REAL_CANDLE_DETECTOR_LABELS_BLOCKED"
NEXT_REQUIRED_ACTION = (
    "HUMAN_APPROVED_BP_FEE_HONEST_REPLAY_OF_105_ACCEPTED_LABELS")

LABELS_PATH = ("data/breakout_pullback/detector_labels/"
               "bp_detector_labels_2026-05-12_2026-06-10.jsonl")
SUMMARY_PATH = ("data/breakout_pullback/detector_labels/"
                "bp_detector_run_summary_2026-05-12_2026-06-10.json")
RUNNER_PATH = "tools/bp_real_candle_detection_once.py"
EXPECTED_LABELS_SHA256 = (
    "80a4b45ff266ce0e63b68214be81933fb9f4f108c8f7d8d4b17adfda7728b202")
EXPECTED_SUMMARY_SHA256 = (
    "9d569fd4c1aa9fe255201b725909550120bc989c23b5d2af771d9d337f13bf5f")

EXPECTED_TOTAL_LABELS = 559
EXPECTED_ACCEPTED = 105
EXPECTED_REJECTED = 454
EXPECTED_ACCEPTED_BY_SYMBOL = {"ARBUSD": 38, "AVAXUSD": 25, "ETHUSD": 15,
                               "SOLUSD": 14, "XRPUSD": 8, "BTCUSD": 5}
EXPECTED_REJECTIONS = {"BP_SETUP_REJECTED_NO_CONTINUATION": 169,
                       "BP_SETUP_REJECTED_RISK_BELOW_81_BPS": 150,
                       "BP_SETUP_REJECTED_FAILED_RETEST": 65,
                       "BP_SETUP_REJECTED_WEAK_BREAKOUT": 60,
                       "BP_SETUP_REJECTED_NO_PULLBACK": 10}
EXPECTED_RISK_MIN_BPS = 81.767807
EXPECTED_RISK_MEDIAN_BPS = 114.483206
EXPECTED_RISK_MAX_BPS = 223.713647
_RISK_TOLERANCE = 0.01
COST_FLOOR_BPS = 81
EXPECTED_STOP_MODELS = {"structural_swing": 68, "atr_1_5x": 37}
EXPECTED_DIRECTIONS = {"long": 42, "short": 63}

_PNL_FORBIDDEN_TOKENS = ("pnl", "profit", "replay_status", "score", "net_r",
                         "gross_r", "win_rate", "fill", "wallet", "login")

REVIEW_CHECKLIST = (
    "labels_and_summary_present_and_sha_pinned",
    "outputs_and_runner_untracked_not_in_git_index",
    "every_label_38_field_schema_candidate_id_authorizes_nothing",
    "every_status_in_closed_10_set",
    "totals_559_accepted_105_rejected_454",
    "accepted_by_symbol_match_observed_run",
    "rejection_counts_match_observed_run",
    "accepted_risk_min_median_max_match",
    "all_accepted_pass_81bps_floor",
    "stop_model_and_direction_split_match",
    "no_replay_pnl_or_scoring_fields",
    "replay_ready_only_with_separate_human_approval_flag",
    "staged_candles_byte_identical",
    "labels_only_run_and_candidate_1_preserved",
)

FORBIDDEN = (
    "replay_runs", "scorer_runs", "optimizer_runs",
    "report_artifact_creation", "modifying_labels", "deleting_labels",
    "modifying_staged_candles", "network_retrieval",
    "broker_exchange_private_api_access",
    "credentials_api_keys_login_account_wallet",
    "trading_endpoints_of_any_kind",
    "paper_live_micro_live_authorization", "gate_unlocks",
    "deleting_or_hiding_candidate_1_rejected_evidence",
)


def get_bp_labels_review_label() -> str:
    return BPL_LABEL


def observe_bp_detector_labels(repo_root: Any,
                               tracked_paths: Any = ()) -> dict[str, Any]:
    """READ-ONLY observation of the detector outputs and data state."""
    root = _pathlib.Path(str(repo_root))
    labels_file = root / LABELS_PATH
    summary_file = root / SUMMARY_PATH
    observation: dict[str, Any] = {
        "labels_present": labels_file.is_file(),
        "summary_present": summary_file.is_file(),
        "labels": [], "summary": None,
        "labels_sha256": None, "summary_sha256": None,
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
        raw = summary_file.read_bytes()
        observation["summary_sha256"] = _hashlib.sha256(raw).hexdigest()
        observation["summary"] = _json.loads(raw.decode("utf-8"))
    for rel_path in BASELINE_PROTECTED_FILES:
        target = root / rel_path
        observation["baseline_files_sha256"][rel_path] = (
            _hashlib.sha256(target.read_bytes()).hexdigest()
            if target.is_file() else None)
    return observation


def certify_bp_detector_labels(observation: Any) -> dict[str, Any]:
    """DETERMINISTIC certification of observed detector outputs. Pure."""
    review: dict[str, Any] = {
        "schema_version": BPL_SCHEMA_VERSION, "label": BPL_LABEL,
        "mode": BPL_MODE, "lane": "crypto_d1_auto_research",
        "candidate_id": CANDIDATE_ID, "verdict": None, "blockers": [],
        "checklist": list(REVIEW_CHECKLIST), "checklist_results": {},
        "labels_total": 0, "accepted_total": 0,
        "accepted_risk_min_bps": None, "accepted_risk_median_bps": None,
        "accepted_risk_max_bps": None,
        "forbidden": list(FORBIDDEN),
        "replay_ready": False, "replay_authorized": False,
        "replay_requires_separate_human_approval": True,
        "candidate_1_evidence_kept_on_record": True,
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
        review["verdict"] = VERDICT_BPL_BLOCKED
        review["blockers"].append("observation_missing")
        return review
    o = observation
    if not o.get("labels_present") or not o.get("summary_present"):
        review["verdict"] = VERDICT_BPL_BLOCKED
        review["blockers"].append("labels_or_summary_file_missing")
        return review

    labels = o.get("labels") or []
    summary = o.get("summary") or {}
    expected_keys = set(BP_LABEL_REQUIRED_FIELDS)
    r: dict[str, bool] = {}
    r["labels_and_summary_present_and_sha_pinned"] = (
        o.get("labels_sha256") == EXPECTED_LABELS_SHA256
        and o.get("summary_sha256") == EXPECTED_SUMMARY_SHA256)
    r["outputs_and_runner_untracked_not_in_git_index"] = not o.get(
        "tracked_output_paths")
    r["every_label_38_field_schema_candidate_id_authorizes_nothing"] = bool(
        labels) and all(
        isinstance(x, dict) and set(x) == expected_keys
        and x.get("candidate_id") == CANDIDATE_ID
        and x.get("label_authorizes_nothing") is True for x in labels)
    r["every_status_in_closed_10_set"] = bool(labels) and all(
        x.get("detector_status") in BP_DETECTOR_STATUSES for x in labels)
    review["labels_total"] = len(labels)
    accepted = [x for x in labels if x.get("detector_status")
                == "BP_SETUP_LABEL_ACCEPTED_FOR_REPLAY_REVIEW"]
    review["accepted_total"] = len(accepted)
    rejections: dict[str, int] = {}
    accepted_by_symbol: dict[str, int] = {}
    for x in labels:
        status = x.get("detector_status")
        if status == "BP_SETUP_LABEL_ACCEPTED_FOR_REPLAY_REVIEW":
            accepted_by_symbol[x.get("symbol")] = (
                accepted_by_symbol.get(x.get("symbol"), 0) + 1)
        else:
            rejections[status] = rejections.get(status, 0) + 1
    r["totals_559_accepted_105_rejected_454"] = (
        len(labels) == EXPECTED_TOTAL_LABELS
        and len(accepted) == EXPECTED_ACCEPTED
        and len(labels) - len(accepted) == EXPECTED_REJECTED)
    r["accepted_by_symbol_match_observed_run"] = (
        accepted_by_symbol == EXPECTED_ACCEPTED_BY_SYMBOL)
    r["rejection_counts_match_observed_run"] = (
        rejections == EXPECTED_REJECTIONS)
    risks = sorted(x.get("risk_distance_bps") for x in accepted
                   if isinstance(x.get("risk_distance_bps"), (int, float)))
    if len(risks) == len(accepted) and risks:
        review["accepted_risk_min_bps"] = risks[0]
        review["accepted_risk_median_bps"] = risks[len(risks) // 2]
        review["accepted_risk_max_bps"] = risks[-1]
        r["accepted_risk_min_median_max_match"] = (
            abs(risks[0] - EXPECTED_RISK_MIN_BPS) < _RISK_TOLERANCE
            and abs(risks[len(risks) // 2] - EXPECTED_RISK_MEDIAN_BPS)
            < _RISK_TOLERANCE
            and abs(risks[-1] - EXPECTED_RISK_MAX_BPS) < _RISK_TOLERANCE)
    else:
        r["accepted_risk_min_median_max_match"] = False
    r["all_accepted_pass_81bps_floor"] = bool(accepted) and all(
        isinstance(x.get("risk_distance_bps"), (int, float))
        and x["risk_distance_bps"] >= COST_FLOOR_BPS
        and x.get("cost_floor_pass") is True
        and x.get("cost_floor_bps") == COST_FLOOR_BPS for x in accepted)
    stop_models: dict[str, int] = {}
    directions: dict[str, int] = {}
    for x in accepted:
        stop_models[x.get("stop_model")] = (
            stop_models.get(x.get("stop_model"), 0) + 1)
        directions[x.get("direction")] = (
            directions.get(x.get("direction"), 0) + 1)
    r["stop_model_and_direction_split_match"] = (
        stop_models == EXPECTED_STOP_MODELS
        and directions == EXPECTED_DIRECTIONS)
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
    r["replay_ready_only_with_separate_human_approval_flag"] = (
        summary.get("replay_ready") is True
        and summary.get("replay_requires_separate_human_approval") is True)
    r["staged_candles_byte_identical"] = (
        o.get("baseline_files_sha256") == BASELINE_PROTECTED_FILES)
    try:
        from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
            REJECTION_REASON, REJECTION_STATUS)
        candidate_1_ok = (REJECTION_STATUS == "REJECTED_KEPT_ON_RECORD"
                          and REJECTION_REASON
                          == "COST_NON_VIABLE_RISK_GEOMETRY")
    except ImportError:
        candidate_1_ok = False
    r["labels_only_run_and_candidate_1_preserved"] = (
        candidate_1_ok
        and summary.get("candidate_id") == CANDIDATE_ID
        and summary.get("accepted_total") == len(accepted)
        and summary.get("labels_total") == len(labels))
    review["checklist_results"] = r
    failed = [name for name, ok in r.items() if not ok]
    if failed:
        review["verdict"] = VERDICT_BPL_REJECTED
        review["blockers"].extend("check_failed:" + n for n in failed)
        return review
    review["replay_ready"] = True
    review["verdict"] = VERDICT_BPL_ACCEPTED
    return review


def build_bp_detector_labels_review(repo_root: Any,
                                    tracked_paths: Any = ()) -> dict[str, Any]:
    """Observe the detector outputs read-only and certify them."""
    return certify_bp_detector_labels(
        observe_bp_detector_labels(repo_root, tracked_paths))


def validate_bp_detector_labels_review(review: Any) -> dict[str, Any]:
    """Validate the review's shape and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(review, dict):
        return {"valid": False, "errors": ["review_not_a_dict"]}
    v = review
    if v.get("verdict") not in (VERDICT_BPL_ACCEPTED, VERDICT_BPL_REJECTED,
                                VERDICT_BPL_BLOCKED):
        errors.append("bad_verdict")
    if v.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if tuple(v.get("checklist") or ()) != REVIEW_CHECKLIST:
        errors.append("checklist_tampered")
    if tuple(v.get("forbidden") or ()) != FORBIDDEN:
        errors.append("forbidden_list_weakened")
    if v.get("replay_authorized") is not False:
        errors.append("replay_can_never_be_authorized_by_this_review")
    results = v.get("checklist_results") or {}
    if v.get("verdict") == VERDICT_BPL_ACCEPTED:
        if v.get("blockers"):
            errors.append("accepted_with_blockers")
        if set(results) != set(REVIEW_CHECKLIST) or not all(
                results.get(n) is True for n in REVIEW_CHECKLIST):
            errors.append("accepted_without_full_passing_checklist")
        if v.get("replay_ready") is not True:
            errors.append("accepted_run_must_report_replay_ready_true")
        if v.get("accepted_total") != EXPECTED_ACCEPTED:
            errors.append("accepted_with_wrong_count")
    else:
        if v.get("replay_ready") is not False:
            errors.append("non_accepted_run_cannot_be_replay_ready")
    if v.get("verdict") in (VERDICT_BPL_REJECTED, VERDICT_BPL_BLOCKED) \
            and not v.get("blockers"):
        errors.append("non_accepted_without_blockers")
    for key, want in (
        ("replay_requires_separate_human_approval", True),
        ("candidate_1_evidence_kept_on_record", True),
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
