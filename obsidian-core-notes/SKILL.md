---
name: obsidian-core-notes
description: Maintain Obsidian vault core-file sidecar notes and relationship indexes. Use when working in an Obsidian vault or document/code workspace and creating, editing, moving, renaming, deleting, scanning, summarizing, or organizing files that may need synchronized `.core.md` notes, `资料索引.md` folder indexes, and wikilink relationships for Obsidian graph view.
---

# Obsidian Core Notes

Keep source files, generated `.core.md` notes, and Obsidian relationship indexes synchronized.

## Workflow

1. Confirm the vault/workspace root. Use the current working directory unless the user names another root.
2. Before writing, run a scan when scope is broad:
   ```bash
   python <skill-dir>/scripts/obsidian_core_notes.py scan --root <vault-root> --json
   ```
3. For create/edit/move/rename/delete operations, update the matching `.core.md` note and nearest `资料索引.md` in the same turn.
4. For bulk refreshes, run:
   ```bash
   python <skill-dir>/scripts/obsidian_core_notes.py refresh --root <vault-root>
   ```
5. Validate after any bulk operation:
   ```bash
   python <skill-dir>/scripts/obsidian_core_notes.py validate --root <vault-root>
   ```
6. Clean generated notes only when explicitly requested:
   ```bash
   python <skill-dir>/scripts/obsidian_core_notes.py clean-generated --root <vault-root>
   ```

## Rules

- Treat non-Markdown source files as attachments and generate distinct sidecar notes named `<source filename>.core.md`.
- Reference existing Markdown core files directly; do not duplicate them.
- Put folder navigation in `资料索引.md`; put the workspace entrypoint in `核心文件索引.md`.
- Use only generated markers for safe overwrite or deletion:
  - `<!-- CORE_FILE_NOTE_V1 -->`
  - `<!-- CORE_FOLDER_INDEX_V1 -->`
  - `<!-- CORE_WORKSPACE_INDEX_V1 -->`
- Never delete hand-written Markdown notes unless the user explicitly asks.
- Exclude dependencies, caches, logs, build output, model artifacts, static vendor bundles, and temporary Office lock files.

## References

- Read `references/core-file-rules.md` before changing core-file classification.
- Read `references/obsidian-linking.md` before changing note names, tags, markers, or relationship link conventions.

## Scripts

- `scripts/obsidian_core_notes.py scan`: count core candidates and summarize scope.
- `scripts/obsidian_core_notes.py refresh`: create or update `.core.md`, `资料索引.md`, and `核心文件索引.md`.
- `scripts/obsidian_core_notes.py validate`: verify generated marker counts and common corruption patterns.
- `scripts/obsidian_core_notes.py clean-generated`: remove only files with generated markers.
