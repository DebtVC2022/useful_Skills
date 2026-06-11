# Codex Integration

## 安装方式

```bash
demandspec install codex --project .
```

或使用脚本：

```bash
bash scripts/install-demandspec.sh --target codex --project .
```

安装内容：

```text
~/.codex/prompts/demandspec-*.md
项目/AGENTS.md
项目/.demandspec/
项目/demands/
```

## 命令触发

在 Codex 中输入：

```text
/demandspec-intake
/demandspec-prd
/demandspec-figma
```

## 兼容建议

优先使用 `/demandspec-intake` 这种横线命名，不使用 `/demandspec:intake` 这种命名空间格式，以减少不同版本工具的兼容风险。
