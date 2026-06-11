# DemandSpec Kit v0.2.0

DemandSpec Kit 是一套向后兼容的“需求侧 OpenSpec”框架。它在原有
需求受理、建模、PRD、原型和交付档案之外，增加需求基线、独立变更、
Delta Spec、审批门禁、严格校验和归档合并。

本包已完成三个阶段：

- **第一阶段：Skill 化**  
  提供 DemandSpec 总技能、子技能、模板、规则、slash command prompt，可安装到 Trae、Codex、Claude Code、Cursor 等 AI 编程/协作工具中。

- **第二阶段：CLI 化**  
  提供 `demandspec` 命令行工具，可初始化需求工程项目、创建需求包、安装工具命令、查看需求状态、归档需求资产。
- **第三阶段：OpenSpec 核心化**
  提供 `specs/` 需求基线、`changes/` 活跃变更、lite/full profile、
  需求 ID 追踪、生命周期审批和 ADDED/MODIFIED/REMOVED 合并。

---

## 1. 快速开始

### 1.1 直接安装到当前项目

Windows PowerShell：

```powershell
cd demandspec-kit
.\scripts\install-demandspec.ps1 -ProjectPath "D:\your-project" -Target all
```

macOS / Linux / Git Bash：

```bash
cd demandspec-kit
bash scripts/install-demandspec.sh --project /path/to/your-project --target all
```

安装后，项目中会生成：

```text
.demandspec/
demands/
specs/
changes/archive/
AGENTS.md
.trae/skills/demandspec/
.trae/rules/demandspec-rules.md
.cursor/rules/demandspec.mdc
.claude/commands/demandspec-*.md
```

同时会向 Codex 命令目录安装：

```text
~/.codex/prompts/demandspec-*.md
~/.codex/skills/demandspec/
```

### 1.2 安装 CLI

推荐使用 editable 安装：

```bash
cd demandspec-kit
python -m pip install -e .
```

验证：

```bash
demandspec --version
```

### 1.3 初始化需求项目

```bash
demandspec init --project .
```

### 1.4 创建一个需求包

```bash
demandspec new "拜访单自动生成" --type ai --owner "算法团队"
```

生成目录：

```text
demands/20260611-visit-form-auto-generation/
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

### 1.5 创建一个需求变更

```bash
demandspec change new "拜访单自动生成" --domain crm --type ai --owner "算法团队"
```

低风险变更默认使用 `lite`；`ai`、`ui`、`high-risk`、`cross-system`
类型自动使用 `full` 并关联一个完整 `demands/` 需求档案。

```bash
demandspec change set-status <change-id> clarifying
demandspec change set-status <change-id> review
demandspec change approve <change-id> --approver "需求委员会"
demandspec change validate <change-id> --strict
demandspec change set-status <change-id> implementing
demandspec change set-status <change-id> verified
demandspec change archive <change-id>
```

变更生命周期：

```text
draft → clarifying → review → approved → implementing → verified → archived
```

---

## 2. Slash Commands

建议使用兼容性更强的横线命名方式：

```text
/demandspec-init
/demandspec-intake
/demandspec-clarify
/demandspec-scope
/demandspec-diagnose
/demandspec-ai-fit
/demandspec-model
/demandspec-data-rules
/demandspec-prototype
/demandspec-figma
/demandspec-prd
/demandspec-acceptance
/demandspec-review
/demandspec-handoff
/demandspec-archive
```

快捷命令：

```text
/demandspec-full
/demandspec-ai-scenario
/demandspec-meeting-to-prd
/demandspec-requirement-to-figma
/demandspec-prd-to-dev-tasks
```

---

## 3. DemandSpec 标准流程

```text
Intake → Clarify → Diagnose → Model → Prototype → Specify → Validate → Handoff → Archive
```

中文：

```text
受理 → 澄清 → 诊断 → 建模 → 原型 → 成文 → 验证 → 交付 → 沉淀
```

---

## 4. 目录说明

```text
demandspec-kit/
  README.md
  pyproject.toml
  demandspec_cli/                 # 第二阶段 CLI
  scripts/                        # 安装脚本
  skills/                         # 第一阶段 Skill 包
  commands/                       # slash command prompts
    codex/
    claude/
    generic/
  rules/                          # AGENTS、Trae、Cursor 规则
  templates/                      # 需求工程模板
  docs/                           # 框架文档
  examples/                       # 示例需求包
```

初始化后的项目核心目录：

```text
.demandspec/                  # 配置、标准和模板
specs/<domain>/spec.md        # 当前已批准需求基线
changes/<change-id>/          # 活跃变更及 Delta Specs
changes/archive/              # 已合并的完整变更历史
demands/<demand-id>/          # 兼容保留的九阶段需求工程档案
```

---

## 5. 推荐使用路径

### 从一句话需求到 PRD

```text
/demandspec-intake
/demandspec-clarify
/demandspec-scope
/demandspec-model
/demandspec-prototype
/demandspec-prd
/demandspec-acceptance
/demandspec-handoff
```

### 从会议纪要到可评审文档

```text
/demandspec-meeting-to-prd
/demandspec-review
```

### AI 场景专项

```text
/demandspec-ai-scenario
/demandspec-ai-fit
/demandspec-handoff
```

### 原型专项

```text
/demandspec-prototype
/demandspec-figma
```

---

## 6. 设计原则

1. **需求资产优先**：每一步都生成可追踪的中间产物，不直接跳到最终 PRD。
2. **先澄清再成文**：未确认项必须显式标记，不允许隐式编造。
3. **先验收再交付**：PRD 必须配套验收标准和测试场景。
4. **AI 场景单独评估**：涉及模型、RAG、Agent、自动决策时必须生成 AI 适配评估。
5. **原型规格化**：Figma/MasterGo 交付物必须包含页面 Frame、组件树、交互跳转、状态说明和原型验收清单。

---

## 7. 当前版本边界

v0.2.0 已完成需求侧 OpenSpec 核心闭环，但仍是本地文件和 CLI 框架。
它不包含在线协作平台、真实 Figma API、Jira/禅道 API 或企业认证。
