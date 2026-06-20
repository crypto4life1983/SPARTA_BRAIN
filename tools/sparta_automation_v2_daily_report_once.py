"""SPARTA Automation V2 -- Daily Decision Report one-off RUNNER
(READ-ONLY; RESEARCH ONLY).

The overnight/autopilot-callable runner that produces the Automation V2 daily decision
report artifact. It:

  1. gathers git facts READ-ONLY (an allowlist of git read subcommands ONLY:
     rev-parse / symbolic-ref / rev-list / status -- NEVER commit / push / fetch / add /
     pull / merge / checkout);
  2. builds the deterministic report via the pure
     sparta_automation_v2_daily_report_contract;
  3. writes a markdown + JSON artifact ONLY into the GITIGNORED reports path
     (reports/automation_v2_daily/);
  4. prints the artifact paths + SHA256s.

It does NOT commit, push, fetch, stage, or `git add` anything; it makes NO network call;
it connects to NO Signum / MCP / Hyperliquid; it uses NO API keys / credentials; it does
NO live / paper / broker / order action; it installs / triggers NO scheduler; it advances
/ promotes NOTHING. All side effects (the two artifact writes) happen only in main(); the
report content is read-only and recommend-only. While C22 is at DATA_NOT_READY the report
recommends DATASET STAGING -- never labels, never fabricated data.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import sparta_commander.sparta_automation_v2_daily_report_contract as _dr  # noqa: E402

# the ONLY git subcommands this runner may ever call -- all strictly READ-ONLY.
GIT_READ_ALLOWLIST = ("rev-parse", "symbolic-ref", "rev-list", "status")

OUT_DIR = REPO_ROOT / "reports" / "automation_v2_daily"


def _git_read(args: list) -> str:
    """Run a READ-ONLY git command from the allowlist. Refuses anything else."""
    if not args or args[0] not in GIT_READ_ALLOWLIST:
        raise RuntimeError("refused_non_read_only_git_command: %r" % args)
    proc = subprocess.run(["git", *args], cwd=str(REPO_ROOT),
                          capture_output=True, text=True)
    return (proc.stdout or "").strip()


def _gather_repo_state() -> dict:
    """READ-ONLY git facts -> the V2 repo_state. No mutation."""
    head = _git_read(["rev-parse", "HEAD"])
    try:
        origin = _git_read(["rev-parse", "origin/master"])
    except Exception:  # noqa: BLE001
        origin = None
    ahead = behind = 0
    try:
        lr = _git_read(["rev-list", "--left-right", "--count",
                        "origin/master...HEAD"])
        parts = lr.split()
        if len(parts) == 2:
            behind, ahead = int(parts[0]), int(parts[1])
    except Exception:  # noqa: BLE001
        pass
    porcelain = ""
    try:
        porcelain = _git_read(["status", "--porcelain"])
    except Exception:  # noqa: BLE001
        pass
    staged = 0
    untracked = 0
    for line in porcelain.splitlines():
        if not line:
            continue
        x = line[:2]
        if x.startswith("??"):
            untracked += 1
        elif x[0] not in (" ", "?"):
            staged += 1
    tracked_dirty = any(
        ln and not ln.startswith("??") and ln[:2] != "  "
        for ln in porcelain.splitlines())
    clean = not tracked_dirty
    return {
        "head": head, "origin": origin, "ahead": ahead, "behind": behind,
        "clean": clean, "staged_count": staged,
        "untracked_clutter_present": untracked > 0,
        "untracked_clutter_ignored_by_path": True,
    }


def _utc_now_iso() -> str:
    import time
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    repo_state = _gather_repo_state()
    run_ts = _utc_now_iso()
    report = _dr.build_daily_report(repo_state, run_ts)
    if not _dr.validate_daily_report(report)["valid"]:
        raise RuntimeError("daily_report_failed_validation_refusing_to_write")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    date_tag = run_ts.split("T")[0]
    md_path = OUT_DIR / ("%s_%s.md" % (_dr.ARTIFACT_MARKDOWN_BASENAME, date_tag))
    json_path = OUT_DIR / ("%s_%s.json" % (_dr.ARTIFACT_JSON_BASENAME, date_tag))

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(report["report_markdown"])
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True)

    out = {
        "markdown_path": str(md_path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "markdown_sha256": compute_sha256(md_path),
        "json_path": str(json_path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "json_sha256": compute_sha256(json_path),
        "artifact_gitignored": _dr.ARTIFACT_IS_GITIGNORED,
        "committed_to_git": False,
        "run_timestamp_utc": run_ts,
        "recommended_next_safe_task": report["recommended_next_safe_task"],
        "next_human_approval_token": report["next_human_approval_token"],
        "c22_data_not_ready": report["c22_data_not_ready"],
        "git_safe_to_automate": report["git_safe_to_automate"],
    }
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
