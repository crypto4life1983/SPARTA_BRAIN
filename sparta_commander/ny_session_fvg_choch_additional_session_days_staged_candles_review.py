"""SPARTA NY-Session FVG+CHOCH ADDITIONAL SESSION DAYS STAGED CANDLES
REVIEW (READ-ONLY, SAMPLE EXPANSION RULES ONLY).

After edit V1 cut 259 attempts to 20 with 0 accepted, the honest next lever
is MORE DATA, not looser rules. This contract defines how the sample is
expanded beyond 2026-06-10: same approved no-auth public source pattern,
same schema, append-only staging that can never rewrite or delete the
baseline candles, labels, or manifests -- and a minimum number of new NY
session days before the next human-approved re-detection. Rules, candidate
asset, locked instructions, and locked scorer are all untouched. Nothing
fetches, stages, detects, replays, or scores here.
"""

from __future__ import annotations

import datetime as _dt
import hashlib as _hashlib
import pathlib as _pathlib
from typing import Any

from sparta_commander.ny_session_fvg_choch_mutable_candidate_edit_v1 import (
    VERDICT_ME_READY,
    build_mutable_candidate_edit_v1,
    validate_mutable_candidate_edit_v1,
)
from sparta_commander.ny_session_fvg_choch_real_candle_staging_plan import (
    REQUIRED_CANDLE_FIELDS,
    REQUIRED_SYMBOLS,
    REQUIRED_TIMEFRAMES,
    SESSION_COVERAGE,
)
from sparta_commander.ny_session_fvg_choch_strategy_spec_contract import (
    CANDIDATE_ID,
)

AD_SCHEMA_VERSION = (
    "ny_session_fvg_choch_additional_session_days_staged_candles_review.v1")
AD_LABEL = ("SPARTA NY-Session FVG+CHOCH Additional Session Days Staged "
            "Candles Review (READ-ONLY, APPEND-ONLY RULES, STAGES NOTHING)")
AD_MODE = "RESEARCH_ONLY"
VERDICT_AD_READY = "NY_FVG_CHOCH_ADDITIONAL_SESSION_DAYS_REVIEW_READY"
VERDICT_AD_BLOCKED = "NY_FVG_CHOCH_ADDITIONAL_SESSION_DAYS_REVIEW_BLOCKED"
NEXT_REQUIRED_ACTION = (
    "HUMAN_RUN_APPROVAL_FOR_ADDITIONAL_SESSION_DAYS_STAGING")

APPROVED_SOURCE_CATEGORY = "no_auth_public_historical_endpoint_human_approved"
EXISTING_SESSION_DATES = ("2026-06-10",)
MIN_ADDITIONAL_SESSION_DAYS = 10
RECOMMENDED_ADDITIONAL_SESSION_DAYS = 20
TARGET_ELIGIBLE_FRESH_ZONES_BEFORE_JUDGING = 100

# Byte-identity baseline: these operational files may NEVER change.
BASELINE_PROTECTED_FILES = {
    "data/ny_fvg_choch/staged/manifest.txt":
        "cbe83729cea90f233c257078063f0bd342baac64bef1a9a4ef64a6f9539de82e",
    "data/ny_fvg_choch/detector_labels/detector_labels_2026-06-10.jsonl":
        "bd4241d8235cab57c013fd51661846fd583d871c4c33e0575c7768ea457795c5",
    "data/ny_fvg_choch/detector_labels/"
    "detector_labels_2026-06-10_edit_v1.jsonl":
        "fcd45a646fb1520d6fc8d71cade4023778635df95c2d33d083cd453e04d5a50d",
    "data/ny_fvg_choch/detector_labels/"
    "detector_run_summary_2026-06-10.json":
        "c2fafdcdfa37f8faa0e72836423d2973dfb653c3ec8e6153ede10e5deb60e7bf",
    "data/ny_fvg_choch/detector_labels/"
    "redetection_summary_2026-06-10_edit_v1.json":
        "b9842f7b6b2f47c0e76a4c3bf90b33d94c488bcacb0838234548e6fbd4dd7f58",
}

APPEND_ONLY_RULES = (
    "existing_staged_csvs_and_manifest_are_never_rewritten_or_deleted",
    "each_new_staging_batch_writes_new_files_plus_its_own_new_manifest_file",
    "prior_label_files_and_summaries_are_never_modified_or_deleted",
    "new_session_dates_must_not_duplicate_already_staged_dates",
    "exclusive_create_only_no_overwrites",
    "manifest_sha_tracking_every_batch_records_filename_sha256_row_count",
)

SAMPLE_EXPANSION_QUESTIONS = (
    "is_zero_accepted_normal_or_was_2026_06_10_one_quiet_misaligned_day",
    "how_many_fresh_15m_zones_appear_over_many_sessions",
    "how_often_do_choch_plus_ltf_fvg_plus_fib_alignment_co_occur",
    "which_symbols_produce_the_cleanest_candidates",
)

FORBIDDEN = (
    "detector_rule_changes", "mutable_candidate_asset_changes",
    "locked_instructions_or_scorer_changes", "replay_runs",
    "pnl_calculation", "scoring_fields", "optimizer_runs",
    "automatic_detector_runs", "mutation_of_prior_staged_candles",
    "mutation_of_prior_labels", "deletion_of_prior_outputs",
    "broker_exchange_credential_access", "order_endpoints",
    "auto_promotion", "paper_live_micro_live_authorization", "gate_unlocks",
)


def get_additional_session_days_review_label() -> str:
    return AD_LABEL


def validate_additional_staging_proposal(proposal: Any) -> dict[str, Any]:
    """Pure rule check of ONE proposed sample-expansion batch. Approvable
    here still requires the human run approval before anything is staged."""
    errors: list[str] = []
    if not isinstance(proposal, dict):
        return {"approvable": False, "errors": ["proposal_not_a_dict"],
                "human_run_approval_still_required": True}
    dates = proposal.get("session_dates")
    if not isinstance(dates, (list, tuple)) or not dates:
        errors.append("session_dates_missing_or_empty")
    else:
        parsed = []
        for value in dates:
            try:
                parsed.append(_dt.date.fromisoformat(str(value)))
            except ValueError:
                errors.append("invalid_session_date:" + str(value))
        if len(set(dates)) != len(dates):
            errors.append("duplicate_session_dates_in_proposal")
        for existing in EXISTING_SESSION_DATES:
            if existing in [str(d) for d in dates]:
                errors.append("duplicates_already_staged_session_day:"
                              + existing)
        if len(dates) < MIN_ADDITIONAL_SESSION_DAYS:
            errors.append("too_few_session_days_minimum_%d"
                          % MIN_ADDITIONAL_SESSION_DAYS)
    if tuple(proposal.get("symbols") or ()) != REQUIRED_SYMBOLS:
        errors.append("symbols_mismatch_with_staging_plan")
    if tuple(proposal.get("timeframes") or ()) != REQUIRED_TIMEFRAMES:
        errors.append("timeframes_mismatch_with_staging_plan")
    if proposal.get("source_category") != APPROVED_SOURCE_CATEGORY:
        errors.append("source_category_not_approved")
    if tuple(proposal.get("output_fields") or ()) != REQUIRED_CANDLE_FIELDS:
        errors.append("schema_incompatible_with_staging_plan")
    if proposal.get("session_coverage") != SESSION_COVERAGE:
        errors.append("session_coverage_missing_or_wrong")
    for flag, want in (("uses_same_approved_fetch_pattern", True),
                       ("append_only", True),
                       ("mutates_prior_staged_files", False),
                       ("mutates_prior_labels", False),
                       ("deletes_prior_outputs", False),
                       ("runs_detector_automatically", False),
                       ("runs_replay", False),
                       ("changes_detector_rules", False),
                       ("changes_candidate_asset", False)):
        if proposal.get(flag) is not want:
            errors.append("rule_flag_wrong:" + flag)
    return {"approvable": not errors, "errors": errors,
            "human_run_approval_still_required": True}


def observe_baseline_integrity(repo_root: Any) -> dict[str, Any]:
    """READ-ONLY: hash every protected baseline file on disk."""
    root = _pathlib.Path(str(repo_root))
    observed: dict[str, Any] = {}
    for rel_path in BASELINE_PROTECTED_FILES:
        target = root / rel_path
        observed[rel_path] = (_hashlib.sha256(target.read_bytes()).hexdigest()
                              if target.is_file() else None)
    return observed


def verify_append_only_integrity(observed: Any) -> dict[str, Any]:
    """Pure: every protected file must exist and be byte-identical."""
    errors: list[str] = []
    if not isinstance(observed, dict):
        return {"intact": False, "errors": ["observation_not_a_dict"]}
    for rel_path, expected in BASELINE_PROTECTED_FILES.items():
        actual = observed.get(rel_path)
        if actual is None:
            errors.append("protected_file_missing_or_deleted:" + rel_path)
        elif actual != expected:
            errors.append("protected_file_mutated:" + rel_path)
    return {"intact": not errors, "errors": errors}


def build_additional_session_days_review() -> dict[str, Any]:
    """Assemble the sample-expansion contract, gated on the READY edit V1.
    Pure; stages nothing."""
    record: dict[str, Any] = {
        "schema_version": AD_SCHEMA_VERSION, "label": AD_LABEL,
        "mode": AD_MODE, "lane": "crypto_d1_auto_research",
        "candidate_id": CANDIDATE_ID, "verdict": None, "blockers": [],
        "approved_source_category": APPROVED_SOURCE_CATEGORY,
        "required_symbols": list(REQUIRED_SYMBOLS),
        "required_timeframes": list(REQUIRED_TIMEFRAMES),
        "required_candle_fields": list(REQUIRED_CANDLE_FIELDS),
        "session_coverage": dict(SESSION_COVERAGE),
        "existing_session_dates": list(EXISTING_SESSION_DATES),
        "min_additional_session_days": MIN_ADDITIONAL_SESSION_DAYS,
        "recommended_additional_session_days":
            RECOMMENDED_ADDITIONAL_SESSION_DAYS,
        "target_eligible_fresh_zones_before_judging":
            TARGET_ELIGIBLE_FRESH_ZONES_BEFORE_JUDGING,
        "baseline_protected_files": dict(BASELINE_PROTECTED_FILES),
        "append_only_rules": list(APPEND_ONLY_RULES),
        "sample_expansion_questions": list(SAMPLE_EXPANSION_QUESTIONS),
        "forbidden": list(FORBIDDEN),
        "replay_ready_remains_false_until_accepted_labels_exist": True,
        "redetection_after_staging_requires_separate_human_approval": True,
        "rules_and_candidate_asset_unchanged": True,
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
    edit = build_mutable_candidate_edit_v1()
    if (edit.get("verdict") != VERDICT_ME_READY
            or not validate_mutable_candidate_edit_v1(edit).get("valid")):
        record["verdict"] = VERDICT_AD_BLOCKED
        record["blockers"].append("mutable_candidate_edit_v1_not_ready")
        return record
    record["verdict"] = VERDICT_AD_READY
    return record


def validate_additional_session_days_review(record: Any) -> dict[str, Any]:
    """Validate the contract's shape and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_AD_READY, VERDICT_AD_BLOCKED):
        errors.append("bad_verdict")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if r.get("approved_source_category") != APPROVED_SOURCE_CATEGORY:
        errors.append("source_category_tampered")
    if tuple(r.get("required_symbols") or ()) != REQUIRED_SYMBOLS:
        errors.append("symbols_tampered")
    if tuple(r.get("required_timeframes") or ()) != REQUIRED_TIMEFRAMES:
        errors.append("timeframes_tampered")
    if tuple(r.get("required_candle_fields") or ()) != REQUIRED_CANDLE_FIELDS:
        errors.append("candle_fields_tampered")
    if r.get("session_coverage") != SESSION_COVERAGE:
        errors.append("session_coverage_tampered")
    if r.get("min_additional_session_days") != MIN_ADDITIONAL_SESSION_DAYS:
        errors.append("min_session_days_tampered")
    if r.get("baseline_protected_files") != BASELINE_PROTECTED_FILES:
        errors.append("baseline_protected_files_tampered")
    if tuple(r.get("append_only_rules") or ()) != APPEND_ONLY_RULES:
        errors.append("append_only_rules_tampered")
    if tuple(r.get("sample_expansion_questions") or ()) != (
            SAMPLE_EXPANSION_QUESTIONS):
        errors.append("expansion_questions_tampered")
    if tuple(r.get("forbidden") or ()) != FORBIDDEN:
        errors.append("forbidden_list_weakened")
    for key, want in (
        ("replay_ready_remains_false_until_accepted_labels_exist", True),
        ("redetection_after_staging_requires_separate_human_approval", True),
        ("rules_and_candidate_asset_unchanged", True),
        ("modifies_mission_flow", False), ("modifies_pm_lane", False),
        ("human_review_required", True),
        ("paper_trading_gate_locked", True),
        ("micro_live_gate_locked", True), ("live_gate_locked", True),
    ):
        if r.get(key) is not want:
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
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    return {"valid": not errors, "errors": errors}
