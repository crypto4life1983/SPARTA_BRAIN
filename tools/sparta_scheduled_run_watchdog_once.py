"""SPARTA scheduled-run WATCHDOG runner (READ-ONLY; SUGGESTION-ONLY; ONE-SHOT).

Reads the Bundle A scheduled-task health (read-only Get-ScheduledTaskInfo) + the C22
collection signals (read-only tracker listing), and prints the suggestion-only watchdog
finding (per-task OK/STALE/FAILED/MISSING/NEVER_RAN, C22 risks, remediation CHECKS).

It NEVER runs a task, NEVER reruns the pickup/import, NEVER changes Windows Task Scheduler,
NEVER installs scheduler code, NEVER auto-executes an approval token, makes NO network call,
connects to NO Signum/MCP, and does NO commit/push.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import sparta_commander.sparta_scheduled_run_watchdog_contract as _wd  # noqa: E402
import tools.sparta_scheduled_task_status_once as _taskmon  # noqa: E402
import tools.sparta_current_state_once as _cs  # noqa: E402


def build_watchdog_finding() -> dict:
    """READ-ONLY: gather task health + C22 signals and classify (no task is run/changed)."""
    task_health = _taskmon.gather_task_health()
    collected, latest, days_since = _cs.gather_c22_collection()
    c22 = {"collected_windows": collected, "latest_window_date": latest,
           "days_since_latest_window": days_since}
    finding = _wd.build_watchdog(task_health, c22)
    assert _wd.validate_watchdog(finding)["valid"], "watchdog_failed_validation"
    return finding


def main() -> int:
    f = build_watchdog_finding()
    print(json.dumps({
        "severity": f["severity"],
        "primary_recommendation": f["primary_recommendation"],
        "recommendations": f["recommendations"],
        "priority_states": f["priority_states"],
        "priority_failed": f["priority_failed"],
        "priority_missing": f["priority_missing"],
        "c22_risks": f["c22_risks"],
        "operator_checks": f["operator_checks"],
        "reran_any_task": f["reran_any_task"],
        "changed_any_scheduled_task": f["changed_any_scheduled_task"],
        "auto_executes_any_token": f["auto_executes_any_token"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
