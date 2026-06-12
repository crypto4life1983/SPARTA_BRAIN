"""SPARTA BREAKOUT-PULLBACK-STRUCTURE DETECTOR/LABELER Spec (READ-ONLY,
SPEC ONLY). Candidate #2's labeling gate.

How approved code IDENTIFIES and LABELS breakout -> pullback/retest ->
continuation setups from provided 15m candles -- and nothing more. Every
label ends in one of 10 closed statuses; the 81 bps cost floor (via the
PUSHED V2 viability filter) is checked at label time, so a cost-dominated
setup can never be accepted for replay review. The detector never fetches,
scores, replays, or trades, and candidate #1 stays rejected on record.
"""

from __future__ import annotations

from typing import Any

from sparta_commander.crypto_intraday_breakout_pullback_structure_strategy_spec_contract import (
    CANDIDATE_FAMILY,
    CANDIDATE_ID,
    MINIMUM_RISK_DISTANCE_BPS,
    RANGE_LOOKBACK_BARS_15M,
    VERDICT_BP_READY as VERDICT_STRATEGY_READY,
    build_breakout_pullback_strategy_spec,
)
from sparta_commander.ny_session_fvg_choch_mutable_candidate_edit_v2_cost_viability import (
    evaluate_setup_cost_viability,
)

BPD_SCHEMA_VERSION = (
    "crypto_intraday_breakout_pullback_structure_detector_spec.v1")
BPD_LABEL = ("SPARTA Breakout-Pullback-Structure Detector/Labeler Spec "
             "(READ-ONLY, SPEC ONLY)")
BPD_MODE = "RESEARCH_ONLY"
VERDICT_BPD_READY = "BREAKOUT_PULLBACK_DETECTOR_SPEC_READY"
VERDICT_BPD_BLOCKED = "BREAKOUT_PULLBACK_DETECTOR_SPEC_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_REVIEW_OF_BP_DETECTOR_DRY_RUN"

CONTEXT_TIMEFRAME = "1h_15m"
TRIGGER_TIMEFRAME = "15m"

# CLOSED status set: every label ends in exactly one of these.
BP_DETECTOR_STATUSES = (
    "BP_SETUP_LABEL_ACCEPTED_FOR_REPLAY_REVIEW",
    "BP_SETUP_REJECTED_NO_BREAKOUT",
    "BP_SETUP_REJECTED_WEAK_BREAKOUT",
    "BP_SETUP_REJECTED_NO_PULLBACK",
    "BP_SETUP_REJECTED_FAILED_RETEST",
    "BP_SETUP_REJECTED_NO_CONTINUATION",
    "BP_SETUP_REJECTED_RISK_BELOW_81_BPS",
    "BP_SETUP_REJECTED_AMBIGUOUS_STRUCTURE",
    "BP_SETUP_REJECTED_INSUFFICIENT_CANDLES",
    "BP_SETUP_REJECTED_FORBIDDEN_CAPABILITY",
)

ALLOWED_DIRECTIONS = ("long", "short")
ALLOWED_STOP_MODELS = ("structural_swing", "atr_1_5x")

BP_LABEL_REQUIRED_FIELDS = (
    "setup_id", "candidate_id", "symbol", "session_date", "direction",
    "context_timeframe", "trigger_timeframe", "range_lookback_bars",
    "range_high", "range_low", "breakout_time", "breakout_level",
    "breakout_direction", "breakout_close", "breakout_distance_bps",
    "breakout_body_ratio", "pullback_time", "pullback_level",
    "pullback_depth_ratio", "retest_pass", "continuation_time",
    "continuation_close", "structure_confirmation_reference",
    "atr_14_15m", "structural_stop_price", "atr_stop_price",
    "selected_stop_price", "stop_model", "entry_price",
    "risk_distance_bps", "target_2r_price", "target_3r_price",
    "target_4r_price", "cost_floor_bps", "cost_floor_pass",
    "rejection_reason", "detector_status", "label_authorizes_nothing",
)

BP_DETECTOR_RULES = (
    "input_candles_come_only_from_approved_staged_or_fixture_sources",
    "no_network_calls_and_no_data_fetching",
    "no_pnl_scoring_or_replay_result_claims_labels_only",
    "cost_floor_81bps_checked_at_label_time_via_the_pushed_v2_filter",
    "rejected_setups_remain_auditable_never_deleted",
    "proposed_prices_are_research_labels_never_instructions",
    "candidate_1_fvg_choch_stays_rejected_on_record",
    "future_replay_blocks_require_separate_human_approval",
)

_ACCEPT_REQUIRED_VALUES = (
    "range_high", "range_low", "breakout_time", "breakout_level",
    "breakout_close", "pullback_time", "continuation_time",
    "continuation_close", "atr_14_15m", "structural_stop_price",
    "atr_stop_price", "selected_stop_price", "stop_model", "entry_price",
    "target_2r_price", "target_3r_price", "target_4r_price",
)

_FORBIDDEN_TOKENS = ("order", "api_key", "credential", "wallet", "account",
                     "login", "fetch_url", "live_authorized",
                     "paper_authorized", "broker", "secret")


def get_bp_detector_spec_label() -> str:
    return BPD_LABEL


def label_bp_setup(observation: Any) -> dict[str, Any]:
    """DETERMINISTIC labeling gate for candidate #2. Takes a pre-computed
    observation and produces ONE label with a closed-set status. Pure;
    never fetches, scores, replays, or trades."""
    label: dict[str, Any] = {name: None for name in BP_LABEL_REQUIRED_FIELDS}
    label["candidate_id"] = CANDIDATE_ID
    label["context_timeframe"] = CONTEXT_TIMEFRAME
    label["trigger_timeframe"] = TRIGGER_TIMEFRAME
    label["range_lookback_bars"] = RANGE_LOOKBACK_BARS_15M
    label["cost_floor_bps"] = MINIMUM_RISK_DISTANCE_BPS
    label["cost_floor_pass"] = False
    label["label_authorizes_nothing"] = True
    if not isinstance(observation, dict):
        label["detector_status"] = "BP_SETUP_REJECTED_AMBIGUOUS_STRUCTURE"
        label["rejection_reason"] = "observation_not_a_dict"
        return label

    for key in ("setup_id", "symbol", "session_date", "direction"):
        label[key] = observation.get(key)

    # Forbidden-capability screen FIRST.
    for key in observation:
        lowered = str(key).lower()
        for token in _FORBIDDEN_TOKENS:
            if token in lowered:
                label["detector_status"] = (
                    "BP_SETUP_REJECTED_FORBIDDEN_CAPABILITY")
                label["rejection_reason"] = ("forbidden_capability_field:"
                                             + str(key))
                return label

    if label["direction"] not in ALLOWED_DIRECTIONS:
        label["detector_status"] = "BP_SETUP_REJECTED_AMBIGUOUS_STRUCTURE"
        label["rejection_reason"] = "direction_outside_closed_set"
        return label

    checks = (
        ("sufficient_candles", "BP_SETUP_REJECTED_INSUFFICIENT_CANDLES"),
        ("breakout_present", "BP_SETUP_REJECTED_NO_BREAKOUT"),
        ("breakout_strong", "BP_SETUP_REJECTED_WEAK_BREAKOUT"),
        ("pullback_present", "BP_SETUP_REJECTED_NO_PULLBACK"),
        ("retest_pass", "BP_SETUP_REJECTED_FAILED_RETEST"),
        ("continuation_confirmed", "BP_SETUP_REJECTED_NO_CONTINUATION"),
    )
    for condition, status in checks:
        if observation.get(condition) is not True:
            label["detector_status"] = status
            label["rejection_reason"] = "condition_failed:" + condition
            # carry whatever context was observed, for auditability
            for key in ("range_high", "range_low", "breakout_time",
                        "breakout_level", "breakout_direction",
                        "breakout_close", "breakout_distance_bps",
                        "breakout_body_ratio", "pullback_time",
                        "pullback_level", "pullback_depth_ratio"):
                label[key] = observation.get(key)
            label["retest_pass"] = observation.get("retest_pass") is True
            return label
    if observation.get("ambiguous") is True:
        label["detector_status"] = "BP_SETUP_REJECTED_AMBIGUOUS_STRUCTURE"
        label["rejection_reason"] = "ambiguous_or_low_quality_structure"
        return label

    # All structural conditions hold: fill the label from the observation.
    for key in ("range_high", "range_low", "breakout_time", "breakout_level",
                "breakout_direction", "breakout_close",
                "breakout_distance_bps", "breakout_body_ratio",
                "pullback_time", "pullback_level", "pullback_depth_ratio",
                "continuation_time", "continuation_close",
                "structure_confirmation_reference", "atr_14_15m",
                "structural_stop_price", "atr_stop_price",
                "selected_stop_price", "stop_model", "entry_price",
                "target_2r_price", "target_3r_price", "target_4r_price"):
        label[key] = observation.get(key)
    label["retest_pass"] = True

    # THE COST FLOOR, at label time, via the pushed V2 filter.
    viability = evaluate_setup_cost_viability(
        label["entry_price"], label["selected_stop_price"])
    label["risk_distance_bps"] = viability.get("entry_to_stop_distance_bps")
    if viability.get("viable") is not True:
        label["detector_status"] = "BP_SETUP_REJECTED_RISK_BELOW_81_BPS"
        label["rejection_reason"] = "risk_distance_below_81_bps"
        return label
    label["cost_floor_pass"] = True

    missing = [k for k in _ACCEPT_REQUIRED_VALUES if label.get(k) is None]
    if missing or not label.get("setup_id") \
            or label.get("stop_model") not in ALLOWED_STOP_MODELS:
        label["detector_status"] = "BP_SETUP_REJECTED_AMBIGUOUS_STRUCTURE"
        label["rejection_reason"] = "accepted_fields_incomplete:" + ",".join(
            missing or ["setup_id_or_stop_model"])
        label["cost_floor_pass"] = False
        return label
    label["detector_status"] = "BP_SETUP_LABEL_ACCEPTED_FOR_REPLAY_REVIEW"
    return label


def record_bp_detector_spec(strategy_verdict: Any) -> dict[str, Any]:
    """Assemble the detector spec, gated on the strategy spec verdict."""
    spec: dict[str, Any] = {
        "schema_version": BPD_SCHEMA_VERSION, "label": BPD_LABEL,
        "mode": BPD_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [],
        "candidate_id": CANDIDATE_ID,
        "candidate_family": CANDIDATE_FAMILY,
        "strategy_spec_verdict": strategy_verdict,
        "detector_statuses": list(BP_DETECTOR_STATUSES),
        "label_required_fields": list(BP_LABEL_REQUIRED_FIELDS),
        "detector_rules": list(BP_DETECTOR_RULES),
        "allowed_directions": list(ALLOWED_DIRECTIONS),
        "allowed_stop_models": list(ALLOWED_STOP_MODELS),
        "context_timeframe": CONTEXT_TIMEFRAME,
        "trigger_timeframe": TRIGGER_TIMEFRAME,
        "cost_floor_bps": MINIMUM_RISK_DISTANCE_BPS,
        "labels_authorize_nothing": True,
        "rejected_setups_auditable": True,
        "modifies_mission_flow": False, "modifies_pm_lane": False,
        "human_review_required": True,
        "executes": False, "writes_files": False, "writes_reports": False,
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
    if strategy_verdict != VERDICT_STRATEGY_READY:
        spec["verdict"] = VERDICT_BPD_BLOCKED
        spec["blockers"].append("strategy_spec_not_ready")
        return spec
    spec["verdict"] = VERDICT_BPD_READY
    return spec


def build_bp_detector_spec(
        repo_root: Any = "C:/SPARTA_BRAIN") -> dict[str, Any]:
    """Build against the LIVE pushed strategy spec chain."""
    strategy = build_breakout_pullback_strategy_spec(repo_root)
    return record_bp_detector_spec(strategy.get("verdict"))


def validate_bp_detector_spec(spec: Any) -> dict[str, Any]:
    """Validate the detector spec's shape and safety invariants."""
    errors: list[str] = []
    if not isinstance(spec, dict):
        return {"valid": False, "errors": ["spec_not_a_dict"]}
    s = spec
    if s.get("verdict") not in (VERDICT_BPD_READY, VERDICT_BPD_BLOCKED):
        errors.append("bad_verdict")
    if s.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if s.get("candidate_family") != CANDIDATE_FAMILY:
        errors.append("candidate_family_tampered")
    if tuple(s.get("detector_statuses") or ()) != BP_DETECTOR_STATUSES:
        errors.append("status_set_tampered")
    if tuple(s.get("label_required_fields") or ()) != (
            BP_LABEL_REQUIRED_FIELDS):
        errors.append("label_fields_tampered")
    if tuple(s.get("detector_rules") or ()) != BP_DETECTOR_RULES:
        errors.append("detector_rules_tampered")
    if s.get("cost_floor_bps") != MINIMUM_RISK_DISTANCE_BPS:
        errors.append("cost_floor_tampered")
    if s.get("verdict") == VERDICT_BPD_READY and s.get(
            "strategy_spec_verdict") != VERDICT_STRATEGY_READY:
        errors.append("ready_without_ready_strategy_spec")
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
    for key in ("executes", "writes_files", "writes_reports",
                "runs_detector_now", "runs_replay_now", "scores_now",
                "fetches_data", "calls_api", "uses_network",
                "uses_credentials", "uses_wallet", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate"):
        if s.get(key) is not False:
            errors.append("capability_not_false:" + key)
    return {"valid": not errors, "errors": errors}
