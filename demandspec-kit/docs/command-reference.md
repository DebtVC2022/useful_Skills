# DemandSpec Command Reference

## CLI 变更命令

| 命令 | 作用 |
|---|---|
| `demandspec change new` | 创建 lite/full 变更包 |
| `demandspec change list` | 列出活跃变更 |
| `demandspec change show` | 查看变更元数据 |
| `demandspec change set-status` | 执行受控状态流转 |
| `demandspec change approve` | 写入审批记录并进入 approved |
| `demandspec change validate --strict` | 执行结构、内容和追踪校验 |
| `demandspec change archive` | 合并 Delta 到基线并归档 |

`validate` 支持 `--json`，供 CI、Agent 和后续平台解析。

## 阶段命令

| 命令 | 作用 | 主要输出 |
|---|---|---|
| /demandspec-init | 初始化 DemandSpec 项目 | .demandspec、demands 目录 |
| /demandspec-intake | 受理原始需求 | demand-card.md |
| /demandspec-clarify | 生成澄清问题 | clarify-questions.md、assumptions.md |
| /demandspec-scope | 定义范围与版本切片 | scope-boundary.md |
| /demandspec-diagnose | 诊断需求类型和复杂度 | demand-type.md、complexity-assessment.md |
| /demandspec-ai-fit | AI 场景适配评估 | ai-fit-assessment.md |
| /demandspec-model | 业务流程建模 | business-process.md、target-process.md |
| /demandspec-data-rules | 数据与规则建模 | data-fields.md、business-rules.md |
| /demandspec-prototype | 原型架构 | page-list.md、page-structure.md |
| /demandspec-figma | Figma/MasterGo 原型规格 | figma-frame-spec.md、component-tree.md、interaction-map.md |
| /demandspec-prd | 生成 PRD | prd.md、user-stories.md、field-spec.md |
| /demandspec-acceptance | 生成验收标准 | acceptance-criteria.md、test-cases.md |
| /demandspec-review | 需求质量评审 | review-checklist.md、risk-list.md |
| /demandspec-handoff | 研发交付拆分 | frontend/backend/algorithm/data/test tasks |
| /demandspec-archive | 归档复盘 | retrospective.md、reusable-assets.md |

## 快捷命令

| 命令 | 适用场景 |
|---|---|
| /demandspec-full | 从原始需求跑完整流程 |
| /demandspec-ai-scenario | AI 场景专项 |
| /demandspec-meeting-to-prd | 会议纪要转 PRD |
| /demandspec-requirement-to-figma | 需求转原型规格 |
| /demandspec-prd-to-dev-tasks | PRD 转研发任务 |
