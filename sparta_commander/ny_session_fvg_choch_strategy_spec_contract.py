"""SPARTA NY-Session FVG + CHOCH Strategy Spec Contract (READ-ONLY).

The first Crypto-D1 Auto Research candidate: the discretionary NY-session
Fair Value Gap + Change of Character idea converted into DETERMINISTIC,
testable research rules. Spec only: no detector, labeler, replay, backtest,
or optimizer execution exists in this block -- each is a future, separately
human-approved block. Nothing here can authorize any market action.
"""

from __future__ import annotations

from typing import Any

from sparta_commander.crypto_d1_auto_research_mutable_candidate_asset_spec import (
    VERDICT_CA_SPEC_READY,
    build_mutable_candidate_asset_spec,
    validate_candidate_asset,
    validate_mutable_candidate_asset_spec,
)

FS_SCHEMA_VERSION = "ny_session_fvg_choch_strategy_spec_contract.v1"
FS_LABEL = ("SPARTA NY-Session FVG+CHOCH Strategy Spec "
            "(READ-ONLY, SPEC ONLY)")
FS_MODE = "RESEARCH_ONLY"
VERDICT_FS_READY = "NY_FVG_CHOCH_STRATEGY_SPEC_READY"
VERDICT_FS_BLOCKED = "NY_FVG_CHOCH_STRATEGY_SPEC_BLOCKED"
VERDICT_SETUP_COMPLETE = "SETUP_COMPLETE_FOR_RESEARCH"
VERDICT_SETUP_REJECTED = "SETUP_REJECTED"
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_FVG_CHOCH_DETECTOR_SPEC"

CANDIDATE_ID = "NY_SESSION_FVG_CHOCH_STRATEGY_CANDIDATE_V1"
CANDIDATE_FAMILY = "intraday_fvg_choch"

# Session windows: research parameters only; none can authorize anything.
DEFAULT_SESSION_WINDOW = "09:30-12:00 America/New_York"
ALLOWED_TEST_WINDOWS = ("09:30-10:30", "09:30-11:30", "09:30-12:00",
                        "09:30-13:00")

# Deterministic rule text, one frozen definition per concept.
DETERMINISTIC_RULES = {
    "htf_15m_bullish_fvg": ("three consecutive 15m candles where "
                            "candle1.high < candle3.low; the gap "
                            "[candle1.high, candle3.low] is the bullish FVG"),
    "htf_15m_bearish_fvg": ("three consecutive 15m candles where "
                            "candle1.low > candle3.high; the gap "
                            "[candle3.high, candle1.low] is the bearish FVG"),
    "fvg_midpoint": "midpoint = (gap_upper + gap_lower) / 2 (consequential "
                    "encroachment level)",
    "htf_invalidation": "setup invalid if a 15m candle CLOSES fully through "
                        "the higher-timeframe FVG against the setup direction",
    "liquidity_inflection_approx": "nearest prior 15m swing high/low within "
                                   "20 bars treated as the liquidity level",
    "sr_flip_approx": "a level is flipped when price closes beyond it and the "
                      "first retest holds without a close back through",
    "prev_high_low_retest_approx": "previous session high/low touched within "
                                   "0.1% counts as a retest",
    "trigger_1m_bullish_choch": "1m close above the most recent lower-high "
                                "pivot (pivot = high with lower highs on both "
                                "sides, 3-bar fractal)",
    "trigger_1m_bearish_choch": "1m close below the most recent higher-low "
                                "pivot (3-bar fractal)",
    "trigger_1m_fvg": "a 1m FVG (same 3-candle rule) printed by the CHOCH "
                      "impulse leg itself; missing CHOCH or missing 1m FVG "
                      "rejects the setup",
    "fib_alignment": "the 1m FVG midpoint must lie inside the 61.8% "
                     "retracement zone of the CHOCH leg, tolerance "
                     "+/- 5% of the leg range; otherwise reject",
    "entry_rule": "research entry marked at the 1m FVG midpoint, only when "
                  "htf context + 1m CHOCH + 1m FVG + fib alignment are ALL "
                  "present",
    "stop_rule": "research stop marked beyond the FVG-producing candle's "
                 "extreme (response zone); research-only, never live sizing",
    "target_rule": "initial research target at 1:4 risk/reward from the "
                   "marked entry and stop; targets authorize nothing",
    "breakeven_rule": "optional: move research stop to entry only after a "
                      "new 1m structure pivot confirms continuation; a "
                      "future replay rule, never an execution instruction",
}
FIB_LEVEL = 0.618
FIB_TOLERANCE = 0.05
RISK_REWARD_TARGET = 4.0

REJECTION_RULES = (
    "missing_15m_fvg_context",
    "missing_liquidity_or_sr_approximation",
    "missing_1m_choch",
    "missing_1m_fvg",
    "missing_fib_alignment",
    "htf_fvg_closed_through_invalidation",
    "ambiguous_or_low_quality_setup",
    "any_live_or_paper_authorization_claim",
)

FORBIDDEN = (
    "order_placement", "broker_or_exchange_api_calls", "credential_access",
    "wallet_account_login_fields", "live_config_modification",
    "paper_micro_live_promotion", "changing_locked_scorer",
    "changing_locked_instructions", "hidden_rejected_experiments",
    "network_calls", "data_fetching", "backtest_or_replay_execution_here",
)

_REQUIRED_CONDITIONS = ("htf_fvg_present", "liquidity_or_sr_context_present",
                        "choch_1m_present", "fvg_1m_present",
                        "fib_alignment_present")


def get_ny_fvg_choch_strategy_spec_label() -> str:
    """Human label for the recognized NY FVG+CHOCH strategy spec contract."""
    return FS_LABEL


def evaluate_setup_completeness(conditions: Any) -> dict[str, Any]:
    """DETERMINISTIC research gate: a setup is complete only when every
    required condition is True and no invalidation applies. Pure; a complete
    setup is a research observation, never an instruction."""
    result: dict[str, Any] = {"verdict": None, "rejection_reasons": [],
                              "completeness_authorizes_nothing": True}
    if not isinstance(conditions, dict):
        result["verdict"] = VERDICT_SETUP_REJECTED
        result["rejection_reasons"].append("conditions_not_a_dict")
        return result
    reasons = result["rejection_reasons"]
    mapping = {"htf_fvg_present": "missing_15m_fvg_context",
               "liquidity_or_sr_context_present":
                   "missing_liquidity_or_sr_approximation",
               "choch_1m_present": "missing_1m_choch",
               "fvg_1m_present": "missing_1m_fvg",
               "fib_alignment_present": "missing_fib_alignment"}
    for name in _REQUIRED_CONDITIONS:
        if conditions.get(name) is not True:
            reasons.append(mapping[name])
    if conditions.get("htf_fvg_closed_through") is True:
        reasons.append("htf_fvg_closed_through_invalidation")
    if conditions.get("ambiguous") is True:
        reasons.append("ambiguous_or_low_quality_setup")
    if conditions.get("live_authorization_claimed") is True or conditions.get(
            "paper_authorization_claimed") is True:
        reasons.append("any_live_or_paper_authorization_claim")
    result["verdict"] = (VERDICT_SETUP_REJECTED if reasons
                         else VERDICT_SETUP_COMPLETE)
    return result


def build_candidate_asset_instance() -> dict[str, Any]:
    """The strategy as a mutable-candidate-asset INSTANCE conforming to the
    pushed asset spec. Pure; research proposal only."""
    return {
        "fields": {
            "candidate_id": CANDIDATE_ID,
            "candidate_family": CANDIDATE_FAMILY,
            "hypothesis": ("NY-session 15m fair value gaps combined with 1m "
                           "change-of-character triggers and 61.8% "
                           "retracement alignment mark repeatable intraday "
                           "reaction zones"),
            "market_scope": "crypto_spot_research",
            "symbol_scope": "BTC,ETH,SOL",
            "timeframe_scope": "15m_context_1m_trigger",
            "session_filter": DEFAULT_SESSION_WINDOW,
            "entry_rules_text": DETERMINISTIC_RULES["entry_rule"],
            "exit_rules_text": (DETERMINISTIC_RULES["target_rule"] + "; "
                                + DETERMINISTIC_RULES["breakeven_rule"]),
            "risk_rules_text": DETERMINISTIC_RULES["stop_rule"],
            "parameters": {"session_windows": list(ALLOWED_TEST_WINDOWS),
                           "fib_level": FIB_LEVEL,
                           "fib_tolerance": FIB_TOLERANCE,
                           "risk_reward_target": RISK_REWARD_TARGET},
            "constraints": "all rejection rules apply; research only",
            "rationale": "first auto-research candidate; converted from a "
                         "discretionary playbook into deterministic rules",
            "lineage": "root_candidate_no_parent",
            "status": "draft",
            "audit_notes": "spec block only; detector/replay not built",
        },
        "research_only": True,
        "live_trading_authorized": False,
        "paper_trading_authorized": False,
        "human_review_required": True,
        "optimizer_may_edit": True,
        "locked_instructions_may_edit": False,
        "locked_scorer_may_edit": False,
    }


def build_ny_fvg_choch_strategy_spec() -> dict[str, Any]:
    """Assemble the strategy spec, gated on the READY candidate asset spec
    AND on the instance conforming to it. Pure."""
    spec: dict[str, Any] = {
        "schema_version": FS_SCHEMA_VERSION, "label": FS_LABEL, "mode": FS_MODE,
        "lane": "crypto_d1_auto_research", "verdict": None, "blockers": [],
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "default_session_window": DEFAULT_SESSION_WINDOW,
        "allowed_test_windows": list(ALLOWED_TEST_WINDOWS),
        "session_windows_are_research_parameters_only": True,
        "deterministic_rules": dict(DETERMINISTIC_RULES),
        "fib_level": FIB_LEVEL, "fib_tolerance": FIB_TOLERANCE,
        "risk_reward_target": RISK_REWARD_TARGET,
        "rejection_rules": list(REJECTION_RULES),
        "forbidden": list(FORBIDDEN),
        "research_only": True, "live_trading_authorized": False,
        "paper_trading_authorized": False, "human_review_required": True,
        "modifies_mission_flow": False, "modifies_pm_lane": False,
        "modifies_locked_scorer": False, "modifies_locked_instructions": False,
        "executes": False, "writes_files": False, "writes_reports": False,
        "runs_scanner": False, "fetches_data": False, "calls_api": False,
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
    asset_spec = build_mutable_candidate_asset_spec()
    if (not validate_mutable_candidate_asset_spec(asset_spec).get("valid")
            or asset_spec.get("verdict") != VERDICT_CA_SPEC_READY):
        spec["verdict"] = VERDICT_FS_BLOCKED
        spec["blockers"].append("candidate_asset_spec_not_ready")
        return spec
    instance_check = validate_candidate_asset(build_candidate_asset_instance())
    if instance_check.get("verdict") != "CANDIDATE_ASSET_ACCEPTED_FOR_RESEARCH":
        spec["verdict"] = VERDICT_FS_BLOCKED
        spec["blockers"].append("instance_does_not_conform_to_asset_spec")
        spec["blockers"].extend(instance_check.get("errors") or [])
        return spec
    spec["verdict"] = VERDICT_FS_READY
    return spec


def validate_ny_fvg_choch_strategy_spec(spec: Any) -> dict[str, Any]:
    """Validate the spec's shape and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(spec, dict):
        return {"valid": False, "errors": ["spec_not_a_dict"]}
    s = spec
    if s.get("verdict") not in (VERDICT_FS_READY, VERDICT_FS_BLOCKED):
        errors.append("bad_verdict")
    if s.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if s.get("candidate_family") != CANDIDATE_FAMILY:
        errors.append("candidate_family_tampered")
    if tuple(s.get("allowed_test_windows") or ()) != ALLOWED_TEST_WINDOWS:
        errors.append("test_windows_tampered")
    if s.get("deterministic_rules") != DETERMINISTIC_RULES:
        errors.append("deterministic_rules_tampered")
    if tuple(s.get("rejection_rules") or ()) != REJECTION_RULES:
        errors.append("rejection_rules_tampered")
    if tuple(s.get("forbidden") or ()) != FORBIDDEN:
        errors.append("forbidden_list_weakened")
    if s.get("fib_level") != FIB_LEVEL or s.get("fib_tolerance") != FIB_TOLERANCE:
        errors.append("fib_parameters_tampered")
    if s.get("risk_reward_target") != RISK_REWARD_TARGET:
        errors.append("risk_reward_tampered")
    for key, want in (
        ("session_windows_are_research_parameters_only", True),
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
    for key in ("executes", "writes_files", "writes_reports", "runs_scanner",
                "fetches_data", "calls_api", "uses_network", "uses_credentials",
                "uses_wallet", "connects_broker", "connects_exchange",
                "uses_real_money", "contains_order_logic", "starts_scheduler",
                "sends_notifications", "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate"):
        if s.get(key) is not False:
            errors.append("capability_not_false:" + key)
    return {"valid": not errors, "errors": errors}
