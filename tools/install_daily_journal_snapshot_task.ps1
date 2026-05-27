# SPARTA Daily Journal Snapshot - Scheduler Installer
#
# Safety labels:
#   READ_ONLY | OBSERVATION_ONLY | NO_LIVE_READINESS_CLAIM
#   NO_STRATEGY_APPROVAL | NO_BROKER | NO_ORDER | NO_OPTIMIZATION
#
# Registers exactly ONE Windows scheduled task named:
#   "SPARTA Daily Journal Snapshot"
#
# Trigger: Daily at 01:10 local machine time.
#
# Action:  C:\SPARTA_BRAIN\.venv\Scripts\python.exe
#          C:\SPARTA_BRAIN\tools\export_journal_snapshot.py
#
# Working directory: C:\SPARTA_BRAIN
#
# What the task actually does:
#   * Calls tools.trade_journal_adapter.load_payload() in read-only mode
#   * Writes a timestamped JSON + Markdown pair into C:\SPARTA_BRAIN\reports
#
# What the task explicitly DOES NOT do:
#   * No trading bot is started, no strategy is run.
#   * No broker / no API / no live trading.
#   * No exchange fetch and no portfolio rebalance.
#   * No optimization run, no parameter sweep.
#   * No write to trades.db; the adapter opens it with SQLite URI mode=ro.
#   * No write anywhere outside C:\SPARTA_BRAIN\reports.
#
# Settings:
#   * Skip if another instance is already running.
#   * Hard time limit of 10 minutes.
#   * Start when available if the scheduled time was missed.
#   * Restart on failure: 1 retry, 5-minute interval.
#
# Idempotent: re-running this installer replaces the same-named task.

$ErrorActionPreference = 'Stop'

$TaskName    = 'SPARTA Daily Journal Snapshot'
$ProjectRoot = 'C:\SPARTA_BRAIN'
$PythonExe   = Join-Path $ProjectRoot '.venv\Scripts\python.exe'
$Script      = Join-Path $ProjectRoot 'tools\export_journal_snapshot.py'

# Sanity guards: refuse to register if either of the two target paths is
# wrong. The point is that this installer can ONLY register a task that
# runs the snapshot exporter; nothing else.
if (-not (Test-Path -LiteralPath $PythonExe)) {
    throw "Python interpreter not found at $PythonExe; refusing to register task."
}
if (-not (Test-Path -LiteralPath $Script)) {
    throw "Snapshot exporter not found at $Script; refusing to register task."
}
$ScriptName = Split-Path -Leaf $Script
if ($ScriptName -ne 'export_journal_snapshot.py') {
    throw "Refusing to register task with non-canonical script: $ScriptName"
}

$Action = New-ScheduledTaskAction `
    -Execute $PythonExe `
    -Argument "`"$Script`"" `
    -WorkingDirectory $ProjectRoot

$Trigger = New-ScheduledTaskTrigger -Daily -At '01:10'

# Build the settings object with the broadly-supported parameters first;
# if any preferred-but-optional parameter is rejected by an older Windows
# ScheduledTasks module, fall back to a minimal-safe settings object.
$Settings = $null
try {
    $Settings = New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries `
        -StartWhenAvailable `
        -MultipleInstances IgnoreNew `
        -ExecutionTimeLimit (New-TimeSpan -Minutes 10) `
        -RestartCount 1 `
        -RestartInterval (New-TimeSpan -Minutes 5)
} catch {
    Write-Output "Falling back to minimal-safe scheduled task settings (reason: $($_.Exception.Message))"
    try {
        $Settings = New-ScheduledTaskSettingsSet `
            -MultipleInstances IgnoreNew `
            -ExecutionTimeLimit (New-TimeSpan -Minutes 10)
    } catch {
        Write-Output "Minimal settings rejected too; using default settings object."
        $Settings = New-ScheduledTaskSettingsSet
    }
}

$Principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType Interactive `
    -RunLevel Limited

# Replace any same-named task. Idempotent: one task, one name.
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

Register-ScheduledTask `
    -TaskName $TaskName `
    -Description 'SPARTA Daily Journal Snapshot - read-only export of /journal payload to reports\journal_snapshot_<UTC>.json|.md. Observation only. No live trading. No broker.' `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Principal $Principal | Out-Null

Write-Output "Registered scheduled task: $TaskName"
Write-Output "  Trigger:  daily 01:10 local"
Write-Output "  Action:   $PythonExe"
Write-Output "  Args:     `"$Script`""
Write-Output "  WorkDir:  $ProjectRoot"
Write-Output ""
Write-Output "Safety: READ ONLY -- OBSERVATION ONLY -- NO LIVE READINESS CLAIM"
Write-Output "Safety: NO STRATEGY APPROVAL -- NO BROKER -- NO ORDER -- NO OPTIMIZATION"
