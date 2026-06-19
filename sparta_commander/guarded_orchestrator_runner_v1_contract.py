"""SPARTA Guarded Orchestrator Runner v1 -- PURE, RESEARCH-ONLY, DRY-RUN / PLANNING.

A thin, pure planning layer that turns the Autopilot Research Orchestrator v2 policy
+ the Explicit-Allowlist Commit Guard v1 policy into a ready-to-follow EXECUTION PLAN
for a single bounded research unit -- so future Claude runs need less manual
copy/paste. For V1 it is STRICTLY DRY-RUN / PLANNING: it GENERATES the plan as data
and EXECUTES NOTHING. It runs no git, no shell, no tests, no fetch, no scheduler, no
broker/trading, and deletes/moves/stashes/modifies no files (and no untracked
clutter). A human (or a separately-approved executor) still performs every actual
build / test / `git add` / commit / push.

Given a DECLARED research-unit descriptor it composes:
  * Orchestrator v2 `decide_orchestrator_step` (auto-continue vs human-stop gate), and
  * Commit Guard `evaluate_staging_plan` (explicit-allowlist, artifact-free staging),
and either:
  * REFUSES (STOP_FOR_HUMAN) with the aggregated reasons, or
  * emits an APPROVED 7-phase dry-run plan:
      1. safety precheck
      2. expected-files allowlist
      3. relevant tests
      4. explicit-path staging plan
      5. commit plan
      6. push verification plan
      7. final-report requirements.

It REFUSES (never plans an auto-run) for: starting a new candidate / C19,
advance/reject decisions, fetch execution, labels->replay advance, replay-verdict
decisions, optimization/rescue/tuning, XAUUSD / any new instrument class, scheduler
changes, credentials / private APIs, any paper/live/broker/order/trading code, broad
staging (`git add .` / `-A` ...), unexpected files outside the allowlist, and
un-exempted data/report artifacts. Pre-existing untracked clutter is tolerated ONLY
because staging is explicit per-path. Every capability flag is pinned False with a
full scope_locks set.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.autopilot_research_orchestrator_v2_contract as _aro2
import sparta_commander.explicit_allowlist_commit_guard_v1_contract as _cg

GOR_SCHEMA_VERSION = 1
GOR_MODE = "RESEARCH_ONLY"
GOR_LANE = "crypto_d1_auto_research"

# Runner verdicts (the COMPLETE allowlist).
VERDICT_PLAN_READY_DRY_RUN = "PLAN_READY_DRY_RUN"
VERDICT_REFUSED_STOP_FOR_HUMAN = "REFUSED_STOP_FOR_HUMAN"
ALL_VERDICTS = (VERDICT_PLAN_READY_DRY_RUN, VERDICT_REFUSED_STOP_FOR_HUMAN)

# The standard scoped test invocation (declared as a STRING to run by hand; the
# runner never executes it).
TEST_COMMAND_TEMPLATE = ("python -m pytest %s -q -p no:cacheprovider "
                         "--rootdir=tests")

# The fields a final report must contain (declared requirement, not produced here).
FINAL_REPORT_REQUIREMENTS = (
    "files_changed", "tests_run_and_result", "commit_hash", "push_result",
    "head_equals_origin_master", "ahead_behind_zero_zero", "what_was_planned",
    "what_was_refused",
)

_CAPABILITY_FLAGS_FALSE = (
    "executes", "is_live_runner", "runs_git", "runs_shell", "runs_tests",
    "stages_files", "auto_commits", "auto_pushes", "writes_files", "deletes_files",
    "moves_files", "stashes_files", "modifies_clutter", "runs_detector",
    "runs_labels", "runs_replay", "computes_pnl", "optimizes_parameters",
    "runs_robustness", "fetches_data", "reads_real_data", "mutates_data",
    "stages_data", "installs_scheduler", "starts_scheduler",
    "runs_overnight_automation", "modifies_scheduler", "sends_notifications",
    "calls_api", "uses_network", "uses_credentials", "connects_broker",
    "connects_exchange", "uses_real_money", "places_orders", "contains_order_logic",
    "paper_trading", "live_trading", "deploys_capital", "starts_new_candidate",
    "starts_c19", "makes_advance_or_reject_decision", "broad_stages",
    "promotes_gate", "unlocks_downstream_gate", "skips_any_gate",
    "weakens_human_gates", "advances_without_human_approval",
    "adds_new_instrument_class", "claims_profitability", "claims_edge",
    "crosses_into_forbidden_gate",
)


def _test_command(test_files: list) -> str:
    files = " ".join(str(t) for t in (test_files or [])) or "<relevant test files>"
    return TEST_COMMAND_TEMPLATE % files


def plan_bounded_research_unit(unit: dict) -> dict[str, Any]:
    """PURE / DRY-RUN. Given a DECLARED bounded-research-unit descriptor, compose the
    Orchestrator v2 gate decision and the Commit Guard staging evaluation and return
    either a REFUSAL (with aggregated reasons) or an APPROVED 7-phase dry-run
    execution plan. Executes NOTHING -- the human still performs every step.

    unit = {
        "category": <aro2 auto-continue OR human-stop category>,
        "description": str,
        "expected_files": [<path>, ...],         # the declared allowlist
        "relevant_tests": [<test path>, ...],
        "precheck": {clean_working_tree, head_equals_origin_master,
                     no_mutating_shell_pending, expected_files_only},
        "tests": {"ran": bool, "passed": bool},  # declared intent/result snapshot
        "staging_command": "git add <path> [<path> ...]",
        "staged_files": [<path>, ...],
        "exemptions": [{"path": <path>, "reviewed_contract": <name>}, ...],
        "commit_message_ref": <path to message file>,
        "untracked_clutter_present": bool,        # informational; tolerated
    }
    """
    unit = unit or {}
    category = unit.get("category")
    expected_files = [str(f) for f in (unit.get("expected_files") or [])]
    relevant_tests = [str(t) for t in (unit.get("relevant_tests") or [])]
    precheck = unit.get("precheck") or {}
    tests = unit.get("tests") or {}
    staging_command = unit.get("staging_command") or ""
    staged_files = [str(f) for f in (unit.get("staged_files") or [])]
    exemptions = unit.get("exemptions") or []
    commit_message_ref = unit.get("commit_message_ref")

    # 1) Commit Guard: explicit-allowlist, artifact-free staging
    guard_plan = {
        "staging_command": staging_command,
        "expected_files": expected_files,
        "staged_files": staged_files,
        "exemptions": exemptions,
        "untracked_clutter_present": bool(unit.get("untracked_clutter_present")),
    }
    guard = _cg.evaluate_staging_plan(guard_plan)

    # 2) Orchestrator v2: gate decision (auto-continue vs human-stop)
    scoped_diff = {
        "only_expected_files": len(guard["staged_files_outside_allowlist"]) == 0,
        "contains_data_artifact": len(guard["artifacts_blocked"]) > 0,
    }
    orch_step = {
        "category": category,
        "precheck": precheck,
        "tests": tests,
        "scoped_diff": scoped_diff,
        "staging_command": staging_command,
        "intends_commit": True,
        "intends_push": True,
    }
    orch = _aro2.decide_orchestrator_step(orch_step)

    # aggregate refusal reasons (the union of both policy layers)
    reasons = list(orch["reasons"]) + [
        "guard__%s" % r for r in guard["reasons"]]
    refuse = (orch["verdict"] == _aro2.VERDICT_STOP_FOR_HUMAN
              or guard["verdict"] == _cg.VERDICT_STOP_FOR_HUMAN
              or not expected_files)
    if not expected_files and "no_expected_files_declared" not in reasons:
        reasons.append("no_expected_files_declared")

    verdict = (VERDICT_REFUSED_STOP_FOR_HUMAN if refuse
               else VERDICT_PLAN_READY_DRY_RUN)

    # 3) Build the 7-phase dry-run plan (only meaningful when not refused, but always
    # returned so the human sees exactly what WOULD run).
    execution_plan = {
        "phase_1_safety_precheck": {
            "required": list(_aro2.REQUIRED_PRECHECKS),
            "declared": dict(precheck),
            "failures": orch["precheck_failures"],
            "note": ("clean_working_tree means a clean TRACKED tree; pre-existing "
                     "untracked clutter is tolerated under explicit-path staging"),
        },
        "phase_2_expected_files_allowlist": {
            "expected_files": expected_files,
            "must_declare_before_staging": True,
        },
        "phase_3_relevant_tests": {
            "test_files": relevant_tests,
            "command_to_run_by_hand": _test_command(relevant_tests),
            "must_pass_before_commit": True,
        },
        "phase_4_explicit_path_staging_plan": {
            "staging_command": staging_command,
            "explicit_path_only": True,
            "broad_staging_forbidden": True,
            "guard_verdict": guard["verdict"],
            "staged_outside_allowlist": guard["staged_files_outside_allowlist"],
            "artifacts_blocked": guard["artifacts_blocked"],
        },
        "phase_5_commit_plan": {
            "commit_message_ref": commit_message_ref,
            "commit_only_expected_files": True,
            "method": "git commit -F <message-file>",
        },
        "phase_6_push_verification_plan": {
            "push": "git push origin master",
            "verify": ["HEAD == origin/master", "ahead/behind == 0/0",
                       "tracked tree clean"],
        },
        "phase_7_final_report_requirements": list(FINAL_REPORT_REQUIREMENTS),
    }

    record: dict[str, Any] = {
        "schema_version": GOR_SCHEMA_VERSION, "mode": GOR_MODE, "lane": GOR_LANE,
        "is_dry_run_only": True,
        "is_pure_planning_only": True,
        "executes_anything": False,
        "category": category,
        "description": unit.get("description"),
        "verdict": verdict,
        "plan_ready": verdict == VERDICT_PLAN_READY_DRY_RUN,
        "refused": verdict == VERDICT_REFUSED_STOP_FOR_HUMAN,
        "refusal_reasons": reasons if refuse else [],
        "orchestrator_decision": orch["verdict"],
        "guard_decision": guard["verdict"],
        "broad_staging_detected": guard["broad_staging_detected"],
        "untracked_clutter_tolerated": True,
        "execution_plan": execution_plan,
        "pairs_with_orchestrator_v2": "autopilot_research_orchestrator_v2_contract",
        "pairs_with_commit_guard": "explicit_allowlist_commit_guard_v1_contract",
        "human_must_execute_every_step": True,
        "requires_human_approval": True,
        "executes_nothing": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = _scope_locks()
    return record


def _scope_locks() -> dict[str, Any]:
    return {
        "no_execute": True, "no_git": True, "no_shell": True, "no_run_tests": True,
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
        "no_private_api": True, "no_human_gate_weakening": True, "no_gate_skip": True,
        "no_downstream_gate_unlock": True, "no_profitability_claim": True,
        "no_crossing_into_forbidden_gate": True,
    }


def build_runner_contract() -> dict[str, Any]:
    """PURE. The declared dry-run runner policy + locked capability posture. Plans /
    runs / stages / commits / pushes NOTHING."""
    aro2 = _aro2.build_orchestrator_contract()
    aro2_valid = _aro2.validate_orchestrator_contract(aro2)["valid"]
    guard = _cg.build_commit_guard_contract()
    guard_valid = _cg.validate_commit_guard_contract(guard)["valid"]
    record: dict[str, Any] = {
        "schema_version": GOR_SCHEMA_VERSION, "mode": GOR_MODE, "lane": GOR_LANE,
        "is_dry_run_only": True,
        "is_pure_planning_only": True,
        "is_live_runner": False,
        "executes_anything": False,
        "label": (
            "Guarded Orchestrator Runner v1 (READ-ONLY, RESEARCH ONLY, DRY-RUN). "
            "Turns the Orchestrator v2 + Explicit-Allowlist Commit Guard policy into "
            "a ready-to-follow 7-phase execution PLAN (precheck / allowlist / tests / "
            "explicit-path staging / commit / push-verify / report) for one bounded "
            "research unit. V1 is strictly planning: it executes nothing -- no git, "
            "shell, tests, fetch, scheduler, broker, trading, or file deletion. It "
            "REFUSES to plan an auto-run for new-candidate/C19 starts, advance/reject, "
            "fetch, labels->replay, replay verdicts, optimization/rescue, XAUUSD / new "
            "instrument classes, scheduler changes, credentials/private APIs, all "
            "trading code, broad staging, unexpected files, and un-exempted data/"
            "report artifacts. Untracked clutter is tolerated only under explicit-path "
            "staging. Every capability flag is False."),
        "verdicts": list(ALL_VERDICTS),
        "plans_seven_phases": list((
            "safety_precheck", "expected_files_allowlist", "relevant_tests",
            "explicit_path_staging_plan", "commit_plan", "push_verification_plan",
            "final_report_requirements")),
        "final_report_requirements": list(FINAL_REPORT_REQUIREMENTS),
        "refuses_categories": list(_aro2.HUMAN_STOP_CATEGORIES),
        "refuses_broad_staging": True,
        "refuses_unexpected_files": True,
        "refuses_unexempted_data_or_report_artifacts": True,
        "tolerates_untracked_clutter_only_with_explicit_allowlist_staging": True,
        "explicit_path_staging_required": True,
        "pairs_with_orchestrator_v2": "autopilot_research_orchestrator_v2_contract",
        "pairs_with_commit_guard": "explicit_allowlist_commit_guard_v1_contract",
        "orchestrator_v2_valid": aro2_valid,
        "commit_guard_valid": guard_valid,
        "does_not_weaken_human_gates": True,
        "human_must_execute_every_step": True,
        "human_review_required": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = _scope_locks()
    return record


def validate_runner_contract(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the runner is research-only, dry-run /
    planning only (not a live runner, executes nothing), plans the full 7 phases,
    refuses the full human-stop category set + broad staging + unexpected files +
    un-exempted artifacts, tolerates clutter only under explicit-allowlist staging,
    pairs with both policy contracts (both certified valid), does not weaken human
    gates, and pins every capability flag False with the scope locks set."""
    failures: list = []
    if record.get("mode") != GOR_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_dry_run_only") is not True:
        failures.append("not_dry_run_only")
    if record.get("is_pure_planning_only") is not True:
        failures.append("not_pure_planning_only")
    if record.get("is_live_runner") is not False:
        failures.append("must_not_be_live_runner")
    if record.get("executes_anything") is not False:
        failures.append("must_execute_nothing")

    # plans the 7 phases
    if len(record.get("plans_seven_phases") or []) != 7:
        failures.append("seven_phases_tampered")
    if set(record.get("final_report_requirements") or []) != set(
            FINAL_REPORT_REQUIREMENTS):
        failures.append("final_report_requirements_tampered")

    # refuses the full human-stop set + the staging hazards
    if set(record.get("refuses_categories") or []) != set(
            _aro2.HUMAN_STOP_CATEGORIES):
        failures.append("refuse_categories_tampered")
    for k in ("refuses_broad_staging", "refuses_unexpected_files",
              "refuses_unexempted_data_or_report_artifacts",
              "tolerates_untracked_clutter_only_with_explicit_allowlist_staging",
              "explicit_path_staging_required", "does_not_weaken_human_gates",
              "human_must_execute_every_step"):
        if record.get(k) is not True:
            failures.append("policy_flag_off_%s" % k)

    # pairing certified
    if record.get("pairs_with_orchestrator_v2") != (
            "autopilot_research_orchestrator_v2_contract"):
        failures.append("orchestrator_pairing_missing")
    if record.get("pairs_with_commit_guard") != (
            "explicit_allowlist_commit_guard_v1_contract"):
        failures.append("guard_pairing_missing")
    if record.get("orchestrator_v2_valid") is not True:
        failures.append("orchestrator_v2_not_valid")
    if record.get("commit_guard_valid") is not True:
        failures.append("commit_guard_not_valid")

    locks = record.get("scope_locks") or {}
    for key in ("no_execute", "no_git", "no_shell", "no_run_tests", "no_stage",
                "no_commit", "no_push", "no_file_deletion", "no_broad_staging",
                "no_git_add_dot", "no_unexempted_data_artifact", "no_data_fetch",
                "no_optimization", "no_rescue_variant", "no_new_candidate", "no_c19",
                "no_advance_or_reject", "no_replay_verdict_decision",
                "no_new_instrument_class", "no_xauusd", "no_paper_trading",
                "no_live_trading", "no_broker", "no_order_logic", "no_credentials",
                "no_private_api", "no_scheduler_change", "no_human_gate_weakening",
                "no_gate_skip"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
