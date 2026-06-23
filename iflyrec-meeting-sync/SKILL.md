---
name: iflyrec-meeting-sync
description: Use when setting up, installing, diagnosing, or packaging Windows automation that exports generated Xunfei Iflyrec meeting minutes, AI summaries, and transcripts from the local Iflyrec desktop client into local Markdown files after WeCom or other online meetings.
---

# Iflyrec Meeting Sync

## Overview

Install a local Windows watcher that listens to Xunfei Iflyrec desktop client logs, finds completed meeting `orderId` values, and saves generated AI minutes plus transcripts as Markdown. The watcher combines log-event triggers with a periodic full scan fallback so missed `FileSystemWatcher` events are corrected automatically.

Use this only for a machine where the user has opened and logged in to 讯飞听见/Iflyrec. The skill does not bypass account login, recharge status, or meeting-platform permissions.

## Quick Start

1. Confirm prerequisites: Windows, Python 3, Xunfei Iflyrec desktop client, and a local target folder.
2. Run the installer from this skill folder:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\install_iflyrec_meeting_sync.ps1 -TargetDir "D:\Meeting Minutes"
```

3. Open WeCom meeting and record with Iflyrec `内录+外录`.
4. End recording and wait until Iflyrec shows generated 智能纪要.
5. Check the target folder for `智能纪要：...md`.

## Scripts

- `scripts/install_iflyrec_meeting_sync.ps1`: copy runtime files to `%APPDATA%\iflyrec-meeting-sync`, write `config.json`, and enable auto-start. Default `-LaunchMode Auto` tries Task Scheduler first and falls back to the current user's Startup folder shortcut when Windows policy blocks task registration.
- `scripts/iflyrec_meeting_sync.py`: parse Iflyrec logs, call generated-result APIs with the local Iflyrec session id, write Markdown, and persist per-`orderId` retry backoff in `sync_retry_state.json`.
- `scripts/watch_iflyrec_meetings.ps1`: long-running watcher with file events, polling fallback, and a default 300-second full scan interval.
- `scripts/run_sync.ps1`: sync entrypoint used by the watcher and installer.
- `scripts/ensure_iflyrec_watcher.ps1`: restart the watcher task when Task Scheduler mode is used.
- `scripts/uninstall_iflyrec_meeting_sync.ps1`: remove the scheduled task or Startup shortcut and optionally remove runtime files.
- `scripts/build_skillhub_package.ps1`: create a release folder and zip with `SKILL.md`, `agents/`, `scripts/`, `references/`, and `assets/`.

## Verification

Use these commands after install:

```powershell
python "%APPDATA%\iflyrec-meeting-sync\iflyrec_meeting_sync.py" self-test --config "%APPDATA%\iflyrec-meeting-sync\config.json"
python "%APPDATA%\iflyrec-meeting-sync\iflyrec_meeting_sync.py" scan --config "%APPDATA%\iflyrec-meeting-sync\config.json"
Get-ScheduledTask -TaskName IflyrecMeetingSync
```

Expected state:

- `self-test` finds the target folder, Iflyrec data dir, Iflyrec log dir, and `datastore.json`.
- `scan` prints recent candidate `order_id` records after Iflyrec has opened meeting result pages.
- scheduled task state is `Running` after install or after `ensure_iflyrec_watcher.ps1`, unless install fell back to a Startup shortcut.
- `watcher.log` startup lines include `fullScan=300s` unless the watcher was launched with a custom `-FullScanSeconds`.

## Troubleshooting

Read `references/windows-setup.md` when install, Task Scheduler, Iflyrec login state, or automatic download fails.

Common checks:

- If a meeting appears only after another later meeting signal, keep the event watcher but use the default full scan fallback; it runs `sync` every 5 minutes even when no new log signature is detected.
- Repeated `skip incomplete` or `skip error` entries are throttled by `sync_retry_state.json` with 10/20/40/60 minute backoff, reducing repeated Iflyrec API calls.

- No Markdown appears: verify Iflyrec generated 智能纪要, then inspect `%APPDATA%\iflyrec-meeting-sync\watcher.log` and `sync.log`.
- Task not running: run `scripts/ensure_iflyrec_watcher.ps1 -TaskName IflyrecMeetingSync`, or reinstall with `-LaunchMode StartupShortcut` if Task Scheduler is blocked by corporate policy.
- One bad meeting blocks sync: current script skips per-record errors and continues.
- Wrong target folder: edit `%APPDATA%\iflyrec-meeting-sync\config.json`, then restart the task.

## Safety Rules

- Do not include copied user logs, `datastore.json`, cookies, phone numbers, generated minutes, or target-folder contents in a public package.
- Do not hardcode personal vault paths in the skill. Always pass `-TargetDir` or edit runtime `config.json`.
- Treat Iflyrec AI minutes as generated content that needs human review before business use.
