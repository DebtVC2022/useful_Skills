# Trae Integration

## 安装方式

```bash
demandspec install trae --project .
```

安装内容：

```text
.trae/skills/demandspec/SKILL.md
.trae/skills/demandspec/templates/
.trae/rules/demandspec-rules.md
.demandspec/
demands/
```

## 使用方式

可以直接向 Trae 发送：

```text
使用 DemandSpec 对这段会议纪要进行需求受理，并输出 demand-card.md。
```

也可以使用约定命令：

```text
/demandspec-intake
/demandspec-figma
/demandspec-prd
```

Trae 若未原生识别自定义 slash command，可通过 Skill 和 Rules 的指令让 Agent 按命令文本执行。
