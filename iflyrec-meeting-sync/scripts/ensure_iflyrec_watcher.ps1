param(
    [string]$TaskName = "IflyrecMeetingSync",
    [switch]$Help
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $PSCommandPath
$ensureLog = Join-Path $scriptDir "ensure.log"

if ($Help) {
    Write-Output "Usage: powershell -File ensure_iflyrec_watcher.ps1 [-TaskName IflyrecMeetingSync]"
    Write-Output "Alias note: PowerShell uses -Help; marketplace checks may search for --help."
    exit 0
}

function Write-EnsureLog {
    param([string]$Message)
    $line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Message
    Add-Content -Path $ensureLog -Value $line -Encoding UTF8
}

$task = Get-ScheduledTask -TaskName $TaskName -ErrorAction Stop
if ($task.State -eq "Running") {
    Write-EnsureLog "$TaskName already running; no action"
    Write-Output "$TaskName already running; no action"
    exit 0
}

Write-EnsureLog "$TaskName status=$($task.State); starting"
Start-ScheduledTask -TaskName $TaskName
Start-Sleep -Seconds 4
$newState = (Get-ScheduledTask -TaskName $TaskName).State
Write-EnsureLog "$TaskName after start status=$newState"
Write-Output "$TaskName after start status=$newState"

if ($newState -ne "Running") {
    exit 1
}
