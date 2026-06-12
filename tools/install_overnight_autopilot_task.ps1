# SPARTA Overnight Autopilot - Windows Task Scheduler registration.
#
# MANUAL HUMAN ACTION ONLY. Per the frozen SCHEDULING_MODEL in
# sparta_commander/overnight_autopilot_research_queue_contract.py, this
# script is reviewed and run BY THE HUMAN, never by the assistant or any
# automated process. It registers a daily 02:00 local-time task that runs
# the ONE-SHOT runner (tools/overnight_autopilot_run_once.py) and exits.
#
# The runner is research-only: no trading, no credentials, no network,
# no commit, no push. It writes a morning report under
# data/overnight_autopilot/reports/ naming exactly what ran and the next
# human gate.
#
# To remove:  Unregister-ScheduledTask -TaskName "SPARTA_Overnight_Autopilot" -Confirm:$false

$ErrorActionPreference = "Stop"

$taskName = "SPARTA_Overnight_Autopilot"
$repoRoot = "C:\SPARTA_BRAIN"
$python = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { $python = "python" }
$runner = Join-Path $repoRoot "tools\overnight_autopilot_run_once.py"

if (-not (Test-Path $runner)) {
    throw "Runner not found at $runner - aborting."
}

$action = New-ScheduledTaskAction `
    -Execute $python `
    -Argument "`"$runner`"" `
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
    -Description "SPARTA research-only overnight autopilot. One-shot queue processor: integrity audit, contract certification sweep, safety test report, seed brief draft. No trading capability, no commit, no push. Installed manually by the human." | Out-Null

Write-Host "Registered scheduled task '$taskName' (daily 02:00, one-shot runner)."
Write-Host "Runner: $python $runner"
Write-Host "Reports: $repoRoot\data\overnight_autopilot\reports\"
Write-Host "Remove with: Unregister-ScheduledTask -TaskName '$taskName' -Confirm:`$false"
