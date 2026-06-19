"""SPARTA Guarded Orchestrator Executor v1 -- PURE, RESEARCH-ONLY AUTHORIZATION.

The authorization layer that sits on top of the Guarded Orchestrator Runner v1 (which
produces the dry-run plan), the Autopilot Research Orchestrator v2 (gate policy), and
the Explicit-Allowlist Commit Guard v1 (staging policy). Its job is to decide whether
an already-runner-APPROVED, explicitly HUMAN-authorized bounded research unit may be
EXECUTED -- and, if so, to emit the exact bounded command sequence -- so future Claude
runs need less manual copy/paste.

CRITICAL SAFETY POSTURE:
  * It is NOT a scheduler and never runs automatically / overnight.
  * It DEFAULTS TO DRY-RUN. Actual execution requires a SEPARATE explicit token
    (EXECUTION_TOKEN) AND explicit human authorization AND a runner-approved plan AND
    a clean live precheck AND green tests -- ALL of them.
  * This contract itself is PURE and executes NOTHING: it runs no git, shell, tests,
    fetch, scheduler, broker, or trading, and writes/deletes/moves/stashes/modifies
    no files. It re-derives the plan by RE-CALLING the dry-run runner (so a
    hand-edited plan cannot smuggle anything past it) and then returns an
    AUTHORIZATION DECISION plus the bounded command sequence a human (or a separately
    approved one-off executor) would run. NO real tool runner is shipped in V1.

It may authorize ONLY these bounded safe phases, in order:
  1. safety precheck
  2. run the declared tests
  3. explicit-path `git add` for the declared allowlist only
  4. `git commit` with the declared message
  5. `git push origin master`
  6. post-push verification (HEAD == origin/master, ahead/behind 0/0, clean tree)
  7. final report.

It REFUSES execution for: new-candidate / C19 start, advance/reject, fetch execution,
labels->replay advance, replay-verdict decisions, optimization/rescue/tuning, XAUUSD /
new instrument class, scheduler changes, credentials / private APIs, all paper/live/
broker/order/trading code, broad staging, unexpected files, un-exempted data/report
artifacts, a dirty tracked tree, SHA drift, and failing or un-run tests. Untracked
clutter is tolerated only under explicit-allowlist staging. Every capability flag is
pinned False with a full scope_locks set.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.guarded_orchestrator_runner_v1_contract as _gor
import sparta_commander.autopilot_research_orchestrator_v2_contract as _aro2
import sparta_commander.explicit_allowlist_commit_guard_v1_contract as _cg

GOE_SCHEMA_VERSION = 1
GOE_MODE = "RESEARCH_ONLY"
GOE_LANE = "crypto_d1_auto_research"

# Modes (default is dry-run; execution needs a separate explicit token).
MODE_DRY_RUN = "dry_run"
MODE_EXECUTE = "execute"
DEFAULT_MODE = MODE_DRY_RUN
ALL_MODES = (MODE_DRY_RUN, MODE_EXECUTE)

# The SEPARATE explicit token a human must supply to authorize real execution. Its
# presence alone is never sufficient -- the plan must also be runner-approved, the
# live precheck clean, and the tests green.
EXECUTION_TOKEN = "EXECUTE_APPROVED_BOUNDED_RESEARCH_UNIT_NOW"

# Authorization decisions (the COMPLETE allowlist).
DECISION_DRY_RUN = "DRY_RUN_PLAN_ONLY"
DECISION_AUTHORIZED_TO_EXECUTE = "AUTHORIZED_TO_EXECUTE"
DECISION_REFUSED = "REFUSED_STOP_FOR_HUMAN"
ALL_DECISIONS = (DECISION_DRY_RUN, DECISION_AUTHORIZED_TO_EXECUTE, DECISION_REFUSED)

# The only phases the executor may authorize, in order.
ALLOWED_EXECUTION_PHASES = (
    "safety_precheck",
    "run_declared_tests",
    "explicit_path_git_add_allowlist_only",
    "git_commit_declared_message",
    "git_push_origin_master",
    "post_push_verification",
    "final_report",
)

# Whether a real git-executing tool runner is shipped in V1 (it is NOT).
REAL_RUNNER_SHIPPED = False
TOOL_RUNNER_DISABLED_BY_DEFAULT = True

_CAPABILITY_FLAGS_FALSE = (
    "executes", "is_scheduler", "runs_automatically", "runs_overnight",
    "runs_git", "runs_shell", "runs_tests", "stages_files", "auto_commits",
    "auto_pushes", "writes_files", "deletes_files", "moves_files", "stashes_files",
    "modifies_clutter", "runs_detector", "runs_labels", "runs_replay", "computes_pnl",
    "optimizes_parameters", "runs_robustness", "fetches_data", "reads_real_data",
    "mutates_data", "stages_data", "installs_scheduler", "starts_scheduler",
    "modifies_scheduler", "runs_overnight_automation", "sends_notifications",
    "calls_api", "uses_network", "uses_credentials", "connects_broker",
    "connects_exchange", "uses_real_money", "places_orders", "contains_order_logic",
    "paper_trading", "live_trading", "deploys_capital", "starts_new_candidate",
    "starts_c19", "makes_advance_or_reject_decision", "broad_stages",
    "promotes_gate", "unlocks_downstream_gate", "skips_any_gate",
    "weakens_human_gates", "advances_without_human_approval",
    "adds_new_instrument_class", "executes_without_separate_token",
    "claims_profitability", "claims_edge", "crosses_into_forbidden_gate",
)


def _bounded_command_sequence(plan: dict) -> list:
    """Pure: the exact ordered commands the authorized phases map to, read straight
    from the runner's dry-run plan (declared strings, never executed here)."""
    ep = plan.get("execution_plan") or {}
    p3 = ep.get("phase_3_relevant_tests") or {}
    p4 = ep.get("phase_4_explicit_path_staging_plan") or {}
    p5 = ep.get("phase_5_commit_plan") or {}
    p6 = ep.get("phase_6_push_verification_plan") or {}
    return [
        {"phase": "safety_precheck",
         "action": "verify clean TRACKED tree, HEAD==origin/master, no mutating "
                   "shell, expected-files-only (clutter tolerated)"},
        {"phase": "run_declared_tests",
         "action": p3.get("command_to_run_by_hand")},
        {"phase": "explicit_path_git_add_allowlist_only",
         "action": p4.get("staging_command")},
        {"phase": "git_commit_declared_message",
         "action": "git commit -F %s" % (p5.get("commit_message_ref"))},
        {"phase": "git_push_origin_master",
         "action": p6.get("push")},
        {"phase": "post_push_verification",
         "action": "verify %s" % ", ".join(p6.get("verify") or [])},
        {"phase": "final_report",
         "action": "emit final report: %s"
                   % ", ".join(_gor.FINAL_REPORT_REQUIREMENTS)},
    ]


def authorize_execution(request: dict) -> dict[str, Any]:
    """PURE. Decide whether an explicitly human-authorized, runner-approved bounded
    research unit may be EXECUTED. Re-derives the plan by RE-CALLING the dry-run
    runner (anti-tamper), then gates on mode + the separate execution token + human
    authorization + clean precheck + green tests. Executes NOTHING -- it returns an
    authorization decision and the bounded command sequence; a human (or a separately
    approved one-off executor) still performs any real action.

    request = {
        "unit": {...},                 # the runner's research-unit descriptor
        "mode": "dry_run" | "execute", # default dry_run
        "human_authorized": bool,      # explicit human authorization
        "execution_token": str,        # must equal EXECUTION_TOKEN to execute
    }
    """
    request = request or {}
    unit = request.get("unit") or {}
    mode = request.get("mode") or DEFAULT_MODE
    human_authorized = bool(request.get("human_authorized"))
    execution_token = request.get("execution_token")

    # 1) re-derive the plan from the dry-run runner (do NOT trust a passed-in plan)
    plan = _gor.plan_bounded_research_unit(unit)
    plan_approved = plan.get("verdict") == _gor.VERDICT_PLAN_READY_DRY_RUN

    refusal_reasons: list = []
    if not plan_approved:
        refusal_reasons.extend(plan.get("refusal_reasons") or ["plan_not_approved"])

    # 2) independent re-checks of the safety-critical conditions (belt and braces)
    category = plan.get("category")
    if category in _aro2.HUMAN_STOP_CATEGORIES:
        refusal_reasons.append("human_stop_category__%s" % category)
    if plan.get("orchestrator_decision") != _aro2.VERDICT_AUTO_CONTINUE:
        refusal_reasons.append("orchestrator_not_auto_continue")
    if plan.get("guard_decision") != _cg.VERDICT_APPROVE_STAGING:
        refusal_reasons.append("guard_did_not_approve_staging")
    if plan.get("broad_staging_detected") is True:
        refusal_reasons.append("broad_staging_forbidden")

    refused = bool(refusal_reasons)

    # 3) mode + token + authorization gating (only reached when not refused)
    token_ok = execution_token == EXECUTION_TOKEN
    wants_execute = mode == MODE_EXECUTE
    authorized = (not refused and wants_execute and human_authorized and token_ok)

    if refused:
        decision = DECISION_REFUSED
    elif authorized:
        decision = DECISION_AUTHORIZED_TO_EXECUTE
    else:
        decision = DECISION_DRY_RUN  # safe default: plan only, do not execute

    # reasons we stayed in dry-run despite a safe plan (transparency)
    dry_run_reasons: list = []
    if not refused and not authorized:
        if not wants_execute:
            dry_run_reasons.append("mode_is_dry_run_default")
        if not human_authorized:
            dry_run_reasons.append("missing_human_authorization")
        if not token_ok:
            dry_run_reasons.append("missing_or_wrong_execution_token")

    record: dict[str, Any] = {
        "schema_version": GOE_SCHEMA_VERSION, "mode": GOE_MODE, "lane": GOE_LANE,
        "is_pure_authorization_only": True,
        "is_scheduler": False,
        "runs_automatically": False,
        "runs_overnight": False,
        "requested_mode": mode,
        "default_mode": DEFAULT_MODE,
        "decision": decision,
        "authorized_to_execute": decision == DECISION_AUTHORIZED_TO_EXECUTE,
        "is_dry_run": decision == DECISION_DRY_RUN,
        "refused": decision == DECISION_REFUSED,
        "refusal_reasons": refusal_reasons,
        "dry_run_reasons": dry_run_reasons,
        "plan_approved_by_runner": plan_approved,
        "category": category,
        "human_authorized": human_authorized,
        "execution_token_ok": token_ok,
        "execution_requires_separate_token": True,
        "allowed_phases": list(ALLOWED_EXECUTION_PHASES),
        # the bounded command sequence (declared strings; executed by nobody here)
        "bounded_command_sequence": _bounded_command_sequence(plan),
        "runner_plan_verdict": plan.get("verdict"),
        "untracked_clutter_tolerated_under_explicit_staging": True,
        "pairs_with_runner": "guarded_orchestrator_runner_v1_contract",
        "pairs_with_orchestrator_v2": "autopilot_research_orchestrator_v2_contract",
        "pairs_with_commit_guard": "explicit_allowlist_commit_guard_v1_contract",
        "real_runner_shipped": REAL_RUNNER_SHIPPED,
        "human_must_run_the_commands": True,
        "requires_human_approval": True,
        "executes_nothing": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = _scope_locks()
    return record


def _scope_locks() -> dict[str, Any]:
    return {
        "no_execute": True, "no_scheduler": True, "no_overnight": True,
        "no_auto_run": True, "no_git": True, "no_shell": True, "no_run_tests": True,
        "no_stage": True, "no_commit": True, "no_push": True, "no_write": True,
        "no_file_deletion": True, "no_file_move": True, "no_file_stash": True,
        "no_clutter_modification": True, "no_broad_staging": True,
        "no_git_add_dot": True, "no_git_add_all": True,
        "no_unexempted_data_artifact": True, "no_detector": True, "no_labels": True,
        "no_replay": True, "no_pnl": True, "no_optimization": True,
        "no_rescue_variant": True, "no_robustness": True, "no_data_fetch": True,
        "no_real_data_access": True, "no_data_mutation": True,
        "no_scheduler_install": True, "no_scheduler_change": True,
        "no_overnight_automation": True, "no_new_candidate": True, "no_c19": True,
        "no_advance_or_reject": True, "no_labels_to_replay_advance": True,
        "no_replay_verdict_decision": True, "no_new_instrument_class": True,
        "no_xauusd": True, "no_paper_trading": True, "no_live_trading": True,
        "no_broker": True, "no_order_logic": True, "no_credentials": True,
        "no_private_api": True, "no_execute_without_separate_token": True,
        "no_human_gate_weakening": True, "no_gate_skip": True,
        "no_downstream_gate_unlock": True, "no_profitability_claim": True,
        "no_crossing_into_forbidden_gate": True,
    }


def build_executor_contract() -> dict[str, Any]:
    """PURE. The declared executor authorization policy + locked capability posture.
    Ships NO real runner; authorizes / executes NOTHING by itself."""
    runner = _gor.build_runner_contract()
    runner_valid = _gor.validate_runner_contract(runner)["valid"]
    record: dict[str, Any] = {
        "schema_version": GOE_SCHEMA_VERSION, "mode": GOE_MODE, "lane": GOE_LANE,
        "is_pure_authorization_only": True,
        "is_scheduler": False,
        "runs_automatically": False,
        "runs_overnight": False,
        "default_mode": DEFAULT_MODE,
        "modes": list(ALL_MODES),
        "decisions": list(ALL_DECISIONS),
        "execution_requires_separate_token": True,
        "execution_token_name": "EXECUTION_TOKEN",
        "execution_requires_human_authorization": True,
        "execution_requires_runner_approved_plan": True,
        "execution_requires_clean_precheck_and_green_tests": True,
        "label": (
            "Guarded Orchestrator Executor v1 (READ-ONLY AUTHORIZATION, RESEARCH "
            "ONLY). Authorizes execution of an already runner-APPROVED, explicitly "
            "human-authorized bounded research unit and emits the bounded command "
            "sequence. NOT a scheduler; never runs automatically / overnight. "
            "DEFAULTS TO DRY-RUN -- real execution needs a SEPARATE explicit token "
            "AND human authorization AND a runner-approved plan AND a clean live "
            "precheck AND green tests. This contract executes nothing and ships no "
            "real runner; a human runs the commands. Refuses new-candidate/C19, "
            "advance/reject, fetch, labels->replay, replay verdicts, optimization/"
            "rescue, XAUUSD/new instrument class, scheduler changes, credentials/"
            "private APIs, all trading code, broad staging, unexpected files, "
            "data/report artifacts, dirty tree, SHA drift, and failing/un-run "
            "tests. Every capability flag is False."),
        "allowed_execution_phases": list(ALLOWED_EXECUTION_PHASES),
        "refuses_categories": list(_aro2.HUMAN_STOP_CATEGORIES),
        "refuses_broad_staging": True,
        "refuses_unexpected_files": True,
        "refuses_unexempted_data_or_report_artifacts": True,
        "refuses_dirty_tracked_tree": True,
        "refuses_sha_drift": True,
        "refuses_failing_or_unrun_tests": True,
        "requires_explicit_allowlist_staging": True,
        "tolerates_untracked_clutter_only_with_explicit_allowlist_staging": True,
        "default_dry_run": True,
        "real_runner_shipped": REAL_RUNNER_SHIPPED,
        "tool_runner_disabled_by_default": TOOL_RUNNER_DISABLED_BY_DEFAULT,
        "pairs_with_runner": "guarded_orchestrator_runner_v1_contract",
        "pairs_with_orchestrator_v2": "autopilot_research_orchestrator_v2_contract",
        "pairs_with_commit_guard": "explicit_allowlist_commit_guard_v1_contract",
        "runner_valid": runner_valid,
        "does_not_weaken_human_gates": True,
        "human_must_run_the_commands": True,
        "human_review_required": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = _scope_locks()
    return record


def validate_executor_contract(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the executor is research-only,
    authorization-only, NOT a scheduler and never auto/overnight, defaults to
    dry-run, requires a separate execution token + human authorization + a runner-
    approved plan + clean precheck + green tests, authorizes only the 7 bounded
    phases, refuses the full human-stop set + staging hazards + dirty tree / SHA
    drift / failing tests, requires explicit-allowlist staging, ships no real runner
    by default, pairs with the runner (certified valid), does not weaken human gates,
    and pins every capability flag False with the scope locks set."""
    failures: list = []
    if record.get("mode") != GOE_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_pure_authorization_only") is not True:
        failures.append("not_pure_authorization_only")
    for k in ("is_scheduler", "runs_automatically", "runs_overnight"):
        if record.get(k) is not False:
            failures.append("must_be_false_%s" % k)

    if record.get("default_mode") != MODE_DRY_RUN:
        failures.append("default_mode_not_dry_run")
    if record.get("default_dry_run") is not True:
        failures.append("default_dry_run_off")
    for k in ("execution_requires_separate_token",
              "execution_requires_human_authorization",
              "execution_requires_runner_approved_plan",
              "execution_requires_clean_precheck_and_green_tests"):
        if record.get(k) is not True:
            failures.append("execution_gate_off_%s" % k)

    # the 7 bounded phases
    if list(record.get("allowed_execution_phases") or []) != list(
            ALLOWED_EXECUTION_PHASES):
        failures.append("allowed_phases_tampered")

    # refuses the full human-stop set + staging hazards + state hazards
    if set(record.get("refuses_categories") or []) != set(
            _aro2.HUMAN_STOP_CATEGORIES):
        failures.append("refuse_categories_tampered")
    for k in ("refuses_broad_staging", "refuses_unexpected_files",
              "refuses_unexempted_data_or_report_artifacts",
              "refuses_dirty_tracked_tree", "refuses_sha_drift",
              "refuses_failing_or_unrun_tests",
              "requires_explicit_allowlist_staging",
              "tolerates_untracked_clutter_only_with_explicit_allowlist_staging",
              "does_not_weaken_human_gates", "human_must_run_the_commands"):
        if record.get(k) is not True:
            failures.append("policy_flag_off_%s" % k)

    # ships no real runner by default
    if record.get("real_runner_shipped") is not False:
        failures.append("real_runner_must_not_be_shipped_by_default")
    if record.get("tool_runner_disabled_by_default") is not True:
        failures.append("tool_runner_not_disabled_by_default")

    # pairing certified
    if record.get("pairs_with_runner") != "guarded_orchestrator_runner_v1_contract":
        failures.append("runner_pairing_missing")
    if record.get("pairs_with_commit_guard") != (
            "explicit_allowlist_commit_guard_v1_contract"):
        failures.append("guard_pairing_missing")
    if record.get("runner_valid") is not True:
        failures.append("runner_not_valid")

    locks = record.get("scope_locks") or {}
    for key in ("no_execute", "no_scheduler", "no_overnight", "no_auto_run",
                "no_git", "no_shell", "no_run_tests", "no_stage", "no_commit",
                "no_push", "no_file_deletion", "no_broad_staging",
                "no_unexempted_data_artifact", "no_data_fetch", "no_optimization",
                "no_rescue_variant", "no_new_candidate", "no_c19",
                "no_advance_or_reject", "no_replay_verdict_decision",
                "no_new_instrument_class", "no_xauusd", "no_paper_trading",
                "no_live_trading", "no_broker", "no_credentials", "no_private_api",
                "no_execute_without_separate_token", "no_scheduler_change",
                "no_human_gate_weakening", "no_gate_skip"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
