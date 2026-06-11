# DemandSpec Skill

## Name
DemandSpec - AI辅助需求工程框架

## Purpose
将业务想法、会议纪要、口述需求、已有 PRD、系统截图、AI 场景设想，按照 DemandSpec 流程转化为可评审、可原型化、可开发、可测试、可沉淀的需求资产。

## Core Workflow

```text
Intake → Clarify → Diagnose → Model → Prototype → Specify → Validate → Handoff → Archive
```

中文：

```text
受理 → 澄清 → 诊断 → 建模 → 原型 → 成文 → 验证 → 交付 → 沉淀
```

## Operating Principles

1. 不要直接跳到 PRD。先判断需求成熟度，再补齐中间资产。
2. 不确定信息必须列为“待确认项”或“当前假设”，不得假装已确认。
3. 涉及 AI 能力时必须调用 AI Fit 评估逻辑。
4. 涉及页面/交互时必须生成原型规格，不能只写功能列表。
5. 生成 PRD 后必须同步生成验收标准。
6. 准备研发时必须拆成前端、后端、算法、数据、测试任务。
7. 所有输出优先写入对应 DemandSpec 目录。

## Slash Commands

### Stage Commands
- `/demandspec-init`
- `/demandspec-intake`
- `/demandspec-clarify`
- `/demandspec-scope`
- `/demandspec-diagnose`
- `/demandspec-ai-fit`
- `/demandspec-model`
- `/demandspec-data-rules`
- `/demandspec-prototype`
- `/demandspec-figma`
- `/demandspec-prd`
- `/demandspec-acceptance`
- `/demandspec-review`
- `/demandspec-handoff`
- `/demandspec-archive`

### Shortcut Commands
- `/demandspec-full`
- `/demandspec-ai-scenario`
- `/demandspec-meeting-to-prd`
- `/demandspec-requirement-to-figma`
- `/demandspec-prd-to-dev-tasks`

## Demand Maturity Levels

| Level | Name | Definition |
|---|---|---|
| L0 | 原始想法 | 只有一句话想法 |
| L1 | 问题描述 | 有业务痛点，但目标不清 |
| L2 | 需求雏形 | 有目标和场景，但流程不完整 |
| L3 | 可建模需求 | 角色、流程、数据基本明确 |
| L4 | 可成文需求 | 已可生成 PRD 和原型说明 |
| L5 | 可交付需求 | 可拆分研发任务和验收标准 |
| L6 | 可沉淀需求 | 已上线或可复盘 |

## Output Directory Convention

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

## Subskills

### S00 Demand Router
判断当前输入属于哪个需求成熟度等级，推荐下一步技能。

### S01 Demand Intake
从原始材料生成需求卡片。

### S02 Demand Clarifier
生成澄清问题、假设、待确认项。

### S03 Scope Definer
明确范围、非范围、MVP、后续版本。

### S04 Demand Diagnoser
判断需求类型、复杂度、优先级、实施路径。

### S05 AI Fit Evaluator
判断 AI 是否适合、如何落地、数据要求、人工兜底、指标体系。

### S06 Process Modeler
生成当前流程、目标流程、异常流程。

### S07 Data & Rule Modeler
生成字段清单、数据来源、业务规则、校验规则。

### S08 Role & Permission Modeler
生成角色权限矩阵、操作边界。

### S09 Prototype Architect
生成页面清单、页面结构、用户路径、低保真原型说明。

### S10 Figma/MasterGo Prototype Generator
生成 Frame 规格、组件树、交互跳转表、Figma/MasterGo 原型生成 Prompt。

### S11 PRD Writer
生成标准 PRD、用户故事、字段说明。

### S12 Acceptance Generator
生成 Given-When-Then 验收标准、测试用例草案。

### S13 Requirement Reviewer
检查完整性、一致性、可实现性、可验收性、AI 风险。

### S14 Dev Handoff
拆分前端、后端、算法、数据、测试任务。

### S15 Archive & Learn
生成变更记录、复盘、可复用资产。

## Response Style

- 输出结构化、可直接复制进 Markdown 文件。
- 对缺失信息保持显式标记。
- 对 AI 场景必须说明“推荐路径”和“不建议直接自动化的风险”。
- 对原型需求必须输出页面/Frame/组件/交互，而不是只写页面名称。
