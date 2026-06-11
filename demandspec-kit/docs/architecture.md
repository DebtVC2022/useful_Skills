# DemandSpec Architecture

## Three Layers

```text
Requirement engineering: demands/<demand-id>/00_intake...08_archive
Change control:          changes/<change-id>/ proposal, specs, tasks, approval
Requirement baseline:   specs/<domain>/spec.md
```

The existing nine-stage demand package remains the detailed business-analysis
record. The change layer packages a reviewable update. The baseline records only
currently approved behavior.

## Change Structure

```text
changes/<change-id>/
  metadata.yaml
  proposal.md
  specs/<domain>/spec.md
  acceptance.md
  tasks.md
  approval.md
  design.md               # full profile
```

Delta specs use `ADDED`, `MODIFIED`, and `REMOVED Requirements`. Each active
requirement has a stable ID, RFC 2119 behavior statement, and Given/When/Then
scenario. Acceptance criteria and tasks reference the same ID.

## Profiles

- `lite`: proposal, delta specs, acceptance, tasks, approval.
- `full`: lite artifacts, design, and a linked nine-stage demand package.

AI, UI, high-risk, and cross-system changes default to full.

## Lifecycle and Archive

```text
draft → clarifying → review → approved → implementing → verified → archived
```

Archive requires strict validation, valid approval, verified status, and complete
tasks. It merges deltas into `specs/` and moves the complete change to
`changes/archive/YYYYMMDD-<change-id>/`.

## Runtime Assets

CLI resources are bundled under `demandspec_cli.resources`, so wheel installations
do not depend on the source repository layout. Tool installers create prompts,
rules, and discoverable skills from these packaged assets.
