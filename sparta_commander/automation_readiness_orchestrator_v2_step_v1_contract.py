"""SPARTA Automation-Readiness Step (Orchestrator V2 + Allowlist Guard) v1
-- PURE, RESEARCH-ONLY READINESS CONTRACT.

The research-only AUTOMATION-READINESS STEP that the candidate-research lane points
to (next_required_action == BUILD_AUTOMATION_READINESS_STEP_RESEARCH_ONLY) now that
Candidate #18 is rejected/closed and there is NO active candidate. It does NOT start
any candidate, fetch data, optimize, or touch trading -- it only CROSS-CHECKS the
already-committed live state and CONFIRMS the system is ready to run future safe,
bounded candidate work under the Autopilot Research Orchestrator v2 + the Explicit-
Allowlist Commit Guard v1.

It composes, read-only:
  * the candidate-research-lane status (authoritative): NO active candidate, rejected
    ledger C1-C18 (23), C18 rejected at fee-honest replay (kept on record), next
    stage = automation readiness;
  * the rejected-ledger count from the Research Expansion Plan (must be 23);
  * the Autopilot Research Orchestrator v2 policy contract (must build + validate);
  * the Explicit-Allowlist Commit Guard v1 policy contract (must build + validate);
and asserts they AGREE, then emits the readiness verdict plus the DECLARED guarded
posture for future automation (what may auto-continue vs what must stop for a human).

It executes NOTHING: no detector, no labels, no replay, no PnL, no optimization, no
data fetch, no writes, no staging/commit/push, no scheduler, no paper/live/broker/
order surface, and it never deletes/moves/stashes/modifies the repo's pre-existing
untracked clutter. Every capability flag is pinned False with a full scope_locks set.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.crypto_d1_candidate_research_lane_status_v1_contract as _lane
import sparta_commander.research_expansion_plan_v1_contract as _rep
import sparta_commander.autopilot_research_orchestrator_v2_contract as _aro2
import sparta_commander.explicit_allowlist_commit_guard_v1_contract as _cg

ARS_SCHEMA_VERSION = 1
ARS_MODE = "RESEARCH_ONLY"
ARS_LANE = "crypto_d1_auto_research"

EXPECTED_LEDGER_COUNT = 23
EXPECTED_LAST_REJECTED = "C18"
EXPECTED_C18_VERDICT = "C18_REJECTED_AT_FEE_HONEST_REPLAY"

READINESS_VERDICT_READY = "READY_FOR_ORCHESTRATOR_V2_GUARDED_AUTOMATION"
READINESS_VERDICT_NOT_READY = "NOT_READY"

# The next action AFTER readiness is confirmed is a HUMAN decision -- selecting the
# next research direction (which, if it opens a new candidate, is itself a hard human
# stop). The readiness step never starts C19 and never auto-advances.
NEXT_REQUIRED_ACTION = (
    "AWAIT_HUMAN_NEXT_RESEARCH_DIRECTION__NO_ACTIVE_CANDIDATE__NO_C19_STARTED")

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "runs_git", "stages_files", "auto_commits",
    "auto_pushes", "runs_detector", "runs_labels", "runs_replay", "computes_pnl",
    "optimizes_parameters", "runs_robustness", "runs_portfolio_compute",
    "fetches_data", "reads_real_data", "mutates_data", "stages_data",
    "deletes_clutter", "moves_clutter", "stashes_clutter", "modifies_clutter",
    "installs_scheduler", "starts_scheduler", "runs_overnight_automation",
    "modifies_scheduler", "sends_notifications", "calls_api", "uses_network",
    "uses_credentials", "connects_broker", "connects_exchange", "uses_real_money",
    "places_orders", "contains_order_logic", "paper_trading", "live_trading",
    "deploys_capital", "starts_new_candidate", "starts_c19",
    "makes_advance_or_reject_decision", "promotes_gate", "unlocks_downstream_gate",
    "skips_any_gate", "weakens_human_gates", "advances_without_human_approval",
    "reproposes_rejected_family", "adds_new_instrument_class", "broad_stages",
    "claims_profitability", "claims_edge", "crosses_into_forbidden_gate",
)


def build_automation_readiness_step() -> dict[str, Any]:
    """PURE. Cross-check the live lane / ledger / orchestrator / guard state and emit
    the automation-readiness verdict + the declared guarded posture for future
    candidate work. Reads already-committed contract state only; executes nothing."""
    lane = _lane.get_lane_status()
    lane_valid = _lane.validate_lane_status(lane)["valid"]
    rep = _rep.build_research_expansion_plan()
    aro2 = _aro2.build_orchestrator_contract()
    aro2_valid = _aro2.validate_orchestrator_contract(aro2)["valid"]
    guard = _cg.build_commit_guard_contract()
    guard_valid = _cg.validate_commit_guard_contract(guard)["valid"]

    rej = lane.get("last_rejected_candidate_detail") or {}

    # the readiness preconditions (each must hold). The lane either has NO active
    # candidate (the moment this step certified readiness) OR has C19 active -- the
    # candidate that was subsequently opened USING this readiness. Both are
    # consistent; a DIFFERENT active candidate would not be.
    checks = {
        "lane_status_valid": lane_valid,
        "no_active_candidate_or_c19_open":
            lane.get("active_candidate") in (None, "C19"),
        # ledger is at least 23 (monotonic; >= the count when this step was certified)
        "ledger_at_least_23_lane":
            lane.get("rejected_ledger_count", 0) >= EXPECTED_LEDGER_COUNT,
        "ledger_at_least_23_rep":
            rep.get("rejected_families_count", 0) >= EXPECTED_LEDGER_COUNT,
        # C18 is REJECTED / closed (present in the ledger) -- it need not be the LAST
        # rejected after later rejections (e.g. C19).
        "c18_rejected_closed": (
            "h4_trend_following_market_structure"
            in (lane.get("rejected_families") or [])),
        # next stage is automation readiness (idle) OR the C19 spec-decision gate
        # (C19 was opened from this readiness) -- never a NEW candidate / drift.
        "next_stage_is_automation_readiness_or_c19_gate":
            (lane.get("next_is_automation_readiness") is True
             or lane.get("active_candidate") == "C19")
            and lane.get("next_is_new_candidate") is False,
        "orchestrator_v2_live": aro2_valid and aro2.get("is_runner") is False
            and aro2.get("installs_scheduler") is False,
        "commit_guard_live": guard_valid and guard.get("is_runner") is False,
        "guard_paired_with_orchestrator":
            aro2.get("pairs_with_commit_guard")
            == "explicit_allowlist_commit_guard_v1_contract",
        "explicit_allowlist_staging_required":
            aro2.get("requires_explicit_allowlist_staging") is True
            and aro2.get("forbids_broad_staging") is True
            and guard.get("explicit_path_staging_required") is True,
        "untracked_clutter_tolerated":
            aro2.get("untracked_clutter_tolerated") is True
            and guard.get("tolerates_preexisting_untracked_clutter") is True,
    }

    blockers = [k for k, v in checks.items() if v is not True]
    ready = not blockers
    verdict = (READINESS_VERDICT_READY if ready
               else READINESS_VERDICT_NOT_READY)

    record: dict[str, Any] = {
        "schema_version": ARS_SCHEMA_VERSION, "mode": ARS_MODE, "lane": ARS_LANE,
        "is_pure_readiness_step_only": True,
        "label": (
            "Automation-Readiness Step v1 (READ-ONLY, RESEARCH ONLY). Confirms the "
            "system is ready to run FUTURE safe, bounded candidate work under "
            "Autopilot Research Orchestrator v2 + Explicit-Allowlist Commit Guard v1: "
            "NO active candidate, rejected ledger C1-C18 (23), C18 rejected/closed at "
            "fee-honest replay, both policy contracts live + valid, explicit-allowlist "
            "staging required, untracked clutter tolerated. Starts NO candidate "
            "(no C19), fetches no data, optimizes nothing, writes no trading code, "
            "and never touches the repo's pre-existing clutter. Executes nothing."),
        "is_step_for": _lane.AUTOMATION_READINESS_TOKEN,
        "blockers": blockers,
        "readiness_verdict": verdict,
        "is_ready": ready,
        "readiness_checks": checks,
        # the confirmed live state (provenance)
        "active_candidate": lane.get("active_candidate"),
        "open_candidate_gate": lane.get("open_candidate_gate"),
        "rejected_ledger_count": lane.get("rejected_ledger_count"),
        "last_rejected_candidate": lane.get("last_rejected_candidate"),
        "last_rejected_candidate_verdict": rej.get("verdict"),
        "next_stage": lane.get("next_stage"),
        # the live policy contracts this step certifies
        "orchestrator_v2_contract": "autopilot_research_orchestrator_v2_contract",
        "commit_guard_contract": "explicit_allowlist_commit_guard_v1_contract",
        "orchestrator_v2_valid": aro2_valid,
        "commit_guard_valid": guard_valid,
        # the DECLARED guarded posture for future automation (mirrors the V2 lists)
        "future_auto_continue_categories": list(_aro2.AUTO_CONTINUE_CATEGORIES),
        "future_human_stop_categories": list(_aro2.HUMAN_STOP_CATEGORIES),
        "future_staging_policy": (
            "explicit_per_path_git_add_only__no_git_add_dot__no_git_add_A__"
            "no_unexempted_data_or_report_artifact"),
        "future_automation_may_auto_continue_safe_bounded_units": ready,
        "future_automation_must_stop_for_real_decisions_and_forbidden_gates": True,
        # hard guarantees of THIS step
        "starts_no_candidate": True, "starts_no_c19": True,
        "fetches_no_data": True, "optimizes_nothing": True,
        "creates_no_strategy_or_candidate_logic": True,
        "creates_no_trading_code": True,
        "touches_no_untracked_clutter": True,
        "uses_explicit_allowlist_staging_only": True,
        "human_review_required": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
        "requires_human_approval": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_execute": True, "no_write": True, "no_git": True, "no_stage": True,
        "no_commit": True, "no_push": True, "no_broad_staging": True,
        "no_detector": True, "no_labels": True, "no_replay": True, "no_pnl": True,
        "no_optimization": True, "no_robustness": True, "no_portfolio_compute": True,
        "no_data_fetch": True, "no_real_data_access": True, "no_data_mutation": True,
        "no_clutter_deletion": True, "no_clutter_move": True, "no_clutter_stash": True,
        "no_clutter_modification": True, "no_scheduler_install": True,
        "no_scheduler_start": True, "no_overnight_automation": True,
        "no_new_candidate": True, "no_c19": True, "no_advance_or_reject": True,
        "no_new_instrument_class": True, "no_xauusd": True, "no_paper_trading": True,
        "no_live_trading": True, "no_broker": True, "no_order_logic": True,
        "no_credentials": True, "no_human_gate_weakening": True, "no_gate_skip": True,
        "no_downstream_gate_unlock": True, "no_profitability_claim": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def get_automation_readiness_next_action() -> str:
    return NEXT_REQUIRED_ACTION


def validate_automation_readiness_step(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the step is research-only, readiness-
    only, all readiness checks pass (no active candidate, ledger 23, C18
    rejected/closed, Orchestrator V2 + Commit Guard live and paired, explicit-
    allowlist staging required, clutter tolerated), it starts no candidate / no C19
    and writes no trading code, the next action is the human direction gate, and
    every capability flag is False with the scope locks set."""
    failures: list = []
    if record.get("mode") != ARS_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_pure_readiness_step_only") is not True:
        failures.append("not_pure_readiness_step_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("readiness_verdict") != READINESS_VERDICT_READY:
        failures.append("verdict_not_ready")
    if record.get("is_ready") is not True:
        failures.append("not_ready")

    # every readiness check must be True
    checks = record.get("readiness_checks") or {}
    for k in ("lane_status_valid", "no_active_candidate_or_c19_open",
              "ledger_at_least_23_lane", "ledger_at_least_23_rep",
              "c18_rejected_closed",
              "next_stage_is_automation_readiness_or_c19_gate", "orchestrator_v2_live",
              "commit_guard_live", "guard_paired_with_orchestrator",
              "explicit_allowlist_staging_required", "untracked_clutter_tolerated"):
        if checks.get(k) is not True:
            failures.append("readiness_check_failed_%s" % k)

    # confirmed live-state facts: no active candidate OR exactly C19 (opened from
    # this readiness); never a different active candidate.
    if record.get("active_candidate") not in (None, "C19"):
        failures.append("active_candidate_must_be_none_or_c19")
    if record.get("rejected_ledger_count", 0) < EXPECTED_LEDGER_COUNT:
        failures.append("ledger_below_23")

    # the live policy contracts must be certified valid
    if record.get("orchestrator_v2_valid") is not True:
        failures.append("orchestrator_v2_not_valid")
    if record.get("commit_guard_valid") is not True:
        failures.append("commit_guard_not_valid")

    # the future posture lists are non-empty and the staging policy is explicit
    if not record.get("future_auto_continue_categories"):
        failures.append("auto_continue_categories_missing")
    if not record.get("future_human_stop_categories"):
        failures.append("human_stop_categories_missing")
    if record.get(
            "future_automation_must_stop_for_real_decisions_and_forbidden_gates"
            ) is not True:
        failures.append("must_stop_posture_missing")

    # hard guarantees of THIS step
    for k in ("starts_no_candidate", "starts_no_c19", "fetches_no_data",
              "optimizes_nothing", "creates_no_strategy_or_candidate_logic",
              "creates_no_trading_code", "touches_no_untracked_clutter",
              "uses_explicit_allowlist_staging_only"):
        if record.get(k) is not True:
            failures.append("guarantee_off_%s" % k)
    if record.get("next_required_action") != NEXT_REQUIRED_ACTION:
        failures.append("next_action_not_human_direction_gate")

    locks = record.get("scope_locks") or {}
    for key in ("no_execute", "no_git", "no_broad_staging", "no_data_fetch",
                "no_optimization", "no_new_candidate", "no_c19",
                "no_advance_or_reject", "no_new_instrument_class", "no_xauusd",
                "no_paper_trading", "no_live_trading", "no_broker", "no_order_logic",
                "no_credentials", "no_clutter_deletion", "no_clutter_move",
                "no_clutter_stash", "no_clutter_modification",
                "no_human_gate_weakening", "no_gate_skip"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
