"""Tests for the overnight-autopilot -> morning-report scheduler wiring.

Static (no-execution) checks proving:
  * the wrapper runs the one-shot overnight runner, then ALWAYS runs the
    morning-report generator as a SEPARATE, UNCONDITIONAL step (not chained
    with && so it refreshes even on failure), and exits with the runner's code;
  * the scheduled-task installer points its action at the wrapper (cmd.exe /c)
    and validates the wrapper + report generator exist;
  * the wiring contains NO trading / broker / order / network / git
    commit / git push capability;
  * the morning-report generator (read-only) handles missing/failed runs
    (DID_NOT_RUN / FAILED) -- so a failed overnight run still updates the report.

These tests do NOT execute the wrapper and do NOT register any scheduled task."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_TOOLS_DIR = _REPO_ROOT / "tools"
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))

WRAPPER = _TOOLS_DIR / "run_overnight_autopilot_and_report.bat"
INSTALLER = _TOOLS_DIR / "install_overnight_autopilot_task.ps1"
RUNNER = _TOOLS_DIR / "overnight_autopilot_run_once.py"
REPORT_GEN = _TOOLS_DIR / "sparta_autopilot_morning_report.py"


# --- existence -------------------------------------------------------------- #

def test_all_wiring_files_exist():
    assert WRAPPER.exists(), WRAPPER
    assert INSTALLER.exists(), INSTALLER
    assert RUNNER.exists(), RUNNER
    assert REPORT_GEN.exists(), REPORT_GEN


# --- wrapper sequences runner then report ----------------------------------- #

def test_wrapper_runs_runner_then_report_unconditionally():
    src = WRAPPER.read_text(encoding="utf-8")
    assert "overnight_autopilot_run_once.py" in src
    assert "sparta_autopilot_morning_report.py" in src
    assert "generate" in src
    # the report call must come AFTER the runner call
    i_run = src.index("overnight_autopilot_run_once.py")
    i_rep = src.index("sparta_autopilot_morning_report.py")
    assert i_run < i_rep, "report must run after the runner"
    # the report must NOT be chained with && (so it runs even on failure)
    assert "&&" not in src
    # the runner's exit code is captured and used for the final exit
    assert "ERRORLEVEL" in src
    assert "RUN_RC" in src
    assert "exit /b %RUN_RC%" in src


def test_wrapper_report_step_is_separate_line_after_runner():
    lines = [ln.strip() for ln in WRAPPER.read_text(encoding="utf-8").splitlines()
             if ln.strip() and not ln.strip().startswith("REM")
             and not ln.strip().lower().startswith("rem")]
    run_idx = next(i for i, ln in enumerate(lines)
                   if "overnight_autopilot_run_once.py" in ln)
    rep_idx = next(i for i, ln in enumerate(lines)
                   if "sparta_autopilot_morning_report.py" in ln)
    # report is on its own later line, not the same line as the runner
    assert rep_idx > run_idx
    assert "overnight_autopilot_run_once.py" not in lines[rep_idx]


# --- installer points at the wrapper ---------------------------------------- #

def test_installer_action_points_at_wrapper():
    src = INSTALLER.read_text(encoding="utf-8")
    assert "run_overnight_autopilot_and_report.bat" in src
    # action runs the wrapper via cmd.exe /c
    assert "cmd.exe" in src
    assert "/c" in src
    assert "$wrapper" in src
    # validates wrapper + report generator presence
    assert "Test-Path $wrapper" in src
    assert "Test-Path $reportGen" in src
    # still references the runner + the report generator path
    assert "overnight_autopilot_run_once.py" in src
    assert "sparta_autopilot_morning_report.py" in src


# --- no trading / push / broker capability in the wiring -------------------- #

def test_wiring_has_no_trading_push_or_broker():
    for f in (WRAPPER, INSTALLER):
        src = f.read_text(encoding="utf-8").lower()
        for banned in ("git commit", "git push", "git add", "ccxt", "binance",
                       "alpaca", "place_order", "create_order", "broker login",
                       "api.telegram.org", "requests.post", "invoke-webrequest",
                       "invoke-restmethod"):
            assert banned not in src, (f.name, banned)


def test_wrapper_declares_research_only_and_no_commit_no_push():
    src = WRAPPER.read_text(encoding="utf-8").lower()
    assert "research-only" in src
    assert "no commit" in src and "no push" in src


# --- failed/missing run still produces a report (generator behavior) -------- #

def test_report_generator_handles_failed_and_missing_runs():
    import sparta_autopilot_morning_report as mr  # noqa: E402
    # missing run -> DID_NOT_RUN
    assert mr.classify_run_status(None) == "DID_NOT_RUN"
    # failed run -> FAILED
    failed = {"tasks_attempted": ["t"], "tasks_completed": [],
              "tasks_failed": ["t"], "tasks_skipped": [], "errors": ["boom"],
              "integrity_status": "INTACT"}
    assert mr.classify_run_status(failed) == "FAILED"
    # the generator's CLI 'generate' is what the wrapper invokes
    src = REPORT_GEN.read_text(encoding="utf-8")
    assert '"generate"' in src
