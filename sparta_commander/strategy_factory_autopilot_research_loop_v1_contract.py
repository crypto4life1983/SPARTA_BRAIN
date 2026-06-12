"""SPARTA STRATEGY FACTORY AUTOPILOT RESEARCH LOOP V1 (READ-ONLY,
RESEARCH ONLY, RULES + STATE MACHINE + SAFETY BOUNDARIES ONLY).

Turns the proven candidate-by-candidate workflow into a semi-automated
research factory CONSTITUTION. Four families have completed the full
lifecycle under it -- spec, detector, dry run, real-candle labels,
fee-honest replay, at most one pre-committed edit, formal rejection --
with zero trades, zero claims, zero deleted evidence. This contract
encodes those mechanics as the loop's law so candidate #5 and beyond run
the same gauntlet with less manual scaffolding and ZERO new authority.

WHAT THE AUTOPILOT IS: a research loop definition. It certifies the
ledger, orders the stages, applies the pre-committed auto-rejection
rules, and produces evidence-language status reports and next-family
RECOMMENDATIONS for the human.

WHAT THE AUTOPILOT IS NOT, EVER: a trader. No paper, no live, no wallet,
no account, no API keys, no orders, no auto-commit, no auto-push, no
evidence deletion, no artifact overwrite, no profitability claims, no
"winner" language from small samples. Every commit, every push, every
promotion, every credential is a HUMAN gate, forever.

This block defines rules only. It runs no detector, fetches nothing,
replays nothing, and does not start candidate #5.
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
from sparta_commander.sol_btc_long_1h_swing_structure_rejection_record_contract import (
    REJECTION_REASON as C4_REASON,
    REJECTION_STATUS as C4_STATUS,
)

AP_SCHEMA_VERSION = "strategy_factory_autopilot_research_loop.v1"
AP_LABEL = ("SPARTA Strategy Factory Autopilot Research Loop V1 "
            "(READ-ONLY, RESEARCH ONLY, RULES AND GATES ONLY, "
            "NEVER A TRADER)")
AP_MODE = "RESEARCH_ONLY"
VERDICT_AP_READY = "STRATEGY_FACTORY_AUTOPILOT_RESEARCH_LOOP_V1_READY"
VERDICT_AP_BLOCKED = "STRATEGY_FACTORY_AUTOPILOT_RESEARCH_LOOP_V1_BLOCKED"
NEXT_REQUIRED_ACTION = (
    "HUMAN_APPROVED_CANDIDATE_5_FAMILY_PROPOSAL_VIA_AUTOPILOT_LOOP")

LEDGER_HEAD_AT_DEFINITION = (
    "bed8f5241768ff6ec5e2cb8638ce1439ee2d9ee1")

FOUR_CANDIDATE_LEDGER = {
    "candidate_1": {
        "family": "ny_session_fvg_choch",
        "status": "REJECTED_KEPT_ON_RECORD",
        "reason": "COST_NON_VIABLE_RISK_GEOMETRY"},
    "candidate_2": {
        "family": "crypto_intraday_breakout_pullback_structure",
        "status": "REJECTED_KEPT_ON_RECORD",
        "reason": "EDGE_FAILURE_SURVIVED_ONE_AUTHORIZED_FILTER"
                  "_EXPERIMENT"},
    "candidate_3": {
        "family": "long_biased_trend_continuation",
        "status": "REJECTED_KEPT_ON_RECORD",
        "reason": "NEAR_ZERO_SETUPS_AFTER_ONE_AUTHORIZED_STRUCTURE"
                  "_EDIT"},
    "candidate_4": {
        "family": "long_1h_swing_structure",
        "status": "REJECTED_KEPT_ON_RECORD",
        "reason": "EDGE_FAILURE_SURVIVED_ONE_AUTHORIZED_FILTER_ONLY"
                  "_EDIT"},
    "zero_trades_zero_claims_zero_deleted_evidence": True,
}

REJECTED_FAMILIES = (
    "ny_session_fvg_choch",
    "crypto_intraday_breakout_pullback_structure",
    "long_biased_trend_continuation",
    "long_1h_swing_structure",
)

# 1. candidate family queue rules ------------------------------------------
QUEUE_RULES = (
    "the loop generates or selects the next candidate family as a "
    "RECOMMENDATION; the human decides",
    "rejected geometry may never be reused unchanged",
    "seeds from closed candidates are inspiration only, never rescue "
    "paths",
    "the next candidate must be a new family or a materially different "
    "hypothesis",
    "every family proposal must name its hypothesis and how it differs "
    "from each rejected family",
)

# 2. ordered research loop stages (the state machine) ----------------------
LOOP_STAGES = (
    "candidate_spec",
    "detector_and_label_review",
    "real_candle_label_freeze",
    "fee_honest_replay",
    "replay_results_review",
    "one_authorized_edit_if_pre_committed_and_evidence_supported",
    "formal_rejection_record_or_promotion_to_human_review_record",
)

# 3. pre-committed auto-rejection rules ------------------------------------
AUTO_REJECTION_RULES = (
    "gross_negative_and_net_negative_after_replay",
    "below_breakeven_hit_rate",
    "near_zero_setup_count_after_one_structure_edit",
    "cost_nonviable_risk_geometry",
    "filter_or_edit_spent_and_still_negative",
    "correlation_or_overlap_adjusted_failure",
    "any_artifact_hash_or_gate_mismatch",
)

# 4. human gates (never automated) -----------------------------------------
HUMAN_GATES = (
    "commit_approval",
    "push_approval",
    "promotion_to_paper_review",
    "promotion_to_paper_trading",
    "promotion_to_micro_live",
    "any_credential_api_or_order_capability",
    "any_change_that_weakens_entries_or_adds_trades_after_labels"
    "_are_frozen",
)

# 5. safety locks -----------------------------------------------------------
SAFETY_LOCKS = (
    "paper_and_live_locked",
    "order_account_wallet_api_capability_false",
    "no_auto_delete_evidence",
    "no_auto_overwrite_artifacts",
    "no_profitability_claim_until_separate_promotion_contract",
    "no_winner_wording_from_small_samples",
    "all_output_must_be_evidence_language_only",
    "no_auto_push",
    "no_auto_commit_unless_a_future_human_approved_policy_explicitly"
    "_allows_it",
)

FORBIDDEN_OUTPUT_LANGUAGE = (
    "winner", "winning strategy", "profitable", "profitability proven",
    "edge confirmed", "guaranteed", "can't lose", "holy grail",
    "ready for live", "ready for paper",
)

# 6. candidate #5 preparation policy ---------------------------------------
CANDIDATE_5_POLICY = (
    "same_symbol_non_overlap_cooldown_should_be_considered_at_label"
    "_replay_time",
    "structural_stop_geometry_must_be_tested_against_fees_before"
    "_promotion",
    "sol_relative_strength_clue_is_too_small_to_promote_but_can"
    "_inspire_a_new_hypothesis",
    "btc_weakness_in_c4_is_not_edge_evidence",
    "overlapping_cluster_wins_and_losses_must_be_penalized",
    "candidate_5_must_not_reuse_c4_as_is",
    "candidate_5_must_start_from_a_clean_hypothesis",
)

# 7. overnight / scheduled certification role ------------------------------
SCHEDULED_ROLE = {
    "may_certify_ledger": True,
    "may_produce_research_status_report": True,
    "may_recommend_next_candidate_family": True,
    "may_trade": False,
    "may_paper_trade": False,
    "may_push": False,
    "may_commit": False,
    "may_claim_profitability": False,
}


def get_autopilot_loop_label() -> str:
    return AP_LABEL


def screen_output_language(text: Any) -> dict[str, Any]:
    """Evidence-language screen: flags forbidden winner/profitability
    wording in any loop output. Pure; never raises."""
    if not isinstance(text, str):
        return {"acceptable": False,
                "violations": ["output_not_a_string"]}
    lowered = text.lower()
    violations = [token for token in FORBIDDEN_OUTPUT_LANGUAGE
                  if token in lowered]
    return {"acceptable": not violations, "violations": violations}


def validate_candidate_family_proposal(proposal: Any) -> dict[str, Any]:
    """Pure gate over a next-family proposal: new or materially
    different, never a rejected family unchanged, seeds never rescues.
    Never raises."""
    errors: list[str] = []
    if not isinstance(proposal, dict):
        return {"acceptable": False, "errors": ["proposal_not_a_dict"]}
    family = str(proposal.get("family") or "").strip()
    if not family:
        errors.append("family_required")
    if family in REJECTED_FAMILIES:
        errors.append("rejected_family_must_not_be_reused_unchanged")
    if not str(proposal.get("hypothesis") or "").strip():
        errors.append("clean_hypothesis_required")
    if not str(proposal.get(
            "difference_from_rejected_families") or "").strip():
        errors.append("difference_from_rejected_families_required")
    if proposal.get("uses_seeds_as_rescue") is not False:
        errors.append("seeds_must_not_be_rescue_paths")
    language = screen_output_language(
        str(proposal.get("hypothesis") or ""))
    if not language["acceptable"]:
        errors.append("forbidden_language_in_hypothesis")
    return {"acceptable": not errors, "errors": errors}


def build_autopilot_loop_contract() -> dict[str, Any]:
    """Assemble the loop constitution, gated on ALL FOUR rejection
    records being intact -- the loop cannot exist if the ledger broke."""
    record: dict[str, Any] = {
        "schema_version": AP_SCHEMA_VERSION, "label": AP_LABEL,
        "mode": AP_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [],
        "ledger_head_at_definition": LEDGER_HEAD_AT_DEFINITION,
        "four_candidate_ledger": {
            key: (dict(value) if isinstance(value, dict) else value)
            for key, value in FOUR_CANDIDATE_LEDGER.items()},
        "rejected_families": list(REJECTED_FAMILIES),
        "queue_rules": list(QUEUE_RULES),
        "loop_stages_ordered": list(LOOP_STAGES),
        "auto_rejection_rules": list(AUTO_REJECTION_RULES),
        "human_gates": list(HUMAN_GATES),
        "safety_locks": list(SAFETY_LOCKS),
        "forbidden_output_language": list(FORBIDDEN_OUTPUT_LANGUAGE),
        "candidate_5_policy": list(CANDIDATE_5_POLICY),
        "scheduled_role": dict(SCHEDULED_ROLE),
        "cost_floor_bps": MINIMUM_RISK_DISTANCE_BPS,
        "controller_is_research_only": True,
        "every_stage_still_requires_evidence_freeze_and_human_gates":
            True,
        "human_review_required": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True, "live_gate_locked": True,
        "executes": False, "writes_files": False,
        "runs_real_detection_now": False, "runs_replay_now": False,
        "scores_now": False, "stages_data_now": False,
        "fetches_data": False, "calls_api": False, "uses_network": False,
        "uses_credentials": False, "uses_wallet": False,
        "uses_account": False, "connects_broker": False,
        "connects_exchange": False, "uses_real_money": False,
        "contains_order_logic": False, "starts_scheduler": False,
        "sends_notifications": False,
        "auto_commits": False, "auto_pushes": False,
        "auto_deletes_evidence": False, "auto_overwrites_artifacts": False,
        "starts_candidate_5_now": False,
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
    )
    for name, status, reason, expected_reason in checks:
        if status != "REJECTED_KEPT_ON_RECORD" \
                or reason != expected_reason:
            record["verdict"] = VERDICT_AP_BLOCKED
            record["blockers"].append(name + "_ledger_broken")
            return record
    if MINIMUM_RISK_DISTANCE_BPS != 81:
        record["verdict"] = VERDICT_AP_BLOCKED
        record["blockers"].append("risk_floor_constant_changed_upstream")
        return record
    record["verdict"] = VERDICT_AP_READY
    return record


def validate_autopilot_loop_contract(record: Any) -> dict[str, Any]:
    """Validate shape and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_AP_READY, VERDICT_AP_BLOCKED):
        errors.append("bad_verdict")
    if r.get("ledger_head_at_definition") != LEDGER_HEAD_AT_DEFINITION:
        errors.append("ledger_head_tampered")
    expected_ledger = {
        key: (dict(value) if isinstance(value, dict) else value)
        for key, value in FOUR_CANDIDATE_LEDGER.items()}
    if r.get("four_candidate_ledger") != expected_ledger:
        errors.append("ledger_tampered")
    if tuple(r.get("rejected_families") or ()) != REJECTED_FAMILIES:
        errors.append("rejected_families_tampered")
    if tuple(r.get("queue_rules") or ()) != QUEUE_RULES:
        errors.append("queue_rules_tampered")
    if tuple(r.get("loop_stages_ordered") or ()) != LOOP_STAGES:
        errors.append("loop_stages_tampered")
    if tuple(r.get("auto_rejection_rules") or ()) != (
            AUTO_REJECTION_RULES):
        errors.append("auto_rejection_rules_weakened")
    if tuple(r.get("human_gates") or ()) != HUMAN_GATES:
        errors.append("human_gates_weakened")
    if tuple(r.get("safety_locks") or ()) != SAFETY_LOCKS:
        errors.append("safety_locks_weakened")
    if tuple(r.get("forbidden_output_language") or ()) != (
            FORBIDDEN_OUTPUT_LANGUAGE):
        errors.append("language_screen_weakened")
    if tuple(r.get("candidate_5_policy") or ()) != CANDIDATE_5_POLICY:
        errors.append("candidate_5_policy_tampered")
    if r.get("scheduled_role") != SCHEDULED_ROLE:
        errors.append("scheduled_role_tampered")
    if r.get("cost_floor_bps") != MINIMUM_RISK_DISTANCE_BPS:
        errors.append("floor_tampered")
    for key in ("controller_is_research_only",
                "every_stage_still_requires_evidence_freeze_and_human"
                "_gates",
                "human_review_required", "paper_trading_gate_locked",
                "micro_live_gate_locked", "live_gate_locked"):
        if r.get(key) is not True:
            errors.append("constitution_flag_wrong:" + key)
    for key in ("executes", "writes_files", "runs_real_detection_now",
                "runs_replay_now", "scores_now", "stages_data_now",
                "fetches_data", "calls_api", "uses_network",
                "uses_credentials", "uses_wallet", "uses_account",
                "connects_broker", "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "auto_commits", "auto_pushes",
                "auto_deletes_evidence", "auto_overwrites_artifacts",
                "starts_candidate_5_now",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate", "claims_profitability"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    return {"valid": not errors, "errors": errors}
