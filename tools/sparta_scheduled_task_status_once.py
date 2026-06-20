"""SPARTA scheduled-task STATUS MONITOR runner (READ-ONLY; REPORTING ONLY; ONE-SHOT).

Queries the known SPARTA Windows scheduled tasks READ-ONLY (Get-ScheduledTask /
Get-ScheduledTaskInfo only -- it CREATES, CHANGES, TRIGGERS, INSTALLS, and DELETES NO
scheduled task), gathers {name, found, last_result, hours_since_last_run} per task, and
classifies them OK / STALE / FAILED / MISSING via the pure health classifier.

It changes NO scheduled task, adds NO scheduler code, runs NO task, makes NO network call,
connects to NO Signum/MCP, and does NO commit/push. On a non-Windows host (or if PowerShell
is unavailable) it reports every task as not-found rather than failing.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import sparta_commander.sparta_scheduled_task_health_classifier_contract as _th  # noqa: E402,E501

# READ-ONLY PowerShell: per known task emit {name, found, last_result, hours_since_last_run}.
_PS_TEMPLATE = r"""
$names = @({names})
$out = @()
foreach ($n in $names) {
  $t = Get-ScheduledTask -TaskName $n -ErrorAction SilentlyContinue
  if ($null -eq $t) {
    $out += [pscustomobject]@{ name = $n; found = $false; last_result = $null; hours_since_last_run = $null }
    continue
  }
  $i = Get-ScheduledTaskInfo -TaskName $n -ErrorAction SilentlyContinue
  $lr = if ($i) { [int]$i.LastTaskResult } else { $null }
  $hrs = $null
  if ($i -and $i.LastRunTime -and $i.LastRunTime.Year -gt 1900) {
    $hrs = [math]::Round(((Get-Date) - $i.LastRunTime).TotalHours, 2)
  }
  $out += [pscustomobject]@{ name = $n; found = $true; last_result = $lr; hours_since_last_run = $hrs }
}
$out | ConvertTo-Json -Depth 3
"""


def _ps_quote(name: str) -> str:
    return "'" + name.replace("'", "''") + "'"


def gather_task_records() -> list:
    """READ-ONLY query of the known SPARTA tasks. Returns a list of gathered records. On any
    failure (non-Windows / no PowerShell / parse error) returns all-not-found records."""
    names = list(_th.KNOWN_SPARTA_TASKS)
    not_found = [{"name": n, "found": False, "last_result": None,
                  "hours_since_last_run": None} for n in names]
    script = _PS_TEMPLATE.replace("{names}", ", ".join(_ps_quote(n) for n in names))
    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
            capture_output=True, text=True, timeout=60)
    except Exception:  # noqa: BLE001 -- non-Windows / no PowerShell
        return not_found
    out = (proc.stdout or "").strip()
    if not out:
        return not_found
    try:
        parsed = json.loads(out)
    except Exception:  # noqa: BLE001
        return not_found
    if isinstance(parsed, dict):
        parsed = [parsed]
    by_name = {}
    for rec in parsed:
        if isinstance(rec, dict) and rec.get("name"):
            by_name[rec["name"]] = {
                "name": rec.get("name"), "found": bool(rec.get("found")),
                "last_result": rec.get("last_result"),
                "hours_since_last_run": rec.get("hours_since_last_run")}
    # preserve the known order; fill any gaps as not-found
    return [by_name.get(n, {"name": n, "found": False, "last_result": None,
                            "hours_since_last_run": None}) for n in names]


def gather_task_health() -> dict:
    """READ-ONLY task-health summary (gather + classify)."""
    return _th.build_task_health(gather_task_records())


def main() -> int:
    health = gather_task_health()
    assert _th.validate_task_health(health)["valid"], "task_health_failed_validation"
    print(json.dumps({
        "overall_task_health": health["overall_task_health"],
        "counts": health["counts"],
        "any_failed": health["any_failed"], "any_missing": health["any_missing"],
        "any_stale": health["any_stale"],
        "priority_failed_or_missing": health["priority_failed_or_missing"],
        "tasks": [{"name": t["name"], "status": t["status"], "is_priority": t["is_priority"],
                   "last_result": t["last_result"],
                   "hours_since_last_run": t["hours_since_last_run"]}
                  for t in health["tasks"]],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
