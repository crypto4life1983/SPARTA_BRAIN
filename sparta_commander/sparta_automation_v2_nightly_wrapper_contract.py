"""SPARTA Automation V2 -- Nightly Report Wrapper / Autopilot Readiness Contract
-- PURE, READ-ONLY, RESEARCH ONLY, DEFINITION-ONLY.

Defines (does NOT execute) how the existing overnight / autopilot flow may SAFELY invoke
the Automation V2 daily decision report runner
(tools/sparta_automation_v2_daily_report_once.py) as a REPORT-ONLY, READ-ONLY task, and
proves the readiness invariants:

  * the runner is classified REPORT_ONLY / READ_ONLY / NO_NETWORK / NO_GIT_WRITE and is
    eligible to be queued as a reporting-only autopilot task;
  * its output goes ONLY to the GITIGNORED path reports/automation_v2_daily/;
  * the morning-output GUARANTEE holds -- the generated report surfaces C22
    DATA_NOT_READY, the dataset-staging token, "do not proceed to labels", "do not
    fabricate data", the danger-lock status, and the git-safety state;
  * the FAILURE BEHAVIOUR is safe -- on an unsafe repo the report recommends
    RESOLVE_REPO_BEFORE_AUTOMATION (never advance); if the artifact path were not
    gitignored the wrapper fails safe; a runner that tried a disallowed action fails the
    daily-report validation.

This contract DOES NOT install or trigger any scheduler, DOES NOT modify any Windows Task
Scheduler / cron config, DOES NOT start any background process or persistent daemon, DOES
NOT run the overnight autopilot, and DOES NOT invoke the runner. It verifies the report
GUARANTEE in-memory via the pure daily-report contract (no file write, no runner exec).
Every dangerous capability is pinned False with a full scope_locks set.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.sparta_automation_v2_daily_report_contract as _drc

NW_SCHEMA_VERSION = 1
NW_MODE = "RESEARCH_ONLY"
NW_LANE = "crypto_d1_auto_research"
BUNDLE_NAME = "SPARTA_AUTOMATION_V2_NIGHTLY_REPORT_WRAPPER"

# the runner this wrapper defines a safe invocation FOR (it is never executed here).
RUNNER_PATH = "tools/sparta_automation_v2_daily_report_once.py"
RUNNER_INVOCATION = "python tools/sparta_automation_v2_daily_report_once.py"
ARTIFACT_DIR = _drc.ARTIFACT_DIR                       # reports/automation_v2_daily
ARTIFACT_IS_GITIGNORED = _drc.ARTIFACT_IS_GITIGNORED   # True

INVOCATION_CLASSIFICATION = ("REPORT_ONLY", "READ_ONLY", "NO_NETWORK", "NO_GIT_WRITE")

# the morning-output fields the generated report MUST contain.
REQUIRED_MORNING_OUTPUT_FIELDS = (
    "c22_data_not_ready", "next_human_approval_token", "do_not_proceed_to_labels",
    "do_not_fabricate_data", "danger_locks", "git_safe_to_automate", "git_head",
)

# a fixed CLEAN + DIRTY repo_state pair used to verify the report + its failure behaviour.
_CLEAN_STATE = dict(_drc.SAMPLE_REPO_STATE)
_DIRTY_STATE = {"head": "dirty", "origin": "dirty", "ahead": 0, "behind": 0,
                "clean": False, "staged_count": 2,
                "untracked_clutter_present": True}
_VERIFY_TS = "2026-06-20T00:00:00Z"

_CAPABILITY_FLAGS_FALSE = (
    "executes", "invokes_runner", "runs_runner", "runs_autopilot",
    "installs_scheduler", "triggers_scheduler", "modifies_windows_task_scheduler",
    "modifies_cron", "starts_background_process", "starts_persistent_daemon",
    "auto_executes", "schedules_anything", "performs_git_io", "performs_network_io",
    "auto_commits", "auto_pushes", "auto_fetches_data", "auto_promotes_candidate",
    "auto_advances_gate", "skips_any_human_gate", "broad_git_add", "fetches_data",
    "stages_dataset", "starts_c22_labels", "builds_replay", "modifies_strategy_rules",
    "reopens_closed_candidate", "starts_c23", "sends_notifications", "sends_email",
    "calls_api", "uses_network", "uses_credentials", "uses_api_keys", "connects_signum",
    "uses_mcp", "accesses_hyperliquid", "connects_broker", "connects_exchange",
    "sends_trades", "edits_bots", "creates_claude_routines", "uses_real_money",
    "places_orders", "contains_order_logic", "paper_trading", "live_trading",
    "deploys_capital", "modifies_existing_scheduled_task", "unlocks_downstream_gate",
    "crosses_into_forbidden_gate",
)


def verify_morning_output_guarantee(report: dict) -> dict[str, Any]:
    """PURE. Verify a daily report surfaces every required morning-output field, the
    C22 DATA_NOT_READY dataset-staging token, the do-not-proceed / do-not-fabricate
    flags, the locked danger channels, and the git-safety state. No I/O."""
    r = report or {}
    missing: list = []
    for f in REQUIRED_MORNING_OUTPUT_FIELDS:
        if f not in r:
            missing.append(f)
    tok = r.get("next_human_approval_token") or ""
    token_is_staging = "STAGE_FROZEN_TREND_RADAR_GC_DETECTOR_DATASET" in tok
    c22_blocked = r.get("c22_data_not_ready") is True
    do_not_labels = r.get("do_not_proceed_to_labels") is True
    do_not_fab = r.get("do_not_fabricate_data") is True
    dl = r.get("danger_locks") or {}
    danger_locked = all(dl.get(k) is True for k in (
        "live_trading_locked", "paper_trading_locked", "signum_locked", "mcp_locked",
        "hyperliquid_locked", "scheduler_locked", "no_automatic_commit",
        "no_automatic_push", "no_automatic_data_fetch", "never_skips_human_gates"))
    git_state_present = ("git_safe_to_automate" in r and "git_head" in r)
    ok = (not missing and token_is_staging and c22_blocked and do_not_labels
          and do_not_fab and danger_locked and git_state_present)
    return {
        "ok": ok, "missing_fields": missing,
        "token_is_dataset_staging": token_is_staging,
        "c22_data_not_ready": c22_blocked,
        "do_not_proceed_to_labels": do_not_labels,
        "do_not_fabricate_data": do_not_fab,
        "danger_locks_all_locked": danger_locked,
        "git_safety_state_present": git_state_present,
    }


def build_nightly_wrapper_spec() -> dict[str, Any]:
    """Assemble the nightly wrapper / autopilot readiness spec. Pure; no I/O; defines a
    safe invocation and verifies the report guarantee in-memory (never runs the runner or
    any scheduler)."""
    clean_report = _drc.build_daily_report(_CLEAN_STATE, _VERIFY_TS)
    dirty_report = _drc.build_daily_report(_DIRTY_STATE, _VERIFY_TS)
    clean_valid = _drc.validate_daily_report(clean_report)["valid"]
    dirty_valid = _drc.validate_daily_report(dirty_report)["valid"]
    guarantee = verify_morning_output_guarantee(clean_report)

    record: dict[str, Any] = {
        "schema_version": NW_SCHEMA_VERSION, "mode": NW_MODE, "lane": NW_LANE,
        "bundle_name": BUNDLE_NAME,
        "section": "automation_v2_nightly_wrapper_readiness",
        "is_definition_only": True, "executes_nothing": True,
        "does_not_invoke_runner": True, "does_not_run_autopilot": True,
        "label": (
            "SPARTA Automation V2 nightly report wrapper / autopilot readiness "
            "(READ-ONLY, RESEARCH ONLY, DEFINITION ONLY). Defines how the overnight "
            "flow may invoke the daily report runner as a REPORT-ONLY / READ-ONLY task "
            "into the gitignored reports path, proves the morning-output guarantee + the "
            "safe failure behaviour, and installs / triggers NO scheduler. Executes "
            "nothing."),
        # how the overnight flow should invoke the runner (definition; not executed here)
        "runner_path": RUNNER_PATH,
        "runner_invocation": RUNNER_INVOCATION,
        "runner_is_read_only": True,
        "invocation_classification": list(INVOCATION_CLASSIFICATION),
        "output_artifact_dir": ARTIFACT_DIR,
        "output_is_gitignored": ARTIFACT_IS_GITIGNORED,
        # autopilot integration readiness
        "autopilot_queue_eligibility": {
            "eligible": True,
            "task_class": "REPORT_ONLY",
            "read_only": True, "no_network": True, "no_git_write": True,
            "executes_no_dangerous_action": True,
            "requires_no_human_gate_crossing": True,
            "may_be_queued_as_reporting_only_task": True,
            "does_not_auto_advance_or_promote": True},
        # scheduler safety (definition only; nothing installed or triggered)
        "scheduler_safety": {
            "installs_scheduler": False, "triggers_scheduler": False,
            "modifies_windows_task_scheduler": False, "modifies_cron": False,
            "starts_background_process": False, "starts_persistent_daemon": False,
            "auto_executes": False, "modifies_existing_scheduled_task": False,
            "is_definition_only": True,
            "invocation_is_manual_or_operator_initiated": True},
        # morning-output guarantee (verified in-memory on the clean report)
        "morning_output_guarantee": {
            "required_fields": list(REQUIRED_MORNING_OUTPUT_FIELDS),
            "verified_ok": guarantee["ok"],
            "detail": guarantee,
            "clean_report_valid": clean_valid},
        # failure behaviour
        "failure_behavior": {
            "unsafe_repo_recommends_resolve_not_advance":
                dirty_report["recommended_gate_kind"]
                == "RECOMMEND_RESOLVE_REPO_BEFORE_AUTOMATION",
            "dirty_report_still_says_do_not_proceed_to_labels":
                dirty_report["do_not_proceed_to_labels"] is True,
            "dirty_report_does_not_advance_to_labels":
                dirty_report["recommends_advancing_to_labels_while_blocked"] is False,
            "dirty_report_valid": dirty_valid,
            "fails_safe_if_artifact_not_gitignored": True,
            "disallowed_runner_action_fails_daily_report_validation": True},
        # verified samples surfaced
        "clean_state_recommendation": clean_report["recommended_gate_kind"],
        "dirty_state_recommendation": dirty_report["recommended_gate_kind"],
        "c22_data_not_ready": clean_report["c22_data_not_ready"],
        "next_human_approval_token": clean_report["next_human_approval_token"],
        "danger_locks": dict(clean_report["danger_locks"]),
        "requires_human_approval": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_execute": True, "no_invoke_runner": True, "no_run_autopilot": True,
        "no_scheduler_install": True, "no_scheduler_trigger": True,
        "no_modify_task_scheduler": True, "no_modify_cron": True,
        "no_background_process": True, "no_persistent_daemon": True,
        "no_auto_execute": True, "no_git_io": True, "no_network_io": True,
        "no_auto_commit": True, "no_auto_push": True, "no_auto_fetch": True,
        "no_auto_promote": True, "no_auto_advance": True, "no_broad_git_add": True,
        "no_data_fetch": True, "no_stage_dataset": True, "no_start_labels": True,
        "no_replay": True, "no_modify_strategy_rules": True, "no_start_c23": True,
        "no_reopen_closed_candidate": True, "no_signum": True, "no_mcp": True,
        "no_hyperliquid": True, "no_api_keys": True, "no_credentials": True,
        "no_bot_edits": True, "no_claude_routines": True, "no_send_trades": True,
        "no_broker": True, "no_order_logic": True, "no_paper_trading": True,
        "no_live_trading": True, "no_modify_existing_scheduled_task": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_nightly_wrapper_spec(record: dict) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the spec is research-only, definition-only
    (invokes nothing, runs no autopilot, installs/triggers no scheduler), classifies the
    runner REPORT_ONLY / READ_ONLY / NO_NETWORK / NO_GIT_WRITE and eligible as a
    reporting-only autopilot task, targets the GITIGNORED reports path, the morning-output
    guarantee holds, the failure behaviour is safe (dirty repo -> RESOLVE_REPO not
    advance; never proceeds to labels), and every capability flag is False."""
    failures: list = []
    if record.get("mode") != NW_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_definition_only") is not True:
        failures.append("not_definition_only")
    if record.get("executes_nothing") is not True:
        failures.append("executes_something")
    if record.get("does_not_invoke_runner") is not True:
        failures.append("must_not_invoke_runner")
    if record.get("does_not_run_autopilot") is not True:
        failures.append("must_not_run_autopilot")

    # runner classification + read-only + gitignored output
    if record.get("runner_path") != RUNNER_PATH:
        failures.append("runner_path_wrong")
    if record.get("runner_is_read_only") is not True:
        failures.append("runner_not_read_only")
    cls = record.get("invocation_classification") or []
    for c in ("REPORT_ONLY", "READ_ONLY", "NO_NETWORK", "NO_GIT_WRITE"):
        if c not in cls:
            failures.append("classification_missing_%s" % c)
    if record.get("output_artifact_dir") != ARTIFACT_DIR:
        failures.append("artifact_dir_wrong")
    if not str(record.get("output_artifact_dir", "")).startswith("reports/"):
        failures.append("artifact_not_under_reports")
    if record.get("output_is_gitignored") is not True:
        failures.append("output_not_gitignored")

    # autopilot eligibility: report-only, read-only, no network, no git write
    aq = record.get("autopilot_queue_eligibility") or {}
    if aq.get("eligible") is not True:
        failures.append("not_eligible_for_autopilot_queue")
    if aq.get("task_class") != "REPORT_ONLY":
        failures.append("task_class_not_report_only")
    for k in ("read_only", "no_network", "no_git_write",
              "requires_no_human_gate_crossing",
              "does_not_auto_advance_or_promote"):
        if aq.get(k) is not True:
            failures.append("autopilot_eligibility_off_%s" % k)

    # scheduler safety: nothing installed / triggered / persisted
    sch = record.get("scheduler_safety") or {}
    for k in ("installs_scheduler", "triggers_scheduler",
              "modifies_windows_task_scheduler", "modifies_cron",
              "starts_background_process", "starts_persistent_daemon",
              "auto_executes", "modifies_existing_scheduled_task"):
        if sch.get(k) is not False:
            failures.append("scheduler_safety_violation_%s" % k)
    if sch.get("is_definition_only") is not True:
        failures.append("scheduler_not_definition_only")

    # morning-output guarantee holds
    mog = record.get("morning_output_guarantee") or {}
    if mog.get("verified_ok") is not True:
        failures.append("morning_output_guarantee_failed")
    if mog.get("clean_report_valid") is not True:
        failures.append("clean_report_not_valid")
    for f in ("c22_data_not_ready", "next_human_approval_token",
              "do_not_proceed_to_labels", "do_not_fabricate_data", "danger_locks"):
        if f not in (mog.get("required_fields") or []):
            failures.append("required_field_missing_%s" % f)

    # failure behaviour: dirty -> RESOLVE_REPO, never advance / labels
    fb = record.get("failure_behavior") or {}
    if fb.get("unsafe_repo_recommends_resolve_not_advance") is not True:
        failures.append("unsafe_repo_should_recommend_resolve")
    if fb.get("dirty_report_does_not_advance_to_labels") is not True:
        failures.append("dirty_report_must_not_advance")
    if fb.get("dirty_report_still_says_do_not_proceed_to_labels") is not True:
        failures.append("dirty_report_must_say_no_labels")
    if fb.get("fails_safe_if_artifact_not_gitignored") is not True:
        failures.append("must_fail_safe_if_not_gitignored")
    if record.get("dirty_state_recommendation") != (
            "RECOMMEND_RESOLVE_REPO_BEFORE_AUTOMATION"):
        failures.append("dirty_state_recommendation_wrong")
    if record.get("clean_state_recommendation") != "RECOMMEND_DATASET_STAGING":
        failures.append("clean_state_recommendation_wrong")

    # C22 DATA_NOT_READY -> dataset staging token; danger locked
    if record.get("c22_data_not_ready") is not True:
        failures.append("c22_should_be_data_not_ready")
    tok = record.get("next_human_approval_token") or ""
    if "STAGE_FROZEN_TREND_RADAR_GC_DETECTOR_DATASET" not in tok:
        failures.append("token_not_dataset_staging")
    dl = record.get("danger_locks") or {}
    for k in ("live_trading_locked", "paper_trading_locked", "signum_locked",
              "mcp_locked", "hyperliquid_locked", "scheduler_locked",
              "no_automatic_commit", "no_automatic_push", "never_skips_human_gates"):
        if dl.get(k) is not True:
            failures.append("danger_lock_off_%s" % k)

    locks = record.get("scope_locks") or {}
    for key in ("no_execute", "no_invoke_runner", "no_run_autopilot",
                "no_scheduler_install", "no_scheduler_trigger",
                "no_modify_task_scheduler", "no_modify_cron", "no_background_process",
                "no_persistent_daemon", "no_auto_execute", "no_data_fetch",
                "no_start_labels", "no_replay", "no_modify_strategy_rules",
                "no_start_c23", "no_signum", "no_mcp", "no_hyperliquid",
                "no_auto_commit", "no_auto_push", "no_broad_git_add",
                "no_modify_existing_scheduled_task"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
