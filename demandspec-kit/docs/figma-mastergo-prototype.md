# Figma / MasterGo Prototype Skill

## 定位

`/demandspec-figma` 不是简单生成页面文字说明，而是生成可复制给 Figma AI、MasterGo AI、即时设计、墨刀或原型设计师的结构化原型规格。

## 输入

- 需求卡片
- 范围边界
- 角色与权限
- 当前流程与目标流程
- 字段清单
- 业务规则
- PRD 草案

## 输出

```text
04_prototype/
  page-list.md
  page-structure.md
  interaction-flow.md
  figma-frame-spec.md
  mastergo-frame-spec.md
  component-tree.md
  interaction-map.md
  prototype-generation-prompt.md
  prototype-review-checklist.md
```

## Frame 规格

每个页面必须描述：

- Frame 名称
- 页面用途
- 页面尺寸建议
- 信息架构
- 核心组件
- 状态：默认、空态、加载、错误、无权限
- 操作按钮
- 表单字段
- 数据来源
- 校验规则
- 跳转关系

## 组件树规格

```text
PageFrame
  Header
  Sidebar
  FilterBar
  ContentArea
    Card / Table / Form / Timeline / Chart
  FooterActionBar
  Modal / Drawer / Toast
```

## 原型验收清单

- 页面是否覆盖主流程？
- 是否覆盖异常流程？
- 是否覆盖空态、错误态、无权限态？
- 字段是否和数据字段清单一致？
- 操作按钮是否有明确跳转或状态变化？
- 是否标注人工确认节点？
- AI 输出是否标注置信度、解释、人工修正入口？
