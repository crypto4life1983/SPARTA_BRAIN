"""SPARTA STRATEGY FACTORY OVERNIGHT AUTOPILOT NEXT-CANDIDATE
PROPOSAL DRAFTER (READ-ONLY, RESEARCH ONLY, NO EXECUTION, NO
TRADING, NO AUTO-PUSH, NO SCHEDULER, NOT A PROFITABILITY CLAIM).

The drafter sits ON TOP OF the pushed Overnight Research Autopilot
V2 contract and adds two RESEARCH-ONLY templates plus a static
validator. Concretely:

  1) C10_PROPOSAL_DRAFT_TEMPLATE -- a NON-COMMITTED draft skeleton
     for the next-candidate family proposal that the human will
     fill in by hand. The drafter pre-populates the constraints
     that are already locked by the pushed chain (V5 blacklist,
     27 bps round-trip fee, 81 bps gross target-distance floor,
     proposal-level anti-cluster protection, proposal-level
     sample-size adequacy assessment, explicit edge argument
     beyond pattern geometry, joint/intersection-trigger sample-
     size pre-justification, human review at every gate). The
     drafter NEVER fills in the hypothesis, edge source, family
     label, universe, timeframe, or rationale -- those remain as
     `"TO_BE_FILLED_BY_HUMAN_REVIEW"` placeholders.

  2) MORNING_AUTOPILOT_REPORT_TEMPLATE -- a NON-COMMITTED morning
     report skeleton that surfaces the live nine-record ledger
     status, the V5 blacklist length, the current open gate, and
     the standing locks. The drafter NEVER auto-populates dates,
     SHAs, or active-candidate fields; it only freezes the SHAPE
     and pre-fills the locked structural values.

  3) validate_c10_proposal_draft(draft) -- a pure, never-raises
     static validator that, given a candidate human-filled draft,
     reports whether the draft satisfies every locked constraint
     before the human submits it as the real Candidate #10 family
     proposal. The validator does NOT mutate, store, commit,
     promote, or transmit the draft anywhere.

The drafter explicitly does NOT:
  - generate the Candidate #10 family proposal contract,
  - generate runners, data artifacts, detection files, replay
    files, schedulers, or trading files,
  - run the detector, replay, relabel, aggregator, or fetcher,
  - authorize any execution, paper, micro-live, or live trading,
  - touch any credentials / wallet / account / broker / exchange
    / order / api / network,
  - start any scheduler, send any notifications, auto-commit, or
    auto-push,
  - claim profitability or declare any family a winner,
  - promote any gate or unlock any downstream trading gate,
  - bypass human approval at any gate.

Chain-gated live on:
  - the pushed NINE-record rejection ledger (C1-C9 all REJECTED
    _KEPT_ON_RECORD),
  - the pushed Rejected Family Blacklist V5,
  - the pushed Rejected Family Blacklist V4,
  - the pushed Rejected Family Blacklist V3,
  - the pushed Overnight Research Autopilot V2,
  - the pushed Recommendation V1,
  - the pushed Autopilot Loop V1.

If ANY of those break, the drafter returns BLOCKED with explicit
blockers.
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
    REJECTION_STATUS as C9_STATUS,
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
    VERDICT_BL4_READY,
    build_rejected_family_blacklist_v4,
)
from sparta_commander.strategy_factory_rejected_family_blacklist_v5_contract import (
    C10_PROPOSAL_REQUIREMENTS as V5_C10_REQS,
    INHERITED_LESSONS as V5_INHERITED_LESSONS,
    LEDGER_FAMILY_LABELS as V5_LEDGER_FAMILY_LABELS,
    LEDGER_KEYS as V5_LEDGER_KEYS,
    PER_FAMILY_REJECTION_REASON as V5_PER_FAMILY_REASON,
    REJECTED_FAMILY_LOGIC_BLACKLIST_V5 as V5_BLACKLIST,
    VERDICT_BL5_READY,
    build_rejected_family_blacklist_v5,
)
from sparta_commander.volatility_compression_expansion_v1_rejection_record import (
    REJECTION_STATUS as C7_STATUS,
)

DRAFTER_SCHEMA_VERSION = (
    "strategy_factory_overnight_autopilot_next_candidate_proposal"
    "_drafter.v1")
DRAFTER_LABEL = (
    "SPARTA Strategy Factory Overnight Autopilot Next-Candidate "
    "Proposal Drafter (READ-ONLY, RESEARCH ONLY, NO EXECUTION, "
    "NO TRADING, NO AUTO-PUSH, NO SCHEDULER, NOT A PROFITABILITY "
    "CLAIM)")
DRAFTER_MODE = "RESEARCH_ONLY"
VERDICT_DRAFTER_READY = (
    "OVERNIGHT_AUTOPILOT_NEXT_CANDIDATE_PROPOSAL_DRAFTER_READY")
VERDICT_DRAFTER_BLOCKED = (
    "OVERNIGHT_AUTOPILOT_NEXT_CANDIDATE_PROPOSAL_DRAFTER_BLOCKED")
NEXT_REQUIRED_ACTION = (
    "HUMAN_DECISION_DRAFT_CANDIDATE_10_FAMILY_PROPOSAL_USING_V5"
    "_BLACKLIST")

# Locked numerics inherited from the pushed chain ---------------------
LOCKED_FEE_ROUND_TRIP_BPS = 27
LOCKED_GROSS_TARGET_DISTANCE_FLOOR_BPS = 81

# Banned tokens for any next_human_gate string the drafter or the
# downstream morning report may produce. (Mirrors V2.)
BANNED_TOKENS_IN_NEXT_HUMAN_GATE = (
    "PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE", "EXECUTION",
    "BACKTEST", "BASELINE", "PAPER", "LIVE", "BROKER", "EXCHANGE",
    "AUTOMATION", "ORDER", "TRACK")

PLACEHOLDER_HUMAN_FILL = "TO_BE_FILLED_BY_HUMAN_REVIEW"

# V5 lists every field a complete C10 proposal must contain. A few of
# those are LOCKED to fixed values (fees/floor) or are mandatory
# True-flags rather than free-text the human composes; those live in
# pre_filled_locked_constraints, not in the human-fill placeholders.
_LOCKED_OR_PREFILLED_C10_FIELDS = (
    "fee_assumption_round_trip_bps",
    "minimum_gross_target_distance_floor_bps",
    "human_review_required_at_every_gate",
    "no_promotion_no_paper_no_live",
)
_C10_HUMAN_FILL_FIELDS = tuple(
    f for f in V5_C10_REQS["required_fields"]
    if f not in _LOCKED_OR_PREFILLED_C10_FIELDS)

# ---------------------------------------------------------------------
# C10 PROPOSAL DRAFT TEMPLATE -- non-committed skeleton; the human
# will fill in the body and convert this into a real C10 proposal
# contract under the standard STOP-BEFORE-COMMIT protocol.
# ---------------------------------------------------------------------
C10_PROPOSAL_DRAFT_TEMPLATE = {
    "draft_kind": (
        "c10_family_proposal_draft_template_human_to_fill"),
    "is_a_committed_proposal": False,
    "is_a_promotion": False,
    "is_a_winner_claim": False,
    "fields_for_human_to_fill": _C10_HUMAN_FILL_FIELDS,
    "field_placeholders": {
        "proposed_family_label":
            PLACEHOLDER_HUMAN_FILL
            + "_MUST_NOT_APPEAR_IN_V5_BLACKLIST",
        "hypothesis_statement":
            PLACEHOLDER_HUMAN_FILL
            + "_MUST_DIFFER_MATERIALLY_FROM_C1_THROUGH_C9",
        "edge_source_hypothesis":
            PLACEHOLDER_HUMAN_FILL,
        "explicit_edge_argument_beyond_pattern_geometry":
            PLACEHOLDER_HUMAN_FILL
            + "_REQUIRED_WHY_THE_ENTRY_SURVIVES_FEES_AND_FLOOR",
        "joint_or_intersection_trigger_sample_size_pre_justification":
            PLACEHOLDER_HUMAN_FILL
            + "_REQUIRED_IF_TRIGGER_USES_INTERSECTING_CONDITIONS",
        "universe_proposal": PLACEHOLDER_HUMAN_FILL,
        "timeframe_proposal": PLACEHOLDER_HUMAN_FILL,
        "direction_proposal": PLACEHOLDER_HUMAN_FILL,
        "sample_window_proposal": PLACEHOLDER_HUMAN_FILL,
        "differentiation_from_each_rejected_family":
            PLACEHOLDER_HUMAN_FILL
            + "_MUST_ADDRESS_ALL_NINE_C1_THROUGH_C9_FAMILIES",
        "explicit_non_reuse_of_rejected_family_logic":
            PLACEHOLDER_HUMAN_FILL,
        "anti_cluster_protection_at_proposal_time":
            PLACEHOLDER_HUMAN_FILL
            + "_REQUIRED_C6_LESSON_PROPOSAL_LEVEL_LOCK",
        "sample_size_adequacy_assessment_at_proposal_time":
            PLACEHOLDER_HUMAN_FILL
            + "_REQUIRED_C7_LESSON_PROPOSAL_LEVEL_LOCK",
        "rationale_paragraph": PLACEHOLDER_HUMAN_FILL,
    },
    "pre_filled_locked_constraints": {
        "rejected_family_logic_blacklist": tuple(V5_BLACKLIST),
        "fee_assumption_round_trip_bps": LOCKED_FEE_ROUND_TRIP_BPS,
        "minimum_gross_target_distance_floor_bps":
            LOCKED_GROSS_TARGET_DISTANCE_FLOOR_BPS,
        "inherited_lessons": tuple(V5_INHERITED_LESSONS),
        "per_family_rejection_reason": dict(V5_PER_FAMILY_REASON),
        "anti_cluster_protection_required_at_proposal_time": True,
        "sample_size_adequacy_required_at_proposal_time": True,
        "explicit_edge_argument_beyond_pattern_geometry_required":
            True,
        "joint_or_intersection_trigger_sample_size_pre_justification"
        "_required_if_applicable": True,
        "human_review_required_at_every_gate": True,
        "no_promotion_no_paper_no_live": True,
    },
    "validator_invariants": (
        "draft.proposed_family_label MUST NOT appear in the V5"
        " blacklist (low_volume_downside_capitulation_mean"
        "_reversion, liquidity_sweep_mean_reversion,"
        " volatility_compression_expansion, multi_symbol"
        "_relative_strength_rotation_filter, eth_sol_relative"
        "_strength_pullback_continuation_v1, sol_btc_long_1h"
        "_swing_structure, btc_sol_long_trend_continuation_v1,"
        " crypto_intraday_breakout_pullback_structure_v2,"
        " ny_session_fvg_choch_v3)",
        "draft.fee_assumption_round_trip_bps MUST equal 27",
        "draft.minimum_gross_target_distance_floor_bps MUST equal"
        " 81",
        "draft.human_review_required_at_every_gate MUST be True",
        "draft.no_promotion_no_paper_no_live MUST be True",
        "draft.differentiation_from_each_rejected_family MUST"
        " explicitly address all 9 rejected families by name",
        "draft.explicit_edge_argument_beyond_pattern_geometry MUST"
        " be non-empty and not equal the placeholder string",
        "draft.anti_cluster_protection_at_proposal_time MUST be"
        " non-empty and not equal the placeholder string",
        "draft.sample_size_adequacy_assessment_at_proposal_time"
        " MUST be non-empty and not equal the placeholder string",
        "if draft uses a joint or intersection trigger, draft"
        ".joint_or_intersection_trigger_sample_size_pre"
        "_justification MUST be non-empty and not equal the"
        " placeholder string",
        "every required field MUST be filled (no remaining"
        " placeholder strings)",
    ),
}

# ---------------------------------------------------------------------
# MORNING AUTOPILOT REPORT TEMPLATE -- non-committed skeleton; the
# system may populate at most the structural pre-filled fields. Date,
# HEAD, active-candidate, blockers, and honest-verdict fields stay as
# PLACEHOLDER_HUMAN_FILL until a separate explicit human gate.
# ---------------------------------------------------------------------
MORNING_AUTOPILOT_REPORT_TEMPLATE = {
    "report_kind":
        "overnight_autopilot_morning_report_template_v1",
    "is_a_committed_report": False,
    "is_a_promotion": False,
    "is_a_winner_claim": False,
    "fields_for_population": (
        "report_date_utc",
        "head_at_report",
        "ledger_status_nine_records",
        "v5_blacklist_length",
        "v5_blacklist_families",
        "current_open_gate",
        "active_candidate_under_review",
        "blockers",
        "honest_verdict",
        "next_human_gate",
        "no_profitability_claim_lock",
        "no_paper_approval_lock",
        "no_live_approval_lock",
        "no_winner_wording_lock",
        "no_execution_lock",
        "no_auto_commit_lock",
        "no_auto_push_lock",
    ),
    "pre_filled_structural_fields": {
        "ledger_status_nine_records":
            tuple(["REJECTED_KEPT_ON_RECORD"] * 9),
        "v5_blacklist_length": 9,
        "v5_blacklist_families": tuple(V5_BLACKLIST),
        "current_open_gate": NEXT_REQUIRED_ACTION,
        "next_human_gate": NEXT_REQUIRED_ACTION,
        "no_profitability_claim_lock": True,
        "no_paper_approval_lock": True,
        "no_live_approval_lock": True,
        "no_winner_wording_lock": True,
        "no_execution_lock": True,
        "no_auto_commit_lock": True,
        "no_auto_push_lock": True,
    },
    "field_placeholders_human_to_fill": {
        "report_date_utc": PLACEHOLDER_HUMAN_FILL,
        "head_at_report": PLACEHOLDER_HUMAN_FILL,
        "active_candidate_under_review": PLACEHOLDER_HUMAN_FILL,
        "blockers": PLACEHOLDER_HUMAN_FILL,
        "honest_verdict":
            PLACEHOLDER_HUMAN_FILL
            + "_EVIDENCE_LANGUAGE_ONLY_NO_WINNER_WORDING",
    },
    "banned_tokens_in_next_human_gate":
        BANNED_TOKENS_IN_NEXT_HUMAN_GATE,
    "report_is_research_only": True,
    "report_authorizes_nothing": True,
    "report_is_not_a_profitability_claim": True,
}

# ---------------------------------------------------------------------
# Hard locks: what the drafter cannot do under any circumstance.
# ---------------------------------------------------------------------
HARD_LOCKS = (
    "no_c10_proposal_committed_in_this_gate",
    "no_c10_proposal_drafting_beyond_placeholder_template",
    "no_real_candle_detection",
    "no_dry_run_detection",
    "no_replay",
    "no_relabel",
    "no_pnl_computation",
    "no_data_fetch",
    "no_api_call",
    "no_network_call",
    "no_credentials_use",
    "no_wallet_use",
    "no_account_use",
    "no_paper_trading",
    "no_micro_live",
    "no_live_trading",
    "no_broker_interaction",
    "no_exchange_interaction",
    "no_order_logic",
    "no_portfolio_logic",
    "no_scheduler_start",
    "no_notifications",
    "no_runner_generation",
    "no_data_artifact_generation",
    "no_detection_file_generation",
    "no_replay_file_generation",
    "no_trading_file_generation",
    "no_staging",
    "no_commit",
    "no_push",
    "no_auto_promotion",
    "no_human_review_bypass",
    "no_winner_wording",
    "no_profitability_claim",
)


def get_drafter_label() -> str:
    return DRAFTER_LABEL


def build_overnight_autopilot_next_candidate_proposal_drafter(
        ) -> dict[str, Any]:
    """Assemble the drafter contract. Pure (no arguments). BLOCKED
    if the nine-record ledger does not hold, the V5 blacklist is
    not certifying, V4 is not certifying, V3 is not certifying, the
    Overnight Autopilot V2 is not certifying, the Recommendation V1
    is not certifying, or the Autopilot Loop V1 is not certifying."""
    record: dict[str, Any] = {
        "schema_version": DRAFTER_SCHEMA_VERSION,
        "label": DRAFTER_LABEL, "mode": DRAFTER_MODE,
        "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [],
        "ledger_keys": list(V5_LEDGER_KEYS),
        "ledger_family_labels": dict(V5_LEDGER_FAMILY_LABELS),
        "required_ledger_status": "REJECTED_KEPT_ON_RECORD",
        "ledger_status_nine_records": None,
        "ledger_all_rejected_kept_on_record": None,
        "v5_blacklist": list(V5_BLACKLIST),
        "v5_blacklist_length": len(V5_BLACKLIST),
        "inherited_lessons_from_v5": list(V5_INHERITED_LESSONS),
        "per_family_rejection_reason_from_v5":
            dict(V5_PER_FAMILY_REASON),
        "locked_fee_round_trip_bps": LOCKED_FEE_ROUND_TRIP_BPS,
        "locked_gross_target_distance_floor_bps":
            LOCKED_GROSS_TARGET_DISTANCE_FLOOR_BPS,
        "banned_tokens_in_next_human_gate":
            list(BANNED_TOKENS_IN_NEXT_HUMAN_GATE),
        "c10_proposal_draft_template": {
            "draft_kind":
                C10_PROPOSAL_DRAFT_TEMPLATE["draft_kind"],
            "is_a_committed_proposal":
                C10_PROPOSAL_DRAFT_TEMPLATE["is_a_committed_proposal"],
            "is_a_promotion":
                C10_PROPOSAL_DRAFT_TEMPLATE["is_a_promotion"],
            "is_a_winner_claim":
                C10_PROPOSAL_DRAFT_TEMPLATE["is_a_winner_claim"],
            "fields_for_human_to_fill":
                list(C10_PROPOSAL_DRAFT_TEMPLATE[
                    "fields_for_human_to_fill"]),
            "field_placeholders":
                dict(C10_PROPOSAL_DRAFT_TEMPLATE["field_placeholders"]),
            "pre_filled_locked_constraints": {
                "rejected_family_logic_blacklist": list(V5_BLACKLIST),
                "fee_assumption_round_trip_bps":
                    LOCKED_FEE_ROUND_TRIP_BPS,
                "minimum_gross_target_distance_floor_bps":
                    LOCKED_GROSS_TARGET_DISTANCE_FLOOR_BPS,
                "inherited_lessons": list(V5_INHERITED_LESSONS),
                "per_family_rejection_reason":
                    dict(V5_PER_FAMILY_REASON),
                "anti_cluster_protection_required_at_proposal_time":
                    True,
                "sample_size_adequacy_required_at_proposal_time":
                    True,
                "explicit_edge_argument_beyond_pattern_geometry"
                "_required": True,
                "joint_or_intersection_trigger_sample_size_pre"
                "_justification_required_if_applicable": True,
                "human_review_required_at_every_gate": True,
                "no_promotion_no_paper_no_live": True},
            "validator_invariants":
                list(C10_PROPOSAL_DRAFT_TEMPLATE[
                    "validator_invariants"])},
        "morning_autopilot_report_template": {
            "report_kind":
                MORNING_AUTOPILOT_REPORT_TEMPLATE["report_kind"],
            "is_a_committed_report":
                MORNING_AUTOPILOT_REPORT_TEMPLATE[
                    "is_a_committed_report"],
            "is_a_promotion":
                MORNING_AUTOPILOT_REPORT_TEMPLATE["is_a_promotion"],
            "is_a_winner_claim":
                MORNING_AUTOPILOT_REPORT_TEMPLATE[
                    "is_a_winner_claim"],
            "fields_for_population":
                list(MORNING_AUTOPILOT_REPORT_TEMPLATE[
                    "fields_for_population"]),
            "pre_filled_structural_fields":
                {k: (list(v) if isinstance(v, tuple) else v)
                 for k, v in MORNING_AUTOPILOT_REPORT_TEMPLATE[
                     "pre_filled_structural_fields"].items()},
            "field_placeholders_human_to_fill":
                dict(MORNING_AUTOPILOT_REPORT_TEMPLATE[
                    "field_placeholders_human_to_fill"]),
            "banned_tokens_in_next_human_gate":
                list(MORNING_AUTOPILOT_REPORT_TEMPLATE[
                    "banned_tokens_in_next_human_gate"]),
            "report_is_research_only": True,
            "report_authorizes_nothing": True,
            "report_is_not_a_profitability_claim": True},
        "hard_locks": list(HARD_LOCKS),
        "human_review_required": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True, "live_gate_locked": True,
        # negative capability surface
        "executes": False, "writes_files": False,
        "runs_detector": False,
        "runs_real_candle_detection": False,
        "runs_dry_run_detection": False,
        "runs_relabel": False, "runs_replay": False,
        "labels_now": False,
        "runs_real_detection_now": False, "runs_replay_now": False,
        "scores_now": False, "stages_data_now": False,
        "fetches_data": False, "calls_api": False,
        "uses_network": False, "uses_credentials": False,
        "uses_wallet": False, "uses_account": False,
        "connects_broker": False, "connects_exchange": False,
        "uses_real_money": False,
        "contains_order_logic": False,
        "contains_portfolio_allocation_logic": False,
        "starts_scheduler": False, "sends_notifications": False,
        "auto_commits": False, "auto_pushes": False,
        "creates_runners_now": False,
        "creates_data_artifacts_now": False,
        "creates_detector_implementation_now": False,
        "modifies_staged_market_data": False,
        "drafts_c10_proposal_contract_now": False,
        "commits_c10_proposal_now": False,
        "approves_c10_proposal_now": False,
        "generates_morning_report_now": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False,
        "authorizes_live_trading": False,
        "promotes_gate": False, "unlocks_downstream_gate": False,
        "claims_profitability": False,
        "bypasses_human_review": False,
        "uses_external_data_source": False,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    statuses = (C1_STATUS, C2_STATUS, C3_STATUS, C4_STATUS, C5_STATUS,
                C6_STATUS, C7_STATUS, C8_STATUS, C9_STATUS)
    record["ledger_status_nine_records"] = list(statuses)
    record["ledger_all_rejected_kept_on_record"] = all(
        s == "REJECTED_KEPT_ON_RECORD" for s in statuses)
    if not record["ledger_all_rejected_kept_on_record"]:
        record["verdict"] = VERDICT_DRAFTER_BLOCKED
        record["blockers"].append("nine_record_ledger_broken")
        return record
    if build_rejected_family_blacklist_v5()["verdict"] != (
            VERDICT_BL5_READY):
        record["verdict"] = VERDICT_DRAFTER_BLOCKED
        record["blockers"].append("v5_blacklist_not_certifying")
        return record
    if build_rejected_family_blacklist_v4()["verdict"] != (
            VERDICT_BL4_READY):
        record["verdict"] = VERDICT_DRAFTER_BLOCKED
        record["blockers"].append("v4_blacklist_not_certifying")
        return record
    if build_rejected_family_blacklist_v3()["verdict"] != (
            VERDICT_BL3_READY):
        record["verdict"] = VERDICT_DRAFTER_BLOCKED
        record["blockers"].append("v3_blacklist_not_certifying")
        return record
    if build_overnight_research_autopilot_v2_contract()["verdict"] != (
            VERDICT_OAP2_READY):
        record["verdict"] = VERDICT_DRAFTER_BLOCKED
        record["blockers"].append(
            "overnight_research_autopilot_v2_not_certifying")
        return record
    if _rec.build_candidate_recommendation()["verdict"] != (
            _rec.VERDICT_CR_READY):
        record["verdict"] = VERDICT_DRAFTER_BLOCKED
        record["blockers"].append("recommendation_v1_not_certifying")
        return record
    if _loop.build_autopilot_loop_contract()["verdict"] != (
            _loop.VERDICT_AP_READY):
        record["verdict"] = VERDICT_DRAFTER_BLOCKED
        record["blockers"].append("autopilot_loop_v1_not_certifying")
        return record
    record["verdict"] = VERDICT_DRAFTER_READY
    return record


def validate_overnight_autopilot_next_candidate_proposal_drafter(
        record: Any) -> dict[str, Any]:
    """Validate the drafter record itself. Never raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_DRAFTER_READY,
                                VERDICT_DRAFTER_BLOCKED):
        errors.append("bad_verdict")
    if list(r.get("ledger_keys") or ()) != list(V5_LEDGER_KEYS):
        errors.append("ledger_keys_tampered")
    if r.get("ledger_family_labels") != V5_LEDGER_FAMILY_LABELS:
        errors.append("ledger_family_labels_tampered")
    if r.get("required_ledger_status") != "REJECTED_KEPT_ON_RECORD":
        errors.append("required_ledger_status_tampered")
    if tuple(r.get("v5_blacklist") or ()) != V5_BLACKLIST:
        errors.append("v5_blacklist_tampered")
    if r.get("v5_blacklist_length") != 9:
        errors.append("v5_blacklist_length_must_be_9")
    if tuple(r.get("inherited_lessons_from_v5") or ()) != (
            V5_INHERITED_LESSONS):
        errors.append("inherited_lessons_tampered")
    if r.get("per_family_rejection_reason_from_v5") != (
            V5_PER_FAMILY_REASON):
        errors.append("per_family_rejection_reason_tampered")
    if r.get("locked_fee_round_trip_bps") != (
            LOCKED_FEE_ROUND_TRIP_BPS):
        errors.append("locked_fee_tampered")
    if r.get("locked_gross_target_distance_floor_bps") != (
            LOCKED_GROSS_TARGET_DISTANCE_FLOOR_BPS):
        errors.append("locked_floor_tampered")
    if tuple(r.get("banned_tokens_in_next_human_gate") or ()) != (
            BANNED_TOKENS_IN_NEXT_HUMAN_GATE):
        errors.append("banned_tokens_tampered")
    if tuple(r.get("hard_locks") or ()) != HARD_LOCKS:
        errors.append("hard_locks_tampered")
    # c10 draft template
    dt = r.get("c10_proposal_draft_template") or {}
    if dt.get("draft_kind") != C10_PROPOSAL_DRAFT_TEMPLATE[
            "draft_kind"]:
        errors.append("c10_draft_kind_tampered")
    if dt.get("is_a_committed_proposal") is not False:
        errors.append("c10_draft_committed_flag_wrong")
    if dt.get("is_a_promotion") is not False:
        errors.append("c10_draft_promotion_flag_wrong")
    if dt.get("is_a_winner_claim") is not False:
        errors.append("c10_draft_winner_flag_wrong")
    if tuple(dt.get("fields_for_human_to_fill") or ()) != (
            _C10_HUMAN_FILL_FIELDS):
        errors.append("c10_draft_fields_tampered")
    if dt.get("field_placeholders") != (
            C10_PROPOSAL_DRAFT_TEMPLATE["field_placeholders"]):
        errors.append("c10_draft_placeholders_tampered")
    pl = dt.get("pre_filled_locked_constraints") or {}
    if tuple(pl.get("rejected_family_logic_blacklist") or ()) != (
            V5_BLACKLIST):
        errors.append("c10_pre_filled_blacklist_tampered")
    if pl.get("fee_assumption_round_trip_bps") != (
            LOCKED_FEE_ROUND_TRIP_BPS):
        errors.append("c10_pre_filled_fee_tampered")
    if pl.get("minimum_gross_target_distance_floor_bps") != (
            LOCKED_GROSS_TARGET_DISTANCE_FLOOR_BPS):
        errors.append("c10_pre_filled_floor_tampered")
    for key in ("anti_cluster_protection_required_at_proposal_time",
                "sample_size_adequacy_required_at_proposal_time",
                "explicit_edge_argument_beyond_pattern_geometry"
                "_required",
                "joint_or_intersection_trigger_sample_size_pre"
                "_justification_required_if_applicable",
                "human_review_required_at_every_gate",
                "no_promotion_no_paper_no_live"):
        if pl.get(key) is not True:
            errors.append("c10_pre_filled_flag_wrong:" + key)
    if tuple(dt.get("validator_invariants") or ()) != (
            C10_PROPOSAL_DRAFT_TEMPLATE["validator_invariants"]):
        errors.append("c10_validator_invariants_tampered")
    # morning report template
    mr = r.get("morning_autopilot_report_template") or {}
    if mr.get("report_kind") != MORNING_AUTOPILOT_REPORT_TEMPLATE[
            "report_kind"]:
        errors.append("morning_report_kind_tampered")
    if mr.get("is_a_committed_report") is not False:
        errors.append("morning_report_committed_flag_wrong")
    if tuple(mr.get("fields_for_population") or ()) != (
            MORNING_AUTOPILOT_REPORT_TEMPLATE["fields_for_population"]):
        errors.append("morning_report_fields_tampered")
    pfs = mr.get("pre_filled_structural_fields") or {}
    if list(pfs.get("ledger_status_nine_records") or ()) != [
            "REJECTED_KEPT_ON_RECORD"] * 9:
        errors.append("morning_report_ledger_status_tampered")
    if pfs.get("v5_blacklist_length") != 9:
        errors.append("morning_report_blacklist_length_tampered")
    if list(pfs.get("v5_blacklist_families") or ()) != list(
            V5_BLACKLIST):
        errors.append("morning_report_blacklist_families_tampered")
    if pfs.get("current_open_gate") != NEXT_REQUIRED_ACTION:
        errors.append("morning_report_open_gate_tampered")
    if pfs.get("next_human_gate") != NEXT_REQUIRED_ACTION:
        errors.append("morning_report_next_gate_tampered")
    for lock_key in ("no_profitability_claim_lock",
                     "no_paper_approval_lock",
                     "no_live_approval_lock",
                     "no_winner_wording_lock",
                     "no_execution_lock", "no_auto_commit_lock",
                     "no_auto_push_lock"):
        if pfs.get(lock_key) is not True:
            errors.append("morning_report_lock_wrong:" + lock_key)
    if mr.get("report_is_research_only") is not True:
        errors.append("morning_report_research_only_flag_wrong")
    if mr.get("report_authorizes_nothing") is not True:
        errors.append("morning_report_authorizes_nothing_flag_wrong")
    if mr.get("report_is_not_a_profitability_claim") is not True:
        errors.append("morning_report_no_profit_flag_wrong")
    # constitution + capabilities
    for key, want in (("human_review_required", True),
                      ("paper_trading_gate_locked", True),
                      ("micro_live_gate_locked", True),
                      ("live_gate_locked", True)):
        if r.get(key) is not want:
            errors.append("constitution_flag_wrong:" + key)
    for key in ("executes", "writes_files",
                "runs_detector", "runs_real_candle_detection",
                "runs_dry_run_detection", "runs_relabel",
                "runs_replay", "labels_now",
                "runs_real_detection_now", "runs_replay_now",
                "scores_now", "stages_data_now", "fetches_data",
                "calls_api", "uses_network", "uses_credentials",
                "uses_wallet", "uses_account", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic",
                "contains_portfolio_allocation_logic",
                "starts_scheduler", "sends_notifications",
                "auto_commits", "auto_pushes",
                "creates_runners_now",
                "creates_data_artifacts_now",
                "creates_detector_implementation_now",
                "modifies_staged_market_data",
                "drafts_c10_proposal_contract_now",
                "commits_c10_proposal_now",
                "approves_c10_proposal_now",
                "generates_morning_report_now",
                "authorizes_paper_execution",
                "authorizes_micro_live",
                "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate",
                "claims_profitability", "bypasses_human_review",
                "uses_external_data_source"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    if r.get("next_required_action") != NEXT_REQUIRED_ACTION:
        errors.append("next_required_action_tampered")
    if r.get("verdict") == VERDICT_DRAFTER_READY and r.get("blockers"):
        errors.append("ready_with_blockers")
    return {"valid": not errors, "errors": errors}


def validate_c10_proposal_draft(draft: Any) -> dict[str, Any]:
    """Pure, never-raises static validator for a human-filled C10
    draft. Reports whether the draft satisfies the locked
    constraints. Does NOT mutate, store, commit, promote, or
    transmit the draft anywhere."""
    errors: list[str] = []
    if not isinstance(draft, dict):
        return {"valid": False, "errors": ["draft_not_a_dict"]}
    label = draft.get("proposed_family_label")
    if not isinstance(label, str) or not label.strip():
        errors.append("proposed_family_label_empty")
    elif label in V5_BLACKLIST:
        errors.append("proposed_family_label_in_v5_blacklist")
    elif PLACEHOLDER_HUMAN_FILL in label:
        errors.append("proposed_family_label_still_placeholder")
    if draft.get("fee_assumption_round_trip_bps") != (
            LOCKED_FEE_ROUND_TRIP_BPS):
        errors.append("fee_assumption_must_equal_27_bps")
    if draft.get("minimum_gross_target_distance_floor_bps") != (
            LOCKED_GROSS_TARGET_DISTANCE_FLOOR_BPS):
        errors.append("floor_must_equal_81_bps")
    if draft.get("human_review_required_at_every_gate") is not True:
        errors.append("human_review_required_must_be_true")
    if draft.get("no_promotion_no_paper_no_live") is not True:
        errors.append("no_promotion_no_paper_no_live_must_be_true")
    # required fields all filled (no remaining placeholder strings)
    for field in V5_C10_REQS["required_fields"]:
        value = draft.get(field)
        if value is None:
            errors.append("required_field_missing:" + field)
            continue
        if isinstance(value, str) and (
                not value.strip()
                or PLACEHOLDER_HUMAN_FILL in value):
            errors.append("required_field_still_placeholder:" + field)
    # differentiation must address all 9 rejected families by name
    diff = draft.get("differentiation_from_each_rejected_family")
    if isinstance(diff, str):
        missing = [family for family in V5_BLACKLIST
                   if family not in diff]
        if missing:
            errors.append(
                "differentiation_missing_families:"
                + ",".join(missing))
    elif isinstance(diff, dict):
        missing = [family for family in V5_BLACKLIST
                   if family not in diff]
        if missing:
            errors.append(
                "differentiation_missing_families:"
                + ",".join(missing))
    elif diff is None:
        errors.append("differentiation_missing")
    # banned tokens check on any next_human_gate the draft proposes
    nhg = draft.get("next_human_gate")
    if isinstance(nhg, str):
        upper = nhg.upper()
        for banned in BANNED_TOKENS_IN_NEXT_HUMAN_GATE:
            if banned in upper:
                errors.append("next_human_gate_has_banned_token:"
                              + banned)
    return {"valid": not errors, "errors": errors}
