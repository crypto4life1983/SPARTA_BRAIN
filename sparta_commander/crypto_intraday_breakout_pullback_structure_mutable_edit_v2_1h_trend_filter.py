"""SPARTA BREAKOUT-PULLBACK MUTABLE CANDIDATE EDIT V2 - 1H TREND FILTER
(READ-ONLY, RESEARCH ONLY, AUTHORIZES NOTHING).

The ONE V2 experiment authorized by the frozen replay evidence (gross
negative in every variant -- edge failure): add the 1h trend-alignment
filter the original concept specified but the detector never implemented.
A long breakout is eligible only when the 1h close is above the 1h SMA(20)
at breakout time; shorts mirror below. This is a FILTER ONLY: it can reduce
or equal the trade count, never expand it, and no entry rule is weakened.
Everything else is unchanged -- breakout/pullback/continuation rules, stop
models, the 81 bps floor, 27 bps costs, anti-lookahead and conservative
replay standards, detector schema, locked scorer, locked instructions, and
both prior candidates' evidence. If V2 also fails the fee-honest replay,
candidate #2 is rejected and kept on record. This block edits the candidate
asset only and runs nothing.
"""

from __future__ import annotations

from typing import Any

from sparta_commander.crypto_d1_auto_research_mutable_candidate_asset_spec import (
    VERDICT_ASSET_ACCEPTED,
    validate_candidate_asset,
)
from sparta_commander.crypto_intraday_breakout_pullback_structure_replay_results_review_contract import (
    VERDICT_BPR2_FROZEN,
    build_bp_replay_results_review,
)
from sparta_commander.crypto_intraday_breakout_pullback_structure_strategy_spec_contract import (
    CANDIDATE_FAMILY,
    CANDIDATE_ID,
    MINIMUM_RISK_DISTANCE_BPS,
    build_candidate_asset_instance,
)

BV2_SCHEMA_VERSION = (
    "crypto_intraday_breakout_pullback_structure_mutable_edit_v2_1h_trend"
    "_filter.v1")
BV2_LABEL = ("SPARTA Breakout-Pullback Mutable Candidate Edit V2 - 1h Trend "
             "Filter (READ-ONLY, RESEARCH ONLY, FILTER ONLY)")
BV2_MODE = "RESEARCH_ONLY"
EDIT_BV2_ID = (
    "BP_STRUCTURE_MUTABLE_CANDIDATE_EDIT_V2_1H_TREND_FILTER")
VERDICT_BV2_READY = "BP_MUTABLE_EDIT_V2_1H_TREND_FILTER_READY"
VERDICT_BV2_BLOCKED = "BP_MUTABLE_EDIT_V2_1H_TREND_FILTER_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_BP_V2_REDETECTION_WITH_1H_TREND_FILTER"

V2_TREND_FILTER_RULE = (
    "a long breakout is eligible only when the most recent COMPLETED 1h "
    "close is above the 1h SMA(20) at the breakout bar's time; a short "
    "breakout is eligible only when it is below; setups failing the filter "
    "are rejected and kept auditable; the filter can only remove setups, "
    "never add or weaken them")

V2_NEW_PARAMETERS = {
    "htf_trend_filter_enabled": True,
    "htf_trend_timeframe": "1h",
    "htf_trend_sma_period": 20,
    "htf_trend_rule_long": "1h_close_above_1h_sma20_at_breakout_time",
    "htf_trend_rule_short": "1h_close_below_1h_sma20_at_breakout_time",
    "filter_only_trade_count_must_reduce_or_equal": True,
}

UNCHANGED_GUARANTEES = (
    "breakout_pullback_continuation_rules_unchanged_no_loosening",
    "stop_models_unchanged_structural_or_atr_wider",
    "81bps_floor_unchanged_27bps_costs_unchanged",
    "anti_lookahead_and_conservative_replay_standards_unchanged",
    "detector_label_schema_unchanged_38_fields_10_statuses",
    "locked_scorer_unchanged", "locked_instructions_unchanged",
    "candidate_1_and_candidate_2_evidence_kept_on_record",
    "no_maker_execution_assumption",
)

FORBIDDEN = (
    "weakening_entry_rules", "expanding_trade_scope",
    "lowering_the_81_bps_floor", "lowering_costs",
    "assuming_maker_execution", "changing_locked_scorer_or_instructions",
    "changing_detector_label_schema",
    "automatic_redetection_or_replay", "optimizer_runs",
    "paper_live_micro_live_authorization", "order_placement",
    "broker_exchange_private_api_access",
    "credentials_api_keys_login_account_wallet",
    "deleting_or_hiding_prior_rejected_evidence", "gate_unlocks",
)

FAILURE_RULE = ("if V2 with the 1h trend filter also fails the fee-honest "
                "replay, candidate #2 is rejected and kept on record")


def get_bp_mutable_edit_v2_label() -> str:
    return BV2_LABEL


def build_edited_candidate_asset_bv2() -> dict[str, Any]:
    """The V2-edited candidate asset: the base instance plus the 1h trend
    filter parameters. Deep-copied; base output never mutated. Pure."""
    base = build_candidate_asset_instance()
    fields = dict(base["fields"])
    parameters = dict(fields["parameters"])
    parameters.update(V2_NEW_PARAMETERS)
    fields["parameters"] = parameters
    fields["constraints"] = (str(fields["constraints"])
                             + "; v2 1h trend filter: " + V2_TREND_FILTER_RULE)
    fields["lineage"] = (str(fields["lineage"])
                         + ">edit_v2_1h_trend_filter_per_frozen_replay"
                           "_evidence_minus_55_61r")
    fields["status"] = "proposed"
    fields["audit_notes"] = ("mutable edit v2 applied per the frozen replay "
                             "results review (gross-negative edge failure); "
                             "one experiment only; filter only; "
                             "re-detection and replay require separate "
                             "human approvals; " + FAILURE_RULE)
    fields["rationale"] = ("105 trades lost gross in all variants; the "
                           "original concept specified 1h context but the "
                           "detector was 15m-only; aligning breakouts with "
                           "the 1h trend is a stricter filter expected to "
                           "remove range-market fake breakouts")
    edited = dict(base)
    edited["fields"] = fields
    return edited


def record_bp_mutable_edit_v2(
        replay_review_verdict: Any) -> dict[str, Any]:
    """Assemble the V2 edit record, gated on the frozen replay evidence."""
    record: dict[str, Any] = {
        "schema_version": BV2_SCHEMA_VERSION, "label": BV2_LABEL,
        "mode": BV2_MODE, "lane": "crypto_d1_auto_research",
        "edit_id": EDIT_BV2_ID, "candidate_id": CANDIDATE_ID,
        "candidate_family": CANDIDATE_FAMILY,
        "verdict": None, "blockers": [],
        "replay_review_verdict": replay_review_verdict,
        "v2_new_parameters": dict(V2_NEW_PARAMETERS),
        "v2_trend_filter_rule": V2_TREND_FILTER_RULE,
        "unchanged_guarantees": list(UNCHANGED_GUARANTEES),
        "failure_rule": FAILURE_RULE,
        "forbidden": list(FORBIDDEN),
        "edited_asset": None, "edited_asset_verdict": None,
        "filter_only_never_expands_scope": True,
        "entry_rules_weakened": False,
        "cost_floor_lowered": False,
        "maker_execution_assumed": False,
        "one_experiment_only": True,
        "redetection_requires_separate_human_approval": True,
        "replay_requires_separate_human_approval": True,
        "prior_evidence_kept_on_record": True,
        "modifies_mission_flow": False, "modifies_pm_lane": False,
        "modifies_locked_scorer": False,
        "modifies_locked_instructions": False,
        "modifies_detector_label_schema": False,
        "modifies_staged_candles": False,
        "modifies_previous_labels": False,
        "human_review_required": True,
        "executes": False, "writes_files": False, "writes_reports": False,
        "runs_detector_now": False, "runs_replay_now": False,
        "scores_now": False, "fetches_data": False, "calls_api": False,
        "uses_network": False, "uses_credentials": False, "uses_wallet": False,
        "connects_broker": False, "connects_exchange": False,
        "uses_real_money": False, "contains_order_logic": False,
        "starts_scheduler": False, "sends_notifications": False,
        "authorizes_paper_execution": False, "authorizes_micro_live": False,
        "authorizes_live_trading": False, "promotes_gate": False,
        "unlocks_downstream_gate": False,
        "paper_trading_gate_locked": True, "micro_live_gate_locked": True,
        "live_gate_locked": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    if replay_review_verdict != VERDICT_BPR2_FROZEN:
        record["verdict"] = VERDICT_BV2_BLOCKED
        record["blockers"].append("replay_evidence_not_frozen")
        return record
    edited = build_edited_candidate_asset_bv2()
    asset_check = validate_candidate_asset(edited)
    record["edited_asset_verdict"] = asset_check.get("verdict")
    if asset_check.get("verdict") != VERDICT_ASSET_ACCEPTED:
        record["verdict"] = VERDICT_BV2_BLOCKED
        record["blockers"].append("edited_asset_rejected_by_asset_spec")
        record["blockers"].extend(asset_check.get("errors") or [])
        return record
    record["edited_asset"] = edited
    record["verdict"] = VERDICT_BV2_READY
    return record


def build_bp_mutable_edit_v2(
        repo_root: Any = "C:/SPARTA_BRAIN") -> dict[str, Any]:
    """Build against the LIVE frozen replay evidence on disk."""
    review = build_bp_replay_results_review(repo_root, tracked_paths=[])
    return record_bp_mutable_edit_v2(review.get("verdict"))


def validate_bp_mutable_edit_v2(record: Any) -> dict[str, Any]:
    """Validate the V2 edit record's shape and safety invariants."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_BV2_READY, VERDICT_BV2_BLOCKED):
        errors.append("bad_verdict")
    if r.get("edit_id") != EDIT_BV2_ID:
        errors.append("edit_id_tampered")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if r.get("v2_new_parameters") != V2_NEW_PARAMETERS:
        errors.append("v2_parameters_tampered")
    if r.get("v2_trend_filter_rule") != V2_TREND_FILTER_RULE:
        errors.append("trend_filter_rule_tampered")
    if tuple(r.get("unchanged_guarantees") or ()) != UNCHANGED_GUARANTEES:
        errors.append("unchanged_guarantees_tampered")
    if r.get("failure_rule") != FAILURE_RULE:
        errors.append("failure_rule_tampered")
    if tuple(r.get("forbidden") or ()) != FORBIDDEN:
        errors.append("forbidden_list_weakened")
    if r.get("filter_only_never_expands_scope") is not True:
        errors.append("must_remain_a_filter_only")
    for key in ("entry_rules_weakened", "cost_floor_lowered",
                "maker_execution_assumed"):
        if r.get(key) is not False:
            errors.append("must_be_false_forever:" + key)
    if r.get("verdict") == VERDICT_BV2_READY:
        if r.get("blockers"):
            errors.append("ready_with_blockers")
        if r.get("replay_review_verdict") != VERDICT_BPR2_FROZEN:
            errors.append("ready_without_frozen_replay_evidence")
        if r.get("edited_asset_verdict") != VERDICT_ASSET_ACCEPTED:
            errors.append("ready_without_accepted_asset")
        edited = r.get("edited_asset") or {}
        parameters = (edited.get("fields") or {}).get("parameters") or {}
        for key, value in V2_NEW_PARAMETERS.items():
            if parameters.get(key) != value:
                errors.append("v2_parameter_missing:" + key)
        if parameters.get("minimum_risk_distance_bps") != (
                MINIMUM_RISK_DISTANCE_BPS):
            errors.append("floor_parameter_lost")
    for key, want in (
        ("one_experiment_only", True),
        ("redetection_requires_separate_human_approval", True),
        ("replay_requires_separate_human_approval", True),
        ("prior_evidence_kept_on_record", True),
        ("modifies_mission_flow", False), ("modifies_pm_lane", False),
        ("modifies_locked_scorer", False),
        ("modifies_locked_instructions", False),
        ("modifies_detector_label_schema", False),
        ("modifies_staged_candles", False),
        ("modifies_previous_labels", False),
        ("human_review_required", True),
        ("paper_trading_gate_locked", True),
        ("micro_live_gate_locked", True), ("live_gate_locked", True),
    ):
        if r.get(key) is not want:
            errors.append("constitution_flag_wrong:" + key)
    for key in ("executes", "writes_files", "writes_reports",
                "runs_detector_now", "runs_replay_now", "scores_now",
                "fetches_data", "calls_api", "uses_network",
                "uses_credentials", "uses_wallet", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    return {"valid": not errors, "errors": errors}
