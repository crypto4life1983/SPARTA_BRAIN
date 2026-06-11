"""SPARTA NY-Session FVG+CHOCH DETECTOR/LABELER Spec (READ-ONLY, SPEC ONLY).

How future approved code will IDENTIFY and LABEL candidate setups from
provided historical candles -- and nothing more. The detector never fetches,
never scores, never backtests, never trades. Input candles come only from a
future approved upstream source; this block defines the label schema, the
closed status set, and the deterministic labeling gate.
"""

from __future__ import annotations

from typing import Any

from sparta_commander.ny_session_fvg_choch_strategy_spec_contract import (
    ALLOWED_TEST_WINDOWS,
    CANDIDATE_ID,
    VERDICT_FS_READY,
    build_ny_fvg_choch_strategy_spec,
    validate_ny_fvg_choch_strategy_spec,
)

DET_SCHEMA_VERSION = "ny_session_fvg_choch_detector_spec.v1"
DET_LABEL = ("SPARTA NY-Session FVG+CHOCH Detector/Labeler Spec "
             "(READ-ONLY, SPEC ONLY)")
DET_MODE = "RESEARCH_ONLY"
VERDICT_DET_READY = "NY_FVG_CHOCH_DETECTOR_SPEC_READY"
VERDICT_DET_BLOCKED = "NY_FVG_CHOCH_DETECTOR_SPEC_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_FVG_CHOCH_REPLAY_SPEC"

# CLOSED status set: every label ends in exactly one of these.
DETECTOR_STATUSES = (
    "SETUP_LABEL_ACCEPTED_FOR_REPLAY_REVIEW",
    "SETUP_REJECTED_MISSING_HTF_FVG",
    "SETUP_REJECTED_MISSING_CONTEXT",
    "SETUP_REJECTED_MISSING_CHOCH",
    "SETUP_REJECTED_MISSING_LTF_FVG",
    "SETUP_REJECTED_FIB_MISALIGNMENT",
    "SETUP_REJECTED_HTF_INVALIDATED",
    "SETUP_REJECTED_AMBIGUOUS",
    "SETUP_REJECTED_FORBIDDEN_CAPABILITY",
)

ALLOWED_DIRECTIONS = ("long", "short")
HTF_TIMEFRAME = "15m"
LTF_TIMEFRAME = "1m"

LABEL_REQUIRED_FIELDS = (
    "setup_id", "candidate_id", "symbol", "session_date", "direction",
    "session_window", "htf_timeframe", "ltf_timeframe", "htf_fvg_bounds",
    "htf_fvg_midpoint", "htf_fvg_type", "htf_context_reason",
    "liquidity_inflection_reference", "support_resistance_flip_reference",
    "previous_high_low_retest_reference", "choch_time", "choch_direction",
    "choch_pivot_reference", "ltf_fvg_bounds", "ltf_fvg_midpoint",
    "fib_0618_zone", "fib_alignment_pass", "proposed_entry_price",
    "proposed_stop_price", "proposed_target_4r_price",
    "breakeven_structure_trigger_reference", "invalidation_reason",
    "rejection_reason", "detector_status",
)

DETECTOR_RULES = (
    "input_candles_come_only_from_a_future_approved_upstream_source",
    "no_network_calls_and_no_data_fetching",
    "no_scoring_or_replay_result_claims_labels_only",
    "no_promotion_decision_ever",
    "rejected_setups_remain_auditable_never_deleted",
    "proposed_prices_are_research_labels_never_instructions",
    "future_replay_blocks_require_separate_human_approval",
)


def get_ny_fvg_choch_detector_spec_label() -> str:
    return DET_LABEL


def label_setup(observation: Any) -> dict[str, Any]:
    """DETERMINISTIC labeling gate. Takes a pre-computed observation (the
    future detector's findings as booleans/values) and produces ONE label
    with a closed-set status. Pure; never fetches, scores, or trades."""
    label: dict[str, Any] = {name: None for name in LABEL_REQUIRED_FIELDS}
    label["candidate_id"] = CANDIDATE_ID
    label["htf_timeframe"] = HTF_TIMEFRAME
    label["ltf_timeframe"] = LTF_TIMEFRAME
    label["label_authorizes_nothing"] = True
    if not isinstance(observation, dict):
        label["detector_status"] = "SETUP_REJECTED_AMBIGUOUS"
        label["rejection_reason"] = "observation_not_a_dict"
        return label

    for key in ("setup_id", "symbol", "session_date", "direction",
                "session_window"):
        label[key] = observation.get(key)

    # Forbidden-capability screen FIRST.
    for bad in ("order", "api_key", "credential", "wallet", "account",
                "live_authorized", "paper_authorized", "fetch_url"):
        for key in observation:
            if bad in str(key).lower():
                label["detector_status"] = "SETUP_REJECTED_FORBIDDEN_CAPABILITY"
                label["rejection_reason"] = "forbidden_capability_field:" + str(key)
                return label

    if label["direction"] not in ALLOWED_DIRECTIONS:
        label["detector_status"] = "SETUP_REJECTED_AMBIGUOUS"
        label["rejection_reason"] = "direction_outside_closed_set"
        return label
    if label["session_window"] not in ALLOWED_TEST_WINDOWS:
        label["detector_status"] = "SETUP_REJECTED_AMBIGUOUS"
        label["rejection_reason"] = "session_window_outside_allowed_set"
        return label

    checks = (
        ("htf_fvg_present", "SETUP_REJECTED_MISSING_HTF_FVG"),
        ("context_present", "SETUP_REJECTED_MISSING_CONTEXT"),
        ("choch_present", "SETUP_REJECTED_MISSING_CHOCH"),
        ("ltf_fvg_present", "SETUP_REJECTED_MISSING_LTF_FVG"),
        ("fib_alignment_pass", "SETUP_REJECTED_FIB_MISALIGNMENT"),
    )
    for cond, status in checks:
        if observation.get(cond) is not True:
            label["detector_status"] = status
            label["rejection_reason"] = "condition_failed:" + cond
            return label
    if observation.get("htf_invalidated") is True:
        label["detector_status"] = "SETUP_REJECTED_HTF_INVALIDATED"
        label["invalidation_reason"] = "htf_fvg_closed_through"
        label["rejection_reason"] = "htf_fvg_closed_through"
        return label
    if observation.get("ambiguous") is True:
        label["detector_status"] = "SETUP_REJECTED_AMBIGUOUS"
        label["rejection_reason"] = "ambiguous_or_low_quality"
        return label

    # All conditions hold: fill the accepted label from the observation.
    for key in ("htf_fvg_bounds", "htf_fvg_midpoint", "htf_fvg_type",
                "htf_context_reason", "liquidity_inflection_reference",
                "support_resistance_flip_reference",
                "previous_high_low_retest_reference", "choch_time",
                "choch_direction", "choch_pivot_reference", "ltf_fvg_bounds",
                "ltf_fvg_midpoint", "fib_0618_zone", "proposed_entry_price",
                "proposed_stop_price", "proposed_target_4r_price",
                "breakeven_structure_trigger_reference"):
        label[key] = observation.get(key)
    label["fib_alignment_pass"] = True
    missing = [k for k in ("htf_fvg_bounds", "htf_fvg_midpoint", "htf_fvg_type",
                           "choch_time", "ltf_fvg_bounds", "ltf_fvg_midpoint",
                           "proposed_entry_price", "proposed_stop_price",
                           "proposed_target_4r_price")
               if label.get(k) is None]
    if missing or not label.get("setup_id"):
        label["detector_status"] = "SETUP_REJECTED_AMBIGUOUS"
        label["rejection_reason"] = "accepted_fields_incomplete:" + ",".join(
            missing or ["setup_id"])
        return label
    label["detector_status"] = "SETUP_LABEL_ACCEPTED_FOR_REPLAY_REVIEW"
    return label


def build_ny_fvg_choch_detector_spec() -> dict[str, Any]:
    """Assemble the detector spec, gated on the READY strategy spec. Pure."""
    spec: dict[str, Any] = {
        "schema_version": DET_SCHEMA_VERSION, "label": DET_LABEL,
        "mode": DET_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [],
        "candidate_id": CANDIDATE_ID,
        "detector_statuses": list(DETECTOR_STATUSES),
        "label_required_fields": list(LABEL_REQUIRED_FIELDS),
        "detector_rules": list(DETECTOR_RULES),
        "allowed_directions": list(ALLOWED_DIRECTIONS),
        "htf_timeframe": HTF_TIMEFRAME, "ltf_timeframe": LTF_TIMEFRAME,
        "labels_authorize_nothing": True,
        "rejected_setups_auditable": True,
        "modifies_mission_flow": False, "modifies_pm_lane": False,
        "human_review_required": True,
        "executes": False, "writes_files": False, "writes_reports": False,
        "runs_scanner": False, "runs_replay_now": False, "scores_now": False,
        "fetches_data": False, "calls_api": False, "uses_network": False,
        "uses_credentials": False, "uses_wallet": False,
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
    strategy = build_ny_fvg_choch_strategy_spec()
    if (not validate_ny_fvg_choch_strategy_spec(strategy).get("valid")
            or strategy.get("verdict") != VERDICT_FS_READY):
        spec["verdict"] = VERDICT_DET_BLOCKED
        spec["blockers"].append("strategy_spec_not_ready")
        return spec
    spec["verdict"] = VERDICT_DET_READY
    return spec


def validate_ny_fvg_choch_detector_spec(spec: Any) -> dict[str, Any]:
    """Validate the detector spec's shape and safety invariants."""
    errors: list[str] = []
    if not isinstance(spec, dict):
        return {"valid": False, "errors": ["spec_not_a_dict"]}
    s = spec
    if s.get("verdict") not in (VERDICT_DET_READY, VERDICT_DET_BLOCKED):
        errors.append("bad_verdict")
    if s.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if tuple(s.get("detector_statuses") or ()) != DETECTOR_STATUSES:
        errors.append("status_set_tampered")
    if tuple(s.get("label_required_fields") or ()) != LABEL_REQUIRED_FIELDS:
        errors.append("label_fields_tampered")
    if tuple(s.get("detector_rules") or ()) != DETECTOR_RULES:
        errors.append("detector_rules_tampered")
    for key, want in (
        ("labels_authorize_nothing", True),
        ("rejected_setups_auditable", True),
        ("modifies_mission_flow", False), ("modifies_pm_lane", False),
        ("human_review_required", True),
        ("paper_trading_gate_locked", True),
        ("micro_live_gate_locked", True), ("live_gate_locked", True),
    ):
        if s.get(key) is not want:
            errors.append("constitution_flag_wrong:" + key)
    for key in ("executes", "writes_files", "writes_reports", "runs_scanner",
                "runs_replay_now", "scores_now", "fetches_data", "calls_api",
                "uses_network", "uses_credentials", "uses_wallet",
                "connects_broker", "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate"):
        if s.get(key) is not False:
            errors.append("capability_not_false:" + key)
    return {"valid": not errors, "errors": errors}
