"""SPARTA STRATEGY FACTORY REJECTED FAMILY BLACKLIST V5 (READ-ONLY,
RESEARCH ONLY, NO EXECUTION, NO TRADING, NO AUTO-PUSH, NO SCHEDULER):
extends the pushed Rejected Family Blacklist V4 from eight to NINE
rejected families by adding `low_volume_downside_capitulation_mean
_reversion` (Candidate #9, rejected on origin/master after the single
edit on DOWNSIDE_Z_SCORE_THRESHOLD failed to resolve the sample-size
adequacy structural failure).

V5 is the recommendation-memory layer ON TOP OF the pushed V4
contract. It freezes ONLY:

  - the NINE-family blacklist that any future Candidate #10+ family
    proposal must clear,
  - the nine-record ledger gating that produces it,
  - the explicit requirements every C10 hypothesis must satisfy
    BEFORE entering the Autopilot Loop V1 lifecycle: materially
    different from all nine rejected families, 27 bps fee model
    locked, 81 bps gross target-distance floor locked, anti-cluster
    protection at proposal time (C6 lesson), sample-size adequacy
    assessment at proposal time (C7 lesson), explicit-edge-argument-
    beyond-pattern-geometry at proposal time (C8 lesson), no
    structurally-too-sparse joint or intersection trigger unless
    sample-size adequacy is pre-justified at proposal time (C9
    lesson), no winner wording, no profitability claim.

V5 DOES NOT:

  - generate or propose Candidate #10,
  - run any detector / replay / relabel / aggregator / fetcher,
  - authorize any execution, paper, micro-live, or live trading,
  - touch any credentials / wallet / account / broker / exchange /
    order / api,
  - start any scheduler, send any notifications,
  - auto-commit or auto-push,
  - claim profitability or declare any family a winner,
  - promote any gate or unlock any downstream trading gate.

Chain-gated live on:
  - the pushed NINE-record rejection ledger (C1-C9 all REJECTED
    _KEPT_ON_RECORD),
  - the pushed Rejected Family Blacklist V4,
  - the pushed Rejected Family Blacklist V3,
  - the pushed Overnight Research Autopilot V2,
  - the pushed Recommendation V1,
  - the pushed Autopilot Loop V1,
  - the C9 rejection record (which exports the
    future_family_blacklist_addition source-of-truth for the new
    entry).

If ANY of those break, V5 returns BLOCKED with explicit blockers.
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
from sparta_commander.liquidity_sweep_mean_reversion_v1_rejection_record import (
    REJECTION_STATUS as C8_STATUS,
)
from sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_rejection_record import (
    FUTURE_FAMILY_BLACKLIST_ADDITION as C9_BLACKLIST_ADDITION,
    REJECTION_REASON as C9_REJECTION_REASON,
    REJECTION_STATUS as C9_STATUS,
    VERDICT_RJ9_RECORDED,
    build_c9_rejection_record,
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
    VERDICT_OAP2_READY,
    build_overnight_research_autopilot_v2_contract,
)
from sparta_commander.strategy_factory_rejected_family_blacklist_v3_contract import (
    VERDICT_BL3_READY,
    build_rejected_family_blacklist_v3,
)
from sparta_commander.strategy_factory_rejected_family_blacklist_v4_contract import (
    REJECTED_FAMILY_LOGIC_BLACKLIST_V4 as V4_BLACKLIST,
    VERDICT_BL4_READY,
    build_rejected_family_blacklist_v4,
)
from sparta_commander.volatility_compression_expansion_v1_rejection_record import (
    REJECTION_STATUS as C7_STATUS,
)

BL5_SCHEMA_VERSION = (
    "strategy_factory_rejected_family_blacklist_v5.v1")
BL5_LABEL = (
    "SPARTA Strategy Factory Rejected Family Blacklist V5 "
    "(READ-ONLY, RESEARCH ONLY, NO EXECUTION, NO TRADING, NO "
    "AUTO-PUSH, NO SCHEDULER, NOT A PROFITABILITY CLAIM, "
    "NINE-FAMILY BLACKLIST)")
BL5_MODE = "RESEARCH_ONLY"
VERDICT_BL5_READY = (
    "STRATEGY_FACTORY_REJECTED_FAMILY_BLACKLIST_V5_READY")
VERDICT_BL5_BLOCKED = (
    "STRATEGY_FACTORY_REJECTED_FAMILY_BLACKLIST_V5_BLOCKED")
NEXT_REQUIRED_ACTION = (
    "HUMAN_DECISION_DRAFT_CANDIDATE_10_FAMILY_PROPOSAL_USING_V5"
    "_BLACKLIST")

# ----------------------------------------------------------------------------
# the nine-record rejection ledger as input (declarative)
# ----------------------------------------------------------------------------
LEDGER_KEYS = ("C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9")
LEDGER_FAMILY_LABELS = {
    "C1": "ny_session_fvg_choch_v3",
    "C2": "crypto_intraday_breakout_pullback_structure_v2",
    "C3": "btc_sol_long_trend_continuation_v1",
    "C4": "sol_btc_long_1h_swing_structure",
    "C5": "eth_sol_relative_strength_pullback_continuation_v1",
    "C6": "multi_symbol_relative_strength_rotation_filter",
    "C7": "volatility_compression_expansion",
    "C8": "liquidity_sweep_mean_reversion",
    "C9": "low_volume_downside_capitulation_mean_reversion",
}
REQUIRED_LEDGER_STATUS = "REJECTED_KEPT_ON_RECORD"

# Per-family rejection reasons (one-liners summarizing the pushed
# rejection record for each candidate)
PER_FAMILY_REJECTION_REASON = {
    "C1": ("ny session fvg choch v3: failed on fee-honest replay; "
           "intraday session-anchored gap+structure setups did not "
           "produce edge net of 27 bps round-trip in this sample"),
    "C2": ("crypto intraday breakout pullback structure v2: failed on "
           "fee-honest replay; pullback-after-breakout did not produce "
           "edge net of fees on this sample"),
    "C3": ("btc sol long trend continuation v1: failed on fee-honest "
           "replay; cross-symbol trend continuation alone did not "
           "produce edge net of fees on this sample"),
    "C4": ("sol btc long 1h swing structure: failed on fee-honest "
           "replay; cross-symbol swing-structure entries did not "
           "produce edge net of fees on this sample"),
    "C5": ("eth sol relative strength pullback continuation v1: small "
           "sample net-negative; the one authorized structure edit "
           "added zero new accepted setups; trigger-window extension "
           "is not the bottleneck"),
    "C6": ("multi-symbol relative strength rotation filter v1: "
           "original replay net-negative and gross-negative at every "
           "variant; the single authorized 24-bar label-time "
           "clustering filter edit reduced overlap from 334 to 37 "
           "skips as designed but did not rescue edge"),
    "C7": ("volatility compression expansion v1: zero accepted "
           "real-candle setups before and after the single edit; "
           "atr(14) never dropped below the contraction fraction "
           "(0.6 in pushed spec or 0.7 in pushed edit) for 5 "
           "consecutive bars on the btcusd 4h 2026-05-02_2026-06-10 "
           "sample window"),
    "C8": ("liquidity sweep mean reversion v1: 51 accepted-post-anti-"
           "cluster real-candle setups on btcusd 15m 2026-05-02_"
           "2026-06-10; all three replay variants structurally net-"
           "negative in-sample (2R net = -45.78, 3R = -58.84, 4R = "
           "-65.78) under 27 bps fees + 81 bps floor + 8-bar anti-"
           "cluster + 96-bar timeout; best variant deeply negative "
           "and not a near-miss; single edit token NOT spent"),
    "C9": ("low volume downside capitulation mean reversion v1: 1 "
           "accepted-post-anti-cluster real-candle setup on btcusd "
           "15m 2026-05-02_2026-06-10 pre-edit and 5 accepted-post "
           "post-edit; the single authorized edit relaxed downside "
           "z-score threshold from -2.0 to -1.5 and expanded trigger "
           "attempts from 8 to 27 (3.4x) as predicted by the lower-"
           "tail expansion, yet sample-size adequacy STILL failed "
           "(5 < 20 threshold); the volume condition (the structural "
           "microstructure edge) is the binding constraint, not the "
           "z-score; post-edit auto-rejection trigger sample_size"
           "_still_below_threshold_after_edited_detection fired; "
           "edit token spent; no replay run"),
}

# ----------------------------------------------------------------------------
# the NINE-family rejected blacklist (the V5 update)
# ----------------------------------------------------------------------------
REJECTED_FAMILY_LOGIC_BLACKLIST_V5 = (
    "ny_session_fvg_choch_v3",
    "crypto_intraday_breakout_pullback_structure_v2",
    "btc_sol_long_trend_continuation_v1",
    "sol_btc_long_1h_swing_structure",
    "eth_sol_relative_strength_pullback_continuation_v1",
    "multi_symbol_relative_strength_rotation_filter",
    "volatility_compression_expansion",
    "liquidity_sweep_mean_reversion",
    "low_volume_downside_capitulation_mean_reversion",
)

PRIOR_V4_BLACKLIST = tuple(V4_BLACKLIST)
NEW_ENTRY_ADDED = C9_BLACKLIST_ADDITION

# ----------------------------------------------------------------------------
# requirements every C10 hypothesis must satisfy at proposal time
# ----------------------------------------------------------------------------
C10_PROPOSAL_REQUIREMENTS = {
    "schema_kind":
        "strategy_factory_rejected_family_blacklist_v5_c10"
        "_requirements",
    "required_fields": (
        "proposed_family_label",
        "hypothesis_statement",
        "edge_source_hypothesis",
        "explicit_edge_argument_beyond_pattern_geometry",
        "joint_or_intersection_trigger_sample_size_pre_justification",
        "universe_proposal",
        "timeframe_proposal",
        "direction_proposal",
        "fee_assumption_round_trip_bps",
        "minimum_gross_target_distance_floor_bps",
        "sample_window_proposal",
        "differentiation_from_each_rejected_family",
        "explicit_non_reuse_of_rejected_family_logic",
        "anti_cluster_protection_at_proposal_time",
        "sample_size_adequacy_assessment_at_proposal_time",
        "rationale_paragraph",
        "human_review_required_at_every_gate",
        "no_promotion_no_paper_no_live",
    ),
    "differentiation_must_address_each_of":
        REJECTED_FAMILY_LOGIC_BLACKLIST_V5,
    "rejected_family_logic_blacklist":
        REJECTED_FAMILY_LOGIC_BLACKLIST_V5,
    "fee_assumption_must_equal_27_bps_round_trip": True,
    "minimum_floor_must_equal_81_bps": True,
    "anti_cluster_protection_must_be_built_in_at_proposal_time":
        True,
    "sample_size_adequacy_must_be_assessed_at_proposal_time": True,
    "explicit_edge_argument_beyond_pattern_geometry_required":
        True,
    "joint_or_intersection_trigger_sample_size_pre_justification"
    "_required": True,
    "must_not_rely_on_overly_narrow_intersection_of_trigger"
    "_conditions_unless_sample_size_adequacy_is_pre_justified":
        True,
    "must_not_reuse_any_rejected_family_logic": True,
    "human_review_required_at_every_gate": True,
    "plan_is_not_a_promotion": True,
}

# ----------------------------------------------------------------------------
# lessons inherited from C1-C9 that the C10 hypothesis must respect
# ----------------------------------------------------------------------------
INHERITED_LESSONS = (
    "c1_lesson: session-anchored structure-shift triggers on 15m did "
    "not produce edge net of 27 bps; avoid intraday session anchors "
    "as the sole edge source",
    "c2_lesson: pullback-after-breakout structure did not produce "
    "edge net of fees; avoid bare breakout-pullback structures",
    "c3_lesson: cross-symbol trend continuation did not produce edge "
    "net of fees; avoid trend-following without a structural cost "
    "filter",
    "c4_lesson: cross-symbol swing-structure entries did not produce "
    "edge net of fees; avoid relying on swing-pair coupling",
    "c5_lesson: trigger-window extension is not a rescue mechanism; "
    "fee-sensitive thin-risk setups must be filtered before replay",
    "c6_lesson: dense same-symbol clusters waste replay-time non-"
    "overlap; ANY new family must include anti-cluster protection "
    "at proposal time, not as a post-hoc edit",
    "c7_lesson: zero-setup strictness is a structural failure mode; "
    "ANY new family must include a sample-size adequacy assessment "
    "at proposal time and a structural argument that the trigger "
    "can fire within the available sample window",
    "c8_lesson: structural cleanliness alone does not produce edge; "
    "a clean liquidity-sweep-plus-reclaim mean-reversion thesis with "
    "proposal-level anti-cluster + sample-size adequacy still "
    "produced all-three-variants-net-negative in-sample under 27 "
    "bps fees + 81 bps floor; ANY new family must provide an "
    "EXPLICIT EDGE ARGUMENT BEYOND PATTERN GEOMETRY at proposal "
    "time -- a reason WHY the entry should survive fees + floor, "
    "not just a pattern definition",
    "c9_lesson: joint price-AND-volume thresholds can be structurally "
    "too sparse. future candidates must not rely on an overly narrow "
    "intersection of trigger conditions unless sample-size adequacy "
    "is pre-justified. the binding constraint in a joint trigger is "
    "the intersection rate, not the marginal rates -- a single "
    "structural edit to one threshold cannot rescue a family where "
    "the other condition is the bottleneck. C10 must clear the V5 "
    "blacklist and be materially different from C1-C9.",
)

CLAIM_LOCKS = (
    "no_profitability_claim",
    "no_paper_approval",
    "no_live_approval",
    "no_execution_approval",
    "no_winner_wording",
    "no_promotion_by_v5",
    "no_unlock_by_v5",
    "no_scheduler_activation",
    "no_auto_commit",
    "no_auto_push",
    "no_candidate_10_generation_in_this_gate",
    "no_candidate_10_proposal_drafting_in_this_gate",
)


def get_blacklist_v5_label() -> str:
    return BL5_LABEL


def build_rejected_family_blacklist_v5() -> dict[str, Any]:
    """Assemble the V5 blacklist contract. Pure (no arguments).
    BLOCKED if the nine-record ledger does not hold, the C9 rejection
    record is not certifying, V4 is not certifying, V3 is not
    certifying, the Autopilot Loop V1 is not certifying, or the
    Recommendation V1 is not certifying."""
    record: dict[str, Any] = {
        "schema_version": BL5_SCHEMA_VERSION,
        "label": BL5_LABEL, "mode": BL5_MODE,
        "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [],
        "ledger_keys": list(LEDGER_KEYS),
        "ledger_family_labels": dict(LEDGER_FAMILY_LABELS),
        "required_ledger_status": REQUIRED_LEDGER_STATUS,
        "ledger_status_nine_records": None,
        "ledger_all_rejected_kept_on_record": None,
        "per_family_rejection_reason":
            dict(PER_FAMILY_REJECTION_REASON),
        "rejected_family_logic_blacklist_v5":
            list(REJECTED_FAMILY_LOGIC_BLACKLIST_V5),
        "blacklist_length": len(REJECTED_FAMILY_LOGIC_BLACKLIST_V5),
        "prior_v4_blacklist": list(PRIOR_V4_BLACKLIST),
        "new_entry_added": NEW_ENTRY_ADDED,
        "c10_proposal_requirements": {
            "schema_kind":
                C10_PROPOSAL_REQUIREMENTS["schema_kind"],
            "required_fields":
                list(C10_PROPOSAL_REQUIREMENTS["required_fields"]),
            "differentiation_must_address_each_of":
                list(C10_PROPOSAL_REQUIREMENTS[
                    "differentiation_must_address_each_of"]),
            "rejected_family_logic_blacklist":
                list(C10_PROPOSAL_REQUIREMENTS[
                    "rejected_family_logic_blacklist"]),
            "fee_assumption_must_equal_27_bps_round_trip": True,
            "minimum_floor_must_equal_81_bps": True,
            "anti_cluster_protection_must_be_built_in_at_proposal"
            "_time": True,
            "sample_size_adequacy_must_be_assessed_at_proposal_time":
                True,
            "explicit_edge_argument_beyond_pattern_geometry_required":
                True,
            "joint_or_intersection_trigger_sample_size_pre"
            "_justification_required": True,
            "must_not_rely_on_overly_narrow_intersection_of_trigger"
            "_conditions_unless_sample_size_adequacy_is_pre_justified":
                True,
            "must_not_reuse_any_rejected_family_logic": True,
            "human_review_required_at_every_gate": True,
            "plan_is_not_a_promotion": True},
        "inherited_lessons": list(INHERITED_LESSONS),
        "c9_rejection_status": C9_STATUS,
        "c9_rejection_reason": C9_REJECTION_REASON,
        "c9_future_family_blacklist_addition":
            C9_BLACKLIST_ADDITION,
        "claim_locks": list(CLAIM_LOCKS),
        "human_review_required": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True, "live_gate_locked": True,
        "executes": False, "writes_files": False,
        "runs_detector": False,
        "runs_real_candle_detection": False,
        "runs_relabel": False, "runs_replay": False,
        "labels_now": False,
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
        "generates_candidate_10_proposal_now": False,
        "generates_morning_report_now": False,
        "drafts_candidate_10_in_this_gate": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False, "authorizes_live_trading": False,
        "promotes_gate": False, "unlocks_downstream_gate": False,
        "claims_profitability": False,
        "uses_external_data_source": False,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    statuses = (C1_STATUS, C2_STATUS, C3_STATUS, C4_STATUS, C5_STATUS,
                C6_STATUS, C7_STATUS, C8_STATUS, C9_STATUS)
    record["ledger_status_nine_records"] = list(statuses)
    record["ledger_all_rejected_kept_on_record"] = all(
        s == REQUIRED_LEDGER_STATUS for s in statuses)
    if not record["ledger_all_rejected_kept_on_record"]:
        record["verdict"] = VERDICT_BL5_BLOCKED
        record["blockers"].append("nine_record_ledger_broken")
        return record
    # the C9 rejection record itself must certify
    c9_record = build_c9_rejection_record()
    if c9_record["verdict"] != VERDICT_RJ9_RECORDED:
        record["verdict"] = VERDICT_BL5_BLOCKED
        record["blockers"].append(
            "c9_rejection_record_not_certifying")
        record["blockers"].extend(c9_record.get("blockers") or [])
        return record
    # the new blacklist entry must equal the C9 contract's source-of-
    # truth
    if NEW_ENTRY_ADDED != C9_BLACKLIST_ADDITION \
            or NEW_ENTRY_ADDED not in (
            REJECTED_FAMILY_LOGIC_BLACKLIST_V5):
        record["verdict"] = VERDICT_BL5_BLOCKED
        record["blockers"].append(
            "new_blacklist_entry_must_match_c9_record")
        return record
    # the prior V4 blacklist must be a STRICT subset of V5 (we only
    # add; we never remove)
    if not set(PRIOR_V4_BLACKLIST).issubset(set(
            REJECTED_FAMILY_LOGIC_BLACKLIST_V5)):
        record["verdict"] = VERDICT_BL5_BLOCKED
        record["blockers"].append(
            "v4_blacklist_must_remain_a_subset_of_v5")
        return record
    if len(REJECTED_FAMILY_LOGIC_BLACKLIST_V5) != (
            len(PRIOR_V4_BLACKLIST) + 1):
        record["verdict"] = VERDICT_BL5_BLOCKED
        record["blockers"].append(
            "v5_must_add_exactly_one_new_entry_over_v4")
        return record
    if build_rejected_family_blacklist_v4()["verdict"] != (
            VERDICT_BL4_READY):
        record["verdict"] = VERDICT_BL5_BLOCKED
        record["blockers"].append("v4_blacklist_not_certifying")
        return record
    if build_rejected_family_blacklist_v3()["verdict"] != (
            VERDICT_BL3_READY):
        record["verdict"] = VERDICT_BL5_BLOCKED
        record["blockers"].append("v3_blacklist_not_certifying")
        return record
    if build_overnight_research_autopilot_v2_contract()["verdict"] != (
            VERDICT_OAP2_READY):
        record["verdict"] = VERDICT_BL5_BLOCKED
        record["blockers"].append(
            "overnight_research_autopilot_v2_not_certifying")
        return record
    if _rec.build_candidate_recommendation()["verdict"] != (
            _rec.VERDICT_CR_READY):
        record["verdict"] = VERDICT_BL5_BLOCKED
        record["blockers"].append("recommendation_v1_not_certifying")
        return record
    if _loop.build_autopilot_loop_contract()["verdict"] != (
            _loop.VERDICT_AP_READY):
        record["verdict"] = VERDICT_BL5_BLOCKED
        record["blockers"].append("autopilot_loop_v1_not_certifying")
        return record
    record["verdict"] = VERDICT_BL5_READY
    return record


def validate_rejected_family_blacklist_v5(
        record: Any) -> dict[str, Any]:
    """Validate shape, frozen blacklist, and the no-execution surface."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_BL5_READY, VERDICT_BL5_BLOCKED):
        errors.append("bad_verdict")
    if list(r.get("ledger_keys") or ()) != list(LEDGER_KEYS):
        errors.append("ledger_keys_tampered")
    if r.get("ledger_family_labels") != LEDGER_FAMILY_LABELS:
        errors.append("ledger_family_labels_tampered")
    if r.get("required_ledger_status") != REQUIRED_LEDGER_STATUS:
        errors.append("required_ledger_status_tampered")
    if r.get("per_family_rejection_reason") != (
            PER_FAMILY_REJECTION_REASON):
        errors.append("per_family_rejection_reason_tampered")
    if tuple(r.get("rejected_family_logic_blacklist_v5") or ()) != (
            REJECTED_FAMILY_LOGIC_BLACKLIST_V5):
        errors.append("blacklist_v5_tampered")
    if r.get("blacklist_length") != 9:
        errors.append("blacklist_length_must_be_9")
    if tuple(r.get("prior_v4_blacklist") or ()) != PRIOR_V4_BLACKLIST:
        errors.append("prior_v4_blacklist_tampered")
    if r.get("new_entry_added") != NEW_ENTRY_ADDED:
        errors.append("new_entry_added_tampered")
    if r.get("c9_rejection_status") != "REJECTED_KEPT_ON_RECORD":
        errors.append("c9_rejection_status_must_remain_rejected")
    if r.get("c9_rejection_reason") != C9_REJECTION_REASON:
        errors.append("c9_rejection_reason_tampered")
    if r.get("c9_future_family_blacklist_addition") != (
            C9_BLACKLIST_ADDITION):
        errors.append("c9_blacklist_addition_tampered")
    # c10 proposal requirements
    reqs = r.get("c10_proposal_requirements") or {}
    if reqs.get("schema_kind") != C10_PROPOSAL_REQUIREMENTS[
            "schema_kind"]:
        errors.append("c10_requirements_schema_kind_tampered")
    if tuple(reqs.get("required_fields") or ()) != (
            C10_PROPOSAL_REQUIREMENTS["required_fields"]):
        errors.append("c10_required_fields_tampered")
    if tuple(reqs.get(
            "differentiation_must_address_each_of") or ()) != (
            C10_PROPOSAL_REQUIREMENTS[
                "differentiation_must_address_each_of"]):
        errors.append("c10_differentiation_targets_tampered")
    if tuple(reqs.get("rejected_family_logic_blacklist") or ()) != (
            REJECTED_FAMILY_LOGIC_BLACKLIST_V5):
        errors.append("c10_blacklist_reference_tampered")
    for key in ("fee_assumption_must_equal_27_bps_round_trip",
                "minimum_floor_must_equal_81_bps",
                "anti_cluster_protection_must_be_built_in_at_proposal"
                "_time",
                "sample_size_adequacy_must_be_assessed_at_proposal"
                "_time",
                "explicit_edge_argument_beyond_pattern_geometry"
                "_required",
                "joint_or_intersection_trigger_sample_size_pre"
                "_justification_required",
                "must_not_rely_on_overly_narrow_intersection_of"
                "_trigger_conditions_unless_sample_size_adequacy_is"
                "_pre_justified",
                "must_not_reuse_any_rejected_family_logic",
                "human_review_required_at_every_gate",
                "plan_is_not_a_promotion"):
        if reqs.get(key) is not True:
            errors.append("c10_requirement_flag_wrong:" + key)
    if tuple(r.get("inherited_lessons") or ()) != INHERITED_LESSONS:
        errors.append("inherited_lessons_tampered")
    if tuple(r.get("claim_locks") or ()) != CLAIM_LOCKS:
        errors.append("claim_locks_tampered")
    for key, want in (("human_review_required", True),
                      ("paper_trading_gate_locked", True),
                      ("micro_live_gate_locked", True),
                      ("live_gate_locked", True)):
        if r.get(key) is not want:
            errors.append("constitution_flag_wrong:" + key)
    for key in ("executes", "writes_files",
                "runs_detector", "runs_real_candle_detection",
                "runs_relabel", "runs_replay", "labels_now",
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
                "generates_candidate_10_proposal_now",
                "generates_morning_report_now",
                "drafts_candidate_10_in_this_gate",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate", "claims_profitability",
                "uses_external_data_source"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    if r.get("next_required_action") != NEXT_REQUIRED_ACTION:
        errors.append("next_required_action_tampered")
    if r.get("verdict") == VERDICT_BL5_READY and r.get("blockers"):
        errors.append("ready_with_blockers")
    return {"valid": not errors, "errors": errors}
