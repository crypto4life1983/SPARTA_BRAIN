"""Generate a cached JARVIS file-hygiene report (manual, offline).

Inspects the repo's git working-tree state ONCE with read-only git commands,
summarizes the untracked / modified / staged counts and the biggest untracked
directories, and writes a summary to storage/jarvis/file_hygiene_report.json.
The web app only ever READS that file — it never runs git or scans the tree
itself. Run this by hand (or from a trusted scheduler) whenever you want the
/jarvis console to show fresh hygiene status:

    python tools/jarvis_file_hygiene_report.py

Read-only by construction. The ONLY git commands used are `git status
--porcelain` and `git check-ignore` (both read-only). Nothing is deleted,
moved, staged, committed, or otherwise mutated. No file contents are read, no
secrets or env values are captured, and no response bodies are written — only
counts, directory names, and short status flags. Exit code is 0 whenever a
report is written, even if warnings are present.
"""
from __future__ import annotations

import json
import subprocess
import time
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = REPO_ROOT / "storage" / "jarvis"
REPORT_PATH = REPORT_DIR / "file_hygiene_report.json"

GIT_TIMEOUT = 15.0

# Areas that are expected to be ignored/generated noise, shown to the operator
# as context so a large untracked count is not alarming on its own.
KNOWN_SAFE_AREAS = [
    "storage/jarvis/ (cached JARVIS reports, gitignored)",
    "data/ (research artifacts, caches, generated json/csv)",
    "trading_research/ (research reports — committed separately, not by JARVIS)",
    "brain_memory/ (operator memory notes)",
    "*.bak / *.log (timestamped backups and logs)",
]


def _git(args: list[str]) -> tuple[int, str]:
    """Run a read-only git command from the repo root. Returns (rc, stdout).
    Never raises; on failure returns a nonzero rc and an empty/partial stdout."""
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=GIT_TIMEOUT,
        )
        return proc.returncode, proc.stdout
    except Exception as exc:  # noqa: BLE001 — fail-soft; report what we can
        return 1, ""


def _parse_porcelain(text: str) -> dict:
    """Classify `git status --porcelain` lines into staged / modified /
    untracked. Porcelain v1 format: XY<space>path. We only ever look at the
    two status chars and the path string — never file contents."""
    untracked: list[str] = []
    staged = 0
    modified = 0
    for raw in text.splitlines():
        if not raw or len(raw) < 3:
            continue
        x, y = raw[0], raw[1]
        path = raw[3:].strip()
        if x == "?" and y == "?":
            untracked.append(path)
            continue
        # Index (staged) column is the first char; worktree (modified) is the
        # second. A non-space/non-? in X means staged; in Y means modified.
        if x not in (" ", "?"):
            staged += 1
        if y not in (" ", "?"):
            modified += 1
    return {"untracked": untracked, "staged": staged, "modified": modified}


def _top_untracked_dirs(untracked: list[str], limit: int = 10) -> list[dict]:
    """Group untracked paths by their top-level directory and count them.
    Path strings only — no file is opened."""
    counts: dict[str, int] = {}
    for p in untracked:
        norm = p.strip().strip('"').replace("\\", "/")
        top = norm.split("/", 1)[0] if "/" in norm else "(repo root)"
        counts[top] = counts.get(top, 0) + 1
    ranked = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    return [{"dir": d, "count": c} for d, c in ranked[:limit]]


def _runtime_report_status() -> dict:
    """Report whether each cached JARVIS report exists and is gitignored.
    Read-only: checks existence + `git check-ignore`; never reads contents."""
    names = [
        "health_report.json",
        "route_smoke_report.json",
        "file_hygiene_report.json",
    ]
    out: dict = {}
    for name in names:
        rel = f"storage/jarvis/{name}"
        exists = (REPORT_DIR / name).exists()
        rc, _ = _git(["check-ignore", rel])
        out[name] = {"exists": exists, "gitignored": rc == 0}
    return out


def build_report() -> dict:
    """Probe git status once and assemble the inert hygiene summary."""
    started = time.monotonic()
    rc, porcelain = _git(["status", "--porcelain"])
    git_ok = rc == 0
    parsed = _parse_porcelain(porcelain)
    untracked = parsed["untracked"]

    warnings: list[str] = []
    if not git_ok:
        warnings.append("git status returned nonzero or was unavailable; "
                        "counts may be incomplete.")
    if parsed["staged"] > 0:
        warnings.append(
            f"{parsed['staged']} file(s) are STAGED. Review before any commit — "
            "JARVIS steps should stage only their own files."
        )

    return {
        "state": "ready",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "git_ok": git_ok,
        "total_untracked_count": len(untracked),
        "tracked_modified_count": parsed["modified"],
        "staged_count": parsed["staged"],
        "top_untracked_dirs": _top_untracked_dirs(untracked),
        "known_safe_areas": list(KNOWN_SAFE_AREAS),
        "runtime_report_status": _runtime_report_status(),
        "warnings": warnings,
        "duration_seconds": round(time.monotonic() - started, 3),
    }


def main() -> int:
    report = build_report()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"[jarvis_file_hygiene_report] untracked={report['total_untracked_count']} "
          f"modified={report['tracked_modified_count']} "
          f"staged={report['staged_count']} -> {REPORT_PATH}")
    for w in report["warnings"]:
        print(f"  ! {w}")
    for d in report["top_untracked_dirs"]:
        print(f"  - {d['dir']}: {d['count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
