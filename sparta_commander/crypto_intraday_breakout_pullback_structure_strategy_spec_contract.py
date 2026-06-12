"""SPARTA CRYPTO INTRADAY BREAKOUT-PULLBACK-STRUCTURE Strategy Spec
(READ-ONLY, SPEC ONLY). Candidate #2 of the auto-research lane.

Born from candidate #1's honest death: the 1m FVG/CHOCH scalp geometry was
rejected (COST_NON_VIABLE_RISK_GEOMETRY, max 39.68 bps risk units vs the
81 bps floor). Candidate #2 uses 15m/1h context -- range breakout, pullback/
retest into structure, continuation confirmation, and STRUCTURAL or
ATR-based stops whose risk units must clear the UNCHANGED 81 bps floor
(27 bps taker round-trip x 3, maker never assumed) before any replay
eligibility. Spec only: no detector, replay, scorer, or optimizer exists in
this block; each is a future, separately human-approved build. Nothing here
can authorize any market action, and candidate #1 is never revived.
"""

from __future__ import annotations

from typing import Any

from sparta_commander.crypto_d1_auto_research_mutable_candidate_asset_spec import (
    VERDICT_ASSET_ACCEPTED,
    validate_candidate_asset,
)
from sparta_commander.next_candidate_family_decision_contract import (
    NEXT_FAMILY_ID,
    NEXT_FAMILY_NAME,
    VERDICT_NF_RECORDED,
    build_next_family_decision,
)
from sparta_commander.ny_session_fvg_choch_mutable_candidate_edit_v2_cost_viability import (
    evaluate_setup_cost_viability,
)
from sparta_commander.ny_session_fvg_choch_strategy_spec_contract import (
    CANDIDATE_ID as REJECTED_CANDIDATE_ID,
)

BP_SCHEMA_VERSION = (
    "crypto_intraday_breakout_pullback_structure_strategy_spec.v1")
BP_LABEL = ("SPARTA Crypto Intraday Breakout-Pullback-Structure Strategy "
            "Spec (READ-ONLY, SPEC ONLY)")
BP_MODE = "RESEARCH_ONLY"
VERDICT_BP_READY = "BREAKOUT_PULLBACK_STRATEGY_SPEC_READY"
VERDICT_BP_BLOCKED = "BREAKOUT_PULLBACK_STRATEGY_SPEC_BLOCKED"
VERDICT_SETUP_COMPLETE = "BP_SETUP_COMPLETE_FOR_RESEARCH"
VERDICT_SETUP_REJECTED = "BP_SETUP_REJECTED"
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_BREAKOUT_PULLBACK_DETECTOR_SPEC"

CANDIDATE_ID = NEXT_FAMILY_ID          # CRYPTO_INTRADAY_BREAKOUT_PULLBACK...
CANDIDATE_FAMILY = NEXT_FAMILY_NAME    # intraday_breakout_pullback_structure

REQUIRED_SYMBOLS = ("BTCUSD", "ETHUSD", "SOLUSD", "AVAXUSD", "ARBUSD",
                    "XRPUSD")
CONTEXT_TIMEFRAMES = ("1h", "15m")
TRIGGER_TIMEFRAME = "15m"
NO_1M_SCALP_ENTRY_GEOMETRY = True
EVALUATION_WINDOW = ("intraday crypto window compatible with staged data; "
                     "NY session 09:30-13:00 America/New_York evaluation "
                     "allowed but no tiny 1m trigger is ever required")

# Deterministic research parameters (mutable-candidate territory later).
RANGE_LOOKBACK_BARS_15M = 20
BREAKOUT_CLOSE_THRESHOLD_BPS = 10
BREAKOUT_BODY_MIN_FRACTION = 0.5
RETEST_TOLERANCE_BPS = 15
MAX_PULLBACK_DEPTH_FRACTION = 0.618
BREAKOUT_FAILURE_RANGE_FRACTION = 0.25
ATR_PERIOD = 14
ATR_STOP_MULTIPLIER = 1.5
TARGET_R_OPTIONS = (2.0, 3.0, 4.0)

# Cost viability: UNCHANGED from the lane's frozen discipline.
ROUND_TRIP_COST_BPS = 27
COST_FLOOR_MULTIPLIER = 3
MINIMUM_RISK_DISTANCE_BPS = 81  # 27 x 3
REJECT_COST_DOMINATED_SETUPS = True

DETERMINISTIC_RULES = {
    "range_definition": ("prior range = highest high and lowest low of the "
                         "last 20 completed 15m bars before the breakout "
                         "bar"),
    "breakout_definition": ("a 15m CLOSE beyond the prior range high (long) "
                            "or low (short) by at least 10 bps of the "
                            "broken level, with breakout candle body >= 50% "
                            "of its high-low range"),
    "pullback_retest": ("after the breakout, price trades back to within "
                        "15 bps of the broken level or structure zone; "
                        "pullback depth must not exceed 61.8% of the "
                        "breakout leg"),
    "breakout_failure": ("the setup is invalid if a 15m candle CLOSES back "
                         "inside the prior range beyond 25% of the range "
                         "height past the broken level"),
    "continuation_confirmation": ("a 15m close in the breakout direction "
                                  "beyond the retest candle's extreme, "
                                  "forming a higher low (long) or lower "
                                  "high (short) versus the pullback "
                                  "extreme"),
    "entry_rule": ("research entry marked at the continuation-confirmation "
                   "close, only when breakout + retest + continuation are "
                   "ALL present"),
    "stop_rule": ("research stop at the pullback structural swing extreme "
                  "OR 1.5 x ATR(14, 15m) from entry, whichever is WIDER; "
                  "the resulting risk distance must be >= 81 bps of entry "
                  "before replay eligibility; research-only, never live "
                  "sizing"),
    "target_rule": ("research targets at 2R, 3R, or 4R from the marked "
                    "entry and stop; targets are research labels, never "
                    "order placement"),
    "cost_viability": ("net-edge thinking is mandatory: 27 bps taker "
                       "round-trip x 3 = 81 bps minimum risk distance; "
                       "cost-dominated setups are rejected before replay; "
                       "maker execution is never assumed"),
}

REJECTION_RULES = (
    "no_breakout",
    "failed_retest",
    "missing_continuation_confirmation",
    "risk_distance_below_81_bps",
    "ambiguous_structure",
    "insufficient_candles",
    "any_live_paper_order_api_credential_field",
)

FORBIDDEN = (
    "live_trading", "paper_trading", "order_placement",
    "broker_exchange_private_api_access",
    "credentials_api_keys_login_account_wallet",
    "maker_execution_assumptions", "lowering_the_81_bps_floor",
    "reviving_ny_fvg_choch_candidate_1",
    "deleting_or_hiding_rejected_evidence",
    "detector_replay_scorer_or_optimizer_runs_in_this_block",
    "gate_unlocks",
)

_REQUIRED_CONDITIONS = ("breakout_present", "retest_present",
                        "continuation_confirmed")
_FORBIDDEN_CONDITION_TOKENS = ("live", "paper", "order", "api_key",
                               "credential", "wallet", "account", "login",
                               "broker")


def get_breakout_pullback_strategy_spec_label() -> str:
    return BP_LABEL


def evaluate_setup_completeness(conditions: Any) -> dict[str, Any]:
    """DETERMINISTIC research gate: a setup is complete only when breakout,
    retest, and continuation are ALL present, no invalidation applies, and
    the entry-to-stop distance clears the 81 bps floor (via the PUSHED V2
    cost-viability filter). Pure; completeness authorizes nothing."""
    result: dict[str, Any] = {"verdict": None, "rejection_reasons": [],
                              "risk_distance_bps": None,
                              "completeness_authorizes_nothing": True}
    if not isinstance(conditions, dict):
        result["verdict"] = VERDICT_SETUP_REJECTED
        result["rejection_reasons"].append("conditions_not_a_dict")
        return result
    reasons = result["rejection_reasons"]
    for key in conditions:
        lowered = str(key).lower()
        for token in _FORBIDDEN_CONDITION_TOKENS:
            if token in lowered:
                reasons.append(
                    "any_live_paper_order_api_credential_field:" + str(key))
    mapping = {"breakout_present": "no_breakout",
               "retest_present": "failed_retest",
               "continuation_confirmed":
                   "missing_continuation_confirmation"}
    for name in _REQUIRED_CONDITIONS:
        if conditions.get(name) is not True:
            reasons.append(mapping[name])
    if conditions.get("breakout_failed") is True:
        reasons.append("failed_retest")
    if conditions.get("ambiguous") is True:
        reasons.append("ambiguous_structure")
    if conditions.get("insufficient_candles") is True:
        reasons.append("insufficient_candles")
    viability = evaluate_setup_cost_viability(
        conditions.get("proposed_entry_price"),
        conditions.get("proposed_stop_price"))
    result["risk_distance_bps"] = viability.get(
        "entry_to_stop_distance_bps")
    if viability.get("viable") is not True:
        reasons.append("risk_distance_below_81_bps")
    result["verdict"] = (VERDICT_SETUP_REJECTED if reasons
                         else VERDICT_SETUP_COMPLETE)
    return result


def build_candidate_asset_instance() -> dict[str, Any]:
    """Candidate #2 as a mutable-candidate-asset INSTANCE conforming to the
    pushed asset spec. Pure; research proposal only."""
    return {
        "fields": {
            "candidate_id": CANDIDATE_ID,
            "candidate_family": CANDIDATE_FAMILY,
            "hypothesis": ("intraday range breakouts that pull back to and "
                           "hold the broken structure, then confirm "
                           "continuation on 15m closes, mark repeatable "
                           "directional moves with risk units wide enough "
                           "to survive real taker costs"),
            "market_scope": "crypto_spot_research",
            "symbol_scope": ",".join(REQUIRED_SYMBOLS),
            "timeframe_scope": "1h_15m_context_15m_trigger_no_1m_scalp",
            "session_filter": EVALUATION_WINDOW,
            "entry_rules_text": DETERMINISTIC_RULES["entry_rule"],
            "exit_rules_text": DETERMINISTIC_RULES["target_rule"],
            "risk_rules_text": DETERMINISTIC_RULES["stop_rule"],
            "parameters": {
                "range_lookback_bars_15m": RANGE_LOOKBACK_BARS_15M,
                "breakout_close_threshold_bps":
                    BREAKOUT_CLOSE_THRESHOLD_BPS,
                "breakout_body_min_fraction": BREAKOUT_BODY_MIN_FRACTION,
                "retest_tolerance_bps": RETEST_TOLERANCE_BPS,
                "max_pullback_depth_fraction": MAX_PULLBACK_DEPTH_FRACTION,
                "breakout_failure_range_fraction":
                    BREAKOUT_FAILURE_RANGE_FRACTION,
                "atr_period": ATR_PERIOD,
                "atr_stop_multiplier": ATR_STOP_MULTIPLIER,
                "target_r_options": list(TARGET_R_OPTIONS),
                "round_trip_cost_bps": ROUND_TRIP_COST_BPS,
                "minimum_risk_to_round_trip_cost_multiple":
                    COST_FLOOR_MULTIPLIER,
                "minimum_risk_distance_bps": MINIMUM_RISK_DISTANCE_BPS,
                "reject_cost_dominated_setups":
                    REJECT_COST_DOMINATED_SETUPS,
            },
            "constraints": ("all rejection rules apply; 81 bps floor before "
                            "replay eligibility; maker never assumed; "
                            "research only"),
            "rationale": ("candidate #2 after the cost-non-viable rejection "
                          "of the 1m FVG/CHOCH scalp candidate; chosen for "
                          "naturally wider structural risk units"),
            "lineage": ("new_family_after_rejection_of:"
                        + REJECTED_CANDIDATE_ID),
            "status": "draft",
            "audit_notes": ("spec block only; detector/replay not built; "
                            "candidate #1 evidence kept on record"),
        },
        "research_only": True,
        "live_trading_authorized": False,
        "paper_trading_authorized": False,
        "human_review_required": True,
        "optimizer_may_edit": True,
        "locked_instructions_may_edit": False,
        "locked_scorer_may_edit": False,
    }


def record_breakout_pullback_strategy_spec(
        family_decision_verdict: Any) -> dict[str, Any]:
    """Assemble the spec, gated on the recorded family decision AND on the
    instance conforming to the pushed asset spec. Pure."""
    spec: dict[str, Any] = {
        "schema_version": BP_SCHEMA_VERSION, "label": BP_LABEL,
        "mode": BP_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [],
        "candidate_id": CANDIDATE_ID,
        "candidate_family": CANDIDATE_FAMILY,
        "family_decision_verdict": family_decision_verdict,
        "rejected_predecessor": REJECTED_CANDIDATE_ID,
        "predecessor_revived": False,
        "required_symbols": list(REQUIRED_SYMBOLS),
        "context_timeframes": list(CONTEXT_TIMEFRAMES),
        "trigger_timeframe": TRIGGER_TIMEFRAME,
        "no_1m_scalp_entry_geometry": NO_1M_SCALP_ENTRY_GEOMETRY,
        "evaluation_window": EVALUATION_WINDOW,
        "deterministic_rules": dict(DETERMINISTIC_RULES),
        "target_r_options": list(TARGET_R_OPTIONS),
        "cost_viability": {
            "round_trip_cost_bps": ROUND_TRIP_COST_BPS,
            "minimum_risk_to_round_trip_cost_multiple":
                COST_FLOOR_MULTIPLIER,
            "minimum_risk_distance_bps": MINIMUM_RISK_DISTANCE_BPS,
            "reject_cost_dominated_setups": REJECT_COST_DOMINATED_SETUPS},
        "rejection_rules": list(REJECTION_RULES),
        "forbidden": list(FORBIDDEN),
        "maker_execution_assumed": False,
        "cost_floor_lowered": False,
        "research_only": True, "live_trading_authorized": False,
        "paper_trading_authorized": False, "human_review_required": True,
        "modifies_mission_flow": False, "modifies_pm_lane": False,
        "modifies_locked_scorer": False,
        "modifies_locked_instructions": False,
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
    if family_decision_verdict != VERDICT_NF_RECORDED:
        spec["verdict"] = VERDICT_BP_BLOCKED
        spec["blockers"].append("next_family_decision_not_recorded")
        return spec
    instance_check = validate_candidate_asset(build_candidate_asset_instance())
    if instance_check.get("verdict") != VERDICT_ASSET_ACCEPTED:
        spec["verdict"] = VERDICT_BP_BLOCKED
        spec["blockers"].append("instance_does_not_conform_to_asset_spec")
        spec["blockers"].extend(instance_check.get("errors") or [])
        return spec
    spec["verdict"] = VERDICT_BP_READY
    return spec


def build_breakout_pullback_strategy_spec(
        repo_root: Any = "C:/SPARTA_BRAIN") -> dict[str, Any]:
    """Build against the LIVE pushed family decision (which itself verifies
    candidate #1's frozen rejection evidence on disk)."""
    decision = build_next_family_decision(repo_root, tracked_paths=[])
    return record_breakout_pullback_strategy_spec(decision.get("verdict"))


def validate_breakout_pullback_strategy_spec(spec: Any) -> dict[str, Any]:
    """Validate the spec's shape and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(spec, dict):
        return {"valid": False, "errors": ["spec_not_a_dict"]}
    s = spec
    if s.get("verdict") not in (VERDICT_BP_READY, VERDICT_BP_BLOCKED):
        errors.append("bad_verdict")
    if s.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if s.get("candidate_family") != CANDIDATE_FAMILY:
        errors.append("candidate_family_tampered")
    if s.get("candidate_id") == REJECTED_CANDIDATE_ID:
        errors.append("rejected_candidate_revived")
    if s.get("predecessor_revived") is not False:
        errors.append("predecessor_must_never_be_revived")
    if tuple(s.get("required_symbols") or ()) != REQUIRED_SYMBOLS:
        errors.append("symbols_tampered")
    if tuple(s.get("context_timeframes") or ()) != CONTEXT_TIMEFRAMES:
        errors.append("context_timeframes_tampered")
    if s.get("trigger_timeframe") != TRIGGER_TIMEFRAME:
        errors.append("trigger_timeframe_tampered")
    if s.get("no_1m_scalp_entry_geometry") is not True:
        errors.append("1m_scalp_geometry_must_stay_excluded")
    if s.get("deterministic_rules") != DETERMINISTIC_RULES:
        errors.append("deterministic_rules_tampered")
    if tuple(s.get("target_r_options") or ()) != TARGET_R_OPTIONS:
        errors.append("target_options_tampered")
    if s.get("cost_viability") != {
            "round_trip_cost_bps": ROUND_TRIP_COST_BPS,
            "minimum_risk_to_round_trip_cost_multiple":
                COST_FLOOR_MULTIPLIER,
            "minimum_risk_distance_bps": MINIMUM_RISK_DISTANCE_BPS,
            "reject_cost_dominated_setups": REJECT_COST_DOMINATED_SETUPS}:
        errors.append("cost_viability_tampered")
    if tuple(s.get("rejection_rules") or ()) != REJECTION_RULES:
        errors.append("rejection_rules_tampered")
    if tuple(s.get("forbidden") or ()) != FORBIDDEN:
        errors.append("forbidden_list_weakened")
    if s.get("maker_execution_assumed") is not False:
        errors.append("maker_execution_must_never_be_assumed")
    if s.get("cost_floor_lowered") is not False:
        errors.append("cost_floor_must_never_be_lowered")
    if s.get("verdict") == VERDICT_BP_READY and s.get(
            "family_decision_verdict") != VERDICT_NF_RECORDED:
        errors.append("ready_without_recorded_family_decision")
    for key, want in (
        ("research_only", True), ("live_trading_authorized", False),
        ("paper_trading_authorized", False), ("human_review_required", True),
        ("modifies_mission_flow", False), ("modifies_pm_lane", False),
        ("modifies_locked_scorer", False),
        ("modifies_locked_instructions", False),
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
