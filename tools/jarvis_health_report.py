"""Generate a cached JARVIS health report (manual, offline).

Runs the JARVIS compile + test checks ONCE, captures a small summary, and
writes it to storage/jarvis/health_report.json. The web app only ever READS
that file — it never runs these checks itself. Run this by hand (or from a
trusted scheduler) whenever you want the /jarvis console to show fresh status:

    python tools/jarvis_health_report.py

Exit code is 0 only if every check passes; nonzero otherwise. No secrets or
environment dumps are ever written — only command, status, returncode, a short
output tail, and timing.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = REPO_ROOT / "storage" / "jarvis"
REPORT_PATH = REPORT_DIR / "health_report.json"

# Keep only a small tail so we never persist huge logs.
_TAIL_CHARS = 1600

CHECKS = [
    {
        "name": "py_compile",
        "command": [sys.executable, "-m", "py_compile", "app.py"],
    },
    {
        "name": "pytest",
        "command": [
            sys.executable, "-m", "pytest",
            "tests/test_jarvis_route.py", "--rootdir=tests", "-q",
        ],
    },
]


def _tail(text: str) -> str:
    text = (text or "").strip()
    if len(text) <= _TAIL_CHARS:
        return text
    return "...(truncated)...\n" + text[-_TAIL_CHARS:]


def _run_check(check: dict) -> dict:
    started = time.monotonic()
    result = {
        "name": check["name"],
        # Display string only; never executed from the web app.
        "command": " ".join(check["command"][1:]) if len(check["command"]) > 1
                   else check["command"][0],
    }
    try:
        proc = subprocess.run(
            check["command"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=600,
        )
        result["returncode"] = proc.returncode
        result["status"] = "pass" if proc.returncode == 0 else "fail"
        result["stdout_tail"] = _tail(proc.stdout)
        result["stderr_tail"] = _tail(proc.stderr)
    except Exception as exc:  # noqa: BLE001 — report errors, never crash hard
        result["returncode"] = None
        result["status"] = "error"
        result["stdout_tail"] = ""
        result["stderr_tail"] = f"{type(exc).__name__}: {exc}"
    result["duration_seconds"] = round(time.monotonic() - started, 3)
    return result


def main() -> int:
    checks = [_run_check(c) for c in CHECKS]
    overall_pass = all(c["status"] == "pass" for c in checks)
    report = {
        "state": "ready",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "overall": "pass" if overall_pass else "fail",
        "checks": checks,
    }
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"[jarvis_health_report] overall={report['overall']} -> {REPORT_PATH}")
    for c in checks:
        print(f"  - {c['name']}: {c['status']} (rc={c['returncode']})")
    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
