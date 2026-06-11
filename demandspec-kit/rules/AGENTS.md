# Project Instructions: DemandSpec

This project uses DemandSpec as the requirement-side AI harness.

## Change Control

Use `specs/<domain>/spec.md` as the approved requirement baseline. Put proposed
updates in `changes/<change-id>/` with proposal, delta specs, acceptance criteria,
tasks, approval, and profile metadata.

Do not implement a change before it reaches `approved`. Do not archive a change
before it reaches `verified`, all tasks are complete, and strict validation passes.
Archiving must merge ADDED/MODIFIED/REMOVED requirements into the baseline and
preserve the complete change under `changes/archive/`.

## Required Behavior

When the user asks to analyze, write, review, or transform a requirement, do not directly produce a final PRD unless the user explicitly requests a quick draft. Prefer the DemandSpec workflow:

1. Intake
2. Clarify
3. Diagnose
4. Model
5. Prototype
6. Specify
7. Validate
8. Handoff
9. Archive

## Directory Rules

Requirement assets must be placed under:

```text
demands/<demand-id>/
```

Use the standard subdirectories:

```text
00_intake
01_clarify
02_diagnose
03_model
04_prototype
05_spec
06_validate
07_handoff
08_archive
```

## Requirement Quality Rules

- Mark unknown information as `待确认`.
- Mark assumptions as `当前假设` with risk.
- Do not invent business facts, system names, owners, or metrics.
- PRD must include scope, non-scope, users, workflow, fields, rules, permissions, acceptance criteria, and risks.
- AI scenarios must include data requirement, model/task type, evaluation metrics, human fallback, and feedback loop.
- Prototype outputs must include frame structure, component tree, interaction map, states, and review checklist.
- Requirement deltas must use stable requirement IDs and Given/When/Then scenarios.
- Acceptance criteria and tasks must reference the corresponding requirement IDs.

## Slash Command Convention

Use hyphenated commands such as:

```text
/demandspec-intake
/demandspec-prd
/demandspec-figma
```
