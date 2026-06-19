"""SPARTA Automation Readiness -- RESEARCH-PREP SPEC v1 (PURE, RESEARCH ONLY).

Defines what the overnight automation is ALLOWED to do next for research-only
strategy discovery now that the candidate-research lane is complete through C16.
The goal is NOT live trading and NOT autonomous candidate creation: it is to let
the overnight automation safely produce BETTER research / candidate-prep output for
the next morning -- still human-gated, still research-only.

It composes the candidate-research-lane status + the automation-readiness bundle
integration (read-only) and declares:
  * the existing safe overnight tasks (integrity audit, contract-certification
    sweep, safety-test report, seed research brief draft),
  * the ADDITIVE next research-prep actions the overnight run may produce
    (advisory drafts only: a rejected-ledger lessons memo, evidence summaries, and
    a render of the automation-readiness surfaces), and
  * the FORBIDDEN actions (new candidate creation, detector/labels/replay/PnL/
    optimization/data-fetch/relabel, and any paper/live/broker/order/auto-commit/
    auto-push).

It executes NOTHING. Every capability flag is pinned False with a full scope_locks
set. The run-record next human gate, the morning report, the coordinator, the lane
status, and the integration all agree on BUILD_AUTOMATION_READINESS_STEP_RESEARCH_
ONLY.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.crypto_d1_candidate_research_lane_status_v1_contract as _lane
import sparta_commander.automation_readiness_bundle_integration_v1_contract as _ari

ARP_VERSION = "v1"
ARP_MODE = "RESEARCH_ONLY"
ARP_LANE = "crypto_d1_auto_research"

NEXT_REQUIRED_ACTION = _lane.AUTOMATION_READINESS_TOKEN  # this stage's action
# The value the overnight runner's run-record next_human_gate must now carry
# (kept in sync; verified against tools/overnight_autopilot_run_once.py by test).
RUN_RECORD_NEXT_HUMAN_GATE = NEXT_REQUIRED_ACTION

# Existing safe overnight tasks (already approved, research-only).
ALLOWED_OVERNIGHT_TASKS_RESEARCH_ONLY = (
    "integrity_audit",
    "contract_certification_sweep",
    "safety_test_suite_report",
    "seed_research_brief_draft",
)

# Additive next research-prep actions the overnight run MAY produce: advisory
# DRAFTS only, assembled from already-frozen evidence/state. They propose; the
# human decides. None of them build, fetch, replay, or trade anything.
ALLOWED_NEXT_RESEARCH_PREP_ACTIONS = (
    "rejected_ledger_lessons_memo_draft",   # distil C1-C16 lessons (advisory)
    "evidence_summary_draft",               # summarize frozen evidence (advisory)
    "automation_readiness_status_render",   # render the readiness surfaces
)

# Hard-forbidden overnight actions (structural; never unlocked here).
FORBIDDEN_OVERNIGHT_ACTIONS = (
    "create_new_candidate", "run_detector", "run_labels", "run_replay",
    "compute_pnl", "optimize_parameters", "fetch_data", "relabel",
    "paper_trade", "live_trade", "broker_order", "place_order",
    "auto_commit", "auto_push",
)

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "creates_new_candidate", "runs_detector",
    "runs_labels", "runs_replay", "computes_pnl", "optimizes_parameters",
    "relabels", "fetches_data", "reads_real_data", "mutates_data", "stages_data",
    "auto_commits", "auto_pushes", "modifies_scheduler", "starts_scheduler",
    "sends_notifications", "calls_api", "uses_network", "uses_credentials",
    "connects_broker", "connects_exchange", "uses_real_money", "places_orders",
    "contains_order_logic", "paper_trading", "live_trading", "deploys_capital",
    "promotes_gate", "unlocks_downstream_gate", "skips_any_gate",
    "advances_without_human_approval", "authorizes_autonomous_trading",
    "claims_profitability", "claims_edge", "crosses_into_forbidden_gate",
)


def safety_posture() -> dict[str, Any]:
    return {
        "mode": ARP_MODE, "read_only": True, "executes": False,
        "human_approval_required": True, "goal_is_live_trading": False,
        "goal_is_autonomous_candidate_creation": False,
        "goal": ("safely improve overnight research/candidate-prep output for the "
                 "next morning, still human-gated and research-only"),
        "overnight_automation_research_only": True,
    }


def build_automation_readiness_research_prep() -> dict[str, Any]:
    """Assemble the frozen automation-readiness research-prep spec. Pure; composes
    the lane status + integration (read-only). Executes nothing."""
    lane = _lane.get_lane_status()
    integ = _ari.build_automation_readiness_integration()

    record: dict[str, Any] = {
        "version": ARP_VERSION, "mode": ARP_MODE, "lane": ARP_LANE,
        "is_pure_prep_spec_only": True,
        "label": (
            "Automation Readiness research-prep spec v1 (READ-ONLY, RESEARCH "
            "ONLY). Defines the safe, human-gated, research-only next steps the "
            "overnight automation may take to improve candidate-prep output -- NOT "
            "live trading, NOT autonomous candidate creation. Executes nothing."),
        "goal_is_live_trading": False,
        "goal_is_autonomous_candidate_creation": False,
        # C16 completion + ledger (from the lane)
        "c16_lifecycle_complete": lane.get("c16_lifecycle_complete"),
        "rejected_ledger_count": lane.get("rejected_ledger_count"),
        # the aligned directive (all surfaces agree)
        "next_required_action": NEXT_REQUIRED_ACTION,
        "run_record_next_human_gate": RUN_RECORD_NEXT_HUMAN_GATE,
        "surfaces_agree": integ.get("surfaces_agree"),
        "next_is_new_candidate": False,
        # what overnight automation may / may not do
        "allowed_overnight_tasks_research_only":
            list(ALLOWED_OVERNIGHT_TASKS_RESEARCH_ONLY),
        "allowed_next_research_prep_actions":
            list(ALLOWED_NEXT_RESEARCH_PREP_ACTIONS),
        "forbidden_overnight_actions": list(FORBIDDEN_OVERNIGHT_ACTIONS),
        "all_next_actions_are_advisory_human_gated": True,
        # posture + downstream locks (from the lane)
        "overnight_automation_research_only": lane.get(
            "overnight_automation_research_only"),
        "real_data_qa_state": lane.get("real_data_qa_state"),
        "replay_state": lane.get("replay_state"),
        "paper_trading_state": lane.get("paper_trading_state"),
        "live_trading_state": lane.get("live_trading_state"),
        "safety_posture": safety_posture(),
        "human_review_required": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_execute": True, "no_write": True, "no_new_candidate": True,
        "no_detector": True, "no_labels": True, "no_replay": True, "no_pnl": True,
        "no_optimization": True, "no_relabel": True, "no_data_fetch": True,
        "no_real_data_access": True, "no_stage": True, "no_commit": True,
        "no_push": True, "no_auto_commit": True, "no_auto_push": True,
        "no_scheduler_change": True, "no_broker": True, "no_credentials": True,
        "no_order_logic": True, "no_paper_trading": True, "no_live_trading": True,
        "no_autonomous_trading": True, "no_gate_skip": True,
        "no_downstream_gate_unlock": True, "no_profitability_claim": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def summarize_for_morning_report() -> dict[str, Any]:
    """Pure morning-report-ready prep block. Read-only; executes nothing."""
    r = build_automation_readiness_research_prep()
    return {
        "section": "automation_readiness_research_prep",
        "c16_lifecycle_complete": r["c16_lifecycle_complete"],
        "rejected_ledger_count": r["rejected_ledger_count"],
        "next_required_action": r["next_required_action"],
        "run_record_next_human_gate": r["run_record_next_human_gate"],
        "allowed_next_research_prep_actions": r["allowed_next_research_prep_actions"],
        "next_is_new_candidate": r["next_is_new_candidate"],
        "overnight_automation_research_only": r["overnight_automation_research_only"],
        "goal_is_live_trading": r["goal_is_live_trading"],
        "requires_human_approval": True,
        "executes_nothing": True,
    }


def validate_automation_readiness_research_prep(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the prep is research-only, prep-spec-
    only, keeps C16 complete + ledger 21 + the automation-readiness directive (run-
    record gate aligned, no new candidate), forbids the unsafe action set, keeps
    overnight research-only with downstream BLOCKED/LOCKED, and pins every
    capability flag False."""
    failures: list = []
    if record.get("mode") != ARP_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_pure_prep_spec_only") is not True:
        failures.append("not_pure_prep_spec_only")

    # goal is not trading / not autonomous candidate creation
    if record.get("goal_is_live_trading") is not False:
        failures.append("goal_must_not_be_live_trading")
    if record.get("goal_is_autonomous_candidate_creation") is not False:
        failures.append("goal_must_not_be_autonomous_candidate")

    # C16 complete + ledger 23 (C17 and C18 both rejected at fee-honest replay)
    if record.get("c16_lifecycle_complete") is not True:
        failures.append("c16_not_complete")
    if record.get("rejected_ledger_count") != 23:
        failures.append("ledger_not_23")

    # aligned directive (all surfaces agree, run-record gate aligned, no candidate)
    if record.get("next_required_action") != NEXT_REQUIRED_ACTION:
        failures.append("next_action_not_automation_readiness")
    if record.get("run_record_next_human_gate") != RUN_RECORD_NEXT_HUMAN_GATE:
        failures.append("run_record_gate_not_aligned")
    if record.get("run_record_next_human_gate") == (
            "HUMAN_DECISION_ON_NEXT_CANDIDATE_FAMILY"):
        failures.append("run_record_gate_still_next_candidate")
    if record.get("surfaces_agree") is not True:
        failures.append("surfaces_do_not_agree")
    if record.get("next_is_new_candidate") is not False:
        failures.append("next_must_not_be_new_candidate")

    # allowed vs forbidden action sets
    if record.get("all_next_actions_are_advisory_human_gated") is not True:
        failures.append("next_actions_not_advisory_human_gated")
    forb = record.get("forbidden_overnight_actions") or []
    for must_forbid in ("create_new_candidate", "run_replay", "compute_pnl",
                        "fetch_data", "paper_trade", "live_trade", "broker_order",
                        "auto_commit", "auto_push"):
        if must_forbid not in forb:
            failures.append("forbidden_action_missing_%s" % must_forbid)
    allowed = record.get("allowed_next_research_prep_actions") or []
    for bad in ("create_new_candidate", "run_replay", "fetch_data", "paper_trade",
                "live_trade", "broker_order"):
        if bad in allowed:
            failures.append("unsafe_action_in_allowed_%s" % bad)

    # overnight research-only + downstream blocked/locked
    if record.get("overnight_automation_research_only") is not True:
        failures.append("overnight_not_research_only")
    if record.get("real_data_qa_state") != _lane.STATE_BLOCKED:
        failures.append("real_data_qa_not_blocked")
    if record.get("replay_state") != _lane.STATE_BLOCKED:
        failures.append("replay_not_blocked")
    if record.get("paper_trading_state") != _lane.STATE_LOCKED:
        failures.append("paper_not_locked")
    if record.get("live_trading_state") != _lane.STATE_LOCKED:
        failures.append("live_not_locked")

    locks = record.get("scope_locks") or {}
    for key in ("no_execute", "no_new_candidate", "no_detector", "no_labels",
                "no_replay", "no_pnl", "no_optimization", "no_data_fetch",
                "no_commit", "no_push", "no_broker", "no_order_logic",
                "no_paper_trading", "no_live_trading", "no_autonomous_trading",
                "no_gate_skip"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
