# Changelog

## v0.2.0 - 2026-06-11

### Added
- `specs/` requirement baseline and `changes/` change-control layer.
- Lite and full profiles with automatic full selection for complex change types.
- Stable requirement IDs, Delta Specs, acceptance and task traceability.
- Controlled lifecycle, approval records, strict validation, and JSON output.
- ADDED/MODIFIED/REMOVED archive merging.
- Packaged runtime resources and discoverable Codex Skill installation.
- Automated unit and end-to-end example tests.

### Fixed
- Non-ASCII demand names no longer collapse to the same `demand` slug.
- Existing demand directories are no longer silently reused.
- Wheel installations no longer depend on repository-relative resource paths.
- Empty change templates and incomplete changes cannot pass archive gates.

## v0.1.0 - 2026-06-11

### Added
- DemandSpec 总框架与 9 阶段流程。
- 15 个核心子技能：Router、Intake、Clarify、Scope、Diagnose、AI Fit、Process Model、Data Rules、Role Permission、Prototype、Figma/MasterGo、PRD、Acceptance、Review、Handoff、Archive。
- Codex slash command prompts。
- Claude Code command prompts。
- Trae Skill 包和 Rules。
- Cursor Rules。
- 项目级 AGENTS.md。
- Python CLI：`init`、`new`、`install`、`status`、`list-commands`、`archive`、`validate`。
- Windows PowerShell 和 Bash 安装脚本。
- 示例需求包：拜访单自动生成。
