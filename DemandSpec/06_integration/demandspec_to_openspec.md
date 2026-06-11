# DemandSpec 与 OpenSpec / 开发侧 Harness 衔接

## 1. 衔接定位

DemandSpec 管需求侧，OpenSpec 管开发侧。

```text
业务想法 → DemandSpec → PRD/原型/验收标准/研发任务 → OpenSpec → 代码实现
```

## 2. 交付给开发侧的最小资产

- PRD
- 原型规格
- 字段说明
- 业务规则
- 验收标准
- 测试场景
- 研发任务拆分
- 风险与依赖清单

## 3. 转换关系

| DemandSpec 产物 | OpenSpec/开发侧产物 |
|---|---|
| 需求范围 | Change Scope |
| 功能说明 | Requirements |
| 页面原型 | UI Implementation Plan |
| 字段说明 | Data Model / API Contract |
| 业务规则 | Domain Logic |
| 验收标准 | Test Cases |
| 风险依赖 | Implementation Risks |
| 研发任务 | Task List |

## 4. 建议命令

```text
/demandspec handoff --target openspec
```

输出：

```text
openspec-change/
  proposal.md
  design.md
  tasks.md
  specs/
    capability/spec.md
```
