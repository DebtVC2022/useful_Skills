# DemandSpec：AI 辅助需求工程框架

DemandSpec 是一套面向需求侧的 AI 辅助需求工程框架，用于将业务想法、会议纪要、口述需求、领导指令、业务痛点或现有文档，结构化转化为需求卡片、澄清问题、业务模型、原型、PRD、验收标准、研发任务与复盘资产。

它可以有两种使用方式：

1. **作为总技能使用**：输入任意需求材料，由 DemandSpec Router 判断当前阶段并调用对应子技能。
2. **作为技能集使用**：每个阶段都是一个独立技能，可嵌入 WorkBuddy、Trae、自研 AIGC 平台、Dify、Coze、Figma/MasterGo 插件或企业知识库系统。

## 核心流程

```text
Intake → Clarify → Diagnose → Model → Prototype → Specify → Validate → Handoff → Archive
受理 → 澄清 → 诊断 → 建模 → 原型 → 成文 → 验证 → 交付 → 沉淀
```

## 关键特点

- 不只是 PRD 生成器，而是需求侧 harness。
- 支持从模糊业务想法到研发任务交付的完整链路。
- 支持 AI 场景专属评估，包括数据要求、模型路径、人工兜底、数据飞轮。
- 新增原型生成模块，支持 Figma / MasterGo / 墨刀 / Axure 等原型工具的结构化交付。
- 所有产物可文件化、版本化、评审化、复用化。

## 推荐目录

```text
demands/
  demand-id-demand-name/
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

## 文件说明

- `00_overview/`：框架总体说明。
- `01_skills/`：每个 DemandSpec 子技能规范。
- `02_templates/`：需求卡片、PRD、AI 可行性评估、原型说明等模板。
- `03_commands/`：可固化到智能体或命令系统中的命令定义。
- `04_examples/`：示例需求包。
- `05_checklists/`：评审清单与验收清单。
- `06_integration/`：与 Figma、MasterGo、Trae、OpenSpec 等集成建议。
- `07_skill_pack/`：可作为技能注册的 YAML/JSON 规格示例。
