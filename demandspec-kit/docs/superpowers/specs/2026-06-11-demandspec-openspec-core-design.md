# DemandSpec OpenSpec Core Design

## Goal

Upgrade DemandSpec from a requirement-document scaffold into a backward-compatible
requirement-side OpenSpec framework with durable baseline specifications, isolated
changes, delta merging, lifecycle gates, configurable profiles, strict validation,
and installable skill and CLI packages.

## Compatibility Boundary

Keep the existing `demands/<demand-id>/00_intake...08_archive` structure as the
full requirement-engineering record. Add a separate change-control layer rather
than replacing existing demand packages.

Existing commands and templates remain available. New change commands operate on
`changes/` and `specs/`. A demand package may reference a change through metadata,
but either layer can be used independently.

## Repository Model

```text
.demandspec/
  config.yaml
  templates/

specs/
  <domain>/spec.md

changes/
  <change-id>/
    metadata.yaml
    proposal.md
    specs/<domain>/spec.md
    acceptance.md
    tasks.md
    design.md
    approval.md
  archive/
    YYYYMMDD-<change-id>/

demands/
  <demand-id>/
    00_intake/
    ...
    08_archive/
```

`specs/` is the current requirement source of truth. `changes/` contains proposed
updates. Archived changes retain their complete review history after their delta
specifications have been merged into the baseline.

## Change Artifacts

Each change contains:

- `metadata.yaml`: identity, profile, domain, owner, reviewers, status, and dates.
- `proposal.md`: problem, intent, scope, non-goals, impact, and dependencies.
- `specs/<domain>/spec.md`: ADDED, MODIFIED, and REMOVED requirement deltas.
- `acceptance.md`: requirement-linked Given/When/Then scenarios.
- `tasks.md`: requirement-linked implementation checklist.
- `approval.md`: review decision, approver, date, and outstanding conditions.
- `design.md`: full-profile design and delivery approach.

Requirement identifiers use stable domain-scoped values such as `CRM-VISIT-001`.
Acceptance scenarios and tasks reference these identifiers to provide traceability.

## Profiles

### Lite

Use for focused, low-risk changes:

```text
proposal -> delta specs -> acceptance -> tasks -> approval
```

### Full

Use for AI, UI, high-risk approval, cross-system, or otherwise complex changes.
Full includes all lite artifacts plus `design.md` and the existing nine-stage
DemandSpec demand package.

The CLI reads profile definitions and conditional requirements from
`.demandspec/config.yaml`. Configuration is executable policy rather than
documentation only.

## Lifecycle

```text
draft -> clarifying -> review -> approved -> implementing -> verified -> archived
```

Allowed transitions are explicit. Approval is required before implementation.
Strict validation, completed tasks, and `verified` status are required before
archive.

## Validation

Validation checks:

- Required artifacts for the selected profile.
- Required Markdown sections and non-placeholder content.
- Delta headers and requirement identifiers.
- RFC 2119 behavior language and at least one scenario per active requirement.
- Given/When/Then acceptance format.
- Requirement identifier traceability across deltas, acceptance, and tasks.
- Blocking unknowns and unresolved assumptions.
- AI and UI conditional artifacts.
- Approval decision and lifecycle consistency.
- Task completion before archive.
- MODIFIED and REMOVED requirements exist in the current baseline.

`validate` supports human-readable output, `--strict`, and `--json`.

## Archive

Archive performs:

1. Strict validation.
2. Lifecycle and task-completion checks.
3. Delta conflict checks against the current baseline.
4. ADDED append, MODIFIED replacement, and REMOVED deletion.
5. Atomic baseline writes.
6. Move of the completed change to `changes/archive/YYYYMMDD-<change-id>/`.

Archive does not silently bypass validation.

## CLI

Keep existing commands and add:

- `change new`
- `change show`
- `change list`
- `change approve`
- `change set-status`
- `change validate`
- `change archive`

The existing top-level `validate` and `archive` commands continue to work for
demand packages and accept change identifiers where unambiguous.

## Skill and Distribution

- Add valid Agent Skill YAML frontmatter to `skills/demandspec/SKILL.md`.
- Add `skills/demandspec/agents/openai.yaml`.
- Install both Codex prompts and the discoverable Codex skill.
- Store runtime resources inside the Python package.
- Include configs, templates, commands, rules, and skill assets in built wheels.
- Resolve resources with `importlib.resources`, not repository-relative paths.

## Identifier Safety

Generate readable ASCII slugs where possible. For Chinese or otherwise
non-transliterated names, use `demand-<stable-short-hash>` or
`change-<stable-short-hash>`. Refuse to overwrite an existing item with different
metadata.

## Testing

Use Python `unittest` with temporary directories. Cover:

- Unique non-ASCII identifiers.
- Project and change initialization.
- Lite and full artifact requirements.
- Empty-template and traceability failures.
- Lifecycle transition and approval gates.
- ADDED, MODIFIED, and REMOVED archive merges.
- Wheel contents and installed CLI execution.
- Codex skill installation.
- Existing demand commands and migrated example.

## Success Criteria

1. Distinct Chinese names never collide silently.
2. Empty templates fail strict validation.
3. Unapproved or incomplete changes cannot archive.
4. Delta operations update baseline specifications correctly.
5. A wheel-installed CLI runs without repository files.
6. The DemandSpec skill passes the official skill validator.
7. The example passes strict validation after migration.
8. All automated tests pass.
