# DemandSpec Overview

DemandSpec 是一个需求侧 AI Harness 和变更控制框架。它将 OpenSpec 的
“基线规格、独立变更、增量合并、历史归档”应用到需求资产，同时保留
完整的需求澄清、建模、原型和交付流程。

## OpenSpec 核心

```text
需求意图
  ↓
changes/<change-id>/proposal.md
  ↓
Delta requirements + acceptance + tasks
  ↓
评审与批准
  ↓
实现与验证
  ↓
归档合并到 specs/<domain>/spec.md
```

`specs/` 是当前有效需求的唯一基线，`changes/` 只保存尚未归档的变更。

## 核心链路

```text
业务想法 / 会议纪要 / 现有文档
  ↓
需求卡片
  ↓
澄清问题与范围边界
  ↓
需求类型、复杂度、AI适配评估
  ↓
流程、数据、规则、权限建模
  ↓
原型架构与 Figma/MasterGo 规格
  ↓
PRD、用户故事、字段说明
  ↓
验收标准、测试用例、风险依赖
  ↓
研发任务拆分
  ↓
上线反馈与复盘沉淀
```

## 和普通 PRD 生成的区别

普通 PRD 生成关注“文档怎么写”。DemandSpec 关注“需求如何被澄清、建模、验证、交付和沉淀”。

## 推荐场景

- AI 应用场景收集与 POC 评审
- 企业内部流程优化需求
- 报表、看板、数据产品需求
- 表单自动化、审批流、移动端助手
- 风控、营销、服务、金融等业务系统需求
- 从会议纪要快速生成需求资产
