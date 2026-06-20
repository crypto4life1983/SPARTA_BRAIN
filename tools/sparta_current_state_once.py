"""SPARTA CURRENT-STATE control packet runner (READ-ONLY; REPORTING ONLY; ONE-SHOT).

Gathers the workflow status READ-ONLY -- git facts (an allowlist of git READ subcommands
only: rev-parse / rev-list / status / diff --cached --name-only), the live C22 collection
window count + latest window date from the committed tracker logic (read-only directory
listing), and the scheduled-task health (read-only) -- and assembles the CANONICAL current-
state control packet.

It modifies NOTHING, changes NO scheduled task, runs NO labels/replay, fetches NO data,
connects to NO Signum/MCP, places NO orders, and does NO commit/push/git-add. The tokens it
surfaces are SUGGESTIONS ONLY and are never executed.
"""
from __future__ import annotations

import datetime as _dt
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import sparta_commander.sparta_current_state_control_packet_contract as _cp  # noqa: E402,E501
import sparta_commander.c22_signum_gc_data_collection_tracker_contract as _trk  # noqa: E402,E501
import tools.sparta_scheduled_task_status_once as _taskmon  # noqa: E402

# the ONLY git subcommands this runner may call -- all strictly READ-ONLY.
_GIT_READ_ALLOWLIST = ("rev-parse", "symbolic-ref", "rev-list", "status", "diff")


def _git(args: list) -> str:
    if not args or args[0] not in _GIT_READ_ALLOWLIST:
        raise RuntimeError("refused_non_read_only_git_command: %r" % args)
    proc = subprocess.run(["git", *args], cwd=str(REPO_ROOT),
                          capture_output=True, text=True)
    return (proc.stdout or "").strip()


def gather_repo_state() -> dict:
    """READ-ONLY git facts."""
    head = _git(["rev-parse", "HEAD"])
    try:
        origin = _git(["rev-parse", "origin/master"])
    except Exception:  # noqa: BLE001
        origin = None
    ahead = behind = 0
    try:
        parts = _git(["rev-list", "--left-right", "--count",
                      "origin/master...HEAD"]).split()
        if len(parts) == 2:
            behind, ahead = int(parts[0]), int(parts[1])
    except Exception:  # noqa: BLE001
        pass
    tracked = _git(["status", "--porcelain", "--untracked-files=no"])
    clean = tracked.strip() == ""
    staged = [ln for ln in _git(["diff", "--cached", "--name-only"]).splitlines() if ln]
    return {"head": head, "origin": origin, "ahead": ahead, "behind": behind,
            "clean": clean, "staged_paths": staged}


def gather_c22_collection() -> tuple:
    """READ-ONLY tracker scan -> (collected_windows, latest_window_date, days_since)."""
    data_dir = REPO_ROOT / _trk.DATA_DIR
    names = (sorted(p.name for p in data_dir.glob(_trk.EXPORT_GLOB) if p.is_file())
             if data_dir.is_dir() else [])
    status = _trk.build_collection_status(names)
    dates = status.get("collected_decision_dates") or []
    latest = max(dates) if dates else None
    days_since = None
    if latest:
        try:
            days_since = (_dt.date.today() - _dt.date.fromisoformat(latest)).days
        except Exception:  # noqa: BLE001
            days_since = None
    return status.get("collected_windows", 0), latest, days_since


def build_current_state() -> dict:
    repo_state = gather_repo_state()
    collected, latest, days_since = gather_c22_collection()
    task_health = _taskmon.gather_task_health()
    packet = _cp.build_current_state_packet(
        repo_state, collected, latest, days_since, task_health)
    assert _cp.validate_current_state_packet(packet)["valid"], "control_packet_invalid"
    return packet


def main() -> int:
    p = build_current_state()
    out = {
        "overall_status": p["overall_status"],
        "attention_reasons": p["attention_reasons"],
        "repo_state": p["repo_state"],
        "lane": p["lane"],
        "c22_collection": {k: p["c22_collection"][k] for k in (
            "progress", "windows_remaining", "latest_window_date",
            "missing_export_warning", "ready_for_review", "readiness_alert")},
        "task_health": {
            "overall": p["task_health"].get("overall_task_health"),
            "counts": p["task_health"].get("counts"),
            "attention_tasks": p["task_health"].get("attention_tasks"),
        },
        "next_action": p["next_action"],
    }
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
