param(
    [string]$TargetDir,
    [string]$InstallDir = (Join-Path $env:APPDATA "iflyrec-meeting-sync"),
    [string]$TaskName = "IflyrecMeetingSync",
    [int]$SinceDays = 3,
    [int]$DebounceSeconds = 90,
    [int]$PollSeconds = 60,
    [int]$FullScanSeconds = 300,
    [ValidateSet("Auto", "TaskScheduler", "StartupShortcut")]
    [string]$LaunchMode = "Auto",
    [switch]$RunElevated,
    [switch]$NoIndexes,
    [switch]$NoStart,
    [switch]$DryRun,
    [switch]$Force,
    [switch]$Help
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $PSCommandPath

if ($Help) {
    Write-Output "Usage: powershell -File install_iflyrec_meeting_sync.ps1 -TargetDir <folder> [-InstallDir <folder>] [-TaskName IflyrecMeetingSync] [-LaunchMode Auto|TaskScheduler|StartupShortcut] [-FullScanSeconds 300] [-NoIndexes] [-NoStart] [-DryRun]"
    Write-Output "Alias note: PowerShell uses -Help; marketplace checks may search for --help."
    exit 0
}

if (-not $TargetDir) {
    throw "TargetDir is required. Use -Help for usage."
}

$runtimeFiles = @(
    "iflyrec_meeting_sync.py",
    "run_sync.ps1",
    "watch_iflyrec_meetings.ps1",
    "ensure_iflyrec_watcher.ps1",
    "uninstall_iflyrec_meeting_sync.ps1"
)

function Resolve-FullPath {
    param([string]$PathText)
    $expanded = [Environment]::ExpandEnvironmentVariables($PathText)
    if ([System.IO.Path]::IsPathRooted($expanded)) {
        return [System.IO.Path]::GetFullPath($expanded)
    }
    return [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $expanded))
}

$targetFull = Resolve-FullPath $TargetDir
$installFull = Resolve-FullPath $InstallDir
$iflyrecDataDir = Join-Path $env:APPDATA "iflyrecAssistant"
$iflyrecLogDir = Join-Path $iflyrecDataDir "logs"

Write-Output "TargetDir: $targetFull"
Write-Output "InstallDir: $installFull"
Write-Output "TaskName: $TaskName"
Write-Output "LaunchMode: $LaunchMode"

if (-not (Get-Command python.exe -ErrorAction SilentlyContinue) -and -not (Get-Command py.exe -ErrorAction SilentlyContinue)) {
    throw "Python not found. Install Python 3 or make python.exe/py.exe available in PATH."
}

if (-not (Test-Path -LiteralPath $iflyrecDataDir)) {
    Write-Warning "Iflyrec data dir not found yet: $iflyrecDataDir. Open and log in to 讯飞听见 first."
}

if ($DryRun) {
    Write-Output "DryRun: no files copied and no scheduled task registered."
    exit 0
}

if ((Test-Path -LiteralPath $installFull) -and -not $Force) {
    Write-Output "InstallDir exists. Existing runtime files will be overwritten; pass -Force to suppress this guard."
}

New-Item -ItemType Directory -Force -Path $installFull | Out-Null
New-Item -ItemType Directory -Force -Path $targetFull | Out-Null

foreach ($file in $runtimeFiles) {
    Copy-Item -LiteralPath (Join-Path $scriptDir $file) -Destination (Join-Path $installFull $file) -Force
}

$config = [ordered]@{
    target_dir = $targetFull
    iflyrec_data_dir = $iflyrecDataDir
    iflyrec_log_dir = $iflyrecLogDir
    since_days = $SinceDays
    update_obsidian_indexes = (-not $NoIndexes.IsPresent)
}
$configPath = Join-Path $installFull "config.json"
$config | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $configPath -Encoding UTF8

$watcherScript = Join-Path $installFull "watch_iflyrec_meetings.ps1"
$registeredTask = $false
$startupShortcut = $null

function New-IflyrecStartupShortcut {
    param(
        [string]$ShortcutTaskName,
        [string]$CommandPath,
        [string]$ConfigPath,
        [int]$Debounce,
        [int]$Poll,
        [int]$FullScan,
        [string]$WorkingDirectory
    )
    $startupFolder = [Environment]::GetFolderPath("Startup")
    if (-not $startupFolder) {
        throw "Windows Startup folder not found for current user."
    }
    $shortcutPath = Join-Path $startupFolder "$ShortcutTaskName.lnk"
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"
    $shortcut.Arguments = "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$CommandPath`" -ConfigPath `"$ConfigPath`" -DebounceSeconds $Debounce -PollSeconds $Poll -FullScanSeconds $FullScan"
    $shortcut.WorkingDirectory = $WorkingDirectory
    $shortcut.WindowStyle = 7
    $shortcut.Description = "Watch Xunfei Iflyrec client logs and sync generated meeting minutes to local Markdown."
    $shortcut.Save()
    return $shortcutPath
}

if ($LaunchMode -ne "StartupShortcut") {
    try {
        $watcherArgs = "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$watcherScript`" -ConfigPath `"$configPath`" -DebounceSeconds $DebounceSeconds -PollSeconds $PollSeconds -FullScanSeconds $FullScanSeconds"
        $action = New-ScheduledTaskAction -Execute "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" -Argument $watcherArgs -WorkingDirectory $installFull
        $trigger = New-ScheduledTaskTrigger -AtLogOn
        $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Days 9999)
        $registerArgs = @{
            TaskName = $TaskName
            Action = $action
            Trigger = $trigger
            Settings = $settings
            Description = "Watch Xunfei Iflyrec client logs and sync generated meeting minutes to local Markdown."
            Force = $true
        }
        if ($RunElevated) {
            $registerArgs.Principal = New-ScheduledTaskPrincipal -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Highest
        }
        Register-ScheduledTask @registerArgs | Out-Null
        $registeredTask = $true
    }
    catch {
        if ($LaunchMode -eq "TaskScheduler") {
            throw
        }
        Write-Warning "Task Scheduler registration failed: $($_.Exception.Message)"
        Write-Warning "Falling back to current user's Startup folder shortcut."
    }
}

if ((-not $registeredTask) -and ($LaunchMode -ne "TaskScheduler")) {
    $startupShortcut = New-IflyrecStartupShortcut -ShortcutTaskName $TaskName -CommandPath $watcherScript -ConfigPath $configPath -Debounce $DebounceSeconds -Poll $PollSeconds -FullScan $FullScanSeconds -WorkingDirectory $installFull
}

if (-not $NoStart) {
    if ($registeredTask) {
        Start-ScheduledTask -TaskName $TaskName
    }
    else {
        Start-Process -FilePath "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-WindowStyle", "Hidden", "-File", "`"$watcherScript`"", "-ConfigPath", "`"$configPath`"", "-DebounceSeconds", "$DebounceSeconds", "-PollSeconds", "$PollSeconds", "-FullScanSeconds", "$FullScanSeconds" -WorkingDirectory $installFull -WindowStyle Hidden
    }
}

Write-Output "Installed."
Write-Output "Config: $configPath"
if ($registeredTask) {
    Write-Output "Task: $TaskName"
}
if ($startupShortcut) {
    Write-Output "Startup shortcut: $startupShortcut"
}
Write-Output "Logs: $(Join-Path $installFull 'watcher.log'), $(Join-Path $installFull 'sync.log')"
