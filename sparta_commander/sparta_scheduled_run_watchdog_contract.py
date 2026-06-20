"""SPARTA scheduled-run WATCHDOG -- PURE, READ-ONLY, SUGGESTION-ONLY.

Consumes the Bundle A scheduled-task health (sparta_scheduled_task_health_classifier) + the
C22 collection signals and produces a REMEDIATION RECOMMENDATION. It is suggestion-only: it
NEVER runs a task, NEVER reruns the pickup/import, NEVER changes Windows Task Scheduler, and
NEVER auto-executes an approval token.

Per-task watchdog status (refines the Bundle A view by splitting never-ran out of stale):
  * OK / STALE / FAILED / MISSING / NEVER_RAN.

It tracks the priority tasks (C22 pickup, C22 import, overnight autopilot), detects
C22-specific risk (pickup failed, import failed, missed latest expected export, progress not
advancing while the automation is healthy), and emits a remediation from the closed set:
  * CHECK_EXTERNAL_SIGNUM_EXPORT  -- the external read-only routine likely did not save a
    new daily export;
  * CHECK_WINDOWS_TASK_SCHEDULER  -- a scheduled task is missing/stale/never-ran;
  * REVIEW_FAILED_TASK_LOGS       -- a task reported a real failure result;
  * RUN_READ_ONLY_STATUS_CHECK    -- inspect the read-only status surfaces;
  * NO_ACTION_REQUIRED.

Operator remediations are CHECKS (read-only investigation), never automated fixes. Approval
tokens remain the control panel's domain; the watchdog surfaces none that advance a gate.
Every dangerous capability is pinned False.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.sparta_scheduled_task_health_classifier_contract as _th

WD_SCHEMA_VERSION = 1
WD_MODE = "RESEARCH_ONLY"

# priority tasks (single-sourced from the Bundle A classifier).
PICKUP_TASK = "C22_Signum_GC_Download_Pickup"
IMPORT_TASK = "C22_Signum_GC_Import_Automation"
OVERNIGHT_TASK = "SPARTA_Overnight_Autopilot"
PRIORITY_TASKS = _th.PRIORITY_TASKS

# per-task watchdog statuses.
W_OK = "OK"
W_STALE = "STALE"
W_FAILED = "FAILED"
W_MISSING = "MISSING"
W_NEVER_RAN = "NEVER_RAN"
ALL_W_STATUSES = (W_OK, W_STALE, W_FAILED, W_MISSING, W_NEVER_RAN)

# remediation recommendations (closed set).
REC_CHECK_EXPORT = "CHECK_EXTERNAL_SIGNUM_EXPORT"
REC_CHECK_SCHEDULER = "CHECK_WINDOWS_TASK_SCHEDULER"
REC_REVIEW_FAILED_LOGS = "REVIEW_FAILED_TASK_LOGS"
REC_RUN_STATUS_CHECK = "RUN_READ_ONLY_STATUS_CHECK"
REC_NO_ACTION = "NO_ACTION_REQUIRED"
ALL_RECOMMENDATIONS = (REC_CHECK_EXPORT, REC_CHECK_SCHEDULER, REC_REVIEW_FAILED_LOGS,
                       REC_RUN_STATUS_CHECK, REC_NO_ACTION)

# severity of the overall watchdog finding.
SEV_NONE = "NONE"
SEV_ATTENTION = "ATTENTION"
SEV_ALERT = "ALERT"

# the export-lag (days) beyond which the latest expected window is "missed".
MISSED_EXPORT_DAY_THRESHOLD = 1

_CAPABILITY_FLAGS_FALSE = (
    "executes", "runs_tasks", "reruns_pickup", "reruns_import", "runs_pickup",
    "runs_import", "changes_scheduled_task", "creates_scheduled_task",
    "deletes_scheduled_task", "triggers_scheduled_task", "installs_scheduler",
    "adds_scheduler_code", "auto_executes_token", "advances_any_gate", "performs_network_io",
    "fetches_data", "connects_signum", "uses_mcp", "calls_api", "places_orders",
    "sends_trades", "paper_trading", "live_trading", "modifies_c22_pipeline",
    "modifies_tracker_storage", "crosses_into_forbidden_gate",
)


def watchdog_status(rec: Any) -> str:
    """PURE. Refined per-task status (splits NEVER_RAN out of STALE). `rec` is a Bundle A
    task entry {found, last_result, hours_since_last_run}. Never raises."""
    if not isinstance(rec, dict) or not rec.get("found"):
        return W_MISSING
    lr = rec.get("last_result")
    if lr is not None and lr not in _th.BENIGN_RESULT_CODES:
        return W_FAILED
    hrs = rec.get("hours_since_last_run")
    if hrs is None:
        return W_NEVER_RAN
    try:
        if float(hrs) > _th.STALENESS_HOURS:
            return W_STALE
    except (TypeError, ValueError):
        return W_STALE
    return W_OK


def build_watchdog(task_health: dict, c22_collection: dict) -> dict[str, Any]:
    """Assemble the suggestion-only watchdog finding. Pure; no I/O. Recommends remediation
    CHECKS only -- never runs/reruns a task, changes a scheduler, or executes a token."""
    th = dict(task_health or {})
    tasks = list(th.get("tasks") or [])
    by_name = {t.get("name"): t for t in tasks if isinstance(t, dict)}

    task_states = {}
    for name in _th.KNOWN_SPARTA_TASKS:
        task_states[name] = watchdog_status(by_name.get(name))

    pickup = task_states.get(PICKUP_TASK, W_MISSING)
    importer = task_states.get(IMPORT_TASK, W_MISSING)
    overnight = task_states.get(OVERNIGHT_TASK, W_MISSING)

    cc = dict(c22_collection or {})
    days_since = cc.get("days_since_latest_window")
    missed_latest_export = (isinstance(days_since, int)
                            and days_since > MISSED_EXPORT_DAY_THRESHOLD)
    automation_healthy = pickup == W_OK and importer == W_OK
    # automation ran fine but no fresh window arrived => the EXTERNAL export is the bottleneck
    progress_not_advancing = bool(missed_latest_export and automation_healthy)

    priority_failed = [n for n in PRIORITY_TASKS if task_states.get(n) == W_FAILED]
    priority_missing = [n for n in PRIORITY_TASKS if task_states.get(n) == W_MISSING]
    priority_stale_or_never = [
        n for n in PRIORITY_TASKS
        if task_states.get(n) in (W_STALE, W_NEVER_RAN)]

    c22_risks = {
        "pickup_failed": pickup == W_FAILED,
        "import_failed": importer == W_FAILED,
        "pickup_missing": pickup == W_MISSING,
        "import_missing": importer == W_MISSING,
        "missed_latest_export": missed_latest_export,
        "progress_not_advancing": progress_not_advancing,
    }

    # remediation recommendations (severity order, de-duplicated, suggestion only)
    recs: list = []
    if priority_failed:
        recs += [REC_REVIEW_FAILED_LOGS, REC_CHECK_SCHEDULER]
    if priority_missing:
        recs.append(REC_CHECK_SCHEDULER)
    if priority_stale_or_never:
        recs += [REC_CHECK_SCHEDULER, REC_RUN_STATUS_CHECK]
    if missed_latest_export:
        recs.append(REC_CHECK_EXPORT)
    # de-dupe preserving order
    seen: set = set()
    recommendations = [r for r in recs if not (r in seen or seen.add(r))]
    if not recommendations:
        recommendations = [REC_NO_ACTION]
    primary = recommendations[0]

    if priority_failed or priority_missing:
        severity = SEV_ALERT
    elif recommendations != [REC_NO_ACTION]:
        severity = SEV_ATTENTION
    else:
        severity = SEV_NONE

    operator_checks: list = []
    if missed_latest_export:
        operator_checks.append(
            "run the external read-only get-trendradar-daily routine and SAVE the daily "
            "export into Downloads / the inbox")
    if priority_failed:
        operator_checks.append(
            "review the failed task's last result + logs in Windows Task Scheduler")
    if priority_missing or priority_stale_or_never:
        operator_checks.append(
            "verify the scheduled task is registered and its last run time in Task Scheduler")

    record: dict[str, Any] = {
        "schema_version": WD_SCHEMA_VERSION, "mode": WD_MODE,
        "section": "sparta_scheduled_run_watchdog",
        "is_read_only_watchdog": True, "is_suggestion_only": True,
        "label": (
            "SPARTA scheduled-run watchdog (READ-ONLY, SUGGESTION ONLY). Reads Bundle A task "
            "health + C22 signals and recommends remediation CHECKS only; never runs/reruns "
            "a task, changes a scheduler, or executes a token."),
        "task_states": task_states,
        "priority_states": {PICKUP_TASK: pickup, IMPORT_TASK: importer,
                            OVERNIGHT_TASK: overnight},
        "priority_failed": priority_failed,
        "priority_missing": priority_missing,
        "priority_stale_or_never_ran": priority_stale_or_never,
        "c22_risks": c22_risks,
        "recommendations": recommendations,
        "primary_recommendation": primary,
        "severity": severity,
        "operator_checks": operator_checks,
        # suggestion-only token surface (the watchdog advances NO gate; tokens are the
        # control panel's domain -- it surfaces none that advance a gate here).
        "suggested_human_tokens": [],
        "auto_executes_any_token": False,
        "reran_any_task": False,
        "changed_any_scheduled_task": False,
        "advances_nothing": True, "human_review_required": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_execute": True, "no_run_tasks": True, "no_rerun_pickup": True,
        "no_rerun_import": True, "no_change_scheduled_task": True, "no_create_task": True,
        "no_delete_task": True, "no_trigger_task": True, "no_install_scheduler": True,
        "no_add_scheduler_code": True, "no_auto_execute_token": True,
        "no_advance_gate": True, "no_network_io": True, "no_data_fetch": True,
        "no_signum_connection": True, "no_mcp": True, "no_order_logic": True,
        "no_paper_trading": True, "no_live_trading": True, "no_modify_c22_pipeline": True,
        "no_modify_tracker_storage": True, "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_watchdog(record: Any) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when research-only, read-only/suggestion-only;
    each task state is from the closed set; the recommendations are from the closed set and
    severity is consistent (ALERT iff a priority task failed/missing; NONE iff NO_ACTION);
    the watchdog reran no task / changed no scheduled task / executed no token; and every
    capability flag is False."""
    failures: list = []
    if not isinstance(record, dict):
        return {"valid": False, "failures": ["record_not_a_dict"]}
    r = record

    if r.get("mode") != WD_MODE:
        failures.append("mode_not_research_only")
    if r.get("is_read_only_watchdog") is not True:
        failures.append("not_read_only_watchdog")
    if r.get("is_suggestion_only") is not True:
        failures.append("not_suggestion_only")

    for name, st in (r.get("task_states") or {}).items():
        if st not in ALL_W_STATUSES:
            failures.append("bad_task_state_%s" % name)

    recs = r.get("recommendations") or []
    if not recs:
        failures.append("recommendations_empty")
    for rec in recs:
        if rec not in ALL_RECOMMENDATIONS:
            failures.append("bad_recommendation_%s" % rec)
    if r.get("primary_recommendation") not in ALL_RECOMMENDATIONS:
        failures.append("bad_primary_recommendation")
    if recs and r.get("primary_recommendation") != recs[0]:
        failures.append("primary_not_first")
    if REC_NO_ACTION in recs and len(recs) > 1:
        failures.append("no_action_mixed_with_others")

    # severity consistency
    pf = r.get("priority_failed") or []
    pm = r.get("priority_missing") or []
    sev = r.get("severity")
    if sev not in (SEV_NONE, SEV_ATTENTION, SEV_ALERT):
        failures.append("bad_severity")
    if (pf or pm) and sev != SEV_ALERT:
        failures.append("priority_failure_must_be_alert")
    if recs == [REC_NO_ACTION] and sev != SEV_NONE:
        failures.append("no_action_must_be_none_severity")
    if recs != [REC_NO_ACTION] and not (pf or pm) and sev != SEV_ATTENTION:
        failures.append("nonempty_recs_must_be_attention")

    # never ran / changed / executed anything
    for k in ("reran_any_task", "changed_any_scheduled_task", "auto_executes_any_token"):
        if r.get(k) is not False:
            failures.append("must_be_false_%s" % k)
    if r.get("advances_nothing") is not True:
        failures.append("must_advance_nothing")
    # the watchdog surfaces NO gate-advancing token
    if r.get("suggested_human_tokens"):
        failures.append("watchdog_must_not_suggest_gate_tokens")

    locks = r.get("scope_locks") or {}
    for key in ("no_execute", "no_run_tasks", "no_rerun_pickup", "no_rerun_import",
                "no_change_scheduled_task", "no_create_task", "no_delete_task",
                "no_trigger_task", "no_install_scheduler", "no_add_scheduler_code",
                "no_auto_execute_token", "no_advance_gate", "no_network_io",
                "no_data_fetch", "no_signum_connection", "no_mcp", "no_order_logic",
                "no_paper_trading", "no_live_trading", "no_modify_c22_pipeline",
                "no_modify_tracker_storage"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if r.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
