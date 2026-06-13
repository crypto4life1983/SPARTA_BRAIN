"""SPARTA CANDIDATE #6 DETERMINISTIC STRATEGY SPEC REVIEW (READ-ONLY,
RESEARCH ONLY, SPEC GATE ONLY):
MULTI_SYMBOL_RELATIVE_STRENGTH_ROTATION_FILTER_V1.

Loop stage: candidate_spec. Gives frozen NUMERIC form to every rule of
the candidate #6 hypothesis -- before any detector exists. Gated live on
the pushed family proposal, the pushed Recommendation V1, the pushed
Autopilot Loop V1, and the FIVE-record rejection ledger.

THE FROZEN NUMERICS: 20-bar close-to-close relative strength computed
simultaneously for btcusd/ethusd/solusd on completed 1h bars; STRICT
rank #1 required (ties fail); continuation event = first completed 1h
bar whose close is a fresh 10-bar closing high on the rank-#1 symbol;
entry at that close, evaluation next bar; WIDER stop =
max(1.5 x atr14, entry - lowest low of the last 10 completed bars);
27 bps fees with the 81 bps gross target-distance floor per variant
(2r/3r/4r only) checked before replay eligibility; existing staged 15m
data only, aggregated by the pushed aggregators -- no fetch ever.

Research-only and human-gated forever: no detector implementation here,
no real detection, no labels, no replay, no artifacts, no runner or
scheduler, no paper/live, no order/api/wallet/account/credential
capability, no profitability claim.
"""

from __future__ import annotations

from typing import Any

import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as _loop
import sparta_commander.strategy_factory_candidate_recommendation_v1_contract as _rec
from sparta_commander.multi_symbol_relative_strength_rotation_filter_family_proposal_contract import (
    CANDIDATE_FAMILY,
    CANDIDATE_ID,
    VERDICT_C6P_READY,
    build_candidate_6_family_proposal,
)

C6S_SCHEMA_VERSION = (
    "multi_symbol_relative_strength_rotation_filter_spec_review.v1")
C6S_LABEL = ("SPARTA Candidate #6 Strategy Spec Review "
             "(READ-ONLY, RESEARCH ONLY, RULES DEFINITION, "
             "NOT A RESCUE, NOT A CLAIM)")
C6S_MODE = "RESEARCH_ONLY"
VERDICT_C6S_READY = "CANDIDATE_6_SPEC_REVIEW_READY"
VERDICT_C6S_BLOCKED = "CANDIDATE_6_SPEC_REVIEW_BLOCKED"
NEXT_REQUIRED_ACTION = (
    "HUMAN_APPROVED_CANDIDATE_6_DETECTOR_SPEC_AND_DRY_RUN_PATH")
CURRENT_LOOP_STAGE = "candidate_spec"
NEXT_LOOP_STAGE = "detector_and_label_review"

# 1+2+3. relative strength metric, lookback, universe ------------------------
UNIVERSE = ("BTCUSD", "ETHUSD", "SOLUSD")
TIMEFRAME = "1h"
DIRECTION = "long_only"

RS_METRIC = {
    "metric": "close_to_close_return",
    "formula": "return_20 = close[t] / close[t-20] - 1",
    "lookback_bars_1h": 20,
    "computed_simultaneously_for_all_three_symbols": True,
    "uses_completed_1h_bars_only": True,
    "no_future_bars": True,
    "no_same_bar_lookahead": True,
}

# 4. rank-#1 trigger rule -----------------------------------------------------
RANK_RULE = {
    "rule": ("the candidate symbol's return_20 must be STRICTLY "
             "greater than both other symbols' return_20 at the "
             "trigger bar (strict rank #1)"),
    "additional_rule": "return_20(candidate) > 0",
    "ties_fail": True,
    "rank_evaluated_at_trigger_bar_close": True,
    "no_lookahead": True,
}

# 5. continuation event rule --------------------------------------------------
CONTINUATION_EVENT = {
    "rule": ("first completed 1h bar whose close is a fresh 10-bar "
             "closing high on the rank-#1 symbol (close strictly "
             "greater than the maximum close of the prior 10 completed "
             "bars) while the rank rule holds at that bar"),
    "closing_high_lookback_bars": 10,
    "entry_price": "close_of_the_event_bar",
    "evaluation_starts": "next_1h_bar_after_event_close",
    "one_setup_per_event_bar": True,
    "no_intrabar_entry": True,
    "not_a_delayed_pullback_resumption": True,
}

# 6. WIDER-stop rule ----------------------------------------------------------
STOP_RULE = {
    "atr_length": 14,
    "atr_uses_completed_1h_bars_only_standard_true_range": True,
    "atr_multiplier": 1.5,
    "structure_stop_distance": ("entry_price - lowest low of the last "
                                "10 completed 1h bars"),
    "structure_lookback_bars": 10,
    "stop_distance": "max(1.5 * atr14, structure_stop_distance)",
    "stop_price": "entry_price - stop_distance",
    "stop_must_be_below_entry": True,
    "invalid_if_stop_distance_not_positive": True,
    "wider_stop_rule_mandatory_no_tightening": True,
}

# 7. staged data boundary -----------------------------------------------------
DATA_BOUNDARY = {
    "source": ("existing append-only staged 15m candles only "
               "(data/ny_fvg_choch/staged/, sha-pinned manifests)"),
    "aggregation": ("15m to 1h by the pushed aggregator, complete "
                    "4-quarter hours only"),
    "sample_tag": "2026-05-02_2026-06-10",
    "no_fetch_ever": True,
    "no_real_time_data": True,
    "staged_data_never_modified": True,
}

# 8+9. fee-aware geometry -------------------------------------------------------
FEE_GEOMETRY = {
    "fee_model_round_trip_bps": 27,
    "minimum_gross_target_distance_floor_bps": 81,
    "floor_is_3x_round_trip_fees": True,
    "applies_per_target_variant": True,
    "checked_before_replay_eligibility": True,
    "no_maker_rebate_assumption": True,
    "no_zero_fee_assumption": True,
}
TARGET_VARIANTS = ("2r", "3r", "4r")
TARGET_RULES = {
    "variants": TARGET_VARIANTS,
    "no_new_variants_after_label_freeze": True,
    "target_price_formula": "entry_price + r_multiple * stop_distance",
}

# non-overlap + edit policy (inherited from the pushed proposal) --------------
NON_OVERLAP = {
    "built_in_at_label_replay_policy_time": True,
    "evaluated_per_variant": True,
    "reduce_or_keep_only_never_add_trades": True,
}
EDIT_POLICY = {
    "maximum_pre_committed_edits": 1,
    "edit_requires_separate_human_approval": True,
}

# 11. claim locks ----------------------------------------------------------------
CLAIM_LOCKS = (
    "no_profitability_claim",
    "no_paper_approval",
    "no_live_approval",
    "no_execution_approval",
    "no_winner_wording",
    "promotion_can_only_produce_a_human_review_record",
)


def get_candidate_6_spec_review_label() -> str:
    return C6S_LABEL


def build_candidate_6_spec_review() -> dict[str, Any]:
    """Assemble the spec review, gated on the pushed proposal, the
    recommendation, the loop, and the five-record ledger all certifying
    live (the proposal itself enforces the ledger and preferred-pick
    gates)."""
    record: dict[str, Any] = {
        "schema_version": C6S_SCHEMA_VERSION, "label": C6S_LABEL,
        "mode": C6S_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [],
        "candidate_id": CANDIDATE_ID,
        "candidate_family": CANDIDATE_FAMILY,
        "universe": list(UNIVERSE), "timeframe": TIMEFRAME,
        "direction": DIRECTION,
        "rs_metric": dict(RS_METRIC),
        "rank_rule": dict(RANK_RULE),
        "continuation_event": dict(CONTINUATION_EVENT),
        "stop_rule": dict(STOP_RULE),
        "data_boundary": dict(DATA_BOUNDARY),
        "fee_geometry": dict(FEE_GEOMETRY),
        "target_rules": {"variants": list(TARGET_VARIANTS),
                         "no_new_variants_after_label_freeze": True,
                         "target_price_formula":
                             TARGET_RULES["target_price_formula"]},
        "non_overlap": dict(NON_OVERLAP),
        "edit_policy": dict(EDIT_POLICY),
        "rejection_conditions": list(_loop.AUTO_REJECTION_RULES),
        "claim_locks": list(CLAIM_LOCKS),
        "current_loop_stage": CURRENT_LOOP_STAGE,
        "next_loop_stage": NEXT_LOOP_STAGE,
        "human_review_required": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True, "live_gate_locked": True,
        "executes": False, "writes_files": False, "labels_now": False,
        "runs_real_detection_now": False, "runs_replay_now": False,
        "scores_now": False, "stages_data_now": False,
        "fetches_data": False, "calls_api": False, "uses_network": False,
        "uses_credentials": False, "uses_wallet": False,
        "uses_account": False, "connects_broker": False,
        "connects_exchange": False, "uses_real_money": False,
        "contains_order_logic": False,
        "contains_portfolio_allocation_logic": False,
        "starts_scheduler": False, "sends_notifications": False,
        "auto_commits": False, "auto_pushes": False,
        "creates_runners_now": False, "creates_data_artifacts_now": False,
        "creates_detector_implementation_now": False,
        "modifies_staged_market_data": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False, "authorizes_live_trading": False,
        "promotes_gate": False, "unlocks_downstream_gate": False,
        "claims_profitability": False,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    proposal = build_candidate_6_family_proposal()
    if proposal["verdict"] != VERDICT_C6P_READY:
        record["verdict"] = VERDICT_C6S_BLOCKED
        record["blockers"].append("candidate_6_proposal_not_certifying")
        record["blockers"].extend(proposal["blockers"])
        return record
    if _rec.build_candidate_recommendation()["verdict"] != (
            _rec.VERDICT_CR_READY):
        record["verdict"] = VERDICT_C6S_BLOCKED
        record["blockers"].append("recommendation_not_certifying")
        return record
    if _loop.build_autopilot_loop_contract()["verdict"] != (
            _loop.VERDICT_AP_READY):
        record["verdict"] = VERDICT_C6S_BLOCKED
        record["blockers"].append("autopilot_loop_not_certifying")
        return record
    record["verdict"] = VERDICT_C6S_READY
    return record


def validate_candidate_6_spec_review(record: Any) -> dict[str, Any]:
    """Validate shape, frozen numerics, and safety invariants. Never
    raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_C6S_READY, VERDICT_C6S_BLOCKED):
        errors.append("bad_verdict")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if r.get("universe") != ["BTCUSD", "ETHUSD", "SOLUSD"]:
        errors.append("universe_tampered")
    if r.get("timeframe") != "1h" or r.get("direction") != "long_only":
        errors.append("timeframe_or_direction_tampered")
    rs = r.get("rs_metric") or {}
    if rs != RS_METRIC:
        errors.append("rs_metric_tampered")
    if rs.get("metric") != "close_to_close_return":
        errors.append("rs_metric_definition_missing_or_altered")
    if rs.get("lookback_bars_1h") != 20:
        errors.append("rs_lookback_missing_or_altered")
    if rs.get("uses_completed_1h_bars_only") is not True \
            or rs.get("no_future_bars") is not True \
            or rs.get("no_same_bar_lookahead") is not True:
        errors.append("rs_lookahead_protection_weakened")
    rank = r.get("rank_rule") or {}
    if rank != RANK_RULE:
        errors.append("rank_rule_tampered")
    if "strict rank #1" not in str(rank.get("rule") or "") \
            or rank.get("ties_fail") is not True:
        errors.append("rank_1_trigger_missing_or_altered")
    continuation = r.get("continuation_event") or {}
    if continuation != CONTINUATION_EVENT:
        errors.append("continuation_event_tampered")
    if continuation.get("closing_high_lookback_bars") != 10 \
            or continuation.get("evaluation_starts") != (
            "next_1h_bar_after_event_close"):
        errors.append("continuation_event_missing_or_altered")
    if continuation.get(
            "not_a_delayed_pullback_resumption") is not True:
        errors.append("c5_rescue_protection_weakened")
    stop = r.get("stop_rule") or {}
    if stop != STOP_RULE:
        errors.append("stop_rule_tampered")
    if stop.get("atr_length") != 14 or stop.get("atr_multiplier") != 1.5:
        errors.append("stop_numbers_missing_or_altered")
    if stop.get("stop_distance") != (
            "max(1.5 * atr14, structure_stop_distance)") \
            or stop.get(
            "wider_stop_rule_mandatory_no_tightening") is not True:
        errors.append("wider_stop_rule_missing_or_altered")
    boundary = r.get("data_boundary") or {}
    if boundary != DATA_BOUNDARY:
        errors.append("data_boundary_tampered")
    if boundary.get("no_fetch_ever") is not True \
            or boundary.get("staged_data_never_modified") is not True:
        errors.append("data_boundary_weakened")
    fee = r.get("fee_geometry") or {}
    if fee != FEE_GEOMETRY:
        errors.append("fee_geometry_tampered")
    if fee.get("fee_model_round_trip_bps") != 27:
        errors.append("fee_bps_missing_or_altered")
    if fee.get("minimum_gross_target_distance_floor_bps") != 81:
        errors.append("floor_81bps_missing_or_altered")
    targets = r.get("target_rules") or {}
    if targets.get("variants") != ["2r", "3r", "4r"]:
        errors.append("target_variants_tampered")
    if r.get("non_overlap") != NON_OVERLAP:
        errors.append("non_overlap_tampered")
    edit = r.get("edit_policy") or {}
    if edit.get("maximum_pre_committed_edits") != 1 or edit.get(
            "edit_requires_separate_human_approval") is not True:
        errors.append("edit_policy_tampered")
    if tuple(r.get("rejection_conditions") or ()) != (
            _loop.AUTO_REJECTION_RULES):
        errors.append("rejection_conditions_tampered")
    if tuple(r.get("claim_locks") or ()) != CLAIM_LOCKS:
        errors.append("claim_locks_tampered")
    if r.get("next_loop_stage") != "detector_and_label_review":
        errors.append("next_stage_tampered")
    for key, want in (("human_review_required", True),
                      ("paper_trading_gate_locked", True),
                      ("micro_live_gate_locked", True),
                      ("live_gate_locked", True)):
        if r.get(key) is not want:
            errors.append("constitution_flag_wrong:" + key)
    for key in ("executes", "writes_files", "labels_now",
                "runs_real_detection_now", "runs_replay_now",
                "scores_now", "stages_data_now", "fetches_data",
                "calls_api", "uses_network", "uses_credentials",
                "uses_wallet", "uses_account", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic",
                "contains_portfolio_allocation_logic",
                "starts_scheduler", "sends_notifications",
                "auto_commits", "auto_pushes", "creates_runners_now",
                "creates_data_artifacts_now",
                "creates_detector_implementation_now",
                "modifies_staged_market_data",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate", "claims_profitability"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    return {"valid": not errors, "errors": errors}
