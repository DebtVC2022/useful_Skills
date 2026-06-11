# DemandSpec Kit v0.1.0

DemandSpec Kit 是一套“需求侧 OpenSpec”风格的 AI 辅助需求工程框架。它用于将业务想法、会议纪要、口述需求、现有 PRD、系统截图、AI 场景设想，结构化转化为可评审、可原型化、可开发、可测试、可沉淀的需求资产。

本包已完成两个阶段：

- **第一阶段：Skill 化**  
  提供 DemandSpec 总技能、子技能、模板、规则、slash command prompt，可安装到 Trae、Codex、Claude Code、Cursor 等 AI 编程/协作工具中。

- **第二阶段：CLI 化**  
  提供 `demandspec` 命令行工具，可初始化需求工程项目、创建需求包、安装工具命令、查看需求状态、归档需求资产。

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
AGENTS.md
.trae/skills/demandspec/
.trae/rules/demandspec-rules.md
.cursor/rules/demandspec.mdc
.claude/commands/demandspec-*.md
```

同时会向 Codex 命令目录安装：

```text
~/.codex/prompts/demandspec-*.md
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

v0.1.0 完成的是“可安装 Skill + 可运行 CLI”的基础版，不包含在线平台、真实 Figma API 调用、Jira/禅道 API 调用、企业认证集成。后续可以扩展为 MCP / 插件 / 服务端平台。
