"""SPARTA POST-PUSH SMOKE runner (READ-ONLY; REPORTING ONLY; ONE-SHOT).

Gathers the read-only post-push checks -- git facts (read-only), the Bundle A artifact guard,
the Bundle A current-state packet, the Bundle C watchdog, the Bundle D lifecycle orchestrator,
and a read-only GET of the /control route -- and prints one consolidated
POST_PUSH_SMOKE_OK / POST_PUSH_SMOKE_NEEDS_ATTENTION report.

It runs NO scheduled task, reruns NO pickup/import, auto-executes NO token, advances NO gate,
modifies NO file, changes NO scheduled task, makes NO outbound network call, connects to NO
Signum/MCP, and does NO commit/push. The only subprocess calls are READ-ONLY git queries and
(via the reused Bundle A/C/D runners) read-only scheduled-task status queries.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import sparta_commander.sparta_post_push_smoke_contract as _ps  # noqa: E402
import sparta_commander.sparta_gitignored_artifact_guard_contract as _ga  # noqa: E402
import tools.sparta_current_state_once as _cs  # noqa: E402
import tools.sparta_scheduled_run_watchdog_once as _wdrun  # noqa: E402
import tools.sparta_candidate_lifecycle_orchestrator_once as _lorun  # noqa: E402

_GIT_READ_ALLOWLIST = ("ls-files", "diff")


def _git(args: list) -> list:
    if not args or args[0] not in _GIT_READ_ALLOWLIST:
        raise RuntimeError("refused_non_read_only_git_command")
    proc = subprocess.run(["git", *args], cwd=str(REPO_ROOT),
                          capture_output=True, text=True)
    return [ln for ln in (proc.stdout or "").splitlines() if ln.strip()]


def _control_route_check() -> dict:
    """READ-ONLY GET of /control via the in-process TestClient. Degrades gracefully."""
    try:
        from fastapi.testclient import TestClient
        import app as _app
        r = TestClient(_app.app).get("/control")
        text = r.text
        low = text.lower()
        return {
            "available": True, "status_code": r.status_code,
            "has_control_panel": "SPARTA — CONTROL PANEL" in text,
            "has_c22_hold": "HOLD_FOR_MORE_FROZEN_DATA_WINDOWS" in text,
            "has_watchdog_section": "Scheduled-run watchdog" in text,
            "has_lifecycle_section": "Candidate lifecycle" in text,
            "no_execution_affordances": not any(
                tok in low for tok in ("<script", "onclick", "<form", "<button")),
        }
    except Exception as exc:  # noqa: BLE001
        return {"available": False, "status_code": None, "error": type(exc).__name__,
                "has_control_panel": False, "has_c22_hold": False,
                "has_watchdog_section": False, "has_lifecycle_section": False,
                "no_execution_affordances": False}


def gather_inputs() -> dict:
    """READ-ONLY gather of all post-push smoke inputs."""
    repo = _cs.gather_repo_state()
    tracked = _git(["ls-files"])
    staged = _git(["diff", "--cached", "--name-only"])
    guard = _ga.build_guard(tracked, staged)
    cs = _cs.build_current_state()
    wd = _wdrun.build_watchdog_finding()
    lo = _lorun.build_lifecycle_finding()
    return {
        "repo": {"head": repo.get("head"), "origin": repo.get("origin"),
                 "ahead": repo.get("ahead"), "behind": repo.get("behind"),
                 "clean": repo.get("clean"),
                 "staged_count": len(repo.get("staged_paths") or []),
                 "dangerous_staged": cs["repo_state"].get("dangerous_staged_artifact")},
        "artifact_guard_clean": guard.get("clean"),
        "current_state": {
            "overall_status": cs.get("overall_status"),
            "c22_progress": cs["c22_collection"].get("progress"),
            "c22_state": cs["lane"].get("c22_state"),
            "task_health_overall": (cs.get("task_health") or {}).get(
                "overall_task_health")},
        "watchdog": {
            "severity": wd.get("severity"),
            "primary_recommendation": wd.get("primary_recommendation"),
            "reran_any_task": wd.get("reran_any_task"),
            "changed_any_scheduled_task": wd.get("changed_any_scheduled_task"),
            "auto_executes_any_token": wd.get("auto_executes_any_token")},
        "lifecycle": {
            "current_gate": lo.get("current_gate"),
            "suggested_human_token": lo.get("suggested_human_token"),
            "advances_any_candidate": lo.get("advances_any_candidate"),
            "opens_c23_as_active": lo.get("opens_c23_as_active"),
            "auto_executes_any_token": lo.get("auto_executes_any_token"),
            "modifies_repo": lo.get("modifies_repo")},
        "control_route": _control_route_check(),
    }


def build_smoke() -> dict:
    report = _ps.build_smoke_report(gather_inputs())
    assert _ps.validate_smoke_report(report)["valid"], "smoke_failed_validation"
    return report


def main() -> int:
    report = build_smoke()
    print(_ps.render_smoke_markdown(report))
    print()
    print(json.dumps({
        "overall": report["overall"],
        "all_clear": report["all_clear"],
        "attention_reasons": report["attention_reasons"],
        "failed_checks": report["failed_checks"],
        "checks": report["checks"],
        "executed_no_task": report["executed_no_task"],
        "executed_no_token": report["executed_no_token"],
        "advanced_no_gate": report["advanced_no_gate"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
