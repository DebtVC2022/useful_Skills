# Trae Rules: DemandSpec

当用户输入 `/demandspec-*` 或要求处理需求、PRD、原型、验收标准、研发任务时，优先调用 DemandSpec 规则。

## 执行要求

1. 判断需求成熟度，不要直接跳过澄清和建模。
2. 输出必须写入或建议写入 `demands/<demand-id>/` 对应目录。
3. 如果用户提供的是会议纪要，先生成 `00_intake/demand-card.md`。
4. 如果需求涉及 AI，必须生成 `02_diagnose/ai-fit-assessment.md`。
5. 如果需求涉及页面，必须生成 `04_prototype/figma-frame-spec.md` 和 `component-tree.md`。
6. 如果生成 PRD，必须同步生成 `06_validate/acceptance-criteria.md`。
7. 如果准备开发，必须生成 `07_handoff/` 下的任务拆分。

## 命令映射

- `/demandspec-intake`：需求卡片
- `/demandspec-clarify`：澄清问题
- `/demandspec-ai-fit`：AI 可行性
- `/demandspec-prototype`：原型架构
- `/demandspec-figma`：Figma/MasterGo 原型规格
- `/demandspec-prd`：PRD
- `/demandspec-review`：需求评审
- `/demandspec-handoff`：研发交付
