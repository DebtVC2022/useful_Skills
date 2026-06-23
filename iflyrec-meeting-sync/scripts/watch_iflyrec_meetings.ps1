param(
    [int]$DebounceSeconds = 90,
    [int]$PollSeconds = 60,
    [int]$FullScanSeconds = 300,
    [string]$ConfigPath,
    [switch]$Help,
    [switch]$SelfTest
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $PSCommandPath
if ($Help) {
    Write-Output "Usage: powershell -File watch_iflyrec_meetings.ps1 [-ConfigPath config.json] [-DebounceSeconds 90] [-PollSeconds 60] [-FullScanSeconds 300] [-SelfTest]"
    Write-Output "Alias note: PowerShell uses -Help; marketplace checks may search for --help."
    exit 0
}
if (-not $ConfigPath) {
    $ConfigPath = Join-Path $scriptDir "config.json"
}

$config = Get-Content -LiteralPath $ConfigPath -Raw -Encoding UTF8 | ConvertFrom-Json
$iflyrecLogDir = $config.iflyrec_log_dir
if (-not $iflyrecLogDir) {
    $iflyrecLogDir = Join-Path $env:APPDATA "iflyrecAssistant\logs"
}

$syncScript = Join-Path $scriptDir "run_sync.ps1"
$watcherLog = Join-Path $scriptDir "watcher.log"

function Write-WatcherLog {
    param([string]$Message)
    $line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Message
    Add-Content -Path $watcherLog -Value $line -Encoding UTF8
}

function Invoke-MeetingSync {
    param([string]$Reason)
    Write-WatcherLog "sync start: $Reason"
    $process = Start-Process -FilePath "powershell.exe" `
        -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-WindowStyle", "Hidden", "-File", "`"$syncScript`"", "-ConfigPath", "`"$ConfigPath`"" `
        -WorkingDirectory $scriptDir `
        -WindowStyle Hidden `
        -Wait `
        -PassThru
    Write-WatcherLog "sync exit: code=$($process.ExitCode)"
}

function Get-MeetingLogSignalSignature {
    param([string]$Path)
    try {
        $matches = Get-Content -Path $Path -Tail 500 -Encoding UTF8 -ErrorAction Stop |
            Select-String -Pattern "orderId="
        if ($matches) {
            $last = $matches | Select-Object -Last 1
            return "$(Split-Path -Leaf $Path):$($last.Line)"
        }
        return $null
    }
    catch {
        return $null
    }
}

function Get-LatestLogWriteTime {
    $latest = Get-ChildItem -Path $iflyrecLogDir -Filter "debug-log.*.log" -File -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
    if ($latest) {
        return $latest.LastWriteTime
    }
    return $null
}

function Get-RecentMeetingLogSignalSignature {
    $logs = Get-ChildItem -Path $iflyrecLogDir -Filter "debug-log.*.log" -File -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 3
    foreach ($log in $logs) {
        $signature = Get-MeetingLogSignalSignature -Path $log.FullName
        if ($signature) {
            return $signature
        }
    }
    return $null
}

if (-not (Test-Path -Path $iflyrecLogDir)) {
    Write-WatcherLog "log dir missing: $iflyrecLogDir"
    exit 2
}

if (-not (Test-Path -Path $syncScript)) {
    Write-WatcherLog "sync command missing: $syncScript"
    exit 3
}

if ($SelfTest) {
    Write-WatcherLog "self-test ok: logDir=$iflyrecLogDir syncScript=$syncScript"
    exit 0
}

Write-WatcherLog "watcher start: logDir=$iflyrecLogDir debounce=${DebounceSeconds}s poll=${PollSeconds}s fullScan=${FullScanSeconds}s"

$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $iflyrecLogDir
$watcher.Filter = "debug-log.*.log"
$watcher.IncludeSubdirectories = $false
$watcher.NotifyFilter = [System.IO.NotifyFilters]'FileName, LastWrite, Size'
$watcher.EnableRaisingEvents = $true

$eventNames = @("Changed", "Created", "Renamed")
foreach ($eventName in $eventNames) {
    Register-ObjectEvent -InputObject $watcher -EventName $eventName -SourceIdentifier "IflyrecLog$eventName" | Out-Null
}

$pending = $false
$lastEventAt = Get-Date
$lastPollAt = Get-Date
$lastFullScanAt = Get-Date
$lastPolledWriteTime = Get-LatestLogWriteTime
$lastSignalSignature = $null
$startupSignal = Get-RecentMeetingLogSignalSignature
if ($startupSignal) {
    $lastSignalSignature = $startupSignal
    $pending = $true
    $lastEventAt = Get-Date
    Write-WatcherLog "startup meeting log signal: $startupSignal"
}

try {
    while ($true) {
        $event = Wait-Event -Timeout 5
        if ($null -ne $event) {
            $eventArgs = $event.SourceEventArgs
            $path = $eventArgs.FullPath
            Remove-Event -EventIdentifier $event.EventIdentifier
            if ($path -and (Split-Path -Leaf $path) -like "debug-log.*.log") {
                $signal = Get-MeetingLogSignalSignature -Path $path
                if ($signal -and $signal -ne $lastSignalSignature) {
                    $lastSignalSignature = $signal
                    $pending = $true
                    $lastEventAt = Get-Date
                    Write-WatcherLog "meeting log signal: $signal"
                }
                else {
                    Write-WatcherLog "log changed ignored: $(Split-Path -Leaf $path)"
                }
            }
        }
        elseif (((Get-Date) - $lastPollAt).TotalSeconds -ge $PollSeconds) {
            $lastPollAt = Get-Date
            $latestWriteTime = Get-LatestLogWriteTime
            if ($latestWriteTime -and (!$lastPolledWriteTime -or $latestWriteTime -gt $lastPolledWriteTime)) {
                $lastPolledWriteTime = $latestWriteTime
                $signal = Get-RecentMeetingLogSignalSignature
                if ($signal -and $signal -ne $lastSignalSignature) {
                    $lastSignalSignature = $signal
                    $pending = $true
                    $lastEventAt = Get-Date
                    Write-WatcherLog "poll meeting log signal: $signal"
                }
                else {
                    Write-WatcherLog "poll log changed ignored"
                }
            }
        }

        if ($FullScanSeconds -gt 0 -and ((Get-Date) - $lastFullScanAt).TotalSeconds -ge $FullScanSeconds) {
            $lastFullScanAt = Get-Date
            if ($pending) {
                Write-WatcherLog "full scan deferred: pending signal"
            }
            else {
                Invoke-MeetingSync -Reason "full scan interval ${FullScanSeconds}s"
            }
        }

        if ($pending -and ((Get-Date) - $lastEventAt).TotalSeconds -ge $DebounceSeconds) {
            $pending = $false
            Invoke-MeetingSync -Reason "iflyrec log quiet for ${DebounceSeconds}s"
        }
    }
}
finally {
    foreach ($eventName in $eventNames) {
        Unregister-Event -SourceIdentifier "IflyrecLog$eventName" -ErrorAction SilentlyContinue
    }
    $watcher.Dispose()
    Write-WatcherLog "watcher stop"
}
