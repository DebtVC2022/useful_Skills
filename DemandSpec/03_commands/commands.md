# DemandSpec 命令体系

## 总命令

```text
/demandspec
```

用途：根据输入自动判断当前需求阶段，并调用对应技能。

## 常用命令

| 命令 | 技能 | 用途 |
|---|---|---|
| `/demandspec route` | S00 | 判断需求成熟度和下一步路径 |
| `/demandspec intake` | S01 | 生成需求卡片 |
| `/demandspec clarify` | S02 | 生成澄清问题 |
| `/demandspec scope` | S03 | 定义范围与版本切片 |
| `/demandspec diagnose` | S04 | 诊断类型、复杂度、优先级 |
| `/demandspec ai-fit` | S05 | AI 适配评估 |
| `/demandspec process` | S06 | 流程建模 |
| `/demandspec data-rule` | S07 | 数据与规则建模 |
| `/demandspec permission` | S08 | 角色权限建模 |
| `/demandspec prototype` | S09 | 原型架构设计 |
| `/demandspec prototype-generate --tool figma` | S10 | 生成 Figma 原型规格 |
| `/demandspec prototype-generate --tool mastergo` | S10 | 生成 MasterGo 原型规格 |
| `/demandspec prd` | S11 | 生成 PRD |
| `/demandspec acceptance` | S12 | 生成验收标准 |
| `/demandspec review` | S13 | 需求评审 |
| `/demandspec handoff` | S14 | 研发任务拆分 |
| `/demandspec archive` | S15 | 复盘沉淀 |

## 运行模式

```text
/demandspec --mode full
/demandspec --mode quick
/demandspec --mode review
/demandspec --mode ai-scenario
/demandspec --mode prototype
/demandspec --mode handoff
```

## 原型生成命令示例

```text
/demandspec prototype-generate \
  --tool mastergo \
  --device pc \
  --style b-end \
  --fidelity low-to-mid \
  --input 04_prototype/prototype-spec.md \
  --output 04_prototype/mastergo-prototype.json
```

```text
/demandspec prototype-generate \
  --tool figma \
  --device mobile \
  --style enterprise \
  --component-library internal-design-system \
  --input prd.md
```
