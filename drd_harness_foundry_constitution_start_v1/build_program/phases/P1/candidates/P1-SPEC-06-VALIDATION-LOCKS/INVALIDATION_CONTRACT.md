# P1-SPEC-06 Invalidation Contract

## Purpose

This contract defines how upstream hash changes invalidate downstream work.

It implements `DRD-CHARTER-015`.

## Invalidation Subjects

Downstream subjects include:

- Candidate artifacts.
- Approved artifacts.
- SPEC_LOCK records.
- BUILD_LOCK records.
- Implementation workpacks.
- Test results.
- Generated indexes.
- Runtime skills or skill packs when they bind to old spec or source hashes.
- Release artifacts.

## Invalidation Causes

| Cause | Meaning |
|---|---|
| `UPSTREAM_HASH_CHANGED` | Locked upstream file, source, review decision, SPEC_LOCK, or BUILD_LOCK hash changed. |
| `REVIEW_DECISION_SUPERSEDED` | Approval was replaced, rejected, or revised. |
| `LOCK_SUPERSEDED` | A newer lock supersedes a previous dependency. |
| `VALIDATOR_VERSION_CHANGED` | Validator logic or schema changed and prior result is no longer trusted. |
| `FORBIDDEN_SCOPE_CHANGE` | A forbidden write path or authority boundary changed. |
| `SOURCE_LOCK_CHANGED` | Constitution, source PRD, or other source lock changed. |

## Invalidation Record Fields

| Field | Requirement |
|---|---|
| `invalidation_id` | Stable ID. |
| `cause` | One declared cause. |
| `changed_dependency` | Upstream dependency path or lock ID. |
| `old_hash` | Previously bound hash. |
| `new_hash` | New hash or null when removed. |
| `affected_subjects` | Downstream artifacts, workpacks, tests, skills, or locks. |
| `required_action` | Revalidate, repair, review, relock, rebuild, retest, or discard. |
| `blocking_state` | Whether downstream use is blocked. |
| `created_by_runtime` | Runtime that detected invalidation. |

## Contract Clauses

### INVALIDATION-CONTRACT-001 Old Hash Means Old Authority

Any downstream subject bound to an old upstream hash is invalid after the upstream hash changes.

### INVALIDATION-CONTRACT-002 Invalidation Blocks Consumption

Invalidated subjects cannot be used as approved upstream inputs, lock inputs, implementation basis, or test evidence.

### INVALIDATION-CONTRACT-003 Revalidation Is Required

Affected subjects must be revalidated against the new upstream hash and may require Human Gate review.

### INVALIDATION-CONTRACT-004 Transitive Invalidation

Invalidation must propagate through dependency graphs until all affected downstream subjects are marked or proven unaffected.

### INVALIDATION-CONTRACT-005 Partial Impact Must Be Explicit

If only part of a downstream subject is affected, the unaffected claim must cite dependency analysis and validator result.

### INVALIDATION-CONTRACT-006 Skill And Workpack Impact Is Recorded

Skills, workpacks, and tests depending on old hashes must be marked invalidated or revalidated, even when their files did not change.

