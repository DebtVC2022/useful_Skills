# DemandSpec 框架总览

## 1. 定位

DemandSpec 是一套面向需求侧的 AI 辅助需求工程框架。它用于将业务侧的模糊想法、会议纪要、用户反馈、领导指令、业务痛点或 AI 场景设想，经过结构化处理，转化为可评审、可原型化、可开发、可测试、可复盘的需求资产。

DemandSpec 的核心不是“写文档”，而是将需求过程 harness 化：

```text
输入受控 → 澄清受控 → 建模受控 → 原型受控 → 文档受控 → 验收受控 → 交付受控 → 沉淀受控
```

## 2. 与开发侧 OpenSpec 的关系

开发侧 OpenSpec 解决的是：

```text
功能变更如何被规格化、设计化、任务化、验证化。
```

DemandSpec 解决的是：

```text
业务想法如何被澄清、建模、原型化、文档化、验收化、交付化。
```

两者可以形成链路：

```text
DemandSpec → OpenSpec → Code Harness → CI/CD → 上线复盘
```

## 3. 九阶段流程

| 阶段 | 中文 | 目标 | 主要产物 |
|---|---|---|---|
| Intake | 受理 | 把原始材料转成需求卡片 | 原始摘要、需求卡片 |
| Clarify | 澄清 | 识别缺失、歧义、冲突 | 澄清问题、假设、待确认项 |
| Diagnose | 诊断 | 判断类型、复杂度、AI 适配性 | 分类、复杂度、可行性判断 |
| Model | 建模 | 建立流程、角色、数据、规则模型 | 流程、字段、规则、权限 |
| Prototype | 原型 | 生成页面结构、低保真/高保真原型交付物 | 页面清单、交互说明、Figma/MasterGo 生成指令 |
| Specify | 成文 | 形成标准化需求文档 | BRD、PRD、用户故事、字段说明 |
| Validate | 验证 | 检查是否完整、可实现、可测试 | 评审清单、验收标准、测试用例 |
| Handoff | 交付 | 转成研发可执行任务 | 前端、后端、算法、数据、测试任务 |
| Archive | 沉淀 | 沉淀变更、反馈、复盘和复用资产 | 变更记录、复盘报告、知识条目 |

## 4. 技能体系

DemandSpec 包含 17 个核心技能：

| 编号 | 技能 | 作用 |
|---|---|---|
| S00 | Demand Router | 判断需求状态和下一步路径 |
| S01 | Demand Intake | 生成需求卡片 |
| S02 | Demand Clarifier | 生成澄清问题 |
| S03 | Scope Definer | 定义范围与版本切片 |
| S04 | Demand Diagnoser | 诊断需求类型、复杂度、优先级 |
| S05 | AI Fit Evaluator | AI 场景适配评估 |
| S06 | Process Modeler | 当前流程、目标流程、异常流程建模 |
| S07 | Data & Rule Modeler | 字段、数据源、业务规则建模 |
| S08 | Role & Permission Modeler | 用户角色与权限建模 |
| S09 | Prototype Architect | 原型信息架构与页面结构设计 |
| S10 | Figma/MasterGo Prototype Generator | 生成可导入设计工具的原型规格 |
| S11 | PRD Writer | 生成标准 PRD |
| S12 | Acceptance Generator | 生成验收标准与测试场景 |
| S13 | Requirement Reviewer | 需求评审与缺陷检查 |
| S14 | Dev Handoff | 拆分研发任务 |
| S15 | Archive & Learn | 复盘沉淀 |
| S16 | DemandSpec Orchestrator | 总技能编排器 |

## 5. 推荐运行模式

| 模式 | 说明 | 适用场景 |
|---|---|---|
| Full Mode | 全流程运行 | 从 0 到 1 的新需求 |
| Quick Mode | 快速生成需求卡片和 PRD | 简单需求、紧急交付 |
| Review Mode | 只做需求评审 | 已有 PRD 或原型 |
| AI Scenario Mode | AI 场景专用 | 智能体、模型、知识库、预测、生成类需求 |
| Prototype Mode | 原型专用 | 需要输出 Figma/MasterGo 原型规格 |
| Handoff Mode | 研发交付 | 需求已明确，准备拆任务 |
