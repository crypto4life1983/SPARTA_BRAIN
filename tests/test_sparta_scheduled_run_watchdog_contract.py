"""Tests for the SPARTA scheduled-run watchdog (Bundle C, suggestion-only).

Proves the watchdog classifies per-task status (OK/STALE/FAILED/MISSING/NEVER_RAN), detects
C22 risk (pickup/import failed, missed export, progress-not-advancing), emits the right
remediation from the closed set, and -- critically -- never runs/reruns a task, never changes
Windows Task Scheduler, and never auto-executes a token. Healthy + failed/stale/missing
fixtures + anti-tamper + module/runner purity."""
from __future__ import annotations

import ast
from pathlib import Path

import sparta_commander.sparta_scheduled_run_watchdog_contract as wd
import sparta_commander.sparta_scheduled_task_health_classifier_contract as th
import tools.sparta_scheduled_run_watchdog_once as runner


def _health(overrides=None):
    """Build a Bundle A task-health record; overrides maps task name -> record fields."""
    overrides = overrides or {}
    recs = []
    for n in th.KNOWN_SPARTA_TASKS:
        base = {"name": n, "found": True, "last_result": 0, "hours_since_last_run": 3.0}
        base.update(overrides.get(n, {}))
        recs.append(base)
    return th.build_task_health(recs)


_FRESH_C22 = {"collected_windows": 1, "latest_window_date": "2026-06-20",
              "days_since_latest_window": 1}


# ---- per-task status incl NEVER_RAN ----------------------------------------

def test_watchdog_status_five_states():
    assert wd.watchdog_status(
        {"found": True, "last_result": 0, "hours_since_last_run": 3.0}) == "OK"
    assert wd.watchdog_status(
        {"found": True, "last_result": 2, "hours_since_last_run": 3.0}) == "FAILED"
    assert wd.watchdog_status(
        {"found": True, "last_result": 0, "hours_since_last_run": 48.0}) == "STALE"
    assert wd.watchdog_status(
        {"found": True, "last_result": 267011, "hours_since_last_run": None}) == "NEVER_RAN"
    assert wd.watchdog_status({"found": False}) == "MISSING"


# ---- healthy state: NO_ACTION_REQUIRED -------------------------------------

def test_healthy_no_action():
    f = wd.build_watchdog(_health(), _FRESH_C22)
    assert f["severity"] == "NONE"
    assert f["recommendations"] == ["NO_ACTION_REQUIRED"]
    assert f["primary_recommendation"] == "NO_ACTION_REQUIRED"
    assert f["priority_failed"] == [] and f["priority_missing"] == []
    assert wd.validate_watchdog(f)["valid"] is True


# ---- failed pickup: REVIEW_FAILED_TASK_LOGS + CHECK_WINDOWS_TASK_SCHEDULER --

def test_failed_pickup_alert():
    h = _health({"C22_Signum_GC_Download_Pickup":
                 {"last_result": 2, "hours_since_last_run": 6.0}})
    f = wd.build_watchdog(h, _FRESH_C22)
    assert f["severity"] == "ALERT"
    assert "C22_Signum_GC_Download_Pickup" in f["priority_failed"]
    assert f["primary_recommendation"] == "REVIEW_FAILED_TASK_LOGS"
    assert "CHECK_WINDOWS_TASK_SCHEDULER" in f["recommendations"]
    assert f["c22_risks"]["pickup_failed"] is True
    assert wd.validate_watchdog(f)["valid"] is True


# ---- missing import task: CHECK_WINDOWS_TASK_SCHEDULER, ALERT ---------------

def test_missing_import_alert():
    h = _health({"C22_Signum_GC_Import_Automation": {"found": False}})
    f = wd.build_watchdog(h, _FRESH_C22)
    assert f["severity"] == "ALERT"
    assert "C22_Signum_GC_Import_Automation" in f["priority_missing"]
    assert "CHECK_WINDOWS_TASK_SCHEDULER" in f["recommendations"]
    assert f["priority_states"]["C22_Signum_GC_Import_Automation"] == "MISSING"
    assert wd.validate_watchdog(f)["valid"] is True


# ---- stale overnight: ATTENTION + scheduler/status checks ------------------

def test_stale_priority_attention():
    h = _health({"SPARTA_Overnight_Autopilot": {"hours_since_last_run": 50.0}})
    f = wd.build_watchdog(h, _FRESH_C22)
    assert f["severity"] == "ATTENTION"
    assert f["priority_states"]["SPARTA_Overnight_Autopilot"] == "STALE"
    assert "CHECK_WINDOWS_TASK_SCHEDULER" in f["recommendations"]
    assert "RUN_READ_ONLY_STATUS_CHECK" in f["recommendations"]
    assert wd.validate_watchdog(f)["valid"] is True


# ---- never_ran priority -> NEVER_RAN + scheduler/status checks --------------

def test_never_ran_priority():
    h = _health({"C22_Signum_GC_Download_Pickup":
                 {"last_result": 267011, "hours_since_last_run": None}})
    f = wd.build_watchdog(h, _FRESH_C22)
    assert f["priority_states"]["C22_Signum_GC_Download_Pickup"] == "NEVER_RAN"
    assert f["severity"] == "ATTENTION"
    assert "CHECK_WINDOWS_TASK_SCHEDULER" in f["recommendations"]


# ---- missed export while automation healthy -> CHECK_EXTERNAL_SIGNUM_EXPORT -

def test_missed_export_progress_not_advancing():
    c22 = {"collected_windows": 1, "latest_window_date": "2026-06-17",
           "days_since_latest_window": 3}
    f = wd.build_watchdog(_health(), c22)   # tasks all OK
    assert f["c22_risks"]["missed_latest_export"] is True
    assert f["c22_risks"]["progress_not_advancing"] is True
    assert "CHECK_EXTERNAL_SIGNUM_EXPORT" in f["recommendations"]
    assert f["primary_recommendation"] == "CHECK_EXTERNAL_SIGNUM_EXPORT"
    assert f["severity"] == "ATTENTION"
    assert any("get-trendradar-daily" in c for c in f["operator_checks"])
    assert wd.validate_watchdog(f)["valid"] is True


# ---- PROOF: never auto-runs tasks or tokens --------------------------------

def test_never_runs_tasks_or_tokens():
    f = wd.build_watchdog(
        _health({"C22_Signum_GC_Download_Pickup":
                 {"last_result": 2, "hours_since_last_run": 6.0}}), _FRESH_C22)
    assert f["reran_any_task"] is False
    assert f["changed_any_scheduled_task"] is False
    assert f["auto_executes_any_token"] is False
    assert f["suggested_human_tokens"] == []        # surfaces no gate-advancing token
    assert f["advances_nothing"] is True
    for flag in ("runs_tasks", "reruns_pickup", "reruns_import", "changes_scheduled_task",
                 "triggers_scheduled_task", "installs_scheduler", "auto_executes_token",
                 "advances_any_gate"):
        assert f[flag] is False, flag
    for key, val in f["scope_locks"].items():
        assert val is True, key


# ---- anti-tamper -----------------------------------------------------------

def test_tamper_rejected():
    f = wd.build_watchdog(_health(), _FRESH_C22)
    # claim a rerun -> invalid
    assert wd.validate_watchdog({**f, "reran_any_task": True})["valid"] is False
    # NO_ACTION but ALERT severity -> invalid
    assert wd.validate_watchdog({**f, "severity": "ALERT"})["valid"] is False
    # surface a gate token -> invalid
    assert wd.validate_watchdog(
        {**f, "suggested_human_tokens": ["HUMAN_APPROVED_X"]})["valid"] is False
    for flag in wd._CAPABILITY_FLAGS_FALSE:
        assert wd.validate_watchdog({**f, flag: True})["valid"] is False


# ---- runner builds a valid finding read-only -------------------------------

def test_runner_builds_valid_finding():
    f = runner.build_watchdog_finding()
    assert wd.validate_watchdog(f)["valid"] is True
    assert f["reran_any_task"] is False


# ---- runner does no rerun / scheduler-mutation / network / trading ---------

_FORBIDDEN_RUNNER_TOKENS = (
    "Register-ScheduledTask", "New-ScheduledTask", "Set-ScheduledTask",
    "Start-ScheduledTask", "schtasks /create", "schtasks /run", "schtasks /change",
    "import_one", "run_import_automation", "run_pickup", "git commit", "git push",
    "place_order", "import requests", "import ccxt",
)


def test_runner_no_rerun_no_mutation():
    src = Path(runner.__file__).read_text(encoding="utf-8")
    for tok in _FORBIDDEN_RUNNER_TOKENS:
        assert tok not in src, tok


# ---- contract module purity ------------------------------------------------

def test_contract_module_purity():
    src = Path(wd.__file__).read_text(encoding="utf-8")
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "open(",
                 "subprocess", "Popen", "urlopen", "json.load", "read_text", "glob(",
                 "Get-ScheduledTask"):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "subprocess",
              "os", "io", "shutil", "json", "hashlib", "pathlib", "numpy", "pandas"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned), imported & banned
