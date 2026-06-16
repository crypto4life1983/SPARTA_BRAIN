# SPARTA Overnight Autopilot - Windows Task Scheduler registration.
#
# MANUAL HUMAN ACTION ONLY. Per the frozen SCHEDULING_MODEL in
# sparta_commander/overnight_autopilot_research_queue_contract.py, this
# script is reviewed and run BY THE HUMAN, never by the assistant or any
# automated process. It registers a daily 02:00 local-time task that runs
# the ONE-SHOT runner (tools/overnight_autopilot_run_once.py) and exits.
#
# The runner is research-only: no trading, no credentials, no network,
# no commit, no push. It writes a per-run record under
# data/overnight_autopilot/reports/ naming exactly what ran and the next
# human gate.
#
# WIRING: the scheduled action runs a thin wrapper
# (tools\run_overnight_autopilot_and_report.bat) which runs the one-shot
# runner and THEN ALWAYS refreshes the human-readable morning report
# (reports\autopilot_morning\latest.{md,json}) -- even if the run failed.
#
# To remove:  Unregister-ScheduledTask -TaskName "SPARTA_Overnight_Autopilot" -Confirm:$false

$ErrorActionPreference = "Stop"

$taskName = "SPARTA_Overnight_Autopilot"
$repoRoot = "C:\SPARTA_BRAIN"
$python = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { $python = "python" }
$runner = Join-Path $repoRoot "tools\overnight_autopilot_run_once.py"
$wrapper = Join-Path $repoRoot "tools\run_overnight_autopilot_and_report.bat"
$reportGen = Join-Path $repoRoot "tools\sparta_autopilot_morning_report.py"

if (-not (Test-Path $runner)) {
    throw "Runner not found at $runner - aborting."
}
if (-not (Test-Path $wrapper)) {
    throw "Wrapper not found at $wrapper - aborting."
}
if (-not (Test-Path $reportGen)) {
    throw "Morning report generator not found at $reportGen - aborting."
}

# The action runs the wrapper (.bat) via cmd.exe /c. The wrapper runs the
# one-shot runner and THEN ALWAYS refreshes the morning report.
$action = New-ScheduledTaskAction `
    -Execute "cmd.exe" `
    -Argument "/c `"$wrapper`"" `
    -WorkingDirectory $repoRoot

$trigger = New-ScheduledTaskTrigger -Daily -At 2:00AM

$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -DontStopOnIdleEnd `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 30) `
    -MultipleInstances IgnoreNew

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description "SPARTA research-only overnight autopilot. Runs a thin wrapper that executes the one-shot queue processor (integrity audit, contract certification sweep, safety test report, seed brief draft) and THEN always refreshes the morning report (reports\autopilot_morning\latest.md/json), even on failure. No trading capability, no commit, no push. Installed manually by the human." | Out-Null

Write-Host "Registered scheduled task '$taskName' (daily 02:00, wrapper: run + report)."
Write-Host "Wrapper: cmd.exe /c $wrapper"
Write-Host "Runner:  $python $runner"
Write-Host "Report:  $python $reportGen generate"
Write-Host "Per-run records: $repoRoot\data\overnight_autopilot\reports\"
Write-Host "Morning report:  $repoRoot\reports\autopilot_morning\latest.md"
Write-Host "Remove with: Unregister-ScheduledTask -TaskName '$taskName' -Confirm:`$false"
