# Windows setup and diagnostics

## Prerequisites

- Windows desktop session. The installer uses Task Scheduler when available and falls back to the current user's Startup folder shortcut when Task Scheduler registration is blocked.
- Python 3 available as `python.exe` or `py.exe`.
- Xunfei Iflyrec desktop client installed, opened, and logged in.
- Iflyrec meeting result page can show generated 智能纪要.
- Local target folder for Markdown output.

## Install

Run from the skill root:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\install_iflyrec_meeting_sync.ps1 -TargetDir "D:\Meeting Minutes"
```

Useful options:

- `-InstallDir`: runtime directory. Default is `%APPDATA%\iflyrec-meeting-sync`.
- `-TaskName`: scheduled task name. Default is `IflyrecMeetingSync`.
- `-LaunchMode`: `Auto`, `TaskScheduler`, or `StartupShortcut`. Default `Auto` tries Task Scheduler first, then creates a Startup shortcut if registration is denied.
- `-RunElevated`: request highest privileges for the scheduled task. Use only when the current Windows account can register elevated tasks.
- `-NoIndexes`: write minutes only, without Obsidian-style `资料索引.md`.
- `-NoStart`: install auto-start metadata but do not start the watcher immediately.
- `-DryRun`: validate paths and Python availability without writing files.

## Runtime flow

1. `watch_iflyrec_meetings.ps1` watches `%APPDATA%\iflyrecAssistant\logs\debug-log.*.log`.
2. It detects new Iflyrec result URLs containing `orderId=`.
3. After the debounce window, it runs `run_sync.ps1`.
4. Independently, the watcher runs a full `sync` fallback every 300 seconds by default (`-FullScanSeconds 300`) so a missed file-system event does not block import until the next meeting.
5. `iflyrec_meeting_sync.py` reads `%APPDATA%\iflyrecAssistant\datastore.json` for the local session id.
6. The script fetches existing generated AI summary, transcript, and insight data from Iflyrec APIs.
7. Failed or incomplete `orderId` records are stored in `sync_retry_state.json` and retried with 10/20/40/60 minute backoff.
8. It writes one Markdown file per new meeting to `target_dir`.

The script does not re-transcribe audio. It pulls already generated Iflyrec results.

## Diagnostics

Check task:

```powershell
Get-ScheduledTask -TaskName IflyrecMeetingSync
Get-ScheduledTaskInfo -TaskName IflyrecMeetingSync
```

If Task Scheduler is blocked, check the Startup shortcut:

```powershell
Get-ChildItem ([Environment]::GetFolderPath("Startup")) -Filter "IflyrecMeetingSync.lnk"
```

Check runtime:

```powershell
Get-Content "$env:APPDATA\iflyrec-meeting-sync\watcher.log" -Tail 40
Get-Content "$env:APPDATA\iflyrec-meeting-sync\sync.log" -Tail 80
python "$env:APPDATA\iflyrec-meeting-sync\iflyrec_meeting_sync.py" self-test --config "$env:APPDATA\iflyrec-meeting-sync\config.json"
python "$env:APPDATA\iflyrec-meeting-sync\iflyrec_meeting_sync.py" scan --config "$env:APPDATA\iflyrec-meeting-sync\config.json"
```

Common findings:

- `log dir missing`: open Iflyrec desktop client once and log in.
- `sid not found`: Iflyrec login state is unavailable. Log out and log in again.
- `skip incomplete`: Iflyrec has not finished generating transcript or AI minutes.
- `skip error ... 999998`: Iflyrec API returned a server error for that meeting. Later meetings continue.
- `skip retry backoff`: the previous attempt failed and the retry window has not elapsed yet; inspect `sync_retry_state.json` for the next retry time.
- meeting imports late only after another meeting signal: verify `watcher.log` contains `fullScan=300s`; restart the watcher if it was launched from an old script version.
- no `orderId`: open the generated meeting result page in Iflyrec so the client writes its result URL to logs.
- `Register-ScheduledTask : Access is denied`: reinstall with default `-LaunchMode Auto` or explicit `-LaunchMode StartupShortcut`.

## Uninstall

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$env:APPDATA\iflyrec-meeting-sync\uninstall_iflyrec_meeting_sync.ps1"
```

Add `-RemoveFiles` only when removing the runtime directory under `%APPDATA%`.
