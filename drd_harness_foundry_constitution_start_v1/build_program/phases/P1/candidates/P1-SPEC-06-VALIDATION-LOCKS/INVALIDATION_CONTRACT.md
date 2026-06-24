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
| `recovery_owner` | Person, runtime, workpack, or role responsible for resolving the invalidation. |
| `required_command` | Concrete command or workflow required to restore trust, when mechanical action is needed. |
| `due_before_consumption` | Whether recovery must happen before any downstream consumption. |
| `blocking_state` | Whether downstream use is blocked. |
| `created_by_runtime` | Runtime that detected invalidation. |

## Dependency Edge Types

Dependency graph edges must declare why a downstream subject depends on an upstream hash.

| Edge Type | Meaning |
|---|---|
| `SOURCE_DEPENDENCY` | Depends on Source PRD, constitution, source lock, or source snapshot. |
| `REVIEW_DEPENDENCY` | Depends on a Human Gate review decision or review hash. |
| `SPEC_LOCK_DEPENDENCY` | Depends on SPEC_LOCK content or hash. |
| `BUILD_LOCK_DEPENDENCY` | Depends on BUILD_LOCK content or hash. |
| `VALIDATOR_DEPENDENCY` | Depends on validator code, schema, command, or runtime identity. |
| `TEST_EVIDENCE_DEPENDENCY` | Depends on a test result or test evidence hash. |
| `WORKPACK_DEPENDENCY` | Depends on workpack scope, inputs, acceptance commands, or status. |
| `SKILL_DEPENDENCY` | Depends on skill pack, skill version, or skill source hash. |
| `RELEASE_DEPENDENCY` | Depends on release artifact, release evidence, or publish state. |

Each edge must include source subject, target subject, edge type, upstream hash, downstream binding field, and invalidation behavior.

## Partial Unaffected Claim Fields

If an invalidation does not affect an entire downstream subject, the unaffected claim must be structured.

| Field | Requirement |
|---|---|
| `claim_id` | Stable ID. |
| `changed_dependency` | Changed upstream dependency. |
| `affected_paths` | Paths, sections, tests, skills, locks, or workpacks affected. |
| `unaffected_paths` | Paths, sections, tests, skills, locks, or workpacks claimed unaffected. |
| `reason` | Dependency analysis explaining why the claim is valid. |
| `validator_result_ref` | Validator result proving or checking the claim. |
| `review_required` | Whether Human Gate must review the unaffected claim. |
| `expires_on_dependency_change` | Dependencies that invalidate the unaffected claim if changed. |

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

The claim must use the structured partial unaffected claim fields. A prose-only "not affected" statement is invalid.

### INVALIDATION-CONTRACT-006 Skill And Workpack Impact Is Recorded

Skills, workpacks, and tests depending on old hashes must be marked invalidated or revalidated, even when their files did not change.

### INVALIDATION-CONTRACT-007 Recovery Is Owned And Executable

Every invalidated subject must name a recovery owner and required command or workflow before it can leave blocking state.
