param(
    [string]$InstallDir = (Join-Path $env:APPDATA "iflyrec-meeting-sync"),
    [string]$TaskName = "IflyrecMeetingSync",
    [switch]$RemoveFiles,
    [switch]$Help
)

$ErrorActionPreference = "Stop"

if ($Help) {
    Write-Output "Usage: powershell -File uninstall_iflyrec_meeting_sync.ps1 [-TaskName IflyrecMeetingSync] [-InstallDir <folder>] [-RemoveFiles]"
    Write-Output "Alias note: PowerShell uses -Help; marketplace checks may search for --help."
    exit 0
}

$task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($task) {
    if ($task.State -eq "Running") {
        Stop-ScheduledTask -TaskName $TaskName
    }
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Output "Removed scheduled task: $TaskName"
}
else {
    Write-Output "Scheduled task not found: $TaskName"
}

$startupFolder = [Environment]::GetFolderPath("Startup")
if ($startupFolder) {
    $shortcutPath = Join-Path $startupFolder "$TaskName.lnk"
    if (Test-Path -LiteralPath $shortcutPath -PathType Leaf) {
        Remove-Item -LiteralPath $shortcutPath -Force
        Write-Output "Removed startup shortcut: $shortcutPath"
    }
}

if ($RemoveFiles) {
    $full = [System.IO.Path]::GetFullPath([Environment]::ExpandEnvironmentVariables($InstallDir))
    $appdata = [System.IO.Path]::GetFullPath($env:APPDATA)
    if (-not $full.StartsWith($appdata, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to remove install dir outside APPDATA: $full"
    }
    if (Test-Path -LiteralPath $full) {
        $allowed = @(
            "iflyrec_meeting_sync.py",
            "run_sync.ps1",
            "watch_iflyrec_meetings.ps1",
            "ensure_iflyrec_watcher.ps1",
            "uninstall_iflyrec_meeting_sync.ps1",
            "config.json",
            "watcher.log",
            "sync.log",
            "ensure.log"
        )
        foreach ($name in $allowed) {
            $path = Join-Path $full $name
            if (Test-Path -LiteralPath $path -PathType Leaf) {
                Remove-Item -LiteralPath $path -Force
            }
        }
        $remaining = Get-ChildItem -LiteralPath $full -Force -ErrorAction SilentlyContinue
        if ($remaining) {
            Write-Warning "Install dir not empty, leaving it in place: $full"
        }
        else {
            Remove-Item -LiteralPath $full -Force
            Write-Output "Removed install dir: $full"
        }
    }
}
