# S10 Figma/MasterGo Prototype Generator 原型生成技能

## 1. 技能定位

Figma/MasterGo Prototype Generator 是 DemandSpec 中负责“把原型架构转化为设计工具可消费规格”的技能。它面向 Figma、MasterGo、墨刀、Axure、即时设计等原型工具，重点输出结构化页面、组件树、交互跳转和设计标注。

该技能适合与以下能力结合：

- Figma 插件
- MasterGo 插件
- MCP 工具
- 设计工具 API
- JSON to UI 自动生成器
- 企业内部组件库
- 前端低代码平台

## 2. 输入

- S09 产出的原型架构说明
- PRD 草稿
- 字段清单
- 业务规则
- 设计系统或组件库约束
- 目标端：PC / 移动端 / 平板 / 大屏
- 目标工具：Figma / MasterGo / 墨刀 / Axure / 即时设计

## 3. 输出

1. 页面 Frame 结构
2. 组件树 Component Tree
3. Auto Layout 约束建议
4. 字段与组件映射
5. 交互跳转表
6. 原型状态表
7. 设计标注说明
8. Figma/MasterGo JSON 规格
9. 原型生成 Prompt
10. 原型验收清单

## 4. 页面 Frame 命名规范

```text
业务域/需求名称/端类型/页面编号_页面名称/状态
```

示例：

```text
Risk/LoanAssistant/PC/P01_客户风险列表/Default
Risk/LoanAssistant/PC/P01_客户风险列表/Empty
Risk/LoanAssistant/PC/P02_风险详情/AI_Review
```

## 5. 组件命名规范

```text
[组件类型]_[业务含义]_[状态]
```

示例：

```text
Table_CustomerRisk_Default
Button_Submit_Primary
Drawer_AIReasoning_Open
Form_CreditReport_Edit
Tag_RiskLevel_High
```

## 6. 组件树输出模板

```markdown
# 页面组件树：P01 页面名称

- Frame: P01_页面名称
  - Header: 顶部标题区
    - Text: 页面标题
    - Button: 新建
  - FilterBar: 筛选区
    - Input: 关键词搜索
    - Select: 状态筛选
    - DatePicker: 时间范围
  - Content: 主内容区
    - Table: 数据表格
      - Column: 字段一
      - Column: 字段二
      - Column: 操作
  - SidePanel: 右侧辅助区
    - Card: AI 建议
    - Card: 风险提示
  - Footer: 底部操作区
```

## 7. Figma/MasterGo JSON 规格模板

```json
{
  "project": "DemandSpec Prototype",
  "target_tool": "Figma/MasterGo",
  "device": "PC",
  "pages": [
    {
      "id": "P01",
      "name": "页面名称",
      "frame": {
        "width": 1440,
        "height": 1024,
        "layout": "vertical",
        "auto_layout": true,
        "padding": 24,
        "gap": 16
      },
      "sections": [
        {
          "id": "header",
          "name": "顶部区域",
          "component": "Header",
          "children": [
            {"type": "Text", "name": "页面标题", "content": "页面名称"},
            {"type": "Button", "name": "主要操作", "text": "新建"}
          ]
        },
        {
          "id": "filter",
          "name": "筛选区域",
          "component": "FilterBar",
          "children": [
            {"type": "Input", "name": "关键词", "placeholder": "请输入关键词"},
            {"type": "Select", "name": "状态", "options": ["全部", "待处理", "已完成"]}
          ]
        },
        {
          "id": "content",
          "name": "主内容区",
          "component": "Table",
          "columns": [
            {"field": "name", "label": "名称", "width": 180},
            {"field": "status", "label": "状态", "width": 120},
            {"field": "action", "label": "操作", "width": 160}
          ]
        }
      ],
      "interactions": [
        {
          "trigger": "点击新建",
          "action": "navigate",
          "target": "P02"
        }
      ],
      "states": ["default", "loading", "empty", "error", "permission_denied"]
    }
  ]
}
```

## 8. 设计工具生成 Prompt 模板

```markdown
你是资深 B 端产品设计师。请基于以下 DemandSpec 原型规格，在 Figma/MasterGo 中生成一个低保真到中保真的产品原型。

## 设计目标
- 业务场景：xxx
- 目标用户：xxx
- 端类型：PC / 移动端
- 风格：企业级 B 端、清晰、信息密度适中、适合评审

## 页面清单
- P01：xxx
- P02：xxx

## 组件要求
- 使用企业 B 端常见组件：表格、筛选区、表单、抽屉、弹窗、标签、步骤条、卡片
- 组件命名遵循：组件类型_业务含义_状态
- 每个页面包含 Default、Empty、Error、Permission Denied 状态

## 交互要求
- 点击 xxx 跳转到 xxx
- 点击 xxx 打开抽屉
- 点击 xxx 触发二次确认

## 输出要求
- 页面 Frame 按页面编号命名
- 保留字段标注
- 保留交互连线
- 标注异常状态
- 适配 1440px PC 宽度
```

## 9. 交互跳转表模板

```markdown
| 来源页面 | 触发组件 | 触发动作 | 系统反馈 | 目标页面/状态 | 备注 |
|---|---|---|---|---|---|
```

## 10. 原型验收清单

```markdown
# 原型验收清单

## 页面完整性
- [ ] 页面清单中的每个页面均已生成
- [ ] 每个核心流程均有对应页面
- [ ] 每个异常流程均有对应状态或提示

## 字段完整性
- [ ] PRD 中的核心字段均已在页面体现
- [ ] 必填字段、只读字段、可编辑字段已区分
- [ ] 字段校验和错误提示已体现

## 交互完整性
- [ ] 主要按钮均有交互说明
- [ ] 页面跳转路径完整
- [ ] 弹窗、抽屉、二次确认已体现

## 权限完整性
- [ ] 不同角色的可见页面已说明
- [ ] 不同角色的可操作按钮已说明
- [ ] 权限不足状态已体现

## AI 场景完整性
- [ ] AI 输出结果有展示区域
- [ ] AI 判断依据有展示区域
- [ ] 人工确认/修改入口已体现
- [ ] AI 失败或低置信度状态已体现
```

## 11. 与 MasterGo/Figma 的落地方式

### 方式一：提示词驱动

把页面结构、组件树、交互表和设计 Prompt 交给具备设计生成能力的插件或 Agent。

### 方式二：JSON 驱动

将 JSON 规格交给内部插件，由插件创建 Frame、组件、连线和标注。

### 方式三：组件库映射

将 DemandSpec 的组件类型映射到企业设计系统：

| DemandSpec 类型 | Figma/MasterGo 组件 | 说明 |
|---|---|---|
| FilterBar | 筛选栏组件 | 查询条件区域 |
| DataTable | 表格组件 | 列表页主区域 |
| DetailDrawer | 抽屉组件 | 详情快速查看 |
| AIInsightCard | AI 建议卡片 | AI 场景专用 |
| ApprovalPanel | 审批面板 | 审批类需求 |
| FormSection | 表单分组 | 新增/编辑页 |

### 方式四：前端低代码联动

如果企业内部有低代码平台，可以把 JSON 规格进一步转换为前端页面 Schema。
