"""SPARTA CANDIDATE #3 STRATEGY SPEC CONTRACT (READ-ONLY, RESEARCH ONLY):
BTC_SOL_LONG_TREND_CONTINUATION_V1.

A NEW candidate family, started by explicit human decision
(HUMAN_DECISION_ON_NEXT_CANDIDATE_FAMILY, 2026-06-12). It is NOT a rescue,
revival, or mutation of Candidate #2 (or #1) -- both stay
REJECTED_KEPT_ON_RECORD, and this contract is BLOCKED if either ledger
constant ever changes.

Research inputs are restricted to the THREE frozen seed observations from
Candidate #2's closed evidence (used as direction-setting inputs for a new
family, never as rescue paths):
  1. BTC was net-positive across Candidate #2 V2 variants (n=5, small).
  2. SOL was net-positive at 3R and 4R.
  3. The long side was materially stronger than shorts.

Inherited honesty DNA, never weakened: 81 bps minimum risk-distance floor
checked AT LABEL TIME via the pushed cost-viability module; 27 bps
fee-honest round-trip cost at replay; structural-vs-ATR WIDER stop; maker
execution never assumed; anti-lookahead replay; no profitability claim
unless fee-honest replay arithmetic proves it -- and even then the claim
gate stays human-owned.

This module defines rules only. It runs nothing, labels nothing, fetches
nothing, and authorizes nothing.
"""

from __future__ import annotations

from typing import Any

from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (
    REJECTION_REASON as C2_REASON,
    REJECTION_STATUS as C2_STATUS,
)
from sparta_commander.ny_session_fvg_choch_mutable_candidate_edit_v2_cost_viability import (
    MINIMUM_RISK_DISTANCE_BPS,
)
from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
    REJECTION_REASON as C1_REASON,
    REJECTION_STATUS as C1_STATUS,
)

TC_SCHEMA_VERSION = "btc_sol_long_trend_continuation_strategy_spec.v1"
TC_LABEL = ("SPARTA Candidate #3 Strategy Spec "
            "(READ-ONLY, RESEARCH ONLY, RULES DEFINITION, NEW FAMILY, "
            "NOT A RESCUE)")
TC_MODE = "RESEARCH_ONLY"
VERDICT_TC_READY = "CANDIDATE_3_STRATEGY_SPEC_READY"
VERDICT_TC_BLOCKED = "CANDIDATE_3_STRATEGY_SPEC_BLOCKED"
NEXT_REQUIRED_ACTION = (
    "HUMAN_APPROVED_CANDIDATE_3_DETECTOR_SPEC_AND_DRY_RUN_PATH")

CANDIDATE_ID = "BTC_SOL_LONG_TREND_CONTINUATION_V1"
CANDIDATE_FAMILY = "long_biased_trend_continuation"

FROZEN_SEED_INPUTS = (
    "btc_was_net_positive_in_all_variants_small_sample",
    "sol_was_net_positive_at_3r_and_4r",
    "long_side_was_materially_stronger_than_shorts",
)

# --- deterministic strategy rules (frozen) ---------------------------------

SYMBOLS = ("BTCUSD", "SOLUSD")
DIRECTION = "long_only"
EXECUTION_TIMEFRAME = "15m"
TREND_TIMEFRAME = "1h"
DATA_SOURCE = ("existing append-only staged 15m candles "
               "(data/ny_fvg_choch/staged/, 21 session days, "
               "sha-pinned manifests); 1h bars aggregated strictly from "
               "staged 15m, complete 4-quarter hours only; no new staging "
               "required and none authorized here")

TREND_QUALIFICATION = {
    "tf": "1h",
    "rule_1": "last_COMPLETED_1h_close_above_1h_sma20",
    "rule_2": "1h_sma20_rising:sma20_now_greater_than_sma20_5_bars_ago",
    "both_required": True,
    "lookahead_note": ("only 1h bars fully completed BEFORE the 15m "
                       "signal bar's open may be used"),
}

PULLBACK_RULES = {
    "tf": "15m",
    "impulse_leg": ("a new 20-bar 15m closing high must have printed "
                    "within the last 8 completed 15m bars"),
    "pullback_definition": ("at least 2 and at most 8 consecutive "
                            "completed 15m bars, each with a lower low "
                            "than the prior bar"),
    "pullback_floor": ("every pullback bar low must hold above the most "
                       "recent 15m swing low (lowest low of the 20 bars "
                       "preceding the impulse high)"),
    "max_pullback_depth": ("pullback may retrace at most 61.8 percent of "
                           "the impulse leg (swing low to impulse high)"),
}

RESUMPTION_ENTRY = {
    "trigger": ("first completed 15m bar that CLOSES above the highest "
                "high of the pullback bars"),
    "entry_price": "close_of_the_resumption_bar",
    "anti_lookahead": ("entry is recorded at the resumption bar CLOSE; "
                       "any replay starts at the NEXT 15m bar open"),
    "one_setup_per_impulse": True,
}

STOP_RULES = {
    "structural_stop": "lowest_low_of_the_pullback_bars",
    "volatility_stop": "entry_minus_1_5x_atr14_on_15m",
    "selection": "WIDER_of_structural_and_volatility_stop_always",
    "never_tightened_after_entry": True,
}

TARGET_VARIANTS = ("2r", "3r", "4r")

COST_DISCIPLINE = {
    "minimum_risk_distance_bps": MINIMUM_RISK_DISTANCE_BPS,  # 81 = 27 x 3
    "checked_at_label_time_via":
        "ny_session_fvg_choch_mutable_candidate_edit_v2_cost_viability"
        ".evaluate_setup_cost_viability",
    "assumed_round_trip_cost_bps": 27,  # 20 taker + 2 spread + 5 slippage
    "maker_execution_assumed": False,
    "floor_may_be_lowered": False,
}

PRE_COMMITTED_FAILURE_RULES = (
    "if fee-honest replay of accepted labels is net-negative in ALL "
    "target variants, the candidate receives AT MOST one authorized "
    "mutable filter-only edit (reduce-or-equal trade count, never weaker "
    "entries); if still negative, candidate #3 is REJECTED_KEPT_ON_RECORD",
    "zero accepted labels at the 81 bps floor is a valid honest outcome, "
    "not a failure to be engineered around",
    "no profitability claim unless fee-honest replay arithmetic proves "
    "it, and even then the claim gate stays human-owned",
)

NON_RESCUE_GUARANTEES = {
    "candidate_1_status_unchanged": True,
    "candidate_2_status_unchanged": True,
    "candidate_2_not_revived": True,
    "candidate_2_not_mutated": True,
    "seeds_are_research_inputs_for_new_family_only": True,
    "distinct_from_candidate_2": (
        "candidate #2 entered on breakout-of-range plus retest across 6 "
        "symbols both directions; candidate #3 is long-only BTC/SOL "
        "trend-continuation: qualified 1h uptrend, 15m impulse-pullback-"
        "resumption structure, no range breakout requirement"),
}

FORBIDDEN = (
    "reviving_or_mutating_candidate_2",
    "reviving_candidate_1",
    "lowering_the_81bps_floor",
    "assuming_maker_execution",
    "short_setups",
    "symbols_outside_btc_sol",
    "paper_or_live_capability",
    "profitability_claims",
    "wallet_account_order_trading_api_key_capability",
    "automatic_commit_or_push",
)


def get_candidate_3_spec_label() -> str:
    return TC_LABEL


def validate_candidate_3_spec(record: Any) -> dict[str, Any]:
    """Validate shape and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_TC_READY, VERDICT_TC_BLOCKED):
        errors.append("bad_verdict")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if r.get("candidate_family") != CANDIDATE_FAMILY:
        errors.append("candidate_family_tampered")
    if tuple(r.get("frozen_seed_inputs") or ()) != FROZEN_SEED_INPUTS:
        errors.append("seed_inputs_tampered")
    if tuple(r.get("symbols") or ()) != SYMBOLS:
        errors.append("symbols_tampered")
    if r.get("direction") != "long_only":
        errors.append("direction_not_long_only")
    cost = r.get("cost_discipline") or {}
    if cost.get("minimum_risk_distance_bps") != MINIMUM_RISK_DISTANCE_BPS:
        errors.append("risk_floor_tampered")
    if cost.get("assumed_round_trip_cost_bps") != 27:
        errors.append("fee_model_tampered")
    if cost.get("maker_execution_assumed") is not False:
        errors.append("maker_execution_assumed")
    if cost.get("floor_may_be_lowered") is not False:
        errors.append("floor_lowering_enabled")
    stops = r.get("stop_rules") or {}
    if stops.get("selection") != (
            "WIDER_of_structural_and_volatility_stop_always"):
        errors.append("stop_selection_weakened")
    if tuple(r.get("pre_committed_failure_rules") or ()) != (
            PRE_COMMITTED_FAILURE_RULES):
        errors.append("failure_rules_tampered")
    guarantees = r.get("non_rescue_guarantees") or {}
    for key in ("candidate_1_status_unchanged",
                "candidate_2_status_unchanged", "candidate_2_not_revived",
                "candidate_2_not_mutated",
                "seeds_are_research_inputs_for_new_family_only"):
        if guarantees.get(key) is not True:
            errors.append("non_rescue_guarantee_missing:" + key)
    if tuple(r.get("forbidden") or ()) != FORBIDDEN:
        errors.append("forbidden_list_weakened")
    for key, want in (("human_review_required", True),
                      ("paper_trading_gate_locked", True),
                      ("micro_live_gate_locked", True),
                      ("live_gate_locked", True)):
        if r.get(key) is not want:
            errors.append("constitution_flag_wrong:" + key)
    for key in ("executes", "writes_files", "labels_now",
                "runs_detector_now", "runs_replay_now", "scores_now",
                "stages_data_now", "fetches_data", "calls_api",
                "uses_network", "uses_credentials", "uses_wallet",
                "connects_broker", "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate",
                "claims_profitability", "revives_candidate_2"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    return {"valid": not errors, "errors": errors}


def build_candidate_3_spec() -> dict[str, Any]:
    """Assemble the Candidate #3 spec, gated on BOTH rejection records
    being intact (this family cannot exist if the ledger broke)."""
    record: dict[str, Any] = {
        "schema_version": TC_SCHEMA_VERSION, "label": TC_LABEL,
        "mode": TC_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [],
        "candidate_id": CANDIDATE_ID,
        "candidate_family": CANDIDATE_FAMILY,
        "frozen_seed_inputs": list(FROZEN_SEED_INPUTS),
        "symbols": list(SYMBOLS),
        "direction": DIRECTION,
        "execution_timeframe": EXECUTION_TIMEFRAME,
        "trend_timeframe": TREND_TIMEFRAME,
        "data_source": DATA_SOURCE,
        "trend_qualification": dict(TREND_QUALIFICATION),
        "pullback_rules": dict(PULLBACK_RULES),
        "resumption_entry": dict(RESUMPTION_ENTRY),
        "stop_rules": dict(STOP_RULES),
        "target_variants": list(TARGET_VARIANTS),
        "cost_discipline": dict(COST_DISCIPLINE),
        "pre_committed_failure_rules": list(PRE_COMMITTED_FAILURE_RULES),
        "non_rescue_guarantees": dict(NON_RESCUE_GUARANTEES),
        "forbidden": list(FORBIDDEN),
        "human_review_required": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True, "live_gate_locked": True,
        "executes": False, "writes_files": False, "labels_now": False,
        "runs_detector_now": False, "runs_replay_now": False,
        "scores_now": False, "stages_data_now": False,
        "fetches_data": False, "calls_api": False, "uses_network": False,
        "uses_credentials": False, "uses_wallet": False,
        "connects_broker": False, "connects_exchange": False,
        "uses_real_money": False, "contains_order_logic": False,
        "starts_scheduler": False, "sends_notifications": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False, "authorizes_live_trading": False,
        "promotes_gate": False, "unlocks_downstream_gate": False,
        "claims_profitability": False, "revives_candidate_2": False,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    if C1_STATUS != "REJECTED_KEPT_ON_RECORD" \
            or C1_REASON != "COST_NON_VIABLE_RISK_GEOMETRY":
        record["verdict"] = VERDICT_TC_BLOCKED
        record["blockers"].append("candidate_1_ledger_broken")
        return record
    if C2_STATUS != "REJECTED_KEPT_ON_RECORD" or C2_REASON != (
            "EDGE_FAILURE_SURVIVED_ONE_AUTHORIZED_FILTER_EXPERIMENT"):
        record["verdict"] = VERDICT_TC_BLOCKED
        record["blockers"].append("candidate_2_ledger_broken")
        return record
    if MINIMUM_RISK_DISTANCE_BPS != 81:
        record["verdict"] = VERDICT_TC_BLOCKED
        record["blockers"].append("risk_floor_constant_changed_upstream")
        return record
    record["verdict"] = VERDICT_TC_READY
    return record
