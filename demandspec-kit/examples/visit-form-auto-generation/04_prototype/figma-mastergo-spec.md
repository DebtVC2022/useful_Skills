# Figma / MasterGo 原型生成规格：拜访单自动生成

## 1. 页面清单
| Frame 名称 | 页面用途 | 主要组件 | 状态 |
|---|---|---|---|
| VisitRecordUpload | 上传拜访材料 | 上传区、客户选择、材料列表 | 默认/上传中/失败 |
| VisitDraftPreview | 查看 AI 草稿 | 字段表单、AI 摘要、置信度、修改入口 | 默认/低置信度/待确认 |
| VisitConfirmSubmit | 确认提交 | 提交按钮、风险提示、确认弹窗 | 默认/错误/成功 |

## 2. 组件树
```text
VisitDraftPreview
  Header
  CustomerInfoCard
  AIGeneratedSummaryCard
  FieldForm
    FieldItem
    ConfidenceBadge
    EditButton
  EvidencePanel
  FooterActionBar
    SaveDraftButton
    SubmitButton
```

## 3. 交互要求
- 用户上传录音/图片/邮件后，进入 AI 处理中状态。
- AI 生成草稿后，展示字段、置信度和证据来源。
- 低置信度字段必须高亮，并要求人工确认。
- 用户修改字段后，记录修改前后内容，用于数据飞轮。
