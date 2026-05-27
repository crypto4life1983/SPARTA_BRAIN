$TaskName = "SPARTA Daily Journal Snapshot"

Write-Host "Verifying scheduled task: $TaskName"
Write-Host ""

$task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

if (-not $task) {
    Write-Host "Task exists: NO"
    exit 1
}

Write-Host "Task exists: YES"
Write-Host ""

Write-Host "Actions:"
$task.Actions | Format-List Execute, Arguments, WorkingDirectory

Write-Host "Triggers:"
$task.Triggers | Format-List *

Write-Host "Runtime info:"
Get-ScheduledTaskInfo -TaskName $TaskName | Format-List LastRunTime, LastTaskResult, NextRunTime, NumberOfMissedRuns

Write-Host ""
Write-Host "Safety: READ ONLY -- OBSERVATION ONLY -- NO LIVE READINESS CLAIM"
Write-Host "Safety: NO STRATEGY APPROVAL -- NO BROKER -- NO ORDER -- NO OPTIMIZATION"
