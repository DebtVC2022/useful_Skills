# Acceptance Criteria

## Scenarios

### CRM-VISIT-001 Draft generated from visit materials
- GIVEN a sales user uploads a supported recording, image, or email text
- WHEN the user requests a visit form draft
- THEN the system displays extracted fields, their sources, and confidence values
- AND submission remains disabled until confirmation

### CRM-VISIT-001 Low-confidence field requires review
- GIVEN a generated field is below the configured confidence threshold
- WHEN the draft is displayed
- THEN the field is visibly marked and requires manual confirmation
