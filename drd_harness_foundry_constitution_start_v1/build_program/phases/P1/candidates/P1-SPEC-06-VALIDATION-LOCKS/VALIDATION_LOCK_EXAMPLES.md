# P1-SPEC-06 Validation Lock Examples

## Positive Example: Review Binding

```json
{
  "decision_id": "P1-SPEC-05-PRESENTATION-LAYOUT-REVIEW-001",
  "subject_hash": "2749676726510e6c64448df120e1be2bf33a306ae317cf3280e0ee4c57fd8472",
  "decision": "APPROVED",
  "reviewer": "human-user",
  "open_blockers": [],
  "approved_sections": [
    "NATURAL_LANGUAGE_LAYOUT_CONTRACT.md",
    "PRESENTATION_LAYOUT_VALIDATOR_SPEC.md"
  ]
}
```

Why this passes:

- Approval binds to a concrete subject hash.
- Open blockers are empty.
- Approved sections are explicit.

## Negative Example: Self Approval

```json
{
  "workpack_id": "P1-SPEC-06-VALIDATION-LOCKS",
  "approval_state": "APPROVED_BY_CODEX",
  "seal_state": "LOCKED"
}
```

Expected result: fail.

Reason:

- Codex cannot approve or lock its own output.

## Negative Example: Stale Review Hash

```json
{
  "decision_id": "P1-SPEC-05-REVIEW-001",
  "subject_hash": "old_hash",
  "decision": "APPROVED"
}
```

Expected result: fail when current Candidate output hash differs.

Reason:

- Approval applies only to the reviewed subject hash.

## Positive Example: Invalidation Record

```json
{
  "invalidation_id": "INV-P1-0001",
  "cause": "UPSTREAM_HASH_CHANGED",
  "changed_dependency": "P1-SPEC-05-PRESENTATION-LAYOUT/SPEC_LOCK",
  "old_hash": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "new_hash": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "affected_subjects": [
    "P1-IMPLEMENT-05-PRESENTATION-LAYOUT",
    "repository/tests/layout/test_layout_completeness.py"
  ],
  "required_action": "revalidate_rebuild_retest",
  "blocking_state": true,
  "created_by_runtime": "python"
}
```

Why this passes:

- It names the changed dependency, old and new hashes, affected subjects, action, and blocking state.

## Negative Example: Lock Missing Review

```json
{
  "lock_id": "SPEC-LOCK-P1-001",
  "phase": "P1",
  "files": [],
  "root_sha256": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
}
```

Expected result: fail.

Reason:

- SPEC_LOCK readiness must include approved files, review decision hashes, validator result hashes, and source lock refs.

## Negative Example: Invalidated Test Used As Evidence

```json
{
  "test_result_id": "TEST-P1-001",
  "bound_spec_lock_hash": "old_hash",
  "used_for_build_lock": true,
  "invalidation_state": "INVALIDATED"
}
```

Expected result: fail.

Reason:

- Invalidated evidence cannot justify current build or lock state.

