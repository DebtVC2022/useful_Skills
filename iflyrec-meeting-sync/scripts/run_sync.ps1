param(
    [string]$ConfigPath,
    [switch]$Help
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $PSCommandPath
$syncLog = Join-Path $scriptDir "sync.log"

if ($Help) {
    Write-Output "Usage: powershell -File run_sync.ps1 [-ConfigPath config.json]"
    Write-Output "Alias note: PowerShell uses -Help; marketplace checks may search for --help."
    exit 0
}

if (-not $ConfigPath) {
    $ConfigPath = Join-Path $scriptDir "config.json"
}

function Write-SyncLog {
    param([string]$Message)
    $line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-ddTHH:mm:ss"), $Message
    Add-Content -Path $syncLog -Value $line -Encoding UTF8
}

Write-SyncLog "sync start"
try {
    $python = Get-Command python.exe -ErrorAction SilentlyContinue
    if (-not $python) {
        $python = Get-Command py.exe -ErrorAction SilentlyContinue
    }
    if (-not $python) {
        throw "Python not found."
    }

    $scriptPath = Join-Path $scriptDir "iflyrec_meeting_sync.py"
    & $python.Source $scriptPath sync --config $ConfigPath *>> $syncLog
    $exitCode = $LASTEXITCODE
    Write-SyncLog "sync exit $exitCode"
    exit $exitCode
}
catch {
    Write-SyncLog "sync failed: $($_.Exception.Message)"
    throw
}
