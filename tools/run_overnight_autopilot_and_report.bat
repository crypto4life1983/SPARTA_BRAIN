@echo off
REM ===========================================================================
REM SPARTA Overnight Autopilot + Morning Report wrapper (RESEARCH-ONLY).
REM
REM This is the single command the Windows scheduled task runs. It:
REM   1. Runs the one-shot overnight autopilot runner.
REM   2. Captures the runner's exit code.
REM   3. ALWAYS runs the morning-report generator next, on its OWN UNCONDITIONAL
REM      line (plain sequential execution, never conditionally chained), so the
REM      report refreshes even if the overnight run failed or returned a
REM      non-zero exit code.
REM   4. Exits with the runner's exit code so Task Scheduler history reflects the
REM      run outcome, while reports/autopilot_morning/latest.{md,json} is updated
REM      regardless.
REM
REM Research-only: no trading, no broker, no credentials, no orders, no network,
REM no commit, no push. It does not change any research logic; it only sequences
REM the existing one-shot runner and the read-only report generator.
REM ===========================================================================
setlocal EnableExtensions
set "REPO=C:\SPARTA_BRAIN"
set "PY=%REPO%\.venv\Scripts\python.exe"
if not exist "%PY%" set "PY=python"
cd /d "%REPO%"

REM --- 1+2: run the overnight autopilot one-shot runner, capture its code ----
"%PY%" "%REPO%\tools\overnight_autopilot_run_once.py"
set "RUN_RC=%ERRORLEVEL%"

REM --- 3: ALWAYS refresh the morning report (runs even if the run failed) -----
"%PY%" "%REPO%\tools\sparta_autopilot_morning_report.py" generate

REM --- 4: exit with the runner's code (report already updated above) ----------
endlocal & exit /b %RUN_RC%
