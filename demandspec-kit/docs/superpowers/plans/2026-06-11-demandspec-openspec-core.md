# DemandSpec OpenSpec Core Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a backward-compatible OpenSpec-style requirement change layer, strict lifecycle validation, delta archive merging, safe identifiers, installable skills/resources, and automated tests.

**Architecture:** Keep legacy demand packages intact. Add focused modules for package resources, configuration and metadata, change lifecycle, Markdown specification parsing, validation, and archive merging. Keep `cli.py` as the command adapter over these modules.

**Tech Stack:** Python 3.9+, standard library, PyYAML, unittest, Markdown files, setuptools.

---

### Task 1: Identifier Safety and Packaged Resources

**Files:**
- Create: `tests/test_identifiers.py`
- Create: `tests/test_resources.py`
- Create: `demandspec_cli/identifiers.py`
- Create: `demandspec_cli/resources.py`
- Create: `demandspec_cli/resources/__init__.py`
- Modify: `demandspec_cli/cli.py`
- Modify: `pyproject.toml`

- [ ] Write tests proving distinct Chinese names produce distinct stable IDs and existing IDs are not silently reused.
- [ ] Run `python -m unittest tests.test_identifiers -v` and verify the tests fail against the current fallback `demand`.
- [ ] Implement stable ASCII-or-hash slugs and collision rejection.
- [ ] Copy configs, templates, commands, rules, and skill assets into `demandspec_cli/resources/`.
- [ ] Add resource lookup through `importlib.resources`.
- [ ] Update project initialization and installers to use packaged resources.
- [ ] Run `python -m unittest tests.test_identifiers tests.test_resources -v` and verify success.

### Task 2: Change Model, Profiles, and Lifecycle

**Files:**
- Create: `tests/test_changes.py`
- Create: `demandspec_cli/config.py`
- Create: `demandspec_cli/changes.py`
- Create: `templates/change/proposal.md`
- Create: `templates/change/spec.md`
- Create: `templates/change/acceptance.md`
- Create: `templates/change/tasks.md`
- Create: `templates/change/design.md`
- Create: `templates/change/approval.md`
- Modify: `configs/config.yaml`

- [ ] Write tests for project `specs/`, `changes/`, and archive initialization.
- [ ] Write tests for lite/full artifact creation and automatic full selection for AI/UI/high-risk/cross-system changes.
- [ ] Write tests for allowed and rejected lifecycle transitions and approval from review state.
- [ ] Run `python -m unittest tests.test_changes -v` and verify missing APIs fail.
- [ ] Implement configuration loading, metadata persistence, profile resolution, change creation, listing, showing, status transitions, and approval.
- [ ] Run `python -m unittest tests.test_changes -v` and verify success.

### Task 3: Strict Validation and Traceability

**Files:**
- Create: `tests/test_validation.py`
- Create: `demandspec_cli/specs.py`
- Create: `demandspec_cli/validation.py`
- Modify: `demandspec_cli/cli.py`

- [ ] Write tests proving empty templates fail strict validation.
- [ ] Write tests for missing sections, invalid delta headings, missing requirement IDs, missing scenarios, unresolved placeholders, and broken requirement traceability.
- [ ] Write tests for full-profile linked demand requirements and approval/status consistency.
- [ ] Run `python -m unittest tests.test_validation -v` and verify failures.
- [ ] Implement Markdown requirement parsing and structured validation results.
- [ ] Add human and JSON validation output with strict behavior.
- [ ] Run `python -m unittest tests.test_validation -v` and verify success.

### Task 4: Delta Merge and Archive Gates

**Files:**
- Create: `tests/test_archive.py`
- Create: `demandspec_cli/archive.py`
- Modify: `demandspec_cli/cli.py`

- [ ] Write tests for ADDED, MODIFIED, and REMOVED requirements.
- [ ] Write tests proving unapproved, incomplete, unverified, invalid, and conflicting changes cannot archive.
- [ ] Run `python -m unittest tests.test_archive -v` and verify failures.
- [ ] Implement baseline parsing, conflict checks, canonical rendering, atomic writes, lifecycle update, and archive move.
- [ ] Run `python -m unittest tests.test_archive -v` and verify success.

### Task 5: CLI Compatibility and Skill Installation

**Files:**
- Create: `tests/test_cli.py`
- Modify: `demandspec_cli/cli.py`
- Modify: `skills/demandspec/SKILL.md`
- Create: `skills/demandspec/agents/openai.yaml`
- Modify: `rules/AGENTS.md`
- Modify: `commands/codex/demandspec-archive.md`
- Modify: `commands/claude/demandspec-archive.md`
- Modify: `commands/generic/demandspec-archive.md`

- [ ] Write CLI tests for `change new/list/show/set-status/approve/validate/archive`.
- [ ] Write compatibility tests for legacy `new/status/validate/archive`.
- [ ] Run `python -m unittest tests.test_cli -v` and verify failures.
- [ ] Add nested change commands and retain legacy commands.
- [ ] Add valid skill frontmatter, OpenAI UI metadata, and Codex skill installation.
- [ ] Update agent rules and archive prompts to reflect validation and delta merging.
- [ ] Run CLI tests and the official skill validator.

### Task 6: Distribution, Example Migration, and Documentation

**Files:**
- Create: `tests/test_example.py`
- Modify: `pyproject.toml`
- Modify: `README.md`
- Modify: `docs/architecture.md`
- Modify: `docs/overview.md`
- Modify: `docs/command-reference.md`
- Modify: `ROADMAP.md`
- Modify: `CHANGELOG.md`
- Modify: `manifest.json`
- Add: `examples/visit-form-auto-generation/change/**`
- Add: missing full-profile demand example artifacts

- [ ] Add a migrated full-profile example with linked demand artifacts and completed traceability.
- [ ] Write a test copying the example into a temporary project and running strict validation.
- [ ] Run `python -m unittest tests.test_example -v` and verify failure before migration is complete.
- [ ] Update package metadata and include all runtime resources in wheels.
- [ ] Update documentation to describe baseline specs, changes, profiles, lifecycle, validation, and archive semantics.
- [ ] Run the complete unit suite.
- [ ] Build and install a wheel into a temporary target, then run `init`, `change new`, and resource installation outside the repository.
- [ ] Run `python -m py_compile demandspec_cli/*.py`.
- [ ] Run the official skill validator.
- [ ] Remove generated build artifacts after verification.

## Final Verification

- [ ] `python -m unittest discover -s tests -v`
- [ ] `python -m py_compile demandspec_cli/*.py`
- [ ] Official `quick_validate.py skills/demandspec`
- [ ] Temporary wheel install smoke test
- [ ] Strict validation of the migrated example
- [ ] Confirm no generated build directories remain

Git commits are omitted because `demandspec-kit` is not inside a Git repository.
