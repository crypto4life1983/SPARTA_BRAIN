"""SPARTA Automation Readiness -- BUNDLE / SURFACE INTEGRATION v1
(PURE, RESEARCH ONLY).

A thin, pure integration that CONNECTS the candidate-research-lane status surface
into the bundle / automation workflow so the whole system visibly moves from
"C16 complete" to "automation readiness" -- not to another candidate. It composes,
read-only:

  * the candidate-research-lane status surface (authoritative directive),
  * the Gate Decision Coordinator's idle/default recommendation (now aligned), and
  * a morning-report / autopilot-style block,

and asserts they AGREE: C16 lifecycle complete, rejected ledger C1-C19 (24), the
next stage is automation readiness, no new candidate is recommended, the overnight/
morning automation path stays research-only, real-data-QA/replay stay BLOCKED, and
paper/micro-live/live stay LOCKED. The generic Safe Research Autopilot idle action
(build a proposal) is OVERRIDDEN by the lane directive at the system level.

It executes NOTHING: no detector, no labels, no replay, no PnL, no optimization,
no data fetch, no writes, no new candidate, no paper/live/broker/order surface.
Every capability flag is pinned False with a full scope_locks set.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.crypto_d1_candidate_research_lane_status_v1_contract as _lane
import sparta_commander.gate_decision_coordinator_v1_contract as _gdc
import sparta_commander.safe_research_autopilot_v1_contract as _sara

ARI_VERSION = "v1"
ARI_MODE = "RESEARCH_ONLY"
ARI_LANE = "crypto_d1_auto_research"

AUTOMATION_READINESS_TOKEN = _lane.NEXT_REQUIRED_ACTION  # BUILD_AUTOMATION_..._ONLY

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "runs_detector", "runs_labels", "runs_replay",
    "computes_pnl", "optimizes_parameters", "runs_robustness", "fetches_data",
    "reads_real_data", "mutates_data", "stages_data", "auto_commits", "auto_pushes",
    "starts_a_new_candidate", "recommends_new_candidate", "modifies_scheduler",
    "starts_scheduler", "sends_notifications", "calls_api", "uses_network",
    "uses_credentials", "connects_broker", "connects_exchange", "uses_real_money",
    "places_orders", "contains_order_logic", "paper_trading", "live_trading",
    "deploys_capital", "promotes_gate", "unlocks_downstream_gate", "skips_any_gate",
    "advances_without_human_approval", "claims_profitability", "claims_edge",
    "crosses_into_forbidden_gate",
)


def _idle_coordinator_state() -> dict:
    """A representative clean + synced + ledger-consistent + no-open-gate state, so
    the coordinator's IDLE/default branch is exercised. Declared-only; no I/O."""
    return {
        "repo": {"clean": True, "ahead": 0, "behind": 0,
                 "uncommitted_changes": False},
        "ledger": {"canonical_count": _lane.REJECTED_LEDGER_COUNT,
                   "expected_count": _lane.REJECTED_LEDGER_COUNT,
                   "reconciles": True},
        "candidates": {
            "C16": {"family": "cointegration_pairs_market_neutral",
                    "status": "REJECTED_KEPT_ON_RECORD", "active": False,
                    "next_action": "NONE__C16_CLOSED", "shipped": True},
        },
    }


def build_automation_readiness_integration() -> dict[str, Any]:
    """Compose the lane status + coordinator-idle + morning blocks and assert the
    surfaces agree that the next stage is automation readiness. Pure; executes
    nothing."""
    lane = _lane.get_lane_status()
    lane_morning = _lane.summarize_for_morning_report()
    coord = _gdc.coordinate(_idle_coordinator_state())
    coord_morning = _gdc.summarize_for_morning_report(coord)
    # The generic SARA idle action (stage NONE) is build-a-proposal; the lane
    # directive overrides it at the system level (informational only).
    sara_idle = _sara.decide_next_safe_action(
        {"active_candidate": None, "stage": _sara.STAGE_NONE,
         "proposed_family": None},
        {"clean": True, "uncommitted_candidate_artifacts": False})
    sara_generic_idle_action = sara_idle.get("next_safe_action")

    # The CURRENT lane directive (authoritative). Post-C16 this was automation
    # readiness; C17 then C18 were each proposed, advanced, and REJECTED at the
    # fee-honest replay stage, so the directive is AUTOMATION READINESS again. The
    # integration follows the lane.
    token = lane.get("next_required_action")
    surfaces = {
        "lane_status_next": lane.get("next_required_action"),
        "coordinator_command": coord.get("next_safe_command"),
        "lane_morning_next": lane_morning.get("next_required_action"),
        "coordinator_recommendation_kind": coord.get("recommendation_kind"),
    }
    all_tokens_match = (
        lane.get("next_required_action") == token
        and coord.get("next_safe_command") == token
        and lane_morning.get("next_required_action") == token)
    no_new_candidate = (
        lane.get("next_is_new_candidate") is False
        and coord.get("next_research_recommended") is False
        and lane_morning.get("next_is_new_candidate") is False)
    research_only = (
        lane.get("overnight_automation_research_only") is True
        and coord.get("executes_nothing") is True)
    downstream_locked = (
        lane.get("real_data_qa_state") == _lane.STATE_BLOCKED
        and lane.get("replay_state") == _lane.STATE_BLOCKED
        and lane.get("paper_trading_state") == _lane.STATE_LOCKED
        and lane.get("live_trading_state") == _lane.STATE_LOCKED)
    coordinator_matches_lane_directive = (
        coord.get("next_safe_command") == token)
    surfaces_agree = (all_tokens_match and no_new_candidate and research_only
                      and downstream_locked and coordinator_matches_lane_directive
                      and lane.get("c16_lifecycle_complete") is True
                      and lane.get("rejected_ledger_count") == 25)
    det = lane.get("active_candidate_detail") or {}
    _rej = lane.get("last_rejected_candidate_detail") or {}

    record: dict[str, Any] = {
        "version": ARI_VERSION, "mode": ARI_MODE, "lane": ARI_LANE,
        "is_pure_integration_only": True,
        "label": (
            "Candidate-lane directive integration v1 (READ-ONLY, RESEARCH ONLY). "
            "Connects the candidate-research-lane status into the coordinator/"
            "morning/autopilot surfaces so they AGREE on the current directive. "
            "Candidate #21 (low-turnover same-asset spot/perp funding carry) is now "
            "the ACTIVE open candidate at the family_proposal gate awaiting the human "
            "candidate-spec decision; C20 stays rejected (kept on record, not "
            "rescued). Executes nothing; overnight/morning automation stays "
            "research-only and human-gated."),
        # the aligned directive (follows the lane)
        "next_required_action": token,
        "next_stage": lane.get("next_stage"),
        "next_is_automation_readiness": lane.get("next_is_automation_readiness"),
        "next_is_new_candidate": False,
        "active_candidate": lane.get("active_candidate"),
        "open_candidate_gate": lane.get("open_candidate_gate"),
        # C21 is the ACTIVE open candidate -> surface its fields
        "active_candidate_label": det.get("label"),
        "active_candidate_verdict": det.get("verdict"),
        "active_candidate_stage": det.get("stage"),
        "active_candidate_stage_label": det.get("stage_label"),
        "active_candidate_timeframe": det.get("timeframe"),
        "active_candidate_scope_note": det.get("scope_note"),
        "active_candidate_is_market_neutral": det.get("is_market_neutral"),
        "active_candidate_is_low_turnover": det.get("is_low_turnover"),
        "c20_remains_rejected_not_rescued":
            lane.get("c20_remains_rejected_not_rescued"),
        # C20 stays visible as the last rejected candidate (provenance)
        "last_rejected_candidate": lane.get("last_rejected_candidate"),
        "last_rejected_candidate_label": _rej.get("label"),
        "last_rejected_candidate_verdict": _rej.get("verdict"),
        "last_rejected_candidate_rejected_at": _rej.get("rejected_at"),
        "last_rejected_candidate_reason": _rej.get("rejection_reason"),
        "requires_human_approval": True,
        # C16 completion + ledger
        "c16_lifecycle_complete": lane.get("c16_lifecycle_complete"),
        "rejected_ledger_count": lane.get("rejected_ledger_count"),
        # cross-surface agreement
        "surfaces": surfaces,
        "surfaces_agree": surfaces_agree,
        "all_tokens_match": all_tokens_match,
        "no_new_candidate_recommended": no_new_candidate,
        "automation_research_only": research_only,
        "downstream_blocked_and_locked": downstream_locked,
        "coordinator_matches_lane_directive": coordinator_matches_lane_directive,
        # SARA generic idle is overridden by the lane directive
        "sara_generic_idle_action": sara_generic_idle_action,
        "sara_generic_idle_overridden_by_lane_directive": True,
        # downstream capability stays blocked/locked
        "real_data_qa_state": lane.get("real_data_qa_state"),
        "replay_state": lane.get("replay_state"),
        "paper_trading_state": lane.get("paper_trading_state"),
        "live_trading_state": lane.get("live_trading_state"),
        "overnight_automation_research_only": lane.get(
            "overnight_automation_research_only"),
        "integrated_surfaces": [
            "candidate_research_lane_status_v1",
            "gate_decision_coordinator_v1",
            "morning_report_block",
            "safe_research_autopilot_v1 (idle overridden)",
        ],
        "human_review_required": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_execute": True, "no_write": True, "no_detector": True,
        "no_labels": True, "no_replay": True, "no_pnl": True,
        "no_optimization": True, "no_data_fetch": True, "no_real_data_access": True,
        "no_stage": True, "no_commit": True, "no_push": True, "no_auto_commit": True,
        "no_auto_push": True, "no_new_candidate": True, "no_scheduler_change": True,
        "no_broker": True, "no_credentials": True, "no_order_logic": True,
        "no_paper_trading": True, "no_live_trading": True, "no_gate_skip": True,
        "no_downstream_gate_unlock": True, "no_profitability_claim": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def summarize_for_morning_report() -> dict[str, Any]:
    """Pure aligned morning-report / autopilot block. Read-only; executes nothing."""
    r = build_automation_readiness_integration()
    return {
        "section": "candidate_lane_directive",
        "c16_lifecycle_complete": r["c16_lifecycle_complete"],
        "rejected_ledger_count": r["rejected_ledger_count"],
        "active_candidate": r["active_candidate"],
        "open_candidate_gate": r["open_candidate_gate"],
        "active_candidate_label": r["active_candidate_label"],
        "active_candidate_verdict": r["active_candidate_verdict"],
        "active_candidate_stage": r["active_candidate_stage"],
        "active_candidate_stage_label": r["active_candidate_stage_label"],
        "active_candidate_timeframe": r["active_candidate_timeframe"],
        "active_candidate_scope_note": r["active_candidate_scope_note"],
        "active_candidate_is_market_neutral": r["active_candidate_is_market_neutral"],
        "active_candidate_is_low_turnover": r["active_candidate_is_low_turnover"],
        "last_rejected_candidate": r["last_rejected_candidate"],
        "last_rejected_candidate_label": r["last_rejected_candidate_label"],
        "last_rejected_candidate_verdict": r["last_rejected_candidate_verdict"],
        "last_rejected_candidate_rejected_at":
            r["last_rejected_candidate_rejected_at"],
        "last_rejected_candidate_reason": r["last_rejected_candidate_reason"],
        "next_stage": r["next_stage"],
        "next_required_action": r["next_required_action"],
        "next_is_automation_readiness": r["next_is_automation_readiness"],
        "next_is_new_candidate": r["next_is_new_candidate"],
        "surfaces_agree": r["surfaces_agree"],
        "overnight_automation_research_only": r["overnight_automation_research_only"],
        "requires_human_approval": True,
        "executes_nothing": True,
    }


def validate_automation_readiness_integration(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the integration is research-only,
    integration-only, all surfaces AGREE on the lane directive (the same token, no
    new candidate), C16 complete + ledger 25 (C18/C20 at replay; C19 at labels), the
    automation path is research-only with downstream BLOCKED/LOCKED, and every
    capability flag is False."""
    failures: list = []
    if record.get("mode") != ARI_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_pure_integration_only") is not True:
        failures.append("not_pure_integration_only")

    if record.get("surfaces_agree") is not True:
        failures.append("surfaces_do_not_agree")
    if record.get("all_tokens_match") is not True:
        failures.append("tokens_do_not_match")
    if record.get("coordinator_matches_lane_directive") is not True:
        failures.append("coordinator_does_not_match_lane_directive")

    # the integration follows the lane's CURRENT directive: C21 is the ACTIVE open
    # candidate at the REAL-CANDLE LABELS review stage awaiting the human fee-honest
    # replay decision (NOT automation readiness and NOT a new candidate).
    if record.get("next_required_action") != (
            "HUMAN_DECISION_C21_ADVANCE_TO_FEE_HONEST_REPLAY_OR_REJECT"):
        failures.append("next_action_not_c21_gate")
    if record.get("active_candidate") != "C21":
        failures.append("active_candidate_not_c21")
    if record.get("open_candidate_gate") is not True:
        failures.append("open_candidate_gate_expected")
    if record.get("next_is_automation_readiness") is not False:
        failures.append("must_not_be_automation_readiness_while_c21_open")
    if record.get("c20_remains_rejected_not_rescued") is not True:
        failures.append("c20_must_remain_rejected_not_rescued")
    if record.get("next_is_new_candidate") is not False:
        failures.append("next_must_not_be_new_candidate")
    if record.get("no_new_candidate_recommended") is not True:
        failures.append("a_surface_recommends_new_candidate")

    if record.get("c16_lifecycle_complete") is not True:
        failures.append("c16_not_complete")
    if record.get("rejected_ledger_count") != 25:
        failures.append("ledger_not_25")

    # automation path research-only + downstream blocked/locked
    if record.get("automation_research_only") is not True:
        failures.append("automation_not_research_only")
    if record.get("downstream_blocked_and_locked") is not True:
        failures.append("downstream_not_blocked_locked")
    if record.get("real_data_qa_state") != _lane.STATE_BLOCKED:
        failures.append("real_data_qa_not_blocked")
    if record.get("replay_state") != _lane.STATE_BLOCKED:
        failures.append("replay_not_blocked")
    if record.get("paper_trading_state") != _lane.STATE_LOCKED:
        failures.append("paper_not_locked")
    if record.get("live_trading_state") != _lane.STATE_LOCKED:
        failures.append("live_not_locked")

    locks = record.get("scope_locks") or {}
    for key in ("no_execute", "no_detector", "no_labels", "no_replay", "no_pnl",
                "no_optimization", "no_data_fetch", "no_commit", "no_push",
                "no_new_candidate", "no_broker", "no_order_logic",
                "no_paper_trading", "no_live_trading", "no_gate_skip"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
