# DemandSpec Architecture

## 两层架构

```text
第一层：Skill Layer
- SKILL.md
- commands/*.md
- templates/*.md
- rules/*.md

第二层：CLI Layer
- demandspec init
- demandspec new
- demandspec install
- demandspec status
- demandspec archive
```

## 三类资产

### 1. 框架资产
存放在 `.demandspec/`：

```text
.demandspec/
  config.yaml
  glossary.md
  stakeholders.md
  standards.md
  templates/
```

### 2. 需求资产
存放在 `demands/`：

```text
demands/<demand-id>/
  00_intake/
  01_clarify/
  02_diagnose/
  03_model/
  04_prototype/
  05_spec/
  06_validate/
  07_handoff/
  08_archive/
```

### 3. 工具适配资产
存放在不同工具的约定目录：

```text
AGENTS.md
.trae/skills/demandspec/SKILL.md
.trae/rules/demandspec-rules.md
.cursor/rules/demandspec.mdc
.claude/commands/demandspec-*.md
~/.codex/prompts/demandspec-*.md
```
