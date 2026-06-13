"""SPARTA CANDIDATE #7 FAMILY PROPOSAL (READ-ONLY, RESEARCH ONLY,
PROPOSAL GATE ONLY): VOLATILITY_COMPRESSION_EXPANSION_V1.

Drafted via the pushed Overnight Research Autopilot V2 next-candidate
plan schema and validated through BOTH pushed gate layers: Autopilot
Loop V1's validate_candidate_family_proposal / screen_output_language
gates AND Recommendation V1's hard rejection rules. BLOCKED if the
six-record ledger (C1-C6), V2, Recommendation V1, or the Autopilot
Loop V1 stops certifying, or if the family equals any rejected family
name from either pushed rejection-family tuple.

CLEAN HYPOTHESIS (evidence language only): candidate #7 tests whether
a single-symbol volatility-regime trigger -- a contraction-then-
expansion event on btcusd 4h bars after the ATR(14) has dropped below
a fraction of its 100-bar rolling average for N consecutive bars,
followed by the first bar whose true range exceeds a multiplier of
the contracted ATR while closing in the upper third of its range --
produces fee-viable continuation labels at 27 bps round-trip with the
81 bps gross target-distance floor. Single-symbol, 4h, long-only,
labels-only research.

MATERIAL DIFFERENCES from C1-C6 (each listed explicitly):
  - not session-anchored: NO new-york session window, NO fair-value
    gap, NO change-of-character structure (NOT C1);
  - not breakout-pullback: NO range breakout AND NO retest after
    breakout (NOT C2);
  - not long-biased trend continuation: NO 15m bar-sequence
    micro-pattern, NO trend-MA filter (NOT C3);
  - not single-pair 1h swing structure: NO sol/btc pair coupling, NO
    swing-pivot trigger, the timeframe is 4h not 1h (NOT C4);
  - not relative-strength pullback continuation: NO eth/sol pairwise
    rs comparison, NO shallow pullback resumption (NOT C5);
  - not cross-sectional rotation: NO simultaneous multi-symbol rank,
    NO top-ranked filter, NO rotation between btc/eth/sol (NOT C6);
  - the EDGE HYPOTHESIS is a volatility-regime shift, not a structure
    pattern; the universe is a SINGLE symbol; the timeframe is 4h.

C6 ANTI-CLUSTER LESSON BAKED IN AT PROPOSAL TIME (not as a future
edit): a built-in minimum-bar-gap clustering constraint between
accepted setups on the same symbol is part of the family hypothesis,
specifically because C6 spent its single edit on a clustering filter
post-hoc and proved the structural cost of dense same-symbol setups.
For C7 the clustering control is pre-committed; it is NOT the single
allowed C7 structure edit.

This is a PROPOSAL. It runs no detector, fetches nothing, builds no
labels, replays nothing, creates no artifacts/runners/schedulers/data,
and the next stage is candidate_spec review by the human -- not
detector execution. Seeds are inspiration and risk-control lessons
only, never rescue paths; no C1-C6 setup_ids, replay rows, edited
labels, or rejected geometry may be reused as candidate #7 evidence.
"""

from __future__ import annotations

from typing import Any

import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as _loop
import sparta_commander.strategy_factory_candidate_recommendation_v1_contract as _rec
from sparta_commander.btc_sol_long_trend_continuation_v1_result_and_rejection_record_contract import (
    REJECTION_STATUS as C3_STATUS,
)
from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (
    REJECTION_STATUS as C2_STATUS,
)
from sparta_commander.eth_sol_relative_strength_rejection_record_contract import (
    REJECTION_STATUS as C5_STATUS,
)
from sparta_commander.multi_symbol_relative_strength_rotation_filter_rejection_record_contract import (
    REJECTION_STATUS as C6_STATUS,
)
from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
    REJECTION_STATUS as C1_STATUS,
)
from sparta_commander.sol_btc_long_1h_swing_structure_rejection_record_contract import (
    REJECTION_STATUS as C4_STATUS,
)
from sparta_commander.strategy_factory_overnight_research_autopilot_v2_contract import (
    REJECTED_FAMILY_LOGIC_BLACKLIST as V2_BLACKLIST,
    VERDICT_OAP2_READY,
    build_overnight_research_autopilot_v2_contract,
)

C7P_SCHEMA_VERSION = (
    "volatility_compression_expansion_v1_family_proposal.v1")
C7P_LABEL = ("SPARTA Candidate #7 Family Proposal "
             "(READ-ONLY, RESEARCH ONLY, PROPOSAL GATE ONLY, VALIDATED "
             "BY AUTOPILOT LOOP V1 AND RECOMMENDATION V1, DRAFTED VIA "
             "OVERNIGHT RESEARCH AUTOPILOT V2 NEXT-CANDIDATE PLAN "
             "SCHEMA, NOT A RESCUE, NOT A CLAIM)")
C7P_MODE = "RESEARCH_ONLY"
VERDICT_C7P_READY = "CANDIDATE_7_FAMILY_PROPOSAL_READY"
VERDICT_C7P_BLOCKED = "CANDIDATE_7_FAMILY_PROPOSAL_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_CANDIDATE_7_SPEC_REVIEW"
NEXT_LOOP_STAGE = "candidate_spec"

CANDIDATE_ID = "VOLATILITY_COMPRESSION_EXPANSION_V1"
CANDIDATE_FAMILY = "volatility_compression_expansion"

CLEAN_HYPOTHESIS = (
    "candidate #7 tests whether a single-symbol volatility-regime "
    "trigger on btcusd 4h bars -- a contraction-then-expansion event "
    "where atr(14) has dropped below a fraction of its 100-bar rolling "
    "average for n consecutive completed bars, followed by the first "
    "completed bar whose true range exceeds a multiplier of the "
    "contracted atr while closing in the upper third of its range -- "
    "produces fee-viable continuation labels at 27 bps round-trip with "
    "the 81 bps gross target-distance floor, on a per-symbol minimum-"
    "bar-gap clustering policy; single-symbol, 4h, long-only, labels-"
    "only research; the edge hypothesis is a volatility-regime shift, "
    "not a structure pattern")

DIFFERENCE_FROM_REJECTED_FAMILIES = (
    "1) not ny-session fvg/choch (no session windows, no fvg, no "
    "choch); "
    "2) not generic breakout-pullback (no range breakout, no pullback "
    "retest); "
    "3) not long-biased trend continuation (no 15m bar-sequence "
    "micro-pattern, no trend-ma filter); "
    "4) not sol/btc 1h swing structure (no sol/btc pair coupling, no "
    "swing-pivot trigger, timeframe is 4h not 1h); "
    "5) not eth/sol relative-strength pullback continuation (no "
    "pairwise rs comparison, no shallow pullback resumption); "
    "6) not multi-symbol relative-strength rotation (no simultaneous "
    "multi-symbol rank, no top-ranked filter, no rotation between "
    "btc/eth/sol); "
    "7) the edge hypothesis is a volatility-regime shift on a single "
    "symbol, not a structure pattern, not a cross-symbol filter; "
    "8) the c6 anti-cluster lesson is built into the proposal as a "
    "pre-committed per-symbol minimum-bar-gap policy, not as a future "
    "edit")

LOOP_PROPOSAL = {
    "family": CANDIDATE_FAMILY,
    "hypothesis": CLEAN_HYPOTHESIS,
    "difference_from_rejected_families":
        DIFFERENCE_FROM_REJECTED_FAMILIES,
    "uses_seeds_as_rescue": False,
}

# universe, timeframe, direction --------------------------------------------
SYMBOLS = ("BTCUSD",)
TIMEFRAME = "4h"
DIRECTION = "long_only"
DIRECTION_NOTE = "long-only research labels; never trading capability"

# volatility-regime trigger family (declarative; exact numerics frozen
# at spec review) ----------------------------------------------------------
TRIGGER_FAMILY = {
    "name": "volatility_compression_then_expansion_event",
    "definition": ("contraction window: atr(14) below a fraction of its "
                   "rolling-100-bar average for n consecutive completed "
                   "4h bars; expansion event: the first completed 4h "
                   "bar whose true range exceeds a multiplier of the "
                   "contracted atr AND whose close lies in the upper "
                   "third of its own range"),
    "uses_completed_4h_bars_only": True,
    "no_future_bars": True,
    "no_same_bar_lookahead": True,
    "no_intrabar_entry": True,
    "evaluation_starts_next_4h_bar_after_event_close": True,
    "exact_numeric_form_frozen_at_spec_review": True,
    "is_a_volatility_regime_trigger_not_a_structure_pattern": True,
    "is_not_a_cross_symbol_rs_filter": True,
    "is_not_a_session_anchored_trigger": True,
    "is_not_a_breakout_pullback_trigger": True,
    "is_not_a_trend_ma_filter": True,
    "is_not_a_swing_pivot_trigger": True,
}

# wider-stop family (same primitive as C6; different timeframe and trigger)
STOP_FAMILY = {
    "rule": ("WIDER stop: max(atr-multiplier * atr(14), entry - "
             "structure-lookback low) -- whichever is wider"),
    "exact_form_frozen_at_spec_review": True,
    "never_tightened_after_entry": True,
    "atr_uses_completed_4h_bars_only_standard_true_range": True,
    "stop_must_be_below_entry": True,
    "invalid_if_stop_distance_not_positive": True,
}

# target variants (kept consistent with autopilot loop's fee floor) --------
TARGET_VARIANTS = ("2r", "3r", "4r")
TARGET_POLICY = {
    "variants": TARGET_VARIANTS,
    "target_price_formula":
        "entry_price + r_multiple * stop_distance",
    "no_new_variants_after_label_freeze": True,
}

# fee-aware geometry policy (kept at the pushed lane standard) -------------
FEE_AWARE_GEOMETRY_POLICY = {
    "fee_model_round_trip_bps": 27,
    "minimum_gross_target_distance_floor_bps": 81,
    "floor_is_3x_round_trip_fees": True,
    "floor_checked_before_replay_eligibility": True,
    "no_maker_rebate_assumption": True,
    "no_zero_fee_assumption": True,
}

# C6 lesson: anti-cluster baked into the proposal at label time -----------
ANTI_CLUSTER_POLICY = {
    "built_in_at_label_emission_time": True,
    "scope": "per_symbol_minimum_bar_gap_between_accepted_events",
    "exact_min_bars_frozen_at_spec_review": True,
    "applies_before_replay_time_non_overlap": True,
    "replay_time_non_overlap_unchanged": True,
    "is_not_the_single_allowed_c7_edit": True,
    "reason_for_built_in":
        "c6_clustering_filter_edit_proved_density_was_structural",
}

# replay-time same-symbol non-overlap (inherited risk control) ------------
NON_OVERLAP_POLICY = {
    "built_in_at_label_replay_policy_time": True,
    "evaluated_per_variant": True,
    "reduce_or_keep_only_never_add_trades": True,
    "is_not_an_edit_or_rescue_path": True,
}

# edit allowance (same one-token allowance as the pushed pattern) ---------
EDIT_ALLOWANCE_POLICY = (
    "at most ONE pre-committed edit for candidate #7, only if "
    "evidence-supported, only via a separately human-approved "
    "contract; if spent and results remain negative, candidate #7 is "
    "REJECTED_KEPT_ON_RECORD; the anti-cluster policy is NOT this "
    "edit token; the edit must target a different structural "
    "parameter than the anti-cluster gap if spent")

# expected failure modes (frozen, evidence-language only) ----------------
EXPECTED_FAILURE_MODES = (
    "cost_prohibitive_small_expansion_bars_failing_the_81_bps_"
    "floor_at_label_time",
    "false_positive_triggers_during_chop_where_atr_contraction_"
    "reflects_range_not_regime",
    "compression_then_expansion_clusters_in_trending_environments_"
    "producing_dense_same_symbol_setups_that_the_built_in_anti_"
    "cluster_policy_must_de_dupe",
    "single_symbol_sample_size_too_small_in_the_pushed_window_to_"
    "support_a_meaningful_kept_trade_count_per_variant",
    "expansion_bars_that_immediately_revert_within_the_next_bar_"
    "before_target_distance_can_be_reached",
    "atr_regime_shift_already_in_progress_at_window_start_producing_"
    "a_lookback_warm_up_set_that_is_research_invalid",
    "any_post_edit_replay_remaining_net_negative_or_gross_negative_"
    "or_with_hit_rate_below_breakeven_at_any_variant",
)

# seeds (inspiration only, never rescue paths) ---------------------------
SEED_USAGE = (
    "c6_clustering_lesson_is_inspiration_for_built_in_anti_cluster_"
    "policy_not_rescue",
    "c5_thin_risk_fee_sensitivity_is_a_risk_control_lesson_only",
    "c5_trigger_resumption_scarcity_warns_against_delayed_pullback_"
    "rescue_entries",
    "c4_btc_weakness_is_not_edge_evidence",
    "single_symbol_volatility_regime_shift_is_a_clean_new_hypothesis_"
    "not_a_recombination_of_rejected_geometry",
    "no_c1_c6_setup_ids_replay_rows_labels_edited_labels_or_replay_"
    "results_may_be_reused_as_candidate_7_evidence",
)
SEEDS_ARE_NEVER_RESCUE_PATHS = True

PROMOTION_TO_HUMAN_REVIEW_CONDITIONS = (
    "fee-honest replay net-positive on the overlap-adjusted "
    "independent sample with sample size not near-zero",
    "all artifact hashes and gates certify",
    "promotion produces a human-review record only: no claim, no "
    "paper, no live, no capability change",
)

SAFETY_AND_NO_CLAIM = (
    "no trading, no paper trading, no live trading",
    "no wallet, account, api, or order capability",
    "no auto-push, no auto-commit",
    "no scheduler activation",
    "no profitability claim and no winner wording at any stage",
    "all output must be evidence language only",
    "every stage requires evidence freeze and explicit human gates",
)

# the V2 blacklist must include this family's six rejected predecessors --
ALL_KNOWN_REJECTED_FAMILIES = tuple(sorted(set(
    list(_loop.REJECTED_FAMILIES) + list(_rec.ALL_REJECTED_FAMILIES)
    + list(V2_BLACKLIST))))


def get_candidate_7_proposal_label() -> str:
    return C7P_LABEL


def build_candidate_7_family_proposal() -> dict[str, Any]:
    """Assemble the proposal. Chain-gated on the six-record ledger
    (C1-C6 all REJECTED_KEPT_ON_RECORD), Overnight Research Autopilot
    V2, Recommendation V1, and Autopilot Loop V1. Validated by the
    pushed loop's validate_candidate_family_proposal + screen_output
    _language gates AND by Recommendation V1's apply_hard_rejection
    _rules."""
    record: dict[str, Any] = {
        "schema_version": C7P_SCHEMA_VERSION, "label": C7P_LABEL,
        "mode": C7P_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [],
        "candidate_id": CANDIDATE_ID,
        "candidate_family": CANDIDATE_FAMILY,
        "selected_candidate_id": CANDIDATE_ID,
        "clean_hypothesis": CLEAN_HYPOTHESIS,
        "difference_from_rejected_families":
            DIFFERENCE_FROM_REJECTED_FAMILIES,
        "loop_proposal": dict(LOOP_PROPOSAL),
        "loop_proposal_check": None,
        "hypothesis_language_check": None,
        "recommendation_hard_rules_check": None,
        "symbols": list(SYMBOLS), "timeframe": TIMEFRAME,
        "direction": DIRECTION, "direction_note": DIRECTION_NOTE,
        "trigger_family": dict(TRIGGER_FAMILY),
        "stop_family": dict(STOP_FAMILY),
        "target_policy": {"variants": list(TARGET_VARIANTS),
                          "target_price_formula":
                              TARGET_POLICY["target_price_formula"],
                          "no_new_variants_after_label_freeze": True},
        "fee_aware_geometry_policy":
            dict(FEE_AWARE_GEOMETRY_POLICY),
        "anti_cluster_policy": dict(ANTI_CLUSTER_POLICY),
        "non_overlap_policy": dict(NON_OVERLAP_POLICY),
        "edit_allowance_policy": EDIT_ALLOWANCE_POLICY,
        "expected_failure_modes": list(EXPECTED_FAILURE_MODES),
        "seed_usage": list(SEED_USAGE),
        "seeds_are_never_rescue_paths": SEEDS_ARE_NEVER_RESCUE_PATHS,
        "required_evidence_stages": list(_loop.LOOP_STAGES),
        "rejection_conditions": list(_loop.AUTO_REJECTION_RULES),
        "promotion_to_human_review_conditions": list(
            PROMOTION_TO_HUMAN_REVIEW_CONDITIONS),
        "safety_and_no_claim": list(SAFETY_AND_NO_CLAIM),
        "all_known_rejected_families": list(
            ALL_KNOWN_REJECTED_FAMILIES),
        "ledger_status_six_records": None,
        "ledger_all_rejected_kept_on_record": None,
        "v2_verdict": None,
        "recommendation_verdict": None,
        "autopilot_loop_verdict": None,
        "next_loop_stage": NEXT_LOOP_STAGE,
        "human_review_required": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True, "live_gate_locked": True,
        "is_a_rescue_attempt": False,
        "is_proposal_only": True,
        "executes": False, "writes_files": False, "labels_now": False,
        "runs_spec_review_now": False,
        "runs_detector": False, "runs_real_candle_detection": False,
        "runs_relabel": False, "runs_replay": False,
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
        "creates_detector_label_replay_files_now": False,
        "creates_detector_implementation_now": False,
        "modifies_staged_market_data": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False, "authorizes_live_trading": False,
        "promotes_gate": False, "unlocks_downstream_gate": False,
        "claims_profitability": False,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    statuses = (C1_STATUS, C2_STATUS, C3_STATUS, C4_STATUS, C5_STATUS,
                C6_STATUS)
    record["ledger_status_six_records"] = list(statuses)
    record["ledger_all_rejected_kept_on_record"] = all(
        s == "REJECTED_KEPT_ON_RECORD" for s in statuses)
    if not record["ledger_all_rejected_kept_on_record"]:
        record["verdict"] = VERDICT_C7P_BLOCKED
        record["blockers"].append("six_record_ledger_broken")
        return record
    v2 = build_overnight_research_autopilot_v2_contract()
    record["v2_verdict"] = v2["verdict"]
    if v2["verdict"] != VERDICT_OAP2_READY:
        record["verdict"] = VERDICT_C7P_BLOCKED
        record["blockers"].append(
            "overnight_research_autopilot_v2_not_certifying")
        return record
    recommendation = _rec.build_candidate_recommendation()
    record["recommendation_verdict"] = recommendation["verdict"]
    if recommendation["verdict"] != _rec.VERDICT_CR_READY:
        record["verdict"] = VERDICT_C7P_BLOCKED
        record["blockers"].append("recommendation_not_certifying")
        return record
    loop_contract = _loop.build_autopilot_loop_contract()
    record["autopilot_loop_verdict"] = loop_contract["verdict"]
    if loop_contract["verdict"] != _loop.VERDICT_AP_READY:
        record["verdict"] = VERDICT_C7P_BLOCKED
        record["blockers"].append("autopilot_loop_not_certifying")
        return record
    # the family must NOT be in any of the three rejection-family
    # tuples (loop's, recommendation's, V2's)
    if CANDIDATE_FAMILY in _loop.REJECTED_FAMILIES \
            or CANDIDATE_FAMILY in _rec.ALL_REJECTED_FAMILIES \
            or CANDIDATE_FAMILY in V2_BLACKLIST:
        record["verdict"] = VERDICT_C7P_BLOCKED
        record["blockers"].append("family_is_a_rejected_family")
        return record
    proposal_check = _loop.validate_candidate_family_proposal(
        dict(LOOP_PROPOSAL))
    record["loop_proposal_check"] = proposal_check
    language_check = _loop.screen_output_language(CLEAN_HYPOTHESIS)
    record["hypothesis_language_check"] = language_check
    hard_check = _rec.apply_hard_rejection_rules({
        "family": CANDIDATE_FAMILY,
        "hypothesis": CLEAN_HYPOTHESIS,
        "materially_different_because":
            DIFFERENCE_FROM_REJECTED_FAMILIES,
        "why_not_rescue":
            ("volatility-regime shift is a new mechanism; no rejected "
             "family geometry, labels, or thresholds are reused; the "
             "c6 anti-cluster lesson is built in at the proposal as a "
             "pre-committed policy not a future edit"),
        "required_spec_gates": ("81_bps_floor_at_label_time",
                                "27_bps_fee_model", "wider_stop_rule",
                                "same_symbol_non_overlap",
                                "completed_bars_only_no_lookahead"),
        "direction": DIRECTION,
    })
    record["recommendation_hard_rules_check"] = hard_check
    if not proposal_check["acceptable"]:
        record["verdict"] = VERDICT_C7P_BLOCKED
        record["blockers"].append("loop_proposal_gate_rejected")
        record["blockers"].extend(proposal_check["errors"])
        return record
    if not language_check["acceptable"]:
        record["verdict"] = VERDICT_C7P_BLOCKED
        record["blockers"].append("forbidden_language_in_hypothesis")
        return record
    if not hard_check["acceptable"]:
        record["verdict"] = VERDICT_C7P_BLOCKED
        record["blockers"].append(
            "recommendation_hard_rules_rejected")
        record["blockers"].extend(hard_check["rejections"])
        return record
    record["verdict"] = VERDICT_C7P_READY
    return record


def validate_candidate_7_family_proposal(record: Any
                                         ) -> dict[str, Any]:
    """Validate shape and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_C7P_READY, VERDICT_C7P_BLOCKED):
        errors.append("bad_verdict")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if r.get("selected_candidate_id") != CANDIDATE_ID:
        errors.append("selected_candidate_id_tampered")
    if r.get("candidate_family") != CANDIDATE_FAMILY:
        errors.append("candidate_family_tampered")
    if r.get("candidate_family") in _loop.REJECTED_FAMILIES \
            or r.get("candidate_family") in _rec.ALL_REJECTED_FAMILIES \
            or r.get("candidate_family") in V2_BLACKLIST:
        errors.append("candidate_family_is_a_rejected_family")
    if r.get("clean_hypothesis") != CLEAN_HYPOTHESIS:
        errors.append("hypothesis_tampered")
    if r.get("difference_from_rejected_families") != (
            DIFFERENCE_FROM_REJECTED_FAMILIES):
        errors.append("difference_tampered")
    if r.get("loop_proposal") != LOOP_PROPOSAL:
        errors.append("loop_proposal_tampered")
    if r.get("symbols") != list(SYMBOLS) or r.get("timeframe") != (
            TIMEFRAME) or r.get("direction") != DIRECTION:
        errors.append("universe_timeframe_or_direction_tampered")
    if r.get("trigger_family") != TRIGGER_FAMILY:
        errors.append("trigger_family_tampered")
    if r.get("stop_family") != STOP_FAMILY:
        errors.append("stop_family_tampered")
    target = r.get("target_policy") or {}
    if target.get("variants") != list(TARGET_VARIANTS):
        errors.append("target_variants_tampered")
    if target.get("target_price_formula") != (
            TARGET_POLICY["target_price_formula"]):
        errors.append("target_price_formula_tampered")
    fee = r.get("fee_aware_geometry_policy") or {}
    if fee != FEE_AWARE_GEOMETRY_POLICY:
        errors.append("fee_aware_geometry_policy_tampered")
    if fee.get("fee_model_round_trip_bps") != 27:
        errors.append("fee_27bps_changed")
    if fee.get("minimum_gross_target_distance_floor_bps") != 81:
        errors.append("floor_81bps_changed")
    if fee.get("no_maker_rebate_assumption") is not True \
            or fee.get("no_zero_fee_assumption") is not True:
        errors.append("fee_assumption_weakened")
    if r.get("anti_cluster_policy") != ANTI_CLUSTER_POLICY:
        errors.append("anti_cluster_policy_tampered")
    if r.get("non_overlap_policy") != NON_OVERLAP_POLICY:
        errors.append("non_overlap_policy_tampered")
    if r.get("edit_allowance_policy") != EDIT_ALLOWANCE_POLICY:
        errors.append("edit_allowance_policy_tampered")
    if tuple(r.get("expected_failure_modes") or ()) != (
            EXPECTED_FAILURE_MODES):
        errors.append("expected_failure_modes_tampered")
    if tuple(r.get("seed_usage") or ()) != SEED_USAGE:
        errors.append("seed_usage_tampered")
    if r.get("seeds_are_never_rescue_paths") is not True:
        errors.append("seeds_must_never_be_rescue_paths")
    if tuple(r.get("required_evidence_stages") or ()) != (
            _loop.LOOP_STAGES):
        errors.append("required_evidence_stages_tampered")
    if tuple(r.get("rejection_conditions") or ()) != (
            _loop.AUTO_REJECTION_RULES):
        errors.append("rejection_conditions_tampered")
    if tuple(r.get("safety_and_no_claim") or ()) != SAFETY_AND_NO_CLAIM:
        errors.append("safety_and_no_claim_tampered")
    if r.get("next_loop_stage") != NEXT_LOOP_STAGE:
        errors.append("next_loop_stage_tampered")
    if r.get("next_required_action") != NEXT_REQUIRED_ACTION:
        errors.append("next_required_action_tampered")
    for key, want in (("human_review_required", True),
                      ("paper_trading_gate_locked", True),
                      ("micro_live_gate_locked", True),
                      ("live_gate_locked", True),
                      ("is_a_rescue_attempt", False),
                      ("is_proposal_only", True)):
        if r.get(key) is not want:
            errors.append("constitution_flag_wrong:" + key)
    for key in ("executes", "writes_files", "labels_now",
                "runs_spec_review_now", "runs_detector",
                "runs_real_candle_detection",
                "runs_relabel", "runs_replay",
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
                "creates_detector_label_replay_files_now",
                "creates_detector_implementation_now",
                "modifies_staged_market_data",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate", "claims_profitability"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    if r.get("verdict") == VERDICT_C7P_READY and r.get("blockers"):
        errors.append("ready_with_blockers")
    return {"valid": not errors, "errors": errors}
