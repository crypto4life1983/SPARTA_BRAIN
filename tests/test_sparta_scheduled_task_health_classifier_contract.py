"""Tests for the SPARTA scheduled-task health classifier (contract + read-only monitor).

Proves the classifier maps gathered task records to OK / STALE / FAILED / MISSING (a real
failure code => FAILED; benign not-yet-run codes are not failures; never-ran / over-stale =>
STALE; not registered => MISSING), that the summary counts/flags are consistent, that the
monitor is read-only (no scheduled-task create/change/delete/trigger/install; no scheduler
code), and module/runner purity + anti-tamper."""
from __future__ import annotations

import ast
from pathlib import Path

import sparta_commander.sparta_scheduled_task_health_classifier_contract as th
import tools.sparta_scheduled_task_status_once as runner


# ---- classify_task: the four statuses --------------------------------------

def test_classify_ok():
    assert th.classify_task(
        {"found": True, "last_result": 0, "hours_since_last_run": 5.0}) == "OK"
    # benign not-yet-run code, recently
    assert th.classify_task(
        {"found": True, "last_result": 267011, "hours_since_last_run": 2.0}) == "OK"


def test_classify_failed():
    assert th.classify_task(
        {"found": True, "last_result": 2, "hours_since_last_run": 1.0}) == "FAILED"
    assert th.classify_task(
        {"found": True, "last_result": 2147942402, "hours_since_last_run": 1.0}) == "FAILED"


def test_classify_stale():
    # over the staleness window
    assert th.classify_task(
        {"found": True, "last_result": 0, "hours_since_last_run": 48.0}) == "STALE"
    # never ran (unknown last run)
    assert th.classify_task(
        {"found": True, "last_result": 267011, "hours_since_last_run": None}) == "STALE"


def test_classify_missing():
    assert th.classify_task({"found": False}) == "MISSING"
    assert th.classify_task(None) == "MISSING"
    assert th.classify_task("nope") == "MISSING"


# ---- build_task_health: counts + flags consistent --------------------------

def test_build_task_health_summary():
    recs = [
        {"name": "C22_Signum_GC_Download_Pickup", "found": True, "last_result": 0,
         "hours_since_last_run": 6.0},
        {"name": "C22_Signum_GC_Import_Automation", "found": True, "last_result": 2,
         "hours_since_last_run": 6.0},                       # FAILED
        {"name": "SPARTA_Overnight_Autopilot", "found": False},  # MISSING
        {"name": "SPARTA Shadow Validator", "found": True, "last_result": 0,
         "hours_since_last_run": 50.0},                      # STALE
    ]
    h = th.build_task_health(recs)
    assert h["counts"] == {"OK": 1, "STALE": 1, "FAILED": 1, "MISSING": 1}
    assert h["any_failed"] is True and h["any_missing"] is True and h["any_stale"] is True
    assert h["all_ok"] is False
    assert h["overall_task_health"] == "ATTENTION"
    assert "C22_Signum_GC_Import_Automation" in h["priority_failed_or_missing"]
    assert "SPARTA_Overnight_Autopilot" in h["priority_failed_or_missing"]
    assert th.validate_task_health(h)["valid"] is True


def test_build_task_health_all_ok():
    recs = [{"name": n, "found": True, "last_result": 0, "hours_since_last_run": 3.0}
            for n in th.PRIORITY_TASKS]
    h = th.build_task_health(recs)
    assert h["all_ok"] is True
    assert h["overall_task_health"] == "OK"
    assert th.validate_task_health(h)["valid"] is True


# ---- anti-tamper -----------------------------------------------------------

def test_tamper_status_inconsistent_rejected():
    h = th.build_task_health(
        [{"name": "x", "found": True, "last_result": 2, "hours_since_last_run": 1.0}])
    # flip the FAILED task to OK -> inconsistent with classify_task
    h["tasks"][0]["status"] = "OK"
    assert th.validate_task_health(h)["valid"] is False


def test_tamper_capability_flag_rejected():
    h = th.build_task_health([])
    assert th.validate_task_health({**h, "creates_scheduled_task": True})["valid"] is False


# ---- read-only monitor: known tasks + capability flags ---------------------

def test_known_tasks_and_capability_flags():
    assert "C22_Signum_GC_Download_Pickup" in th.KNOWN_SPARTA_TASKS
    assert "C22_Signum_GC_Import_Automation" in th.KNOWN_SPARTA_TASKS
    assert "SPARTA_Overnight_Autopilot" in th.KNOWN_SPARTA_TASKS
    h = th.build_task_health([])
    for flag in th._CAPABILITY_FLAGS_FALSE:
        assert h[flag] is False, flag
    for key, val in h["scope_locks"].items():
        assert val is True, key


# ---- the runner gathers + classifies without crashing (read-only) ----------

def test_runner_gather_is_read_only_and_classifies():
    # gather_task_records must return one record per known task and never raise
    recs = runner.gather_task_records()
    assert {r["name"] for r in recs} == set(th.KNOWN_SPARTA_TASKS)
    health = runner.gather_task_health()
    assert th.validate_task_health(health)["valid"] is True


# ---- the monitor changes NO scheduled task (no mutation tokens) -------------

_FORBIDDEN_MUTATION_TOKENS = (
    "Register-ScheduledTask", "Unregister-ScheduledTask", "New-ScheduledTask",
    "Set-ScheduledTask", "Disable-ScheduledTask", "Enable-ScheduledTask",
    "Start-ScheduledTask", "Stop-ScheduledTask", "schtasks /create", "schtasks /change",
    "schtasks /delete", "schtasks /run", "/Create", "/Delete", "/Change",
    "place_order", "send-trading-signal", "import requests", "import ccxt",
)


def test_monitor_changes_no_scheduled_task():
    src = Path(runner.__file__).read_text(encoding="utf-8")
    for tok in _FORBIDDEN_MUTATION_TOKENS:
        assert tok not in src, tok
    # it DOES use the read-only query mechanism
    assert "Get-ScheduledTaskInfo" in src
    assert "Get-ScheduledTask" in src


# ---- contract module purity ------------------------------------------------

def test_contract_module_purity():
    src = Path(th.__file__).read_text(encoding="utf-8")
    assert "__main__" not in src
    # actionable I/O verbs only -- "Get-ScheduledTask"/"schtasks" appear solely in the
    # descriptive docstring (the pure contract makes no such call; the runner does).
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "open(",
                 "subprocess", "Popen", "urlopen", "json.load", "read_text"):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "subprocess",
              "os", "io", "shutil", "json", "hashlib", "pathlib", "numpy", "pandas"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned), imported & banned
