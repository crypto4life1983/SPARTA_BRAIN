"""SPARTA STRATEGY FACTORY CANDIDATE FAMILY RECOMMENDATION V1
(READ-ONLY, RESEARCH ONLY, RECOMMENDATION LAYER ONLY).

Uses the FIVE-candidate frozen rejection ledger and the seed lessons to
propose three clean Candidate #6 hypotheses through the pushed Autopilot
Loop V1 -- and to pick ONE preferred hypothesis deterministically, as a
PROPOSAL RECOMMENDATION ONLY, never execution. The human decides.

Every recommendation is validated live by the loop's own
validate_candidate_family_proposal and screen_output_language gates,
then screened by this module's hard rejection rules (no prior-family
reuse, no c5-continuation dependence, no rs-gate weakening to add
trades, no fee removal or floor lowering, no tiny-sample promotion
dependence, no trading capability, no winner language). Seeds are
inspiration only, never rescue paths.

This module runs no detector, fetches nothing, labels nothing, replays
nothing, creates no artifacts or runners, schedules nothing, trades
nothing, and claims nothing.
"""

from __future__ import annotations

from typing import Any

import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as _loop
from sparta_commander.btc_sol_long_trend_continuation_v1_result_and_rejection_record_contract import (
    REJECTION_REASON as C3_REASON,
    REJECTION_STATUS as C3_STATUS,
)
from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (
    REJECTION_REASON as C2_REASON,
    REJECTION_STATUS as C2_STATUS,
)
from sparta_commander.eth_sol_relative_strength_rejection_record_contract import (
    REJECTION_REASON as C5_REASON,
    REJECTION_STATUS as C5_STATUS,
)
from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
    REJECTION_REASON as C1_REASON,
    REJECTION_STATUS as C1_STATUS,
)
from sparta_commander.sol_btc_long_1h_swing_structure_rejection_record_contract import (
    REJECTION_REASON as C4_REASON,
    REJECTION_STATUS as C4_STATUS,
)

CR_SCHEMA_VERSION = "strategy_factory_candidate_recommendation.v1"
CR_LABEL = ("SPARTA Strategy Factory Candidate Family Recommendation V1 "
            "(READ-ONLY, RESEARCH ONLY, RECOMMENDATION ONLY, "
            "NEVER EXECUTION)")
CR_MODE = "RESEARCH_ONLY"
VERDICT_CR_READY = "STRATEGY_FACTORY_CANDIDATE_RECOMMENDATION_V1_READY"
VERDICT_CR_BLOCKED = (
    "STRATEGY_FACTORY_CANDIDATE_RECOMMENDATION_V1_BLOCKED")
NEXT_REQUIRED_ACTION = (
    "HUMAN_APPROVED_CANDIDATE_6_FAMILY_PROPOSAL_VIA_AUTOPILOT_LOOP")

FIVE_CANDIDATE_LEDGER = {
    "candidate_1": {"family": "ny_session_fvg_choch",
                    "status": "REJECTED_KEPT_ON_RECORD",
                    "reason": "COST_NON_VIABLE_RISK_GEOMETRY"},
    "candidate_2": {"family":
                    "crypto_intraday_breakout_pullback_structure",
                    "status": "REJECTED_KEPT_ON_RECORD",
                    "reason": "EDGE_FAILURE_SURVIVED_ONE_AUTHORIZED"
                              "_FILTER_EXPERIMENT"},
    "candidate_3": {"family": "long_biased_trend_continuation",
                    "status": "REJECTED_KEPT_ON_RECORD",
                    "reason": "NEAR_ZERO_SETUPS_AFTER_ONE_AUTHORIZED"
                              "_STRUCTURE_EDIT"},
    "candidate_4": {"family": "long_1h_swing_structure",
                    "status": "REJECTED_KEPT_ON_RECORD",
                    "reason": "EDGE_FAILURE_SURVIVED_ONE_AUTHORIZED"
                              "_FILTER_ONLY_EDIT"},
    "candidate_5": {"family":
                    "eth_sol_relative_strength_pullback_continuation",
                    "status": "REJECTED_KEPT_ON_RECORD",
                    "reason": "SMALL_SAMPLE_NET_NEGATIVE_AND_EDIT"
                              "_ADDED_NOTHING"},
    "zero_trades_zero_claims_zero_deleted_evidence": True,
}

ALL_REJECTED_FAMILIES = (
    "ny_session_fvg_choch",
    "crypto_intraday_breakout_pullback_structure",
    "long_biased_trend_continuation",
    "long_1h_swing_structure",
    "eth_sol_relative_strength_pullback_continuation",
)

PROPOSAL_RULES = (
    "must be materially different from all five rejected families",
    "must use frozen seeds only as inspiration",
    "must never use seeds as rescue paths",
    "must never reuse rejected geometry unchanged",
    "must pass autopilot v1 validate_candidate_family_proposal",
    "must use evidence language only",
)

SEED_INVENTORY_FUTURE_FAMILY_ONLY = (
    "cost_geometry_can_kill_an_otherwise_plausible_idea",
    "breakout_pullback_edge_failure_must_not_be_rescued_by_weaker"
    "_filters",
    "near_zero_setup_count_after_structure_edit_is_a_kill_condition",
    "same_symbol_overlap_correlation_must_be_penalized",
    "sol_side_relative_strength_recurrence_across_c4_c5_is"
    "_inspiration_only",
    "thin_risk_fee_sensitivity_must_be_filtered_before_replay",
    "trigger_resumption_scarcity_is_a_structural_lesson",
    "same_symbol_non_overlap_can_remove_winners",
    "eth_side_negative_contribution_in_c5_is_not_edge_evidence",
    "btc_weakness_in_c4_is_not_edge_evidence",
)

HARD_REJECTION_RULES = (
    "reject_if_same_as_any_prior_family",
    "reject_if_it_depends_on_c5_continuation_as_is",
    "reject_if_it_weakens_rs_gate_just_to_add_trades",
    "reject_if_it_removes_fees_or_lowers_fee_floor",
    "reject_if_it_depends_on_tiny_sample_promotion",
    "reject_if_it_has_paper_live_trading_capability",
    "reject_if_it_uses_winner_or_profitability_language",
)

NO_CLAIM_LANGUAGE = (
    "hypothesis only; nothing is known about edge until the full "
    "autopilot loop gauntlet completes; no profitability claim at any "
    "stage")

RECOMMENDATIONS = {
    "SOL_RELATIVE_STRENGTH_BREAKOUT_CONTINUATION_V1": {
        "family_id": "SOL_RELATIVE_STRENGTH_BREAKOUT_CONTINUATION_V1",
        "family": "sol_relative_strength_breakout_continuation",
        "hypothesis": ("tests whether solusd continuation after a "
                       "confirmed range breakout, gated by sol "
                       "relative strength versus an eth/btc proxy, "
                       "produces fee-viable labels on 1h candles"),
        "symbols": ("SOLUSD",),
        "timeframe": "1h",
        "direction": "long_only",
        "materially_different_because": (
            "single-symbol rs-gated breakout continuation: no session "
            "windows or fvg/choch (c1), no 15m breakout-retest "
            "structure (c2), no 15m bar-sequence micro-pattern (c3), "
            "no swing-pair requirement (c4), no shallow-pullback "
            "resumption trigger (c5)"),
        "seeds_inspiring_it": (
            "sol_side_relative_strength_recurrence_across_c4_c5_is"
            "_inspiration_only",
            "trigger_resumption_scarcity_is_a_structural_lesson"),
        "why_not_rescue": ("new entry mechanism on a new single-symbol "
                           "scope; reuses no c4/c5 geometry, labels, or "
                           "thresholds"),
        "expected_failure_risks": (
            "breakout mechanisms rhyme with c2's failure mode; "
            "single-symbol scope may produce a small sample"),
        "required_spec_gates": ("81_bps_floor_at_label_time",
                                "27_bps_fee_model",
                                "wider_stop_rule",
                                "same_symbol_non_overlap",
                                "completed_bars_only_no_lookahead"),
        "no_claim": NO_CLAIM_LANGUAGE,
    },
    "MULTI_SYMBOL_RELATIVE_STRENGTH_ROTATION_FILTER_V1": {
        "family_id":
            "MULTI_SYMBOL_RELATIVE_STRENGTH_ROTATION_FILTER_V1",
        "family": "multi_symbol_relative_strength_rotation_filter",
        "hypothesis": ("tests whether ranking ethusd/solusd/btcusd by "
                       "relative strength and labeling ONLY the "
                       "top-ranked symbol's continuation events "
                       "produces fee-viable labels on 1h candles; "
                       "research-only label logic, long-only"),
        "symbols": ("ETHUSD", "SOLUSD", "BTCUSD"),
        "timeframe": "1h",
        "direction": "long_only",
        "materially_different_because": (
            "cross-sectional ranking is a mechanism class none of the "
            "five families used; selection happens BETWEEN symbols "
            "before any entry pattern fires, so it is not a session/"
            "fvg, breakout-retest, micro-pattern, swing-pair, or "
            "pullback-resumption family"),
        "seeds_inspiring_it": (
            "sol_side_relative_strength_recurrence_across_c4_c5_is"
            "_inspiration_only",
            "same_symbol_overlap_correlation_must_be_penalized",
            "thin_risk_fee_sensitivity_must_be_filtered_before_replay"),
        "why_not_rescue": ("ranking-based selection is a new mechanism; "
                           "it does not continue, loosen, or re-test "
                           "any rejected family's entries and uses no "
                           "wallet/order/portfolio logic -- labels "
                           "only"),
        "expected_failure_risks": (
            "rank churn may concentrate labels in one symbol; "
            "continuation events on the top-ranked symbol may still "
            "lack edge"),
        "required_spec_gates": ("81_bps_floor_at_label_time",
                                "27_bps_fee_model",
                                "wider_stop_rule",
                                "same_symbol_non_overlap",
                                "completed_bars_only_no_lookahead"),
        "no_claim": NO_CLAIM_LANGUAGE,
    },
    "VOLATILITY_EXPANSION_AFTER_RS_COMPRESSION_V1": {
        "family_id": "VOLATILITY_EXPANSION_AFTER_RS_COMPRESSION_V1",
        "family": "volatility_expansion_after_rs_compression",
        "hypothesis": ("tests whether range expansion immediately "
                       "following an rs-positive volatility "
                       "compression produces fee-viable labels on 1h "
                       "ethusd/solusd candles; entry on the expansion "
                       "bar close, not on a delayed pullback "
                       "resumption"),
        "symbols": ("ETHUSD", "SOLUSD"),
        "timeframe": "1h",
        "direction": "long_only",
        "materially_different_because": (
            "compression-then-expansion timing is a volatility-state "
            "mechanism, not a price-structure pattern: no session/fvg "
            "(c1), no breakout-retest (c2), no micro-pattern (c3), no "
            "swing pairs (c4), and it explicitly avoids c5's delayed "
            "pullback-resumption trigger that caused the 372/411 "
            "scarcity"),
        "seeds_inspiring_it": (
            "trigger_resumption_scarcity_is_a_structural_lesson",
            "thin_risk_fee_sensitivity_must_be_filtered_before_replay"),
        "why_not_rescue": ("the entry fires AT the expansion event "
                           "rather than waiting for resumption, a "
                           "different mechanism rather than a "
                           "loosened version of c5"),
        "expected_failure_risks": (
            "compression breakouts may gap through stops; expansion "
            "bars may produce thin-risk geometry that the floor then "
            "rejects"),
        "required_spec_gates": ("81_bps_floor_at_label_time",
                                "27_bps_fee_model",
                                "wider_stop_rule",
                                "same_symbol_non_overlap",
                                "completed_bars_only_no_lookahead"),
        "no_claim": NO_CLAIM_LANGUAGE,
    },
}

PREFERRED_CANDIDATE_6 = (
    "MULTI_SYMBOL_RELATIVE_STRENGTH_ROTATION_FILTER_V1")

PREFERRED_RATIONALE = (
    "most structurally different: cross-sectional ranking is a "
    "mechanism class none of the five rejected families used",
    "most likely to avoid the five known failure modes: 1h geometry "
    "supports the 81 bps floor (vs c1); selection-before-entry is not "
    "a breakout-retest rescue (vs c2); ranking across three symbols "
    "generates regular eligibility instead of waiting on rare "
    "micro-patterns (vs c3/c5 scarcity); top-ranked-only labeling "
    "structurally limits same-symbol stacking (vs c4's overlap "
    "amplification)",
    "this is a proposal recommendation only, not execution; the human "
    "decides and every loop stage still applies",
)


def get_candidate_recommendation_label() -> str:
    return CR_LABEL


def apply_hard_rejection_rules(recommendation: Any) -> dict[str, Any]:
    """Pure screen of one recommendation against the hard rejection
    rules. Never raises."""
    rejections: list[str] = []
    if not isinstance(recommendation, dict):
        return {"acceptable": False,
                "rejections": ["recommendation_not_a_dict"]}
    family = str(recommendation.get("family") or "")
    if family in ALL_REJECTED_FAMILIES:
        rejections.append("reject_if_same_as_any_prior_family")
    text = " ".join(str(recommendation.get(key) or "") for key in
                    ("hypothesis", "materially_different_because",
                     "why_not_rescue"))
    lowered = text.lower()
    if "continue c5 as-is" in lowered or "c5 continuation as-is" \
            in lowered:
        rejections.append("reject_if_it_depends_on_c5_continuation"
                          "_as_is")
    if "weaken the rs gate" in lowered or "weaker rs gate" in lowered:
        rejections.append("reject_if_it_weakens_rs_gate_just_to_add"
                          "_trades")
    if "zero-fee" in lowered or "without fees" in lowered \
            or "lower the floor" in lowered:
        rejections.append("reject_if_it_removes_fees_or_lowers_fee"
                          "_floor")
    if "promote on the small sample" in lowered \
            or "tiny sample promotion" in lowered:
        rejections.append("reject_if_it_depends_on_tiny_sample"
                          "_promotion")
    gates = tuple(recommendation.get("required_spec_gates") or ())
    if "81_bps_floor_at_label_time" not in gates \
            or "27_bps_fee_model" not in gates:
        rejections.append("reject_if_it_removes_fees_or_lowers_fee"
                          "_floor")
    if recommendation.get("direction") not in ("long_only",):
        rejections.append("reject_if_it_has_paper_live_trading"
                          "_capability")
    language = _loop.screen_output_language(text)
    if not language["acceptable"]:
        rejections.append("reject_if_it_uses_winner_or_profitability"
                          "_language")
    return {"acceptable": not rejections,
            "rejections": sorted(set(rejections))}


def build_candidate_recommendation() -> dict[str, Any]:
    """Assemble the recommendation, gated on the FIVE-record ledger and
    the loop certifying live; every recommendation passes the loop's
    own proposal gate plus the hard rejection rules."""
    record: dict[str, Any] = {
        "schema_version": CR_SCHEMA_VERSION, "label": CR_LABEL,
        "mode": CR_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [],
        "five_candidate_ledger": {
            key: (dict(value) if isinstance(value, dict) else value)
            for key, value in FIVE_CANDIDATE_LEDGER.items()},
        "all_rejected_families": list(ALL_REJECTED_FAMILIES),
        "proposal_rules": list(PROPOSAL_RULES),
        "seed_inventory_future_family_only": list(
            SEED_INVENTORY_FUTURE_FAMILY_ONLY),
        "hard_rejection_rules": list(HARD_REJECTION_RULES),
        "recommendations": {
            key: {field: (list(value) if isinstance(value, tuple)
                          else value)
                  for field, value in rec.items()}
            for key, rec in RECOMMENDATIONS.items()},
        "recommendation_checks": {},
        "preferred_candidate_6": PREFERRED_CANDIDATE_6,
        "preferred_rationale": list(PREFERRED_RATIONALE),
        "preferred_is_proposal_recommendation_only": True,
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
        "creates_candidate_6_execution_files": False,
        "modifies_staged_market_data": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False, "authorizes_live_trading": False,
        "promotes_gate": False, "unlocks_downstream_gate": False,
        "claims_profitability": False,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    checks = (
        ("candidate_1", C1_STATUS, C1_REASON,
         "COST_NON_VIABLE_RISK_GEOMETRY"),
        ("candidate_2", C2_STATUS, C2_REASON,
         "EDGE_FAILURE_SURVIVED_ONE_AUTHORIZED_FILTER_EXPERIMENT"),
        ("candidate_3", C3_STATUS, C3_REASON,
         "NEAR_ZERO_SETUPS_AFTER_ONE_AUTHORIZED_STRUCTURE_EDIT"),
        ("candidate_4", C4_STATUS, C4_REASON,
         "EDGE_FAILURE_SURVIVED_ONE_AUTHORIZED_FILTER_ONLY_EDIT"),
        ("candidate_5", C5_STATUS, C5_REASON,
         "SMALL_SAMPLE_NET_NEGATIVE_AND_EDIT_ADDED_NOTHING"),
    )
    for name, status, reason, expected_reason in checks:
        if status != "REJECTED_KEPT_ON_RECORD" \
                or reason != expected_reason:
            record["verdict"] = VERDICT_CR_BLOCKED
            record["blockers"].append(name + "_ledger_broken")
            return record
    if _loop.build_autopilot_loop_contract()["verdict"] != (
            _loop.VERDICT_AP_READY):
        record["verdict"] = VERDICT_CR_BLOCKED
        record["blockers"].append("autopilot_loop_not_certifying")
        return record
    all_pass = True
    for key, rec in RECOMMENDATIONS.items():
        loop_proposal = {
            "family": rec["family"],
            "hypothesis": rec["hypothesis"],
            "difference_from_rejected_families":
                rec["materially_different_because"],
            "uses_seeds_as_rescue": False,
        }
        loop_check = _loop.validate_candidate_family_proposal(
            loop_proposal)
        hard_check = apply_hard_rejection_rules(rec)
        record["recommendation_checks"][key] = {
            "loop_gate": loop_check, "hard_rules": hard_check}
        if not (loop_check["acceptable"] and hard_check["acceptable"]):
            all_pass = False
    if not all_pass:
        record["verdict"] = VERDICT_CR_BLOCKED
        record["blockers"].append("a_recommendation_failed_its_gates")
        return record
    if PREFERRED_CANDIDATE_6 not in RECOMMENDATIONS:
        record["verdict"] = VERDICT_CR_BLOCKED
        record["blockers"].append("preferred_not_in_shortlist")
        return record
    record["verdict"] = VERDICT_CR_READY
    return record


def validate_candidate_recommendation(record: Any) -> dict[str, Any]:
    """Validate shape and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_CR_READY, VERDICT_CR_BLOCKED):
        errors.append("bad_verdict")
    ledger = r.get("five_candidate_ledger") or {}
    expected_ledger = {
        key: (dict(value) if isinstance(value, dict) else value)
        for key, value in FIVE_CANDIDATE_LEDGER.items()}
    if ledger != expected_ledger:
        errors.append("ledger_tampered")
    if len([key for key in ledger if key.startswith("candidate_")]) != 5:
        errors.append("ledger_count_not_five")
    if tuple(r.get("all_rejected_families") or ()) != (
            ALL_REJECTED_FAMILIES):
        errors.append("rejected_families_tampered")
    if tuple(r.get("proposal_rules") or ()) != PROPOSAL_RULES:
        errors.append("proposal_rules_tampered")
    if tuple(r.get("seed_inventory_future_family_only") or ()) != (
            SEED_INVENTORY_FUTURE_FAMILY_ONLY):
        errors.append("seed_inventory_tampered")
    if tuple(r.get("hard_rejection_rules") or ()) != (
            HARD_REJECTION_RULES):
        errors.append("hard_rejection_rules_tampered")
    expected_recommendations = {
        key: {field: (list(value) if isinstance(value, tuple)
                      else value)
              for field, value in rec.items()}
        for key, rec in RECOMMENDATIONS.items()}
    if r.get("recommendations") != expected_recommendations:
        errors.append("recommendations_tampered")
    if r.get("preferred_candidate_6") != PREFERRED_CANDIDATE_6:
        errors.append("preferred_candidate_tampered")
    if tuple(r.get("preferred_rationale") or ()) != PREFERRED_RATIONALE:
        errors.append("preferred_rationale_tampered")
    if r.get("preferred_is_proposal_recommendation_only") is not True:
        errors.append("preferred_must_be_recommendation_only")
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
                "creates_candidate_6_execution_files",
                "modifies_staged_market_data",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate", "claims_profitability"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    return {"valid": not errors, "errors": errors}
