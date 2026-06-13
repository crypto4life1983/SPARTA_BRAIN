"""SPARTA CANDIDATE #6 SINGLE PRE-COMMITTED EDIT --
SAME-SYMBOL CLUSTERING FILTER AT LABEL TIME
(READ-ONLY, RESEARCH ONLY, STRUCTURE FILTER ONLY,
NOT A RESCUE, NOT A CLAIM):
MULTI_SYMBOL_RELATIVE_STRENGTH_ROTATION_FILTER_V1.

Spends the family's SINGLE pre-committed edit token on a LABEL-TIME
clustering filter. The filter freezes EXACTLY one structural rule:
an accepted continuation event on a symbol is emitted only if at least
24 completed 1h bars (one trading day at the 1h timeframe) have
elapsed since the most recent prior accepted event on the SAME symbol
within this sample window. Tie-breaker keeps the earlier event and
drops the later one. The replay-time non-overlap filter is unchanged
and runs after the clustering filter on the reduced label set.

THE EDIT IS MOTIVATED BY THE PUSHED REPLAY EVIDENCE -- NOT a rescue.
The pushed replay artifacts froze 334 overlap skips on 405 variant
slots (82 percent of variant slots wasted to clustering), 26/24/21
kept after non-overlap on 135 eligible setups, and net-negative on
every variant (2r net -11.085290, 3r net -10.846129, 4r net
-8.340989). The clustering filter targets that wasted-density problem
at label time so the surviving label set is sparser and more
independent before fee-honest replay re-runs.

NOTHING ELSE CHANGES. The 20-bar close-to-close RS metric, the
strict-rank-#1 trigger with ties_fail, the 10-bar fresh-closing-high
continuation event, the WIDER stop = max(1.5 * atr14, entry - 10-bar
low), the ATR(14) base, the 27 bps round-trip fee model, the 81 bps
gross target-distance floor, the BTCUSD/ETHUSD/SOLUSD universe, the
2r/3r/4r variant set, the long-only direction, the 1h timeframe, and
the 2026-05-02_2026-06-10 sample tag remain inviolable. Modifying any
of those invalidates this contract.

THIS CONTRACT BY ITSELF DOES NOT AUTHORIZE:
  - re-running the detector with the edit applied,
  - re-emitting labels,
  - re-running fee-honest replay,
  - changing the staged 15m candles,
  - paper, micro-live, or live execution,
  - any order / api / wallet / account / credential / broker / exchange
    capability,
  - any profitability or winner claim.

It freezes the edit RULE and burns the family's one edit token. The
next gate is the HUMAN decision on whether to authorize an edited
relabel run on the existing staged 15m window or close the family
without a relabel. If the eventual edited replay still triggers any
of the pushed auto-rejection rules, Candidate #6 becomes the sixth
ledger entry automatically -- no further edits are allowed.

Gated live on the pushed five-record rejection ledger, the pushed C6
family proposal, the pushed C6 spec review, the pushed C6 detector
spec, the pushed C6 dry-run review, the pushed C6 real-candle labels
review, the pushed C6 informational replay results review (honest
verdict edge_failed_all_variants_net_negative), the pushed
Recommendation V1, and the pushed Autopilot Loop V1.
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
from sparta_commander.multi_symbol_relative_strength_rotation_filter_dry_run_review_contract import (
    VERDICT_C6R_FROZEN,
    build_c6_dry_run_review,
)
from sparta_commander.multi_symbol_relative_strength_rotation_filter_family_proposal_contract import (
    CANDIDATE_FAMILY,
    CANDIDATE_ID,
    VERDICT_C6P_READY,
    build_candidate_6_family_proposal,
)
from sparta_commander.multi_symbol_relative_strength_rotation_filter_real_candle_labels_review_contract import (
    VERDICT_C6L_FROZEN,
    build_c6_labels_review,
)
from sparta_commander.multi_symbol_relative_strength_rotation_filter_replay_results_review_contract import (
    EXPECTED_OVERLAP_SKIPPED_TOTAL,
    EXPECTED_VARIANTS as REPLAY_EXPECTED_VARIANTS,
    HONEST_VERDICT as REPLAY_HONEST_VERDICT,
    VERDICT_C6RR_FROZEN,
    build_c6_replay_results_review,
)
from sparta_commander.multi_symbol_relative_strength_rotation_filter_spec_review_contract import (
    VERDICT_C6S_READY,
    build_candidate_6_spec_review,
)
from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
    REJECTION_STATUS as C1_STATUS,
)
from sparta_commander.sol_btc_long_1h_swing_structure_rejection_record_contract import (
    REJECTION_STATUS as C4_STATUS,
)

C6E_SCHEMA_VERSION = (
    "multi_symbol_relative_strength_rotation_filter_single_edit"
    "_clustering_filter.v1")
C6E_LABEL = ("SPARTA Candidate #6 Single Pre-Committed Edit -- "
             "Same-Symbol Clustering Filter at Label Time "
             "(READ-ONLY, RESEARCH ONLY, STRUCTURE FILTER ONLY, "
             "NOT A RESCUE, NOT A CLAIM)")
C6E_MODE = "RESEARCH_ONLY"
VERDICT_C6E_READY = (
    "C6_SINGLE_EDIT_CLUSTERING_FILTER_FROZEN_READY_FOR_HUMAN_REVIEW")
VERDICT_C6E_BLOCKED = "C6_SINGLE_EDIT_CLUSTERING_FILTER_BLOCKED"
NEXT_REQUIRED_ACTION = (
    "HUMAN_DECISION_C6_RELABEL_WITH_EDIT_OR_CLOSE_FAMILY")
CURRENT_LOOP_STAGE = "candidate_spec"
NEXT_LOOP_STAGE = "detector_and_label_review"

# --- The edit token ---------------------------------------------------------
EDIT_TOKEN_USED = 1
EDITS_REMAINING_AFTER_THIS = 0
EDIT_KIND = (
    "label_time_same_symbol_minimum_bar_gap_clustering_filter")
EDIT_SCOPE = (
    "applied at label-emission time on per-symbol completed 1h bar "
    "gap; runs BEFORE replay-time same-symbol non-overlap; does not "
    "touch any detector primitive, any stop/target geometry, the fee "
    "model, the 81 bps floor, the universe, the variants, or the "
    "staged 15m candles")

# --- The frozen filter rule -------------------------------------------------
MIN_BARS_BETWEEN_SAME_SYMBOL_ACCEPTED_EVENTS_1H = 24
EDIT_RULE = {
    "applies_at": "label_emission_time_before_replay",
    "scope": "per_symbol",
    "constraint": (
        "an accepted continuation event on symbol S is emitted only "
        "if the most recent prior accepted event on the same symbol "
        "within this sample window is at least "
        "min_bars_between_same_symbol_accepted_events_1h completed 1h "
        "bars earlier"),
    "min_bars_between_same_symbol_accepted_events_1h":
        MIN_BARS_BETWEEN_SAME_SYMBOL_ACCEPTED_EVENTS_1H,
    "tie_breaker": "keep_the_earlier_event_drop_the_later_one",
    "applies_to_all_variants_uniformly": True,
    "applies_before_replay_time_non_overlap": True,
    "replay_time_non_overlap_unchanged": True,
    "leaves_15m_raw_data_unchanged": True,
    "no_intrabar_state": True,
    "no_lookahead": True,
    "deterministic": True,
    "no_other_detector_change": True,
}
EDIT_RATIONALE_FOR_24_BARS = (
    "24 completed 1h bars equals one full trading day at the 1h "
    "timeframe; it is longer than the 20-bar return_20 RS lookback "
    "and longer than the 10-bar structure/continuation lookback, so "
    "consecutive accepted events on the same symbol cannot share RS "
    "or structure inputs and are forced into distinct daily windows")

# --- Inviolable upstream rules this edit MUST NOT change --------------------
INVIOLABLE_RULES = {
    "rs_metric": "close_to_close_return",
    "rs_formula": "return_20 = close[t] / close[t-20] - 1",
    "rs_lookback_bars_1h": 20,
    "rank_rule": "strict_rank_1_ties_fail",
    "rank_additional_rule": "return_20(candidate) > 0",
    "continuation_event_closing_high_lookback_bars": 10,
    "continuation_entry_price": "close_of_the_event_bar",
    "continuation_evaluation_starts": "next_1h_bar_after_event_close",
    "stop_distance_formula": (
        "max(1.5 * atr14, structure_stop_distance)"),
    "structure_lookback_bars": 10,
    "atr_length": 14,
    "atr_multiplier": 1.5,
    "fee_round_trip_bps": 27,
    "minimum_gross_target_distance_floor_bps": 81,
    "universe": ("BTCUSD", "ETHUSD", "SOLUSD"),
    "target_variants": ("2r", "3r", "4r"),
    "target_price_formula": (
        "entry_price + r_multiple * stop_distance"),
    "direction": "long_only",
    "timeframe": "1h",
    "sample_tag": "2026-05-02_2026-06-10",
    "no_fetch_ever": True,
    "staged_data_never_modified": True,
    "no_maker_rebate_assumption": True,
    "no_zero_fee_assumption": True,
}

# --- Frozen replay evidence motivating the edit -----------------------------
FROZEN_REPLAY_EVIDENCE_FOR_EDIT = {
    "candidate_id": CANDIDATE_ID,
    "honest_verdict": REPLAY_HONEST_VERDICT,
    "eligible_setups_after_label_freeze": 135,
    "total_overlap_skips_across_variants":
        EXPECTED_OVERLAP_SKIPPED_TOTAL,
    "variant_2r_skipped_overlap": 109,
    "variant_3r_skipped_overlap": 111,
    "variant_4r_skipped_overlap": 114,
    "variant_2r_kept_after_non_overlap": 26,
    "variant_3r_kept_after_non_overlap": 24,
    "variant_4r_kept_after_non_overlap": 21,
    "variant_2r_net_r_total":
        REPLAY_EXPECTED_VARIANTS["2r"]["net_r_total"],
    "variant_3r_net_r_total":
        REPLAY_EXPECTED_VARIANTS["3r"]["net_r_total"],
    "variant_4r_net_r_total":
        REPLAY_EXPECTED_VARIANTS["4r"]["net_r_total"],
    "all_variants_net_negative": True,
    "all_variants_gross_negative": True,
    "all_hit_rates_below_gross_breakeven": True,
}

# --- Post-edit auto-rejection conditions (no new escape hatches) ------------
POST_EDIT_AUTO_REJECTION_TRIGGERS = (
    "any_variant_net_negative_after_edited_relabel_and_replay",
    "any_variant_gross_negative_after_edited_relabel_and_replay",
    "any_variant_hit_rate_below_gross_breakeven_after_edited_"
    "relabel_and_replay",
    "any_variant_kept_set_size_drops_below_minimum_evaluable_count",
    "any_artifact_hash_or_gate_mismatch_in_edited_pipeline",
    "any_attempt_to_change_an_inviolable_upstream_rule",
    "any_attempt_to_spend_a_second_edit_on_this_family",
)

# --- Claim locks ------------------------------------------------------------
CLAIM_LOCKS = (
    "edit_is_structure_filter_only_no_target_or_fee_manipulation",
    "edit_does_not_authorize_relabel",
    "edit_does_not_authorize_replay",
    "edit_does_not_authorize_paper_or_live_or_execution",
    "edit_is_not_a_rescue_attempt",
    "no_profitability_claim",
    "no_winner_wording",
    "automatic_rejection_if_any_post_edit_trigger_fires",
    "single_pre_committed_edit_token_spent_no_further_edits_allowed",
)


def get_c6_single_edit_label() -> str:
    return C6E_LABEL


def build_c6_single_edit_clustering_filter(
        repo_root: Any = ".", tracked_paths: Any = ()
) -> dict[str, Any]:
    """Assemble the C6 single-edit clustering-filter record, chain-gated
    on the full pushed C6 lane plus the five-record rejection ledger,
    Recommendation V1, and Autopilot Loop V1. The replay results review
    must certify with the honest verdict
    edge_failed_all_variants_net_negative -- the only valid reason to
    spend this edit."""
    record: dict[str, Any] = {
        "schema_version": C6E_SCHEMA_VERSION, "label": C6E_LABEL,
        "mode": C6E_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [],
        "candidate_id": CANDIDATE_ID,
        "candidate_family": CANDIDATE_FAMILY,
        "edit_token_used": EDIT_TOKEN_USED,
        "edits_remaining_after_this": EDITS_REMAINING_AFTER_THIS,
        "edit_kind": EDIT_KIND, "edit_scope": EDIT_SCOPE,
        "edit_rule": dict(EDIT_RULE),
        "edit_rationale_for_24_bars": EDIT_RATIONALE_FOR_24_BARS,
        "inviolable_rules": {key: (list(value) if isinstance(value,
                             tuple) else value) for key, value
                             in INVIOLABLE_RULES.items()},
        "frozen_replay_evidence_for_edit":
            dict(FROZEN_REPLAY_EVIDENCE_FOR_EDIT),
        "post_edit_auto_rejection_triggers":
            list(POST_EDIT_AUTO_REJECTION_TRIGGERS),
        "rejection_conditions": list(_loop.AUTO_REJECTION_RULES),
        "claim_locks": list(CLAIM_LOCKS),
        "current_loop_stage": CURRENT_LOOP_STAGE,
        "next_loop_stage": NEXT_LOOP_STAGE,
        "human_review_required": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True, "live_gate_locked": True,
        "edit_token_spent_by_this_contract": True,
        "this_is_the_only_allowed_c6_edit": True,
        "is_a_rescue_attempt": False,
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
        "authorizes_relabel": False, "authorizes_replay": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False, "authorizes_live_trading": False,
        "promotes_gate": False, "unlocks_downstream_gate": False,
        "claims_profitability": False,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    if not (C1_STATUS == C2_STATUS == C3_STATUS == C4_STATUS
            == C5_STATUS == "REJECTED_KEPT_ON_RECORD"):
        record["verdict"] = VERDICT_C6E_BLOCKED
        record["blockers"].append("ledger_broken")
        return record
    if build_candidate_6_family_proposal()["verdict"] != (
            VERDICT_C6P_READY):
        record["verdict"] = VERDICT_C6E_BLOCKED
        record["blockers"].append("family_proposal_not_certifying")
        return record
    if build_candidate_6_spec_review()["verdict"] != VERDICT_C6S_READY:
        record["verdict"] = VERDICT_C6E_BLOCKED
        record["blockers"].append("spec_review_not_certifying")
        return record
    if build_c6_dry_run_review()["verdict"] != VERDICT_C6R_FROZEN:
        record["verdict"] = VERDICT_C6E_BLOCKED
        record["blockers"].append("dry_run_review_not_certifying")
        return record
    labels_review = build_c6_labels_review(repo_root, tracked_paths)
    if labels_review["verdict"] != VERDICT_C6L_FROZEN:
        record["verdict"] = VERDICT_C6E_BLOCKED
        record["blockers"].append("labels_review_not_certifying")
        record["blockers"].extend(labels_review["failures"])
        return record
    replay_review = build_c6_replay_results_review(
        repo_root, tracked_paths)
    if replay_review["verdict"] != VERDICT_C6RR_FROZEN:
        record["verdict"] = VERDICT_C6E_BLOCKED
        record["blockers"].append("replay_results_review_not_certifying")
        record["blockers"].extend(replay_review["failures"])
        return record
    if replay_review.get("honest_verdict") != REPLAY_HONEST_VERDICT:
        record["verdict"] = VERDICT_C6E_BLOCKED
        record["blockers"].append("replay_honest_verdict_mismatch")
        return record
    if _rec.build_candidate_recommendation()["verdict"] != (
            _rec.VERDICT_CR_READY):
        record["verdict"] = VERDICT_C6E_BLOCKED
        record["blockers"].append("recommendation_not_certifying")
        return record
    if _loop.build_autopilot_loop_contract()["verdict"] != (
            _loop.VERDICT_AP_READY):
        record["verdict"] = VERDICT_C6E_BLOCKED
        record["blockers"].append("autopilot_loop_not_certifying")
        return record
    record["verdict"] = VERDICT_C6E_READY
    return record


def validate_c6_single_edit_clustering_filter(
        record: Any) -> dict[str, Any]:
    """Validate shape, frozen edit rule, inviolable rules, and safety
    invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_C6E_READY, VERDICT_C6E_BLOCKED):
        errors.append("bad_verdict")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if r.get("candidate_family") != CANDIDATE_FAMILY:
        errors.append("candidate_family_tampered")
    # edit token enforcement (rejects any second edit)
    if r.get("edit_token_used") != 1:
        errors.append("edit_token_used_must_be_exactly_1")
    if r.get("edits_remaining_after_this") != 0:
        errors.append("edits_remaining_after_this_must_be_0")
    if r.get("edit_kind") != EDIT_KIND:
        errors.append("edit_kind_tampered_must_be_clustering_filter")
    rule = r.get("edit_rule") or {}
    if rule != EDIT_RULE:
        errors.append("edit_rule_tampered")
    if rule.get("min_bars_between_same_symbol_accepted_events_1h") != 24:
        errors.append("min_bars_must_be_exactly_24")
    if rule.get("applies_at") != "label_emission_time_before_replay":
        errors.append("edit_must_apply_at_label_emission_time")
    if rule.get("scope") != "per_symbol":
        errors.append("edit_scope_must_be_per_symbol")
    if rule.get(
            "applies_before_replay_time_non_overlap") is not True \
            or rule.get(
            "replay_time_non_overlap_unchanged") is not True:
        errors.append("replay_time_non_overlap_protection_weakened")
    if rule.get("leaves_15m_raw_data_unchanged") is not True:
        errors.append("must_not_touch_staged_data")
    if rule.get("no_other_detector_change") is not True:
        errors.append("edit_must_be_filter_only_no_detector_rewrite")
    if rule.get("no_lookahead") is not True:
        errors.append("no_lookahead_protection_weakened")
    if rule.get("deterministic") is not True:
        errors.append("deterministic_requirement_weakened")
    if rule.get(
            "tie_breaker") != "keep_the_earlier_event_drop_the_later_one":
        errors.append("tie_breaker_tampered")
    # inviolable rules check: nothing else can move
    expected_invio = {key: (list(value) if isinstance(value, tuple)
                            else value) for key, value
                      in INVIOLABLE_RULES.items()}
    invio = r.get("inviolable_rules") or {}
    if invio != expected_invio:
        errors.append("inviolable_rules_tampered")
    if invio.get("rs_metric") != "close_to_close_return" or invio.get(
            "rs_lookback_bars_1h") != 20:
        errors.append("rs_metric_or_lookback_changed")
    if invio.get("rank_rule") != "strict_rank_1_ties_fail":
        errors.append("rank_rule_changed_ties_must_fail")
    if invio.get(
            "continuation_event_closing_high_lookback_bars") != 10:
        errors.append("continuation_high_rule_changed")
    if invio.get("stop_distance_formula") != (
            "max(1.5 * atr14, structure_stop_distance)"):
        errors.append("wider_stop_formula_changed")
    if invio.get("atr_length") != 14 or invio.get(
            "atr_multiplier") != 1.5:
        errors.append("atr_period_or_multiplier_changed")
    if invio.get("fee_round_trip_bps") != 27:
        errors.append("fee_27bps_changed")
    if invio.get("minimum_gross_target_distance_floor_bps") != 81:
        errors.append("floor_81bps_changed")
    if invio.get("universe") != ["BTCUSD", "ETHUSD", "SOLUSD"]:
        errors.append("universe_changed")
    if invio.get("target_variants") != ["2r", "3r", "4r"]:
        errors.append("target_variants_changed")
    if invio.get("target_price_formula") != (
            "entry_price + r_multiple * stop_distance"):
        errors.append("target_price_formula_changed")
    if invio.get("direction") != "long_only":
        errors.append("direction_changed")
    if invio.get("timeframe") != "1h":
        errors.append("timeframe_changed")
    if invio.get("sample_tag") != "2026-05-02_2026-06-10":
        errors.append("sample_tag_changed")
    if invio.get("no_fetch_ever") is not True or invio.get(
            "staged_data_never_modified") is not True:
        errors.append("data_boundary_weakened")
    if invio.get("no_maker_rebate_assumption") is not True \
            or invio.get("no_zero_fee_assumption") is not True:
        errors.append("fee_assumption_weakened")
    # frozen replay evidence motivation
    ev = r.get("frozen_replay_evidence_for_edit") or {}
    if ev != FROZEN_REPLAY_EVIDENCE_FOR_EDIT:
        errors.append("frozen_replay_evidence_for_edit_tampered")
    if ev.get("total_overlap_skips_across_variants") != 334:
        errors.append("motivation_334_skips_must_be_present")
    if ev.get("honest_verdict") != REPLAY_HONEST_VERDICT:
        errors.append("motivation_honest_verdict_must_match")
    if ev.get("all_variants_net_negative") is not True:
        errors.append("motivation_all_variants_net_negative_required")
    # post-edit auto-rejection triggers
    if tuple(r.get("post_edit_auto_rejection_triggers") or ()) != (
            POST_EDIT_AUTO_REJECTION_TRIGGERS):
        errors.append("post_edit_auto_rejection_triggers_tampered")
    if tuple(r.get("rejection_conditions") or ()) != (
            _loop.AUTO_REJECTION_RULES):
        errors.append("rejection_conditions_tampered")
    if tuple(r.get("claim_locks") or ()) != CLAIM_LOCKS:
        errors.append("claim_locks_tampered")
    # capability locks
    for key, want in (("human_review_required", True),
                      ("paper_trading_gate_locked", True),
                      ("micro_live_gate_locked", True),
                      ("live_gate_locked", True),
                      ("edit_token_spent_by_this_contract", True),
                      ("this_is_the_only_allowed_c6_edit", True),
                      ("is_a_rescue_attempt", False)):
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
                "authorizes_relabel", "authorizes_replay",
                "authorizes_paper_execution",
                "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate", "claims_profitability"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    if r.get("next_loop_stage") != "detector_and_label_review":
        errors.append("next_loop_stage_tampered")
    if r.get("next_required_action") != NEXT_REQUIRED_ACTION:
        errors.append("next_required_action_tampered")
    if r.get("verdict") == VERDICT_C6E_READY and r.get("blockers"):
        errors.append("ready_with_blockers")
    return {"valid": not errors, "errors": errors}
