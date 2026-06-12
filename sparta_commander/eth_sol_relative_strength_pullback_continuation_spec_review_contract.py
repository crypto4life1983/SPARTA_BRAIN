"""SPARTA CANDIDATE #5 DETERMINISTIC STRATEGY SPEC REVIEW (READ-ONLY,
RESEARCH ONLY, SPEC GATE ONLY):
ETH_SOL_RELATIVE_STRENGTH_PULLBACK_CONTINUATION_V1.

Loop stage: candidate_spec. Gives frozen NUMERIC form to every rule of
the candidate #5 hypothesis -- before any detector exists, exactly as
candidates #1-#4 were specified before they were tested. Gated live on
the pushed family proposal, the pushed Autopilot Loop V1, and the
four-record rejection ledger.

Anti-lookahead is law in every block: completed bars only for the RS
gate, the up-leg, the pullback, the ATR, and the trigger; entry at the
trigger close; replay/label evaluation starts only on the NEXT 1h bar.
WIDER-stop rule mandatory. 27 bps fees, 81 bps gross target-distance
floor at label time per variant. 2R/3R/4R only. Same-symbol non-overlap
built in at label/replay policy time per variant. At most one
pre-committed edit, separately human-approved, never weakening.

This module defines rules only. It runs no detector, fetches nothing,
labels nothing, replays nothing, creates nothing, and claims nothing.
"""

from __future__ import annotations

from typing import Any

import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as _loop
from sparta_commander.eth_sol_relative_strength_pullback_continuation_family_proposal_contract import (
    CANDIDATE_FAMILY,
    CANDIDATE_ID,
    VERDICT_C5P_READY,
    build_candidate_5_family_proposal,
)

C5S_SCHEMA_VERSION = (
    "eth_sol_relative_strength_pullback_continuation_spec_review.v1")
C5S_LABEL = ("SPARTA Candidate #5 Strategy Spec Review "
             "(READ-ONLY, RESEARCH ONLY, RULES DEFINITION, "
             "NOT A RESCUE, NOT A CLAIM)")
C5S_MODE = "RESEARCH_ONLY"
VERDICT_C5S_READY = "CANDIDATE_5_SPEC_REVIEW_READY"
VERDICT_C5S_BLOCKED = "CANDIDATE_5_SPEC_REVIEW_BLOCKED"
NEXT_REQUIRED_ACTION = (
    "HUMAN_APPROVED_CANDIDATE_5_DETECTOR_SPEC_AND_DRY_RUN_PATH")
CURRENT_LOOP_STAGE = "candidate_spec"
NEXT_LOOP_STAGE = "detector_and_label_review"

# 1. candidate identity ------------------------------------------------------
IDENTITY = {
    "family_id": CANDIDATE_ID,
    "family": CANDIDATE_FAMILY,
    "symbols": ("ETHUSD", "SOLUSD"),
    "timeframe": "1h",
    "direction": "long_only",
    "current_loop_stage": CURRENT_LOOP_STAGE,
}

# 2. relative strength gate --------------------------------------------------
RS_GATE = {
    "uses_completed_1h_bars_only": True,
    "lookback_bars": 20,
    "return_formula": "return_20 = close[t] / close[t-20] - 1",
    "pass_rule_1": "return_20(symbol) > 0",
    "pass_rule_2": "return_20(symbol) > return_20(other_symbol)",
    "no_future_bars": True,
    "no_same_bar_lookahead": True,
    "required_entry_gate_not_rescue_or_post_failure_score": True,
}

# 3. prior up-leg definition -------------------------------------------------
UP_LEG = {
    "window": "same 20-bar window used by the rs gate",
    "up_leg_low": "min low over completed bars t-20 through t",
    "up_leg_high": "max high over completed bars t-20 through t",
    "up_leg_size": "up_leg_high - up_leg_low",
    "up_leg_size_must_be_positive": True,
    "reject_if_up_leg_size_not_positive": True,
}

# 4. shallow pullback definition ---------------------------------------------
PULLBACK = {
    "min_bars": 2, "max_bars": 6,
    "bars_must_be_completed_1h": True,
    "must_occur_after_prior_up_leg_high": True,
    "pullback_low": "min low during pullback window",
    "pullback_high": "max high during pullback window",
    "pullback_depth": "up_leg_high - pullback_low",
    "valid_rule_1": "pullback_depth > 0",
    "valid_rule_2_max_depth_pct_of_up_leg": 38.2,
    "valid_rule_3": "pullback_low > up_leg_low",
    "purpose": ("prevents deep retracement / failed-trend rescue "
                "entries"),
}

# 5. continuation trigger ----------------------------------------------------
TRIGGER = {
    "rule": ("first completed 1h close above pullback_high while the rs "
             "gate still passes"),
    "entry_price": "trigger_candle_close",
    "evaluation_starts": "next_1h_bar_after_trigger_close",
    "no_intrabar_trigger_entry": True,
    "no_future_pullback_extension_after_trigger": True,
}

# 6. stop logic ---------------------------------------------------------------
STOP_LOGIC = {
    "atr_length": 14,
    "atr_uses_completed_1h_bars_only_standard_true_range": True,
    "atr_multiplier": 1.5,
    "atr_stop_distance": "1.5 * atr14",
    "structure_stop_distance": "entry_price - pullback_low",
    "stop_distance": "max(atr_stop_distance, structure_stop_distance)",
    "stop_price": "entry_price - stop_distance",
    "stop_must_be_below_entry": True,
    "invalid_if_stop_distance_not_positive": True,
    "wider_stop_rule_mandatory_no_tightening_to_improve_r": True,
}

# 7. fee-aware geometry -------------------------------------------------------
FEE_GEOMETRY = {
    "fee_model_round_trip_bps": 27,
    "label_time_minimum_gross_target_distance_bps": 81,
    "floor_is_3x_round_trip_fees": True,
    "applies_per_target_variant_being_evaluated": True,
    "checked_before_any_replay_is_authorized": True,
    "no_maker_rebate_assumption": True,
    "no_zero_fee_assumption": True,
    "rule": ("if target distance is below 81 bps gross, the setup is "
             "not eligible for replay labeling"),
}

# 8. target variants ----------------------------------------------------------
TARGET_VARIANTS = ("2r", "3r", "4r")
TARGET_RULES = {
    "variants": TARGET_VARIANTS,
    "no_new_variants_after_label_freeze": True,
    "target_price_formula":
        "entry_price + r_multiple * stop_distance",
}

# 9. same-symbol non-overlap/cooldown ----------------------------------------
NON_OVERLAP = {
    "built_in_at_label_replay_policy_time": True,
    "rule": ("for each symbol independently, a setup is eligible only "
             "if its trigger/entry does not occur before the prior "
             "kept same-symbol setup's exit under the same variant"),
    "evaluated_per_variant_because_exits_differ": True,
    "may_only_reduce_or_keep_trade_count_never_add": True,
    "is_not_an_edit_or_rescue_path": True,
}

# 10. edit policy --------------------------------------------------------------
EDIT_POLICY = {
    "maximum_pre_committed_edits": 1,
    "edit_must_be_filter_only_or_structure_only_as_pre_authorized":
        True,
    "edit_may_never": (
        "weaken_entries", "add_symbols",
        "add_trades_after_labels_are_frozen", "remove_fees",
        "loosen_no_overlap", "change_target_variants"),
    "edit_requires_separate_human_approval": True,
}

# 11. rejection conditions (inherited verbatim from autopilot v1) -------------
REJECTION_CONDITIONS = _loop.AUTO_REJECTION_RULES

# 12. promotion-to-human-review conditions ------------------------------------
PROMOTION_CONDITIONS = (
    "fee_honest_net_positive_after_replay",
    "gross_positive_before_fees",
    "hit_rate_above_breakeven",
    "non_overlap_adjusted_result_remains_acceptable",
    "sample_size_not_near_zero",
    "no_concentration_only_result",
    "no_profitability_claim_only_human_review_candidate_status"
    "_allowed",
)

# 13. safety / no-claim block ---------------------------------------------------
SAFETY_NO_CLAIM = (
    "no_trading", "no_paper_trading", "no_live_trading",
    "no_wallet_account_api_order_capability",
    "no_auto_push", "no_auto_commit",
    "no_profitability_or_winner_claim",
    "no_paper_or_live_approval_from_this_spec",
)


def get_candidate_5_spec_review_label() -> str:
    return C5S_LABEL


def build_candidate_5_spec_review() -> dict[str, Any]:
    """Assemble the spec review, gated on the pushed proposal, the
    pushed loop, and the four-record ledger all certifying live."""
    record: dict[str, Any] = {
        "schema_version": C5S_SCHEMA_VERSION, "label": C5S_LABEL,
        "mode": C5S_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [],
        "identity": {key: (list(value) if isinstance(value, tuple)
                           else value)
                     for key, value in IDENTITY.items()},
        "rs_gate": dict(RS_GATE),
        "up_leg": dict(UP_LEG),
        "pullback": dict(PULLBACK),
        "trigger": dict(TRIGGER),
        "stop_logic": dict(STOP_LOGIC),
        "fee_geometry": dict(FEE_GEOMETRY),
        "target_rules": {"variants": list(TARGET_VARIANTS),
                         "no_new_variants_after_label_freeze": True,
                         "target_price_formula":
                             TARGET_RULES["target_price_formula"]},
        "non_overlap": dict(NON_OVERLAP),
        "edit_policy": {
            key: (list(value) if isinstance(value, tuple) else value)
            for key, value in EDIT_POLICY.items()},
        "rejection_conditions": list(REJECTION_CONDITIONS),
        "promotion_conditions": list(PROMOTION_CONDITIONS),
        "safety_no_claim": list(SAFETY_NO_CLAIM),
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
        "contains_order_logic": False, "starts_scheduler": False,
        "sends_notifications": False,
        "auto_commits": False, "auto_pushes": False,
        "creates_runners_now": False, "creates_data_artifacts_now": False,
        "modifies_staged_market_data": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False, "authorizes_live_trading": False,
        "promotes_gate": False, "unlocks_downstream_gate": False,
        "claims_profitability": False,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    proposal = build_candidate_5_family_proposal()
    if proposal["verdict"] != VERDICT_C5P_READY:
        record["verdict"] = VERDICT_C5S_BLOCKED
        record["blockers"].append("candidate_5_proposal_not_certifying")
        record["blockers"].extend(proposal["blockers"])
        return record
    loop_contract = _loop.build_autopilot_loop_contract()
    if loop_contract["verdict"] != _loop.VERDICT_AP_READY:
        record["verdict"] = VERDICT_C5S_BLOCKED
        record["blockers"].append("autopilot_loop_not_certifying")
        record["blockers"].extend(loop_contract["blockers"])
        return record
    record["verdict"] = VERDICT_C5S_READY
    return record


def validate_candidate_5_spec_review(record: Any) -> dict[str, Any]:
    """Validate shape, frozen numerics, and safety invariants. Never
    raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_C5S_READY, VERDICT_C5S_BLOCKED):
        errors.append("bad_verdict")
    identity = r.get("identity") or {}
    if identity.get("family_id") != CANDIDATE_ID:
        errors.append("family_id_tampered")
    if identity.get("symbols") != ["ETHUSD", "SOLUSD"]:
        errors.append("symbols_tampered")
    if identity.get("timeframe") != "1h":
        errors.append("timeframe_tampered")
    if identity.get("direction") != "long_only":
        errors.append("direction_tampered")
    if identity.get("current_loop_stage") != "candidate_spec":
        errors.append("loop_stage_tampered")
    rs = r.get("rs_gate") or {}
    if rs != RS_GATE:
        errors.append("rs_gate_tampered")
    if rs.get("lookback_bars") != 20:
        errors.append("rs_lookback_tampered")
    if rs.get("no_future_bars") is not True \
            or rs.get("no_same_bar_lookahead") is not True \
            or rs.get("uses_completed_1h_bars_only") is not True:
        errors.append("rs_lookahead_protection_weakened")
    if r.get("up_leg") != UP_LEG:
        errors.append("up_leg_tampered")
    pullback = r.get("pullback") or {}
    if pullback != PULLBACK:
        errors.append("pullback_tampered")
    if pullback.get("min_bars") != 2 or pullback.get("max_bars") != 6:
        errors.append("pullback_length_tampered")
    if pullback.get("valid_rule_2_max_depth_pct_of_up_leg") != 38.2:
        errors.append("pullback_depth_tampered")
    trigger = r.get("trigger") or {}
    if trigger != TRIGGER:
        errors.append("trigger_tampered")
    if trigger.get("evaluation_starts") != (
            "next_1h_bar_after_trigger_close"):
        errors.append("trigger_lookahead_protection_weakened")
    stop = r.get("stop_logic") or {}
    if stop != STOP_LOGIC:
        errors.append("stop_logic_tampered")
    if stop.get("atr_length") != 14:
        errors.append("atr_length_tampered")
    if stop.get("atr_multiplier") != 1.5:
        errors.append("atr_multiplier_tampered")
    if stop.get(
            "wider_stop_rule_mandatory_no_tightening_to_improve_r") is \
            not True:
        errors.append("wider_stop_rule_weakened")
    fee = r.get("fee_geometry") or {}
    if fee != FEE_GEOMETRY:
        errors.append("fee_geometry_tampered")
    if fee.get("fee_model_round_trip_bps") != 27:
        errors.append("fee_bps_tampered")
    if fee.get("label_time_minimum_gross_target_distance_bps") != 81:
        errors.append("floor_81bps_tampered")
    if fee.get("checked_before_any_replay_is_authorized") is not True:
        errors.append("floor_must_precede_replay")
    targets = r.get("target_rules") or {}
    if targets.get("variants") != ["2r", "3r", "4r"]:
        errors.append("target_variants_tampered")
    if targets.get("no_new_variants_after_label_freeze") is not True:
        errors.append("variant_freeze_weakened")
    overlap = r.get("non_overlap") or {}
    if overlap != NON_OVERLAP:
        errors.append("non_overlap_tampered")
    if overlap.get("built_in_at_label_replay_policy_time") is not True \
            or overlap.get(
                "may_only_reduce_or_keep_trade_count_never_add") is not \
            True:
        errors.append("non_overlap_weakened")
    edit = r.get("edit_policy") or {}
    if edit.get("maximum_pre_committed_edits") != 1:
        errors.append("edit_count_tampered")
    if edit.get("edit_may_never") != [
            "weaken_entries", "add_symbols",
            "add_trades_after_labels_are_frozen", "remove_fees",
            "loosen_no_overlap", "change_target_variants"]:
        errors.append("edit_limits_weakened")
    if edit.get("edit_requires_separate_human_approval") is not True:
        errors.append("edit_human_gate_removed")
    if tuple(r.get("rejection_conditions") or ()) != (
            REJECTION_CONDITIONS):
        errors.append("rejection_conditions_tampered")
    if tuple(r.get("promotion_conditions") or ()) != (
            PROMOTION_CONDITIONS):
        errors.append("promotion_conditions_tampered")
    if tuple(r.get("safety_no_claim") or ()) != SAFETY_NO_CLAIM:
        errors.append("safety_no_claim_tampered")
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
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "auto_commits", "auto_pushes",
                "creates_runners_now", "creates_data_artifacts_now",
                "modifies_staged_market_data",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate", "claims_profitability"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    return {"valid": not errors, "errors": errors}
