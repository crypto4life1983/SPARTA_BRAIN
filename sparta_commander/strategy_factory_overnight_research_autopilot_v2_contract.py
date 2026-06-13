"""SPARTA STRATEGY FACTORY OVERNIGHT RESEARCH AUTOPILOT V2 (READ-ONLY,
RESEARCH ONLY, NO EXECUTION, NO TRADING, NO AUTO-PUSH, NO SCHEDULER).

The next automation layer ON TOP OF the pushed five-stage research
loop V1 contract and the pushed Recommendation V1 contract. V2 freezes
ONLY the SHAPE of two new research-only artifacts and the ledger
gating that produces them:

  1) a MORNING REPORT schema (what the system shows the human when
     they wake up: what happened overnight, what gate is open now,
     what the locks still hold);
  2) a NEXT-CANDIDATE RECOMMENDATION-PLAN schema (the shape of a
     proposed next family hypothesis -- never an automatic promotion,
     never reused logic from C1-C6, never bypassing human gates).

V2 does NOT generate either artifact on import. V2 does NOT run the
detector, the replay, the relabel, the aggregator, or the fetcher. V2
does NOT auto-commit or auto-push anything. V2 does NOT activate a
scheduler, send notifications, or touch credentials/wallets/accounts/
broker/exchange/order/api. V2 cannot authorize paper or live trading.
V2 cannot claim profitability. V2 cannot promote any gate or unlock
any downstream gate. Generation of a morning report or the drafting
of a next-candidate proposal happens at a later separate human gate.

Chain-gated live on:
  - the pushed six-record rejection ledger (C1, C2, C3, C4, C5, C6 all
    REJECTED_KEPT_ON_RECORD),
  - the pushed Recommendation V1,
  - the pushed Autopilot Loop V1.

If ANY of those break, V2 returns BLOCKED with explicit blockers.
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
from sparta_commander.multi_symbol_relative_strength_rotation_filter_family_proposal_contract import (
    CANDIDATE_FAMILY as C6_CANDIDATE_FAMILY,
    CANDIDATE_ID as C6_CANDIDATE_ID,
)
from sparta_commander.multi_symbol_relative_strength_rotation_filter_rejection_record_contract import (
    REJECTION_REASON as C6_REJECTION_REASON,
    REJECTION_STATUS as C6_STATUS,
)
from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
    REJECTION_STATUS as C1_STATUS,
)
from sparta_commander.sol_btc_long_1h_swing_structure_rejection_record_contract import (
    REJECTION_STATUS as C4_STATUS,
)

OAP2_SCHEMA_VERSION = (
    "strategy_factory_overnight_research_autopilot_v2.v1")
OAP2_LABEL = ("SPARTA Strategy Factory Overnight Research Autopilot V2 "
              "(READ-ONLY, RESEARCH ONLY, NO EXECUTION, NO TRADING, "
              "NO AUTO-PUSH, NO SCHEDULER, NOT A PROFITABILITY CLAIM)")
OAP2_MODE = "RESEARCH_ONLY"
VERDICT_OAP2_READY = (
    "STRATEGY_FACTORY_OVERNIGHT_RESEARCH_AUTOPILOT_V2_READY")
VERDICT_OAP2_BLOCKED = (
    "STRATEGY_FACTORY_OVERNIGHT_RESEARCH_AUTOPILOT_V2_BLOCKED")
NEXT_REQUIRED_ACTION = (
    "HUMAN_DECISION_GENERATE_MORNING_REPORT_OR_PROPOSE_NEXT_CANDIDATE"
    "_FAMILY")

# ----------------------------------------------------------------------------
# the six-record rejection ledger as input (declarative)
# ----------------------------------------------------------------------------
LEDGER_KEYS = ("C1", "C2", "C3", "C4", "C5", "C6")
LEDGER_FAMILY_LABELS = {
    "C1": "ny_session_fvg_choch_v3",
    "C2": "crypto_intraday_breakout_pullback_structure_v2",
    "C3": "btc_sol_long_trend_continuation_v1",
    "C4": "sol_btc_long_1h_swing_structure",
    "C5": "eth_sol_relative_strength_pullback_continuation_v1",
    "C6": "multi_symbol_relative_strength_rotation_filter",
}
REQUIRED_LEDGER_STATUS = "REJECTED_KEPT_ON_RECORD"

# Lessons extracted (frozen text, evidence-language only) ---------------------
# These are summaries -- not rescue paths. Reuse of any rejected family logic
# is permanently blacklisted; see REJECTED_FAMILY_LOGIC_BLACKLIST below.
LESSONS_FROM_REJECTED_FAMILIES = {
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
           "is not the bottleneck -- the structures simply did not "
           "resume"),
    "C6": ("multi-symbol relative strength rotation filter v1: "
           "original replay net-negative and gross-negative at every "
           "variant; the single authorized 24-bar label-time clustering "
           "filter edit reduced overlap from 334 to 37 skips as "
           "designed but did not rescue edge -- post-edit replay was "
           "also net-negative at every variant; cross-sectional rank-1 "
           "alone is not edge on this universe and timeframe in this "
           "sample window"),
}

# explicit, validator-permanent blacklist of any rejected family logic
REJECTED_FAMILY_LOGIC_BLACKLIST = (
    "ny_session_fvg_choch_v3",
    "crypto_intraday_breakout_pullback_structure_v2",
    "btc_sol_long_trend_continuation_v1",
    "sol_btc_long_1h_swing_structure",
    "eth_sol_relative_strength_pullback_continuation_v1",
    "multi_symbol_relative_strength_rotation_filter",
)

# ----------------------------------------------------------------------------
# morning report schema (what V2 will eventually populate -- not now)
# ----------------------------------------------------------------------------
MORNING_REPORT_SCHEMA = {
    "report_kind":
        "overnight_research_autopilot_v2_morning_report",
    "required_fields": (
        "report_date_utc",
        "head_at_report",
        "previous_night_status",
        "candidate_under_review",
        "completed_gate",
        "blockers",
        "honest_verdict",
        "next_human_gate",
        "ledger_status_six_records",
        "no_profitability_claim_lock",
        "no_paper_approval_lock",
        "no_live_approval_lock",
        "no_winner_wording_lock",
        "no_execution_lock",
        "no_auto_commit_lock",
        "no_auto_push_lock",
    ),
    "field_kinds": {
        "report_date_utc": "iso_date_string_utc",
        "head_at_report": "git_sha_40_hex",
        "previous_night_status": (
            "string_enum:idle_no_active_candidate"
            "_or_under_review_or_blocked"),
        "candidate_under_review":
            "candidate_id_or_null",
        "completed_gate": "loop_stage_label_or_null",
        "blockers": "tuple_of_strings",
        "honest_verdict":
            "string_evidence_language_only_no_winner_wording",
        "next_human_gate":
            "human_command_label_no_banned_tokens",
        "ledger_status_six_records":
            "tuple_of_six_string_statuses_all_must_equal_"
            "rejected_kept_on_record",
        "no_profitability_claim_lock": "must_be_true",
        "no_paper_approval_lock": "must_be_true",
        "no_live_approval_lock": "must_be_true",
        "no_winner_wording_lock": "must_be_true",
        "no_execution_lock": "must_be_true",
        "no_auto_commit_lock": "must_be_true",
        "no_auto_push_lock": "must_be_true",
    },
    "must_include_locks": (
        "no_profitability_claim_lock",
        "no_paper_approval_lock",
        "no_live_approval_lock",
        "no_winner_wording_lock",
        "no_execution_lock",
        "no_auto_commit_lock",
        "no_auto_push_lock",
    ),
    "report_is_research_only": True,
    "report_authorizes_nothing": True,
    "report_is_not_a_profitability_claim": True,
    "banned_tokens_in_next_human_gate": (
        "PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
        "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
        "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"),
}

# ----------------------------------------------------------------------------
# next-candidate recommendation-plan schema (the shape of a proposed
# candidate #7 hypothesis -- never an automatic promotion)
# ----------------------------------------------------------------------------
NEXT_CANDIDATE_RECOMMENDATION_PLAN_SCHEMA = {
    "plan_kind":
        "overnight_research_autopilot_v2_next_candidate_plan",
    "required_fields": (
        "proposed_family_label",
        "hypothesis_statement",
        "edge_source_hypothesis",
        "universe_proposal",
        "timeframe_proposal",
        "direction_proposal",
        "fee_assumption_round_trip_bps",
        "minimum_gross_target_distance_floor_bps",
        "sample_window_proposal",
        "differentiation_from_each_rejected_family",
        "explicit_non_reuse_of_rejected_family_logic",
        "rationale_paragraph",
        "human_review_required_at_every_gate",
        "no_promotion_no_paper_no_live",
    ),
    "differentiation_must_address_each_of": tuple(
        LEDGER_FAMILY_LABELS[key] for key in LEDGER_KEYS),
    "rejected_family_logic_blacklist": (
        REJECTED_FAMILY_LOGIC_BLACKLIST),
    "fee_assumption_must_equal_27_bps_round_trip": True,
    "minimum_floor_must_equal_81_bps": True,
    "plan_is_research_only": True,
    "plan_authorizes_nothing": True,
    "plan_is_not_a_promotion": True,
    "plan_cannot_reuse_any_rejected_family_logic": True,
    "human_review_required_at_every_gate": True,
}

CLAIM_LOCKS = (
    "no_profitability_claim",
    "no_paper_approval",
    "no_live_approval",
    "no_execution_approval",
    "no_winner_wording",
    "no_promotion_by_v2",
    "no_unlock_by_v2",
    "no_scheduler_activation",
    "no_auto_commit",
    "no_auto_push",
    "no_morning_report_generation_now",
    "no_next_candidate_proposal_drafting_now",
)


def get_overnight_autopilot_v2_label() -> str:
    return OAP2_LABEL


def build_overnight_research_autopilot_v2_contract() -> dict[str, Any]:
    """Assemble the V2 contract. Pure (no arguments). Returns BLOCKED if
    the six-record ledger does not hold, the V1 loop is not certifying,
    or the Recommendation V1 is not certifying."""
    record: dict[str, Any] = {
        "schema_version": OAP2_SCHEMA_VERSION,
        "label": OAP2_LABEL, "mode": OAP2_MODE,
        "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [],
        "ledger_keys": list(LEDGER_KEYS),
        "ledger_family_labels": dict(LEDGER_FAMILY_LABELS),
        "required_ledger_status": REQUIRED_LEDGER_STATUS,
        "ledger_status_six_records": None,
        "ledger_all_rejected_kept_on_record": None,
        "c6_rejection_reason": C6_REJECTION_REASON,
        "lessons_from_rejected_families": {
            key: value for key, value
            in LESSONS_FROM_REJECTED_FAMILIES.items()},
        "rejected_family_logic_blacklist":
            list(REJECTED_FAMILY_LOGIC_BLACKLIST),
        "morning_report_schema": {
            "report_kind":
                MORNING_REPORT_SCHEMA["report_kind"],
            "required_fields":
                list(MORNING_REPORT_SCHEMA["required_fields"]),
            "field_kinds":
                dict(MORNING_REPORT_SCHEMA["field_kinds"]),
            "must_include_locks":
                list(MORNING_REPORT_SCHEMA["must_include_locks"]),
            "report_is_research_only":
                MORNING_REPORT_SCHEMA["report_is_research_only"],
            "report_authorizes_nothing":
                MORNING_REPORT_SCHEMA["report_authorizes_nothing"],
            "report_is_not_a_profitability_claim":
                MORNING_REPORT_SCHEMA[
                    "report_is_not_a_profitability_claim"],
            "banned_tokens_in_next_human_gate": list(
                MORNING_REPORT_SCHEMA[
                    "banned_tokens_in_next_human_gate"])},
        "next_candidate_recommendation_plan_schema": {
            "plan_kind":
                NEXT_CANDIDATE_RECOMMENDATION_PLAN_SCHEMA["plan_kind"],
            "required_fields":
                list(NEXT_CANDIDATE_RECOMMENDATION_PLAN_SCHEMA[
                    "required_fields"]),
            "differentiation_must_address_each_of":
                list(NEXT_CANDIDATE_RECOMMENDATION_PLAN_SCHEMA[
                    "differentiation_must_address_each_of"]),
            "rejected_family_logic_blacklist":
                list(NEXT_CANDIDATE_RECOMMENDATION_PLAN_SCHEMA[
                    "rejected_family_logic_blacklist"]),
            "fee_assumption_must_equal_27_bps_round_trip": True,
            "minimum_floor_must_equal_81_bps": True,
            "plan_is_research_only": True,
            "plan_authorizes_nothing": True,
            "plan_is_not_a_promotion": True,
            "plan_cannot_reuse_any_rejected_family_logic": True,
            "human_review_required_at_every_gate": True},
        "claim_locks": list(CLAIM_LOCKS),
        "human_review_required": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True, "live_gate_locked": True,
        # negative capability surface (everything that V2 CANNOT do)
        "executes": False, "writes_files": False,
        "runs_detector": False,
        "runs_real_candle_detection": False,
        "runs_relabel": False,
        "runs_replay": False,
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
        "generates_morning_report_now": False,
        "generates_next_candidate_proposal_now": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False, "authorizes_live_trading": False,
        "promotes_gate": False, "unlocks_downstream_gate": False,
        "claims_profitability": False,
        "uses_external_data_source": False,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    statuses = (C1_STATUS, C2_STATUS, C3_STATUS, C4_STATUS, C5_STATUS,
                C6_STATUS)
    record["ledger_status_six_records"] = list(statuses)
    record["ledger_all_rejected_kept_on_record"] = all(
        s == REQUIRED_LEDGER_STATUS for s in statuses)
    if not record["ledger_all_rejected_kept_on_record"]:
        record["verdict"] = VERDICT_OAP2_BLOCKED
        record["blockers"].append("six_record_ledger_broken")
        return record
    if _rec.build_candidate_recommendation()["verdict"] != (
            _rec.VERDICT_CR_READY):
        record["verdict"] = VERDICT_OAP2_BLOCKED
        record["blockers"].append("recommendation_v1_not_certifying")
        return record
    if _loop.build_autopilot_loop_contract()["verdict"] != (
            _loop.VERDICT_AP_READY):
        record["verdict"] = VERDICT_OAP2_BLOCKED
        record["blockers"].append("autopilot_loop_v1_not_certifying")
        return record
    # the C6 ledger entry must specifically have the post-edit failure
    # reason (proves V2 has the correct C6 lineage; protects against a
    # future re-imported C6 contract that flips the reason)
    if C6_REJECTION_REASON != "EDIT_SPENT_AND_STILL_NEGATIVE_EDGE_FAILURE":
        record["verdict"] = VERDICT_OAP2_BLOCKED
        record["blockers"].append("c6_rejection_reason_tampered")
        return record
    if C6_CANDIDATE_ID != "MULTI_SYMBOL_RELATIVE_STRENGTH_ROTATION_FILTER" \
            "_V1":
        record["verdict"] = VERDICT_OAP2_BLOCKED
        record["blockers"].append("c6_candidate_id_tampered")
        return record
    if C6_CANDIDATE_FAMILY not in REJECTED_FAMILY_LOGIC_BLACKLIST:
        record["verdict"] = VERDICT_OAP2_BLOCKED
        record["blockers"].append(
            "c6_family_must_be_blacklisted_from_reuse")
        return record
    record["verdict"] = VERDICT_OAP2_READY
    return record


def validate_overnight_research_autopilot_v2(
        record: Any) -> dict[str, Any]:
    """Validate shape, frozen schemas, and the no-execution surface."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_OAP2_READY, VERDICT_OAP2_BLOCKED):
        errors.append("bad_verdict")
    if list(r.get("ledger_keys") or ()) != list(LEDGER_KEYS):
        errors.append("ledger_keys_tampered")
    if r.get("ledger_family_labels") != LEDGER_FAMILY_LABELS:
        errors.append("ledger_family_labels_tampered")
    if r.get("required_ledger_status") != REQUIRED_LEDGER_STATUS:
        errors.append("required_ledger_status_tampered")
    if r.get("c6_rejection_reason") != C6_REJECTION_REASON:
        errors.append("c6_rejection_reason_tampered")
    if r.get("lessons_from_rejected_families") != (
            LESSONS_FROM_REJECTED_FAMILIES):
        errors.append("lessons_tampered")
    if tuple(r.get("rejected_family_logic_blacklist") or ()) != (
            REJECTED_FAMILY_LOGIC_BLACKLIST):
        errors.append("rejected_family_logic_blacklist_tampered")
    # morning-report schema fields
    mr = r.get("morning_report_schema") or {}
    if mr.get("report_kind") != MORNING_REPORT_SCHEMA["report_kind"]:
        errors.append("morning_report_kind_tampered")
    if tuple(mr.get("required_fields") or ()) != (
            MORNING_REPORT_SCHEMA["required_fields"]):
        errors.append("morning_report_required_fields_tampered")
    if mr.get("field_kinds") != MORNING_REPORT_SCHEMA["field_kinds"]:
        errors.append("morning_report_field_kinds_tampered")
    if tuple(mr.get("must_include_locks") or ()) != (
            MORNING_REPORT_SCHEMA["must_include_locks"]):
        errors.append("morning_report_locks_tampered")
    for key in ("report_is_research_only", "report_authorizes_nothing",
                "report_is_not_a_profitability_claim"):
        if mr.get(key) is not True:
            errors.append("morning_report_flag_wrong:" + key)
    if tuple(mr.get("banned_tokens_in_next_human_gate") or ()) != (
            MORNING_REPORT_SCHEMA["banned_tokens_in_next_human_gate"]):
        errors.append("morning_report_banned_tokens_tampered")
    # next-candidate plan schema
    plan = r.get("next_candidate_recommendation_plan_schema") or {}
    if plan.get("plan_kind") != (
            NEXT_CANDIDATE_RECOMMENDATION_PLAN_SCHEMA["plan_kind"]):
        errors.append("plan_kind_tampered")
    if tuple(plan.get("required_fields") or ()) != (
            NEXT_CANDIDATE_RECOMMENDATION_PLAN_SCHEMA[
                "required_fields"]):
        errors.append("plan_required_fields_tampered")
    if tuple(plan.get(
            "differentiation_must_address_each_of") or ()) != (
            NEXT_CANDIDATE_RECOMMENDATION_PLAN_SCHEMA[
                "differentiation_must_address_each_of"]):
        errors.append("plan_differentiation_targets_tampered")
    if tuple(plan.get("rejected_family_logic_blacklist") or ()) != (
            REJECTED_FAMILY_LOGIC_BLACKLIST):
        errors.append("plan_blacklist_tampered")
    for key in ("fee_assumption_must_equal_27_bps_round_trip",
                "minimum_floor_must_equal_81_bps",
                "plan_is_research_only",
                "plan_authorizes_nothing",
                "plan_is_not_a_promotion",
                "plan_cannot_reuse_any_rejected_family_logic",
                "human_review_required_at_every_gate"):
        if plan.get(key) is not True:
            errors.append("plan_flag_wrong:" + key)
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
                "generates_morning_report_now",
                "generates_next_candidate_proposal_now",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate", "claims_profitability",
                "uses_external_data_source"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    if r.get("next_required_action") != NEXT_REQUIRED_ACTION:
        errors.append("next_required_action_tampered")
    if r.get("verdict") == VERDICT_OAP2_READY and r.get("blockers"):
        errors.append("ready_with_blockers")
    return {"valid": not errors, "errors": errors}
