# CRM Requirement Delta

## ADDED Requirements

### Requirement: CRM-VISIT-001 Generate a reviewable visit form draft
The system MUST generate a visit form draft from supported visit materials and require human confirmation before submission.

#### Scenario: Draft generated from visit materials
- GIVEN a sales user has uploaded supported visit materials
- WHEN the user requests a visit form draft
- THEN the system displays extracted fields with source and confidence information
- AND the system prevents submission until the user confirms the draft

#### Scenario: Low-confidence field requires review
- GIVEN a generated field is below the configured confidence threshold
- WHEN the draft is displayed
- THEN the system marks the field for mandatory human review
