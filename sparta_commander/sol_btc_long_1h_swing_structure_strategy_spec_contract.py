"""SPARTA CANDIDATE #4 STRATEGY SPEC CONTRACT (READ-ONLY, RESEARCH ONLY):
SOL_BTC_LONG_1H_SWING_STRUCTURE_V1.

A NEW candidate family, started by explicit human decision
(HUMAN_DECISION_ON_NEXT_CANDIDATE_FAMILY, 2026-06-12), built strictly on
the frozen NEW-FAMILY seeds -- never as a rescue of candidates #1, #2 or
#3, all of which stay REJECTED_KEPT_ON_RECORD. This contract is BLOCKED
if ANY of the three ledger constants ever changes.

SEEDS (research inputs, frozen):
  1. BTC/SOL long-side strength (candidate #2 frozen evidence).
  2. SOL produced 7 of 9 accepted labels in candidate #3 V1.
  3. All accepted setups used STRUCTURAL stops with healthy 92-151 bps
     risk geometry.

THESIS: the three honest kills teach one lesson -- 15m micro-structure is
either cost-non-viable (#1: 2.6-39.7 bps risk units) or too scarce
(#3: 9 accepts in 711 attempts), while the setups that DID survive were
structural-stop setups whose risk geometry (92-151 bps) lives naturally
ONE TIMEFRAME UP. Candidate #4 therefore moves execution to 1h swing
structure: long-only SOL/BTC higher-low swings in a 4h uptrend, entered
on a 1h close above the inter-swing high, stopped below the higher swing
low. 1h structural distances should clear the 81 bps floor by default
instead of fighting it.

Inherited honesty DNA, never weakened: 81 bps floor checked AT LABEL TIME
via the pushed cost-viability module; 27 bps fee-honest round trip at any
future replay; structural-vs-ATR WIDER stop; maker execution never
assumed; completed-bars-only anti-lookahead; pre-committed failure rules;
no profitability claim regardless of outcome without human-owned gates.

This module defines rules only. It runs nothing, labels nothing, fetches
nothing, and authorizes nothing.
"""

from __future__ import annotations

from typing import Any

from sparta_commander.btc_sol_long_trend_continuation_v1_result_and_rejection_record_contract import (
    REJECTION_REASON as C3_REASON,
    REJECTION_STATUS as C3_STATUS,
)
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

C4_SCHEMA_VERSION = "sol_btc_long_1h_swing_structure_strategy_spec.v1"
C4_LABEL = ("SPARTA Candidate #4 Strategy Spec "
            "(READ-ONLY, RESEARCH ONLY, RULES DEFINITION, NEW FAMILY, "
            "NOT A RESCUE)")
C4_MODE = "RESEARCH_ONLY"
VERDICT_C4_READY = "CANDIDATE_4_STRATEGY_SPEC_READY"
VERDICT_C4_BLOCKED = "CANDIDATE_4_STRATEGY_SPEC_BLOCKED"
NEXT_REQUIRED_ACTION = (
    "HUMAN_APPROVED_CANDIDATE_4_DETECTOR_SPEC_AND_DRY_RUN_PATH")

CANDIDATE_ID = "SOL_BTC_LONG_1H_SWING_STRUCTURE_V1"
CANDIDATE_FAMILY = "long_1h_swing_structure"

FROZEN_SEED_INPUTS = (
    "btc_sol_long_side_strength_from_candidate_2",
    "sol_produced_7_of_9_accepted_labels_in_candidate_3_v1",
    "structural_stop_setups_with_healthy_92_to_151_bps_risk_geometry",
)

THESIS = (
    "15m micro-structure proved cost-non-viable (#1) or too scarce (#3); "
    "the surviving setups were structural-stop setups with 92-151 bps "
    "risk geometry, SOL-weighted and long-side; candidate #4 moves "
    "execution one timeframe up to 1h swing structure where structural "
    "stop distances clear the 81 bps floor by default")

# --- deterministic strategy rules (frozen) ---------------------------------

SYMBOLS = ("SOLUSD", "BTCUSD")  # SOL first per the seed weighting
DIRECTION = "long_only"
EXECUTION_TIMEFRAME = "1h"
TREND_TIMEFRAME = "4h"
DATA_SOURCE = ("existing append-only staged 15m candles "
               "(data/ny_fvg_choch/staged/, sha-pinned manifests); 1h "
               "bars aggregated strictly from staged 15m (complete "
               "4-quarter hours only); 4h bars aggregated strictly from "
               "those 1h bars (complete 4-hour groups only); no new "
               "staging required and none authorized here")

TREND_QUALIFICATION = {
    "tf": "4h",
    "rule_1": "last_COMPLETED_4h_close_above_4h_sma10",
    "rule_2": "4h_sma10_rising:sma10_now_greater_than_sma10_3_bars_ago",
    "both_required": True,
    "lookahead_note": ("only 4h bars fully completed BEFORE the 1h "
                       "signal bar's open may be used"),
}

SWING_STRUCTURE_RULES = {
    "tf": "1h",
    "swing_low_definition": ("a 1h bar whose low is strictly lower than "
                             "the lows of the 2 bars before it and the "
                             "2 bars after it (confirmed only 2 bars "
                             "later -- no lookahead at detection time)"),
    "setup": ("two consecutive confirmed swing lows SL1 then SL2 with "
              "SL2 low strictly higher than SL1 low (higher-low "
              "structure)"),
    "inter_swing_high": ("the highest 1h high strictly between SL1 and "
                         "SL2 bars"),
    "max_bars_between_swings": 48,
    "max_bars_from_sl2_to_entry": 24,
}

ENTRY_RULES = {
    "trigger": ("first completed 1h bar after SL2 confirmation that "
                "CLOSES above the inter-swing high"),
    "entry_price": "close_of_the_trigger_bar",
    "anti_lookahead": ("entry is recorded at the trigger bar CLOSE; any "
                       "replay starts at the NEXT 1h bar open"),
    "invalidation_before_entry": ("if any 1h low prints below SL2 low "
                                  "before the trigger, the setup is "
                                  "void"),
    "one_setup_per_swing_pair": True,
}

STOP_RULES = {
    "structural_stop": "low_of_SL2_the_higher_swing_low",
    "volatility_stop": "entry_minus_1_5x_atr14_on_1h",
    "selection": "WIDER_of_structural_and_volatility_stop_always",
    "never_tightened_after_entry": True,
}

TARGET_VARIANTS = ("2r", "3r", "4r")

COST_DISCIPLINE = {
    "minimum_risk_distance_bps": MINIMUM_RISK_DISTANCE_BPS,  # 81 = 27 x 3
    "checked_at_label_time_via":
        "ny_session_fvg_choch_mutable_candidate_edit_v2_cost_viability"
        ".evaluate_setup_cost_viability",
    "assumed_round_trip_cost_bps": 27,
    "maker_execution_assumed": False,
    "floor_may_be_lowered": False,
}

PRE_COMMITTED_FAILURE_RULES = (
    "if real-candle detection yields fewer than 10 accepted labels "
    "across both symbols, candidate #4 may receive AT MOST one "
    "separately human-approved mutable edit; if still fewer than 10, "
    "candidate #4 is REJECTED_KEPT_ON_RECORD",
    "if fee-honest replay of accepted labels is net-negative in ALL "
    "target variants, candidate #4 may receive AT MOST one separately "
    "human-approved filter-only edit (reduce-or-equal trade count, "
    "never weaker entries); if still negative, candidate #4 is "
    "REJECTED_KEPT_ON_RECORD",
    "at most ONE mutable edit total for candidate #4, whichever branch "
    "consumes it",
    "zero accepted labels at the 81 bps floor is a valid honest "
    "outcome, not a failure to be engineered around",
    "no profitability claim unless fee-honest replay arithmetic proves "
    "it, and even then the claim gate stays human-owned",
)

NON_RESCUE_GUARANTEES = {
    "candidate_1_status_unchanged": True,
    "candidate_2_status_unchanged": True,
    "candidate_3_status_unchanged": True,
    "candidate_3_not_revived": True,
    "candidate_3_not_mutated_again": True,
    "seeds_are_research_inputs_for_new_family_only": True,
    "distinct_from_candidate_3": (
        "candidate #3 required a 15m impulse-pullback-resumption bar "
        "sequence; candidate #4 uses confirmed 1h swing lows in "
        "higher-low structure with a 4h trend gate -- different "
        "timeframe, different structure definition, no bar-sequence "
        "micro-pattern requirement"),
}

FORBIDDEN = (
    "reviving_candidate_1_2_or_3",
    "mutating_candidate_3_again",
    "lowering_the_81bps_floor",
    "assuming_maker_execution",
    "short_setups",
    "symbols_outside_sol_btc",
    "paper_or_live_capability",
    "profitability_claims",
    "wallet_account_order_trading_api_key_capability",
    "automatic_commit_or_push",
)


def get_candidate_4_spec_label() -> str:
    return C4_LABEL


def validate_candidate_4_spec(record: Any) -> dict[str, Any]:
    """Validate shape and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_C4_READY, VERDICT_C4_BLOCKED):
        errors.append("bad_verdict")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if r.get("candidate_family") != CANDIDATE_FAMILY:
        errors.append("candidate_family_tampered")
    if tuple(r.get("frozen_seed_inputs") or ()) != FROZEN_SEED_INPUTS:
        errors.append("seed_inputs_tampered")
    if r.get("thesis") != THESIS:
        errors.append("thesis_tampered")
    if tuple(r.get("symbols") or ()) != SYMBOLS:
        errors.append("symbols_tampered")
    if r.get("direction") != "long_only":
        errors.append("direction_not_long_only")
    if r.get("execution_timeframe") != "1h" \
            or r.get("trend_timeframe") != "4h":
        errors.append("timeframes_tampered")
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
                "candidate_2_status_unchanged",
                "candidate_3_status_unchanged",
                "candidate_3_not_revived",
                "candidate_3_not_mutated_again",
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
                "claims_profitability", "revives_candidate_3"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    return {"valid": not errors, "errors": errors}


def build_candidate_4_spec() -> dict[str, Any]:
    """Assemble the Candidate #4 spec, gated on ALL THREE rejection
    records being intact (this family cannot exist if the ledger broke)."""
    record: dict[str, Any] = {
        "schema_version": C4_SCHEMA_VERSION, "label": C4_LABEL,
        "mode": C4_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [],
        "candidate_id": CANDIDATE_ID,
        "candidate_family": CANDIDATE_FAMILY,
        "frozen_seed_inputs": list(FROZEN_SEED_INPUTS),
        "thesis": THESIS,
        "symbols": list(SYMBOLS),
        "direction": DIRECTION,
        "execution_timeframe": EXECUTION_TIMEFRAME,
        "trend_timeframe": TREND_TIMEFRAME,
        "data_source": DATA_SOURCE,
        "trend_qualification": dict(TREND_QUALIFICATION),
        "swing_structure_rules": dict(SWING_STRUCTURE_RULES),
        "entry_rules": dict(ENTRY_RULES),
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
        "claims_profitability": False, "revives_candidate_3": False,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    if C1_STATUS != "REJECTED_KEPT_ON_RECORD" \
            or C1_REASON != "COST_NON_VIABLE_RISK_GEOMETRY":
        record["verdict"] = VERDICT_C4_BLOCKED
        record["blockers"].append("candidate_1_ledger_broken")
        return record
    if C2_STATUS != "REJECTED_KEPT_ON_RECORD" or C2_REASON != (
            "EDGE_FAILURE_SURVIVED_ONE_AUTHORIZED_FILTER_EXPERIMENT"):
        record["verdict"] = VERDICT_C4_BLOCKED
        record["blockers"].append("candidate_2_ledger_broken")
        return record
    if C3_STATUS != "REJECTED_KEPT_ON_RECORD" or C3_REASON != (
            "NEAR_ZERO_SETUPS_AFTER_ONE_AUTHORIZED_STRUCTURE_EDIT"):
        record["verdict"] = VERDICT_C4_BLOCKED
        record["blockers"].append("candidate_3_ledger_broken")
        return record
    if MINIMUM_RISK_DISTANCE_BPS != 81:
        record["verdict"] = VERDICT_C4_BLOCKED
        record["blockers"].append("risk_floor_constant_changed_upstream")
        return record
    record["verdict"] = VERDICT_C4_READY
    return record
