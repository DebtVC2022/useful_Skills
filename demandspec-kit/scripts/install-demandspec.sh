#!/usr/bin/env bash
set -euo pipefail

PROJECT="."
TARGET="all"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project)
      PROJECT="$2"
      shift 2
      ;;
    --target)
      TARGET="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1"
      exit 1
      ;;
  esac
done

KIT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_FULL="$(cd "$PROJECT" && pwd)"

echo "Installing DemandSpec Kit"
echo "KitRoot: $KIT_ROOT"
echo "Project: $PROJECT_FULL"
echo "Target: $TARGET"

mkdir -p "$PROJECT_FULL/.demandspec/templates" "$PROJECT_FULL/demands"
cp "$KIT_ROOT/configs/config.yaml" "$PROJECT_FULL/.demandspec/config.yaml"
cp "$KIT_ROOT/configs/glossary.md" "$PROJECT_FULL/.demandspec/glossary.md"
cp "$KIT_ROOT/configs/stakeholders.md" "$PROJECT_FULL/.demandspec/stakeholders.md"
cp "$KIT_ROOT/configs/standards.md" "$PROJECT_FULL/.demandspec/standards.md"
cp "$KIT_ROOT"/templates/*.md "$PROJECT_FULL/.demandspec/templates/"

if [[ "$TARGET" == "codex" || "$TARGET" == "all" ]]; then
  CODEX_HOME_DIR="${CODEX_HOME:-$HOME/.codex}"
  mkdir -p "$CODEX_HOME_DIR/prompts"
  cp "$KIT_ROOT"/commands/codex/*.md "$CODEX_HOME_DIR/prompts/"
  cp "$KIT_ROOT/rules/AGENTS.md" "$PROJECT_FULL/AGENTS.md"
  echo "Installed Codex prompts to $CODEX_HOME_DIR/prompts"
fi

if [[ "$TARGET" == "trae" || "$TARGET" == "all" ]]; then
  mkdir -p "$PROJECT_FULL/.trae/skills/demandspec/templates" "$PROJECT_FULL/.trae/rules"
  cp "$KIT_ROOT/skills/demandspec/SKILL.md" "$PROJECT_FULL/.trae/skills/demandspec/SKILL.md"
  cp "$KIT_ROOT"/templates/*.md "$PROJECT_FULL/.trae/skills/demandspec/templates/"
  cp "$KIT_ROOT/rules/trae-demandspec-rules.md" "$PROJECT_FULL/.trae/rules/demandspec-rules.md"
  echo "Installed Trae skill to $PROJECT_FULL/.trae/skills/demandspec"
fi

if [[ "$TARGET" == "claude" || "$TARGET" == "all" ]]; then
  mkdir -p "$PROJECT_FULL/.claude/commands"
  cp "$KIT_ROOT"/commands/claude/*.md "$PROJECT_FULL/.claude/commands/"
  cp "$KIT_ROOT/rules/AGENTS.md" "$PROJECT_FULL/AGENTS.md"
  echo "Installed Claude commands to $PROJECT_FULL/.claude/commands"
fi

if [[ "$TARGET" == "cursor" || "$TARGET" == "all" ]]; then
  mkdir -p "$PROJECT_FULL/.cursor/rules"
  cp "$KIT_ROOT/rules/cursor-demandspec.mdc" "$PROJECT_FULL/.cursor/rules/demandspec.mdc"
  echo "Installed Cursor rules to $PROJECT_FULL/.cursor/rules"
fi

echo "DemandSpec installation complete."
