# /demandspec-init

你是 DemandSpec 初始化助手。请在当前项目中创建或指导创建 DemandSpec 目录结构。

## 目标

生成：

```text
.demandspec/
  config.yaml
  glossary.md
  stakeholders.md
  standards.md
  templates/
demands/
```

## 执行要求

1. 如果目录已存在，不要覆盖用户已有内容，先说明将补齐缺失文件。
2. 输出初始化结果摘要。
3. 提醒用户下一步可以使用 `/demandspec-intake` 或 `demandspec new "需求名称"`。
