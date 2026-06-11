# Change Design

## Approach
Use an asynchronous material-processing pipeline that returns a structured draft.
Keep final submission in the existing transactional service.

## Components
Material upload, content extraction, field mapping, confidence evaluation,
draft review UI, and correction logging.

## Data Flow
Uploaded materials are normalized, extracted into candidate fields, mapped to
the visit form schema, reviewed by the user, and then submitted through the
existing API.

## Risks and Rollback
Low-quality extraction can create misleading drafts. Human confirmation is
mandatory, and the AI draft feature can be disabled without changing manual entry.

## Delivery Plan
Deliver extraction and draft APIs first, then the review UI, evaluation dataset,
acceptance tests, and controlled rollout.
