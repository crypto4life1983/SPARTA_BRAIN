"""SPARTA NY-Session FVG+CHOCH ACCEPTED LABELS HUMAN REVIEW (READ-ONLY).

The first accepted labels in the lane's history deserve their own gate:
this contract freezes the EXACT 7 accepted setups from the expanded-sample
re-detection -- their setup_ids, symbols, and dates -- and certifies they
are real, unique, schema-valid, produced by the frozen edit-V1 rules, and
free of any PnL/replay/order/credential field, with every prior output
byte-identical. replay_ready stays True and replay_authorized stays False:
the fee-honest replay of EXACTLY these 7 labels is its own future human
approval. Changes no rules, runs nothing.
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
    LABEL_REQUIRED_FIELDS,
)
from sparta_commander.ny_session_fvg_choch_expanded_sample_redetection_review_contract import (
    EXPECTED_ACCEPTED_SETUP_IDS,
    EXPECTED_LABELS_SHA256,
    LABELS_PATH,
    SUMMARY_PATH,
    VERDICT_EX_ACCEPTED,
    build_expanded_redetection_review,
)
from sparta_commander.ny_session_fvg_choch_mutable_candidate_edit_v1 import (
    EDIT_ID,
    NEW_PARAMETERS,
)
from sparta_commander.ny_session_fvg_choch_strategy_spec_contract import (
    CANDIDATE_ID,
    FIB_LEVEL,
    FIB_TOLERANCE,
    RISK_REWARD_TARGET,
)

AL_SCHEMA_VERSION = "ny_session_fvg_choch_accepted_labels_human_review.v1"
AL_LABEL = ("SPARTA NY-Session FVG+CHOCH Accepted Labels Human Review "
            "(READ-ONLY, REVIEW ONLY, REPLAY STILL HUMAN-GATED)")
AL_MODE = "RESEARCH_ONLY"
VERDICT_AL_APPROVED = (
    "ACCEPTED_LABELS_HUMAN_REVIEW_APPROVED_FOR_REPLAY_DECISION")
VERDICT_AL_REJECTED = "ACCEPTED_LABELS_HUMAN_REVIEW_REJECTED"
VERDICT_AL_BLOCKED = "ACCEPTED_LABELS_HUMAN_REVIEW_BLOCKED"
NEXT_REQUIRED_ACTION = (
    "HUMAN_APPROVED_FEE_HONEST_REPLAY_OF_7_ACCEPTED_LABELS_ONLY")

FROZEN_ACCEPTED_SETUP_IDS = tuple(sorted(EXPECTED_ACCEPTED_SETUP_IDS))
FROZEN_ACCEPTED_BY_SYMBOL_DATES = {
    "SOLUSD": ("2026-05-13", "2026-05-20", "2026-05-26"),
    "ETHUSD": ("2026-05-13", "2026-05-15"),
    "BTCUSD": ("2026-06-09",),
    "AVAXUSD": ("2026-05-29",),
}
ZERO_ACCEPTED_SYMBOLS = ("ARBUSD", "XRPUSD")
APPROVED_SESSION_DATES = (
    "2026-05-12", "2026-05-13", "2026-05-14", "2026-05-15", "2026-05-18",
    "2026-05-19", "2026-05-20", "2026-05-21", "2026-05-22", "2026-05-25",
    "2026-05-26", "2026-05-27", "2026-05-28", "2026-05-29", "2026-06-01",
    "2026-06-02", "2026-06-03", "2026-06-04", "2026-06-05", "2026-06-09",
    "2026-06-10",
)
BATCH2_MANIFEST_PATH = (
    "data/ny_fvg_choch/staged/manifest_batch2_2026-05-12_2026-06-09.txt")
BATCH2_MANIFEST_SHA256 = (
    "e95274b6822196a72a69c5a9a29910150e4bbe9128ea97f42e7cf8d0079e32fc")

FROZEN_RULES_ECHO = {
    "edit_id": EDIT_ID,
    "fvg_freshness_controls": dict(NEW_PARAMETERS),
    "fib_level": FIB_LEVEL, "fib_tolerance": FIB_TOLERANCE,
    "risk_reward_target": RISK_REWARD_TARGET,
}

_FORBIDDEN_LABEL_TOKENS = ("pnl", "profit", "score", "win_rate", "replay",
                           "fill", "order", "broker", "credential",
                           "api_key", "wallet", "login", "live_trading",
                           "live_authorized", "paper_authorized")

REVIEW_CHECKLIST = (
    "inputs_present",
    "expanded_review_certified_accepted",
    "exactly_7_accepted_and_unique",
    "setup_ids_exactly_frozen",
    "symbols_and_dates_match_frozen_map",
    "dates_inside_approved_staged_sample",
    "zero_accepted_symbols_confirmed",
    "accepted_labels_have_29_field_schema_and_authorize_nothing",
    "no_forbidden_fields_in_accepted_labels",
    "frozen_rules_consistent_no_drift",
    "prior_outputs_and_candles_not_mutated",
    "replay_gated_on_separate_human_approval",
)

FORBIDDEN = (
    "replay_runs", "pnl_calculation", "profitability_scoring",
    "optimizer_runs", "rule_changes", "candidate_asset_changes",
    "modifying_labels_candles_or_summaries",
    "broker_exchange_credential_access", "order_endpoints",
    "paper_live_micro_live_authorization", "gate_unlocks",
)


def get_accepted_labels_human_review_label() -> str:
    return AL_LABEL


def observe_accepted_labels(repo_root: Any,
                            tracked_paths: Any = ()) -> dict[str, Any]:
    """READ-ONLY observation: the 7 accepted labels plus integrity state."""
    root = _pathlib.Path(str(repo_root))
    labels_file = root / LABELS_PATH
    summary_file = root / SUMMARY_PATH
    observation: dict[str, Any] = {
        "labels_present": labels_file.is_file(),
        "summary_present": summary_file.is_file(),
        "accepted_labels": [], "summary": None,
        "labels_sha256": None,
        "expanded_review_verdict": None,
        "tracked_output_paths": [str(p) for p in (tracked_paths or ())],
        "baseline_files_sha256": {}, "batch2_manifest_sha256": None,
    }
    if observation["labels_present"]:
        raw = labels_file.read_bytes()
        observation["labels_sha256"] = _hashlib.sha256(raw).hexdigest()
        for line in raw.decode("utf-8").splitlines():
            if line.strip():
                label = _json.loads(line)
                if label.get("detector_status") == (
                        "SETUP_LABEL_ACCEPTED_FOR_REPLAY_REVIEW"):
                    observation["accepted_labels"].append(label)
    if observation["summary_present"]:
        observation["summary"] = _json.loads(
            summary_file.read_text(encoding="utf-8"))
    observation["expanded_review_verdict"] = build_expanded_redetection_review(
        repo_root, tracked_paths=[]).get("verdict")
    for rel_path in BASELINE_PROTECTED_FILES:
        target = root / rel_path
        observation["baseline_files_sha256"][rel_path] = (
            _hashlib.sha256(target.read_bytes()).hexdigest()
            if target.is_file() else None)
    batch2 = root / BATCH2_MANIFEST_PATH
    if batch2.is_file():
        observation["batch2_manifest_sha256"] = _hashlib.sha256(
            batch2.read_bytes()).hexdigest()
    return observation


def certify_accepted_labels(observation: Any) -> dict[str, Any]:
    """DETERMINISTIC certification of the 7 accepted labels. Pure."""
    review: dict[str, Any] = {
        "schema_version": AL_SCHEMA_VERSION, "label": AL_LABEL,
        "mode": AL_MODE, "lane": "crypto_d1_auto_research",
        "candidate_id": CANDIDATE_ID, "edit_id": EDIT_ID,
        "verdict": None, "blockers": [],
        "checklist": list(REVIEW_CHECKLIST), "checklist_results": {},
        "accepted_total": 0,
        "frozen_accepted_setup_ids": list(FROZEN_ACCEPTED_SETUP_IDS),
        "frozen_accepted_by_symbol_dates": {
            k: list(v) for k, v in FROZEN_ACCEPTED_BY_SYMBOL_DATES.items()},
        "zero_accepted_symbols": list(ZERO_ACCEPTED_SYMBOLS),
        "frozen_rules_echo": {k: (dict(v) if isinstance(v, dict) else v)
                              for k, v in FROZEN_RULES_ECHO.items()},
        "forbidden": list(FORBIDDEN),
        "replay_ready": False, "replay_authorized": False,
        "replay_scope_is_exactly_these_7_labels_only": True,
        "replay_requires_separate_human_approval": True,
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
        review["verdict"] = VERDICT_AL_BLOCKED
        review["blockers"].append("observation_missing")
        return review
    o = observation
    if not o.get("labels_present") or not o.get("summary_present"):
        review["verdict"] = VERDICT_AL_BLOCKED
        review["blockers"].append("labels_or_summary_file_missing")
        return review

    accepted = o.get("accepted_labels") or []
    summary = o.get("summary") or {}
    expected_keys = set(LABEL_REQUIRED_FIELDS) | {"label_authorizes_nothing"}
    r: dict[str, bool] = {}
    r["inputs_present"] = True
    r["expanded_review_certified_accepted"] = (
        o.get("expanded_review_verdict") == VERDICT_EX_ACCEPTED
        and o.get("labels_sha256") == EXPECTED_LABELS_SHA256)
    ids = [x.get("setup_id") for x in accepted]
    review["accepted_total"] = len(accepted)
    r["exactly_7_accepted_and_unique"] = (len(accepted) == 7
                                          and len(set(ids)) == 7)
    r["setup_ids_exactly_frozen"] = (
        tuple(sorted(ids)) == FROZEN_ACCEPTED_SETUP_IDS)
    observed_map: dict[str, list] = {}
    for x in accepted:
        observed_map.setdefault(x.get("symbol"), []).append(
            x.get("session_date"))
    r["symbols_and_dates_match_frozen_map"] = (
        {k: tuple(sorted(v)) for k, v in observed_map.items()}
        == {k: tuple(sorted(v))
            for k, v in FROZEN_ACCEPTED_BY_SYMBOL_DATES.items()})
    r["dates_inside_approved_staged_sample"] = bool(accepted) and all(
        x.get("session_date") in APPROVED_SESSION_DATES for x in accepted)
    r["zero_accepted_symbols_confirmed"] = not any(
        x.get("symbol") in ZERO_ACCEPTED_SYMBOLS for x in accepted)
    r["accepted_labels_have_29_field_schema_and_authorize_nothing"] = bool(
        accepted) and all(
        isinstance(x, dict) and set(x) == expected_keys
        and x.get("label_authorizes_nothing") is True
        and x.get("candidate_id") == CANDIDATE_ID for x in accepted)
    clean = True
    for x in accepted:
        for key in x:
            lowered = str(key).lower()
            if any(token in lowered for token in _FORBIDDEN_LABEL_TOKENS):
                clean = False
    r["no_forbidden_fields_in_accepted_labels"] = bool(accepted) and clean
    r["frozen_rules_consistent_no_drift"] = (
        summary.get("edit_id") == EDIT_ID
        and summary.get("edited_candidate_parameters_active")
        == NEW_PARAMETERS
        and FIB_LEVEL == 0.618 and FIB_TOLERANCE == 0.05
        and RISK_REWARD_TARGET == 4.0)
    r["prior_outputs_and_candles_not_mutated"] = (
        o.get("baseline_files_sha256") == BASELINE_PROTECTED_FILES
        and o.get("batch2_manifest_sha256") == BATCH2_MANIFEST_SHA256
        and not o.get("tracked_output_paths"))
    r["replay_gated_on_separate_human_approval"] = (
        summary.get("replay_ready") is True
        and summary.get("replay_requires_separate_human_approval") is True)
    review["checklist_results"] = r
    failed = [name for name, ok in r.items() if not ok]
    if failed:
        review["verdict"] = VERDICT_AL_REJECTED
        review["blockers"].extend("check_failed:" + n for n in failed)
        return review
    review["replay_ready"] = True
    review["verdict"] = VERDICT_AL_APPROVED
    return review


def build_accepted_labels_human_review(repo_root: Any,
                                       tracked_paths: Any = ()) -> dict[str, Any]:
    """Observe the accepted labels read-only and certify them."""
    return certify_accepted_labels(
        observe_accepted_labels(repo_root, tracked_paths))


def validate_accepted_labels_human_review(review: Any) -> dict[str, Any]:
    """Validate the review's shape and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(review, dict):
        return {"valid": False, "errors": ["review_not_a_dict"]}
    v = review
    if v.get("verdict") not in (VERDICT_AL_APPROVED, VERDICT_AL_REJECTED,
                                VERDICT_AL_BLOCKED):
        errors.append("bad_verdict")
    if v.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if v.get("edit_id") != EDIT_ID:
        errors.append("edit_id_tampered")
    if tuple(v.get("checklist") or ()) != REVIEW_CHECKLIST:
        errors.append("checklist_tampered")
    if tuple(v.get("frozen_accepted_setup_ids") or ()) != (
            FROZEN_ACCEPTED_SETUP_IDS):
        errors.append("frozen_setup_ids_tampered")
    if {k: tuple(v2) for k, v2 in (v.get("frozen_accepted_by_symbol_dates")
                                   or {}).items()} != (
            FROZEN_ACCEPTED_BY_SYMBOL_DATES):
        errors.append("frozen_symbol_dates_tampered")
    if tuple(v.get("zero_accepted_symbols") or ()) != ZERO_ACCEPTED_SYMBOLS:
        errors.append("zero_accepted_symbols_tampered")
    if tuple(v.get("forbidden") or ()) != FORBIDDEN:
        errors.append("forbidden_list_weakened")
    if v.get("replay_authorized") is not False:
        errors.append("replay_can_never_be_authorized_by_this_review")
    results = v.get("checklist_results") or {}
    if v.get("verdict") == VERDICT_AL_APPROVED:
        if v.get("blockers"):
            errors.append("approved_with_blockers")
        if set(results) != set(REVIEW_CHECKLIST) or not all(
                results.get(n) is True for n in REVIEW_CHECKLIST):
            errors.append("approved_without_full_passing_checklist")
        if v.get("replay_ready") is not True:
            errors.append("approved_review_must_report_replay_ready_true")
        if v.get("accepted_total") != 7:
            errors.append("approved_without_exactly_7_accepted")
    else:
        if v.get("replay_ready") is not False:
            errors.append("non_approved_review_cannot_be_replay_ready")
    if v.get("verdict") in (VERDICT_AL_REJECTED, VERDICT_AL_BLOCKED) \
            and not v.get("blockers"):
        errors.append("non_approved_without_blockers")
    for key, want in (
        ("replay_scope_is_exactly_these_7_labels_only", True),
        ("replay_requires_separate_human_approval", True),
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
