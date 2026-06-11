# Figma / MasterGo 集成建议

## 1. 集成目标

DemandSpec 的原型生成模块并不是只输出“页面说明”，而是输出可被设计工具、插件或自动化 Agent 消费的结构化规格。

目标链路：

```text
需求模型 → 原型架构 → 页面组件树 → Figma/MasterGo JSON → 插件生成 Frame 和组件 → 人工调整 → 原型评审
```

## 2. 三种落地方式

### 方式一：提示词驱动

适合已有 AI 设计插件的团队。

流程：

```text
DemandSpec 生成原型 Prompt → 复制到 Figma/MasterGo AI 插件 → 生成初稿 → 设计师调整
```

优点：上手快。  
缺点：结构一致性依赖插件能力。

### 方式二：JSON 驱动

适合有研发能力的团队。

流程：

```text
DemandSpec 生成 JSON → 插件读取 JSON → 创建页面 Frame、组件、连线、标注
```

优点：可控、可版本化、可批量生成。  
缺点：需要开发插件或脚本。

### 方式三：组件库映射

适合有企业设计系统的团队。

流程：

```text
DemandSpec 组件类型 → 企业组件库映射 → 自动生成页面 → 保持设计一致性
```

## 3. 组件映射表

| DemandSpec 组件类型 | 设计工具组件 | 说明 |
|---|---|---|
| PageFrame | Frame | 页面容器 |
| Header | Header/NavBar | 顶部区域 |
| FilterBar | 筛选栏 | 查询条件 |
| DataTable | 表格 | 数据列表 |
| DetailDrawer | 抽屉 | 详情查看 |
| FormSection | 表单分组 | 新建/编辑 |
| Modal | 弹窗 | 确认、编辑、提示 |
| AIInsightCard | AI 建议卡片 | AI 场景专用 |
| AIReasonPanel | AI 判断依据面板 | 展示推理依据、召回材料 |
| ApprovalPanel | 审批区 | 审批类场景 |
| Timeline | 时间线 | 流程记录 |
| StatusTag | 状态标签 | 状态展示 |
| EmptyState | 空状态 | 无数据 |
| ErrorState | 错误状态 | 异常展示 |
| PermissionDenied | 权限不足状态 | 安全边界 |

## 4. MasterGo/Figma 原型生成最小字段

```json
{
  "page_id": "P01",
  "page_name": "页面名称",
  "device": "PC",
  "width": 1440,
  "height": 1024,
  "layout": "vertical",
  "sections": [],
  "components": [],
  "interactions": [],
  "states": []
}
```

## 5. 建议内部插件能力

- 创建 Frame
- 创建文本、按钮、输入框、表格、卡片、抽屉、弹窗
- 支持 Auto Layout
- 支持组件库映射
- 支持页面跳转连线
- 支持状态页生成
- 支持字段标注
- 支持从 PRD 自动更新原型

## 6. 原型与 PRD 的一致性检查

DemandSpec 应该检查：

- PRD 功能是否均有页面承载
- 页面字段是否均在字段清单中定义
- 页面操作是否均有业务规则
- 页面异常状态是否覆盖异常流程
- AI 输出是否有人工确认入口
- 权限规则是否反映在页面可见性和操作按钮中
