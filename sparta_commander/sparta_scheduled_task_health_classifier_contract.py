"""SPARTA scheduled-task HEALTH CLASSIFIER -- PURE, READ-ONLY, REPORTING ONLY.

Classifies the read-only status of the known SPARTA Windows scheduled tasks into
OK / STALE / FAILED / MISSING. It is PURE: it operates on ALREADY-GATHERED task records
(the runner reads them via read-only Get-ScheduledTaskInfo and passes them in); it creates,
changes, triggers, installs, and deletes NO scheduled task and runs nothing.

A record per task is {name, found, last_result, hours_since_last_run}:
  * MISSING -- the task is not registered;
  * FAILED  -- last_result is a real failure code (not 0 and not a benign not-yet-run/ready/
               running code);
  * STALE   -- never ran, or last ran longer ago than the daily staleness window;
  * OK      -- ran within the staleness window with a success / benign result.

This contract changes NO scheduled task, adds NO scheduler code, and performs NO trading /
network / data-fetch. Every dangerous capability is pinned False.
"""
from __future__ import annotations

from typing import Any

TH_SCHEMA_VERSION = 1
TH_MODE = "RESEARCH_ONLY"

# the known SPARTA scheduled tasks (read-only monitoring targets).
PRIORITY_TASKS = (
    "C22_Signum_GC_Download_Pickup",
    "C22_Signum_GC_Import_Automation",
    "SPARTA_Overnight_Autopilot",
)
OTHER_KNOWN_TASKS = (
    "SPARTA Daily Journal Snapshot",
    "SPARTA Research Hunter Daily Scan",
    "SPARTA Shadow Validator",
    "SPARTA_BRAIN_FrozenStackDailyEvidenceCycle",
    "SPARTA_BRAIN_ProfitBrainDailyRefresh",
)
KNOWN_SPARTA_TASKS = PRIORITY_TASKS + OTHER_KNOWN_TASKS

STATUS_OK = "OK"
STATUS_STALE = "STALE"
STATUS_FAILED = "FAILED"
STATUS_MISSING = "MISSING"
ALL_STATUSES = (STATUS_OK, STATUS_STALE, STATUS_FAILED, STATUS_MISSING)

# a daily task should have run within this window; older => STALE.
STALENESS_HOURS = 36
# benign Windows Task Scheduler "last result" codes that are NOT failures.
# 0 = success; 267011 = has not yet run; 267009 = currently running; 267010 = ready/not-run.
BENIGN_RESULT_CODES = (0, 267011, 267009, 267010)

_CAPABILITY_FLAGS_FALSE = (
    "executes", "creates_scheduled_task", "changes_scheduled_task",
    "deletes_scheduled_task", "triggers_scheduled_task", "installs_scheduler",
    "adds_scheduler_code", "runs_tasks", "performs_network_io", "fetches_data",
    "connects_signum", "uses_mcp", "calls_api", "uses_credentials", "places_orders",
    "sends_trades", "paper_trading", "live_trading", "auto_executes_token",
    "crosses_into_forbidden_gate",
)


def classify_task(rec: Any) -> str:
    """PURE. Classify one gathered task record. Never raises."""
    if not isinstance(rec, dict) or not rec.get("found"):
        return STATUS_MISSING
    lr = rec.get("last_result")
    if lr is not None and lr not in BENIGN_RESULT_CODES:
        return STATUS_FAILED
    hrs = rec.get("hours_since_last_run")
    if hrs is None:
        return STATUS_STALE                 # never ran / unknown last-run
    try:
        if float(hrs) > STALENESS_HOURS:
            return STATUS_STALE
    except (TypeError, ValueError):
        return STATUS_STALE
    return STATUS_OK


def build_task_health(task_records: Any) -> dict[str, Any]:
    """PURE. Classify a list of gathered task records into a health summary. No I/O."""
    recs = list(task_records or [])
    tasks: list = []
    for rec in recs:
        name = rec.get("name") if isinstance(rec, dict) else None
        status = classify_task(rec)
        tasks.append({
            "name": name,
            "is_priority": name in PRIORITY_TASKS,
            "found": bool(rec.get("found")) if isinstance(rec, dict) else False,
            "last_result": rec.get("last_result") if isinstance(rec, dict) else None,
            "hours_since_last_run": (rec.get("hours_since_last_run")
                                     if isinstance(rec, dict) else None),
            "status": status,
        })
    counts = {s: sum(1 for t in tasks if t["status"] == s) for s in ALL_STATUSES}
    any_failed = counts[STATUS_FAILED] > 0
    any_missing = counts[STATUS_MISSING] > 0
    any_stale = counts[STATUS_STALE] > 0
    priority_failed_or_missing = [
        t["name"] for t in tasks
        if t["is_priority"] and t["status"] in (STATUS_FAILED, STATUS_MISSING)]
    attention = [t["name"] for t in tasks
                 if t["status"] in (STATUS_FAILED, STATUS_MISSING, STATUS_STALE)]
    all_ok = all(t["status"] == STATUS_OK for t in tasks) and bool(tasks)

    record: dict[str, Any] = {
        "schema_version": TH_SCHEMA_VERSION, "mode": TH_MODE,
        "section": "sparta_scheduled_task_health",
        "is_read_only_monitor": True,
        "staleness_hours": STALENESS_HOURS,
        "tasks": tasks,
        "counts": counts,
        "any_failed": any_failed, "any_missing": any_missing, "any_stale": any_stale,
        "all_ok": all_ok,
        "priority_failed_or_missing": priority_failed_or_missing,
        "attention_tasks": attention,
        "overall_task_health": (STATUS_OK if (not any_failed and not any_missing)
                                else "ATTENTION"),
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_execute": True, "no_create_task": True, "no_change_task": True,
        "no_delete_task": True, "no_trigger_task": True, "no_install_scheduler": True,
        "no_add_scheduler_code": True, "no_run_tasks": True, "no_network_io": True,
        "no_data_fetch": True, "no_signum_connection": True, "no_mcp": True,
        "no_order_logic": True, "no_paper_trading": True, "no_live_trading": True,
        "no_auto_execute_token": True, "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_task_health(record: Any) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when research-only, read-only monitor; each task
    status is from the closed set and consistent with classify_task; the counts/flags match
    the tasks; and every capability flag is False (the monitor changes no task)."""
    failures: list = []
    if not isinstance(record, dict):
        return {"valid": False, "failures": ["record_not_a_dict"]}
    r = record

    if r.get("mode") != TH_MODE:
        failures.append("mode_not_research_only")
    if r.get("is_read_only_monitor") is not True:
        failures.append("not_read_only_monitor")
    if r.get("staleness_hours") != STALENESS_HOURS:
        failures.append("staleness_tampered")

    tasks = r.get("tasks") or []
    for t in tasks:
        if t.get("status") not in ALL_STATUSES:
            failures.append("bad_status_%s" % t.get("name"))
        # re-derive the status from the record and compare (anti-tamper)
        expected = classify_task({"found": t.get("found"),
                                  "last_result": t.get("last_result"),
                                  "hours_since_last_run": t.get("hours_since_last_run")})
        if t.get("status") != expected:
            failures.append("status_inconsistent_%s" % t.get("name"))

    counts = r.get("counts") or {}
    for s in ALL_STATUSES:
        if counts.get(s) != sum(1 for t in tasks if t.get("status") == s):
            failures.append("count_inconsistent_%s" % s)
    if r.get("any_failed") is not (counts.get(STATUS_FAILED, 0) > 0):
        failures.append("any_failed_inconsistent")
    if r.get("any_missing") is not (counts.get(STATUS_MISSING, 0) > 0):
        failures.append("any_missing_inconsistent")
    if r.get("overall_task_health") not in (STATUS_OK, "ATTENTION"):
        failures.append("bad_overall_health")

    locks = r.get("scope_locks") or {}
    for key in ("no_execute", "no_create_task", "no_change_task", "no_delete_task",
                "no_trigger_task", "no_install_scheduler", "no_add_scheduler_code",
                "no_run_tasks", "no_network_io", "no_data_fetch", "no_signum_connection",
                "no_order_logic", "no_paper_trading", "no_live_trading",
                "no_auto_execute_token"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if r.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}
